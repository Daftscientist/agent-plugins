"""Principal-scoped SQLite snapshot store with FTS5 indexing."""

import asyncio
import sqlite3
from pathlib import Path

from office_mcp.domain.state import PresentationSnapshot
from office_mcp.errors import ErrorCode, OfficeError, RevisionConflict

from .protocols import RequestScope


class LocalPresentationStore:
    def __init__(self, database: Path) -> None:
        self.database = database
        self._lock = asyncio.Lock()
        database.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS presentations (
                  scope_key TEXT NOT NULL,
                  presentation_id TEXT NOT NULL,
                  name TEXT NOT NULL,
                  description TEXT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  current_revision_id TEXT NOT NULL,
                  PRIMARY KEY(scope_key, presentation_id)
                );
                CREATE TABLE IF NOT EXISTS revisions (
                  scope_key TEXT NOT NULL,
                  presentation_id TEXT NOT NULL,
                  revision_id TEXT NOT NULL,
                  parent_revision_id TEXT,
                  created_at TEXT NOT NULL,
                  snapshot_json TEXT NOT NULL,
                  content_hash TEXT NOT NULL,
                  PRIMARY KEY(scope_key, presentation_id, revision_id),
                  FOREIGN KEY(scope_key, presentation_id)
                    REFERENCES presentations(scope_key, presentation_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS slides (
                  scope_key TEXT NOT NULL,
                  presentation_id TEXT NOT NULL,
                  slide_id TEXT NOT NULL,
                  ordinal INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  description TEXT,
                  extracted_text TEXT NOT NULL,
                  PRIMARY KEY(scope_key, presentation_id, slide_id),
                  FOREIGN KEY(scope_key, presentation_id)
                    REFERENCES presentations(scope_key, presentation_id) ON DELETE CASCADE
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS presentation_fts USING fts5(
                  scope_key UNINDEXED, presentation_id UNINDEXED,
                  name, description, slide_names, slide_descriptions, slide_text
                );
                """
            )

    @staticmethod
    def _json(snapshot: PresentationSnapshot) -> str:
        return snapshot.model_dump_json()

    @staticmethod
    def _hash(payload: str) -> str:
        import hashlib

        return hashlib.sha256(payload.encode()).hexdigest()

    def _index(
        self, db: sqlite3.Connection, scope: RequestScope, snapshot: PresentationSnapshot
    ) -> None:
        from office_mcp.domain.html import visible_text

        db.execute(
            "DELETE FROM slides WHERE scope_key=? AND presentation_id=?",
            (scope.key, snapshot.presentation_id),
        )
        db.execute(
            "DELETE FROM presentation_fts WHERE scope_key=? AND presentation_id=?",
            (scope.key, snapshot.presentation_id),
        )
        for index, slide in enumerate(snapshot.slides):
            db.execute(
                "INSERT INTO slides VALUES(?,?,?,?,?,?,?)",
                (
                    scope.key,
                    snapshot.presentation_id,
                    slide.slide_id,
                    index,
                    slide.name,
                    slide.description,
                    visible_text(slide.html),
                ),
            )
        db.execute(
            "INSERT INTO presentation_fts VALUES(?,?,?,?,?,?,?)",
            (
                scope.key,
                snapshot.presentation_id,
                snapshot.name,
                snapshot.description or "",
                "\n".join(slide.name for slide in snapshot.slides),
                "\n".join(slide.description or "" for slide in snapshot.slides),
                "\n".join(visible_text(slide.html) for slide in snapshot.slides),
            ),
        )

    async def create(self, scope: RequestScope, snapshot: PresentationSnapshot) -> None:
        payload = self._json(snapshot)
        async with self._lock:
            with self._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute(
                    "INSERT INTO presentations VALUES(?,?,?,?,?,?,?)",
                    (
                        scope.key,
                        snapshot.presentation_id,
                        snapshot.name,
                        snapshot.description,
                        snapshot.created_at.isoformat(),
                        snapshot.updated_at.isoformat(),
                        snapshot.revision_id,
                    ),
                )
                db.execute(
                    "INSERT INTO revisions VALUES(?,?,?,?,?,?,?)",
                    (
                        scope.key,
                        snapshot.presentation_id,
                        snapshot.revision_id,
                        None,
                        snapshot.updated_at.isoformat(),
                        payload,
                        self._hash(payload),
                    ),
                )
                self._index(db, scope, snapshot)

    async def get(
        self, scope: RequestScope, presentation_id: str, revision_id: str | None = None
    ) -> PresentationSnapshot:
        with self._connect() as db:
            if revision_id is None:
                row = db.execute(
                    """SELECT r.snapshot_json FROM presentations p JOIN revisions r
                    ON r.scope_key=p.scope_key AND r.presentation_id=p.presentation_id
                    AND r.revision_id=p.current_revision_id
                    WHERE p.scope_key=? AND p.presentation_id=?""",
                    (scope.key, presentation_id),
                ).fetchone()
            else:
                row = db.execute(
                    """SELECT snapshot_json FROM revisions
                    WHERE scope_key=? AND presentation_id=? AND revision_id=?""",
                    (scope.key, presentation_id, revision_id),
                ).fetchone()
        if row is None:
            raise OfficeError(
                ErrorCode.PRESENTATION_NOT_FOUND, "presentation or revision was not found"
            )
        return PresentationSnapshot.model_validate_json(row[0])

    async def commit(
        self,
        scope: RequestScope,
        snapshot: PresentationSnapshot,
        expected_revision: str | None,
    ) -> None:
        payload = self._json(snapshot)
        async with self._lock:
            with self._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    """SELECT current_revision_id FROM presentations
                    WHERE scope_key=? AND presentation_id=?""",
                    (scope.key, snapshot.presentation_id),
                ).fetchone()
                if row is None:
                    raise OfficeError(
                        ErrorCode.PRESENTATION_NOT_FOUND, "presentation was not found"
                    )
                current = str(row[0])
                if expected_revision is not None and expected_revision != current:
                    raise RevisionConflict(expected_revision, current)
                if snapshot.parent_revision_id != current:
                    raise RevisionConflict(snapshot.parent_revision_id or "none", current)
                db.execute(
                    "INSERT INTO revisions VALUES(?,?,?,?,?,?,?)",
                    (
                        scope.key,
                        snapshot.presentation_id,
                        snapshot.revision_id,
                        current,
                        snapshot.updated_at.isoformat(),
                        payload,
                        self._hash(payload),
                    ),
                )
                db.execute(
                    """UPDATE presentations
                    SET name=?, description=?, updated_at=?, current_revision_id=?
                    WHERE scope_key=? AND presentation_id=?""",
                    (
                        snapshot.name,
                        snapshot.description,
                        snapshot.updated_at.isoformat(),
                        snapshot.revision_id,
                        scope.key,
                        snapshot.presentation_id,
                    ),
                )
                self._index(db, scope, snapshot)

    async def delete(
        self, scope: RequestScope, presentation_id: str, expected_revision: str | None
    ) -> None:
        async with self._lock:
            with self._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    """SELECT current_revision_id FROM presentations
                    WHERE scope_key=? AND presentation_id=?""",
                    (scope.key, presentation_id),
                ).fetchone()
                if row is None:
                    raise OfficeError(
                        ErrorCode.PRESENTATION_NOT_FOUND, "presentation was not found"
                    )
                current = str(row[0])
                if expected_revision is not None and expected_revision != current:
                    raise RevisionConflict(expected_revision, current)
                db.execute(
                    "DELETE FROM presentation_fts WHERE scope_key=? AND presentation_id=?",
                    (scope.key, presentation_id),
                )
                db.execute(
                    "DELETE FROM presentations WHERE scope_key=? AND presentation_id=?",
                    (scope.key, presentation_id),
                )

    async def list_current(self, scope: RequestScope) -> list[PresentationSnapshot]:
        with self._connect() as db:
            rows = db.execute(
                """SELECT r.snapshot_json FROM presentations p JOIN revisions r
                ON r.scope_key=p.scope_key AND r.presentation_id=p.presentation_id
                AND r.revision_id=p.current_revision_id WHERE p.scope_key=?
                ORDER BY p.updated_at DESC, p.presentation_id ASC""",
                (scope.key,),
            ).fetchall()
        return [PresentationSnapshot.model_validate_json(row[0]) for row in rows]

    async def search_ids(self, scope: RequestScope, query: str, fields: list[str]) -> list[str]:
        tokens = __import__("re").findall(r"[\w'-]+", query, flags=__import__("re").UNICODE)
        if not tokens:
            return []
        column_map = {
            "name": "name",
            "description": "description",
            "slide_names": "slide_names",
            "slide_descriptions": "slide_descriptions",
            "slide_text": "slide_text",
        }
        columns = [column_map[field] for field in fields]
        phrase = " AND ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens)
        match = " OR ".join(f"{column}:({phrase})" for column in columns)
        with self._connect() as db:
            rows = db.execute(
                """SELECT presentation_id FROM presentation_fts
                WHERE presentation_fts MATCH ? AND scope_key=? ORDER BY bm25(presentation_fts)""",
                (match, scope.key),
            ).fetchall()
        return [str(row[0]) for row in rows]

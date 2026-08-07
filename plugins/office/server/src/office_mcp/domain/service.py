"""Complete Office presentation, slide, and element domain service."""

import base64
import hashlib
import re
from typing import cast

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

from office_mcp.config import OfficeConfig
from office_mcp.constants import MAX_SLIDES
from office_mcp.domain.cursors import CursorCodec
from office_mcp.domain.html import (
    detach_domoxml_metadata,
    direct_child_ids,
    element_tags,
    model_facing_html,
    parse_styles,
    remint_ids,
    sanitize_fragment,
    select_element,
    serialize_styles,
    visible_text,
)
from office_mcp.domain.preview import contact_sheets
from office_mcp.domain.state import PresentationSnapshot, StoredSlide, now_utc
from office_mcp.domoxml_adapter import DomOXMLAdapter
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.ids import presentation_id, revision_id, slide_id
from office_mcp.inputs import validate_pptx
from office_mcp.models.common import (
    Editability,
    PresentationTheme,
    Representation,
    SourceRetention,
)
from office_mcp.models.element import (
    AddedElement,
    ElementAddArgs,
    ElementAddResult,
    ElementDeleteArgs,
    ElementDeleteResult,
    ElementInsertPosition,
    ElementInspectArgs,
    ElementInspectResult,
    ElementMoveArgs,
    ElementMoveResult,
    ElementUpdateArgs,
    ElementUpdateResult,
)
from office_mcp.models.presentation import (
    ImportWarning,
    MutationResult,
    NewSlide,
    PresentationCreateArgs,
    PresentationCreateResult,
    PresentationDeleteArgs,
    PresentationDeleteResult,
    PresentationExportArgs,
    PresentationExportResult,
    PresentationInspectArgs,
    PresentationInspectDetail,
    PresentationInspectResult,
    PresentationOpenArgs,
    PresentationOpenResult,
    PresentationSearchArgs,
    PresentationSearchItem,
    PresentationSearchMatch,
    PresentationSearchResult,
    PresentationSearchSort,
    PresentationUpdateArgs,
    SlideRef,
)
from office_mcp.models.preview import (
    PresentationPreviewArgs,
    PresentationPreviewResult,
    PreviewAll,
    PreviewImageDescriptor,
    PreviewLayout,
    PreviewRange,
    PreviewSelection,
    PreviewSlides,
)
from office_mcp.models.slide import (
    ElementStructureNode,
    InsertBefore,
    InsertEnd,
    InsertStart,
    SlideAddArgs,
    SlideAddResult,
    SlideDeleteArgs,
    SlideDeleteResult,
    SlideDuplicateArgs,
    SlideDuplicateResult,
    SlideInsertionPosition,
    SlideInspectArgs,
    SlideInspectDetail,
    SlideInspectResult,
    SlideReorderArgs,
    SlideReorderResult,
    SlideSummary,
    SlideUpdateArgs,
)
from office_mcp.models.validation import (
    CoverageItem,
    PresentationValidateArgs,
    PresentationValidationResult,
    ValidationDetail,
    ValidationWarning,
)
from office_mcp.storage.protocols import InputResolver, OutputSink, PresentationStore, RequestScope


class PresentationService:
    _MAX_PREVIEW_CACHE_ENTRIES = 32
    _MAX_VALIDATION_CACHE_ENTRIES = 256

    def __init__(
        self,
        store: PresentationStore,
        resolver: InputResolver,
        output: OutputSink,
        adapter: DomOXMLAdapter,
        cursor: CursorCodec,
        config: OfficeConfig,
    ) -> None:
        self.store = store
        self.resolver = resolver
        self.output = output
        self.adapter = adapter
        self.cursor = cursor
        self.config = config
        self._preview_cache: dict[str, tuple[list[bytes], PresentationPreviewResult]] = {}
        self._validation_cache: dict[tuple[str, str, str], PresentationValidationResult] = {}

    @staticmethod
    def _refs(snapshot: PresentationSnapshot) -> list[SlideRef]:
        return [
            SlideRef(
                slide_id=slide.slide_id,
                number=index,
                name=slide.name,
                description=slide.description,
            )
            for index, slide in enumerate(snapshot.slides, start=1)
        ]

    def _sanitize(
        self,
        html: str,
        *,
        exactly_one_root: bool = False,
        preserve_ids: bool = False,
        preserve_domoxml: bool = False,
    ) -> tuple[str, list[str]]:
        return sanitize_fragment(
            html,
            exactly_one_root=exactly_one_root,
            max_bytes=self.config.max_html_bytes,
            _preserve_office_ids=preserve_ids,
            _preserve_domoxml_metadata=preserve_domoxml,
        )

    def _stored(self, new: NewSlide) -> StoredSlide:
        html, _ = self._sanitize(new.html)
        return StoredSlide(
            slide_id=slide_id(),
            name=new.name,
            description=new.description,
            html=html,
            transition=new.transition,
            size=new.size,
        )

    @staticmethod
    def _find_slide(snapshot: PresentationSnapshot, target: str) -> tuple[int, StoredSlide]:
        for index, slide in enumerate(snapshot.slides):
            if slide.slide_id == target:
                return index, slide
        raise OfficeError(
            ErrorCode.SLIDE_NOT_FOUND, "slide was not found; refresh the presentation outline"
        )

    @staticmethod
    def _next(snapshot: PresentationSnapshot) -> tuple[str, PresentationSnapshot]:
        previous = snapshot.revision_id
        copy = snapshot.model_copy(deep=True)
        copy.parent_revision_id = previous
        copy.revision_id = revision_id()
        copy.updated_at = now_utc()
        return previous, copy

    async def create(
        self, scope: RequestScope, args: PresentationCreateArgs
    ) -> PresentationCreateResult:
        if len(args.slides) > MAX_SLIDES:
            raise OfficeError(ErrorCode.RESOURCE_TOO_LARGE, "presentation exceeds slide limit")
        now = now_utc()
        snapshot = PresentationSnapshot(
            presentation_id=presentation_id(),
            revision_id=revision_id(),
            name=args.name,
            description=args.description,
            size=args.size,
            theme=args.theme,
            slides=[self._stored(slide) for slide in args.slides],
            created_at=now,
            updated_at=now,
        )
        await self.store.create(scope, snapshot)
        return PresentationCreateResult(
            presentation_id=snapshot.presentation_id,
            revision=snapshot.revision_id,
            name=snapshot.name,
            slide_count=len(snapshot.slides),
            slides=self._refs(snapshot),
            resource_uri=f"office://presentations/{snapshot.presentation_id}",
        )

    async def open(self, scope: RequestScope, args: PresentationOpenArgs) -> PresentationOpenResult:
        data = await self.resolver.resolve(args.source.uri)
        validate_pptx(data, self.config)
        imported = await self.adapter.import_pptx(data)
        if len(imported.slides) > MAX_SLIDES:
            raise OfficeError(ErrorCode.RESOURCE_TOO_LARGE, "presentation exceeds slide limit")
        for slide in imported.slides:
            if len(slide.html.encode("utf-8")) > self.config.max_html_bytes:
                raise OfficeError(
                    ErrorCode.RESOURCE_TOO_LARGE, "imported slide HTML exceeds the byte limit"
                )
            slide.slide_id = slide_id()
        now = now_utc()
        fallback_name = args.source.filename_hint or "Imported presentation"
        fallback_name = re.sub(r"(?i)\.pptx$", "", fallback_name)[:160] or "Imported presentation"
        snapshot = PresentationSnapshot(
            presentation_id=presentation_id(),
            revision_id=revision_id(),
            name=args.name or fallback_name,
            description=args.description,
            size=imported.size,
            theme=PresentationTheme(),
            slides=imported.slides,
            created_at=now,
            updated_at=now,
            imported_pptx_b64=base64.b64encode(data).decode(),
            imported_preservation=imported.preservation,
            imported_coverage=imported.coverage,
            import_warnings=imported.warnings,
        )
        await self.store.create(scope, snapshot)
        warnings = [
            ImportWarning.model_validate(
                {
                    **warning,
                    "slide_number": warning.get("slide_number"),
                }
            )
            for warning in imported.warnings
        ]
        if imported.preservation:
            warnings.append(
                ImportWarning(
                    code="PRESERVED_SOURCE",
                    message=(
                        f"domOXML retained {len(imported.preservation)} "
                        "unsupported source fragments"
                    ),
                )
            )
        return PresentationOpenResult(
            presentation_id=snapshot.presentation_id,
            revision=snapshot.revision_id,
            name=snapshot.name,
            slide_count=len(snapshot.slides),
            slides=self._refs(snapshot),
            warnings=warnings,
            resource_uri=f"office://presentations/{snapshot.presentation_id}",
        )

    async def inspect(
        self, scope: RequestScope, args: PresentationInspectArgs
    ) -> PresentationInspectResult:
        snapshot = await self.store.get(scope, args.presentation_id, args.revision)
        return PresentationInspectResult(
            presentation_id=snapshot.presentation_id,
            revision=snapshot.revision_id,
            name=snapshot.name,
            description=snapshot.description,
            size=snapshot.size,
            theme=snapshot.theme,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
            slide_count=len(snapshot.slides),
            slides=self._refs(snapshot) if args.detail is PresentationInspectDetail.OUTLINE else [],
        )

    async def search(
        self, scope: RequestScope, args: PresentationSearchArgs
    ) -> PresentationSearchResult:
        snapshots = await self.store.list_current(scope)
        order: dict[str, int] = {}
        if args.query:
            ids = await self.store.search_ids(
                scope, args.query, [field.value for field in args.search_in]
            )
            order = {item: index for index, item in enumerate(ids)}
            snapshots = [item for item in snapshots if item.presentation_id in order]

        def allowed(item: PresentationSnapshot) -> bool:
            return not (
                (args.created_after and item.created_at < args.created_after)
                or (args.created_before and item.created_at > args.created_before)
                or (args.updated_after and item.updated_at < args.updated_after)
                or (args.updated_before and item.updated_at > args.updated_before)
            )

        snapshots = [item for item in snapshots if allowed(item)]
        if args.sort is PresentationSearchSort.RELEVANCE and args.query:
            snapshots.sort(key=lambda item: order.get(item.presentation_id, 10**9))
        elif args.sort is PresentationSearchSort.UPDATED_ASC:
            snapshots.sort(key=lambda item: (item.updated_at, item.presentation_id))
        elif args.sort is PresentationSearchSort.UPDATED_DESC:
            snapshots.sort(key=lambda item: (item.updated_at, item.presentation_id), reverse=True)
        elif args.sort is PresentationSearchSort.CREATED_ASC:
            snapshots.sort(key=lambda item: (item.created_at, item.presentation_id))
        elif args.sort is PresentationSearchSort.CREATED_DESC:
            snapshots.sort(key=lambda item: (item.created_at, item.presentation_id), reverse=True)
        elif args.sort is PresentationSearchSort.NAME_ASC:
            snapshots.sort(key=lambda item: (item.name.casefold(), item.presentation_id))
        elif args.sort is PresentationSearchSort.NAME_DESC:
            snapshots.sort(
                key=lambda item: (item.name.casefold(), item.presentation_id), reverse=True
            )
        filter_hash = hashlib.sha256(
            args.model_dump_json(exclude={"cursor", "limit"}).encode()
        ).hexdigest()
        offset = 0
        if args.cursor:
            payload = self.cursor.decode(args.cursor)
            if payload.get("scope") != scope.key or payload.get("filter") != filter_hash:
                raise OfficeError(
                    ErrorCode.INVALID_PRESENTATION_SOURCE, "cursor does not match this search"
                )
            offset = int(payload["offset"])
        page = snapshots[offset : offset + args.limit]
        next_cursor = None
        if offset + args.limit < len(snapshots):
            next_cursor = self.cursor.encode(
                {"scope": scope.key, "filter": filter_hash, "offset": offset + args.limit}
            )
        query = (args.query or "").casefold()
        items: list[PresentationSearchItem] = []
        for snapshot in page:
            matches: list[PresentationSearchMatch] = []
            if query:
                for slide in snapshot.slides:
                    text = visible_text(slide.html)
                    haystack = " ".join((slide.name, slide.description or "", text))
                    if query in haystack.casefold() or any(
                        token in haystack.casefold() for token in query.split()
                    ):
                        snippet = text[:240] or slide.description or slide.name
                        matches.append(
                            PresentationSearchMatch(
                                slide_id=slide.slide_id, slide_name=slide.name, snippet=snippet
                            )
                        )
                        if len(matches) == 3:
                            break
            if not matches:
                matches.append(
                    PresentationSearchMatch(snippet=(snapshot.description or snapshot.name)[:240])
                )
            items.append(
                PresentationSearchItem(
                    presentation_id=snapshot.presentation_id,
                    revision=snapshot.revision_id,
                    name=snapshot.name,
                    description=snapshot.description,
                    created_at=snapshot.created_at,
                    updated_at=snapshot.updated_at,
                    slide_count=len(snapshot.slides),
                    matches=matches,
                    resource_uri=f"office://presentations/{snapshot.presentation_id}",
                )
            )
        return PresentationSearchResult(items=items, next_cursor=next_cursor)

    async def update(self, scope: RequestScope, args: PresentationUpdateArgs) -> MutationResult:
        current = await self.store.get(scope, args.presentation_id)
        previous, snapshot = self._next(current)
        if "name" in args.model_fields_set and args.name is not None:
            snapshot.name = args.name
        if "description" in args.model_fields_set:
            snapshot.description = args.description
        if "size" in args.model_fields_set:
            if args.size is None:
                raise OfficeError(
                    ErrorCode.INVALID_PRESENTATION_SOURCE, "presentation size cannot be cleared"
                )
            snapshot.size = args.size
        if args.theme:
            theme_data: dict[str, object] = snapshot.theme.model_dump()
            patch: dict[str, object] = args.theme.model_dump(exclude_unset=True)
            for group, values in patch.items():
                if isinstance(values, dict):
                    target = theme_data[group]
                    if isinstance(target, dict):
                        typed_target = cast(dict[str, object], target)
                        typed_values = cast(dict[str, object], values)
                        typed_target.update(
                            {key: value for key, value in typed_values.items() if value is not None}
                        )
            snapshot.theme = PresentationTheme.model_validate(theme_data)
        if {"size", "theme"} & args.model_fields_set:
            snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        return MutationResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
        )

    def _insertion_index(
        self, snapshot: PresentationSnapshot, position: SlideInsertionPosition
    ) -> int:
        if isinstance(position, InsertStart):
            return 0
        if isinstance(position, InsertEnd):
            return len(snapshot.slides)
        if isinstance(position, InsertBefore):
            return self._find_slide(snapshot, position.slide_id)[0]
        return self._find_slide(snapshot, position.slide_id)[0] + 1

    async def slide_add(self, scope: RequestScope, args: SlideAddArgs) -> SlideAddResult:
        current = await self.store.get(scope, args.presentation_id)
        previous, snapshot = self._next(current)
        added = [self._stored(slide) for slide in args.slides]
        if len(snapshot.slides) + len(added) > MAX_SLIDES:
            raise OfficeError(ErrorCode.RESOURCE_TOO_LARGE, "presentation exceeds slide limit")
        position = self._insertion_index(snapshot, args.position)
        snapshot.slides[position:position] = added
        snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        refs = self._refs(snapshot)
        added_ids = {slide.slide_id for slide in added}
        return SlideAddResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
            added=[ref for ref in refs if ref.slide_id in added_ids],
            slide_count=len(snapshot.slides),
        )

    async def slide_inspect(
        self, scope: RequestScope, args: SlideInspectArgs
    ) -> SlideInspectResult:
        snapshot = await self.store.get(scope, args.presentation_id, args.revision)
        index, slide = self._find_slide(snapshot, args.slide_id)
        tags = element_tags(slide.html)
        summary = SlideSummary(
            slide_id=slide.slide_id,
            number=index + 1,
            name=slide.name,
            description=slide.description,
            transition=slide.transition,
            size=slide.size,
            element_count=len(tags),
        )
        structure = None
        html = None
        if args.detail is SlideInspectDetail.STRUCTURE:
            structure = [
                ElementStructureNode(
                    element_id=str(tag["data-office-id"]),
                    element_name=str(tag["data-office-name"])
                    if tag.has_attr("data-office-name")
                    else None,
                    tag=tag.name,
                    text=" ".join(tag.find_all(string=True, recursive=False)).strip() or None,
                    child_ids=direct_child_ids(tag),
                )
                for tag in tags
            ]
        elif args.detail is SlideInspectDetail.SOURCE:
            html = model_facing_html(slide.html)
        return SlideInspectResult(
            presentation_id=snapshot.presentation_id,
            revision=snapshot.revision_id,
            summary=summary,
            structure=structure,
            html=html,
        )

    async def slide_update(self, scope: RequestScope, args: SlideUpdateArgs) -> MutationResult:
        current = await self.store.get(scope, args.presentation_id)
        previous, snapshot = self._next(current)
        _, slide = self._find_slide(snapshot, args.slide_id)
        for field in ("name", "description", "transition", "size"):
            if field in args.model_fields_set:
                setattr(slide, field, getattr(args, field))
        if "html" in args.model_fields_set:
            if args.html is None:
                raise OfficeError(ErrorCode.INVALID_HTML, "slide HTML cannot be cleared")
            slide.html = self._sanitize(args.html)[0]
        if {"transition", "size", "html"} & args.model_fields_set:
            snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        return MutationResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
        )

    async def slide_duplicate(
        self, scope: RequestScope, args: SlideDuplicateArgs
    ) -> SlideDuplicateResult:
        current = await self.store.get(scope, args.presentation_id)
        previous, snapshot = self._next(current)
        source_index, source = self._find_slide(snapshot, args.slide_id)
        duplicate = source.model_copy(deep=True)
        duplicate.slide_id = slide_id()
        duplicate.name = args.name
        duplicate.description = args.description
        duplicate.html = remint_ids(duplicate.html)
        if len(snapshot.slides) >= MAX_SLIDES:
            raise OfficeError(ErrorCode.RESOURCE_TOO_LARGE, "presentation exceeds slide limit")
        position = (
            self._insertion_index(snapshot, args.position) if args.position else source_index + 1
        )
        snapshot.slides.insert(position, duplicate)
        snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        ref = next(item for item in self._refs(snapshot) if item.slide_id == duplicate.slide_id)
        return SlideDuplicateResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
            slide=ref,
        )

    async def slide_delete(self, scope: RequestScope, args: SlideDeleteArgs) -> SlideDeleteResult:
        current = await self.store.get(scope, args.presentation_id)
        current_ids = {slide.slide_id for slide in current.slides}
        missing = set(args.slide_ids) - current_ids
        if missing:
            raise OfficeError(ErrorCode.SLIDE_NOT_FOUND, "one or more slides were not found")
        previous, snapshot = self._next(current)
        targets = set(args.slide_ids)
        snapshot.slides = [slide for slide in snapshot.slides if slide.slide_id not in targets]
        snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        return SlideDeleteResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
            deleted_slide_ids=args.slide_ids,
            slide_count=len(snapshot.slides),
        )

    async def slide_reorder(
        self, scope: RequestScope, args: SlideReorderArgs
    ) -> SlideReorderResult:
        current = await self.store.get(scope, args.presentation_id)
        current_ids = [slide.slide_id for slide in current.slides]
        if len(set(args.slide_ids)) != len(args.slide_ids) or set(args.slide_ids) != set(
            current_ids
        ):
            raise OfficeError(
                ErrorCode.INVALID_SLIDE_ORDER, "supply every current slide ID exactly once"
            )
        previous, snapshot = self._next(current)
        by_id = {slide.slide_id: slide for slide in snapshot.slides}
        snapshot.slides = [by_id[item] for item in args.slide_ids]
        snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        return SlideReorderResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
            slides=self._refs(snapshot),
        )

    async def element_inspect(
        self, scope: RequestScope, args: ElementInspectArgs
    ) -> ElementInspectResult:
        snapshot = await self.store.get(scope, args.presentation_id, args.revision)
        _, slide = self._find_slide(snapshot, args.slide_id)
        soup = BeautifulSoup(slide.html, "html.parser")
        tag = select_element(soup, args.element)
        attributes = {
            key: " ".join(value) if isinstance(value, list) else str(value)
            for key, value in tag.attrs.items()
            if key not in {"style"} and not key.startswith("data-domoxml-")
        }
        styles = parse_styles(str(tag.get("style", ""))) if args.include_styles else None
        clone = BeautifulSoup(str(tag), "html.parser").find(True)
        if clone and args.depth >= 0:

            def trim(node: Tag, depth: int) -> None:
                if depth == 0:
                    for child in list(node.children):
                        if isinstance(child, Tag):
                            child.decompose()
                    return
                for child in list(node.children):
                    if isinstance(child, Tag):
                        trim(child, depth - 1)

            trim(clone, args.depth)
        return ElementInspectResult(
            presentation_id=snapshot.presentation_id,
            revision=snapshot.revision_id,
            slide_id=slide.slide_id,
            element_id=str(tag["data-office-id"]),
            element_name=str(tag["data-office-name"]) if tag.has_attr("data-office-name") else None,
            tag=tag.name,
            text=tag.get_text(" ", strip=True) or None,
            attributes=attributes,
            styles=styles,
            html=model_facing_html(str(clone)) if args.include_html and clone else None,
            child_ids=direct_child_ids(tag),
        )

    async def element_add(self, scope: RequestScope, args: ElementAddArgs) -> ElementAddResult:
        current = await self.store.get(scope, args.presentation_id)
        previous, snapshot = self._next(current)
        _, slide = self._find_slide(snapshot, args.slide_id)
        soup = BeautifulSoup(slide.html, "html.parser")
        relative = select_element(soup, args.relative_to)
        fragment_html, _ = self._sanitize(args.html)
        fragment = BeautifulSoup(fragment_html, "html.parser")
        roots = [item.extract() for item in list(fragment.contents) if isinstance(item, Tag)]
        if args.position is ElementInsertPosition.BEFORE:
            for root in roots:
                relative.insert_before(root)
        elif args.position is ElementInsertPosition.AFTER:
            for root in reversed(roots):
                relative.insert_after(root)
        elif args.position is ElementInsertPosition.PREPEND:
            for root in reversed(roots):
                relative.insert(0, root)
        else:
            for root in roots:
                relative.append(root)
        slide.html = self._sanitize(str(soup), preserve_ids=True, preserve_domoxml=True)[0]
        snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        return ElementAddResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
            slide_id=slide.slide_id,
            roots=[
                AddedElement(
                    element_id=str(root["data-office-id"]),
                    element_name=str(root["data-office-name"])
                    if root.has_attr("data-office-name")
                    else None,
                    tag=root.name,
                )
                for root in roots
            ],
        )

    async def element_update(
        self, scope: RequestScope, args: ElementUpdateArgs
    ) -> ElementUpdateResult:
        current = await self.store.get(scope, args.presentation_id)
        previous, snapshot = self._next(current)
        _, slide = self._find_slide(snapshot, args.slide_id)
        soup = BeautifulSoup(slide.html, "html.parser")
        updated: list[str] = []
        for mutation in args.elements:
            tag = select_element(soup, mutation.element)
            stable_id = str(tag["data-office-id"])
            detach_domoxml_metadata(tag)
            if "text" in mutation.model_fields_set:
                tag.clear()
                tag.append(NavigableString(mutation.text or ""))
            elif "inner_html" in mutation.model_fields_set:
                fragment_html = mutation.inner_html or "<span></span>"
                normalized, _ = self._sanitize(fragment_html)
                fragment = BeautifulSoup(normalized, "html.parser")
                tag.clear()
                for child in list(fragment.contents):
                    tag.append(child.extract())
            elif "replace_html" in mutation.model_fields_set:
                normalized, _ = self._sanitize(mutation.replace_html or "", exactly_one_root=True)
                replacement = BeautifulSoup(normalized, "html.parser").find(True)
                assert replacement is not None
                replacement["data-office-id"] = stable_id
                tag.replace_with(replacement)
                tag = replacement
            if mutation.styles:
                styles = parse_styles(str(tag.get("style", "")))
                for name in mutation.styles.remove:
                    styles.pop(name.lower(), None)
                styles.update({name.lower(): value for name, value in mutation.styles.set.items()})
                tag["style"] = serialize_styles(styles)
            if mutation.attributes:
                for name in mutation.attributes.remove:
                    tag.attrs.pop(name, None)
                for name, value in mutation.attributes.set.items():
                    if name.lower() in {"href", "src"} and value.lower().strip().startswith(
                        ("javascript:", "file:", "http:")
                    ):
                        raise OfficeError(ErrorCode.UNSAFE_HTML, f"unsafe URL in {name}")
                    tag[name] = value
            updated.append(stable_id)
        slide.html = self._sanitize(str(soup), preserve_ids=True, preserve_domoxml=True)[0]
        snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        return ElementUpdateResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
            slide_id=slide.slide_id,
            updated_element_ids=updated,
        )

    async def element_move(self, scope: RequestScope, args: ElementMoveArgs) -> ElementMoveResult:
        current = await self.store.get(scope, args.presentation_id)
        previous, snapshot = self._next(current)
        _, slide = self._find_slide(snapshot, args.slide_id)
        soup = BeautifulSoup(slide.html, "html.parser")
        moved: list[str] = []
        for operation in args.moves:
            tag = select_element(soup, operation.element)
            relative = select_element(soup, operation.relative_to)
            if tag is relative or relative in tag.descendants:
                raise OfficeError(
                    ErrorCode.INVALID_ELEMENT_MOVE,
                    "cannot move an element relative to itself or its descendant",
                )
            moved.append(str(tag["data-office-id"]))
            extracted = tag.extract()
            if operation.position is ElementInsertPosition.BEFORE:
                relative.insert_before(extracted)
            elif operation.position is ElementInsertPosition.AFTER:
                relative.insert_after(extracted)
            elif operation.position is ElementInsertPosition.PREPEND:
                relative.insert(0, extracted)
            else:
                relative.append(extracted)
        slide.html = self._sanitize(str(soup), preserve_ids=True, preserve_domoxml=True)[0]
        snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        return ElementMoveResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
            slide_id=slide.slide_id,
            moved_element_ids=moved,
        )

    async def element_delete(
        self, scope: RequestScope, args: ElementDeleteArgs
    ) -> ElementDeleteResult:
        current = await self.store.get(scope, args.presentation_id)
        previous, snapshot = self._next(current)
        _, slide = self._find_slide(snapshot, args.slide_id)
        soup = BeautifulSoup(slide.html, "html.parser")
        tags = [select_element(soup, selector) for selector in args.elements]
        ids = [str(tag["data-office-id"]) for tag in tags]
        if len(set(ids)) != len(ids):
            raise OfficeError(ErrorCode.INVALID_HTML, "duplicate element selectors are not allowed")
        roots = [item for item in soup.contents if isinstance(item, Tag)]
        if len(roots) == 1 and roots[0] in tags:
            raise OfficeError(ErrorCode.INVALID_HTML, "cannot delete the sole slide root element")
        for tag in tags:
            tag.decompose()
        slide.html = self._sanitize(str(soup), preserve_ids=True, preserve_domoxml=True)[0]
        snapshot.content_changed_after_import = True
        await self.store.commit(scope, snapshot, args.expected_revision)
        return ElementDeleteResult(
            presentation_id=snapshot.presentation_id,
            previous_revision=previous,
            revision=snapshot.revision_id,
            slide_id=slide.slide_id,
            deleted_element_ids=ids,
        )

    async def validate(
        self, scope: RequestScope, args: PresentationValidateArgs
    ) -> PresentationValidationResult:
        snapshot = await self.store.get(scope, args.presentation_id, args.revision)
        selected = args.slide_ids or [slide.slide_id for slide in snapshot.slides]
        if len(set(selected)) != len(selected):
            raise OfficeError(ErrorCode.SLIDE_NOT_FOUND, "duplicate slide IDs are not allowed")
        indices = [self._find_slide(snapshot, item)[0] for item in selected]
        cache_key = (scope.key, snapshot.revision_id, ",".join(selected) + ":" + args.detail.value)
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]
        coverage: list[CoverageItem] = []
        warnings: list[ValidationWarning] = []
        selected_numbers = {index + 1 for index in indices}
        for warning in snapshot.import_warnings:
            number_value = warning.get("slide_number")
            number = int(number_value) if isinstance(number_value, int | str) else None
            if number is not None and number not in selected_numbers:
                continue
            warnings.append(
                ValidationWarning(
                    code=str(warning.get("code", "DOMOXML_WARNING")),
                    message=str(warning.get("message", "Imported source has fidelity debt")),
                    slide_id=snapshot.slides[number - 1].slide_id if number else None,
                    element=str(warning["element"]) if warning.get("element") else None,
                )
            )
        use_reverse_coverage = bool(
            snapshot.imported_pptx_b64
            and not snapshot.content_changed_after_import
            and snapshot.imported_coverage
        )
        if use_reverse_coverage:
            for item in snapshot.imported_coverage:
                number_value = item.get("slide_number")
                if not isinstance(number_value, int) or number_value not in selected_numbers:
                    continue
                output_value = item.get("output_count", 0)
                raster_value = item.get("raster_area_emu2", 0)
                coverage.append(
                    CoverageItem(
                        slide_id=snapshot.slides[number_value - 1].slide_id,
                        element=str(item.get("element", "imported element")),
                        representation=Representation(str(item.get("representation", "failed"))),
                        editability=Editability(str(item.get("editability", "none"))),
                        source_retention=SourceRetention(str(item.get("source_retention", "lost"))),
                        output_count=int(output_value)
                        if isinstance(output_value, int | str)
                        else 0,
                        raster_area_emu2=int(raster_value)
                        if isinstance(raster_value, int | str)
                        else 0,
                        reason=str(item.get("reason", "")),
                    )
                )
        for index in [] if use_reverse_coverage else indices:
            slide = snapshot.slides[index]
            result = await self.adapter.validate(snapshot, {index})
            if result is None:
                continue
            for item in result.coverage.items:
                coverage.append(
                    CoverageItem(
                        slide_id=slide.slide_id,
                        element=item.element,
                        representation=Representation(item.representation.value),
                        editability=Editability(item.editability.value),
                        source_retention=SourceRetention(item.source_retention.value),
                        output_count=item.output_count,
                        raster_area_emu2=item.raster_area_emu2,
                        reason=item.reason,
                    )
                )
            warnings.extend(
                ValidationWarning(
                    code="DOMOXML_WARNING",
                    message=item.message,
                    slide_id=slide.slide_id,
                    element=item.element or None,
                )
                for item in result.warnings
            )
        if snapshot.content_changed_after_import and snapshot.imported_preservation:
            warnings.append(
                ValidationWarning(
                    code="PRESERVATION_DEBT",
                    message=(
                        "Imported source-only OOXML fragments cannot be reattached by the "
                        "current domOXML public API after edits; inspect the affected slides."
                    ),
                )
            )
            for fragment in snapshot.imported_preservation:
                part = str(fragment.get("part", ""))
                match = re.search(r"(?:^|/)slide(\d+)\.xml", part, re.IGNORECASE)
                if not match:
                    continue
                number = int(match.group(1))
                if number not in selected_numbers:
                    continue
                coverage.append(
                    CoverageItem(
                        slide_id=snapshot.slides[number - 1].slide_id,
                        element=str(fragment.get("owner_node_id") or part),
                        representation=Representation.APPROXIMATED,
                        editability=Editability.NONE,
                        source_retention=SourceRetention.LOST,
                        output_count=0,
                        raster_area_emu2=0,
                        reason="source-only OOXML preservation fragment is detached after edit",
                    )
                )
        mixed_sizes = self.adapter.mixed_size_indices(snapshot) & set(indices)
        for index in sorted(mixed_sizes):
            slide = snapshot.slides[index]
            warnings.append(
                ValidationWarning(
                    code="MIXED_SLIDE_SIZE_UNSUPPORTED",
                    message=(
                        "PowerPoint export requires one presentation-wide slide size; "
                        "this per-slide override is preview-only until normalized."
                    ),
                    slide_id=slide.slide_id,
                    element="slide-size",
                )
            )
            coverage.append(
                CoverageItem(
                    slide_id=slide.slide_id,
                    element="slide-size",
                    representation=Representation.FAILED,
                    editability=Editability.NONE,
                    source_retention=SourceRetention.NOT_REQUIRED,
                    output_count=0,
                    raster_area_emu2=0,
                    reason="effective slide size differs from presentation-wide PPTX size",
                )
            )
        failures = sum(item.representation is Representation.FAILED for item in coverage)
        count = len(coverage)
        native = sum(
            item.representation in {Representation.NATIVE, Representation.DECOMPOSED}
            for item in coverage
        )
        editable = sum(
            item.editability in {Editability.SEMANTIC, Editability.COMPONENTS} for item in coverage
        )
        layered = sum(
            item.representation
            in {
                Representation.HYBRID,
                Representation.LAYERED,
                Representation.ELEMENT_LAYER,
                Representation.RASTERIZED,
            }
            for item in coverage
        )
        result = PresentationValidationResult(
            presentation_id=snapshot.presentation_id,
            revision=snapshot.revision_id,
            valid=failures == 0,
            slide_count=len(indices),
            native_ratio=native / count if count else 1.0,
            editable_ratio=editable / count if count else 1.0,
            layered_ratio=layered / count if count else 0.0,
            warning_count=len(warnings),
            failed_count=failures,
            warnings=warnings,
            coverage=coverage if args.detail is ValidationDetail.FULL else None,
        )
        if len(self._validation_cache) >= self._MAX_VALIDATION_CACHE_ENTRIES:
            self._validation_cache.pop(next(iter(self._validation_cache)))
        self._validation_cache[cache_key] = result
        return result

    def _preview_indices(
        self, snapshot: PresentationSnapshot, selection: PreviewSelection
    ) -> list[int]:
        if isinstance(selection, PreviewAll):
            indices = list(range(len(snapshot.slides)))
            if not indices:
                raise OfficeError(ErrorCode.SLIDE_NOT_FOUND, "presentation has no slides")
            return indices
        if isinstance(selection, PreviewRange):
            if selection.end > len(snapshot.slides):
                raise OfficeError(
                    ErrorCode.SLIDE_NOT_FOUND, "preview range exceeds the slide count"
                )
            return list(range(selection.start - 1, selection.end))
        assert isinstance(selection, PreviewSlides)
        indices = [self._find_slide(snapshot, item)[0] for item in selection.slide_ids]
        if len(set(indices)) != len(indices):
            raise OfficeError(ErrorCode.SLIDE_NOT_FOUND, "duplicate preview slide IDs are invalid")
        # domOXML's public indices API renders in deck order. Keep metadata in
        # the same order so each image always maps to the correct stable ID.
        return sorted(indices)

    async def preview(
        self, scope: RequestScope, args: PresentationPreviewArgs
    ) -> tuple[list[bytes], PresentationPreviewResult]:
        snapshot = await self.store.get(scope, args.presentation_id, args.revision)
        indices = self._preview_indices(snapshot, args.selection)
        chosen_ids = [snapshot.slides[index].slide_id for index in indices]
        key = hashlib.sha256(
            (scope.key + snapshot.revision_id + args.model_dump_json()).encode()
        ).hexdigest()
        if key in self._preview_cache:
            return self._preview_cache[key]
        pngs = list(await self.adapter.preview_pngs(snapshot, set(indices)))
        layout = args.layout
        if layout is PreviewLayout.AUTO:
            layout = PreviewLayout.SINGLE if len(indices) == 1 else PreviewLayout.CONTACT_SHEET
        images: list[bytes]
        descriptors: list[PreviewImageDescriptor]
        if layout is PreviewLayout.SINGLE:
            if len(indices) != 1:
                raise OfficeError(
                    ErrorCode.RENDER_FAILED,
                    "single preview layout requires exactly one selected slide",
                )
            import io

            from PIL import Image

            image = Image.open(io.BytesIO(pngs[0]))
            images = pngs
            descriptors = [
                PreviewImageDescriptor(
                    page=1, slide_ids=chosen_ids, width_px=image.width, height_px=image.height
                )
            ]
        else:
            sheets = contact_sheets(
                pngs,
                chosen_ids,
                [snapshot.slides[index].name for index in indices],
                args.labels,
                args.quality,
                args.columns,
            )
            images = [sheet.png for sheet in sheets]
            descriptors = [
                PreviewImageDescriptor(
                    page=page,
                    slide_ids=sheet.slide_ids,
                    width_px=sheet.width,
                    height_px=sheet.height,
                )
                for page, sheet in enumerate(sheets, start=1)
            ]
        result = PresentationPreviewResult(
            presentation_id=snapshot.presentation_id,
            revision=snapshot.revision_id,
            layout=layout,
            images=descriptors,
        )
        if len(self._preview_cache) >= self._MAX_PREVIEW_CACHE_ENTRIES:
            self._preview_cache.pop(next(iter(self._preview_cache)))
        self._preview_cache[key] = (images, result)
        return images, result

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        cleaned = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", filename).strip(" .")
        reserved = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            *(f"COM{i}" for i in range(1, 10)),
            *(f"LPT{i}" for i in range(1, 10)),
        }
        if not cleaned or cleaned.split(".")[0].upper() in reserved:
            cleaned = "presentation"
        if not cleaned.lower().endswith(".pptx"):
            cleaned += ".pptx"
        return cleaned[:255]

    async def export(
        self, scope: RequestScope, args: PresentationExportArgs
    ) -> PresentationExportResult:
        snapshot = await self.store.get(scope, args.presentation_id, args.revision)
        filename = self.sanitize_filename(args.filename or snapshot.name)
        uri = f"office://presentations/{snapshot.presentation_id}/revisions/{snapshot.revision_id}/file"
        # A revision URI is immutable.  Reuse the first published artifact so
        # repeated exports and resource reads are byte-for-byte idempotent even
        # when an OOXML writer varies ZIP metadata between compilations.
        data = await self.output.read(scope, uri)
        if data is None:
            data, _ = await self.adapter.export_pptx(snapshot)
            validate_pptx(data, self.config)
            await self.output.publish(scope, uri, data)
        return PresentationExportResult(
            presentation_id=snapshot.presentation_id,
            revision=snapshot.revision_id,
            filename=filename,
            mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            size_bytes=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            resource_uri=uri,
        )

    async def delete(
        self, scope: RequestScope, args: PresentationDeleteArgs
    ) -> PresentationDeleteResult:
        await self.store.delete(scope, args.presentation_id, args.expected_revision)
        await self.output.delete_presentation(scope, args.presentation_id)
        self._preview_cache.clear()
        self._validation_cache.clear()
        return PresentationDeleteResult(presentation_id=args.presentation_id)

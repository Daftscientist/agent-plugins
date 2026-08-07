# Repository agent rules

- Every directory under `plugins/` is an independently packageable Agent Plugin.
- Read the nearest plugin `AGENTS.md` and design contract completely before changing it.
- Keep portable plugin behavior independent of any particular client or future host.
- Never commit generated runtime state, credentials, local environments, or presentation data.
- Run the plugin's complete lint, type, and test gates before pushing.

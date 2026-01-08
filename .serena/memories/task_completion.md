# Task Completion Checklist
- Run relevant automated checks: backend pytest with coverage; frontend `npm run test`, `npm run lint`, `npm run type-check`; re-run formatters if needed.
- Ensure migrations/DB seeds are applied when schema changes (`alembic upgrade head`, update seed scripts).
- Confirm i18n keys added for any new UI text; keep EN-US source strings and translations synced.
- Verify ACL coverage: new actions/resources must have rules and UI gating (`useACL()`, middleware) plus status-driven transitions.
- Update documentation or inline comments for new behaviors (especially AI transparency, audit/versioned CRUD flows).
- If containers were started, stop/clean as appropriate; summarize remaining risks/todos in the handoff.

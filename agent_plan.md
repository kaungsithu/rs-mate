# RSMate Improvement Plan

## Current State Summary

RSMate is a functional web-based tool for managing Amazon Redshift users, roles, groups, and privileges. It is built on FastHTML + MonsterUI + HTMX with a Python backend. The app works but has significant issues that prevent production readiness:

- **Performance**: N+1 query patterns throughout, no connection pooling, sequential queries where batching is possible. A detail page for a single user or role can fire 40+ individual queries.
- **Modularity**: `app.py` is a 1015-line monolith containing all 46 routes. Component files are 400-500+ lines each.
- **Security**: 15+ SQL injection vulnerabilities via f-string interpolation in DDL/DCL statements. Pickle-based session serialization. No session expiration. No CSRF protection.
- **UI/UX**: No client-side caching, full page reloads on navigation, no optimistic updates, limited loading state feedback, broad error catching with generic messages.
- **Testing**: Zero test files. pytest is in CI but discovers nothing.
- **Local development**: No way to test without a live Redshift cluster.

---

## Phase 1: Local Redshift Emulator & Test Foundation

**Goal**: Establish a local testing environment and baseline test infrastructure so all subsequent phases can be validated.

**Success Criteria**: A developer can run `docker compose up` to get a local Redshift-compatible database, and `pytest` discovers and passes all foundation tests.

### Task 1.1: Set Up LocalStack or PostgreSQL-based Redshift Emulator

- Research and select an emulation approach. Redshift is PostgreSQL-compatible, so the recommended path is a Docker Compose file with a PostgreSQL 14+ container that mimics Redshift system views.
- Create a `docker-compose.yml` at the project root with a PostgreSQL service named `redshift-emulator` on port 5439 (Redshift default).
- Create a directory `tests/fixtures/` to hold SQL seed scripts.
- Create `tests/fixtures/init_schema.sql` that:
  - Creates the system catalog views RSMate queries (`pg_user_info`, `svv_roles`, `svv_role_grants`, `pg_group`, `svv_user_grants`, `svv_relation_privileges`, etc.) as regular tables or views that return compatible column structures.
  - Seeds sample data: at least 20 users, 10 roles, 5 groups, 15 schemas, 200 tables spread across schemas, and privilege grants connecting them.
- Create `tests/fixtures/seed_data.sql` with INSERT statements for the sample data above.
- Create a `tests/conftest.py` with:
  - A `db_connection` pytest fixture that connects to the local PostgreSQL emulator using `psycopg2` or `redshift_connector` (which supports PostgreSQL protocol).
  - A `seeded_db` fixture that runs `init_schema.sql` and `seed_data.sql` before each test session and rolls back or drops after.
  - A `mock_session` fixture that provides a fake session dictionary with encrypted connection info pointing to the emulator.
- Update `requirements.txt` to add `pytest`, `pytest-cov`, `psycopg2-binary` (or keep `redshift_connector` if it can connect to plain PostgreSQL).

**Tests for this task:**
- `tests/test_emulator_setup.py`:
  - Test that the emulator connection succeeds.
  - Test that the seeded database contains the expected number of users, roles, groups, schemas, and tables.
  - Test that the system catalog views return data in the expected column format.

### Task 1.2: Add Test Infrastructure and CI Integration

- Create `pytest.ini` or `pyproject.toml` section with:
  - Test paths: `tests/`
  - Coverage target: `--cov=redshift --cov=components --cov=helpers --cov-report=term-missing`
  - Markers: `unit`, `integration`, `slow`
- Update `.github/workflows/python-app.yml`:
  - Add a Docker Compose service step that starts the emulator before tests.
  - Run `pytest --cov` instead of plain `pytest`.
  - Add a coverage threshold check (fail if below 50% initially, raise as coverage grows).
- Create `tests/__init__.py` (empty).
- Create `tests/unit/__init__.py` and `tests/integration/__init__.py` (empty).

**Tests for this task:**
- `tests/test_ci_smoke.py`:
  - A trivial test that imports the main modules (`redshift.user`, `redshift.role`, `redshift.group`, `redshift.database`, `redshift.sql_queries`, `helpers.session_helper`) without error.
  - A test that verifies the Fernet key generation works.

### Task 1.3: Write Baseline Model Layer Tests

- Create `tests/unit/test_user_model.py`:
  - Test `RSUser.get_all()` returns a list of `RSUser` dataclass instances.
  - Test `RSUser.get_user()` returns a fully populated user with groups, roles, and privileges.
  - Test `RSUser.create_user()` with valid inputs creates a user.
  - Test `RSUser.drop_user()` removes a user.
  - Test user password change operation.
- Create `tests/unit/test_role_model.py`:
  - Test `RSRole.get_all()` returns a list of `RSRole` instances.
  - Test `RSRole.get_role()` returns a role with users, nested roles, and privileges.
  - Test `RSRole.create_role()` and `RSRole.drop_role()`.
  - Test granting and revoking role membership.
- Create `tests/unit/test_group_model.py`:
  - Test `RSGroup.get_all()` returns a list of `RSGroup` instances.
  - Test `RSGroup.get_group()` returns a group with its members.
  - Test `RSGroup.create_group()` and `RSGroup.drop_group()`.
  - Test adding and removing users from groups.
- Create `tests/unit/test_sql_queries.py`:
  - Test that every query string in `sql_queries.py` is valid SQL (no syntax errors) by running `EXPLAIN` or `PREPARE` against the emulator.
  - Test that parameterized queries with sample values return expected column names.

**Success Criteria**: `pytest` passes all model tests against the local emulator. Coverage for the `redshift/` directory reaches at least 40%.

---

## Phase 2: Security Hardening

**Goal**: Eliminate all SQL injection vulnerabilities, improve credential storage, add session security, and introduce CSRF protection.

**Success Criteria**: No SQL statement uses f-string interpolation with user-supplied data. All credentials are encrypted at rest. Sessions expire after inactivity. All security tests pass.

### Task 2.1: Fix SQL Injection in User Operations

- Open `redshift/user.py`.
- Locate every instance of f-string SQL construction (approximately lines 59-77 in `create_user()`, lines 194-233 in `get_alt_user_sql()`).
- Redshift DDL/DCL statements (`CREATE USER`, `ALTER USER`, `GRANT`, `REVOKE`) do not support parameterized identifiers. The fix is to:
  - Create a utility function `validate_identifier(name: str) -> str` in a new file `redshift/sanitize.py` that validates identifiers against a strict allowlist regex (`^[a-zA-Z_][a-zA-Z0-9_]{0,126}$`) and raises `ValueError` for anything else.
  - Create a utility function `escape_literal(value: str) -> str` that doubles single quotes and wraps in single quotes for string literals.
  - Replace all f-string interpolations with calls to these utility functions.
- Update `create_user()`, `alter_user()`, `drop_user()`, `rename_user()`, and all privilege grant/revoke functions to use the sanitized values.

**Tests:**
- `tests/unit/test_sanitize.py`:
  - Test `validate_identifier()` accepts valid SQL identifiers.
  - Test `validate_identifier()` rejects identifiers with special characters, SQL keywords injection attempts (e.g., `admin; DROP TABLE users--`), empty strings, and strings exceeding 127 characters.
  - Test `escape_literal()` properly escapes single quotes, backslashes, and null bytes.
- `tests/unit/test_user_security.py`:
  - Test that `create_user()` with a malicious username raises `ValueError`.
  - Test that `create_user()` with a password containing single quotes does not break the SQL.

### Task 2.2: Fix SQL Injection in Role and Group Operations

- Open `redshift/role.py`. Locate all f-string SQL (approximately lines 223, 251, 272, 298, 361-366).
- Apply the same `validate_identifier()` and `escape_literal()` treatment to all role DDL/DCL operations: `create_role()`, `drop_role()`, `grant_role()`, `revoke_role()`, and all privilege operations.
- Open `redshift/group.py`. Locate all f-string SQL (approximately lines 104, 130, 189, 213).
- Apply the same sanitization to all group DDL/DCL operations: `create_group()`, `drop_group()`, `add_users_to_group()`, `remove_users_from_group()`.

**Tests:**
- `tests/unit/test_role_security.py`:
  - Test that `create_role()` with malicious role name raises `ValueError`.
  - Test that `grant_role()` with injection attempts in role or user name raises `ValueError`.
- `tests/unit/test_group_security.py`:
  - Test that `create_group()` with malicious group name raises `ValueError`.
  - Test that `add_users_to_group()` with injection attempts raises `ValueError`.

### Task 2.3: Replace Pickle Serialization with JSON

- Open `helpers/session_helper.py`.
- Replace `pickle.dumps()` / `pickle.loads()` with `json.dumps()` / `json.loads()`.
- Update `sess_store_obj()` to serialize dataclass objects to dictionaries using a custom encoder or `dataclasses.asdict()` before JSON serialization.
- Update `sess_get_obj()` to deserialize JSON back to the expected dataclass type by accepting a `cls` parameter.
- Update all call sites in `app.py` that use `sess_store_obj()` and `sess_get_obj()` to pass the appropriate class.

**Tests:**
- `tests/unit/test_session_helper.py`:
  - Test round-trip serialization/deserialization of `RSUser`, `RSRole`, `RSGroup` objects.
  - Test that deserialization of a tampered hex string raises an error (not arbitrary code execution).
  - Test that `sess_get_obj()` returns `None` for missing session keys.
  - Test backward compatibility: if an old pickle-format value exists in session, it is handled gracefully (returns None or triggers re-login).

### Task 2.4: Add Session Expiration and CSRF Protection

- In `app.py` (or a new middleware file `middleware.py`), add session expiration logic:
  - Store a `session_created_at` timestamp when a database connection is established.
  - On each request, check if the session is older than a configurable timeout (default 30 minutes). If expired, clear the session and redirect to the login page with a toast message.
- Add CSRF protection:
  - Generate a CSRF token per session and store it in the session.
  - Include the token as a hidden field in all forms (create a helper `mk_csrf_field(session)` in `components/common.py`).
  - Validate the token on all POST/PUT/DELETE requests.
- Add the Fernet key to a `.env` file pattern:
  - Create a `.env.example` file with `RSMATE_FERNET_KEY=` placeholder.
  - Add `.env` to `.gitignore` if not already present.
  - Document that production deployments must set this environment variable.

**Tests:**
- `tests/unit/test_session_expiry.py`:
  - Test that a session with a timestamp older than 30 minutes is detected as expired.
  - Test that a fresh session is not expired.
  - Test that a session without a timestamp is treated as expired (forces re-login).
- `tests/unit/test_csrf.py`:
  - Test that `mk_csrf_field()` generates a hidden input with a token value.
  - Test that a request with a valid CSRF token passes validation.
  - Test that a request with a missing or invalid CSRF token is rejected.

---

## Phase 3: Performance Optimization

**Goal**: Eliminate N+1 queries, add connection pooling, implement batch operations, and add caching where appropriate.

**Success Criteria**: A user detail page fires no more than 5 queries (down from 40+). Privilege save operations use batch SQL. Connection pooling is active. Performance tests pass within defined time budgets.

### Task 3.1: Implement Connection Pooling

- Open `redshift/database.py`.
- Replace the current pattern of opening a new connection per query with a connection pool.
- Implement a simple connection pool class `ConnectionPool` in `redshift/database.py`:
  - Constructor accepts `min_connections` (default 2), `max_connections` (default 10), and connection parameters.
  - `get_connection()` returns an available connection or creates a new one (up to max).
  - `release_connection(conn)` returns a connection to the pool.
  - `close_all()` closes all pooled connections.
  - Use a thread-safe queue (`queue.Queue`) internally.
- Update `RSDatabase` class to use the pool instead of creating connections per query.
- Add a `close()` or `shutdown()` method to `RSDatabase` that drains the pool.

**Tests:**
- `tests/unit/test_connection_pool.py`:
  - Test that the pool returns connections up to `max_connections`.
  - Test that requesting a connection beyond `max_connections` blocks (with timeout).
  - Test that released connections are reused (connection identity check).
  - Test that `close_all()` closes all connections.
  - Test that a broken/closed connection is discarded and replaced.

### Task 3.2: Batch Schema and Relation Queries

- Open `redshift/sql_queries.py`.
- Create new batch query constants:
  - `GET_ALL_SCHEMAS_WITH_RELATIONS`: A single query that returns schemas with their tables, views, functions, and procedures in one result set, with a `relation_type` column to distinguish them.
  - `GET_USER_PRIVILEGES_BATCH`: A query that fetches all privileges for a user across all schemas in one call.
  - `GET_ROLE_PRIVILEGES_BATCH`: A query that fetches all privileges for a role across all schemas in one call.
- Open `redshift/user.py` and `redshift/role.py`:
  - Add a new method `get_schema_relations_batch(db, schema_list)` that uses the batch query.
  - Modify `get_user_privileges()` and `get_role_privileges()` to use the batch privilege query.
- Open `app.py`:
  - Refactor the `/user/{user_id}` route (lines 139-183) to use the batch method instead of looping per schema.
  - Refactor the `/role/{role_name}` route (lines 489-532) similarly.
  - Refactor the privilege save routes to batch GRANT/REVOKE statements where possible (combine multiple grants of the same type into single statements: `GRANT SELECT ON table1, table2, table3 TO user`).

**Tests:**
- `tests/integration/test_batch_queries.py`:
  - Test that `GET_ALL_SCHEMAS_WITH_RELATIONS` returns correct data for the seeded database (20 users, 15 schemas, 200 tables).
  - Test that the batch privilege query returns the same data as the individual queries.
  - Test that the batched route handler produces the same response data as the original.
  - Test that the number of queries executed for a user detail page is 5 or fewer (instrument query counting in the test).

### Task 3.3: Optimize User/Role Detail Loading

- In `redshift/user.py`, refactor `get_user()` (lines 143-160):
  - Replace the 5 sequential queries with a maximum of 2-3 queries by joining user info, groups, and roles into combined queries.
  - Use `GET_USER_PRIVILEGES_BATCH` from Task 3.2 for privilege loading.
- In `redshift/role.py`, refactor `get_role()` (lines 57-89):
  - Combine the 4 sequential queries into 2 by joining role membership and nested roles.
  - Use `GET_ROLE_PRIVILEGES_BATCH` for privilege loading.
- For list pages (`get_all()` methods), keep them lightweight (no related data loaded) since the UI uses HTMX lazy loading.

**Tests:**
- `tests/integration/test_user_detail_perf.py`:
  - Test that `get_user()` completes within 2 seconds for a user with 50 privileges across 10 schemas (against the emulator).
  - Test that the returned `RSUser` object has all expected fields populated (groups, roles, privileges).
- `tests/integration/test_role_detail_perf.py`:
  - Test that `get_role()` completes within 2 seconds for a role with 50 privileges.
  - Test that the returned `RSRole` object has all expected fields populated.

### Task 3.4: Add Server-Side Caching for Schema Metadata

- Create a new file `redshift/cache.py` with a simple TTL cache:
  - `class TTLCache` with `get(key)`, `set(key, value, ttl_seconds)`, and `invalidate(key)` methods.
  - Default TTL of 300 seconds (5 minutes) for schema metadata.
  - Thread-safe using `threading.Lock`.
- Cache the following in `app.py`:
  - Schema list (invalidate on schema creation/deletion).
  - Schema relations (tables, views, functions, procedures per schema) — invalidate on privilege changes.
- Add a "Refresh" button in the UI privilege pages that clears the cache and reloads.

**Tests:**
- `tests/unit/test_cache.py`:
  - Test that `set()` and `get()` work for basic key-value pairs.
  - Test that values expire after TTL.
  - Test that `invalidate()` removes a specific key.
  - Test thread safety: concurrent reads and writes do not cause errors.

---

## Phase 4: Modularization

**Goal**: Break the monolithic `app.py` into focused route modules. Split large component files. Establish clear module boundaries.

**Success Criteria**: `app.py` is under 100 lines (just setup and imports). Each route module is under 300 lines. All existing tests still pass. No functionality is lost.

### Task 4.1: Create Route Module Structure

- Create a directory `routes/` with an `__init__.py`.
- Create the following route module files:
  - `routes/database.py` — Database connection routes (2 routes).
  - `routes/user.py` — User management routes (11 routes).
  - `routes/user_privileges.py` — User privilege/schema routes (14 routes).
  - `routes/role.py` — Role management routes (11 routes).
  - `routes/role_privileges.py` — Role privilege/schema routes (8 routes).
  - `routes/group.py` — Group management routes (5 routes).
- Each module should export a function `register_routes(app)` that takes the FastHTML app instance and registers all its routes using `@app.rt()`.

**Tests:**
- `tests/unit/test_route_modules.py`:
  - Test that each route module can be imported without error.
  - Test that `register_routes()` is callable for each module.
  - Test that the total number of registered routes across all modules equals 46 (or the current total, accounting for any consolidation).

### Task 4.2: Extract Routes from app.py

- Move each group of routes from `app.py` to its corresponding module:
  - Move database connection routes (lines 29-49) to `routes/database.py`.
  - Move user routes (lines 56-211) to `routes/user.py`.
  - Move user privilege routes (lines 212-468) to `routes/user_privileges.py`.
  - Move role routes (lines 471-616) to `routes/role.py`.
  - Move role privilege routes (lines 617-878) to `routes/role_privileges.py`.
  - Move group routes (lines 902-1006) to `routes/group.py`.
- Each route function needs access to the session and database connection. Pass these through FastHTML's request/session mechanism (already available via function parameters).
- Extract shared helper functions used across routes into `routes/helpers.py`:
  - Session validation helper (check if connected to database).
  - Schema/relation fetching helper (used by both user and role privilege routes).
  - Toast notification helper.
- Refactor `app.py` to:
  - Import and call `register_routes()` from each module.
  - Keep only app initialization, middleware setup, and static file configuration.
  - Target: under 100 lines.

**Tests:**
- `tests/integration/test_routes_integration.py`:
  - Test that the app starts without errors after refactoring.
  - Test that key routes return expected HTTP status codes (200 for GET pages, 302 for redirects).
  - Test that the database connection flow works end-to-end (POST connection info, verify session is populated).
  - Test at least one CRUD operation per entity type (user, role, group) through the route layer.

### Task 4.3: Split Large Component Files

- Split `components/user.py` (527 lines) into:
  - `components/user/list.py` — User list table component (`mk_user_table`, `mk_user_list_item`).
  - `components/user/form.py` — User creation/edit form components (`mk_user_form`, `mk_user_edit_form`).
  - `components/user/privileges.py` — User privilege UI (`mk_user_privileges`, `mk_privilege_table`).
  - `components/user/__init__.py` — Re-exports all public names for backward compatibility.
- Split `components/role.py` (447 lines) into:
  - `components/role/list.py` — Role list components.
  - `components/role/form.py` — Role creation/edit forms.
  - `components/role/privileges.py` — Role privilege UI.
  - `components/role/__init__.py` — Re-exports.
- Keep `components/group.py` (149 lines) as-is since it is a reasonable size.
- Keep `components/common.py` (84 lines) and `components/database.py` (33 lines) as-is.

**Tests:**
- `tests/unit/test_component_imports.py`:
  - Test that importing from `components.user` still works (backward compatibility).
  - Test that importing specific submodules (`components.user.list`, `components.user.form`, `components.user.privileges`) works.
  - Test that all `mk_*()` functions are importable and callable (with mock data, verify they return FastHTML elements).

### Task 4.4: Extract Business Logic from Routes

- Identify business logic currently in route handlers (e.g., computing privilege diffs, determining which grants/revokes to execute).
- Create a `services/` directory with:
  - `services/__init__.py`
  - `services/user_service.py` — User CRUD orchestration, privilege diff computation, batch grant/revoke execution.
  - `services/role_service.py` — Role CRUD orchestration, privilege management.
  - `services/group_service.py` — Group CRUD orchestration.
- Move business logic from route handlers into service functions. Route handlers should only:
  - Parse request parameters.
  - Call service functions.
  - Return UI components or redirects.

**Tests:**
- `tests/unit/test_user_service.py`:
  - Test privilege diff computation: given current privileges and desired privileges, produce correct grant/revoke lists.
  - Test that batch grant/revoke produces the expected SQL commands.
- `tests/unit/test_role_service.py`:
  - Test role membership diff computation.
  - Test privilege diff for roles.
- `tests/unit/test_group_service.py`:
  - Test group membership diff computation.

---

## Phase 5: UI/UX Improvements

**Goal**: Smoother interactions, better loading states, optimistic updates, improved error messages, and client-side navigation state.

**Success Criteria**: All pages show loading indicators during data fetch. Error messages are specific and actionable. Navigation does not lose state. Form submissions provide immediate feedback.

### Task 5.1: Improve Loading States and Skeleton Screens

- In `components/common.py`, create a `mk_skeleton_row(columns: int)` function that returns a table row with pulsating placeholder elements (using MonsterUI's animation utilities or a simple CSS class).
- Create a `mk_skeleton_table(rows: int, columns: int)` that renders a full skeleton table.
- Update user list, role list, and group list components to show skeleton tables while HTMX requests are in flight:
  - Use `hx-indicator` to show loading state.
  - Use `hx-swap="innerHTML transition:true"` for smoother transitions.
- For privilege pages, show a skeleton grid while schema data loads.

**Tests:**
- `tests/unit/test_skeleton_components.py`:
  - Test that `mk_skeleton_row(5)` returns an element with 5 child cells.
  - Test that `mk_skeleton_table(10, 5)` returns a table with 10 rows.
  - Test that skeleton elements have the expected CSS classes.

### Task 5.2: Improve Error Handling and User Feedback

- Create `components/error.py` with:
  - `mk_error_toast(message, error_type)` — Different styling for connection errors, validation errors, permission errors, and unexpected errors.
  - `mk_inline_error(message)` — For form field validation errors displayed inline.
  - `mk_error_page(title, message, retry_url)` — Full-page error display with a retry button.
- In `app.py` (or the new route modules), replace all broad `except Exception` blocks with specific exception handling:
  - `redshift_connector.InterfaceError` — Connection lost, show reconnect prompt.
  - `redshift_connector.ProgrammingError` — SQL error, show the specific message.
  - `ValueError` — Input validation failed, show which field is invalid.
  - `PermissionError` — Insufficient Redshift privileges, show which privilege is needed.
- Add a global error handler (FastHTML's exception handling mechanism) that catches unhandled exceptions and shows a friendly error page instead of a stack trace.

**Tests:**
- `tests/unit/test_error_components.py`:
  - Test that `mk_error_toast()` produces the correct HTML structure for each error type.
  - Test that `mk_inline_error()` produces a form error element.
  - Test that `mk_error_page()` includes the retry URL.
- `tests/integration/test_error_handling.py`:
  - Test that a connection failure results in a connection error toast (not a generic error).
  - Test that an invalid user creation (e.g., duplicate name) results in a specific error message.

### Task 5.3: Add Confirmation Dialogs and Undo Support

- Review all destructive operations (drop user, drop role, drop group, revoke privileges).
- Ensure every destructive operation has a confirmation modal that:
  - Names the entity being affected.
  - Describes the consequences (e.g., "This will remove all privileges and group memberships for user X").
  - Requires explicit confirmation (a button labeled with the action, not just "OK").
- For privilege save operations, implement a preview step:
  - Before executing grants/revokes, show a summary dialog listing all changes that will be made.
  - Allow the user to confirm or cancel.
  - This reuses the privilege diff logic from the service layer (Phase 4, Task 4.4).
- For group/role membership changes, show a similar preview.

**Tests:**
- `tests/unit/test_confirmation_dialogs.py`:
  - Test that the drop user confirmation modal contains the username.
  - Test that the privilege change preview lists the correct grants and revokes.
  - Test that the confirmation button has the correct HTMX attributes.

### Task 5.4: Improve Navigation and State Persistence

- Add breadcrumb navigation to all pages:
  - Create `mk_breadcrumb(items)` in `components/common.py` where items is a list of `(label, url)` tuples.
  - Add breadcrumbs to: user detail, role detail, group detail, privilege pages.
- Preserve filter/search state across navigation:
  - Use URL query parameters to store the current search term and filter state.
  - When navigating back to a list page, restore the previous search/filter from query parameters.
  - Update List.js configuration to sync with URL query parameters.
- Add keyboard shortcuts:
  - `Escape` to close modals.
  - `Ctrl+S` / `Cmd+S` to save forms (prevent default browser save dialog).
  - Document shortcuts in a help tooltip accessible from the header.

**Tests:**
- `tests/unit/test_breadcrumbs.py`:
  - Test that `mk_breadcrumb()` generates correct navigation links.
  - Test that the current page item is not a link (just text).
- `tests/unit/test_navigation_state.py`:
  - Test that search parameters are preserved in generated URLs.

### Task 5.5: Add Bulk Operations UI

- Add a "Select All" checkbox to user, role, and group list tables.
- Add bulk action buttons that appear when items are selected:
  - Users: Bulk drop, bulk add to group, bulk add to role.
  - Roles: Bulk drop, bulk grant to users.
  - Groups: Bulk drop.
- Implement HTMX-driven bulk operations that:
  - Collect selected item IDs via JavaScript (minimal JS allowed for checkbox state).
  - Send a single POST request with all selected items.
  - Show a progress indicator during execution.
  - Display a summary of results (succeeded/failed) when complete.

**Tests:**
- `tests/unit/test_bulk_ui_components.py`:
  - Test that list tables include select-all checkbox.
  - Test that bulk action buttons are rendered when expected.
  - Test that the bulk operation form includes the correct HTMX attributes.
- `tests/integration/test_bulk_operations.py`:
  - Test bulk drop of 3 users (against emulator).
  - Test bulk add of 5 users to a group.
  - Test that partial failures (e.g., 2 of 3 drops succeed) return correct summary.

---

## Phase Summary & Dependencies

```
Phase 1: Local Emulator & Test Foundation
   └── No dependencies (start here)

Phase 2: Security Hardening
   └── Depends on Phase 1 (needs test infrastructure)

Phase 3: Performance Optimization
   └── Depends on Phase 1 (needs emulator for perf tests)
   └── Partially depends on Phase 2 (sanitize.py used in new queries)

Phase 4: Modularization
   └── Depends on Phase 2 (security fixes should be in place before large refactor)
   └── Depends on Phase 3 (batch queries should be written before moving routes)

Phase 5: UI/UX Improvements
   └── Depends on Phase 4 (modular structure makes UI changes easier)
   └── Depends on Phase 3 (performance improvements affect UI loading patterns)
```

## Execution Order

1. **Phase 1** — Tasks 1.1, 1.2, 1.3 (sequential)
2. **Phase 2** — Tasks 2.1, 2.2 (parallel), then 2.3, then 2.4
3. **Phase 3** — Task 3.1 first, then 3.2 and 3.3 (parallel), then 3.4
4. **Phase 4** — Tasks 4.1, 4.2, 4.3, 4.4 (sequential — each builds on previous)
5. **Phase 5** — Tasks 5.1 and 5.2 (parallel), then 5.3, then 5.4 and 5.5 (parallel)

## Coverage Targets by Phase

| Phase | Cumulative Coverage Target |
|-------|---------------------------|
| Phase 1 | 40% (model layer) |
| Phase 2 | 55% (security + session) |
| Phase 3 | 65% (performance + cache) |
| Phase 4 | 75% (routes + services) |
| Phase 5 | 80% (UI components) |

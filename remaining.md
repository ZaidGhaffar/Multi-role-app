# Remaining Work

## Phase 1 – Frontend Upload Flow
- Frontend: Call `GET /generate_signed_url` to obtain signed URL.
- Frontend: Upload video directly to GCS using the signed URL (or use `/upload_direct`).
- Frontend: Notify backend with `POST /upload_complete` to store metadata.
- Employee UI: Show upload status/history using `GET /my/videos`.

## Phase 3 – HR Dashboard Frontend Integration
- Wire HR dashboard pages to new APIs:
  - `GET /hr/dashboard/summary`
  - `GET /hr/dashboard/emotion-distribution`
  - `GET /hr/dashboard/emotion-pie-distribution`
  - `GET /hr/dashboard/emotion-trend?days=<n>`
  - `GET /hr/dashboard/emotion-histogram-distribution?emotion=<e>&bins=<n>`
  - `GET /hr/employees?page=<p>&page_size=<n>`
  - `GET /hr/employees/{employee_id}`
- Build charts and cards on the frontend (summary KPIs, distribution, trend, histogram).
- Employee table (search/sort/pagination) and employee detail view.
- Frontend auth guard for HR role (redirect non-HR away from HR pages).

## Phase 5 – Connect HR Frontend + Backend
- Centralize API client in `neurofy-frontend/lib/api.ts` for new endpoints.
- Ensure company-based data filtering in the frontend views (backend already enforces it).
- Ensure protected routes for HR dashboard (JWT presence + role=hr in context).

## Demo/Seed & Processing Triggers
- Add a small seed script (optional) to create demo employees/videos.
- Provide a simple admin/HR action in UI to trigger AI on pending videos via:
  - `POST /ai/process-video/{video_id}`
  - `POST /ai/process-all-pending`

## Phase 6 – Testing & QA
- Backend unit tests for HR endpoints (FastAPI test client).
- Integration test: upload → store metadata → AI processing → HR queries.
- Frontend e2e smoke checks for HR dashboard pages.
- Performance tests for large uploads and concurrent queries.
- Security checks: signed URL expiry, JWT/role access control, multi-tenancy isolation.

## DevOps/Docs (Optional but Recommended)
- Postman collection or `README` section with example requests for all endpoints.
- Environment setup docs for frontend/backend (env vars, run scripts).
- CI workflow for lint/tests.

## Nice-to-Have Enhancements
- Department support in DB (currently `Employee-department` returns counts only).
- Caching of heavy analytics (e.g., per-company summaries) if needed.
- Better emotion label harmonization if the model changes labels.


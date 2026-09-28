# CropSense AI — Improvements

_Last updated: 2026-09-28 (branch `feat/livestock-assistant-services-i18n`)._

What to fix next, most urgent first. Each item links to where it was found. Fix everything **additively**: no deleted features or data; turn things off with a config toggle; schema changes go through model JSON → `setup.php` → migration (see [DATA_MODEL.md §5](DATA_MODEL.md#5-changing-the-schema)). Before fixing, confirm the cause from logs or the stored record, and leave logging behind that would show it next time.

| Priority | Meaning |
|---|---|
| **P0** | Security or privacy: one user can see or change another's data, or anyone can write without signing in |
| **P1** | A user-facing flow is broken |
| **P2** | Reliability, cost and operations |
| **P3** | Mismatches, dead code and clean-up |

---

## P0: security and privacy

| # | Problem | Where | Suggested fix |
|---|---|---|---|
| 1 | Any signed-in user can read another farmer's herd (or every herd, by leaving `farmer_id` out) and portfolio | `api/v1/livestock.py:140` (`GET /livestock/`), `/livestock/farmer/{id}/portfolio` | Ignore the `farmer_id` query for non-admins and always filter by the caller; allow other ids only for `CurrentAdmin` |
| 2 | Market reference data can be written with no sign-in | `api/v1/market_data.py`: `POST /crop-prices`, `/crop-prices/bulk`, `/historical-yields`, `/crop-profitability`, `/seasonal-trends/store`, `/opportunity-cost/save` | Add `dependencies=[Depends(get_current_admin)]` to those handlers (reads stay public) |
| 3 | `/admin/analytics` opens for any signed-in user | `solidjs/src/components/ProtectedRoute.tsx` | Add an optional `roles` prop to `ProtectedRoute`, and use `roles={['admin']}` on admin routes |
| 4 | The previous user's data stays on a shared phone after sign-out | apiClient memory cache, IndexedDB `rural_farming_db`, localStorage `assistant_chat` and `user_data`, SW cache `farming-platform-v1.1` (keyed by URL only) | On `signOut`: `apiClient.clearCache()`, clear IndexedDB stores, remove `assistant_chat`, and post a `CLEAR_API_CACHE` message to the service worker. Better still, stop caching authenticated `/api/*` GETs in the SW |
| 5 | Listing counters can be inflated anonymously | `POST /livestock-listings/{id}/interest`, `/inquiry` | Require sign-in, or rate-limit per IP |

## P1: broken flows

| # | Problem | Where | Suggested fix |
|---|---|---|---|
| 6 | Buyer dashboard can't reach the API: its requests go to the frontend host with no token, and `buyer_id` is hard-coded to `1` | `pages/marketplace/BuyerDashboard.tsx:56,90,119,151` | Use `apiClient.post('/supply-requests/…')`; take `buyer_id` from `user().id`, or let the backend set it (it is already in `OWNER_COLUMNS`) |
| 7 | Bookings created from matches can never be confirmed or quality-checked | `supply_request_matching_service.py:1225` creates `pending_farmer_confirmation`; `booking_workflow.py` `confirm` needs `pending` | Let `confirm` accept `pending_farmer_confirmation` too, and add farmer-side Confirm / Cancel buttons on `BookingDetails` |
| 8 | Payment, confirm, complete and cancel have no UI | `advance-booking.service.ts` methods exist but are uncalled | Add the buttons to `BookingDetails`, shown by role and status |
| 9 | `/strategy/results` gets a 500 once any strategy exists | `api/v1/annual_strategy.py:552` passes `total_annual_profit`; `schemas/crop.py:195` requires `total_expected_profit` | Pass `total_expected_profit=`; add `id` (or map `strategy_id`) and `created_at` to `StrategyListItem`; make `Results.tsx` use them |
| 10 | "Save" on a strategy saves nothing; POST `/annual-strategy` returns no id | `pages/strategy/Request.tsx`, `annual_strategy.py` | Return the draft's `id` from POST; have Save call `PUT /annual-strategy/{id}/status` (`active`) |
| 11 | `/soil/hub` loads no soil data | `shared/Service/Soil.ts` points at `/soil/health/`, `/soil/map/`, `/soil/fertilizer-recommendations/`; `SoilFertilizerHub.tsx` fetches plots only when `selectedFarmId()` is set, which is null at mount | Point the page at `/soil/health/plot/{id}`, `/soil-maps/*` and `/fertilizer-recommendations`; load plots after a farm is chosen |
| 12 | Pest "Identify" does not identify | `pages/pest-disease/PestDiseaseHub.tsx`; calls a non-existent `bulk_ai_import` | Call `POST /pest-disease/identify` with the description, then `GET /pest-disease/treatments` |
| 13 | Quota widget is hard-coded to user 1, so everyone else gets a 403 | `pages/farm/Register.tsx:29`, `pages/strategy/Request.tsx:145` | `userId={user()?.id}` |
| 14 | "Contact farmer" on the public listing page returns 401 for visitors | `/marketplace/:id` is public; `POST /marketplace/buyer-interest` needs sign-in | Show a "Sign in to contact" button that returns to the listing after sign-in |
| 15 | Links to routes that don't exist | `/crops/{id}` (`MyCrops.tsx:241`), `/livestock-marketplace/{id}`, `/transport/dashboard` | Add the detail routes (backend endpoints exist), or point the links at existing pages |
| 16 | Transport bookings can be invisible to the person who booked them | `core/ownership.py` `transport_bookings` rule omits `requester_id` | Add `OR t.requester_id = {uid}`, and add `requester_id` to `OWNER_COLUMNS` |
| 17 | Firebase token refresh fails when `username` is missing | `stores/auth.store.ts:102` falls back to `'firebase-user'` → `/auth/refresh` returns 404 | Store the Firebase uid or email, and have `/auth/refresh` look the user up by `firebase_id` |

## P2: reliability, cost and operations

| # | Problem | Where | Suggested fix |
|---|---|---|---|
| 18 | POST requests are retried on 5xx: a 503 from `/voice/assist` costs three Gemini calls, and a create that fails after writing can be duplicated | `lib/api-client.ts` `executeWithRetry` | Retry only GET / PUT / DELETE by default; POST retries must be opted in per call |
| 19 | Schedulers run in every Cloud Run instance (up to 10), so jobs can run up to 10 times | `main.py` `_start_background_jobs`, `jobs/*` | Move the jobs to Cloud Scheduler calling an admin endpoint, or take a Postgres advisory lock before running |
| 20 | Weekly yield update never runs | `jobs/weekly_yield_update.py` is not scheduled | Schedule it with the same mechanism as #19 |
| 21 | Cold start is longer than the sign-in timeout, so `min-instances=1` is always paid for | `deploy-gcp.sh` backend sizing | Profile imports at startup (lazy-load the AI, satellite and pandas modules); then try `min-instances=0` with CPU boost |
| 22 | A migration is not in the deploy list | `database/migrations/2026-09-26-cloudsql-additive.sql` | Confirm those 17 tables exist in production, then add the file to `MIGRATIONS` (it is safe to re-run) |
| 23 | Uploads fall back to `/tmp/uploads`, which is lost on restart | `services/file_storage.py` | Make `GCS_BUCKET` required in production, and fail loudly at startup if it is missing |
| 24 | `/islogin` lists have no pagination | `core/crud_service.py` `all()` | Add optional `?limit=&offset=` (default unlimited, so current callers keep working) |
| 25 | The offline queue is never used | `utils/offlineQueue.ts` `queueAction()` has no callers | Queue failed writes from the key forms (crop expense, health record) when offline |
| 26 | `/crop-recommendations/health` always returns 503 | `api/v1/crop_recommendations.py` | Report the real state of the RAG store, or say "fallback: Gemini" |
| 27 | Backend MFA is faked | `users.py` `/users/me/mfa/*`, `Security.tsx` | Use Firebase multi-factor (phone), or hide the toggle behind a Settings flag until it is real |

## P3: mismatches and clean-up

| # | Problem | Where | Suggested fix |
|---|---|---|---|
| 28 | Two farm shapes (`location_state` vs `state`, …) | `/farm` uses `/islogin/farm/`; the other pages use `/farms` | Make `/farm` use `FarmService.getFarms()` |
| 29 | Booking and milestone status names differ between frontend and backend | `Bookings.tsx` / `BookingDetails.tsx` vs `booking_workflow.py` | Use one list of status values in both; document them in the column `COMMENT` |
| 30 | Collected form fields are dropped | `plots/Create.tsx` (`sun_exposure`, `soil_ph`, `water_availability`, `notes`), `PlotManagement` (`current_crop`) | Send them if the columns exist, or stop asking |
| 31 | Mock or hard-coded UI data | "Upcoming Vax = 12" (`LivestockHub`), `/quota/history` usage table, `upcoming_tasks` always `[]` | Use `/vaccination-reminders`, `ai_usage_quota` history and `crop_milestones` |
| 32 | Generated services call controllers that don't exist | `shared/Service/Services.ts`: `/islogin/role`, `crop_market_data`, `push_subscription`, `slusi_ingestion_run`, `ndap_*` | Point them at `/isuper` or `/ipublic`, or leave them unused (don't delete) |
| 33 | Unused frontend code | Unrouted pages (`QuotaMonitoring`, `BrowseInfinite`, `GeolocationTest`), unrendered components (transport, `FarmList`, `NotificationSettings`, …), and services no page uses (`weather`, `soil` (broken registry keys), `pest-disease`) | Wire up the useful ones (`QuotaMonitoring` → `/admin/quota`, transport booking → `/transport/tracking`); fix the `soil.service.ts` keys |
| 34 | The language picker isn't saved to the account | `stores/i18n.store.ts` | Also `PUT /users/profile {language_preference}` when signed in |
| 35 | Legacy AWS code is still in the tree | `core/monitoring.py`, `core/alerting.py`, `services/bedrock_service.py`, `sagemaker_service.py`, `cognito_service.py`, `notification_service.py` (SNS), `/health/bedrock` | Keep it (additive rule), but label it legacy in the code and exclude it from the GCP health checks |
| 36 | Push uses a build-time VAPID key | `notification.service.ts` reads `VITE_VAPID_PUBLIC_KEY` | Fetch `GET /notifications/vapid-public-key`, so a key rotation needs no rebuild |

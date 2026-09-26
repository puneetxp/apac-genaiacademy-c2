# CropSense AI — Feature Inventory & Improvement Plan

_Last audited: 2026-09-26. Status reflects what the code does today, not what the UI promises._

**Status key:** ✅ Working · 🟡 Partial / mock data / placeholder · 🔴 Broken · ⚪ Built but not wired up (no route / not mounted)

**Stack:** FastAPI (`python/app`) + SolidJS (`solidjs/src`) + PostgreSQL, generated from `database/Model/*.json` by `php setup.php` (see `skills/SKILL.md`). Deployed on Cloud Run (`cropsense-backend`, `cropsense-frontend`), auth via Firebase.

---

## 1. Features by area

### Accounts & sign-in
| Feature | Backend | Frontend | Status | Notes |
|---|---|---|---|---|
| Email + password sign-up / sign-in | `/auth/signup`, `/auth/signin` | `/auth/signup`, `/auth/signin` | ✅ | Verified against Firebase 2026-09-26 |
| Email verification, forgot / reset password | `/auth/verify-email`, `/auth/forgot-password`, … | `EmailConfirmation`, `PasswordReset` | ✅ | |
| Google sign-in | `/auth/firebase` (`/auth/google`) | `QuickSignIn` | ✅ | Needed min-instances=1 (cold start > client timeout) |
| Phone OTP sign-in | `/auth/firebase` | `QuickSignIn` | 🔴 | Firebase **SMS region policy is empty** → `auth/internal-error`. Allow India in Firebase Console (or re-run `deploy-gcp.sh`, which now sets it) |
| SMS MFA | `/auth/verify-mfa`, `/users/me/mfa/*` | `MFAVerification`, `/users/security` | 🟡 | Frontend path fixed; backend MFA is faked (`cognito_service.py:237, 466-470`) |
| Profile view / edit, change password | `/users/profile`, `/users/change-password` | `/users/profile`, `/users/security` | ✅ | |

### Farms, plots & crops
| Feature | Backend | Frontend | Status | Notes |
|---|---|---|---|---|
| Farm registration with soil lookup | `/farms`, `/farms/soil-lookup/v2` | `/farm/register` | ✅ | `SHC_WMS_PATH` empty → SHC soil profile comes back empty |
| Farm list / dashboard / edit | `/farms/{id}`, `/islogin/farm` | `/farm`, `/farm/:id` | ✅ | Edit form crash and delete-plot bug fixed 2026-09-26 |
| Plot create | `/farms/{id}/plots` | `/plots/create` | ✅ | |
| Plot analyze / compare | `/plot-analysis/*` | `/plots/analyze`, `/plots/compare` | 🟡 | Frontend pages are stubs; backend uses SQLAlchemy calls on non-SQLAlchemy models |
| Quick-plant a crop, my crops | `/crops/quick-plant`, `/crops/my-crops` | `/crops/plant`, `/crops/my-crops` | ✅ | My-crops URL fixed 2026-09-26 |
| Crop expenses | `/crops/{id}/expenses` | Farm analytics | ✅ | URL fixed 2026-09-26 |
| Crop milestones / growth stages | `/crop-milestones/*` | — | ✅ | No auth on router |
| Yield prediction / harvest readiness | `/crops/yield-prediction…`, `/yield-predictions` | — | 🔴 | `db.query()` on lightweight ORM (`crops.py:525-676`, `yield_predictions.py:94`) |
| AI annual strategy (Gemini) | `/annual-strategy` | `/strategy/*`, `/crops/annual-strategy/:id` | 🟡 | Generate works; "Save" navigates to `/strategy/results`, which has no route |
| Crop recommendations (RAG) | `/crop-recommendations` | — | 🟡 | Stub ORMs → falls back to Gemini only; `/health` always 503 |

### Soil, weather & pests
| Feature | Backend | Frontend | Status | Notes |
|---|---|---|---|---|
| Weather current / forecast / alerts | `/weather/*`, `/severe-weather/*` | `/climate/hub` | 🟡 | Page fixed 2026-09-26: uses the farm's coordinates and real `/weather/forecast` + `/severe-weather/alerts/active`; forecast needs a working weather source (503 in sandbox) |
| Weather-based recommendations | `/weather-recommendations/*` | — | ✅ | Ported to raw SQL 2026-09-26 (sandbox-verified, owner-scoped) |
| Soil tests, health, fertilizer | `/soil`, `/soil-testing`, `/soil-health`, `/fertilizer-*` | `/soil/hub` | 🟡 | Backend ported 2026-09-26 (soil_testing, soil_health, fertilizer_*; owner-scoped). `/soil/hub` still calls `/soil/health`, `/soil/map`, which don't exist; `soil.py` is in 2b |
| SLUSI / SHC soil data ingestion | `/slusi/*` + weekly job | — | 🟡 | Weekly scrape works; `/farms/soil-lookup` (v1) now reachable and forwards to v2 when `state`+`district` are given (still 400 without them) |
| Pest & disease risk / alerts | `/pest-disease/*` | `/pest-disease/hub` | 🟡 | Backend ported 2026-09-26; ModelService fixed. `/pest-disease/alerts/farm/{id}` is shadowed by `/alerts/{crop_id}` (use `?farm_id=`) |
| Crop image diagnosis (Gemini Vision) | `/vision/*` | — | 🟡 | Mock fallback when Vertex unavailable |
| Voice Q&A | `/voice/query` | — | 🟡 | Mock fallback |

### Marketplace & supply chain
| Feature | Backend | Frontend | Status | Notes |
|---|---|---|---|---|
| Browse / search crop listings | `/marketplace/listings`, `/marketplace/search` | `/marketplace` | ✅ | Public |
| Listing detail + buyer interest | `/marketplace/listings/{id}`, `/marketplace/buyer-interest` | `/marketplace/:id` | 🟡 | URL fixed; backend detail uses `uuid.UUID(id)` on BIGINT ids and `db.query` |
| My listings | `/marketplace/my-listings` | `/marketplace/my-listings` | ✅ | Wrong path fixed 2026-09-26 |
| Advance bookings, quality verification | `/marketplace/advance-bookings/*` | `/bookings`, `/bookings/:id` | 🟡 | Dispute is a fake `alert()`; payments endpoint doesn't exist |
| Market intelligence, MSP, price trends | `/market-intelligence/*` | `/intelligence`, `/admin/analytics` | ✅ | Fixed 2026-09-26: frontend unwrapped `{success,data}` and mapped field names (pages crashed on `.toFixed`) |
| Price / demand prediction, supply planning | `/predictive-analytics/*` | `/supply-planning` | 🟡 | Service uses `select()` on lightweight ORM |
| Market data ingestion & analytics | `/market-data/*` | — | 🔴 | 15 `db.query` calls; tables not in `structure.sql`; no Agmarknet/NDAP client exists |
| Supply requests / matching (pgvector) | `/supply-requests` (not mounted) | `BuyerDashboard` (no route) | ⚪ | |
| Transport bookings & tracking | `/transport/*` | `/transport/tracking` | 🟡 | Backend fixed (sandbox-verified); `/transport/tracking` page still uses the ModelService layer (P1-7) |

### Livestock
| Feature | Backend | Frontend | Status | Notes |
|---|---|---|---|---|
| Livestock CRUD, portfolio, ROI | `/livestock/*` | `/livestock/hub` | 🟡 | Backend works; hub page broken (ModelService layer), "Upcoming Vax" hard-coded |
| Health records & vaccinations | `/livestock-health/*` | — | ✅ | Fixed 2026-09-26: shadowing, owner scoping, create 500 (sandbox-verified) |
| Nutrition / feed plans | `/livestock-nutrition/*` | — | 🟡 | Regional ingredients are placeholder data |
| Breeding records & offspring | `/livestock-breeding/*` + CRUD | — | ✅ | DB tables added 2026-09-26 |
| Buy / sell transactions | `/livestock-transactions/*` | — | 🟡 | `user_id` taken from query param (spoofable) |
| Vaccination reminders | `/vaccination-reminders/*` | — | 🟡 | Sends are log-only |
| Vet directory + AI symptom check | `/veterinary/*` | `/livestock/doctors` | ✅ | Appointments endpoint is a stub |
| Livestock marketplace | `/livestock-marketplace` (not mounted) | orphan page | ⚪ | |

### Platform
| Feature | Backend | Frontend | Status | Notes |
|---|---|---|---|---|
| Dashboard & analytics | `/analytics/*` | `/dashboard`, `/analytics/farm/:id` | ✅ | |
| Web push notifications | `/notifications/*` | service worker | ✅ | Push works; SMS/email placeholders |
| Notification inbox | `/notifications/inbox`, `/{id}/read`, `/read-all` | `/notifications` | 🟡 | Backend done (sandbox-verified); page not yet wired to it (P1-7) |
| AI usage quota | `/ai-quota/*` + midnight job | quota widgets | 🟡 | Quota history page is mock data and unrouted |
| AI agent chat (ADK) | `/agents/chat` | — | ✅ | |
| Community dashboard | `/community/dashboard` | — | 🟡 | Mock unless BigQuery configured |
| Image / document upload | `/upload/*` | used by bookings | 🟡 | Stored on ephemeral `/tmp` on Cloud Run (lost on restart) |
| PWA (offline, install) | — | `sw.js`, `manifest.json` | ✅ | Icons generated 2026-09-26 |
| SageMaker / model training / hybrid AI | `/sagemaker`, `/model-training`, `/hybrid-ai` | — | 🟡 | All mocks; sklearn/pandas not installed |
| Generated CRUD (43 isuper · 40 islogin · 9 ipublic tables) | `/api/v1/{isuper,islogin,ipublic}/<table>` | `shared/Service/*` | 🟡 | Auth added 2026-09-26 (see below); frontend layer calls wrong URLs |

---

## 2. Fixed on 2026-09-26

**Production (2026-09-26, MVP):** Cloud SQL migration applied (16 tables present); backend `cropsense-backend-00013` (image `mvp-20260926`, image-only, env unchanged); frontend `cropsense-frontend-00007` (image `mvp-20260926`). Smoke-tested: health 200, admin/owner routes 401 without login, new tables readable, CORS OK. Still unset in prod: `GCS_BUCKET` (uploads).

| Area | Fix | Live? |
|---|---|---|
| 🔒 Security | Generated `/isuper/*` routes now require admin, `/islogin/*` require sign-in (`main.py`, applied at mount so regeneration can't drop it). **Before: `/api/v1/isuper/user/` returned every user with no login.** | ✅ Deployed 2026-09-26 (backend revision `cropsense-backend-00012`; `/isuper/user/` now 401) |
| Auth | CSP allowed Google/reCAPTCHA/Firebase/backend (`index.html`) — fixed email + Google sign-in | ✅ |
| Auth | Sign-in requests wait 90 s (cold-start safe); backend min-instances=1 (also in `deploy-gcp.sh`) | ✅ |
| Auth | `deploy-gcp.sh` now sets the Firebase SMS region allow-list (`SMS_REGIONS`, default `IN`) | On next deploy |
| API | `api-client` no longer doubles `/api/v1` — fixes my-crops, expenses, buyer interest, MFA toggle | ✅ |
| API | Wrong paths: `my-listings`, `verify-mfa`; dead links `/farms/register`, `/marketplace/detail/:id` | ✅ |
| Farms | Edit form crash (`For` not imported); delete plot sent a malformed URL | ✅ |
| DB | `breeding_records` + `offspring` tables, CRUD, interfaces (via JSON → `setup.php`) | Local DB ✅ · Cloud SQL ⏳ |
| Types | 14 model JSONs used `"datatype": "text"` → invalid TS; now `string` (TS errors 79 → 15) | ✅ |
| PWA | Real app icons (were a text placeholder); SW no longer tries to cache `chrome-extension://` | ✅ |
| Build | Backend Dockerfile: non-interactive, no recommended packages (smaller, quieter) | Next backend build |
| Hygiene | `gcp-sa-key.json` (empty) added to `.gitignore` | ✅ |
| Transport | `services/transport_service.py` fully on `DB.raw`. Sandbox-verified: register/search providers, cost estimate, booking by a transaction party, status by the provider owner only (buyer 403, stranger 404), in_transit→delivered, one review per booking (updates provider rating), cancel. `components/transport/*` now use `apiClient` (they used relative `fetch('/transport/...')` with a wrong token key); client-sent `user_id`/`requester_id` removed. | ✅ Live 2026-09-26 |
| DB | 9 new models via JSON + `setup.php`: `historical_yields`, `crop_profitability`, `seasonal_trends`, `opportunity_costs`, `weather_forecasts` (public read, admin write), `soil_tests`, `soil_amendments`, `livestock_roi_predictions` (owner-scoped through plot/animal), `user_notifications` (inbox; users read/mark/delete their own, only admin/system creates). Columns taken from the old Alembic migration. Custom seasonal-trend logic moved to `services/seasonal_trend_analysis.py` so the generated `seasonal_trend_service.py` can't overwrite it. Idempotent `database/migrations/2026-09-26-cloudsql-additive.sql` (16 tables incl. breeding_records/offspring + FKs), tested on sandbox and a fresh DB. | ✅ Live 2026-09-26 (migration applied) |
| Notifications | Inbox API in `api/v1/notifications.py` + `services/notification_inbox.py`: GET `/notifications/inbox` (`unread_only`, paging, `unread_count`), POST `/{id}/read`, POST `/read-all`, all limited to the caller's own rows. Every `web_push_service.send_to_user` call also stores an inbox row, so alerts show up even without a push subscription. | ✅ Live 2026-09-26 |
| Routing | `{id:int}` path converters on `/livestock-health/{id}` and `/farms/{id}` (GET/PUT/DELETE), so `/livestock-health/vaccinations`, `/livestock-health/records` (also shadowed before) and `/farms/soil-lookup` reach their handlers. The vaccination/appointment aliases now pass real filter values (before, they passed `Query()` objects). | ✅ Live 2026-09-26 |
| 🔒 Security | `/livestock-health/*` had auth but **no ownership check: any signed-in user could read, edit or delete any farmer's animal health records**. A router dependency now checks livestock/record ids in the path, query and body against `ownership.py` (404 for other users, admins exempt), and lists are filtered to your own animals. Also fixed: creating a record returned 500 (`Model.create` without `get_inserted()`). | ✅ Live 2026-09-26 |
| Backend ORM (2a) | Ported to `DB.raw` with owner scoping via new `services/farm_access.py`: fertilizer_tracking, soil_testing, soil_health(_report), fertilizer_recommendations, pest_disease, plot_analysis, plot_publishing, weather_recommendations, severe_weather, slusi, nbss, yield_prediction_update, `GET /users/{id}` (others' contact fields hidden), agent_tools (farm tools use the signed-in user). `pest-disease/monitor-all` is now admin-only. | ✅ Live 2026-09-26 |
| Frontend data layer | `shared/Service/ModelService.ts` now goes through `apiClient` (Bearer token, `/api/v1`): `api/<table>` → `/islogin/<table>/`, real per-id PUT/DELETE, `where()` filters client-side (no more `WHERE` method). The generator template (`solidset.php`) emits `/islogin/<table>/` and no longer adds the non-existent `AccountService` to `run.ts` (a ReferenceError). IndexedDB skips stores that don't exist instead of throwing. | Sandbox ✅ |
| Pages | `/climate/hub` (farm location, real forecast/alerts), `/notifications` (inbox API, working "Mark all read"), `/marketplace/intelligence`, `/marketplace/supply-planning`, `/admin/analytics` (response adapters in `market-intelligence.service.ts`), `/strategy/select-farm` and `FarmService.getFarms()` (the API returns a list, not `{farms}`). Page sweep: 30/30, full suite 54/54. | ✅ Live 2026-09-26 |
| Routes & small fixes | New routes: `/strategy/results` (opens the farm's newest saved strategy, else offers to generate one; new `pages/strategy/Results.tsx`), `/quota/history`, `/marketplace/buyer-dashboard`, `/livestock-marketplace`. BookingDetails dispute now calls POST `/marketplace/advance-bookings/{id}/dispute` (was a TODO + fake alert). `uploadPhoto` no longer sets a manual multipart Content-Type (it broke the boundary). `rating.toFixed` guarded on doctors, transport, verifiers. | ✅ Live 2026-09-26 |
| TypeScript | 77 → 3 errors: added `node` + `@testing-library/jest-dom/vitest` types, fixed FarmDashboard/BookingDetails param types, FarmList `primary_soil_type`, plots/Create Farm type, GeolocationTest, initServiceWorker, useAsync, renderHook `cleanup`. The 3 left are in `pages/marketplace/BrowseInfinite.tsx`, which isn't routed and calls service methods that don't exist (left as-is, additive rule). | ✅ |
| DB layer | `core/db.py` `DB.exe()` now borrows from a shared SQLAlchemy connection pool (engine only: no SQLAlchemy models, no `create_all`, no Alembic) instead of opening a new psycopg connection per query. Default 2 + 2 overflow per worker (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`), sized for Cloud SQL `db-f1-micro` (~25 connections). The `create_all` spots and `python/alembic/` now say the schema comes from `setup.php`. | ✅ Live 2026-09-26 |

---

## 3. Improvement plan (prioritised)

### P0 — do now
1. **Deploy the backend** so the CRUD auth fix goes live (`deploy-gcp.sh`, or Cloud Build + `gcloud run deploy`). Until then admin/user data is publicly readable and writable.
2. **Allow India in Firebase SMS region policy** (phone OTP).
3. **Apply `breeding_records` / `offspring` to Cloud SQL** (`CREATE TABLE IF NOT EXISTS` from `database/structure.sql` + `relation.sql`).
4. **Add auth to ~30 custom v1 routers that have none** — worst first: `ai-quota` reset/limit, `upload` DELETE, `model-training/deploy-model`, `market-intelligence` collect, `livestock-transactions` (user id from query string), `transport`.
5. **Scope `/islogin/*` to the owner.** Signed-in users can currently read/edit *every* farm, crop, user row. Filter by `current_user.id` in the generated services (or add a generator template).

### P1 — make broken features work
6. **ORM mismatch** (biggest source of 🔴): ~20 services call SQLAlchemy `db.query()` / `select()` on the lightweight `app/core/model.py` classes. Port them to the `Model` API (`.where().get()`), starting with transport, predictive-analytics, soil/fertilizer, yield, marketplace detail.
7. **Frontend `ModelService` layer** (`shared/Service/*`) uses relative URLs without `/api/v1`, cookies instead of the Bearer token, and a non-standard `WHERE` method → Climate, Soil, Pest, Livestock hub, Transport, Notifications pages show nothing. Route it through `apiClient` + `/api/v1/islogin/<table>` (fix in the generator template so it survives regeneration).
8. ~~**Missing tables:**~~ (done 2026-09-26, see §2) `historical_yields`, `crop_profitability`, `seasonal_trends`, `opportunity_costs`, `soil_tests`, `soil_amendments`, `weather_forecasts`, `livestock_roi_predictions` exist only in an Alembic migration. Add JSON models (per skill) and replace the stub ORMs.
9. ~~**Route shadowing:**~~ (done 2026-09-26) `/livestock-health/{id}` before `/vaccinations`; `/farms/{id}` before `/farms/soil-lookup`.
10. **Wire up or remove orphans:** routes for `QuotaHistory`, `BuyerDashboard`, livestock marketplace; mount `supply_requests` / `livestock_marketplace` routers; add `/strategy/results`.

### P2 — reliability, cost, data
11. **Uploads to GCS** instead of `/tmp` (files vanish on every Cloud Run restart).
12. **Rate limiter:** set `request.state.user_id` so signed-in users get their 100/min, and stop trusting client-supplied `X-Forwarded-For`.
13. **Faster cold starts** so min-instances can go back to 0: lazy-load heavy AI clients, move SHC seeding off the startup path, trim image.
14. **Real integrations** for placeholders: IMD, ICAR, NBSS, SHC WMS (`SHC_WMS_PATH`), data.gov.in keys, Agmarknet/NDAP (claimed in explainability text but not implemented).
15. **Real MFA** (Firebase multi-factor) or remove the MFA UI.

### P3 — code health
16. **Tests:** 51 test files fail to collect with the default `.env`; add `ENVIRONMENT=test` config and fix import errors (botocore, pandas, `app.models.market_intelligence`, `Base`).
17. **Remove AWS/Cognito leftovers** (naming, `boto3` monitoring, SageMaker mocks, Cognito CSP hosts) once replacements exist.
18. **Generator hygiene:** `vendor/.../solidset.php` re-adds `AccountService` to `run.ts`; regenerating `isuper/push_subscription` drops its admin guard; hyphen-named duplicate controller folders (`islogin/weather-alert/…`) are invalid Python and unused.
19. ~~Remaining TS errors~~ (3 left, dead `BrowseInfinite.tsx`). **Unit tests (vitest): 26/49 fail for setup reasons:** Solid renders in SSR mode ("Client-only API called on the server"), `~` alias missing from the vitest config, and router tests that grep source text. Not app bugs.

---

## 4. How to keep this file current
- Add a model: create `database/Model/<name>.json` → run `php setup.php` in a scratch copy → bring back only new files and additive diffs (regeneration can drop hand-added auth, see P3-18).
- When a feature changes status, update its row and add a line to §2.

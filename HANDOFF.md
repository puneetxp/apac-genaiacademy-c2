# Handoff: CropSense "fix everything" work (2026-09-26)

Read this first, then FEATURES.md (the issue list). Nothing is committed to git.

## Rules (the user's)
- ORM: the user's own `Model`/`DB` (`app/core/model.py`, `app/core/db.py`). SQLAlchemy is ONLY the connection pool under `DB` (plus the legacy users model). Never add SQLAlchemy models, `create_all` or Alembic migrations.
- Additive only: never delete features, files or DB data without asking.
- All DB/schema changes: `database/Model/*.json` → run `php setup.php` in a SCRATCH COPY of the repo → copy back only the generated files that changed. Never hand-write CREATE TABLE.
- Role-based controllers: access comes from each model JSON's `crud` block (`isuper` = admin, `islogin` = signed-in owner, `ipublic` = public). Generated code lives in `python/app/api/{isuper,islogin,ipublic}/<table>/`.
- Never put business logic in `python/app/services/<table>_service.py`: the generator overwrites those files (the old milestone, transaction and booking logic was lost that way). Use other names, e.g. `booking_workflow.py`.
- Production deploys need the user's explicit OK. Don't read `.env` files.
- Keep token use low: work in small steps, avoid big file dumps, no more than 1 background agent.

## Test sandbox (done)
- Shell PATH lacks node/gcloud: prefix `PATH=$HOME/.nvm/versions/node/v24.20.0/bin:/opt/homebrew/bin:$PATH`.
- Separate DB `cropsense_e2e`, backend :8100 (test mode, mock auth), frontend :3100. See `e2e/sandbox/README.md`.
- Start: `cd e2e && (E2E_RELOAD=1 ./sandbox/start-backend.sh &) ; (./sandbox/start-frontend.sh &)`
- Run: `npm run sandbox` (headless), `npm run sandbox:headed`, `npm run sandbox:ui`. Set `E2E_SKIP_RESET=1` to keep the data between runs.
- Users (password `E2e-Test-Pass1!`): e2e_farmer (id 1, owns farm 1, crop 1, listing 1, livestock), e2e_buyer (2), e2e_admin (3).
- API calls with curl: `-H "Authorization: Bearer mock-token-e2e.farmer@example.com"`.
- Specs: 01 auth and 02 security (24/24 passing), 03 page-health sweep.

## Done this session
- Security: owner scoping for all `/islogin/*` (`app/core/ownership.py` + `app/core/crud_service.py`), admin guard on `/isuper/*`, auth on about 25 custom routers, spoofable user ids removed, rate limiter fixed, `system_settings` made admin-only.
- Generator (`vendor/puneetxp/compile-php/src/Class/pythonset.php`): services subclass CrudService, islogin routers pass the owner, isuper routers are admin-guarded, `<Model>Input` classes for create/update bodies, DECIMAL → float. `islogin` got `a` (list) in all model JSONs. Regenerated and copied back.
- Fixed: profile 500, uploads (GCS in prod plus `/upload/files/{name}`), marketplace detail/create/buyer interest, advance bookings (`services/booking_workflow.py`: confirm, cancel, payments, dispute), market intelligence, predictive analytics/supply planning, livestock transactions (`services/livestock_trade_workflow.py`), livestock listings (`services/livestock_listing_catalog.py`), livestock marketplace, crop milestones (`services/crop_growth_tracker.py`), nutrition, yield prediction/harvest readiness, vet directory (public again), and dev `VITE_API_URL`.
- Mounted in main.py: livestock_listings, livestock_marketplace, supply_requests.
- deploy-gcp.sh now creates the upload bucket and sets GCS_BUCKET.

## Still to do (in order)
1. ~~Transport~~ DONE 2026-09-26 (backend sandbox-verified, components use apiClient). Backend deployed to prod as image tag `sec-20260926` (revision 00012, image-only deploy, env/secrets unchanged, so GCS_BUCKET is still unset in prod).
2. (2b STOPPED by the user's choice 2026-09-26: MVP first; market_data/crop_recommendation/profit_margin are partly ported, soil.py untouched) (2a DONE 2026-09-26 by agent, helper `services/farm_access.py`; 2b = market_data/seasonal_trend_analysis/crop_recommendation/profit_margin/soil.py/crop_recommendations.py, now unblocked) **Still using SQLAlchemy on the lightweight ORM (broken):** market_data_service + seasonal_trend_service + api/v1/market_data, crop_recommendation_service, profit_margin_service, soil.py, soil_testing(+service), fertilizer_tracking_service, fertilizer_recommendations.py, soil_health_report_service, pest_disease(+service), plot_analysis_service, plot_publishing(+service), weather_recommendations_service, severe_weather(+service), slusi_service, nbss_service. Find them with `grep -rlE "db\.query\(|select\([A-Z]|self\.db\.(add|commit)" python/app`. Only `app/orm/user_sqlalchemy.py` is a real SQLAlchemy model.
3. ~~Missing tables~~ DONE 2026-09-26 (inbox table is `user_notifications`, model `user_notification`, to avoid clobbering the push `notification_service.py`). Was: historical_yields, crop_profitability, seasonal_trends, opportunity_costs, soil_tests, soil_amendments, weather_forecasts, livestock_roi_predictions, a notifications inbox table. Then write `database/migrations/2026-09-26-cloudsql-additive.sql` (include breeding_records and offspring).
4. ~~Notification inbox API~~ DONE 2026-09-26 (`services/notification_inbox.py`; pushes are also saved to the inbox). Was: GET `/notifications/inbox`, POST `/{id}/read`, `/read-all`.
5. ~~Route shadowing~~ DONE 2026-09-26 (plus livestock-health ownership hole fixed). Was: `/livestock-health/{id}` vs `/vaccinations`; `/farms/{id}` vs `/farms/soil-lookup`.
6. ~~Frontend~~ DONE 2026-09-26 except the soil hub's missing `/soil/health` + `/soil/map` endpoints (belongs to 2b). See FEATURES §2. Was:
   - Generated `shared/Service/*` layer: use apiClient + `/api/v1/islogin/<table>/`, and fix the generator template too. This is what breaks the climate, soil, pest, livestock hub and transport pages.
   - Climate hub: use the farm's coordinates, not Mumbai.
   - Doctors page: `Number(rating).toFixed`.
   - Notifications page: wire it to the inbox API.
   - Add a `/strategy/results` route.
   - Add routes for QuotaHistory, BuyerDashboard and the livestock-marketplace page.
   - BookingDetails dispute: call POST `/marketplace/advance-bookings/{id}/dispute`.
   - `advance-booking.service.ts` uploadPhoto: remove the manual multipart Content-Type header.
   - Fix the remaining TypeScript errors (`npx tsc --noEmit`).
7. Write feature specs 10–15 in `e2e/specs/`, run the whole suite, and update FEATURES.md.
8. DONE 2026-09-26 with the user's OK: Cloud SQL migration, backend (rev 00013) and frontend (rev 00007) deployed as image-only deploys. `deploy-gcp.sh` was NOT run. Still ask before any further deploy. Was: Ask the user before: deploying the backend (the security fix isn't live yet; production still leaks user data at `/api/v1/isuper/user/`), running `deploy-gcp.sh`, and applying the Cloud SQL migration.

# E2E sandbox

Runs the real app (FastAPI backend + SolidJS frontend) against a **throwaway database**, so
tests never touch production, Cloud SQL, or your local `cropsense_local` data.

| Piece | Sandbox | Normal dev |
|---|---|---|
| Database | `cropsense_e2e` (rebuilt every run) | `cropsense_local` |
| Backend | http://localhost:8100, `ENVIRONMENT=test`, `E2E_MODE=true` | :8000 |
| Frontend | http://localhost:3100 | :3000 |
| Sign-in | Mock auth, no Firebase calls | Firebase |
| Background jobs | Off (quota reset, SLUSI scrape, SHC seeding) | On |

## Run it

```bash
cd e2e
npm install                 # first time only
npx playwright install chromium

npm run sandbox             # headless, fast
npm run sandbox:headed      # watch the browser (300 ms between actions)
npm run sandbox:watch       # slow motion (800 ms) + video of every test
npm run sandbox:ui          # Playwright UI: pick tests, time-travel through each step
npm run sandbox:debug       # inspector: step through one action at a time
npm run sandbox:report      # open the HTML report from the last run
```

Playwright starts both servers itself (or reuses them if already running). Run one file or test:

```bash
npx playwright test -c sandbox.config.ts specs/03-page-health.spec.ts --headed
npx playwright test -c sandbox.config.ts -g "marketplace"
```

Keep the data from the previous run instead of reseeding: `E2E_SKIP_RESET=1 npm run sandbox`.

Run the servers yourself (e.g. to click around in a normal browser on http://localhost:3100):

```bash
E2E_RELOAD=1 ./sandbox/start-backend.sh     # auto-restarts on backend code changes
./sandbox/start-frontend.sh
npm run sandbox:reset                       # wipe + reseed cropsense_e2e
```

## Test users

All use the password `E2e-Test-Pass1!`.

| Role | Username | Email | Owns |
|---|---|---|---|
| Farmer | `e2e_farmer` | e2e.farmer@example.com | Farm "E2E Green Acres" (Pune), 2 plots, Soybean crop, marketplace listing, Gir cattle + goats |
| Buyer | `e2e_buyer` | e2e.buyer@example.com | nothing |
| Admin | `e2e_admin` | e2e.admin@example.com | admin pages (`user_type = 'admin'`) |

API calls in specs use `Authorization: Bearer mock-token-<email>` (see `specs/fixtures.ts`).

## Safety

`E2E_MODE` is ignored unless **all** of these hold, so it cannot switch on in production:
`ENVIRONMENT=test`, the database name ends in `_e2e`, and it is not running on Cloud Run.
`reset-db.sh` refuses to touch any database whose name doesn't end in `_e2e`.

AI calls (Gemini) still use whatever keys `python/.env` has; without Google credentials they fall back
to mock responses.

## Files

- `sandbox/reset-db.sh`: drop and recreate `cropsense_e2e` from `database/structure.sql` + `relation.sql`, then `seed.sql`
- `sandbox/seed.sql`: test users and starter data
- `sandbox/start-backend.sh`, `sandbox/start-frontend.sh`: servers in sandbox mode
- `sandbox.config.ts`: Playwright config
- `specs/`: the tests. `01` auth, `02` API security, `03` page health sweep (every page), `1x` feature flows

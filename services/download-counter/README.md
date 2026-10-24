# Anonymous download counter

Maintainer service for the website's optional download-session counts.
It is not shipped in the student ZIP or downloaded thesis files.

The browser sends only `{"asset":"starter"}` (or `overleaf`, `class`,
`cheatsheet`) on the first trusted download click in a tab session.
A tab-local yes/no flag suppresses repeats. Nothing identifying a visitor is
sent in the body. The Worker stores UTC day, asset type, and an atomic total.
IP addresses, referrers, request headers and raw events are not stored in D1.
Cloudflare necessarily receives network metadata as the hosting provider.

## Deploy

Use the existing Cloudflare account and keep the service on its current plan;
do not enable paid add-ons. In the Cloudflare dashboard:

1. Create a D1 database named `rpi-thesis-download-counts`. Run `schema.sql`
   in its console. The schema contains only daily aggregate counters.
2. Create a Worker named `rpi-thesis-download-counts` and replace its source
   with `worker.js`. Bind the D1 database as `COUNTS`.
3. In the Worker's observability settings, disable invocation/request logs
   and traces. The source has no console logging. Do not attach log drains.
4. Deploy. `/counts` returns the aggregate table; `/event` accepts only the
   live site's Origin and the fixed payload. CORS is not authentication and
   this public counter is not resistant to deliberate falsification.
5. Set `download_counter_url` in `site/site.json` to the Worker's HTTPS
   `/event` URL. Publish through the normal issue and PR workflow.
6. Open the live privacy notice with `?measurement=off#privacy` in each
   maintainer browser. Confirm that it says measurement is off. This cannot
   exclude other devices remotely and cannot remove past page views.

Cloudflare Web Analytics provides coarse geographic and traffic reports;
this counter deliberately stores no location. Treat both as estimates, not
verified users. The application and thesis files have no telemetry.

## Check and recover

The focused browser tests are `python3 scripts/tests/test_measurement.py`.
They use a local fixture, not the production endpoint. CI runs them in the
full test suite. Inspect `/counts` to check the deployed schema and service.
Do not send test events to the live counter; use D1 or local fixtures for
validation so tests do not inflate adoption totals.

If the service fails or reaches a platform limit, downloads still use their
original destinations. Remove `download_counter_url` to disable events.
Export D1's aggregate table before replacing or removing the database.
The public `/counts` response permits five minutes of caching and shows the
latest 1,464 day/category rows; D1 retains older totals for manual exports.

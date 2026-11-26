# BankRate Lab

<!-- coolcode:guide -->
Choose a date range and use the date inspector or data table to compare rates with matching units. Indexed FX starts each series at its first available observation, while CSV exports preserve original exchange rates and blank observations. Check the next scheduled policy decision and recent observed target changes, then follow the private payment-scenario link to Renewal Bench.
<!-- /coolcode:guide -->

[Open BankRate Lab](https://coolcode.ca/bankrates/) to compare Bank of Canada business-day observations. Explore the overnight policy target, Bank Rate, 2-, 5- and 10-year Government of Canada benchmark yields, and CAD exchange rates for USD, EUR, GBP and JPY. Each view has a date range, keyboard-accessible date inspector, tabular data, a shareable URL, and raw observation CSV export. The official policy calendar shows the next explicitly scheduled decision, and an observation-change table identifies movements in the target series.

All controls use a static same-origin JSON snapshot. The chart groups rates and exchange rates by units. Indexed FX rebases each series to its first available observation within the chosen date range. The CSV retains the original CAD exchange rates. Empty observations remain blank in exported data.

For the forecast behind a decision, [Policy Rate Scorecard](https://coolcode.ca/scorecard/) compares earlier public survey medians with the announced overnight target.

## Build

```sh
python3 scripts/build.py
python3 -m http.server 8080 --directory dist
```

The Python 3.11+ build uses only the standard library. It fetches [Valet](https://www.bankofcanada.ca/valet-api-how-to/) without a key, validates the expected series and units, and stages the deployment only after data is usable. Use `--input FILE` for a saved Valet JSON response obtained with the series and start date configured in `scripts/build.py`. All asset paths are relative for GitHub Pages. The site labels the snapshot build date and the date of each overview observation.

Data source: Bank of Canada. Original observations are reorganized and plotted in an independent browser tool. See the [Bank of Canada terms](https://www.bankofcanada.ca/terms/) and links to the respective series and methodology in the app.

## Regression checks

Pull requests that change code run logic tests and Chromium checks at this tool’s
Pages subpath, including a real control interaction and 320/390-pixel layouts.
Documentation-only pull requests skip this workflow. Publication waits for the
same checks. Test data stays in a separate job and is never packaged for Pages.

```sh
node --test tests/*.test.mjs
python3 tests/build_fixture.py
python3 -m pip install -r tests/browser-requirements.txt
python3 -m playwright install chromium
python3 tests/browser_smoke.py
```

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. The independent CoolCode watchdog supplements GitHub schedules and exposes collector failures separately from watchdog-service health. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->

## Policy calendar and payment scenarios

The online build reads the explicitly dated schedule tables on the Bank of Canada policy-rate page. `snapshot.json.calendar.checked_at` records the successful calendar retrieval separately. If no future date remains, the app says so rather than projecting an eight-meeting pattern. Dates may change. An offline `--input` build contains no captured calendar and links to the publisher.

The target-change table lists the first daily observation at a different rate, preserving its date rather than treating it as the press-release date. Unchanged meetings are not included. Follow Renewal Bench for monthly payment scenarios using **your own contractual rates**; no one-for-one relationship between policy changes and lender pricing is assumed.

## Expand or customize

`SERIES` and `START` in `scripts/build.py` control accepted Valet series and coverage. Add a labelled rates/FX series and validate its official units; the selectors derive options dynamically. The calendar parser is in `scripts/calendars.py`. Refresh with the existing weekday workflow or manual Run workflow. The schedule, watchdog target and metrics identity remain unchanged.

## Ready-to-use examples

- [Bank of Canada Policy Rate History](https://coolcode.ca/bankrates/policy-rate-history.html). See the target overnight rate and the dates it changed. The chart opens to twelve months of policy rates. Change the time range to see earlier decisions or export the daily observations.
- [Canadian 2-Year and 10-Year Government Bond Yields](https://coolcode.ca/bankrates/canada-bond-yields.html). Compare the two-year and ten-year benchmark yields on the same dates. The chart shows annual percentage yields. Use the table for individual observations and the export for longer comparisons.

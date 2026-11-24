# BankRate Lab

<!-- coolcode:guide -->
Choose a date range and use the date inspector or data table to compare rates with matching units. Indexed FX starts each series at its first available observation, while CSV exports preserve original exchange rates and blank observations.
<!-- /coolcode:guide -->

[Open BankRate Lab](https://coolcode.ca/bankrates/) to compare Bank of Canada business-day observations. Explore the overnight policy target, Bank Rate, 2-, 5- and 10-year Government of Canada benchmark yields, and CAD exchange rates for USD, EUR, GBP and JPY. Each view has a date range, keyboard-accessible date inspector, tabular data, a shareable URL, and raw observation CSV export.

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

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->

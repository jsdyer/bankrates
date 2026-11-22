# BankRate Lab

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

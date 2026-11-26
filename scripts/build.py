"""Build the browser data snapshot from public Bank of Canada Valet observations."""
import argparse
from datetime import date, datetime, timezone
import json
import math
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from calendars import boc_events

CALENDAR_SOURCE = "https://www.bankofcanada.ca/core-functions/monetary-policy/key-interest-rate/"

from public_pages import publish_pages

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.bankofcanada.ca/valet/observations/"
START = "2017-01-01"
SERIES = {
    "V39079": ["Policy rate", "rates"],
    "V39078": ["Bank Rate", "rates"],
    "BD.CDN.2YR.DQ.YLD": ["Canada 2-year yield", "rates"],
    "BD.CDN.5YR.DQ.YLD": ["Canada 5-year yield", "rates"],
    "BD.CDN.10YR.DQ.YLD": ["Canada 10-year yield", "rates"],
    "FXUSDCAD": ["USD/CAD", "fx"],
    "FXEURCAD": ["EUR/CAD", "fx"],
    "FXGBPCAD": ["GBP/CAD", "fx"],
    "FXJPYCAD": ["JPY/CAD", "fx"],
}
SOURCE = BASE + ",".join(SERIES) + "/json?start_date=" + START
LIMIT = 5 * 1024 * 1024


def fetch():
    request = Request(SOURCE, headers={"Accept": "application/json", "User-Agent": "CoolCode BankRate Lab build (https://coolcode.ca/bankrates/)"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as response:
                payload = response.read(LIMIT + 1)
            if len(payload) > LIMIT:
                raise ValueError("Valet response exceeded the size limit.")
            return json.loads(payload)
        except (URLError, TimeoutError, OSError) as error:
            if attempt == 2:
                raise RuntimeError(f"Could not fetch Valet: {error}") from error
            time.sleep(2 ** attempt)


def normalize(raw):
    details = raw["seriesDetail"]
    tracks = {}
    for key, (label, group) in SERIES.items():
        item = details[key]
        unit = item["metadata"]["unit"]
        if group == "rates" and unit != "Percent":
            raise ValueError(f"Unexpected unit for {key}: {unit}")
        if group == "fx" and not unit.startswith("Canadian dollars per "):
            raise ValueError(f"Unexpected unit for {key}: {unit}")
        tracks[key] = {"label": label, "group": group, "unit": unit, "description": item["description"], "data": []}
    dates = []
    for item in raw["observations"]:
        when = item["d"]
        parsed = date.fromisoformat(when)
        if parsed.isoformat() != when or (dates and when <= dates[-1]):
            raise ValueError(f"Unordered or invalid observation date {when}.")
        if parsed > datetime.now(timezone.utc).date() or when < START:
            raise ValueError(f"Out-of-range observation date {when}.")
        dates.append(when)
        for key, track in tracks.items():
            observation = item.get(key, {}).get("v")
            value = None if observation in (None, "") else float(observation)
            if value is not None and (not math.isfinite(value) or (track["group"] == "fx" and value <= 0)):
                raise ValueError(f"Invalid observation for {key} on {when}.")
            track["data"].append(value)
    if len(dates) < 500 or any(sum(value is not None for value in track["data"]) < 500 for track in tracks.values()):
        raise ValueError("Valet returned too few observations.")
    return {
        "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": SOURCE,
        "dates": dates,
        "tracks": tracks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Use previously downloaded Valet JSON for the configured range and series.")
    args = parser.parse_args()
    raw = json.loads(args.input.read_bytes()) if args.input else fetch()
    snapshot = normalize(raw)
    if args.input:
        snapshot['calendar'] = {'checked_at': None, 'source': CALENDAR_SOURCE, 'events': [], 'note': 'Offline input build: calendar not collected'}
    else:
        request = Request(CALENDAR_SOURCE, headers={'User-Agent': 'CoolCode BankRate Lab (+https://coolcode.ca/bankrates/)', 'Accept':'text/html'})
        with urlopen(request, timeout=45) as response:
            page = response.read(3_000_001)
        if len(page)>3_000_000: raise ValueError('Calendar response too large')
        snapshot['calendar'] = {'checked_at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'source': CALENDAR_SOURCE, 'events': boc_events(page.decode('utf-8'), CALENDAR_SOURCE)}
    with TemporaryDirectory(dir=ROOT) as temporary:
        stage = Path(temporary) / "dist"
        shutil.copytree(ROOT / "web", stage)
        (stage / "snapshot.json").write_text(json.dumps(snapshot, separators=(",", ":")), encoding="utf-8")
        publish_pages(stage, (stage / "index.html").read_text(encoding="utf-8"), json.loads((ROOT / "tool.json").read_text()), snapshot)
        output = ROOT / "dist"
        if output.exists():
            shutil.rmtree(output)
        stage.replace(output)
    print(f"Prepared {len(snapshot['dates']):,} dates for {len(SERIES)} Valet series.")


if __name__ == "__main__":
    main()

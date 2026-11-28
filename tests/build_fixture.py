from datetime import date, timedelta
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build import SERIES, normalize
from public_pages import publish_pages

prime = "V80691311"
details = {
    key: {"description": label, "metadata": {"unit": "Percent" if group == "rates" else "Canadian dollars per test currency"}}
    for key, (label, group) in SERIES.items()
}
details[prime]["metadata"]["frequency"] = "Weekly"
observations = []
for i in range(750):
    when = date(2020, 1, 1) + timedelta(days=i)
    if when.weekday() > 4:
        continue
    row = {"d": when.isoformat()}
    for key in SERIES:
        if key != prime or when.weekday() == 2:
            row[key] = {"v": str(1 + i / 1000)}
    observations.append(row)

snapshot = normalize({"observations": observations, "seriesDetail": details})
stage = ROOT / "dist"
shutil.copytree(ROOT / "web", stage, dirs_exist_ok=True)
(stage / "snapshot.json").write_text(json.dumps(snapshot))
publish_pages(stage, (stage / "index.html").read_text(), json.loads((ROOT / "tool.json").read_text()), snapshot)

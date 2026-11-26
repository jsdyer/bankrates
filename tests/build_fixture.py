import datetime,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import normalize,SERIES
from public_pages import publish_pages
raw={'seriesDetail':{key:{'description':label,'metadata':{'unit':'Percent' if group=='rates' else 'Canadian dollars per test currency'}} for key,(label,group) in SERIES.items()},'observations':[]}
for i in range(600):
 row={'d':(datetime.date(2020,1,1)+datetime.timedelta(days=i)).isoformat()}
 row.update({key:{'v':str(1+i/1000)} for key in SERIES});raw['observations'].append(row)
shutil.copytree(ROOT/'web',ROOT/'dist',dirs_exist_ok=True)
(ROOT/'dist/snapshot.json').write_text(json.dumps(normalize(raw)))

snapshot = normalize(raw)
publish_pages(ROOT / "dist", (ROOT / "web/index.html").read_text(), json.loads((ROOT / "tool.json").read_text()), snapshot)

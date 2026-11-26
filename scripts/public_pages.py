"""Build working, directly linkable views of the tool from its page template."""
from html import escape
import json
import re

from urllib.parse import parse_qs

from search_metadata import add_search_metadata


def public_records(data, case):
    params = parse_qs(case["value"])
    keys = params["series"] + params.get("compare", [])
    rows = []
    for key in keys:
        series = data["tracks"][key]
        index = next((i for i in range(len(series["data"]) - 1, -1, -1)
                      if series["data"][i] is not None), None)
        if index is None:
            continue
        rows.append(f'<li>{escape(series["label"])} · {series["data"][index]:.2f}% on {escape(data["dates"][index])}</li>')
    return '<ul aria-label="Latest observations">' + "".join(rows) + '</ul>'


def publish_pages(stage, page, tool, data):
    cases = json.loads((stage / "use-cases.json").read_text(encoding="utf-8"))
    for case in cases:
        filename = case["slug"] + ".html"
        preset = {**tool, "title": case["title"], "url": tool["url"] + filename,
                  "description": case["description"]}
        title = escape(case["title"])
        summary = escape(case["description"])
        result = re.sub(r"<title>.*?</title>", lambda _: "<title>" + title + " · CoolCode</title>", page, count=1)
        result = re.sub(r"(<h1\b[^>]*>).*?</h1>", lambda m: m[1] + title + "</h1>", result, count=1, flags=re.S)
        result = re.sub(r'<meta name="description" content="[^"]*">', lambda _: '<meta name="description" content="' + summary + '">', result, count=1)
        result = re.sub(r"<body(?=[ >])", lambda _: '<body data-' + case["setting"] + '="' + escape(case["value"]) + '"', result, count=1)
        result = result.replace("<!-- case-context -->", '<p class="case-context">' + summary + ' <a href="./">Open the full tool</a></p>' + public_records(data, case))
        (stage / filename).write_text(add_search_metadata(result, preset), encoding="utf-8")
    (stage / "index.html").write_text(add_search_metadata(page, tool), encoding="utf-8")

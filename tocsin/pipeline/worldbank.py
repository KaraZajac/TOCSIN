"""World Bank Open Data (WDI) — structural covariates, CC BY 4.0.

Pulls a fixed set of development indicators through the public API (paginated
JSON, no key) into sources/worldbank/. These are the covariates the conflict
literature leans on — income, inflation, age structure, urbanization, infant
mortality — and the inputs for testing whether "inflation + a young
population" carries forecasting signal.

Provenance note: most WDI series are World-Bank/UN-compiled (clean CC BY);
inflation (FP.CPI.TOTL.ZG) is IMF-sourced and redistributed by the Bank under
its open terms — flagged in DATA-RIGHTS.md so the release attribution is
honest.
"""

import json

from tocsin.paths import ROOT, SOURCES
from tocsin.pipeline.download import _get as fetch

API = "https://api.worldbank.org/v2"
DEST = SOURCES / "worldbank"

# logical name -> (indicator code, source label for attribution)
INDICATORS = {
    "gdp_pc": ("NY.GDP.PCAP.KD", "World Bank national accounts"),
    "inflation": ("FP.CPI.TOTL.ZG", "IMF IFS via World Bank"),
    "pop_0014": ("SP.POP.0014.TO.ZS", "UN Population Division via World Bank"),
    "pop_1564": ("SP.POP.1564.TO.ZS", "UN Population Division via World Bank"),
    "urban_pct": ("SP.URB.TOTL.IN.ZS", "UN via World Bank"),
    "infant_mort": ("SP.DYN.IMRT.IN", "UN IGME via World Bank"),
    "pop_growth": ("SP.POP.GROW", "UN Population Division via World Bank"),
}


def _get(url: str):
    """One API page as (meta, rows), through download's retrying fetcher.
    Uncached all-country requests can take minutes before the first byte
    (118s, then over 120s, then 298s on 2026-11-13; cached ones about 1s),
    and the old 120s timeout is what failed the 2026-10 refresh. The API's
    Cloudflare front gives up at 300s with an HTTP 524, which the fetcher
    retries; 600s just keeps our own timeout out of its way.
    A 200 that is not a data page (the API's error message for a bad or
    retired indicator, an HTML error page) stops the pull, showing what came
    back."""
    body = fetch(url, timeout=600)
    try:
        meta, rows = json.loads(body)
    except (ValueError, TypeError):  # not JSON, or the one-element error message
        meta = rows = None
    if not isinstance(meta, dict) or "pages" not in meta:
        raise SystemExit(f"World Bank API returned no data page for {url}: {body[:300].decode(errors='replace')}")
    return meta, rows


def fetch_indicator(code: str) -> list[dict]:
    """All country-year observations for one indicator (follows pagination)."""
    out, page = [], 1
    while True:
        url = f"{API}/country/all/indicator/{code}?format=json&per_page=20000&page={page}&date=1960:2025"
        meta, rows = _get(url)
        for r in rows or []:
            if r["value"] is not None and r["countryiso3code"]:
                out.append({"iso3": r["countryiso3code"], "year": int(r["date"]), "value": r["value"]})
        if page >= meta["pages"]:
            break
        page += 1
    return out


def pull(force: bool = False) -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for logical, (code, _src) in INDICATORS.items():
        dest = DEST / f"{logical}.json"
        if dest.exists() and not force:
            print(f"  cached {dest.relative_to(ROOT)}")
            continue
        rows = fetch_indicator(code)
        dest.write_text(json.dumps(rows, separators=(",", ":")))
        print(f"  -> {dest.relative_to(ROOT)} ({len(rows):,} obs)")


def main() -> None:
    import sys

    pull(force="--force" in sys.argv)


if __name__ == "__main__":
    main()

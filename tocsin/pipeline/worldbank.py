"""World Bank Open Data (WDI) — structural covariates, CC BY 4.0.

Pulls a fixed set of development indicators from the public API (no key) into
sources/worldbank/: each from its bulk-download zip (one wide CSV, served from
the API's CDN cache), else from the paginated JSON API, with identical
results either way. These are the covariates the conflict literature leans
on — income, inflation, age structure, urbanization, infant mortality — and
the inputs for testing whether "inflation + a young population" carries
forecasting signal.

Provenance note: most WDI series are World-Bank/UN-compiled (clean CC BY);
inflation (FP.CPI.TOTL.ZG) is IMF-sourced and redistributed by the Bank under
its open terms — flagged in DATA-RIGHTS.md so the release attribution is
honest.
"""

import csv
import io
import json
import zipfile

from tocsin.paths import ROOT, SOURCES
from tocsin.pipeline.download import _get as fetch

API = "https://api.worldbank.org/v2"
DEST = SOURCES / "worldbank"
YEARS = (1960, 2025)  # the window both paths keep

# The JSON API returns these aggregates (the four income groups and "Not
# classified") with an empty countryiso3code, so the JSON path never kept
# them; the bulk CSV gives them codes, so it drops them to keep the same rows.
NO_ISO3_IN_API = {"HIC", "LIC", "LMC", "UMC", "INX"}

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
        url = f"{API}/country/all/indicator/{code}?format=json&per_page=20000&page={page}&date={YEARS[0]}:{YEARS[1]}"
        meta, rows = _get(url)
        for r in rows or []:
            if r["value"] is not None and r["countryiso3code"]:
                out.append({"iso3": r["countryiso3code"], "year": int(r["date"]), "value": r["value"]})
        if page >= meta["pages"]:
            break
        page += 1
    return out


def bulk_rows(payload: bytes, code: str) -> list[dict]:
    """fetch_indicator's observations from a bulk-download zip, whose
    API_<code>_*.csv is a wide table (one column per year) after a few
    metadata lines. Same rows, shape and newest-first years per country;
    cells parse as JSON numbers, so integral values stay ints as in the API's
    JSON. Anything unexpected raises ValueError."""
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        names = [n for n in zf.namelist() if n.startswith(f"API_{code}_") and n.endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"expected one API_{code}_*.csv in the zip, found {zf.namelist()}")
        lines = csv.reader(io.StringIO(zf.read(names[0]).decode("utf-8-sig")))
    for header in lines:
        if header[:4] == ["Country Name", "Country Code", "Indicator Name", "Indicator Code"]:
            break
    else:
        raise ValueError("no Country Name/Country Code header row")
    cols = sorted(((int(h), i) for i, h in enumerate(header) if h.isdigit() and YEARS[0] <= int(h) <= YEARS[1]), reverse=True)
    out = []
    for r in lines:
        if len(r) < 4 or not r[1] or r[1] in NO_ISO3_IN_API:
            continue
        if r[3] != code:
            raise ValueError(f"a {r[3]!r} row in the {code} file")
        out += [{"iso3": r[1], "year": y, "value": json.loads(r[i])} for y, i in cols if i < len(r) and r[i]]
    return out


def fetch_indicator_bulk(code: str) -> list[dict]:
    """fetch_indicator's observations from the bulk download, which the API's
    CDN serves from cache (0.2s on 2026-11-13, while the JSON endpoint took up
    to 298s on an uncached all-country request)."""
    return bulk_rows(fetch(f"{API}/en/indicator/{code}?downloadformat=csv"), code)


def pull(force: bool = False) -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for logical, (code, _src) in INDICATORS.items():
        dest = DEST / f"{logical}.json"
        if dest.exists() and not force:
            print(f"  cached {dest.relative_to(ROOT)}")
            continue
        try:
            rows, via = fetch_indicator_bulk(code), "bulk CSV"
            problem = "" if rows else "no observations"
        except (SystemExit, ValueError, zipfile.BadZipFile, csv.Error) as e:
            rows, problem = [], str(e)
        if problem:
            print(f"  ! bulk CSV for {code} unusable ({problem}) — falling back to the JSON API", flush=True)
            rows, via = fetch_indicator(code), "JSON API"
        dest.write_text(json.dumps(rows, separators=(",", ":")))
        print(f"  -> {dest.relative_to(ROOT)} ({len(rows):,} obs, {via})")


def main() -> None:
    import sys

    pull(force="--force" in sys.argv)


if __name__ == "__main__":
    main()

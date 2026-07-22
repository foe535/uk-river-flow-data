"""
eFLaG Hydrology Bulk Download and Clean (simobs) — Freshwater Digital Twin project

Works for any of the four eFLaG models (G2G, GR4J, GR6J, PDM). Downloads
the "simobs" river flow file for every catchment eFLaG covers (200
catchments), then combines them into one clean CSV per model, with a
station-number column so you can tell them apart.

simobs is driven by real historical weather, one flow estimate per day,
against which the model's accuracy can be checked using the real gauge
record (Qobs). For the separate, differently-structured simrcm product
(future-climate projections), see hydrology_simrcm_download_clean.py.

Station numbers came directly from eFLaG_Station_Metadata.xlsx (the
River Flow sheet), not scraped from the website's folder listing, which
needs a login session and fails when a script tries to read it directly.

SETUP (once):
    pip install pandas requests

USAGE:
    python3 hydrology_download_clean.py GR6J test        # try 3 stations, check access works
    python3 hydrology_download_clean.py GR6J download     # download all 200
    python3 hydrology_download_clean.py GR6J clean        # combine into one CSV

    python3 hydrology_download_clean.py G2G test
    python3 hydrology_download_clean.py G2G download
    python3 hydrology_download_clean.py G2G clean

Each model gets its own folder and output file (e.g. gr6j_raw/ and
gr6j_all_catchments_clean.csv, or g2g_raw/ and g2g_all_catchments_clean.csv),
so running this for G2G will never overwrite or interfere with GR6J's
files, or vice versa.
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

VALID_MODELS = ("G2G", "GR4J", "GR6J", "PDM")

STATIONS = [
    2001, 3003, 6007, 7001, 7003, 8004, 8006, 9002, 11001, 12001, 12005, 13007,
    14001, 15006, 16001, 16003, 17005, 18001, 18005, 19006, 20001, 21009, 21022,
    21023, 21024, 22001, 22009, 23004, 24004, 24005, 25001, 25006, 25020, 27002,
    27007, 27009, 27021, 27034, 27035, 27041, 27042, 27051, 27089, 28009, 28022,
    28043, 28046, 28082, 29003, 30001, 31010, 32003, 33018, 33026, 33029, 33034,
    33039, 34002, 34004, 34006, 34011, 35008, 36007, 36010, 37001, 37005, 37011,
    37019, 38001, 38003, 38014, 38017, 39001, 39006, 39007, 39010, 39014, 39019,
    39020, 39025, 39027, 39028, 39034, 39049, 39057, 39072, 39081, 39088, 39089,
    39090, 39127, 39130, 39141, 40003, 40009, 40011, 41004, 41011, 41022, 41029,
    42004, 42008, 43005, 43007, 44002, 45001, 45005, 46005, 47001, 47009, 48003,
    48004, 48005, 49001, 49004, 50001, 50002, 52004, 52005, 52010, 53006, 53009,
    53017, 54001, 54002, 54008, 54018, 54029, 54032, 54057, 55002, 55007, 55016,
    55023, 55029, 56001, 56007, 56013, 57004, 58005, 58007, 58008, 58012, 59001,
    60002, 60006, 60009, 60010, 61002, 62001, 63001, 64001, 65001, 65005, 65007,
    66011, 67015, 67018, 68003, 68005, 69007, 71006, 72005, 72014, 73005, 73010,
    73011, 75003, 76007, 77002, 79002, 79004, 81002, 81004, 82001, 83006, 83010,
    84013, 84016, 84022, 84026, 85001, 85003, 89003, 90003, 91002, 93001, 94001,
    96002, 97002, 102001, 201006, 202002, 203020, 203028, 204001, 205004, 205008,
    206001, 236007,
]


def base_url(model: str) -> str:
    return f"https://catalogue.ceh.ac.uk/datastore/eidchub/1bb90673-ad37-4679-90b9-0126109639a9/River_Flow/{model}/simobs"


def raw_dir(model: str) -> Path:
    d = Path(os.environ.get(f"{model}_RAW_DIR", Path(__file__).parent / f"{model.lower()}_raw"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def output_file(model: str) -> Path:
    return Path(
        os.environ.get(
            f"{model}_OUTPUT_FILE", Path(__file__).parent / f"{model.lower()}_all_catchments_clean.csv"
        )
    )


def download_one(model: str, station: int) -> str:
    url = f"{base_url(model)}/{model}_simobs_{station}.csv"
    dest = raw_dir(model) / f"{model}_simobs_{station}.csv"

    if dest.exists():
        return "skipped (already have it)"

    try:
        response = requests.get(url, timeout=30)
    except Exception as exc:
        return f"failed (connection error: {exc})"

    if response.status_code == 200:
        dest.write_bytes(response.content)
        return "ok"
    elif response.status_code in (401, 403):
        return f"failed (status {response.status_code} — likely needs an EIDC login)"
    else:
        return f"failed (status {response.status_code})"


def download_batch(model: str, stations: list[int]):
    results = {}
    for i, station in enumerate(stations, 1):
        result = download_one(model, station)
        results[station] = result
        print(f"[{i}/{len(stations)}] {model} station {station}: {result}")
        time.sleep(0.5)  # small pause between requests, don't hammer their server

    ok_count = sum(1 for v in results.values() if v == "ok" or v.startswith("skipped"))
    print(f"\n{ok_count}/{len(stations)} {model} files available in {raw_dir(model)}")

    failed = {k: v for k, v in results.items() if not (v == "ok" or v.startswith("skipped"))}
    if failed:
        print(f"{len(failed)} failed, first few: {dict(list(failed.items())[:5])}")


def clean_and_combine(model: str):
    frames = []
    missing = []

    for station in STATIONS:
        f = raw_dir(model) / f"{model}_simobs_{station}.csv"
        if not f.exists():
            missing.append(station)
            continue
        df = pd.read_csv(f)
        df["station"] = station
        frames.append(df)

    if not frames:
        sys.exit(f"No downloaded {model} files found. Run 'download' first.")

    combined = pd.concat(frames, ignore_index=True)
    out = output_file(model)
    combined.to_csv(out, index=False)

    print(f"Combined {len(frames)} {model} stations, {len(combined)} total rows.")
    print(f"Saved to: {out}")
    if missing:
        preview = missing[:10]
        more = "..." if len(missing) > 10 else ""
        print(f"{len(missing)} stations had no downloaded file and were skipped: {preview}{more}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in VALID_MODELS or sys.argv[2] not in ("test", "download", "clean"):
        sys.exit(f"Usage: python3 {sys.argv[0]} [{'|'.join(VALID_MODELS)}] [test|download|clean]")

    model_arg, action = sys.argv[1], sys.argv[2]
    if action == "test":
        download_batch(model_arg, STATIONS[:3])
    elif action == "download":
        download_batch(model_arg, STATIONS)
    else:
        clean_and_combine(model_arg)

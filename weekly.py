#!/usr/bin/env python3
"""The weekly run: fetch the newest TLE, make a set, check it, publish it.

GitHub Actions runs this every Monday (.github/workflows/weekly.yml):

  1. Fetch KNACKSAT-2's TLE from CelesTrak, three tries. If CelesTrak has no
     elements at all, KNACKSAT-2 has most likely re-entered: stop with an error.
  2. Make the set for the 7 days from 00:00 UTC today with make_ephemeris.py.
  3. Check it, and publish nothing if a check fails:
     - every pass against PyEphem, a separate SGP4 code: the same passes, rise
       and set within 2 s (the CSV rounds to the second), the peak and the
       rise and set azimuths within 0.2 deg;
     - the OEM against geocentric.csv: the same instants and, once the frame
       bias is applied, the same states; OEM version 1.0, which GMAT reads.
  4. Measure how late the previous set's TLE runs at this TLE's epoch.
  5. Write the set's CHECKS.md, copy the set to latest/, list it in README.md.

    python weekly.py                    # what the job runs
    python weekly.py --tle saved.tle    # from a saved TLE instead of CelesTrak
    python weekly.py --dry-run          # into _dry-run/, publishing nothing
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

import ephem
import numpy as np
from skyfield.api import EarthSatellite, load
from skyfield.framelib import ICRS_to_J2000

import make_ephemeris as me

ROOT = Path(__file__).resolve().parent
SET_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DAYS = 7
RISE_SET_TOLERANCE_S = 2.0
PEAK_TOLERANCE_DEG = 0.2


# --- 1. elements ------------------------------------------------------------
def fetch_tle(tries: int = 3, wait_s: float = 60.0) -> str:
    for k in range(1, tries + 1):
        try:
            text = me.fetch_tle()
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"CelesTrak, try {k}: {exc}")
        else:
            if re.search(rf"^1 {me.NORAD}", text, re.M):
                return text
            if "No GP data found" in text:
                sys.exit("CelesTrak has no elements for KNACKSAT-2, so it has most likely"
                         " re-entered. Disable the weekly workflow.")
            print(f"CelesTrak, try {k}: unexpected reply {text[:80]!r}")
        if k < tries:
            time.sleep(wait_s)
    sys.exit(f"no TLE from CelesTrak after {tries} tries")


# --- 3. checks --------------------------------------------------------------
def read_csv(path: Path) -> list[dict]:
    lines = path.read_text(encoding="ascii").splitlines()
    head = lines[0].split(",")
    return [dict(zip(head, ln.split(","))) for ln in lines[1:] if ln]


def utc(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=timezone.utc)


def pyephem_passes(l1: str, l2: str, start: datetime, end: datetime) -> list[tuple]:
    """(aos, los, peak, aos az, los az), in degrees, of each pass overlapping [start, end), no refraction."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(me.STATION_LAT), str(me.STATION_LON)
    obs.elevation = me.STATION_ALT_M
    obs.pressure = 0
    obs.horizon = "0"
    body = ephem.readtle("KNACKSAT-2", l1, l2)
    obs.date = ephem.Date((start - timedelta(minutes=30)).replace(tzinfo=None))
    out = []
    for _ in range(50 * DAYS):                  # about 4 passes a day; never loop forever
        rise, rise_az, _, peak, set_, set_az = obs.next_pass(body)
        if rise is None or set_ is None:        # up already: move on past this pass
            obs.date = ephem.Date((set_ or obs.date) + ephem.minute)
            continue
        aos, los = (ephem.Date(x).datetime().replace(tzinfo=timezone.utc) for x in (rise, set_))
        if aos >= end:
            return out
        if los > start:
            out.append((aos, los, *(float(x) * 180 / np.pi for x in (peak, rise_az, set_az))))
        obs.date = set_ + ephem.minute
    raise RuntimeError("PyEphem never reached the end of the span")


def check_passes(set_dir: Path, l1: str, l2: str, start: datetime, end: datetime) -> tuple[list, str]:
    rows = read_csv(set_dir / "passes.csv")
    ref = pyephem_passes(l1, l2, start, end)
    errors, d_time, d_peak, d_az = [], 0.0, 0.0, 0.0
    for r in rows:
        aos, los, peak = utc(r["aos_utc"]), utc(r["los_utc"]), float(r["max_el_deg"])
        near = min(ref, key=lambda p: abs((p[0] - aos).total_seconds()), default=None)
        if near is None:
            errors.append(f"pass {r['pass']}: PyEphem finds no pass at all")
            continue
        dt = max(abs((near[0] - aos).total_seconds()), abs((near[1] - los).total_seconds()))
        da = max(abs((near[3] - float(r["aos_az_deg"]) + 180) % 360 - 180),
                 abs((near[4] - float(r["los_az_deg"]) + 180) % 360 - 180))
        d_time, d_peak, d_az = max(d_time, dt), max(d_peak, abs(near[2] - peak)), max(d_az, da)
        if dt > RISE_SET_TOLERANCE_S or abs(near[2] - peak) > PEAK_TOLERANCE_DEG or da > PEAK_TOLERANCE_DEG:
            errors.append(f"pass {r['pass']} at {r['aos_utc']}: PyEphem has {near[0]:%H:%M:%S}"
                          f"-{near[1]:%H:%M:%S}, peak {near[2]:.2f} deg, azimuths {near[3]:.1f}"
                          f"/{near[4]:.1f}; the CSV has peak {peak}, azimuths {r['aos_az_deg']}"
                          f"/{r['los_az_deg']}")
    # Every pass PyEphem finds well inside the span must be in the CSV.
    aos_csv = [utc(r["aos_utc"]) for r in rows]
    for aos, los, *_ in ref:
        inside = aos >= start + timedelta(minutes=1) and los <= end - timedelta(minutes=1)
        if inside and not any(abs((aos - a).total_seconds()) <= RISE_SET_TOLERANCE_S for a in aos_csv):
            errors.append(f"PyEphem's pass at {aos:%Y-%m-%d %H:%M:%S} is missing from the CSV")
    line = (f"| Passes against PyEphem {ephem.__version__}, a separate SGP4 code, no refraction"
            f" | {len(rows)} passes, {len(ref)} from PyEphem; rise and set within {d_time:.2f} s,"
            f" peaks within {d_peak:.2f}°, rise and set azimuths within {d_az:.2f}°"
            " (the CSV rounds to 1 s and 0.1°) |")
    return errors, line


def check_oem(set_dir: Path) -> tuple[list, str]:
    oem = next(set_dir.glob("*.oem"))
    text = oem.read_text(encoding="ascii")
    errors = [] if text.startswith("CCSDS_OEM_VERS = 1.0\n") else [f"{oem.name} is not OEM version 1.0"]
    data = text.split("META_STOP\n", 1)[1].split()
    states = np.array(data, dtype=object).reshape(-1, 7)
    geo = read_csv(set_dir / "geocentric.csv")
    if len(geo) != len(states):
        return errors + [f"{len(states)} OEM states but {len(geo)} geocentric rows"], ""
    if any(s[0] != g["utc"][:-1] + ".000" for s, g in zip(states, geo)):
        errors.append("the OEM and geocentric.csv have different instants")
    r_oem = states[:, 1:4].astype(float)
    v_oem = states[:, 4:7].astype(float)
    r_geo = np.array([[float(g[f"{c}_gcrf_km"]) for c in "xyz"] for g in geo])
    v_geo = np.array([[float(g[f"v{c}_gcrf_km_s"]) for c in "xyz"] for g in geo])
    dr = np.linalg.norm(r_oem - r_geo @ ICRS_to_J2000.T, axis=1).max()
    dv = np.linalg.norm(v_oem - v_geo @ ICRS_to_J2000.T, axis=1).max()
    if dr > 1e-5 or dv > 1e-8:
        errors.append(f"the OEM is {dr * 1e6:.1f} mm / {dv * 1e9:.1f} um/s from geocentric.csv")
    line = (f"| OEM against geocentric.csv | {len(geo)} states at the same instants,"
            f" {dr * 1e6:.1f} mm apart once the frame bias is applied; CCSDS OEM 1.0 |")
    return errors, line


# --- 4. how late the previous TLE runs ----------------------------------------
def tle_lines(path: Path) -> tuple[str, str]:
    lines = [ln.strip() for ln in path.read_text(encoding="ascii").splitlines() if ln.strip()]
    return lines[-2], lines[-1]


def lateness(old: tuple[str, str], new: tuple[str, str]) -> tuple[float, float, float]:
    """(seconds the old TLE's satellite arrives late, miss km, age days) at the new epoch."""
    ts = load.timescale()
    a, b = EarthSatellite(*old, ts=ts), EarthSatellite(*new, ts=ts)
    t = b.epoch
    target = b.at(t).position.km

    def miss(dts):
        return np.linalg.norm(a.at(ts.tt_jd(t.tt + dts / 86400)).position.km - target[:, None], axis=0)

    coarse = np.arange(-3600.0, 3600.0, 5.0)
    fine = coarse[int(np.argmin(miss(coarse)))] + np.arange(-5.0, 5.0, 0.05)
    d = miss(fine)
    k = int(np.argmin(d))
    return float(fine[k]), float(d[k]), float(t - a.epoch)


def previous_set(name: str) -> Path | None:
    older = sorted(p for p in ROOT.iterdir()
                   if p.is_dir() and SET_NAME.match(p.name) and p.name < name and (p / "tle.txt").is_file())
    return older[-1] if older else None


# --- 5. publishing ------------------------------------------------------------
def day_month(dt: datetime) -> str:
    return f"{dt.day} {dt:%b}"


def list_in_readme(name: str, start: datetime, end: datetime, epoch: datetime) -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    entry = (f"- [{name}]({name}/README.md): {day_month(start)} to {day_month(end)} {end:%Y},"
             f" from the TLE of {day_month(epoch)} {epoch:%H:%M} UTC")
    lines = [ln for ln in text.splitlines() if not ln.startswith(f"- [{name}](")]
    at = lines.index("## Sets") + 2
    lines.insert(at, entry)
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tle", type=Path, help="a saved TLE instead of fetching one")
    ap.add_argument("--source", help="where the --tle file came from, for the README")
    ap.add_argument("--start", help="UTC start date (default: today)")
    ap.add_argument("--dry-run", action="store_true", help="write into _dry-run/ and publish nothing")
    ap.add_argument("--replace", action="store_true", help="overwrite a set that already exists")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")   # a Thai Windows console (cp874) has no "°"

    made = datetime.now(timezone.utc)
    start = (me.parse_start(a.start) if a.start else made).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=DAYS)
    name = f"{start:%Y-%m-%d}"
    set_dir = (ROOT / "_dry-run" if a.dry_run else ROOT) / name
    if set_dir.exists():
        if not (a.dry_run or a.replace):
            sys.exit(f"{name} exists already; pass --replace to make it again")
        shutil.rmtree(set_dir)

    if a.tle:
        tle_text, source = a.tle.read_text(encoding="ascii"), a.source or f"file `{a.tle.name}`"
    else:
        tle_text = fetch_tle()
        source = f"CelesTrak (gp.php?CATNR={me.NORAD}), fetched {made:%Y-%m-%dT%H:%MZ}"
    _, l1, l2 = me.parse_tle(tle_text)

    # 2. The set.
    set_dir.parent.mkdir(parents=True, exist_ok=True)
    fetched = set_dir.parent / f".tle-{name}.txt"
    fetched.write_text(tle_text, encoding="ascii")
    try:
        subprocess.run([sys.executable, str(ROOT / "make_ephemeris.py"), "--tle", str(fetched),
                        "--source", source, "--start", f"{start:%Y-%m-%dT%H:%M:%SZ}",
                        "--days", str(DAYS), "--out", str(set_dir)], check=True)
    finally:
        fetched.unlink()

    # 3. The checks.
    errors, pass_line = check_passes(set_dir, l1, l2, start, end)
    oem_errors, oem_line = check_oem(set_dir)
    errors += oem_errors
    if errors:
        print("NOT PUBLISHED. Failed checks:", *errors, sep="\n  ")
        sys.exit(1)

    # 4. The previous set's TLE.
    ts = load.timescale()
    epoch = EarthSatellite(l1, l2, ts=ts).epoch.utc_datetime()
    age0 = (start - epoch).total_seconds() / 86400
    prev = previous_set(name)
    if prev is None:
        drift = "There is no earlier set to compare with."
    elif tle_lines(prev / "tle.txt") == (l1, l2):
        drift = f"The previous set, {prev.name}, used these same elements: CelesTrak had nothing newer."
    else:
        late, miss_km, age = lateness(tle_lines(prev / "tle.txt"), (l1, l2))
        rate = abs(late) / age**2
        drift = (f"The previous set's TLE ([{prev.name}](../{prev.name}/README.md)), propagated {age:.1f}"
                 f" days to this TLE's epoch, reaches the same point {late:+.1f} s late (missing it by"
                 f" {miss_km:.1f} km then). That is {rate:.2f} s per day² of age. At that rate this set's"
                 f" passes come about {rate * (age0 + DAYS) ** 2:.0f} s early by its last day.")

    (set_dir / "CHECKS.md").write_text("\n".join([
        "# Checks on this set",
        "",
        f"Made by `weekly.py` at {made:%Y-%m-%d %H:%M} UTC, which publishes nothing that fails a check.",
        "",
        "| Check | Result |",
        "|---|---|",
        pass_line,
        oem_line,
        f"| TLE age | {age0:.2f} days at the start of the span, {age0 + DAYS:.2f} at the end |",
        "",
        "## How late the last set's TLE ran",
        "",
        drift,
        "",
        "The first set, [2026-10-29](../2026-10-29/CHECKS.md), was also checked against satellite.js and GMAT.",
        "",
    ]), encoding="utf-8")
    print(pass_line, oem_line, drift, sep="\n")

    # 5. Publish.
    if not a.dry_run:
        latest = ROOT / "latest"
        if latest.exists():
            shutil.rmtree(latest)
        shutil.copytree(set_dir, latest)
        list_in_readme(name, start, end, epoch)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"set={name}\n")
    print(f"{'dry run: ' if a.dry_run else ''}{name} -> {set_dir}")


if __name__ == "__main__":
    main()

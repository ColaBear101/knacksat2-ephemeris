#!/usr/bin/env python3
"""Ephemerides for KNACKSAT-2 (NORAD 67683) from its newest TLE.

One run writes a folder for a span that starts now (or at --start):

  passes.csv          every pass over the ground station: AOS, TCA and LOS in
                      UTC and ICT, the azimuth at each, and the peak elevation
  pass_tracks.csv     az/el, range, range rate and the Doppler-corrected
                      frequencies of both transmitters, every second of a pass
  geocentric.csv      the sub-satellite point and the GCRF state every minute
  KNACKSAT-2_*.oem    the same states as a CCSDS OEM in EME2000, the inertial
                      frame GMAT's CCSDS-OEM propagator reads
  tle.txt, README.md  the elements used, and what was made from them

Propagation is SGP4 through Skyfield, as in the dashboard's predictor.py, so a
pass here has the dashboard's AOS and LOS for the same TLE. At about 340 km a
TLE goes stale in days: make a new set every day or two and keep the span short.

    python make_ephemeris.py                       # newest TLE from CelesTrak
    python make_ephemeris.py --tle old.tle --start 2026-11-01T00:00Z --days 2

CelesTrak blocks clients that ask for the same data more often than every two
hours, so --tle a saved file when running this repeatedly.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from skyfield.api import EarthSatellite, load, load_file, wgs84
from skyfield.framelib import ICRS_to_J2000

NORAD = 67683
CELESTRAK_URL = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={NORAD}&FORMAT=TLE"

# The ground station (WGS84).
STATION_NAME = "Bangkok ground station"
STATION_LAT = 13.823781779271652
STATION_LON = 100.51295302800892
STATION_ALT_M = 60.0
MIN_CULMINATION_DEG = 10.0      # the lowest peak the station schedules

# SatNOGS DB on 2026-10-29: both alive and active.
UHF_DOWN_HZ = 400_630_000       # Mode U, FSK 9k6 AX.25 G3RUH telemetry (downlink only)
VHF_HZ = 145_825_000            # Mode V/V, FSK 9k6 digipeater (same frequency up and down)
C_KM_S = 299_792.458

ICT = timezone(timedelta(hours=7), "ICT")

# The Sun comes from a JPL ephemeris for the sunlit columns. GMAT ships DE421,
# so an installed GMAT saves a 17 MB download; without one the columns are left out.
DE421_PLACES = [
    Path(__file__).with_name("de421.bsp"),
    Path.home() / "Documents/GMAT_R2025a/data/planetary_ephem/spk/de421.bsp",
]


# --- elements ---------------------------------------------------------------
def tle_checksum_ok(line: str) -> bool:
    total = sum(int(c) if c.isdigit() else (c == "-") for c in line[:68])
    return len(line) >= 69 and line[68].isdigit() and total % 10 == int(line[68])


def parse_tle(text: str) -> tuple[str, str, str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for i in range(len(lines) - 1):
        if lines[i].startswith("1 ") and lines[i + 1].startswith("2 "):
            name = lines[i - 1] if i and not lines[i - 1][:2] in ("1 ", "2 ") else "KNACKSAT-2"
            l1, l2 = lines[i], lines[i + 1]
            for ln in (l1, l2):
                if not tle_checksum_ok(ln):
                    sys.exit(f"bad TLE checksum: {ln}")
            if int(l1[2:7]) != NORAD or int(l2[2:7]) != NORAD:
                sys.exit(f"these elements are for NORAD {l1[2:7]}, not KNACKSAT-2 ({NORAD})")
            return name.removeprefix("0 "), l1, l2
    sys.exit("no TLE found")


def fetch_tle() -> str:
    req = urllib.request.Request(CELESTRAK_URL, headers={"User-Agent": "knacksat2-ephemeris"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("ascii", "replace")


def cospar_id(l1: str) -> str:
    """'98067YA ' -> '1998-067YA'."""
    yy, rest = int(l1[9:11]), l1[11:17].strip()
    return f"{1900 + yy if yy >= 57 else 2000 + yy}-{rest[:3]}{rest[3:]}"


# --- time -------------------------------------------------------------------
def parse_start(text: str | None) -> datetime:
    if text is None:
        return datetime.now(timezone.utc).replace(second=0, microsecond=0)
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return dt.replace(tzinfo=dt.tzinfo or timezone.utc).astimezone(timezone.utc)


def utc_iso(dt: datetime, ms: bool = False) -> str:
    if ms:
        return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}"
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def ict_str(dt: datetime) -> str:
    return dt.astimezone(ICT).strftime("%Y-%m-%d %H:%M:%S")


def round_s(dt: datetime) -> datetime:
    return (dt + timedelta(microseconds=500_000)).replace(microsecond=0)


class Clock:
    """Arrays of Skyfield times as whole seconds from one UTC midnight."""

    def __init__(self, ts, origin: datetime):
        self.ts = ts
        self.origin = origin.replace(hour=0, minute=0, second=0, microsecond=0)

    def secs(self, dt: datetime) -> float:
        return (dt - self.origin).total_seconds()

    def at(self, secs):
        o = self.origin
        return self.ts.utc(o.year, o.month, o.day, 0, 0, np.asarray(secs, dtype=float))

    def dt(self, secs: float) -> datetime:
        return self.origin + timedelta(seconds=float(secs))


# --- passes -----------------------------------------------------------------
def find_passes(sat, site, clock: Clock, start: datetime, end: datetime, min_el: float):
    """Passes that overlap [start, end), as (aos, tca, los) in seconds from the clock's origin.

    Skyfield finds the events to about half a second. Each is then pinned down
    on a 0.1 s grid: rise and set by interpolating the elevation's zero
    crossing, the peak by a parabola through the three highest samples.
    """
    diff = sat - site
    ts = clock.ts
    t0 = ts.from_datetime(start - timedelta(minutes=30))
    t1 = ts.from_datetime(end + timedelta(minutes=30))
    times, events = sat.find_events(site, t0, t1, altitude_degrees=min_el)

    def el_on(grid):
        return diff.at(clock.at(grid)).altaz()[0].degrees

    def crossing(s, rising):
        grid = s + np.arange(-20, 21) * 0.1
        y = el_on(grid) - min_el
        sign = np.signbit(y)
        idx = np.flatnonzero(sign[:-1] != sign[1:])
        idx = [i for i in idx if (y[i + 1] > y[i]) == rising]
        if not idx:
            return s
        i = min(idx, key=lambda k: abs(grid[k] - s))
        return grid[i] + 0.1 * y[i] / (y[i] - y[i + 1])

    def peak(s):
        grid = s + np.arange(-100, 101) * 0.1
        y = el_on(grid)
        i = int(np.clip(np.argmax(y), 1, len(y) - 2))
        y0, y1, y2 = y[i - 1:i + 2]
        bend = y0 - 2 * y1 + y2
        return grid[i] + (0.05 * (y0 - y2) / bend if bend else 0.0)

    out, rise, culms = [], None, []
    for t, ev in zip(times, events):
        s = clock.secs(t.utc_datetime())
        if ev == 0:
            rise, culms = s, []
        elif ev == 1 and rise is not None:
            culms.append(s)
        elif ev == 2 and rise is not None:
            aos, los = crossing(rise, True), crossing(s, False)
            # A pass can report more than one culmination; keep the highest.
            tops = [peak(c) for c in (culms or [(aos + los) / 2])]
            tca = max(tops, key=lambda c: float(el_on([c])[0]))
            if los > clock.secs(start) and aos < clock.secs(end):
                out.append((aos, tca, los))
            rise = None
    return out


def look(diff, clock: Clock, secs):
    """az, el, range, range rate at each time (arrays)."""
    topo = diff.at(clock.at(secs))
    el, az, dist = topo.altaz()
    rate = np.einsum("ij,ij->j", topo.position.km, topo.velocity.km_per_s) / dist.km
    return az.degrees, el.degrees, dist.km, rate


def doppler(f_hz, rate_km_s):
    """Received frequency of a carrier sent at f_hz (first order)."""
    return f_hz * (1.0 - rate_km_s / C_KM_S)


# --- writers ----------------------------------------------------------------
def write_csv(path: Path, header: list[str], rows) -> int:
    n = 0
    with path.open("w", newline="", encoding="ascii") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in rows:
            w.writerow(row)
            n += 1
    return n


def write_oem(path: Path, name, l1, l2, made, secs, clock, r_km, v_kms):
    first, last = clock.dt(secs[0]), clock.dt(secs[-1])
    with path.open("w", newline="\n", encoding="ascii") as f:
        # 1.0, not 2.0: GMAT R2025a reads a version 2 OEM only in its testing mode.
        f.write("CCSDS_OEM_VERS = 1.0\n")
        f.write(f"COMMENT {name} (NORAD {NORAD}) by SGP4 (Skyfield) from this TLE:\n")
        f.write(f"COMMENT {l1}\nCOMMENT {l2}\n")
        f.write("COMMENT GCRS from Skyfield, rotated to EME2000 by the IERS frame bias.\n")
        f.write(f"CREATION_DATE = {utc_iso(made, ms=True)}\n")
        f.write("ORIGINATOR = make_ephemeris.py\n\n")
        f.write("META_START\n")
        f.write(f"OBJECT_NAME = {name}\n")
        f.write(f"OBJECT_ID = {cospar_id(l1)}\n")
        f.write("CENTER_NAME = EARTH\n")
        f.write("REF_FRAME = EME2000\n")
        f.write("TIME_SYSTEM = UTC\n")
        f.write(f"START_TIME = {utc_iso(first, ms=True)}\n")
        f.write(f"STOP_TIME = {utc_iso(last, ms=True)}\n")
        f.write("INTERPOLATION = LAGRANGE\n")
        f.write("INTERPOLATION_DEGREE = 7\n")
        f.write("META_STOP\n\n")
        for k, s in enumerate(secs):
            x, y, z = r_km[:, k]
            vx, vy, vz = v_kms[:, k]
            f.write(f"{utc_iso(clock.dt(s), ms=True)} {x:15.6f} {y:15.6f} {z:15.6f}"
                    f" {vx:12.9f} {vy:12.9f} {vz:12.9f}\n")


def az_word(az: float) -> str:
    return "N NE E SE S SW W NW".split()[int(((az % 360) + 22.5) // 45) % 8]


# --- main -------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tle", type=Path, help="TLE file (2 or 3 lines); default: fetch from CelesTrak")
    ap.add_argument("--source", help="where the --tle file came from, for the README")
    ap.add_argument("--start", help="UTC start, ISO 8601 (default: now, to the minute)")
    ap.add_argument("--days", type=float, default=7.0)
    ap.add_argument("--geo-step", type=int, default=60, help="seconds between geocentric/OEM states")
    ap.add_argument("--track-step", type=int, default=1, help="seconds between pass-track rows")
    ap.add_argument("--min-el", type=float, default=0.0, help="AOS/LOS elevation, degrees")
    ap.add_argument("--bsp", type=Path, help="JPL ephemeris for the sunlit columns (default: look for de421.bsp)")
    ap.add_argument("--out", type=Path, help="output folder (default: next to this script, named by start date)")
    a = ap.parse_args()

    made = datetime.now(timezone.utc)
    if a.tle:
        source = a.source or f"file `{a.tle.name}`"
        tle_text = a.tle.read_text(encoding="ascii", errors="replace")
    else:
        source = f"{CELESTRAK_URL} at {utc_iso(made)}"
        tle_text = fetch_tle()
    name, l1, l2 = parse_tle(tle_text)

    start = parse_start(a.start)
    end = start + timedelta(days=a.days)
    out = a.out or Path(__file__).resolve().parent / start.strftime("%Y-%m-%d")
    out.mkdir(parents=True, exist_ok=True)

    ts = load.timescale()               # builtin tables: nothing downloaded
    sat = EarthSatellite(l1, l2, name, ts)
    epoch = sat.epoch.utc_datetime()
    age_d = (start - epoch).total_seconds() / 86400
    site = wgs84.latlon(STATION_LAT, STATION_LON, elevation_m=STATION_ALT_M)
    diff = sat - site
    clock = Clock(ts, start)

    bsp = a.bsp or next((p for p in DE421_PLACES if p.is_file()), None)
    eph = load_file(str(bsp)) if bsp else None

    def sunlit(secs):
        if eph is None:
            return None
        return sat.at(clock.at(secs)).is_sunlit(eph)

    # Passes and their tracks.
    passes = find_passes(sat, site, clock, start, end, a.min_el)
    pass_rows, track_rows, table = [], [], []
    for n, (aos, tca, los) in enumerate(passes, 1):
        az3, el3, rng3, _ = look(diff, clock, [aos, tca, los])
        step = a.track_step
        grid = np.arange(math.ceil(aos / step) * step, math.floor(los / step) * step + 1e-6, step)
        if grid.size == 0:              # a pass shorter than one step: keep its peak
            grid = np.array([tca])
        az, el, rng, rate = look(diff, clock, grid)
        lit = sunlit(grid)
        lit_word = "" if lit is None else ("yes" if lit.all() else "no" if not lit.any() else "part")
        rx_uhf = doppler(UHF_DOWN_HZ, rate)
        rx_vhf = doppler(VHF_HZ, rate)
        tx_vhf = VHF_HZ * (1.0 + rate / C_KM_S)  # sent so that the satellite hears VHF_HZ
        for k, s in enumerate(grid):
            dt = clock.dt(s)
            track_rows.append([
                n, utc_iso(dt), ict_str(dt), f"{az[k]:.3f}", f"{el[k]:.3f}", f"{rng[k]:.3f}",
                f"{rate[k]:.5f}", f"{rx_uhf[k] - UHF_DOWN_HZ:.0f}", f"{rx_uhf[k]:.0f}",
                f"{rx_vhf[k]:.0f}", f"{tx_vhf[k]:.0f}",
            ] + ([] if lit is None else [int(lit[k])]))
        t_aos, t_tca, t_los = (round_s(clock.dt(s)) for s in (aos, tca, los))
        dur = los - aos
        pass_rows.append([
            n, utc_iso(t_aos), utc_iso(t_tca), utc_iso(t_los),
            ict_str(t_aos), ict_str(t_tca), ict_str(t_los),
            f"{dur:.0f}", f"{az3[0]:.1f}", f"{az3[1]:.1f}", f"{az3[2]:.1f}", f"{el3[1]:.1f}",
            f"{rng3[1]:.1f}", "yes" if el3[1] >= MIN_CULMINATION_DEG else "no",
            f"{(rx_uhf.max() - UHF_DOWN_HZ) / 1e3:+.2f}", f"{(rx_uhf.min() - UHF_DOWN_HZ) / 1e3:+.2f}",
        ] + ([] if lit is None else [lit_word]))
        table.append((n, t_aos, t_tca, t_los, dur, az3, el3[1], lit_word))

    lit_col = [] if eph is None else ["sunlit"]
    write_csv(out / "passes.csv", [
        "pass", "aos_utc", "tca_utc", "los_utc", "aos_ict", "tca_ict", "los_ict",
        "duration_s", "aos_az_deg", "tca_az_deg", "los_az_deg", "max_el_deg", "tca_range_km",
        f"max_el_ge_{MIN_CULMINATION_DEG:g}deg", "uhf_doppler_max_khz", "uhf_doppler_min_khz",
    ] + lit_col, pass_rows)
    write_csv(out / "pass_tracks.csv", [
        "pass", "utc", "ict", "az_deg", "el_deg", "range_km", "range_rate_km_s",
        "uhf_doppler_hz", f"uhf_rx_hz_{UHF_DOWN_HZ}", f"vhf_rx_hz_{VHF_HZ}", f"vhf_tx_hz_{VHF_HZ}",
    ] + lit_col, track_rows)

    # Geocentric states.
    s0 = clock.secs(start)
    secs = s0 + np.arange(0, int(a.days * 86400) + 1, a.geo_step)
    geo = sat.at(clock.at(secs))
    r, v = geo.position.km, geo.velocity.km_per_s
    lat, lon = wgs84.latlon_of(geo)
    h = wgs84.height_of(geo).km
    lit = sunlit(secs)
    rows = []
    for k, s in enumerate(secs):
        rows.append([utc_iso(clock.dt(s)), f"{lat.degrees[k]:.5f}", f"{lon.degrees[k]:.5f}", f"{h[k]:.3f}"]
                    + [f"{c:.6f}" for c in r[:, k]] + [f"{c:.9f}" for c in v[:, k]]
                    + ([] if lit is None else [int(lit[k])]))
    write_csv(out / "geocentric.csv", [
        "utc", "lat_deg", "lon_deg", "alt_km",
        "x_gcrf_km", "y_gcrf_km", "z_gcrf_km", "vx_gcrf_km_s", "vy_gcrf_km_s", "vz_gcrf_km_s",
    ] + lit_col, rows)

    oem = out / f"KNACKSAT-2_{start:%Y-%m-%d}.oem"
    write_oem(oem, name, l1, l2, made, secs, clock, ICRS_to_J2000 @ r, ICRS_to_J2000 @ v)
    (out / "tle.txt").write_text(f"{name}\n{l1}\n{l2}\n", encoding="ascii")

    # README.
    up = sum(1 for p in table if p[6] >= MIN_CULMINATION_DEG)
    md = [
        f"# KNACKSAT-2 ephemerides, {start:%d %b %Y %H:%M} UTC + {a.days:g} days",
        "",
        f"Made {utc_iso(made)} by `make_ephemeris.py` (Skyfield SGP4). Elements from {source}:",
        "",
        "```", name, l1, l2, "```",
        "",
        f"- TLE epoch **{utc_iso(round_s(epoch))}**: {age_d:.2f} days old at the start of the span,"
        f" {age_d + a.days:.2f} at the end.",
        "- At this height a TLE goes stale in days. One fitted to past tracking underestimates the"
        " drag to come (KNACKSAT-2's own TLEs in Sep-Oct 2026 ran 32 s late after 18 days), so"
        " passes late in the span are likely to come early. For the best times, make a fresh set"
        " with `python make_ephemeris.py`.",
        f"- Height above the WGS84 ellipsoid {h.min():.1f}-{h.max():.1f} km over the span (mean {h.mean():.1f}).",
        f"- Station: {STATION_NAME}, {STATION_LAT:.5f} N {STATION_LON:.5f} E, {STATION_ALT_M:g} m.",
        f"- AOS/LOS at {a.min_el:g} deg geometric elevation (no refraction), as the dashboard uses;"
        f" {up} of {len(table)} passes peak at {MIN_CULMINATION_DEG:g} deg or more.",
        "- Azimuth from true north through east. Range rate positive when receding.",
        f"- Doppler: `uhf_rx` is what reaches the station from {UHF_DOWN_HZ/1e6:.3f} MHz;"
        f" `vhf_tx` is what to send so the digipeater hears {VHF_HZ/1e6:.3f} MHz.",
        "- GCRF is Skyfield's GCRS. The OEM is the same states in EME2000 (J2000 mean equator),"
        " rotated by the IERS frame bias, which moves a point here by under a metre.",
        "- `sunlit` is 1 when the Sun is not behind the Earth (DE421 Sun, spherical Earth, no penumbra)."
        if eph is not None else "- No DE421 file was found, so there are no sunlit columns.",
        "",
        "| File | What |",
        "|---|---|",
        f"| `passes.csv` | {len(pass_rows)} passes: AOS/TCA/LOS in UTC and ICT, azimuths, peak elevation |",
        f"| `pass_tracks.csv` | {len(track_rows)} rows, every {a.track_step} s of every pass:"
        " az/el, range, range rate, Doppler |",
        f"| `geocentric.csv` | {len(rows)} rows, every {a.geo_step} s: lat/lon/alt and GCRF position/velocity |",
        f"| `{oem.name}` | CCSDS OEM 1.0, EME2000, UTC, the same {len(rows)} states |",
        "| `tle.txt` | the elements above |",
        "",
        "## Passes over the station",
        "",
        f"Times are rounded to the second. ICT = UTC+7. Peaks of {MIN_CULMINATION_DEG:g}° or more are in bold."
        + (" Sun: sunlit for all, none or part of the pass." if eph is not None else ""),
        "",
        "| # | AOS (ICT) | LOS (ICT) | AOS (UTC) | Dur | Peak | Azimuth AOS / peak / LOS |"
        + (" Sun |" if eph is not None else ""),
        "|---:|---|---|---|---:|---:|---|" + ("---|" if eph is not None else ""),
    ]
    for n, t_aos, t_tca, t_los, dur, az3, max_el, lit_word in table:
        peak = f"**{max_el:.1f}°**" if max_el >= MIN_CULMINATION_DEG else f"{max_el:.1f}°"
        md.append(
            f"| {n} | {t_aos.astimezone(ICT):%a %d %b %H:%M:%S} | {t_los.astimezone(ICT):%H:%M:%S}"
            f" | {t_aos:%d %b %H:%M:%S} | {int(dur // 60)}:{int(dur % 60):02d} | {peak}"
            f" | {az3[0]:.0f}° {az_word(az3[0])} / {az3[1]:.0f}° {az_word(az3[1])} / {az3[2]:.0f}° {az_word(az3[2])} |"
            + (f" {lit_word} |" if eph is not None else ""))
    # GMAT's interpolator wants points either side, so start and stop inside the file.
    gmat_epoch = start + timedelta(minutes=10)
    md += [
        "",
        "## Loading the OEM in GMAT",
        "",
        "```",
        "Create Spacecraft KNACKSAT2;",
        "GMAT KNACKSAT2.DateFormat = UTCGregorian;",
        f"GMAT KNACKSAT2.Epoch = '{gmat_epoch:%d %b %Y %H:%M:%S}.000';",
        f"GMAT KNACKSAT2.EphemerisName = '<this folder>/{oem.name}';",
        "Create Propagator OEMProp;",
        "GMAT OEMProp.Type = CCSDS-OEM;",
        "GMAT OEMProp.StepSize = 60;",
        "GMAT OEMProp.StartEpoch = 'FromSpacecraft';",
        "BeginMissionSequence;",
        f"Propagate OEMProp(KNACKSAT2) {{KNACKSAT2.ElapsedDays = {a.days - 1 / 24:.4f}}};",
        "```",
        "",
        "Put this folder's full path in place of `<this folder>`: GMAT reads a relative path"
        " from its own bin folder.",
        "",
    ]
    (out / "README.md").write_text("\n".join(md), encoding="utf-8")

    print(f"{name}: epoch {utc_iso(round_s(epoch))}, {age_d:+.2f} d old at {utc_iso(start)}")
    print(f"{len(table)} passes ({up} peak >= {MIN_CULMINATION_DEG:g} deg), "
          f"{len(track_rows)} track rows, {len(rows)} states -> {out}")


if __name__ == "__main__":
    main()

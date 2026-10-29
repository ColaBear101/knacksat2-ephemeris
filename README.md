# KNACKSAT-2 ephemerides

Ephemerides for KNACKSAT-2 (NORAD 67683) as seen from a ground station in Bangkok. They are made from the newest TLE with SGP4 through Skyfield. That is the same propagation the KNACKSAT-2 ground-station dashboard uses, so for the same TLE the pass times agree with it.

## Use

```bash
pip install -r requirements.txt
python make_ephemeris.py
```

That fetches the TLE from CelesTrak and writes the 7 days from now into a folder named by the start date. The station and the two frequencies are constants at the top of `make_ephemeris.py`.

| Option | Default | |
|---|---|---|
| `--tle FILE` | fetch from CelesTrak | A saved 2- or 3-line TLE. CelesTrak blocks clients that fetch the same data more often than every two hours. |
| `--source TEXT` | | Where that file came from, for the README. |
| `--start ISO` | now | UTC start, e.g. `2026-11-01T00:00Z`. |
| `--days N` | 7 | Length of the span. |
| `--geo-step S` | 60 | Seconds between geocentric/OEM states. |
| `--track-step S` | 1 | Seconds between pass-track rows. |
| `--min-el DEG` | 0 | Elevation for AOS and LOS. |
| `--bsp FILE` | finds `de421.bsp` | JPL ephemeris for the sunlit columns, looked for next to the script and in GMAT R2025a. Without one, those columns are left out. |
| `--out DIR` | `./<start date>` | Output folder. |

## What a run writes

| File | |
|---|---|
| `passes.csv` | Each pass: AOS, TCA and LOS in UTC and ICT, the azimuth at each, peak elevation, range at the peak, Doppler range, sunlit |
| `pass_tracks.csv` | Every second of every pass: az/el, range, range rate, the received 400.630 MHz and 145.825 MHz, and the 145.825 MHz to transmit |
| `geocentric.csv` | Every minute: latitude, longitude, height, and GCRF position and velocity |
| `KNACKSAT-2_<date>.oem` | The same states as a CCSDS OEM 1.0 in EME2000, which GMAT's CCSDS-OEM propagator reads (GMAT R2025a refuses version 2) |
| `tle.txt`, `README.md` | The elements used, and a table of the passes |

## Accuracy

The files reproduce SGP4 to their printed rounding. They were checked against satellite.js, PyEphem and GMAT; see [2026-10-29/CHECKS.md](2026-10-29/CHECKS.md).

The limit is the TLE itself. KNACKSAT-2 is around 343 km and decaying faster than each TLE's drag term assumes: its TLEs in Sep–Oct 2026 ran 32 s late after 18 days. Make a new set every day or two.

## Sets

- [2026-10-29](2026-10-29/README.md): 29 Oct to 5 Nov 2026, from the TLE of 28 Oct 08:15 UTC

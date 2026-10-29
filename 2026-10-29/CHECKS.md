# Checks on this file set

Run on 29 Oct 2026 against the files in this folder. Each check uses a separate implementation and compares every row unless a row count is given.

| Check | Against | Result |
|---|---|---|
| AOS/LOS of all 28 passes | satellite.js 6.0.1 (its own SGP4 port and event search), given UT1 | within 1 ms |
| AOS/LOS of all 28 passes | PyEphem 4.1.6, no refraction | within 0.02 s |
| 13,373 pass-track rows | satellite.js look angles and range rate | az/el 0.0005°, range 1 m, range rate 10 mm/s, UHF Doppler 0.5 Hz: the printed rounding |
| 10,081 geocentric rows | satellite.js geodetic point | lat/lon 0.00001°, height 0.5 m: the printed rounding |
| TEME state | satellite.js vs python-sgp4 (Skyfield's) | 65 mm apart after 7 days |
| OEM frame | the GCRF rows rotated by the IERS frame bias | 1.6 mm (rounding); the bias itself moves a point 0.76 m |
| OEM interpolation | 8-point Lagrange at each of 10,074 midpoints vs SGP4 | 1 mm |
| OEM in GMAT R2025a | CCSDS-OEM propagator, 30 s steps over 6.9 days | 2 mm from the file at its points, 3 mm from SGP4 between them; GMAT's own Earth model puts the ground point within 19 m and the height within 0.7 m |
| GMAT snippet in README | run as written in GmatConsole | "Mission run completed" |

Not checked independently: the `sunlit` flags. They come from Skyfield's `is_sunlit` with DE421 and show the satellite sunlit for 62.7 % of the span.

## Notes

- **UT1 matters at this level.** satellite.js treats UTC as UT1. Left that way, it differs from these files by up to 11 ms at AOS/LOS and by 0.45 m/s in range rate near the peak. UT1−UTC is +0.089 s now, which shifts the station about 40 m. These files use UT1.
- **OEM version 1.0.** GMAT R2025a refuses a version 2 OEM outside its testing mode.

## How fast these elements go stale

These are KNACKSAT-2's own older TLEs, each propagated to a newer TLE's epoch and timed against it:

| Older TLE | To the epoch of | Age | Its satellite arrives late by |
|---|---|---:|---:|
| 12 Sep | 10 Oct | 28.4 d | 222 s |
| 10 Oct | 28 Oct | 17.6 d | 32 s |
| 12 Sep | 28 Oct | 46.0 d | 1,183 s |

The real satellite was always ahead: it is decaying faster than each TLE's drag term assumes. Mean altitude from mean motion was 363.3 km (12 Sep), 352.4 km (10 Oct) and 342.6 km (28 Oct), so the loss sped up from 0.38 to 0.56 km per day.

That growth is about 0.10–0.28 s per day² of age. At that rate, this set's passes come early by under 1 s on its first day and by roughly 6–17 s on its last day, when the TLE will be 7.85 days old. Make a new set every day or two.

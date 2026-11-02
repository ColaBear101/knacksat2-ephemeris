# Checks on this set

Made by `weekly.py` at 2026-11-02 06:04 UTC, which publishes nothing that fails a check.

| Check | Result |
|---|---|
| Passes against PyEphem 4.1.6, a separate SGP4 code, no refraction | 29 passes, 29 from PyEphem; rise and set within 0.49 s, peaks within 0.05°, rise and set azimuths within 0.05° (the CSV rounds to 1 s and 0.1°) |
| OEM against geocentric.csv | 10081 states at the same instants, 1.4 mm apart once the frame bias is applied; CCSDS OEM 1.0 |
| TLE age | 0.41 days at the start of the span, 7.41 at the end |

## How late the last set's TLE ran

The previous set's TLE ([2026-10-29](../2026-10-29/README.md)), propagated 4.2 days to this TLE's epoch, reaches the same point +9.3 s late (missing it by 1.0 km then). That is 0.52 s per day² of age. At that rate this set's passes come about 28 s early by its last day.

The first set, [2026-10-29](../2026-10-29/CHECKS.md), was also checked against satellite.js and GMAT.

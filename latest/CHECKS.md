# Checks on this set

Made by `weekly.py` at 2026-11-09 06:30 UTC, which publishes nothing that fails a check.

| Check | Result |
|---|---|
| Passes against PyEphem 4.1.6, a separate SGP4 code, no refraction | 28 passes, 28 from PyEphem; rise and set within 0.49 s, peaks within 0.05°, rise and set azimuths within 0.05° (the CSV rounds to 1 s and 0.1°) |
| OEM against geocentric.csv | 10081 states at the same instants, 1.5 mm apart once the frame bias is applied; CCSDS OEM 1.0 |
| TLE age | 1.77 days at the start of the span, 8.77 at the end |

## How late the last set's TLE ran

The previous set's TLE ([2026-11-02](../2026-11-02/README.md)), propagated 5.6 days to this TLE's epoch, reaches the same point -4.9 s late (missing it by 1.2 km then). That is 0.15 s per day² of age. At that rate this set's passes come about 12 s early by its last day.

The first set, [2026-10-29](../2026-10-29/CHECKS.md), was also checked against satellite.js and GMAT.

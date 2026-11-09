# KNACKSAT-2 ephemerides, 09 Nov 2026 00:00 UTC + 7 days

Made 2026-11-09T06:30:10Z by `make_ephemeris.py` (Skyfield SGP4). Elements from CelesTrak (gp.php?CATNR=67683), fetched 2026-11-09T06:30Z:

```
KNACKSAT-2
1 67683U 98067YA  26311.23189889  .00158629  00000+0  90831-3 0  9995
2 67683  51.6228 286.9141 0009576  49.5310 310.6524 15.77766899 42716
```

- TLE epoch **2026-11-07T05:33:56Z**: 1.77 days old at the start of the span, 8.77 at the end.
- At this height a TLE goes stale in days. One fitted to past tracking underestimates the drag to come (KNACKSAT-2's own TLEs in Sep-Oct 2026 ran 32 s late after 18 days), so passes late in the span are likely to come early. For the best times, make a fresh set with `python make_ephemeris.py`.
- Height above the WGS84 ellipsoid 325.4-358.3 km over the span (mean 338.2).
- Station: Bangkok ground station, 13.82378 N 100.51295 E, 60 m.
- AOS/LOS at 0 deg geometric elevation (no refraction), as the dashboard uses; 18 of 28 passes peak at 10 deg or more.
- Azimuth from true north through east. Range rate positive when receding.
- Doppler: `uhf_rx` is what reaches the station from 400.630 MHz; `vhf_tx` is what to send so the digipeater hears 145.825 MHz.
- GCRF is Skyfield's GCRS. The OEM is the same states in EME2000 (J2000 mean equator), rotated by the IERS frame bias, which moves a point here by under a metre.
- `sunlit` is 1 when the Sun is not behind the Earth (DE421 Sun, spherical Earth, no penumbra).

| File | What |
|---|---|
| `passes.csv` | 28 passes: AOS/TCA/LOS in UTC and ICT, azimuths, peak elevation |
| `pass_tracks.csv` | 12586 rows, every 1 s of every pass: az/el, range, range rate, Doppler |
| `geocentric.csv` | 10081 rows, every 60 s: lat/lon/alt and GCRF position/velocity |
| `KNACKSAT-2_2026-11-09.oem` | CCSDS OEM 1.0, EME2000, UTC, the same 10081 states |
| `tle.txt` | the elements above |

## Passes over the station

Times are rounded to the second. ICT = UTC+7. Peaks of 10° or more are in bold. Sun: sunlit for all, none or part of the pass.

| # | AOS (ICT) | LOS (ICT) | AOS (UTC) | Dur | Peak | Azimuth AOS / peak / LOS | Sun |
|---:|---|---|---|---:|---:|---|---|
| 1 | Mon 09 Nov 14:42:49 | 14:46:01 | 09 Nov 07:42:49 | 3:12 | 1.1° | 143° SE / 123° SE / 103° E | yes |
| 2 | Mon 09 Nov 16:14:17 | 16:23:45 | 09 Nov 09:14:17 | 9:27 | **63.2°** | 222° SW / 307° NW / 33° NE | yes |
| 3 | Tue 10 Nov 01:56:33 | 02:05:41 | 09 Nov 18:56:33 | 9:07 | **24.4°** | 338° N / 51° NE / 124° SE | no |
| 4 | Tue 10 Nov 03:32:16 | 03:39:18 | 09 Nov 20:32:16 | 7:02 | 7.0° | 284° W / 236° SW / 188° S | no |
| 5 | Tue 10 Nov 15:00:19 | 15:08:46 | 10 Nov 08:00:19 | 8:26 | **15.1°** | 188° S / 125° SE / 61° NE | yes |
| 6 | Tue 10 Nov 16:35:16 | 16:43:21 | 10 Nov 09:35:16 | 8:04 | **11.8°** | 252° W / 311° NW / 10° N | yes |
| 7 | Wed 11 Nov 00:43:23 | 00:49:05 | 10 Nov 17:43:23 | 5:41 | 3.8° | 9° N / 46° NE / 83° E | no |
| 8 | Wed 11 Nov 02:16:28 | 02:25:56 | 10 Nov 19:16:28 | 9:27 | **46.6°** | 315° NW / 234° SW / 152° SE | no |
| 9 | Wed 11 Nov 15:19:39 | 15:29:07 | 11 Nov 08:19:39 | 9:28 | **85.0°** | 218° SW / 307° NW / 37° NE | yes |
| 10 | Wed 11 Nov 16:58:07 | 17:00:50 | 11 Nov 09:58:07 | 2:43 | 0.7° | 298° NW / 315° NW / 333° NW | yes |
| 11 | Thu 12 Nov 01:01:47 | 01:10:39 | 11 Nov 18:01:47 | 8:51 | **19.5°** | 342° N / 51° NE / 119° SE | no |
| 12 | Thu 12 Nov 02:37:06 | 02:44:39 | 11 Nov 19:37:06 | 7:32 | 9.0° | 288° W / 236° SW / 183° S | no |
| 13 | Thu 12 Nov 14:05:19 | 14:13:21 | 12 Nov 07:05:19 | 8:02 | **11.9°** | 183° S / 124° SE / 66° NE | yes |
| 14 | Thu 12 Nov 15:39:49 | 15:48:14 | 12 Nov 08:39:49 | 8:25 | **14.7°** | 247° SW / 310° NW / 14° N | yes |
| 15 | Thu 12 Nov 23:48:24 | 23:53:01 | 12 Nov 16:48:24 | 4:36 | 2.3° | 16° N / 46° NE / 75° E | no |
| 16 | Fri 13 Nov 01:20:57 | 01:30:27 | 12 Nov 18:20:57 | 9:29 | **65.2°** | 319° NW / 234° SW / 148° SE | no |
| 17 | Fri 13 Nov 14:23:49 | 14:33:15 | 13 Nov 07:23:49 | 9:25 | **67.5°** | 213° SW / 127° SE / 40° NE | yes |
| 18 | Fri 13 Nov 16:01:21 | 16:05:42 | 13 Nov 09:01:21 | 4:21 | 2.0° | 287° W / 315° NW / 342° N | yes |
| 19 | Sat 14 Nov 00:05:51 | 00:14:20 | 13 Nov 17:05:51 | 8:29 | **15.1°** | 346° N / 50° NE / 114° SE | no |
| 20 | Sat 14 Nov 01:40:43 | 01:48:46 | 13 Nov 18:40:43 | 8:02 | **11.7°** | 294° NW / 236° SW / 177° S | no |
| 21 | Sat 14 Nov 13:09:11 | 13:16:38 | 14 Nov 06:09:11 | 7:27 | 8.8° | 177° S / 124° SE / 72° E | yes |
| 22 | Sat 14 Nov 14:43:08 | 14:51:53 | 14 Nov 07:43:08 | 8:44 | **18.9°** | 241° SW / 310° NW / 18° N | yes |
| 23 | Sat 14 Nov 22:52:34 | 22:55:18 | 14 Nov 15:52:34 | 2:43 | 0.7° | 28° NE / 45° NE / 62° NE | no |
| 24 | Sun 15 Nov 00:24:13 | 00:33:42 | 14 Nov 17:24:13 | 9:28 | **84.6°** | 323° NW / 53° NE / 142° SE | no |
| 25 | Sun 15 Nov 13:26:48 | 13:36:07 | 15 Nov 06:26:48 | 9:19 | **44.2°** | 207° SW / 126° SE / 45° NE | yes |
| 26 | Sun 15 Nov 15:03:31 | 15:09:07 | 15 Nov 08:03:31 | 5:35 | 3.7° | 277° W / 314° NW / 351° N | yes |
| 27 | Sun 15 Nov 23:08:43 | 23:16:41 | 15 Nov 16:08:43 | 7:58 | **11.2°** | 351° N / 49° NE / 107° E | no |
| 28 | Mon 16 Nov 00:43:07 | 00:51:37 | 15 Nov 17:43:07 | 8:30 | **15.8°** | 299° NW / 235° SW / 171° S | no |

## Loading the OEM in GMAT

```
Create Spacecraft KNACKSAT2;
GMAT KNACKSAT2.DateFormat = UTCGregorian;
GMAT KNACKSAT2.Epoch = '09 Nov 2026 00:10:00.000';
GMAT KNACKSAT2.EphemerisName = '<this folder>/KNACKSAT-2_2026-11-09.oem';
Create Propagator OEMProp;
GMAT OEMProp.Type = CCSDS-OEM;
GMAT OEMProp.StepSize = 60;
GMAT OEMProp.StartEpoch = 'FromSpacecraft';
BeginMissionSequence;
Propagate OEMProp(KNACKSAT2) {KNACKSAT2.ElapsedDays = 6.9583};
```

Put this folder's full path in place of `<this folder>`: GMAT reads a relative path from its own bin folder.

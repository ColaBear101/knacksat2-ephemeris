# KNACKSAT-2 ephemerides, 02 Nov 2026 00:00 UTC + 7 days

Made 2026-11-02T06:04:23Z by `make_ephemeris.py` (Skyfield SGP4). Elements from CelesTrak (gp.php?CATNR=67683), fetched 2026-11-02T06:04Z:

```
KNACKSAT-2
1 67683U 98067YA  26305.59236765  .00104975  00000+0  64115-3 0  9994
2 67683  51.6239 316.0163 0010026  22.7171 337.4271 15.76495325 41826
```

- TLE epoch **2026-11-01T14:13:01Z**: 0.41 days old at the start of the span, 7.41 at the end.
- At this height a TLE goes stale in days. One fitted to past tracking underestimates the drag to come (KNACKSAT-2's own TLEs in Sep-Oct 2026 ran 32 s late after 18 days), so passes late in the span are likely to come early. For the best times, make a fresh set with `python make_ephemeris.py`.
- Height above the WGS84 ellipsoid 330.2-361.2 km over the span (mean 344.4).
- Station: Bangkok ground station, 13.82378 N 100.51295 E, 60 m.
- AOS/LOS at 0 deg geometric elevation (no refraction), as the dashboard uses; 14 of 29 passes peak at 10 deg or more.
- Azimuth from true north through east. Range rate positive when receding.
- Doppler: `uhf_rx` is what reaches the station from 400.630 MHz; `vhf_tx` is what to send so the digipeater hears 145.825 MHz.
- GCRF is Skyfield's GCRS. The OEM is the same states in EME2000 (J2000 mean equator), rotated by the IERS frame bias, which moves a point here by under a metre.
- `sunlit` is 1 when the Sun is not behind the Earth (DE421 Sun, spherical Earth, no penumbra).

| File | What |
|---|---|
| `passes.csv` | 29 passes: AOS/TCA/LOS in UTC and ICT, azimuths, peak elevation |
| `pass_tracks.csv` | 13577 rows, every 1 s of every pass: az/el, range, range rate, Doppler |
| `geocentric.csv` | 10081 rows, every 60 s: lat/lon/alt and GCRF position/velocity |
| `KNACKSAT-2_2026-11-02.oem` | CCSDS OEM 1.0, EME2000, UTC, the same 10081 states |
| `tle.txt` | the elements above |

## Passes over the station

Times are rounded to the second. ICT = UTC+7. Peaks of 10° or more are in bold. Sun: sunlit for all, none or part of the pass.

| # | AOS (ICT) | LOS (ICT) | AOS (UTC) | Dur | Peak | Azimuth AOS / peak / LOS | Sun |
|---:|---|---|---|---:|---:|---|---|
| 1 | Mon 02 Nov 07:02:00 | 07:07:19 | 02 Nov 00:02:00 | 5:18 | 3.2° | 270° W / 237° SW / 203° SW | yes |
| 2 | Mon 02 Nov 18:29:45 | 18:38:55 | 02 Nov 11:29:45 | 9:09 | **27.2°** | 199° S / 125° SE / 51° NE | part |
| 3 | Mon 02 Nov 20:05:51 | 20:12:50 | 02 Nov 13:05:51 | 6:59 | 6.8° | 265° W / 312° NW / 0° N | part |
| 4 | Tue 03 Nov 04:13:12 | 04:20:46 | 02 Nov 21:13:12 | 7:34 | 8.5° | 356° N / 48° NE / 100° E | part |
| 5 | Tue 03 Nov 05:47:21 | 05:56:33 | 02 Nov 22:47:21 | 9:12 | **23.7°** | 306° NW / 235° SW / 163° S | part |
| 6 | Tue 03 Nov 17:18:43 | 17:24:23 | 03 Nov 10:18:43 | 5:40 | 3.9° | 161° S / 124° SE / 87° E | yes |
| 7 | Tue 03 Nov 18:51:36 | 19:00:57 | 03 Nov 11:51:36 | 9:21 | **36.4°** | 229° SW / 308° NW / 27° NE | part |
| 8 | Wed 04 Nov 04:34:13 | 04:43:46 | 03 Nov 21:34:13 | 9:33 | **40.2°** | 332° NW / 52° NE / 132° SE | part |
| 9 | Wed 04 Nov 06:10:53 | 06:16:33 | 03 Nov 23:10:53 | 5:40 | 3.8° | 273° W / 236° SW / 200° S | part |
| 10 | Wed 04 Nov 17:38:41 | 17:47:44 | 04 Nov 10:38:41 | 9:03 | **24.5°** | 198° S / 125° SE / 53° NE | yes |
| 11 | Wed 04 Nov 19:14:34 | 19:21:46 | 04 Nov 12:14:34 | 7:12 | 7.5° | 263° W / 312° NW / 2° N | part |
| 12 | Thu 05 Nov 03:22:01 | 03:29:19 | 04 Nov 20:22:01 | 7:17 | 7.5° | 358° N / 48° NE / 97° E | no |
| 13 | Thu 05 Nov 04:56:00 | 05:05:16 | 04 Nov 21:56:00 | 9:16 | **26.3°** | 308° NW / 235° SW / 161° S | part |
| 14 | Thu 05 Nov 16:27:28 | 16:32:38 | 05 Nov 09:27:28 | 5:10 | 3.1° | 157° SE / 124° SE / 90° E | yes |
| 15 | Thu 05 Nov 18:00:02 | 18:09:26 | 05 Nov 11:00:02 | 9:23 | **41.6°** | 227° SW / 308° NW / 29° NE | yes |
| 16 | Fri 06 Nov 03:42:34 | 03:52:01 | 05 Nov 20:42:34 | 9:27 | **35.0°** | 333° NW / 52° NE / 130° SE | part |
| 17 | Fri 06 Nov 05:18:57 | 05:25:03 | 05 Nov 22:18:57 | 6:05 | 4.5° | 276° W / 236° SW / 197° S | part |
| 18 | Fri 06 Nov 16:46:50 | 16:55:46 | 06 Nov 09:46:50 | 8:55 | **21.5°** | 195° S / 125° SE / 55° NE | yes |
| 19 | Fri 06 Nov 18:22:28 | 18:29:56 | 06 Nov 11:22:28 | 7:27 | 8.5° | 260° W / 312° NW / 4° N | yes |
| 20 | Sat 07 Nov 02:30:06 | 02:37:02 | 06 Nov 19:30:06 | 6:56 | 6.5° | 1° N / 47° NE / 94° E | no |
| 21 | Sat 07 Nov 04:03:52 | 04:13:12 | 06 Nov 21:03:52 | 9:20 | **30.1°** | 310° NW / 234° SW / 159° S | no |
| 22 | Sat 07 Nov 15:35:32 | 15:39:58 | 07 Nov 08:35:32 | 4:26 | 2.2° | 152° SE / 123° SE / 95° E | yes |
| 23 | Sat 07 Nov 17:07:41 | 17:17:07 | 07 Nov 10:07:41 | 9:26 | **49.7°** | 225° SW / 308° NW / 31° NE | yes |
| 24 | Sun 08 Nov 02:50:07 | 02:59:27 | 07 Nov 19:50:07 | 9:20 | **29.7°** | 335° NW / 51° NE / 127° SE | no |
| 25 | Sun 08 Nov 04:26:13 | 04:32:46 | 07 Nov 21:26:13 | 6:33 | 5.6° | 279° W / 236° SW / 193° S | no |
| 26 | Sun 08 Nov 15:54:13 | 16:02:58 | 08 Nov 08:54:13 | 8:44 | **18.4°** | 192° S / 125° SE / 58° NE | yes |
| 27 | Sun 08 Nov 17:29:34 | 17:37:19 | 08 Nov 10:29:34 | 7:45 | 9.9° | 256° W / 311° NW / 7° N | yes |
| 28 | Mon 09 Nov 01:37:26 | 01:43:53 | 08 Nov 18:37:26 | 6:27 | 5.3° | 4° N / 47° NE / 90° E | no |
| 29 | Mon 09 Nov 03:10:55 | 03:20:20 | 08 Nov 20:10:55 | 9:25 | **36.0°** | 312° NW / 234° SW / 156° SE | no |

## Loading the OEM in GMAT

```
Create Spacecraft KNACKSAT2;
GMAT KNACKSAT2.DateFormat = UTCGregorian;
GMAT KNACKSAT2.Epoch = '02 Nov 2026 00:10:00.000';
GMAT KNACKSAT2.EphemerisName = '<this folder>/KNACKSAT-2_2026-11-02.oem';
Create Propagator OEMProp;
GMAT OEMProp.Type = CCSDS-OEM;
GMAT OEMProp.StepSize = 60;
GMAT OEMProp.StartEpoch = 'FromSpacecraft';
BeginMissionSequence;
Propagate OEMProp(KNACKSAT2) {KNACKSAT2.ElapsedDays = 6.9583};
```

Put this folder's full path in place of `<this folder>`: GMAT reads a relative path from its own bin folder.

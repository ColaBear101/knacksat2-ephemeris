# KNACKSAT-2 ephemerides, 29 Oct 2026 04:41 UTC + 7 days

Made 2026-10-29T05:05:37Z by `make_ephemeris.py` (Skyfield SGP4). Elements from CelesTrak (gp.php?CATNR=67683), fetched 2026-10-29T04:31Z:

```
KNACKSAT-2
1 67683U 98067YA  26301.34419441  .00073665  00000+0  46828-3 0  9999
2 67683  51.6232 337.9052 0010016   3.8937 356.2139 15.75727961 41158
```

- TLE epoch **2026-10-28T08:15:38Z**: 0.85 days old at the start of the span, 7.85 at the end.
- At this height a TLE goes stale in days. One fitted to past tracking underestimates the drag to come (KNACKSAT-2's own TLEs in Sep-Oct 2026 ran 32 s late after 18 days), so passes late in the span are likely to come early. Make a new set every day or two: `python D:/Claude/knacksat2-ephemeris/make_ephemeris.py`.
- Height above the WGS84 ellipsoid 332.9-361.5 km over the span (mean 347.1).
- Station: Bangkok ground station, 13.82378 N 100.51295 E, 60 m.
- AOS/LOS at 0 deg geometric elevation (no refraction), as the dashboard uses; 14 of 28 passes peak at 10 deg or more.
- Azimuth from true north through east. Range rate positive when receding.
- Doppler: `uhf_rx` is what reaches the station from 400.630 MHz; `vhf_tx` is what to send so the digipeater hears 145.825 MHz.
- GCRF is Skyfield's GCRS. The OEM is the same states in EME2000 (J2000 mean equator), rotated by the IERS frame bias, which moves a point here by under a metre.
- `sunlit` is 1 when the Sun is not behind the Earth (DE421 Sun, spherical Earth, no penumbra).

| File | What |
|---|---|
| `passes.csv` | 28 passes: AOS/TCA/LOS in UTC and ICT, azimuths, peak elevation |
| `pass_tracks.csv` | 13373 rows, every 1 s of every pass: az/el, range, range rate, Doppler |
| `geocentric.csv` | 10081 rows, every 60 s: lat/lon/alt and GCRF position/velocity |
| `KNACKSAT-2_2026-10-29.oem` | CCSDS OEM 1.0, EME2000, UTC, the same 10081 states |
| `tle.txt` | the elements above |

## Passes over the station

Times are rounded to the second. ICT = UTC+7. Peaks of 10° or more are in bold. Sun: sunlit for all, none or part of the pass.

| # | AOS (ICT) | LOS (ICT) | AOS (UTC) | Dur | Peak | Azimuth AOS / peak / LOS | Sun |
|---:|---|---|---|---:|---:|---|---|
| 1 | Thu 29 Oct 20:09:41 | 20:18:58 | 29 Oct 13:09:41 | 9:17 | **31.3°** | 202° S / 126° SE / 50° NE | no |
| 2 | Thu 29 Oct 21:46:02 | 21:52:46 | 29 Oct 14:46:02 | 6:44 | 6.0° | 268° W / 313° NW / 358° N | no |
| 3 | Fri 30 Oct 05:53:21 | 06:01:15 | 29 Oct 22:53:21 | 7:54 | 9.8° | 354° N / 48° NE / 103° E | yes |
| 4 | Fri 30 Oct 07:27:44 | 07:36:52 | 30 Oct 00:27:44 | 9:07 | **21.0°** | 304° NW / 235° SW / 166° S | yes |
| 5 | Fri 30 Oct 18:59:07 | 19:05:23 | 30 Oct 11:59:07 | 6:15 | 5.0° | 165° S / 124° SE / 82° E | part |
| 6 | Fri 30 Oct 20:32:24 | 20:41:42 | 30 Oct 13:32:24 | 9:18 | **31.1°** | 232° SW / 309° NW / 25° NE | no |
| 7 | Sat 31 Oct 06:15:16 | 06:24:56 | 30 Oct 23:15:16 | 9:40 | **49.2°** | 329° NW / 52° NE / 135° SE | yes |
| 8 | Sat 31 Oct 07:52:21 | 07:57:23 | 31 Oct 00:52:21 | 5:01 | 2.8° | 268° W / 237° SW / 205° SW | yes |
| 9 | Sat 31 Oct 19:20:08 | 19:29:22 | 31 Oct 12:20:08 | 9:14 | **29.7°** | 201° S / 125° SE / 50° NE | part |
| 10 | Sat 31 Oct 20:56:23 | 21:03:13 | 31 Oct 13:56:23 | 6:50 | 6.3° | 267° W / 313° NW / 359° N | no |
| 11 | Sun 01 Nov 05:03:43 | 05:11:30 | 31 Oct 22:03:43 | 7:47 | 9.3° | 355° N / 48° NE / 102° E | part |
| 12 | Sun 01 Nov 06:38:01 | 06:47:10 | 31 Oct 23:38:01 | 9:09 | **22.0°** | 305° NW / 235° SW / 165° S | yes |
| 13 | Sun 01 Nov 18:09:24 | 18:15:26 | 01 Nov 11:09:24 | 6:02 | 4.6° | 163° S / 124° SE / 84° E | part |
| 14 | Sun 01 Nov 19:42:32 | 19:51:51 | 01 Nov 12:42:32 | 9:19 | **32.9°** | 231° SW / 308° NW / 26° NE | part |
| 15 | Mon 02 Nov 05:25:18 | 05:34:57 | 01 Nov 22:25:18 | 9:38 | **45.6°** | 330° NW / 52° NE / 134° SE | part |
| 16 | Mon 02 Nov 07:02:14 | 07:07:31 | 02 Nov 00:02:14 | 5:17 | 3.1° | 270° W / 237° SW / 203° SW | yes |
| 17 | Mon 02 Nov 18:30:03 | 18:39:13 | 02 Nov 11:30:03 | 9:10 | **27.6°** | 200° S / 125° SE / 51° NE | part |
| 18 | Mon 02 Nov 20:06:10 | 20:13:08 | 02 Nov 13:06:10 | 6:58 | 6.7° | 265° W / 313° NW / 360° N | part |
| 19 | Tue 03 Nov 04:13:33 | 04:21:10 | 02 Nov 21:13:33 | 7:36 | 8.6° | 356° N / 48° NE / 100° E | part |
| 20 | Tue 03 Nov 05:47:44 | 05:56:56 | 02 Nov 22:47:44 | 9:11 | **23.4°** | 306° NW / 235° SW / 164° S | part |
| 21 | Tue 03 Nov 17:19:09 | 17:24:55 | 03 Nov 10:19:09 | 5:45 | 4.0° | 161° S / 124° SE / 86° E | yes |
| 22 | Tue 03 Nov 18:52:06 | 19:01:27 | 03 Nov 11:52:06 | 9:21 | **35.7°** | 230° SW / 308° NW / 27° NE | part |
| 23 | Wed 04 Nov 04:34:48 | 04:44:23 | 03 Nov 21:34:48 | 9:34 | **41.4°** | 331° NW / 52° NE / 132° SE | part |
| 24 | Wed 04 Nov 06:11:32 | 06:17:08 | 03 Nov 23:11:32 | 5:36 | 3.6° | 272° W / 236° SW / 201° S | part |
| 25 | Wed 04 Nov 17:39:24 | 17:48:30 | 04 Nov 10:39:24 | 9:05 | **25.2°** | 198° S / 125° SE / 53° NE | yes |
| 26 | Wed 04 Nov 19:15:21 | 19:22:31 | 04 Nov 12:15:21 | 7:09 | 7.3° | 263° W / 312° NW / 1° N | part |
| 27 | Thu 05 Nov 03:22:51 | 03:30:14 | 04 Nov 20:22:51 | 7:23 | 7.8° | 358° N / 48° NE / 98° E | no |
| 28 | Thu 05 Nov 04:56:54 | 05:06:09 | 04 Nov 21:56:54 | 9:15 | **25.5°** | 307° NW / 235° SW / 162° S | part |

## Loading the OEM in GMAT

```
Create Spacecraft KNACKSAT2;
GMAT KNACKSAT2.DateFormat = UTCGregorian;
GMAT KNACKSAT2.Epoch = '29 Oct 2026 04:51:00.000';
GMAT KNACKSAT2.EphemerisName = 'D:/Claude/knacksat2-ephemeris/2026-10-29/KNACKSAT-2_2026-10-29.oem';
Create Propagator OEMProp;
GMAT OEMProp.Type = CCSDS-OEM;
GMAT OEMProp.StepSize = 60;
GMAT OEMProp.StartEpoch = 'FromSpacecraft';
BeginMissionSequence;
Propagate OEMProp(KNACKSAT2) {KNACKSAT2.ElapsedDays = 6.9583};
```

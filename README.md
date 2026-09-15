# TPBL 2025–26 data pipeline

Reproducible collection and validation of public Taiwan Professional Basketball
League statistics for player profiling, partner-fit research and later TPBL–KBL
comparisons. This repository supplies data and basic metrics; it does not perform
clustering, GMM modeling, Kanter fit analysis or lineup optimization.

The snapshot contains **7 teams, 140 players, 150 completed games, 4,059 player-game
roster entries and 300 team-game rows**. There are **3,318 positive-minute
appearances**. All records belong to 2025–26; phases are explicitly separated.
The data covers October 3, 2025 through June 6, 2026 (Taiwan local dates).

| Competition phase | Games |
| --- | ---: |
| Preseason | 7 |
| Regular season | 126 |
| Play-in | 2 |
| Playoffs | 8 |
| Finals | 7 |

| Target | API player ID | Regular-season GP | All-phase GP |
| --- | ---: | ---: | ---: |
| Chris McCullough / 麥卡洛 | 10860 | 24 | 28 |
| Lasannah Kromah / 克羅馬 | 68 | 30 | 35 |
| Cheick Diallo / 迪亞洛 | 10861 | 24 | 28 |
| Malcolm Miller / 米勒 | 16 | 30 | 36 |

Taoyuan Taiwan Beer Leopards (team ID **5**) have 36 regular-season games,
2 preseason games and 4 playoff games, totaling **42**.

## Sources and season definition

Entry points: [Leopards](https://t-leopards.com/), the four player profile pages
under `/team/{id}`, and [team statistics](https://t-leopards.com/stats/team).
The shared league frontend uses Nuxt, with server-rendered profile metadata and
JavaScript requests to the public [TPBL API](https://api.tpbl.basketball/api/seasons).

`/seasons` identifies **2025-2026 賽季** as season **2**, upstream GoHoops season
**213**. Frontend event ID is **2** (upstream event 490). Divisions are 8 preseason,
9 regular season, 11 play-in, 12 playoffs, and 35 finals. `/seasons/2/games` defines
membership. A mutable nested team object can point to the following season; it is
not used to select games. The supplied season end date is May 31, but its schedule
contains games through June 6, so no arbitrary cutoff truncates postseason data.

Team and player discovery is automatic through `/events/2/teams` and the union of
`/divisions/{id}/players` across all five phases. Placeholder teams are excluded
using `is_real_team`. Profiles enrich available English names and other missing
metadata. Game box scores `/games/{id}/stats` provide the primary player and team
totals. Separate player-game and Leopards team-game APIs independently validate
the target data. All observed collection endpoints return complete arrays/objects;
there is no pagination envelope. See [discovery notes](reports/scraping_notes.md).

## Install and run

Python 3.12+ recommended. From the repository directory:

```sh
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux instead: source .venv/bin/activate
python -m pip install -r requirements.txt
python run_pipeline.py
python -m pytest -q --basetemp=.cache/pytest
```

The first run fetches the public sources with a single worker, a minimum 1.25-second
request interval, timeouts and bounded exponential backoff. It checks robots.txt,
honors Retry-After seconds, and never retries authentication/access denials.
No account, API key, CAPTCHA or browser session is required.

Successful responses are cached atomically under `.cache/http`. A failed page is
recorded and collection continues. Rerun to retry failed responses; valid responses
are reused. Missing core discovery data stops execution rather than creating
misleading empty tables. Failed validations or collections give a nonzero exit code.
Source consistency warnings remain visible even when the pipeline exits successfully.

```sh
python run_pipeline.py --offline   # Regenerate from an existing local cache
python run_pipeline.py --refresh   # Refresh the snapshot from the source
```

Offline mode needs a prior successful collection. The large cache is intentionally
not committed. Raw CSVs preserve the relevant original JSON and normalized outputs
are committed, so the delivered snapshot is usable without contacting the API.
`reports/source_manifest.json` records request URLs, retrieval timestamps, response
SHA-256 hashes, and dataset sizes/hashes. Refreshes can change results if the source
corrects historical statistics; do not expect a fresh scrape to be byte-identical.

## Output tables and safe joins

The following files exist in both `data/raw/` and `data/processed/`:

- `teams.csv`: one row per season team.
- `players.csv`: one row per season player; raw JSON retains all roster versions.
- `games.csv`: one row per official game ID.
- `player_game_logs.csv`: one row per `(game_id, player_id)`, including roster entries
  with no statistics. `participation_status` and `appearance` distinguish them.
- `team_game_logs.csv`: one row per `(game_id, team_id)`.
- `roster_memberships.csv`: one row per source division/team/player roster membership.

Additional processed outputs:

- `mccullough_2025_26_game_logs.csv`: all canonical player-game columns for stable
  player ID 10860 and season 2025–26, enriched with validated team context.
- `mccullough_2025_26_profile.csv`: one explicitly labeled all-phase season summary.
  Shooting and style ratios use season totals, not means of game percentages.
  Team ratings are unweighted means over matched positive-minute games; rating
  availability counts are included. Games played means positive recorded minutes.

These two McCullough files are **automatically regenerated by `python run_pipeline.py`**
after canonical processing. They are never maintained independently. Canonical
`player_game_logs.csv`, `team_game_logs.csv`, and `games.csv` remain the source of
truth. A team-context match requires unique official `(game_id, team_id)` plus a
unique schedule row, agreeing on season, date, opponent, side and scores. Missing
or inconsistent matches are `unmatched`; duplicate candidates are `ambiguous`.
The player row remains, with all team context null and a diagnostic reason.
Canonical duplicate McCullough game IDs fail generation rather than being silently
deduplicated. See `reports/mccullough_validation.json` for join and totals checks.
No pairing or shared-minutes metrics are added.

- `target_players_2025_26.csv`: the four target players, all phases, same player-game
  grain (128 roster entries; 127 positive-minute appearances).
- `tpbl_2025_26_analysis_ready.csv`: player-game rows joined many-to-one to team-game
  context, with a checked join cardinality. Team columns repeat for teammates and
  must not be summed across player rows.
- `substitution_events.csv`: original rotation events, not computed pairings.

Filter `competition_phase == 'regular_season'` for regular-season research and
`appearance == True` for positive-minute games played. Do not pool preseason and
postseason implicitly. The original Chinese name, supplied English name and a
normalized NFKC/casefold name are separate fields. IDs are semantically strings;
load with `dtype={'player_id': str, 'game_id': str, 'team_id': str}` as needed.
The notebook [quick_data_check.ipynb](notebooks/quick_data_check.ipynb) demonstrates
safe use of these files.

Home/away derives from official schedule team IDs, not the player's displayed
vs/@ glyph (which was reversed in an inspected row). Repeated matchups and changed
dates remain distinct through official game IDs. No date/name composite key is used.

## Derived metrics

| Variable | Formula |
| --- | --- |
| `minutes` | source seconds / 60 |
| `FG_pct`, `two_P_pct`, `three_P_pct`, `FT_pct` | made / attempted |
| `eFG_pct` | (FGM + 0.5 × three_PM) / FGA |
| `TS_pct` | points / (2 × (FGA + 0.44 × FTA)) |
| `three_PA_rate` | three_PA / FGA |
| `FT_rate` | FTA / FGA |
| `AST_TOV` | AST / TOV |
| `possessions_est` | FGA − OREB + TOV + 0.44 × FTA |
| `ORtg` | 100 × team_points / possessions_est |
| `DRtg` | 100 × opponent_points / opponent_possessions_est |
| `Net_Rating` | ORtg − DRtg |

Ratios are fractions, not percentage points. Undefined denominators yield NA,
never zero. The original displayed percentages are retained as `source_*_pct`.
Other useful source statistics (shot types, paint/transition scoring, turnover and
foul types) are retained under `source_` prefixes, with original JSON in raw CSVs.
Team ratings use each side's own box-score possession estimate. They are not exact
possession counts, pace-adjusted symmetric ratings, individual ratings or pair ratings.
See the complete [data dictionary](reports/data_dictionary.md).

## Validation and limitations

Automated validation covers duplicate keys, required IDs, season membership, malformed
dates, invalid minutes, negative/fractional counts, makes versus attempts, shooting
percentages, score arithmetic, team/opponent mappings, UTF-8 Chinese, join integrity
and individual plus/minus extraction. Tests include deliberately corrupted records.
All four targets are checked against separate player-game endpoints and Leopards
totals against the separate team-game endpoint. A browser cross-check reviewed five
games per target and six fields per game: **120 comparisons, all passing**.

Source warnings remain: **7 team-game plus/minus reconciliation discrepancies**
and **3 team-game minute-total discrepancies**. They are not corrected without
evidence. See the affected IDs and residuals in
[team_player_reconciliation.csv](reports/team_player_reconciliation.csv).
Team rebounds, turnovers and fouls can include team/bench credits; player sums need
not match those team totals. There are 729 roster entries without stat objects and
12 with exactly zero recorded seconds; several zero-second entries have a foul or
plus/minus. These are retained and classified, not silently discarded or imputed.

Some English names or identity fields may remain absent. Profiles are mutable
enrichment, not a season-specific registration authority. Collection completeness
is relative to the identified official schedule and roster/box-score APIs.
Profile enrichment failed after retries for player IDs **99 (盧冠良), 10885
(劉丞勳), and 14437 (弗利沙)**. Their roster metadata and game statistics are
included, but English names remain NA. All other 137 players have supplied English
names. These three optional enrichment exceptions are a separate warning rule;
there are no missing game box scores or substitution feeds. The final test suite
has **39 passing tests**; its saved output is in `reports/test_results.txt`.

### Pairing and substitution limitation

Historical `/games/{id}/broadcasts` provides timed substitutions: **29,806 rotation
events across 150 games**. This is more information than box scores alone, but
exact two-player shared minutes are not directly supplied or certified here.
The audit finds sequence anomalies in 12 games, and 3,302 of 3,330 recorded-stat
player entries reconcile with reconstructed rotation minutes within one second.
Further source repair/review is required before treating all feeds as exact lineups.
**No shared minutes, pairing possessions, pairing ORtg/DRtg/Net Rating or lineup
optimization is calculated.** Manual video tagging may be needed for discrepancies.
See [validation_report.md](reports/validation_report.md) and substitution audit CSVs.

## Repository layout

```text
data/{raw,processed}/       Committed UTF-8 CSV snapshots
reports/                   Coverage, validation, dictionary and provenance
notebooks/                 Quick reproducible data checks
src/client.py              Rate limit, cache, timeout, retry, robots
src/collect.py             Season/roster/profile/box-score discovery
src/normalize.py           Numeric/date/ID cleaning and metric formulas
src/transform.py           Raw preservation and analysis tables
src/validate.py            Automated data validation
src/rotations.py           Public substitution collector
src/rotation_audit.py      Substitution consistency checks
src/report.py              Generated reports
tests/                     Unit/integration tests and browser fixture
run_pipeline.py            End-to-end entry point
```

## Code license and source data

The MIT license applies **only to original code in this repository**. TPBL source
statistics, names, source responses and other provider content remain subject to
their original rights and terms. This repository does not claim ownership of or
relicense the underlying source data. The GitHub repository is private.

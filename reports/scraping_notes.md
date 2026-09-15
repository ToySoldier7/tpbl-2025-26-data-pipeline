# Source discovery

Inspected 2026-09-14: https://t-leopards.com/team/10860, /team/68, /team/10861,
/team/16 and /stats/team are entry points. Nuxt renders metadata in HTML and loads
statistics from public JSON at https://api.tpbl.basketball/api/ . The page's
JavaScript API service and browser-observed resource URLs agree. No credentials
are required. Initial urllib CDN request returned 403; ordinary requests and the
browser load the public resources successfully, without cookies or challenges.

## Season and identity

`GET /seasons`: 2025-2026 賽季 is ID **2**, upstream GoHoops season **213**.
The frontend current event is **2**, upstream event **490**. Do not use a player's
current nested team season to filter games: that mutable object can say 2026-27.
Filter by season schedule membership and division, checking game-scoped season
IDs wherever supplied. Source season end is May 31 but postseason can extend
beyond it; schedule membership is authoritative, not arbitrary date cutoffs.

`GET /events/2/divisions`: 8 preseason, 9 regular season, 11 play-in,
12 playoffs, 35 finals. Preserve division_id and competition_phase on every row;
never pool phases implicitly. Upstream division IDs are separate identifiers.

`GET /events/2/teams`: 7 real teams, API IDs 2–8. Exclude IDs 67 and 68
(`is_real_team=false`), which represent seeded placeholders. API ID 5 is Leopards.
UI navigation IDs differ from API IDs; use `internal_id` in the bundled team
metadata when mapping English names. Original Chinese names remain untouched.

## Public endpoints and grains

- `/divisions/{division_id}/players`: division roster array, including stable
  website player ID, upstream roster ID, team, original name, height, weight,
  birthday, position and sometimes English name. Union all season divisions;
  preserve roster membership as a separate table. Do not assume current rosters
  cover historical appearances; augment metadata from observed box scores.
- `/players/{id}`: profile metadata, useful for the four target English names.
  Retrieved for every discovered season player because roster English-name fields
  are often blank. Only missing roster metadata is enriched; profile season stats
  and current team membership are never added to season game tables.
- `/players/{id}/games/stats?division_id={id}`: player-game array; accumulated,
  average and percentage stat groups. `time_on_court` is seconds, not minutes.
- `/teams/{id}/games/stats?division_id={id}`: team-game array, including FGA,
  FTA, OREB, TOV and opponent scores. Used independently to check Leopards totals.
- `/seasons/2/games`: complete schedule array with official game ID, phase ID,
  home/away objects, score, status, venue and `gamed_at` (`YYYY-MM-DD HH:MM:SS`,
  local Taiwan time). This snapshot has 150 completed games; 126 regular season.
- `/games/{game_id}/stats`: both teams, `teams.total`, `players.total`, and
  quarter-level `rounds`. One request yields all player and team box-score totals.
  This is the primary league collector, avoiding hundreds of player-phase calls.
- `/games/{id}/broadcasts` and `/games/{id}/live-broadcasts` appear in frontend
  code. The historical broadcasts endpoint supplies quarter events including
  Rotation / Entering / Leaving, remaining milliseconds, event order and player
  and team IDs. Collected 29,806 rotation events from 150 games. The inspected
  live-broadcasts endpoint is empty for a completed game. Historical sequences
  have anomalies in 12 games and cannot be assumed to provide certified exact
  pair minutes across the season. See the substitution audit; no pairing metrics
  are produced. Raw full event responses are cached, normalized rotation events
  are committed, and full play-by-play scoring/shot exports are outside this scope.

Observed endpoints return whole arrays/objects, without pagination envelopes or
next-page links. Reject unexpected structures rather than silently taking page 1.
News pagination exists but is irrelevant. `/events` returns 404 and is not used.

## Joins and interpretation

Game IDs are official API IDs, not row numbers. Player grain is (game_id,player_id),
team grain is (game_id,team_id). Home/away comes from schedule objects. The player
page's vs/@ display appears reversed for the inspected May 2 game; do not infer
home status from that symbol. `won_score` means points scored even for the losing
team, and `lost_score` means opponent points; these names do not imply a win.
Box scores include `is_starting` and the actual individual `plus_minus`. Example:
McCullough game 1493 has +9, whereas team margin is -3.

## Responsible collection

Leopards robots.txt returned HTTP 200 with an empty body; API robots.txt returned
404. The collector checks API robots on each live run, honors disallow/crawl-delay,
uses one worker with at least 1.25 seconds between request starts, timeouts, bounded
exponential retries, no retries on access denials, and resumable local JSON cache.
Raw CSVs preserve full relevant source objects as JSON; large response caches are
excluded from git. No tokens, cookies, browser profiles or credentials are saved.

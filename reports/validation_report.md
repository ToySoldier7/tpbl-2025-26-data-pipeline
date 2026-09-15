# Validation report

Automated rules: 124; failures: 0;
warning rules: 3. Full results are in
[validation_checks.csv](validation_checks.csv). Source data is retained unchanged
where warnings are present. Duplicate IDs and player/game or team/game keys,
season membership, numeric/date parsing, UTF-8 Chinese, shot arithmetic, score
reconciliation, foreign keys and actual individual plus/minus are tested.

## Source discrepancies

| check | violations | status | details |
| --- | --- | --- | --- |
| optional_profile_metadata_unavailable | 3 | WARN | [{'endpoint': 'players/99', 'error': 'HTTPError', 'optional_enrichment': True}, {'endpoint': 'players/10885', 'error': 'HTTPError', 'optional_enrichment': True}, {'endpoint': 'players/14437', 'error': 'HTTPError', 'optional_enrichment': True}] |
| sum_plus_minus_equals_five_times_margin | 7 | WARN | Source audit; no replacement of individual plus/minus |
| sum_player_minutes | 3 | WARN | Tolerance 10 seconds per team; source timing precision |


[team_player_reconciliation.csv](team_player_reconciliation.csv) identifies the
affected games and residuals. Team rebounds, turnovers and fouls may include team
or bench credits; those differences are recorded rather than forced to match.
Warnings make these data unsuitable for assuming perfect lineup consistency.

## Independent endpoint checks

All four players' game logs were compared to game box scores across all season
divisions, including seconds, individual +/- and all principal counting stats.
Leopards team box scores were compared to the separate team-game endpoint.
See the corresponding rows of validation_checks.csv for comparison counts.

## Browser cross-checks

Manually inspected the rendered regular-season game-log table on each of the four
supplied player pages. Five distinct games per player; six variables each;
120 comparisons, 0 failures. The fixture
is a transcription of rendered values, not generated from the pipeline data.
For game 1493, McCullough has +9 versus a team margin of -3; this explicitly
demonstrates that the individual statistic was not replaced by team margin.
The vs/@ glyph is not used to determine home/away: official schedule objects are.

| player | game | variable | source_value | collected_value | result | notes |
| --- | --- | --- | --- | --- | --- | --- |
| McCullough | 1493 | minutes_display | 34:16 | 34:16 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1493 | points | 21 | 21.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1493 | FGA | 15 | 15.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1493 | REB | 18 | 18.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1493 | AST | 3 | 3.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1493 | plus_minus | 9 | 9.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1503 | minutes_display | 25:33 | 25:33 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1503 | points | 12 | 12.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1503 | FGA | 12 | 12.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1503 | REB | 11 | 11.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1503 | AST | 1 | 1.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1503 | plus_minus | 1 | 1.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1480 | minutes_display | 21:50 | 21:50 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1480 | points | 15 | 15.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1480 | FGA | 17 | 17.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1480 | REB | 18 | 18.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1480 | AST | 0 | 0.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1480 | plus_minus | -3 | -3.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1477 | minutes_display | 30:02 | 30:02 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1477 | points | 22 | 22.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1477 | FGA | 16 | 16.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1477 | REB | 10 | 10.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1477 | AST | 1 | 1.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1477 | plus_minus | 18 | 18.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1461 | minutes_display | 28:17 | 28:17 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1461 | points | 10 | 10.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1461 | FGA | 12 | 12.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1461 | REB | 6 | 6.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1461 | AST | 2 | 2.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| McCullough | 1461 | plus_minus | -22 | -22.0 | PASS | Rendered https://t-leopards.com/team/10860; regular season; reviewed 2026-09-14 |
| Kromah | 1489 | minutes_display | 38:27 | 38:27 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1489 | points | 35 | 35.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1489 | FGA | 20 | 20.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1489 | REB | 4 | 4.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1489 | AST | 3 | 3.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1489 | plus_minus | -2 | -2.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1484 | minutes_display | 39:38 | 39:38 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1484 | points | 20 | 20.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1484 | FGA | 19 | 19.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1484 | REB | 8 | 8.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1484 | AST | 7 | 7.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1484 | plus_minus | -6 | -6.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1480 | minutes_display | 37:41 | 37:41 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1480 | points | 16 | 16.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1480 | FGA | 18 | 18.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1480 | REB | 11 | 11.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1480 | AST | 6 | 6.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1480 | plus_minus | 4 | 4.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1477 | minutes_display | 34:57 | 34:57 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1477 | points | 26 | 26.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1477 | FGA | 23 | 23.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1477 | REB | 7 | 7.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1477 | AST | 7 | 7.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1477 | plus_minus | 2 | 2.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1475 | minutes_display | 29:54 | 29:54 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1475 | points | 21 | 21.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1475 | FGA | 13 | 13.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1475 | REB | 2 | 2.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1475 | AST | 6 | 6.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Kromah | 1475 | plus_minus | 23 | 23.0 | PASS | Rendered https://t-leopards.com/team/68; regular season; reviewed 2026-09-14 |
| Diallo | 1493 | minutes_display | 21:55 | 21:55 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1493 | points | 14 | 14.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1493 | FGA | 6 | 6.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1493 | REB | 9 | 9.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1493 | AST | 2 | 2.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1493 | plus_minus | -6 | -6.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1489 | minutes_display | 33:23 | 33:23 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1489 | points | 23 | 23.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1489 | FGA | 16 | 16.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1489 | REB | 11 | 11.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1489 | AST | 2 | 2.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1489 | plus_minus | 0 | 0.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1503 | minutes_display | 29:07 | 29:07 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1503 | points | 31 | 31.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1503 | FGA | 16 | 16.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1503 | REB | 18 | 18.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1503 | AST | 3 | 3.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1503 | plus_minus | 23 | 23.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1484 | minutes_display | 28:53 | 28:53 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1484 | points | 10 | 10.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1484 | FGA | 8 | 8.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1484 | REB | 7 | 7.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1484 | AST | 1 | 1.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1484 | plus_minus | -9 | -9.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1475 | minutes_display | 27:17 | 27:17 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1475 | points | 10 | 10.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1475 | FGA | 10 | 10.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1475 | REB | 15 | 15.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1475 | AST | 1 | 1.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Diallo | 1475 | plus_minus | 19 | 19.0 | PASS | Rendered https://t-leopards.com/team/10861; regular season; reviewed 2026-09-14 |
| Miller | 1493 | minutes_display | 39:49 | 39:49 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1493 | points | 24 | 24.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1493 | FGA | 17 | 17.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1493 | REB | 6 | 6.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1493 | AST | 3 | 3.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1493 | plus_minus | -9 | -9.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1489 | minutes_display | 24:10 | 24:10 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1489 | points | 12 | 12.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1489 | FGA | 9 | 9.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1489 | REB | 8 | 8.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1489 | AST | 1 | 1.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1489 | plus_minus | 10 | 10.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1503 | minutes_display | 41:45 | 41:45 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1503 | points | 29 | 29.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1503 | FGA | 24 | 24.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1503 | REB | 10 | 10.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1503 | AST | 1 | 1.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1503 | plus_minus | 6 | 6.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1484 | minutes_display | 27:29 | 27:29 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1484 | points | 11 | 11.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1484 | FGA | 5 | 5.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1484 | REB | 7 | 7.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1484 | AST | 2 | 2.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1484 | plus_minus | -13 | -13.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1480 | minutes_display | 36:29 | 36:29 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1480 | points | 28 | 28.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1480 | FGA | 16 | 16.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1480 | REB | 9 | 9.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1480 | AST | 2 | 2.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |
| Miller | 1480 | plus_minus | -7 | -7.0 | PASS | Rendered https://t-leopards.com/team/16; regular season; reviewed 2026-09-14 |

## Substitution availability audit

{
  "events": 29806,
  "games": 150,
  "sequence_issues": 70,
  "player_checks": 3330,
  "within_one_second": 3302,
  "games_with_sequence_issues": 12,
  "collection_failures": []
}

[substitution_minutes_audit.csv](substitution_minutes_audit.csv) compares individual
time reconstructed from rotation events against box-score seconds with a one-second
tolerance. [substitution_sequence_anomalies.csv](substitution_sequence_anomalies.csv)
records invalid state transitions and intervals without five active players.
Events are ordered by decreasing remaining clock and source event_order within ties.
Quarters are 12 minutes; overtime is 5 minutes. A failed audit is a source limitation,
not permission to fabricate substitutions or pairing minutes. No pairing metrics
are calculated in this project.

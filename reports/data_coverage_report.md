# Data coverage

Snapshot: 2026-09-14. Season 2025–26 (API season/event 2, upstream season 213).

- Teams: 7; distinct players discovered: 140.
- Completed games: 150; player-game roster entries: 4059;
  positive-minute appearances: 3318; team-game rows: 300.
- Date range (Taiwan local): 2025-10-03 through 2026-06-06.
- Leopards games across phases: 42.
- Failed collections: 3; see source manifest and validation checks.
- No-stats roster entries: 729;
  zero-recorded-minute entries: 12.
  These entries are preserved, not counted as positive-minute games played.

### Collection exceptions

| endpoint | error | optional_enrichment |
| --- | --- | --- |
| players/99 | HTTPError | True |
| players/10885 | HTTPError | True |
| players/14437 | HTTPError | True |


Optional profile failures retain division-roster metadata and all box-score data.
English names are unavailable for 3
players. Game and team collection has no failures in this snapshot.

## Competition phases

| competition_phase | games |
| --- | --- |
| finals | 7 |
| play_in | 2 |
| playoffs | 8 |
| preseason | 7 |
| regular_season | 126 |

## Target player summary

Games played means positive recorded time. Ratios use summed numerators and
denominators within the phase, not averages of game percentages. Missing/DNP
records are not added as zero-performance games.

| player | phase | games_played | total_minutes | PPG | RPG | APG | three_PA_rate | TS_pct | average_plus_minus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| McCullough | playoffs | 2 | 51.1833 | 24.0 | 8.0 | 1.0 | 0.4545 | 0.6417 | 4.0 |
| McCullough | preseason | 2 | 59.0333 | 20.5 | 9.5 | 1.0 | 0.1667 | 0.5535 | -6.0 |
| McCullough | regular_season | 24 | 682.45 | 15.875 | 10.625 | 1.5417 | 0.1587 | 0.5293 | 2.2083 |
| Diallo | playoffs | 2 | 41.25 | 14.0 | 4.0 | 0.0 | 0.0 | 0.647 | -3.0 |
| Diallo | preseason | 2 | 46.9167 | 10.0 | 9.0 | 0.5 | 0.0 | 0.495 | -7.5 |
| Diallo | regular_season | 24 | 670.95 | 19.0 | 11.625 | 1.4167 | 0.0033 | 0.6328 | 6.4167 |
| Miller | playoffs | 4 | 135.8333 | 21.25 | 7.5 | 3.0 | 0.34 | 0.6772 | 5.0 |
| Miller | preseason | 2 | 59.15 | 12.0 | 11.0 | 0.0 | 0.3478 | 0.4762 | -3.0 |
| Miller | regular_season | 30 | 964.6667 | 15.8667 | 8.9 | 2.0667 | 0.2853 | 0.577 | 2.3333 |
| Kromah | playoffs | 4 | 151.55 | 24.0 | 6.25 | 10.25 | 0.2237 | 0.5408 | 1.0 |
| Kromah | preseason | 1 | 22.8667 | 13.0 | 5.0 | 0.0 | 0.2 | 0.5527 | -30.0 |
| Kromah | regular_season | 30 | 1070.7333 | 24.1667 | 7.0 | 6.5 | 0.2193 | 0.55 | 3.1333 |

## Missingness

Full counts and rates for **every column in every processed dataset** are in
[missingness.csv](missingness.csv). Selected player-game missing fields:

| variable | missing_count | rows | missing_rate |
| --- | --- | --- | --- |
| points | 729 | 4059 | 0.1796 |
| FGM | 729 | 4059 | 0.1796 |
| FGA | 729 | 4059 | 0.1796 |
| two_PM | 729 | 4059 | 0.1796 |
| two_PA | 729 | 4059 | 0.1796 |
| three_PM | 729 | 4059 | 0.1796 |
| three_PA | 729 | 4059 | 0.1796 |
| FTM | 729 | 4059 | 0.1796 |
| FTA | 729 | 4059 | 0.1796 |
| OREB | 729 | 4059 | 0.1796 |
| DREB | 729 | 4059 | 0.1796 |
| REB | 729 | 4059 | 0.1796 |
| AST | 729 | 4059 | 0.1796 |
| STL | 729 | 4059 | 0.1796 |
| BLK | 729 | 4059 | 0.1796 |
| TOV | 729 | 4059 | 0.1796 |
| PF | 729 | 4059 | 0.1796 |
| plus_minus | 729 | 4059 | 0.1796 |
| FG_pct | 1085 | 4059 | 0.2673 |
| two_P_pct | 1454 | 4059 | 0.3582 |
| three_P_pct | 1416 | 4059 | 0.3489 |
| FT_pct | 2357 | 4059 | 0.5807 |
| source_FG_pct | 729 | 4059 | 0.1796 |
| source_two_P_pct | 729 | 4059 | 0.1796 |
| source_three_P_pct | 729 | 4059 | 0.1796 |
| source_FT_pct | 729 | 4059 | 0.1796 |
| minutes | 729 | 4059 | 0.1796 |
| time_on_court_seconds | 729 | 4059 | 0.1796 |
| source_field_goals_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_missed | 729 | 4059 | 0.1796 |
| source_three_pointers_missed | 729 | 4059 | 0.1796 |
| source_free_throws_missed | 729 | 4059 | 0.1796 |
| source_defensive_fouls | 729 | 4059 | 0.1796 |
| source_offensive_fouls | 729 | 4059 | 0.1796 |
| source_personal_fouls | 729 | 4059 | 0.1796 |
| source_points_in_paint | 729 | 4059 | 0.1796 |
| source_second_chance_points | 729 | 4059 | 0.1796 |
| source_fast_break_points | 729 | 4059 | 0.1796 |
| source_efficiency | 729 | 4059 | 0.1796 |
| source_efg | 729 | 4059 | 0.1796 |
| source_tsp | 729 | 4059 | 0.1796 |
| source_pir | 729 | 4059 | 0.1796 |
| source_field_goals_made_in_the_paint | 729 | 4059 | 0.1796 |
| source_field_goals_missed_in_the_paint | 729 | 4059 | 0.1796 |
| source_field_goals_attempted_in_the_paint | 729 | 4059 | 0.1796 |
| source_field_goals_made_on_fast_break | 729 | 4059 | 0.1796 |
| source_field_goals_missed_on_fast_break | 729 | 4059 | 0.1796 |
| source_field_goals_attempted_on_fast_break | 729 | 4059 | 0.1796 |
| source_field_goals_made_on_second_chance | 729 | 4059 | 0.1796 |
| source_field_goals_missed_on_second_chance | 729 | 4059 | 0.1796 |
| source_field_goals_attempted_on_second_chance | 729 | 4059 | 0.1796 |
| source_technical_fouls | 729 | 4059 | 0.1796 |
| source_unsportsmanlike_fouls | 729 | 4059 | 0.1796 |
| source_disqualifying_fouls | 729 | 4059 | 0.1796 |
| source_bad_pass_turnovers | 729 | 4059 | 0.1796 |
| source_ball_handling_turnovers | 729 | 4059 | 0.1796 |
| source_out_of_bounds_turnovers | 729 | 4059 | 0.1796 |
| source_travel_turnovers | 729 | 4059 | 0.1796 |
| source_three_seconds_turnovers | 729 | 4059 | 0.1796 |
| source_five_seconds_turnovers | 729 | 4059 | 0.1796 |
| source_back_court_turnovers | 729 | 4059 | 0.1796 |
| source_offensive_goal_tending_turnovers | 729 | 4059 | 0.1796 |
| source_double_dribble_turnovers | 729 | 4059 | 0.1796 |
| source_carry_turnovers | 729 | 4059 | 0.1796 |
| source_offensive_foul_turnovers | 729 | 4059 | 0.1796 |
| source_other_turnovers | 729 | 4059 | 0.1796 |
| source_points_off_turnovers | 729 | 4059 | 0.1796 |
| source_two_pointers_jump_shot_made | 729 | 4059 | 0.1796 |
| source_two_pointers_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_three_pointers_jump_shot_made | 729 | 4059 | 0.1796 |
| source_three_pointers_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_three_pointers_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_layup_made | 729 | 4059 | 0.1796 |
| source_two_pointers_layup_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_layup_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_driving_layup_made | 729 | 4059 | 0.1796 |
| source_two_pointers_driving_layup_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_driving_layup_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_dunk_made | 729 | 4059 | 0.1796 |
| source_two_pointers_dunk_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_dunk_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_putback_dunk_made | 729 | 4059 | 0.1796 |
| source_two_pointers_putback_dunk_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_putback_dunk_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_putback_tip_in_made | 729 | 4059 | 0.1796 |
| source_two_pointers_putback_tip_in_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_putback_tip_in_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_alley_oop_made | 729 | 4059 | 0.1796 |
| source_two_pointers_alley_oop_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_alley_oop_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_hook_shot_made | 729 | 4059 | 0.1796 |
| source_two_pointers_hook_shot_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_hook_shot_attempted | 729 | 4059 | 0.1796 |
| source_three_pointers_hook_shot_made | 729 | 4059 | 0.1796 |
| source_three_pointers_hook_shot_missed | 729 | 4059 | 0.1796 |
| source_three_pointers_hook_shot_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_floating_jump_shot_made | 729 | 4059 | 0.1796 |
| source_two_pointers_floating_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_floating_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_three_pointers_floating_jump_shot_made | 729 | 4059 | 0.1796 |
| source_three_pointers_floating_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_three_pointers_floating_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_fadeaway_jump_shot_made | 729 | 4059 | 0.1796 |
| source_two_pointers_fadeaway_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_fadeaway_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_three_pointers_fadeaway_jump_shot_made | 729 | 4059 | 0.1796 |
| source_three_pointers_fadeaway_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_three_pointers_fadeaway_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_turnaround_jump_shot_made | 729 | 4059 | 0.1796 |
| source_two_pointers_turnaround_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_turnaround_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_three_pointers_turnaround_jump_shot_made | 729 | 4059 | 0.1796 |
| source_three_pointers_turnaround_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_three_pointers_turnaround_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_step_back_jump_shot_made | 729 | 4059 | 0.1796 |
| source_two_pointers_step_back_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_step_back_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_three_pointers_step_back_jump_shot_made | 729 | 4059 | 0.1796 |
| source_three_pointers_step_back_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_three_pointers_step_back_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_two_pointers_pull_up_jump_shot_made | 729 | 4059 | 0.1796 |
| source_two_pointers_pull_up_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_two_pointers_pull_up_jump_shot_attempted | 729 | 4059 | 0.1796 |
| source_three_pointers_pull_up_jump_shot_made | 729 | 4059 | 0.1796 |
| source_three_pointers_pull_up_jump_shot_missed | 729 | 4059 | 0.1796 |
| source_three_pointers_pull_up_jump_shot_attempted | 729 | 4059 | 0.1796 |
| eFG_pct | 1085 | 4059 | 0.2673 |
| TS_pct | 1053 | 4059 | 0.2594 |
| three_PA_rate | 1085 | 4059 | 0.2673 |
| FT_rate | 1085 | 4059 | 0.2673 |
| AST_TOV | 1970 | 4059 | 0.4853 |
| player_name_english | 97 | 4059 | 0.0239 |


English names and nationality/identity metadata are absent for some players;
they are not guessed. DNP statistics and undefined ratios remain NA. A zero-second
entry can still have fouls or plus/minus (clock precision/source behavior); it is
explicitly flagged. Team metadata is season membership, not proof of current roster.

## Lineup data

Public historical broadcasts contain Entering/Leaving events, quarter, remaining
clock in milliseconds, team and stable player IDs. Collected 29806
rotation events from 150 games. Exact pairing totals are not
provided as a ready-made endpoint. Sequence/minute reconciliation is documented in
validation_report.md. No shared-minutes, pairing possessions or pairing ratings
have been invented or added. Further event correction/validation is needed before
using these feeds for exact lineup analysis.

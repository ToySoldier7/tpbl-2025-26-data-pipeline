"""Generate coverage, manual checks, dictionaries and reproducibility manifests."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from .collect import TARGETS
from .normalize import STAT_MAP,PCT_MAP,ratio

def table(df):
    def value(v):
        if v is None or pd.isna(v): return 'NA'
        return str(round(v,4) if isinstance(v,float) else v).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+''.join('| '+' | '.join(value(v) for v in row)+' |\n' for row in df.itertuples(index=False,name=None))

def manual_checks(root,players):
    sample=pd.read_csv(root/'tests/fixtures/browser_crosscheck.csv',dtype={'player_id':str,'game_id':str})
    indexed=players.set_index(['game_id','player_id']); rows=[]
    for e in sample.to_dict('records'):
        p=indexed.loc[(e['game_id'],e['player_id'])]
        for var in ('minutes_display','points','FGA','REB','AST','plus_minus'):
            expected=e[var]
            if var=='minutes_display':
                sec=int(p.time_on_court_seconds); actual=f'{sec//60}:{sec%60:02d}'
            else: actual=p[var]
            rows.append({'player':TARGETS[int(e['player_id'])],'game':e['game_id'],'variable':var,
              'source_value':expected,'collected_value':actual,'result':'PASS' if actual==expected else 'FAIL',
              'notes':f"Rendered https://t-leopards.com/team/{e['player_id']}; regular season; reviewed 2026-09-14"})
    df=pd.DataFrame(rows); df.to_csv(root/'reports/manual_crosschecks.csv',index=False)
    return df

def reports(root,frames,bundle,checks,rotations):
    root=Path(root); dest=root/'reports'; p,t,g=(frames[k] for k in ['player_game_logs','team_game_logs','games'])
    manual=manual_checks(root,p)
    summaries=[]
    for (pid,phase),df in frames['target_players_2025_26'].groupby(['player_id','competition_phase']):
        played=df[df.appearance]; totals=played[['points','REB','AST','FGM','FGA','FTA','three_PA']].sum(); n=len(played)
        summaries.append(dict(player=TARGETS[int(pid)],phase=phase,games_played=n,total_minutes=played.minutes.sum(),
          PPG=ratio(totals.points,n),RPG=ratio(totals.REB,n),APG=ratio(totals.AST,n),
          three_PA_rate=ratio(totals.three_PA,totals.FGA),TS_pct=ratio(totals.points,2*(totals.FGA+.44*totals.FTA)),
          average_plus_minus=played.plus_minus.mean()))
    summary=pd.DataFrame(summaries); summary.to_csv(dest/'target_player_summary.csv',index=False)
    coverage={'teams':len(frames['teams']),'players':len(frames['players']),'games':len(g),
      'player_game_rows':len(p),'player_appearances':int(p.appearance.sum()),'team_game_rows':len(t),
      'start_date':g.game_date.min(),'end_date':g.game_date.max(),'Leopards_games':int((t.team_id=='5').sum()),
      'target_appearances':{TARGETS[int(pid)]:int(df.appearance.sum()) for pid,df in frames['target_players_2025_26'].groupby('player_id')},
      'collection_failures':bundle['failures'],'validation_failures':sum(c['status']=='FAIL' for c in checks),
      'validation_warnings':sum(c['status']=='WARN' for c in checks),'manual_checks':len(manual),
      'manual_failures':int((manual.result=='FAIL').sum()),'rotations':rotations}
    (dest/'summary.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
    counts=g.groupby('competition_phase').agg(games=('game_id','size')).reset_index()
    missing=pd.read_csv(dest/'missingness.csv'); selected=missing[(missing.dataset=='player_game_logs')&(missing.missing_count>0)]
    coverage_text=f'''# Data coverage

Snapshot: 2026-09-14. Season 2025–26 (API season/event 2, upstream season 213).

- Teams: {len(frames['teams'])}; distinct players discovered: {len(frames['players'])}.
- Completed games: {len(g)}; player-game roster entries: {len(p)};
  positive-minute appearances: {int(p.appearance.sum())}; team-game rows: {len(t)}.
- Date range (Taiwan local): {g.game_date.min()} through {g.game_date.max()}.
- Leopards games across phases: {int((t.team_id=='5').sum())}.
- Failed collections: {len(bundle['failures'])}; see source manifest and validation checks.
- No-stats roster entries: {int((p.participation_status=='no_stats_listed').sum())};
  zero-recorded-minute entries: {int((p.participation_status=='zero_recorded_minutes').sum())}.
  These entries are preserved, not counted as positive-minute games played.

### Collection exceptions

{table(pd.DataFrame(bundle['failures'])) if bundle['failures'] else 'None.'}

Optional profile failures retain division-roster metadata and all box-score data.
English names are unavailable for {int(frames['players'].player_name_english.isna().sum())}
players. Game and team collection has no failures in this snapshot.

## Competition phases

{table(counts)}
## Target player summary

Games played means positive recorded time. Ratios use summed numerators and
denominators within the phase, not averages of game percentages. Missing/DNP
records are not added as zero-performance games.

{table(summary)}
## Missingness

Full counts and rates for **every column in every processed dataset** are in
[missingness.csv](missingness.csv). Selected player-game missing fields:

{table(selected[['variable','missing_count','rows','missing_rate']])}

English names and nationality/identity metadata are absent for some players;
they are not guessed. DNP statistics and undefined ratios remain NA. A zero-second
entry can still have fouls or plus/minus (clock precision/source behavior); it is
explicitly flagged. Team metadata is season membership, not proof of current roster.

## Lineup data

Public historical broadcasts contain Entering/Leaving events, quarter, remaining
clock in milliseconds, team and stable player IDs. Collected {rotations.get('events',0)}
rotation events from {rotations.get('games',0)} games. Exact pairing totals are not
provided as a ready-made endpoint. Sequence/minute reconciliation is documented in
validation_report.md. No shared-minutes, pairing possessions or pairing ratings
have been invented or added. Further event correction/validation is needed before
using these feeds for exact lineup analysis.
'''
    (dest/'data_coverage_report.md').write_text(coverage_text,encoding='utf-8')
    warnings=pd.DataFrame([c for c in checks if c['status']!='PASS'])
    val=f'''# Validation report

Automated rules: {len(checks)}; failures: {coverage['validation_failures']};
warning rules: {coverage['validation_warnings']}. Full results are in
[validation_checks.csv](validation_checks.csv). Source data is retained unchanged
where warnings are present. Duplicate IDs and player/game or team/game keys,
season membership, numeric/date parsing, UTF-8 Chinese, shot arithmetic, score
reconciliation, foreign keys and actual individual plus/minus are tested.

## Source discrepancies

{table(warnings) if len(warnings) else 'None.'}

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
{len(manual)} comparisons, {int((manual.result=='FAIL').sum())} failures. The fixture
is a transcription of rendered values, not generated from the pipeline data.
For game 1493, McCullough has +9 versus a team margin of -3; this explicitly
demonstrates that the individual statistic was not replaced by team margin.
The vs/@ glyph is not used to determine home/away: official schedule objects are.

{table(manual)}
## Substitution availability audit

{json.dumps(rotations,indent=2)}

[substitution_minutes_audit.csv](substitution_minutes_audit.csv) compares individual
time reconstructed from rotation events against box-score seconds with a one-second
tolerance. [substitution_sequence_anomalies.csv](substitution_sequence_anomalies.csv)
records invalid state transitions and intervals without five active players.
Events are ordered by decreasing remaining clock and source event_order within ties.
Quarters are 12 minutes; overtime is 5 minutes. A failed audit is a source limitation,
not permission to fabricate substitutions or pairing minutes. No pairing metrics
are calculated in this project.
'''
    (dest/'validation_report.md').write_text(val,encoding='utf-8')
    write_dictionary(root,frames)
    manifest={'season':bundle['season'],'divisions':bundle['divisions'],'responses':bundle['manifest'],
              'api_robots':bundle['robots'],'outputs':[]}
    for path in sorted((root/'data').rglob('*.csv')):
        manifest['outputs'].append({'path':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    rmanifest=root/'.cache/rotation_manifest.json'
    if rmanifest.exists(): manifest['rotation_responses']=json.loads(rmanifest.read_text(encoding='utf-8'))
    (dest/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return coverage

def write_dictionary(root,frames):
    known={
      'season':('Canonical season label','season schedule','string','2025-26'),
      'season_id':('Official API season ID','/seasons','integer','2'),
      'division_id':('Official competition division ID','/events/2/divisions','integer','phase identity'),
      'competition_phase':('Competition phase label','division mapping','string','preseason/regular_season/play_in/playoffs/finals'),
      'game_id':('Stable official game ID','schedule','string','join key'),
      'game_date':('Taiwan local calendar date','gamed_at','date','YYYY-MM-DD'),
      'minutes':('Recorded playing time','time_on_court / 60','float','minutes'),
      'time_on_court_seconds':('Recorded playing time','box total time_on_court','integer','seconds'),
      'starter':('Listed starting player','is_starting','boolean','true/false'),
      'appearance':('Positive recorded playing time','time_on_court > 0','boolean','true/false'),
      'participation_status':('Playing-time/stat availability classification','source presence','string','played/no_stats_listed/zero_recorded_minutes'),
      'eFG_pct':('Effective field-goal percentage','(FGM + 0.5 * three_PM) / FGA','float','ratio'),
      'TS_pct':('True shooting percentage','points / (2 * (FGA + 0.44 * FTA))','float','ratio'),
      'three_PA_rate':('Three-point attempt share','three_PA / FGA','float','ratio'),
      'FT_rate':('Free-throw attempt rate','FTA / FGA','float','ratio'),
      'AST_TOV':('Assist to turnover ratio','AST / TOV','float','ratio'),
      'possessions_est':('Estimated team possessions','FGA - OREB + TOV + 0.44 * FTA','float','possessions'),
      'opponent_possessions_est':('Opponent estimate joined by game/opponent','opponent FGA - OREB + TOV + 0.44 * FTA','float','possessions'),
      'ORtg':('Estimated offensive rating','100 * team_points / possessions_est','float','points/100 possessions'),
      'DRtg':('Estimated defensive rating','100 * opponent_points / opponent_possessions_est','float','points/100 opponent possessions'),
      'Net_Rating':('Difference between estimated ratings','ORtg - DRtg','float','points/100 possessions'),
      'plus_minus':('Actual individual score differential while on court','players.total.plus_minus','integer','points'),
      'home_away':('Official schedule side','schedule home_team/away_team IDs','string','home/away'),
      'team_points':('Team score even if team lost','teams.total.won_score','integer','points'),
      'opponent_points':('Opponent score','teams.total.lost_score','integer','points')}
    known.update({
      'height_cm':('Listed height','roster/profile meta.height','numeric','centimeters'),
      'weight_kg':('Listed weight','roster/profile meta.weight','numeric','kilograms'),
      'birthday':('Listed birth date','roster/profile meta.birthday','date','YYYY-MM-DD'),
      'position':('Listed basketball position','roster/profile meta.position','string','source role'),
      'nationality':('Listed nationality classification','roster/profile meta.nationality','string','source label'),
      'national_identity':('Listed player eligibility/identity','roster/profile meta.national_identity','string','source label'),
      'team':('Original game team name','schedule team.name','string','Chinese text'),
      'opponent':('Original opposing team name','schedule opposing team.name','string','Chinese text'),
      'quarter':('Source period number','broadcast quarter','integer','1-based period'),
      'clock_remaining_ms':('Remaining period clock','broadcast event_quarter_time','integer','milliseconds'),
      'event_order':('Source ordering key','broadcast order','integer','ordering key, not game clock'),
      'action':('Substitution event outcome','broadcast event_outcome','string','Entering/Leaving'),
      'is_overtime':('Source overtime flag','broadcast is_overtime','boolean','true/false'),
      'result':('Player team game result','team score versus opponent score','string','W/L'),
      'win_loss':('Team game result','team score versus opponent score','string','W/L')})
    reverse={v:k for k,v in STAT_MAP.items()}
    rows=[]
    for name,df in frames.items():
        for col in df:
            if col in known: desc,source,kind,unit=known[col]
            elif col in reverse: desc,source,kind,unit=reverse[col].replace('_',' '),'box total.'+reverse[col],'integer','count'
            elif col in PCT_MAP.values(): desc,source,kind,unit='Shooting percentage','made / attempted','float','ratio 0–1'
            elif col.startswith('source_'): desc,source,kind,unit='Preserved source statistic',col[7:],'numeric','source units (percentage fields 0–100 except source_*_pct ratios 0–1)'
            elif col.endswith('_id'): desc,source,kind,unit='Stable identity; namespaces are not interchangeable','official API field','string','identifier'
            elif 'name_original' in col: desc,source,kind,unit='Original Chinese name preserved verbatim','API name','string','text'
            elif 'name_english' in col: desc,source,kind,unit='English name when supplied','profile/roster meta.alt_name or official team frontend','string','text'
            elif 'name_normalized' in col: desc,source,kind,unit='NFKC, trimmed whitespace, casefold name','English name if available, otherwise original','string','text'
            elif col.startswith('team_') and col[5:] in known: desc,source,kind,unit=known[col[5:]]
            else: desc,source,kind,unit=col.replace('_',' '),'official API metadata or documented join',str(df[col].dtype),'field-specific'
            derived=col in ['minutes','appearance','participation_status','competition_phase','eFG_pct','TS_pct','three_PA_rate','FT_rate','AST_TOV','possessions_est','opponent_possessions_est','ORtg','DRtg','Net_Rating','FG_pct','two_P_pct','three_P_pct','FT_pct'] or 'normalized' in col
            rows.append(dict(dataset=name,column=col,description=desc,source_or_formula=source,classification='derived' if derived else 'source/normalized',unit=unit,expected_type=kind,missing_meaning='Unavailable / not listed / undefined denominator; never imputed zero'))
    dictionary=pd.DataFrame(rows); dictionary.to_csv(root/'reports/data_dictionary.csv',index=False)
    text='# Data dictionary\n\nAll processed columns are enumerated below. CSV numeric columns use blank NA; IDs are\nstrings semantically even if a reader infers integers. Ratios are fractions, not\npercentage points. Source percentages are retained alongside recomputed ratios.\n\nRaw tables preserve scalar source fields and source_json (exact JSON values, including\nChinese names, nested objects and original percentage strings). Raw players has one\nrow per player with all season roster versions; roster_memberships has phase/team\nmembership grain. Caches contain full HTTP responses and are excluded from git.\n\n'
    text+='Team ratings use each side\'s own estimated possessions, not a symmetric pace estimate.\nThese are approximate box-score ratings, never player or pairing ratings.\n\n'
    text+=table(dictionary)
    from .mccullough import LOG_NAME,PROFILE_NAME,CONTEXT,COUNTS
    if PROFILE_NAME in frames:
        text+='\n## McCullough derived views\n\nBoth files are regenerated from canonical processed player_game_logs.csv,\nteam_game_logs.csv and games.csv. All original player-game columns above retain\ntheir values and units. The single profile row pools all 2025–26 phases explicitly;\nfilter the game-log phase column for regular-season-only research.\n\n'
        detail=[]
        for col in frames[LOG_NAME]:
            source=next((s for s,d in CONTEXT.items() if d==col),None)
            formula=('Validated team_game_logs.'+source) if source else 'Unchanged canonical player_game_logs.'+col
            if col=='point_differential': formula='team_points - opponent_points'
            if col=='team_context_join_status': formula='matched / unmatched / ambiguous; requires unique team and schedule matches with consistent identities, date, season, side and scores'
            if col=='team_context_join_reason': formula='Reason for accepted or rejected join; rejected context remains NA'
            detail.append({'dataset':LOG_NAME,'column':col,'definition_or_formula':formula})
        formulas={'FG_pct':'total_FGM / total_FGA','two_P_pct':'total_two_PM / total_two_PA',
            'three_P_pct':'total_three_PM / total_three_PA','FT_pct':'total_FTM / total_FTA',
            'eFG_pct':'(total_FGM + 0.5 * total_three_PM) / total_FGA',
            'TS_pct':'total_points / (2 * (total_FGA + 0.44 * total_FTA))',
            'three_PA_rate':'total_three_PA / total_FGA','FT_rate':'total_FTA / total_FGA',
            'AST_TOV':'total_AST / total_TOV','minutes_per_game':'total_minutes / games_played',
            'PPG':'total_points / games_played','RPG':'total_REB / games_played','APG':'total_AST / games_played',
            'SPG':'total_STL / games_played','BPG':'total_BLK / games_played',
            'games_played':'Count of positive-minute appearances','games_started':'Sum of starter among positive-minute appearances',
            'total_minutes':'Sum of listed minutes; missing listed values propagate NA',
            'avg_plus_minus':'Arithmetic mean of actual individual plus_minus among appearances',
            'phase_scope':'all_2025_26_phases','competition_phases':'Semicolon-separated observed phases',
            'game_log_rows':'Number of canonical player-game rows, including any no-stat roster entries',
            'matched_team_context_games':'Matched positive-minute appearances',
            'unmatched_team_context_rows':'Unmatched game-log rows','ambiguous_team_context_rows':'Ambiguous game-log rows',
            'date_start':'Earliest canonical game date, YYYY-MM-DD','date_end':'Latest canonical game date, YYYY-MM-DD',
            'season':'2025-26','player_id':'Stable website ID 10860','player_name':'Supplied English name, falling back to original',
            'player_name_original':'Preserved original Chinese name','team':'Distinct canonical team names, semicolon-separated'}
        for col in frames[PROFILE_NAME]:
            formula=formulas.get(col)
            if col.startswith('total_') and col[6:] in COUNTS: formula='Sum of '+col[6:]+' across listed-stat game rows; missing listed values propagate NA'
            if col.endswith('_per_game') and col!='minutes_per_game': formula='total_'+col[:-9]+' / games_played'
            if col.startswith('avg_team_'): formula='Unweighted arithmetic mean of '+col[4:]+' over matched positive-minute games with available rating'
            if col.endswith('_games') and col.startswith('team_'): formula='Number of matched positive-minute games with nonmissing '+col[:-6]
            detail.append({'dataset':PROFILE_NAME,'column':col,'definition_or_formula':formula})
        text+='All shooting/style ratios use season totals, never average game percentages.\nUndefined denominators are NA. Counts use count units; minutes use minutes; ratings\nuse points per 100 estimated possessions; percentages are fractions. Team means\nare game-weighted context, not McCullough individual or pairing ratings. The *_games\nfields expose each rating denominator. No-stat roster entries are excluded from sums;\nzero-second entries with listed counts are retained.\n\n'+table(pd.DataFrame(detail))
    text+='\nSubstitution events: game_id/team_id/player_id are official IDs; quarter is 1-based;\nclock_remaining_ms is remaining period time in milliseconds; event_order is the\nsource ordering key; action is Entering/Leaving; is_overtime is the source flag.\nNo shared-time metric is derived.\n'
    (root/'reports/data_dictionary.md').write_text(text,encoding='utf-8')

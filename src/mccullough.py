"""Regenerate McCullough views exclusively from canonical processed CSVs."""
import json
from pathlib import Path
import pandas as pd

PLAYER_ID = '10860'
SEASON = '2025-26'
LOG_NAME = 'mccullough_2025_26_game_logs'
PROFILE_NAME = 'mccullough_2025_26_profile'
COUNTS = ['points','REB','AST','STL','BLK','TOV','PF','FGM','FGA','two_PM','two_PA',
          'three_PM','three_PA','FTM','FTA','OREB','DREB']
CONTEXT = {'team_points':'team_points','opponent_points':'opponent_points',
           'possessions_est':'estimated_possessions','ORtg':'team_ORtg',
           'DRtg':'team_DRtg','Net_Rating':'team_NetRtg',
           **{c:'team_'+c for c in ['FGA','FTA','OREB','TOV','REB','AST','STL','BLK']}}

def safe_ratio(a,b):
    return float(a/b) if pd.notna(a) and pd.notna(b) and b!=0 else None

def equal(a,b):
    return pd.notna(a) and pd.notna(b) and a==b

def build_logs(players,teams,games):
    logs=players.loc[(players.player_id.astype(str)==PLAYER_ID)&(players.season==SEASON)].copy()
    if logs.game_id.isna().any() or logs.duplicated('game_id').any():
        raise ValueError('Canonical McCullough rows have missing or duplicate game IDs')
    for dest in [*CONTEXT.values(),'point_differential']:
        if dest in logs: raise ValueError(f'Context column collision: {dest}')
        logs[dest]=float('nan')
    logs['team_context_join_status']='unmatched'
    logs['team_context_join_reason']='missing_team_or_schedule'
    tg={key:df for key,df in teams.groupby(['game_id','team_id'],dropna=False)}
    gg={key:df for key,df in games.groupby('game_id',dropna=False)}
    for idx,p in logs.iterrows():
        candidates=tg.get((p.game_id,p.team_id)); schedule=gg.get(p.game_id)
        if (candidates is not None and len(candidates)>1) or (schedule is not None and len(schedule)>1):
            logs.loc[idx,['team_context_join_status','team_context_join_reason']]=['ambiguous','duplicate_team_or_schedule_key']
            continue
        if candidates is None or schedule is None: continue
        t=candidates.iloc[0]; g=schedule.iloc[0]
        mismatches=[c for c in ['season','game_date','opponent_id','home_away'] if not equal(p[c],t[c])]
        mismatches += ['schedule_'+c for c in ['season','game_date'] if not equal(p[c],g[c])]
        if p.home_away not in ('home','away'):
            mismatches.append('invalid_home_away')
        else:
            side=p.home_away; other='away' if side=='home' else 'home'
            if not equal(p.team_id,g[side+'_team_id']) or not equal(p.opponent_id,g[other+'_team_id']):
                mismatches.append('schedule_team_opponent')
            if not equal(t.team_points,g[side+'_points']) or not equal(t.opponent_points,g[other+'_points']):
                mismatches.append('schedule_score')
        if mismatches:
            logs.loc[idx,'team_context_join_reason']='mismatch:'+','.join(mismatches)
            continue
        for src,dest in CONTEXT.items(): logs.loc[idx,dest]=t.get(src,float('nan'))
        logs.loc[idx,'point_differential']=t.team_points-t.opponent_points
        logs.loc[idx,['team_context_join_status','team_context_join_reason']]=['matched','validated_official_game_team_key']
    return logs.sort_values(['game_date','game_id'],kind='stable').reset_index(drop=True)

def build_profile(logs):
    if logs.empty: raise ValueError('No canonical 2025–26 McCullough records')
    played=logs[logs.appearance.eq(True)]
    listed=logs[logs.participation_status!='no_stats_listed']
    # Missing listed statistics propagate NA; absent-stat roster entries are not imputed.
    totals={c:listed[c].sum(min_count=max(1,len(listed))) for c in COUNTS}
    n=len(played)
    join=played[played.team_context_join_status=='matched']
    first=logs.iloc[0]
    profile=dict(season=SEASON,player_id=PLAYER_ID,
        player_name=first.player_name_english if pd.notna(first.player_name_english) else first.player_name_original,
        player_name_original=first.player_name_original,team='; '.join(sorted(logs.team.dropna().unique())),
        phase_scope='all_2025_26_phases',competition_phases='; '.join(sorted(logs.competition_phase.unique())),
        game_log_rows=len(logs),games_played=n,
        games_started=played.starter.sum(min_count=max(1,n)),
        total_minutes=listed.minutes.sum(min_count=max(1,len(listed))),
        date_start=logs.game_date.min(),date_end=logs.game_date.max(),
        avg_plus_minus=played.plus_minus.mean(),
        matched_team_context_games=len(join),
        unmatched_team_context_rows=int(logs.team_context_join_status.eq('unmatched').sum()),
        ambiguous_team_context_rows=int(logs.team_context_join_status.eq('ambiguous').sum()))
    profile.update({'total_'+c:v for c,v in totals.items()})
    profile['minutes_per_game']=safe_ratio(profile['total_minutes'],n)
    per_game={'points':'PPG','REB':'RPG','AST':'APG','STL':'SPG','BLK':'BPG',
              **{c:c+'_per_game' for c in ['TOV','PF','FGA','three_PA','FTA','OREB','DREB']}}
    profile.update({dest:safe_ratio(totals[src],n) for src,dest in per_game.items()})
    for made,att,dest in [('FGM','FGA','FG_pct'),('two_PM','two_PA','two_P_pct'),
        ('three_PM','three_PA','three_P_pct'),('FTM','FTA','FT_pct'),
        ('three_PA','FGA','three_PA_rate'),('FTA','FGA','FT_rate'),('AST','TOV','AST_TOV')]:
        profile[dest]=safe_ratio(totals[made],totals[att])
    profile['eFG_pct']=safe_ratio(totals['FGM']+.5*totals['three_PM'],totals['FGA'])
    profile['TS_pct']=safe_ratio(totals['points'],2*(totals['FGA']+.44*totals['FTA']))
    for col in ['team_ORtg','team_DRtg','team_NetRtg']:
        profile['avg_'+col]=join[col].mean()
        profile[col+'_games']=int(join[col].notna().sum())
    return pd.DataFrame([profile])

def generate(root):
    root=Path(root); dest=root/'data/processed'
    ids={k:str for k in ['player_id','game_id','team_id','opponent_id','home_team_id','away_team_id']}
    players,teams,games=[pd.read_csv(dest/f'{name}.csv',dtype=ids) for name in ['player_game_logs','team_game_logs','games']]
    logs=build_logs(players,teams,games); profile=build_profile(logs); checks=[]
    def check(name,ok): checks.append(dict(check='mccullough_'+name,violations=int(not ok),status='PASS' if ok else 'FAIL',details='Derived from canonical processed CSVs'))
    canonical=players[(players.player_id==PLAYER_ID)&(players.season==SEASON)].sort_values(['game_date','game_id']).reset_index(drop=True)
    check('canonical_values_preserved',logs[players.columns].equals(canonical))
    check('identity_season',logs.player_id.eq(PLAYER_ID).all() and logs.season.eq(SEASON).all())
    check('unique_games',not logs.game_id.duplicated().any())
    check('game_count',len(logs)==len(canonical))
    check('dates',pd.to_datetime(logs.game_date,format='%Y-%m-%d',errors='coerce').notna().all())
    check('numeric_types',all(pd.api.types.is_numeric_dtype(logs[c]) for c in COUNTS+['minutes','plus_minus']))
    check('original_text',logs.player_name_original.equals(canonical.player_name_original) and not logs.player_name_original.str.contains('\ufffd').any())
    check('shooting',all(not (logs[m]>logs[a]).any() for m,a in [('FGM','FGA'),('two_PM','two_PA'),('three_PM','three_PA'),('FTM','FTA')]))
    missing=logs.team_context_join_status!='matched'
    check('failed_joins_null',logs.loc[missing,[*CONTEXT.values(),'point_differential']].isna().all().all())
    matched=logs[~missing]
    reference=matched[['game_id','team_id']].merge(teams,on=['game_id','team_id'],validate='one_to_one')
    check('matched_context_values',all(matched[d].reset_index(drop=True).equals(reference[s].astype(float).reset_index(drop=True)) for s,d in CONTEXT.items()))
    for col in COUNTS:
        expected=logs[col].sum(min_count=1); actual=profile.iloc[0]['total_'+col]
        check('profile_total_'+col,bool(pd.isna(expected) and pd.isna(actual)) or equal(expected,actual))
    check('profile_minutes',abs(profile.iloc[0].total_minutes-logs.minutes.sum())<1e-8)
    for name,df in [(LOG_NAME,logs),(PROFILE_NAME,profile)]:
        df.to_csv(dest/f'{name}.csv',index=False,encoding='utf-8',lineterminator='\n')
    report={'checks':checks,'joins':logs.team_context_join_status.value_counts().to_dict(),
            'join_exceptions':logs.loc[missing,['game_id','team_context_join_status','team_context_join_reason']].to_dict('records'),
            'phase_scope':'All phases in the canonical 2025–26 dataset; no per-game percentage averaging.'}
    (root/'reports/mccullough_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return {LOG_NAME:logs,PROFILE_NAME:profile},checks

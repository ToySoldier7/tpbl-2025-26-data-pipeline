"""Validation results are evidence, never silently repaired source statistics."""
import json
import re
from pathlib import Path
import pandas as pd
from .normalize import STAT_MAP

def duplicate_count(frame,keys):
    return int(frame.duplicated(keys).sum())

def validate(frames,bundle,root,parse_issues):
    checks=[]; anomalies=[]
    def record(name,count,details='',severity='error'):
        checks.append(dict(check=name,violations=int(count),status='PASS' if count==0 else ('WARN' if severity=='warning' else 'FAIL'),details=details))
    def mask_check(name,df,mask,severity='error'):
        bad=df.loc[mask]
        record(name,len(bad),severity=severity)
        if len(bad):
            for row in bad.head(50).to_dict('records'):
                anomalies.append({'check':name,**{k:row.get(k) for k in ['game_id','team_id','player_id']}})
    p,t,g=map(frames.get,['player_game_logs','team_game_logs','games'])
    critical=[f for f in bundle['failures'] if not f.get('optional_enrichment')]
    optional=[f for f in bundle['failures'] if f.get('optional_enrichment')]
    record('collection_failures',len(critical),str(critical))
    record('optional_profile_metadata_unavailable',len(optional),str(optional),severity='warning')
    record('parse_issues',len(parse_issues),str(parse_issues))
    if 'games' in bundle:
        source_season_errors=sum(any(game[side].get('gohoops_season_id')!=213 for side in ['home_team','away_team']) for game in bundle['games'])
        record('source_schedule_upstream_season',source_season_errors,'Both schedule-side upstream season IDs must be 213')
    for name,keys in [('teams',['team_id']),('players',['player_id']),('games',['game_id']),
                      ('player_game_logs',['game_id','player_id']),('team_game_logs',['game_id','team_id'])]:
        df=frames[name]
        record(name+'_duplicate_keys',duplicate_count(df,keys))
        for key in keys: record(name+'_missing_'+key,int(df[key].isna().sum()))
        record(name+'_unexpected_season',int((df.season!='2025-26').sum()))
        record(name+'_replacement_characters',sum('\ufffd' in str(v) for v in df.astype(str).to_numpy().flat))
    for name,df in [('player',p),('team',t),('games',g)]:
        mask_check(name+'_malformed_dates',df,pd.to_datetime(df.game_date,format='%Y-%m-%d',errors='coerce').isna())
        if name=='games': continue
        if name=='player': df=df[df.participation_status!='no_stats_listed']
        for made,att in [('FGM','FGA'),('two_PM','two_PA'),('three_PM','three_PA'),('FTM','FTA')]:
            mask_check(name+'_'+made+'_exceeds_'+att,df,df[made]>df[att])
        counting=[c for c in ['FGM','FGA','two_PM','two_PA','three_PM','three_PA','FTM','FTA','OREB','DREB','REB','AST','STL','BLK','TOV','PF','points','team_points','opponent_points'] if c in df]
        mask_check(name+'_negative_counts',df,(df[counting]<0).any(axis=1))
        mask_check(name+'_fractional_counts',df,((df[counting]%1)!=0).any(axis=1))
        for c in ['FG_pct','two_P_pct','three_P_pct','FT_pct','source_FG_pct','source_two_P_pct','source_three_P_pct','source_FT_pct']:
            mask_check(name+'_'+c+'_range',df,df[c].notna()&~df[c].between(0,1))
        mask_check(name+'_shooting_components',df,(df.FGM!=df.two_PM+df.three_PM)|(df.FGA!=df.two_PA+df.three_PA))
        pts='points' if name=='player' else 'team_points'
        mask_check(name+'_scoring_identity',df,df[pts]!=2*df.two_PM+3*df.three_PM+df.FTM)
        mask_check(name+'_rebound_components',df,df.REB!=df.OREB+df.DREB)
        for made,att,pct in [('FGM','FGA','FG_pct'),('two_PM','two_PA','two_P_pct'),('three_PM','three_PA','three_P_pct'),('FTM','FTA','FT_pct')]:
            mask_check(name+'_'+pct+'_display_rounding',df,df[pct].notna()&((df[pct]-df['source_'+pct]).abs()>0.000501))
    limit=48+(p.periods-4).clip(lower=0)*5
    mask_check('player_invalid_minutes',p,(p.minutes.isna()&(p.participation_status!='no_stats_listed'))|(p.minutes<0)|(p.minutes>limit+1/60))
    record('individual_plus_minus_present_when_stats_listed',int((p.plus_minus.isna()&(p.participation_status!='no_stats_listed')).sum()))
    record('player_ids_known',int((~p.player_id.isin(frames['players'].player_id)).sum()))
    record('player_team_ids_known',int((~p.team_id.isin(frames['teams'].team_id)).sum()))
    record('Chinese_player_names_present',int((~frames['players'].player_name_original.str.contains(r'[\u3400-\u9fff]',regex=True)).sum()))
    gm=g.set_index('game_id'); tm=t.set_index(['game_id','team_id'])
    mismap=score=0
    for row in t.itertuples():
        game=gm.loc[row.game_id]
        home=row.home_away=='home'
        expected=(game.home_team_id,game.away_team_id) if home else (game.away_team_id,game.home_team_id)
        mismap+=(row.team_id,row.opponent_id)!=expected
        expected_score=(game.home_points,game.away_points) if home else (game.away_points,game.home_points)
        score+=(row.team_points,row.opponent_points)!=expected_score
    record('team_opponent_home_away_mapping',mismap)
    record('schedule_final_scores_match',score)
    record('two_team_rows_per_completed_game',int((t.groupby('game_id').size()!=2).sum())+len(set(g.loc[g.status=='COMPLETED','game_id'])-set(t.game_id)))
    joined=p.merge(t[['game_id','team_id','opponent_id','home_away']],on=['game_id','team_id'],how='left',suffixes=('','_team'),validate='many_to_one',indicator=True)
    record('player_team_join',int(((joined['_merge']!='both')|(joined.opponent_id!=joined.opponent_id_team)|(joined.home_away!=joined.home_away_team)).sum()))
    sums=p.groupby(['game_id','team_id'])[['points','FGM','FGA','two_PM','two_PA','three_PM','three_PA','FTM','FTA','AST','STL','BLK']].sum()
    for c in sums:
        source='team_points' if c=='points' else c
        record('player_sum_vs_team_'+c,int((sums[c]!=tm.loc[sums.index,source]).sum()))
    # Player rebound/turnover sums may omit team credits; retain differences as an audit.
    audit=p.groupby(['game_id','team_id'])[['OREB','DREB','REB','TOV','PF','time_on_court_seconds','plus_minus']].sum().join(t.set_index(['game_id','team_id'])[['OREB','DREB','REB','TOV','PF','team_points','opponent_points','periods']],rsuffix='_team')
    audit['plus_minus_residual']=audit.plus_minus-5*(audit.team_points-audit.opponent_points)
    audit['minutes_residual_seconds']=audit.time_on_court_seconds-5*(48+(audit.periods-4).clip(lower=0)*5)*60
    for c in ['OREB','DREB','REB','TOV','PF']: audit[c+'_team_credit_difference']=audit[c+'_team']-audit[c]
    dest=Path(root)/'reports'; dest.mkdir(exist_ok=True)
    audit.to_csv(dest/'team_player_reconciliation.csv',encoding='utf-8')
    record('sum_plus_minus_equals_five_times_margin',int((audit.plus_minus_residual!=0).sum()),'Source audit; no replacement of individual plus/minus',severity='warning')
    record('sum_player_minutes',int((audit.minutes_residual_seconds.abs()>10).sum()),'Tolerance 10 seconds per team; source timing precision',severity='warning')
    target_errors=[]; compared=0
    pi=p.set_index(['game_id','player_id'])
    for key,logs in bundle['target_logs'].items():
        pid,did=key.split(':')
        expected=set()
        for entry in logs or []:
            gid=str(entry['game']['id']); expected.add(gid)
            if (gid,pid) not in pi.index:
                target_errors.append((key,gid,'missing row')); continue
            actual=pi.loc[(gid,pid)]
            for src,col in {**STAT_MAP,'time_on_court':'time_on_court_seconds'}.items():
                compared+=1
                if actual[col]!=entry['accumulated_stats'].get(src): target_errors.append((key,gid,col))
            if entry['game'].get('gohoops_season_id')!=213: target_errors.append((key,gid,'season'))
        observed=set(p.loc[(p.player_id==pid)&(p.division_id==int(did))&p.appearance,'game_id'])
        if observed!=expected: target_errors.append((key,'coverage',f'{observed ^ expected}'))
    record('target_logs_independent_API_comparison',len(target_errors),f'{compared} values compared; {target_errors[:20]}')
    team_errors=[]; n=0
    for did,logs in bundle['team_checks'].items():
        for e in logs or []:
            gid=str(e['game']['id'])
            if (gid,'5') not in tm.index: team_errors.append((gid,'missing')); continue
            actual=tm.loc[(gid,'5')]
            for src,col in {**{k:v for k,v in STAT_MAP.items() if v not in ['points','plus_minus']},'won_score':'team_points','lost_score':'opponent_points'}.items():
                n+=1
                if actual[col]!=e['accumulated_stats'].get(src): team_errors.append((gid,col))
    record('Leopards_independent_team_log_comparison',len(team_errors),f'{n} values compared; {team_errors[:20]}')
    pd.DataFrame(checks).to_csv(dest/'validation_checks.csv',index=False)
    pd.DataFrame(anomalies,columns=['check','game_id','team_id','player_id']).to_csv(dest/'validation_anomalies.csv',index=False)
    missing=[]
    for name,df in frames.items():
        for col in df:
            missing.append({'dataset':name,'variable':col,'missing_count':int(df[col].isna().sum()),'rows':len(df),'missing_rate':float(df[col].isna().mean())})
    pd.DataFrame(missing).to_csv(dest/'missingness.csv',index=False)
    return checks

"""Check substitution sequences before claiming they support exact lineups."""
from collections import defaultdict
import pandas as pd

def audit_rotations(root,players):
    events=pd.read_csv(root/'data/processed/substitution_events.csv',dtype={'game_id':str,'team_id':str,'player_id':str})
    totals=defaultdict(float); anomalies=[]
    for (gid,tid,q),group in events.groupby(['game_id','team_id','quarter']):
        active={}; previous=720000 if q<=4 else 300000
        for clock in sorted(group.clock_remaining_ms.unique(),reverse=True):
            at=group[group.clock_remaining_ms==clock].sort_values('event_order')
            if clock>previous or clock<0: anomalies.append((gid,tid,q,'invalid_clock'))
            for pid in active: totals[(gid,tid,pid)]+=(previous-clock)/1000
            if previous>clock and len(active)!=5: anomalies.append((gid,tid,q,'not_five_active'))
            for e in at.itertuples():
                if e.action=='Entering':
                    if e.player_id in active: anomalies.append((gid,tid,q,'duplicate_enter'))
                    active[e.player_id]=True
                elif e.action=='Leaving':
                    if e.player_id not in active: anomalies.append((gid,tid,q,'leave_without_enter'))
                    active.pop(e.player_id,None)
                else: anomalies.append((gid,tid,q,'unknown_action'))
            previous=clock
        if previous>0:
            for pid in active: totals[(gid,tid,pid)]+=previous/1000
            if len(active)!=5: anomalies.append((gid,tid,q,'incomplete_period_end'))
    rows=[]
    for p in players.itertuples():
        if p.participation_status=='no_stats_listed': continue
        reconstructed=totals.get((p.game_id,p.team_id,p.player_id))
        residual=None if reconstructed is None else reconstructed-p.time_on_court_seconds
        rows.append({'game_id':p.game_id,'team_id':p.team_id,'player_id':p.player_id,
            'source_seconds':p.time_on_court_seconds,'rotation_seconds':reconstructed,
            'residual_seconds':residual,'within_one_second':residual is not None and abs(residual)<=1})
    df=pd.DataFrame(rows)
    df.to_csv(root/'reports/substitution_minutes_audit.csv',index=False)
    pd.DataFrame(anomalies,columns=['game_id','team_id','quarter','issue']).to_csv(root/'reports/substitution_sequence_anomalies.csv',index=False)
    return {'events':len(events),'games':events.game_id.nunique(),'sequence_issues':len(anomalies),
            'player_checks':len(df),'within_one_second':int(df.within_one_second.sum()),
            'games_with_sequence_issues':len({a[0] for a in anomalies})}

"""Normalize official game totals without losing the raw representation."""
import json
from pathlib import Path
import pandas as pd
from .normalize import identifier, date, normalized_name, stats, player_metrics, possessions, ratio
from .collect import TARGETS

PHASES={8:'preseason',9:'regular_season',11:'play_in',12:'playoffs',35:'finals'}
# English labels transcribed from official frontend team metadata; roster discovery is dynamic.
TEAM_EN={8:'Taipei Taishin Mars',7:'New Taipei Kings',6:'New Taipei CTBC DEA',
 5:'Taoyuan Taiwan Beer Leopards',4:'Hsinchu Toplus Lioneers',3:'Formosa Dreamers',2:'Kaohsiung Aquas'}

def as_rows(obj):
    if isinstance(obj,dict): return list(obj.values())
    if isinstance(obj,list): return obj
    raise ValueError('Unexpected totals structure')

def raw_row(payload,**keys):
    # Flat source stats plus exact JSON preserves all remaining fields and types.
    return {**keys,**{k:v for k,v in payload.items() if not isinstance(v,(dict,list))},
            'source_json':json.dumps(payload,ensure_ascii=False,separators=(',',':'))}

def transform(bundle,root):
    raw={k:[] for k in ('teams','players','games','player_game_logs','team_game_logs','roster_memberships')}
    out={k:[] for k in raw}
    issues=[]
    teams={t['id']:t for t in bundle['teams'] if t.get('is_real_team')}
    for tid,t in teams.items():
        raw['teams'].append(raw_row(t,season='2025-26',team_id=tid))
        out['teams'].append(dict(season='2025-26',team_id=identifier(tid),team_name_original=t['name'],
           team_name_english=TEAM_EN.get(tid),team_name_normalized=normalized_name(TEAM_EN.get(tid,t['name'])),
           gohoops_team_id=t['gohoops_id']))
    metadata={}
    for p in bundle['players']:
        pid=identifier(p['id']); tid=identifier(p['team']['id']); did=p['division_id']
        if p['team']['id'] not in teams: continue
        raw['players'].append(raw_row(p,season='2025-26',player_id=pid,team_id=tid))
        metadata.setdefault(pid,p)
        if not metadata[pid].get('meta',{}).get('alt_name') and p.get('meta',{}).get('alt_name'):
            metadata[pid]=p
        membership=dict(season='2025-26',division_id=did,competition_phase=PHASES[did],
          player_id=pid,team_id=tid,gohoops_roster_id=p.get('gohoops_roster_id'),
          registered=p.get('registered'),source='division_roster')
        out['roster_memberships'].append(membership)
        raw['roster_memberships'].append(raw_row(p,**membership))
    for pid,p in bundle['profiles'].items():
        if p:
            # Profile English name is enrichment only, never a season membership claim.
            metadata.setdefault(pid,p)
            enriched=dict(metadata[pid].get('meta',{}))
            for key,value in p.get('meta',{}).items():
                if not enriched.get(key) and value: enriched[key]=value
            metadata[pid]={**metadata[pid], 'meta':enriched}
    for g in bundle['games']:
        did=g['division_id']
        if did not in PHASES: raise ValueError('Unexpected season division')
        if g['home_team']['id'] not in teams or g['away_team']['id'] not in teams:
            issues.append({'game_id':g['id'],'reason':'placeholder team'}); continue
        gid=identifier(g['id']); h,a=g['home_team'],g['away_team']
        grow=dict(season='2025-26',season_id=2,division_id=did,competition_phase=PHASES[did],
          game_id=gid,gohoops_game_id=g['gohoops_id'],game_date=date(g['gamed_at']),
          game_datetime_local=g['gamed_at'],timezone='Asia/Taipei',home_team_id=identifier(h['id']),
          away_team_id=identifier(a['id']),home_team=h['name'],away_team=a['name'],
          home_points=h.get('won_score'),away_points=a.get('won_score'),status=g['status'],
          venue=g.get('venue'),periods=g.get('round'))
        raw['games'].append(raw_row(g,season='2025-26',game_id=gid))
        out['games'].append(grow)
        box=bundle['boxes'].get(gid)
        if not box:
            if g['status']=='COMPLETED': issues.append({'game_id':gid,'reason':'missing box score'})
            continue
        for side,other in [('home_team','away_team'),('away_team','home_team')]:
            b=box[side]; tid=identifier(b['id']); opp=g[other]
            if b['id']!=g[side]['id']: raise ValueError('Box/schedule side mismatch')
            context={k:grow[k] for k in ('season','season_id','division_id','competition_phase','game_id','game_date','periods')}
            context.update(team_id=tid,team=g[side]['name'],opponent_id=identifier(opp['id']),
                           opponent=opp['name'],home_away='home' if side=='home_team' else 'away',
                           source_url=f'https://api.tpbl.basketball/api/games/{gid}/stats')
            total=b['teams']['total']
            raw['team_game_logs'].append(raw_row(total,**context))
            trow={**context,**stats(total,team=True)}
            trow['win_loss']='W' if trow['team_points']>trow['opponent_points'] else 'L'
            trow['possessions_est']=possessions(trow)
            trow['ORtg']=ratio(100*trow['team_points'],trow['possessions_est'])
            out['team_game_logs'].append(trow)
            for p in as_rows(b['players']['total']):
                pid=identifier(p['id'])
                if pid not in metadata:
                    metadata[pid]={'id':p['id'],'name':p['name'],'gohoops_id':p.get('gohoops_id'),
                                   'meta':{'position':p.get('positions')},'metadata_source':'box_score'}
                raw['player_game_logs'].append(raw_row(p,**context,player_id=pid))
                row={**context, 'player_id':pid,'player_name_original':p['name'],
                     'gohoops_roster_id':p.get('gohoops_roster_id'),**stats(p)}
                row['result']=trow['win_loss']
                row['appearance']=row['time_on_court_seconds'] is not None and row['time_on_court_seconds']>0
                row['participation_status']='played' if row['appearance'] else ('no_stats_listed' if row['minutes'] is None else 'zero_recorded_minutes')
                row.update(player_metrics(row))
                out['player_game_logs'].append(row)
    for pid,p in metadata.items():
        m=p.get('meta',{})
        en=m.get('alt_name') or None
        out['players'].append(dict(season='2025-26',player_id=pid,player_name_original=p['name'],
          player_name_english=en,player_name_normalized=normalized_name(en or p['name']),
          gohoops_player_id=p.get('gohoops_id'),position=m.get('position'),height_cm=m.get('height'),
          weight_kg=m.get('weight'),birthday=m.get('birthday') or None,
          nationality=m.get('nationality') or None,national_identity=m.get('national_identity') or None,
          metadata_source=p.get('metadata_source','division_roster/profile')))
    # One raw metadata row per player; all historical roster versions retained.
    raw['players']=[raw_row({'id':int(pid),'name':p['name'],
        'roster_records':[v for v in bundle['players'] if str(v['id'])==pid],
        'profile':bundle['profiles'].get(pid)},season='2025-26',player_id=pid)
        for pid,p in metadata.items()]
    pm={p['player_id']:p for p in out['players']}
    for r in out['player_game_logs']:
        for k in ('player_name_english','player_name_normalized'): r[k]=pm[r['player_id']][k]
    tm={(r['game_id'],r['team_id']):r for r in out['team_game_logs']}
    for r in out['team_game_logs']:
        opp=tm.get((r['game_id'],r['opponent_id']))
        r['opponent_possessions_est']=opp['possessions_est'] if opp else None
        r['DRtg']=ratio(100*r['opponent_points'],r['opponent_possessions_est'])
        r['Net_Rating']=None if r['ORtg'] is None or r['DRtg'] is None else r['ORtg']-r['DRtg']
    frames={k:pd.DataFrame(v) for k,v in out.items()}
    # Normalize membership uniqueness; multiple source phases remain explicit.
    frames['roster_memberships']=frames['roster_memberships'].drop_duplicates()
    frames['target_players_2025_26']=frames['player_game_logs'][frames['player_game_logs'].player_id.isin(map(str,TARGETS))].copy()
    cols=['game_id','team_id','team_points','opponent_points','possessions_est','ORtg','DRtg','Net_Rating']
    frames['tpbl_2025_26_analysis_ready']=frames['player_game_logs'].merge(
        frames['team_game_logs'][cols].rename(columns={c:'team_'+c if c in ('ORtg','DRtg','Net_Rating') else c for c in cols}),
        on=['game_id','team_id'],how='left',validate='many_to_one')
    for folder,tables in [('raw',{k:pd.DataFrame(v) for k,v in raw.items()}),('processed',frames)]:
        dest=Path(root)/'data'/folder; dest.mkdir(parents=True,exist_ok=True)
        for name,df in tables.items():
            if folder=='processed':
                keys=[c for c in ['game_date','game_id','team_id','player_id','division_id'] if c in df]
                if keys: df=df.sort_values(keys,kind='stable')
            df.to_csv(dest/f'{name}.csv',index=False,encoding='utf-8',lineterminator='\n')
    return frames,issues

"""Discover season, rosters, then collect target and league box scores."""
import json
import logging
from pathlib import Path
from .client import Client

TARGETS = {10860:'McCullough',68:'Kromah',10861:'Diallo',16:'Miller'}

def collect(root, offline=False, refresh=False):
    c=Client(root,offline,refresh)
    robots=c.check_robots()
    failures=[]
    previous=Path(root)/'.cache/collection.json'
    previous_failures={}
    if offline and previous.exists():
        previous_failures={f['endpoint']:f for f in json.loads(previous.read_text(encoding='utf-8')).get('failures',[])}
    def get(path,optional=False):
        try: return c.get(path)
        except Exception as e:
            logging.error('Failed %s: %s',path,type(e).__name__)
            failure={'endpoint':path,'error':type(e).__name__,
                             'http_status':getattr(getattr(e,'response',None),'status_code',None),
                             'optional_enrichment':optional}
            if offline and path in previous_failures:
                failure={**previous_failures[path],'optional_enrichment':optional}
            failures.append(failure)
            return None
    seasons=get('seasons')
    season=next(s for s in seasons if s['name'].startswith('2025-2026'))
    if season['id']!=2 or season['gohoops_id']!=213:
        raise ValueError('Season identifiers changed; review discovery')
    divisions=get('events/2/divisions')
    teams=get('events/2/teams')
    games=get('seasons/2/games')
    if not all((divisions,teams,games)): raise RuntimeError('Core discovery failed')
    players=[]
    for d in divisions:
        roster=get(f"divisions/{d['id']}/players")
        for p in roster or []: players.append({'division_id':d['id'],**p})
    profile_ids=sorted({p['id'] for p in players}|set(TARGETS))
    profiles={str(pid):get(f'players/{pid}',optional=True) for pid in profile_ids}
    target_logs={}
    for pid in TARGETS:
        for d in divisions:
            key=f"{pid}:{d['id']}"
            target_logs[key]=get(f"players/{pid}/games/stats?division_id={d['id']}")
    team_checks={}
    for d in divisions:
        team_checks[str(d['id'])]=get(f"teams/5/games/stats?division_id={d['id']}")
    boxes={}
    target_gate_checked=False
    ordered=sorted(games,key=lambda g:(5 not in (g['home_team']['id'],g['away_team']['id']),g['gamed_at'],g['id']))
    for i,g in enumerate(ordered):
        if g['status']!='COMPLETED': continue
        if not target_gate_checked and 5 not in (g['home_team']['id'],g['away_team']['id']):
            # Verify target values before expanding beyond Leopards games.
            mismatches=[]
            for key,logs in target_logs.items():
                pid=key.split(':')[0]
                for row in logs or []:
                    gid=str(row['game']['id']); box=boxes.get(gid)
                    if not box:
                        mismatches.append((gid,pid,'missing box')); continue
                    candidates=box['home_team']['players']['total']
                    candidates=(list(candidates.values()) if isinstance(candidates,dict) else candidates)
                    other=box['away_team']['players']['total']
                    candidates+=list(other.values()) if isinstance(other,dict) else other
                    match=next((p for p in candidates if str(p['id'])==pid),None)
                    for field in ('score','time_on_court','plus_minus','field_goals_attempted','free_throws_attempted'):
                        if not match or match.get(field)!=row['accumulated_stats'].get(field):
                            mismatches.append((gid,pid,field))
            if mismatches:
                failures.append({'endpoint':'target_box_gate','error':str(mismatches),'optional_enrichment':False})
                logging.error('Target box validation has exceptions; retaining them while collecting other pages')
            target_gate_checked=True
            if not mismatches: logging.info('Target box-score gate passed; expanding to remaining league games')
        boxes[str(g['id'])]=get(f"games/{g['id']}/stats")
        if (i+1)%10==0: logging.info('Box scores %s/%s',i+1,len(games))
    bundle=dict(season=season,divisions=divisions,teams=teams,games=games,players=players,
                profiles=profiles,target_logs=target_logs,team_checks=team_checks,boxes=boxes,
                failures=failures,robots=robots,manifest=c.manifest)
    out=Path(root)/'.cache/collection.json'
    out.write_text(json.dumps(bundle,ensure_ascii=False),encoding='utf-8')
    return bundle

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    collect(Path(__file__).resolve().parents[1])

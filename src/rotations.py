"""Preserve public substitution events; do not calculate pairing ratings."""
import json
import logging
from pathlib import Path
import pandas as pd
from .client import Client

def collect_rotations(root,bundle,offline=False,refresh=False):
    client=Client(root,offline,refresh); client.check_robots()
    rows=[]; failures=[]
    for i,g in enumerate(bundle['games']):
        if g['status']!='COMPLETED': continue
        try:
            data=client.get(f"games/{g['id']}/broadcasts")
            count=0
            for q in data['rounds']:
                for e in q['events']:
                    if e['event_type']!='Rotation': continue
                    count+=1
                    rows.append(dict(season='2025-26',game_id=str(g['id']),division_id=g['division_id'],
                      quarter=e['quarter'],clock_remaining_ms=e['event_quarter_time'],
                      event_order=e['order'],team_id=str(e['team']['id']),player_id=str(e['player']['id']),
                      player_name_original=e['player']['name'],action=e['event_outcome'],
                      is_overtime=e.get('is_overtime'),source_url=f"https://api.tpbl.basketball/api/games/{g['id']}/broadcasts"))
            if not count: failures.append({'game_id':g['id'],'reason':'no rotation events'})
        except Exception as exc:
            failures.append({'game_id':g['id'],'reason':type(exc).__name__})
        if (i+1)%25==0: logging.info('Substitution feeds %s/%s',i+1,len(bundle['games']))
    dest=Path(root)/'data/processed'; dest.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(dest/'substitution_events.csv',index=False,encoding='utf-8')
    (Path(root)/'.cache/rotation_manifest.json').write_text(json.dumps(client.manifest),encoding='utf-8')
    return failures

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    root=Path(__file__).resolve().parents[1]
    bundle=json.loads((root/'.cache/collection.json').read_text(encoding='utf-8'))
    failures=collect_rotations(root,bundle)
    (root/'.cache/rotation_failures.json').write_text(json.dumps(failures),encoding='utf-8')

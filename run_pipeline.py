"""Run public collection, normalization, validation and reports."""
import argparse
import json
import logging
from pathlib import Path
import pandas as pd
from src.collect import collect
from src.transform import transform
from src.validate import validate
from src.rotations import collect_rotations
from src.rotation_audit import audit_rotations
from src.report import reports
from src.mccullough import generate as generate_mccullough

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline',action='store_true',help='Use cached responses; never access network')
    parser.add_argument('--refresh',action='store_true',help='Refresh cached responses from public API')
    args=parser.parse_args()
    if args.offline and args.refresh: parser.error('--offline and --refresh are mutually exclusive')
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    root=Path(__file__).resolve().parent
    bundle=collect(root,args.offline,args.refresh)
    frames,issues=transform(bundle,root)
    mccullough_frames,mccullough_checks=generate_mccullough(root)
    frames.update(mccullough_frames)
    failures=collect_rotations(root,bundle,args.offline,args.refresh)
    frames['substitution_events']=pd.read_csv(root/'data/processed/substitution_events.csv',dtype={'game_id':str,'player_id':str,'team_id':str})
    checks=validate(frames,bundle,root,issues)
    checks.extend(mccullough_checks)
    pd.DataFrame(checks).to_csv(root/'reports/validation_checks.csv',index=False)
    audit=audit_rotations(root,frames['player_game_logs'])
    audit['collection_failures']=failures
    summary=reports(root,frames,bundle,checks,audit)
    logging.info('Result: %s',json.dumps(summary,ensure_ascii=False))
    return 1 if summary['validation_failures'] or summary['manual_failures'] or failures else 0

if __name__=='__main__':
    raise SystemExit(main())

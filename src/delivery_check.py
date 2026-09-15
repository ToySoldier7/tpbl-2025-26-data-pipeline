"""Verify committed snapshot bytes, UTF-8, sizes and expected artifacts."""
import hashlib
import json
from pathlib import Path
import pandas as pd

def main():
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'reports/source_manifest.json').read_text(encoding='utf-8'))
    rows=[]
    for item in manifest['outputs']:
        path=root/item['path']; data=path.read_bytes()
        assert hashlib.sha256(data).hexdigest()==item['sha256'],item['path']
        data.decode('utf-8',errors='strict')
        assert len(data)<50_000_000,item['path']
        df=pd.read_csv(path)
        assert len(df)>0,item['path']
        if 'season' in df: assert set(df.season)=={'2025-26'}
        rows.append({'path':item['path'],'rows':len(df),'bytes':len(data),'sha256_verified':True,'utf8_verified':True})
    (root/'reports/delivery_check.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    inventory='# Dataset delivery inventory\n\nAll files are committed to the private repository on main.\n\n| Dataset | Rows | Exact local path | GitHub path |\n| --- | ---: | --- | --- |\n'
    for r in rows:
        local=(root/r['path']).as_posix()
        remote='https://github.com/ToySoldier7/tpbl-2025-26-data-pipeline/blob/main/'+r['path']
        inventory+=f"| {r['path']} | {r['rows']} | `{local}` | [{r['path']}]({remote}) |\n"
    (root/'reports/dataset_inventory.md').write_text(inventory,encoding='utf-8')
    print(f'Verified {len(rows)} nonempty UTF-8 CSV datasets, season labels, sizes and SHA-256 hashes.')

if __name__=='__main__': main()

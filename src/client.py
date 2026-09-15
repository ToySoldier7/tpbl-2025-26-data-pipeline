"""Polite public HTTP client; never sends credentials or retries access denials."""
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.robotparser import RobotFileParser
import requests

BASE = 'https://api.tpbl.basketball/api/'

class Client:
    def __init__(self, root, offline=False, refresh=False, delay=1.25):
        self.cache = Path(root) / '.cache/http'
        self.cache.mkdir(parents=True, exist_ok=True)
        self.offline, self.refresh, self.delay = offline, refresh, delay
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TPBLResearchPipeline/1.0', 'Accept': 'application/json'})
        self.last = 0
        self.manifest = []
        self.robot = None

    def check_robots(self):
        url = 'https://api.tpbl.basketball/robots.txt'
        path = self.cache / 'robots.json'
        if self.offline:
            info = json.loads(path.read_text(encoding='utf-8'))
        else:
            r = self.session.get(url, timeout=40)
            if r.status_code not in (200,404):
                r.raise_for_status()
            info = {'url':url,'status':r.status_code,'body':r.text if r.status_code==200 else '',
                    'retrieved_at':datetime.now(timezone.utc).isoformat()}
            path.write_text(json.dumps(info), encoding='utf-8')
        self.robot = RobotFileParser()
        self.robot.parse(info['body'].splitlines())
        self.delay = max(self.delay, self.robot.crawl_delay('*') or 0)
        return info

    def get(self, endpoint):
        url = BASE + endpoint
        if self.robot is None:
            raise RuntimeError('Check robots before requests')
        if not self.robot.can_fetch('TPBLResearchPipeline',url):
            raise RuntimeError('robots.txt disallows requested endpoint')
        path = self.cache / (hashlib.sha256(url.encode()).hexdigest() + '.json')
        if path.exists() and not self.refresh:
            envelope = json.loads(path.read_text(encoding='utf-8'))
        else:
            if self.offline: raise FileNotFoundError(f'Offline cache missing: {endpoint}')
            for attempt in range(4):
                time.sleep(max(0, self.delay-(time.monotonic()-self.last)))
                self.last = time.monotonic()
                try:
                    r = self.session.get(url,timeout=(15,60))
                    if r.status_code == 429 or r.status_code >= 500:
                        retry = r.headers.get('Retry-After','0')
                        time.sleep(max(2**(attempt+1),float(retry) if retry.isdigit() else 0))
                        r.raise_for_status()
                    r.raise_for_status()
                    payload=r.json()
                    envelope={'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),
                              'sha256':hashlib.sha256(r.content).hexdigest(),'data':payload}
                    tmp=path.with_suffix('.tmp')
                    tmp.write_text(json.dumps(envelope,ensure_ascii=False),encoding='utf-8')
                    tmp.replace(path)
                    break
                except requests.RequestException as exc:
                    if getattr(exc.response,'status_code',None) in (400,401,403,404) or attempt == 3:
                        raise
                    logging.warning('Retry %s attempt %s', endpoint, attempt+1)
                    time.sleep(2**(attempt+1))
        self.manifest.append({k:v for k,v in envelope.items() if k!='data'})
        return envelope['data']

import hashlib
import json
import requests
import pytest
from urllib.robotparser import RobotFileParser
from src.client import Client,BASE

def allow(c):
    c.robot=RobotFileParser(); c.robot.parse([])

def response(status,payload):
    r=requests.Response(); r.status_code=status
    r._content=json.dumps(payload).encode(); r.url=BASE+'seasons'
    return r

def test_offline_cache_never_requests(tmp_path,monkeypatch):
    c=Client(tmp_path,offline=True); allow(c)
    url=BASE+'seasons'; path=c.cache/(hashlib.sha256(url.encode()).hexdigest()+'.json')
    path.write_text(json.dumps({'url':url,'retrieved_at':'test','sha256':'test','data':[{'id':2}]}))
    def forbidden(*args,**kwargs): raise AssertionError('Network attempted')
    monkeypatch.setattr(c.session,'get',forbidden)
    assert c.get('seasons')==[{'id':2}]
    with pytest.raises(FileNotFoundError): c.get('missing')

def test_access_denial_not_retried(tmp_path,monkeypatch):
    c=Client(tmp_path,delay=0); allow(c); calls=[]
    def get(*a,**k): calls.append(a); return response(403,{})
    monkeypatch.setattr(c.session,'get',get)
    with pytest.raises(requests.HTTPError): c.get('seasons')
    assert len(calls)==1

def test_transient_failure_retried_and_cached(tmp_path,monkeypatch):
    c=Client(tmp_path,delay=0); allow(c)
    replies=iter([response(503,{}),response(200,[{'id':2}])])
    monkeypatch.setattr(c.session,'get',lambda *a,**k:next(replies))
    monkeypatch.setattr('src.client.time.sleep',lambda _:None)
    assert c.get('seasons')==[{'id':2}]
    assert c.get('seasons')==[{'id':2}]

def test_robots_disallow_blocks_request(tmp_path):
    c=Client(tmp_path); c.robot=RobotFileParser(); c.robot.parse(['User-agent: *','Disallow: /api/'])
    with pytest.raises(RuntimeError,match='disallows'): c.get('seasons')

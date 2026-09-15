"""Unit, source-regression and dataset integration tests."""
import json
from pathlib import Path
import pandas as pd
import pytest
from src.normalize import number,identifier,date,normalized_name,ratio,stats,player_metrics,possessions
from src.validate import duplicate_count,validate
from src.report import manual_checks

ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('value,expected',[('1,234',1234),(' 53.3% ',53.3),('--',None),('',None),(None,None),('-9',-9)])
def test_number(value,expected): assert number(value)==expected

@pytest.mark.parametrize('value',['nan','inf','not a number'])
def test_reject_bad_number(value):
    with pytest.raises(ValueError): number(value)

def test_ids_and_names():
    assert identifier('010860')=='10860'
    assert identifier(68.0)=='68'
    for bad in [None,0,-1,1.5]:
        with pytest.raises(ValueError): identifier(bad)
    assert normalized_name('  Chris  McCullough ' )=='chris mccullough'
    assert normalized_name('麥卡洛')=='麥卡洛'

@pytest.mark.parametrize('value',['2026-05-02 17:00:00','2026/05/02','2026-05-02'])
def test_date(value): assert date(value)=='2026-05-02'

def test_bad_date():
    with pytest.raises(ValueError): date('2026-02-30')

def test_source_parser_and_plus_minus():
    source={'score':21,'field_goals_made':8,'field_goals_attempted':15,'three_pointers_made':1,
      'three_pointers_attempted':6,'free_throws_attempted':6,'assists':3,'turnovers':1,
      'time_on_court':2056,'plus_minus':9,'field_goals_percentage':'53.3','is_starting':True}
    r=stats(source)
    assert r['minutes']==pytest.approx(34+16/60)
    assert r['plus_minus']==9
    assert r['FG_pct']==8/15
    assert r['source_FG_pct']==pytest.approx(.533)
    m=player_metrics(r)
    assert m['eFG_pct']==8.5/15
    assert m['TS_pct']==21/(2*(15+.44*6))
    assert m['three_PA_rate']==.4
    assert m['AST_TOV']==3

def test_undefined_metrics_and_dnp():
    assert ratio(0,0) is None
    assert ratio(None,5) is None
    assert stats({'id':23,'name':'王柏智','is_starting':False})['minutes'] is None
    assert all(v is None for v in player_metrics({}).values())

def test_possessions():
    assert possessions({'FGA':80,'OREB':9,'TOV':12,'FTA':19})==pytest.approx(91.36)
    assert possessions({'FGA':80}) is None

def test_duplicates():
    assert duplicate_count(pd.DataFrame({'game_id':[1,1,1],'player_id':[2,2,3]}),['game_id','player_id'])==1

@pytest.fixture(scope='module')
def frames():
    names=['teams','players','games','player_game_logs','team_game_logs']
    return {n:pd.read_csv(ROOT/f'data/processed/{n}.csv',dtype={k:str for k in ['game_id','player_id','team_id','opponent_id','home_team_id','away_team_id']}) for n in names}

def test_dataset_grains_and_season(frames):
    assert len(frames['teams'])==7
    for name,df in frames.items(): assert set(df.season)=={'2025-26'}
    assert not frames['player_game_logs'].duplicated(['game_id','player_id']).any()
    assert not frames['team_game_logs'].duplicated(['game_id','team_id']).any()
    p=frames['player_game_logs']
    assert {'10860','68','10861','16'}.issubset(set(p.player_id))
    assert p[p.appearance].minutes.notna().all()

def test_browser_regression(frames,tmp_path):
    (tmp_path/'reports').mkdir()
    (tmp_path/'tests/fixtures').mkdir(parents=True)
    (tmp_path/'tests/fixtures/browser_crosscheck.csv').write_bytes((ROOT/'tests/fixtures/browser_crosscheck.csv').read_bytes())
    result=manual_checks(tmp_path,frames['player_game_logs'])
    assert len(result)==120
    assert result.result.eq('PASS').all()

@pytest.mark.parametrize('column,value,rule',[('FGM',999,'player_FGM_exceeds_FGA'),('points',-1,'player_negative_counts'),('minutes',1000,'player_invalid_minutes'),('FG_pct',1.5,'player_FG_pct_range')])
def test_validation_catches_corruption(frames,tmp_path,column,value,rule):
    edited={k:v.copy() for k,v in frames.items()}
    idx=edited['player_game_logs'].index[edited['player_game_logs'].appearance][0]
    edited['player_game_logs'].loc[idx,column]=value
    bundle={'failures':[],'target_logs':{},'team_checks':{}}
    checks=validate(edited,bundle,tmp_path,[])
    assert next(c for c in checks if c['check']==rule)['status']=='FAIL'

def test_raw_chinese_and_preservation():
    raw=pd.read_csv(ROOT/'data/raw/player_game_logs.csv')
    sample=raw[(raw.game_id==1493)&(raw.player_id==10860)].iloc[0]
    source=json.loads(sample.source_json)
    assert source['name']=='麥卡洛'
    assert source['plus_minus']==9
    assert source['time_on_court']==2056

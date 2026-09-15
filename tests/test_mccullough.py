from pathlib import Path
import pandas as pd
import pytest
from src.mccullough import build_logs,build_profile,CONTEXT,COUNTS

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def canonical():
    ids={c:str for c in ['player_id','game_id','team_id','opponent_id','home_team_id','away_team_id']}
    return [pd.read_csv(ROOT/f'data/processed/{n}.csv',dtype=ids) for n in ['player_game_logs','team_game_logs','games']]

def test_canonical_filter_and_totals(canonical):
    p,t,g=canonical
    logs=build_logs(p,t,g); profile=build_profile(logs).iloc[0]
    expected=p[(p.player_id=='10860')&(p.season=='2025-26')]
    assert len(logs)==len(expected)==28
    assert logs.team_context_join_status.eq('matched').all()
    for c in COUNTS: assert profile['total_'+c]==pytest.approx(logs[c].sum())
    assert profile.total_minutes==pytest.approx(logs.minutes.sum())
    assert profile.TS_pct==pytest.approx(logs.points.sum()/(2*(logs.FGA.sum()+.44*logs.FTA.sum())))

@pytest.mark.parametrize('field,value',[('opponent_id','999'),('game_date','2026-01-01'),('season','2024-25'),('home_away','wrong')])
def test_inconsistent_team_context_retains_player(canonical,field,value):
    p,t,g=canonical; selected=p[p.player_id=='10860'].iloc[[0]]
    key=selected.iloc[0]
    t.loc[(t.game_id==key.game_id)&(t.team_id==key.team_id),field]=value
    logs=build_logs(selected,t,g)
    assert len(logs)==1
    assert logs.iloc[0].team_context_join_status=='unmatched'
    assert logs[list(CONTEXT.values())+['point_differential']].isna().all().all()

@pytest.mark.parametrize('duplicate',['team','schedule'])
def test_ambiguous_match_not_multiplied(canonical,duplicate):
    p,t,g=canonical; selected=p[p.player_id=='10860'].iloc[[0]]; key=selected.iloc[0]
    if duplicate=='team': t=pd.concat([t,t[(t.game_id==key.game_id)&(t.team_id==key.team_id)]])
    else: g=pd.concat([g,g[g.game_id==key.game_id]])
    logs=build_logs(selected,t,g)
    assert len(logs)==1
    assert logs.iloc[0].team_context_join_status=='ambiguous'
    assert logs[list(CONTEXT.values())].isna().all().all()

def test_missing_context_and_duplicate_player(canonical):
    p,t,g=canonical; selected=p[p.player_id=='10860'].iloc[[0]]
    logs=build_logs(selected,t.iloc[:0],g)
    assert logs.iloc[0].team_context_join_status=='unmatched'
    with pytest.raises(ValueError,match='duplicate'): build_logs(pd.concat([selected,selected]),t,g)

def test_season_percentages_weighted_by_attempts(canonical):
    logs=build_logs(*canonical).iloc[:2].copy()
    logs['FGM']=[1.,0.]; logs['FGA']=[1.,99.]; logs['FG_pct']=[1.,0.]
    logs['three_PM']=0.; logs['FTA']=0.; logs['points']=[2.,0.]
    profile=build_profile(logs).iloc[0]
    assert profile.FG_pct==pytest.approx(.01)
    assert profile.FG_pct!=logs.FG_pct.mean()
    assert profile.TS_pct==pytest.approx(.01)
    logs[['FGM','FGA','three_PM','three_PA','FTA','FTM','TOV']]=0.
    profile=build_profile(logs).iloc[0]
    assert pd.isna(profile.FG_pct) and pd.isna(profile.TS_pct) and pd.isna(profile.AST_TOV)

def test_other_player_or_season_not_included(canonical):
    p,t,g=canonical; other=p[p.player_id=='10860'].iloc[[0]].copy(); other['season']='2024-25'
    assert len(build_logs(pd.concat([p,other]),t,g))==28

"""Explicit type conversion and source-to-analysis schema mapping."""
import math
import re
import unicodedata
from datetime import datetime

STAT_MAP = {'score':'points','field_goals_made':'FGM','field_goals_attempted':'FGA',
 'two_pointers_made':'two_PM','two_pointers_attempted':'two_PA',
 'three_pointers_made':'three_PM','three_pointers_attempted':'three_PA',
 'free_throws_made':'FTM','free_throws_attempted':'FTA','offensive_rebounds':'OREB',
 'defensive_rebounds':'DREB','rebounds':'REB','assists':'AST','steals':'STL',
 'blocks':'BLK','turnovers':'TOV','fouls':'PF','plus_minus':'plus_minus'}
PCT_MAP={'field_goals_percentage':'FG_pct','two_pointers_percentage':'two_P_pct',
 'three_pointers_percentage':'three_P_pct','free_throws_percentage':'FT_pct'}

def number(value):
    if value is None or str(value).strip().lower() in ('','na','n/a','null','none','--','-'):
        return None
    n=float(str(value).strip().replace(',','').rstrip('%'))
    if not math.isfinite(n): raise ValueError('Nonfinite numeric value')
    return int(n) if n.is_integer() else n

def identifier(value):
    n=number(value)
    if n is None or not isinstance(n,int) or n<=0: raise ValueError('Invalid ID')
    return str(n)

def date(value):
    s=str(value).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S','%Y-%m-%d','%Y/%m/%d'):
        try: return datetime.strptime(s,fmt).date().isoformat()
        except ValueError: pass
    raise ValueError(f'Invalid date: {s}')

def normalized_name(value):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',value or '')).strip().casefold()

def ratio(a,b):
    if a is None or b is None or b==0: return None
    return a/b

def stats(source, team=False):
    out={dest:number(source.get(key)) for key,dest in STAT_MAP.items() if not team or dest not in ('points','plus_minus')}
    for key,dest in PCT_MAP.items():
        n=number(source.get(key)); out[dest]=None if n is None else n/100
    for made,attempt,pct in [('FGM','FGA','FG_pct'),('two_PM','two_PA','two_P_pct'),('three_PM','three_PA','three_P_pct'),('FTM','FTA','FT_pct')]:
        # Preserve displayed source percentages separately; undefined ratios stay NA.
        out['source_'+pct]=out[pct]
        out[pct]=ratio(out[made],out[attempt])
    if team:
        out.update(team_points=number(source.get('won_score')),opponent_points=number(source.get('lost_score')))
    else:
        sec=number(source.get('time_on_court'))
        out.update(minutes=None if sec is None else sec/60,time_on_court_seconds=sec,
                   starter=source.get('is_starting'))
    excluded=set(STAT_MAP)|set(PCT_MAP)|{'id','gohoops_id','gohoops_roster_id','name','status','positions','number','is_starting','time_on_court','won_score','lost_score','total_won_score','total_lost_score','field_goals','two_pointers','three_pointers','free_throws'}
    for key,value in source.items():
        if key not in excluded:
            out['source_'+key]=number(value)
    return out

def player_metrics(row):
    fg,three,fa,ft,pts,ast,tov=(row.get(k) for k in ['FGM','three_PM','FGA','FTA','points','AST','TOV'])
    return {'eFG_pct':ratio(None if fg is None or three is None else fg+.5*three,fa),
            'TS_pct':ratio(pts,None if fa is None or ft is None else 2*(fa+.44*ft)),
            'three_PA_rate':ratio(row.get('three_PA'),fa),'FT_rate':ratio(ft,fa),'AST_TOV':ratio(ast,tov)}

def possessions(row):
    vals=[row.get(k) for k in ('FGA','OREB','TOV','FTA')]
    return None if any(v is None for v in vals) else vals[0]-vals[1]+vals[2]+.44*vals[3]

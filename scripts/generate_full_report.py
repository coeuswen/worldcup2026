#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界杯2026 完整报告生成器 v30.0 — 两阶段架构·阶段2（本地AI推理）
职业足球量化分析师 + 博彩风控模型 + 战术分析师

读取GitHub Actions采集的一至四数据(JSON) → AI深度推理 → 输出完整v28.4报告(HTML)
包含: 近期国际赛战绩 / 类似对手参照 / 战术分析(星级力量) / 首发伤病检测 /
      关键球员联赛数据 / 综合推演 / 双面融合(理论+实际) → 最终结论

用法:
  python generate_full_report.py                    # 读取后天数据并提示AI填入
  python generate_full_report.py 2026-06-21         # 指定日期
  python generate_full_report.py 2026-06-21 --deploy # 生成后推送GitHub

工作流:
  1. 读取 data/YYYY-MM-DD.json (GitHub Actions阶段1产出)
  2. 展示数据摘要给AI查看
  3. AI基于数据 + v28.4框架填写16个核心字典
  4. 生成完整HTML报告 → 分析/YYYY-MM-DD-分析报告.htm
  5. 可选: git push到GitHub Pages
"""
import sys
import os
import json
import math
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ====================================================
# 配置
# ====================================================
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR.parent / "data"
REPORT_DIR = SCRIPT_DIR.parent / "分析"

# ELO评级库 (与auto_generate_report保持一致)
ELO_2026 = {
    "Brazil": 2080, "France": 2054, "England": 2030, "Argentina": 2025,
    "Portugal": 2015, "Spain": 2010, "Netherlands": 2000, "Germany": 1995,
    "Belgium": 1975, "Croatia": 1960, "Italy": 1950, "Uruguay": 1940,
    "USA": 1920, "Mexico": 1910, "Colombia": 1900, "Senegal": 1895,
    "Morocco": 1890, "Japan": 1880, "Switzerland": 1870, "Denmark": 1865,
    "Australia": 1855, "South Korea": 1850, "Ecuador": 1840, "Serbia": 1835,
    "Czechia": 1830, "Austria": 1825, "Turkey": 1820, "Poland": 1810,
    "Chile": 1800, "Canada": 1795, "Algeria": 1790, "Egypt": 1785,
    "Iran": 1770, "Saudi Arabia": 1760, "Qatar": 1730, "South Africa": 1720,
    "Paraguay": 1715, "Haiti": 1680, "Bosnia & Herzegovina": 1760,
    "Scotland": 1795, "Norway": 1790,
    # 中文映射
    "巴西": 2080, "法国": 2054, "英格兰": 2030, "阿根廷": 2025,
    "葡萄牙": 2015, "西班牙": 2010, "荷兰": 2000, "德国": 1995,
    "比利时": 1975, "克罗地亚": 1960, "意大利": 1950, "乌拉圭": 1940,
    "美国": 1920, "墨西哥": 1910, "哥伦比亚": 1900, "塞内加尔": 1895,
    "摩洛哥": 1890, "日本": 1880, "瑞士": 1870, "丹麦": 1865,
    "澳大利亚": 1855, "韩国": 1850, "厄瓜多尔": 1840, "塞尔维亚": 1835,
    "捷克": 1830, "奥地利": 1825, "土耳其": 1820, "波兰": 1810,
    "智利": 1800, "加拿大": 1795, "阿尔及利亚": 1790, "埃及": 1785,
    "伊朗": 1770, "沙特阿拉伯": 1760, "卡塔尔": 1730, "南非": 1720,
    "巴拉圭": 1715, "海地": 1680, "波黑": 1760, "苏格兰": 1795,
}

# FIFA排名
FIFA_RANKINGS = {
    "阿根廷": 1, "法国": 2, "西班牙": 3, "英格兰": 4, "巴西": 5,
    "葡萄牙": 6, "比利时": 7, "荷兰": 8, "德国": 9, "哥伦比亚": 10,
    "意大利": 11, "乌拉圭": 12, "克罗地亚": 13, "摩洛哥": 14, "日本": 15,
    "瑞士": 16, "塞内加尔": 17, "墨西哥": 18, "美国": 19, "丹麦": 20,
}


# ====================================================
# 核心工具函数
# ====================================================

def bj_date_offset(days=2):
    bj_tz = timezone(timedelta(hours=8))
    return (datetime.now(bj_tz) + timedelta(days=days)).strftime("%Y-%m-%d")

def format_date_cn(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{d.month}月{d.day}日"

def get_elo(name):
    return ELO_2026.get(name, ELO_2026.get(name.replace(" ", ""), 1700))

def get_fifa(name):
    return FIFA_RANKINGS.get(name, FIFA_RANKINGS.get(name.replace(" ", ""), 50))

def odds_to_prob(home_odds, draw_odds, away_odds):
    """赔率转真实概率"""
    raw_h = 1/home_odds; raw_d = 1/draw_odds; raw_a = 1/away_odds
    total = raw_h+raw_d+raw_a
    return {"home": round(raw_h/total,4), "draw": round(raw_d/total,4), 
            "away": round(raw_a/total,4), "overround": round((total-1)*100,2)}

def compute_elo_prob(elo_home, elo_away):
    elo_diff = elo_home - elo_away + 30
    home_win_prob = 1/(1+10**(-elo_diff/400))
    elo_abs = abs(elo_diff)
    draw_prob = max(0.12, 0.28 - elo_abs*0.0008)
    home_p = home_win_prob * (1-draw_prob)
    away_p = (1-home_win_prob) * (1-draw_prob)
    return {"home": round(home_p,4), "draw": round(draw_prob,4), "away": round(away_p,4)}

def blended_prob(euro, elo, we=0.6, wl=0.4):
    return {"home": round(euro["home"]*we+elo["home"]*wl,4),
            "draw": round(euro["draw"]*we+elo["draw"]*wl,4),
            "away": round(euro["away"]*we+elo["away"]*wl,4)}

def poisson_btts(xg_home, xg_away):
    import math
    def pp(k,l): return l**k*math.exp(-l)/math.factorial(k)
    scores={}
    for h in range(6):
        for a in range(6):
            scores[(h,a)] = pp(h,xg_home)*pp(a,xg_away)
    btts=sum(p for(h,a),p in scores.items() if h>0 and a>0)
    over25=sum(p for(h,a),p in scores.items() if h+a>2)
    top5=sorted(scores.items(),key=lambda x:x[1],reverse=True)[:5]
    return {"btts":round(btts,4),"over25":round(over25,4),
            "under25":round(1-over25,4),
            "top_scores":[(f"{h}:{a}",round(p*100,2)) for(h,a),p in top5]}

def risk_level(hp,dp,ap):
    mp=max(hp,dp,ap); margin=mp-min(hp,dp,ap)
    if mp>=0.55 and margin>=0.25: return "低","🟢"
    elif mp>=0.45 and margin>=0.15: return "中","🟡"
    else: return "高","🔴"


# ====================================================
# 数据加载
# ====================================================

def load_collected_data(target_date):
    """加载阶段1采集的JSON数据"""
    filepath = DATA_DIR / f"{target_date}.json"
    if not filepath.exists():
        print(f"❌ 数据文件不存在: {filepath}")
        print(f"   请先运行 GitHub Actions 或手动执行: python collect_data.py {target_date}")
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"✅ 已加载数据: {filepath}")
    print(f"   版本: {data.get('meta',{}).get('version','?')}")
    print(f"   场次: {len(data.get('matches',{}))}")
    
    if not data.get("matches"):
        print("⚠️ 无比赛数据")
        return None
    
    return data


def summarize_for_ai(data):
    """将采集的数据格式化为AI友好的摘要，用于推理参考"""
    lines = []
    meta = data.get("meta", {})
    target_date = meta.get("target_date", "?")
    
    lines.append(f"\n{'='*70}")
    lines.append(f"  📋 {target_date} 世界杯比赛 — 阶段1数据摘要")
    lines.append(f"{'='*70}\n")
    
    for mk, md in data.get("matches", {}).items():
        # 基础实力
        s1 = md.get("stage_one", {})
        h = s1.get("home", {})
        a = s1.get("away", {})
        
        lines.append(f"▸ {mk}")
        
        # 一、基础实力
        lines.append(f"  【一、基础实力】")
        lines.append(f"  主队: {h.get('name','?')} | ELO:{h.get('elo','?')} | FIFA #{h.get('fifa_rank','?')} | 等级:{h.get('strength_level','?')}")
        if h.get("stats"):
            st = h["stats"]
            lines.append(f"  主队统计: 场均进{st.get('avg_gf','?')} / 场均失{st.get('avg_ga','?')} | 胜率{st.get('wins','?')}/{st.get('played','?')}")
        lines.append(f"  客队: {a.get('name','?')} | ELO:{a.get('elo','?')} | FIFA #{a.get('fifa_rank','?')} | 等级:{a.get('strength_level','?')}")
        if a.get("stats"):
            st = a["stats"]
            lines.append(f"  客队统计: 场均进{st.get('avg_gf','?')} / 场均失{st.get('avg_ga','?')} | 胜率{st.get('wins','?')}/{st.get('played','?')}")
        lines.append(f"  ELO差距: {s1.get('elo_diff',0)} ({s1.get('dominant_side','?')})")
        
        # 二、状态分析
        s2 = md.get("stage_two", {})
        fs_h = s2.get("form_summary", {}).get("home", {})
        fs_a = s2.get("form_summary", {}).get("away", {})
        lines.append(f"  【二、状态】主队: {fs_h.get('form_string','?')}({fs_h.get('badge','?')},PPG{fs_h.get('ppg','?')}) | "
                     f"客队: {fs_a.get('form_string','?')}{fs_a.get('badge','?')},PPG{fs_a.get('ppg','?')}")
        
        injuries = s2.get("injuries", [])
        if injuries:
            inj_names = [f"{i['player']}({i.get('reason','?')})" for i in injuries[:5]]
            lines.append(f"  伤病: {'; '.join(inj_names)}")
        else:
            lines.append(f"  伤病: ✅ 暂无API伤病数据")
        
        # 三、战术
        s3 = md.get("stage_three", {})
        sp_h = s3.get("star_power_home", {})
        sp_a = s3.get("star_power_away", {})
        lines.append(f"  【三、战术】主队阵容{sp_h.get('total_squad_size','?')}人 | 客队阵容{sp_a.get('total_squad_size','?')}人")
        
        # 四、盘口赔率
        s4 = md.get("stage_four", {})
        pinnacle = s4.get("oddspapi_pinnacle", {})
        o12 = pinnacle.get("1x2", {})
        ah = pinnacle.get("ah_main", {})
        ou = pinnacle.get("ou25", {})
        btts = pinnacle.get("btts", {})
        
        lines.append(f"  【四、Pinnacle赔率】")
        if o12:
            lines.append(f"  1X2: 主{o12.get('home','?')}/平{o12.get('draw','?')}/客{o12.get('away','?')}")
            prob = odds_to_prob(o12["home"],o12["draw"],o12["away"])
            lines.append(f"  隐含概率: 主{prob['home']*100:.1f}%/平{prob['draw']*100:.1f}%/客{prob['away']*100:.1f}%")
        if ah:
            lines.append(f"  亚盘主盘: {ah.get('line',0):+.2f} | 主{ah.get('home','?')}/客{ah.get('away','?')}")
        if ou:
            lines.append(f"  大小球2.5: 大{ou.get('over','?')}/小{ou.get('under','?')}")
        if btts:
            lines.append(f"  BTTS: 是{btts.get('yes','?')}/否{btts.get('no','?')}")
        
        af_pred = s4.get("af_predictions", {})
        if af_pred.get("advice"):
            lines.append(f"  API建议: {af_pred['advice']}")
        
        h2h = s4.get("h2h", [])
        if h2h:
            h2h_matches = " ; ".join([f'{h["score"]}({h["date"]})' for h in h2h])
            lines.append(f"  历史交锋: {h2h_matches}")
        else:
            lines.append(f"  历史交锋: 暂无数据")
        
        lines.append("")
    
    lines.append(f"{'='*70}")
    lines.append(f"  以上为阶段1原始数据，请AI基于此进行v28.4完整推理")
    lines.append(f"{'='*70}\n")
    
    return "\n".join(lines)


# ====================================================
# HTML模板引擎 (v28.4风格)
# ====================================================

CSS_TEMPLATE = """
:root {
  --bg-deep: #0a0f1e;
  --bg-card: #111827;
  --bg-section: #1a2236;
  --border: rgba(255,255,255,0.08);
  --text-primary: #f0f4ff;
  --text-secondary: #94a3b8;
  --blue-bright: #60a5fa;
  --gold: #fbbf24;
  --orange: #fb923c;
  --green: #4ade80;
  --red: #f87171;
  --purple: #a78bfa;
  --teal: #2dd4bf;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg-deep); color: var(--text-primary); font-family: 'SF Pro Display', -apple-system, 'Helvetica Neue', sans-serif; }

/* Header */
.header { background: linear-gradient(135deg, #0a0f1e 0%, #1a1040 50%, #0a1628 100%); padding: 36px 20px; text-align: center; border-bottom: 1px solid var(--border); }
.header h1 { font-size: 1.9em; font-weight: 800; letter-spacing: .02em; }
.header h1 span { color: var(--gold); }
.subtitle { color: var(--text-secondary); margin-top: 8px; font-size: .88em; }
.identity-tags { margin-top: 12px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
.id-tag { background: rgba(96,165,250,.1); border: 1px solid rgba(96,165,250,.3); color: var(--blue-bright); padding: 4px 12px; border-radius: 20px; font-size: .8em; }

.container { max-width: 900px; margin: 0 auto; padding: 20px; }

/* Card */
.match-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; margin-bottom: 24px; overflow: hidden; }

/* Match header */
.match-header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 20px; border-bottom: 1px solid var(--border); }
.match-meta { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.round-badge { background: rgba(251,191,36,.15); color: var(--gold); padding: 3px 10px; border-radius: 12px; font-size: .8em; border: 1px solid rgba(251,191,36,.3); }
.time-badge { background: rgba(96,165,250,.1); color: var(--blue-bright); padding: 3px 10px; border-radius: 12px; font-size: .8em; }
.venue-badge { background: rgba(167,139,250,.1); color: var(--purple); padding: 3px 10px; border-radius: 12px; font-size: .8em; }
.teams-row { display: flex; align-items: center; gap: 20px; }
.team { flex: 1; }
.team-name { font-size: 1.5em; font-weight: 700; }
.elo-badge { font-size: .8em; color: var(--text-secondary); margin-top: 4px; }
.home-team { text-align: right; }
.vs-center { text-align: center; min-width: 120px; }
.vs-text { font-size: 1.2em; font-weight: 800; color: var(--text-secondary); }
.risk-badge { margin-top: 6px; padding: 4px 12px; border-radius: 20px; font-size: .8em; font-weight: 600; display: inline-block; }
.risk-低 { background: rgba(74,222,128,.1); color: var(--green); border: 1px solid rgba(74,222,128,.3); }
.risk-中 { background: rgba(251,191,36,.1); color: var(--gold); border: 1px solid rgba(251,191,36,.3); }
.risk-高 { background: rgba(248,113,113,.1); color: var(--red); border: 1px solid rgba(248,113,113,.3); }

.elo-bar { display: flex; margin-top: 14px; height: 6px; border-radius: 3px; overflow: hidden; }
.elo-bar-home { background: var(--blue-bright); display: flex; align-items: center; justify-content: flex-end; padding-right: 6px; font-size: .65em; color: #0a0f1e; font-weight: 700; }
.elo-bar-away { background: var(--orange); display: flex; align-items: center; padding-left: 6px; font-size: .65em; color: #0a0f1e; font-weight: 700; }

/* Section */
.section { padding: 16px 20px; border-bottom: 1px solid var(--border); }
.section-title { font-size: .85em; font-weight: 700; color: var(--text-secondary); margin-bottom: 12px; letter-spacing: .05em; text-transform: uppercase; }

/* Stat Grid */
.stat-grid { display: flex; gap: 16px; }
.stat-col { flex: 1; }
.stat-team-name { font-size: 1.05em; font-weight: 700; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
.stat-row { display: flex; justify-content: space-between; font-size: .85em; padding: 3px 0; color: var(--text-secondary); }
.stat-row span:last-child { color: var(--text-primary); font-weight: 600; }
.fifa-rank-row { display: flex; align-items: center; gap: 6px; }
.fifa-badge { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #000; padding: 1px 8px; border-radius: 10px; font-size: .75em; font-weight: 700; }
.elo-diff-bar { margin-top: 10px; padding: 8px; background: rgba(255,255,255,.03); border-radius: 6px; text-align: center; font-size: .85em; color: var(--text-secondary); }

/* Form card */
.form-card { background: rgba(255,255,255,.02); border: 1px solid var(--border); border-radius: 10px; padding: 12px; margin-bottom: 10px; }
.form-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.form-team-name { font-size: .95em; font-weight: 700; }
.form-record { font-family: monospace; letter-spacing: 2px; font-size: .95em; }
.form-badge-hot { color: #ef4444; } .form-badge-good { color: #22c55e; }
.form-badge-ok { color: #eab308; } .form-badge-poor { color: #6b7280; }
.form-detail { font-size: .82em; color: var(--text-secondary); line-height: 1.7; }

/* Similar ref card */
.similar-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
.similar-item { background: rgba(255,255,255,.02); border: 1px solid var(--border); border-radius: 8px; padding: 10px; font-size: .82em; line-height: 1.7; }
.similar-item-title { font-weight: 700; color: var(--gold); margin-bottom: 4px; }

/* Tactic card */
.tactic-split { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.tactic-side { background: rgba(255,255,255,.02); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.tactic-team-name { font-weight: 700; margin-bottom: 6px; }
.star-power-box { background: rgba(251,191,36,.06); border: 1px solid rgba(251,191,36,.15); border-radius: 8px; padding: 10px; margin-top: 8px; }
.sp-title { font-size: .78em; color: var(--gold); font-weight: 700; margin-bottom: 4px; }

/* Lineup card */
.lineup-section { margin-top: 10px; }
.lineup-side { margin-bottom: 12px; }
.lineup-team { font-weight: 700; margin-bottom: 6px; color: var(--blue-bright); }
.player-list { display: flex; flex-wrap: wrap; gap: 6px; }
.player-chip { background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.18); padding: 3px 10px; border-radius: 12px; font-size: .8em; }
.player-chip.confirmed { border-color: var(--green); color: var(--green); }
.player-chip.doubtful { border-color: var(--gold); color: var(--gold); }
.injury-item { font-size: .83em; color: var(--red); padding: 2px 0; }

/* Odds panel */
.odds-grid { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.odds-card { flex: 1; min-width: 150px; background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.odds-card-title { font-size: .8em; font-weight: 700; color: var(--gold); margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
.odds-card-row { display: flex; justify-content: space-between; align-items: center; font-size: .85em; padding: 3px 0; }
.odds-num { font-weight: 700; color: var(--text-primary); font-size: 1.05em; }
.implied-prob { font-size: .78em; color: var(--text-secondary); min-width: 40px; text-align: right; }
.ah-table { margin-top: 10px; background: rgba(255,255,255,.02); border: 1px solid var(--border); border-radius: 8px; padding: 10px; }
.ah-table-title { font-size: .78em; color: var(--text-secondary); margin-bottom: 8px; }
.ah-lines { display: flex; flex-wrap: wrap; gap: 6px; }
.ah-chip { font-size: .78em; background: rgba(96,165,250,.06); border: 1px solid rgba(96,165,250,.15); padding: 3px 8px; border-radius: 10px; color: var(--text-secondary); }

/* Prob bars */
.prob-row { display: flex; gap: 12px; }
.prob-col { flex: 1; }
.prob-label { font-size: .8em; color: var(--text-secondary); margin-bottom: 6px; }
.prob-bar { background: rgba(255,255,255,.06); border-radius: 4px; height: 8px; overflow: hidden; margin-bottom: 4px; }
.prob-fill { height: 100%; border-radius: 4px; transition: width .3s ease; }
.prob-value { font-size: 1.4em; font-weight: 800; }
.home-color { color: var(--blue-bright); }
.gold-color { color: var(--gold); }
.away-color { color: var(--orange); }
.sub-probs { margin-top: 12px; font-size: .82em; color: var(--text-secondary); }

/* Score matrix */
.score-matrix { margin-top: 12px; padding: 10px; background: rgba(255,255,255,.02); border-radius: 8px; }
.score-matrix-title { font-size: .78em; color: var(--text-secondary); margin-bottom: 8px; }
.score-chips { display: flex; gap: 6px; flex-wrap: wrap; }
.score-chip { background: rgba(255,255,255,.06); border: 1px solid var(--border); padding: 4px 10px; border-radius: 12px; font-size: .82em; color: var(--gold); }
.score-chip em { font-style: normal; color: var(--text-secondary); font-size: .9em; }

/* Analysis text */
.analysis-text { font-size: .88em; line-height: 1.8; color: var(--text-secondary); white-space: pre-wrap; }
.analysis-text-small { font-size: .85em; line-height: 2; color: var(--text-secondary); }
.analysis-text-small strong { color: var(--blue-bright); }

/* Fusion panel */
.fusion-panel { background: linear-gradient(135deg, rgba(96,165,250,.04) 0%, rgba(251,191,36,.04) 100%); border: 1px solid rgba(251,191,36,.12); border-radius: 12px; padding: 14px; margin: 10px 0; }
.fusion-header { display: flex; gap: 16px; margin-bottom: 10px; flex-wrap: wrap; }
.theory-side { flex: 1; min-width: 200px; }
.practice-side { flex: 1; min-width: 200px; }
.side-label { font-size: .78em; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
.theory-label { color: var(--blue-bright); }
.practice-label { color: var(--orange); }
.side-content { font-size: .82em; line-height: 1.7; color: var(--text-secondary); }
.alignment-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: .78em; font-weight: 600; margin-left: 8px; }
.align-consistent { background: rgba(74,222,128,.1); color: var(--green); border: 1px solid rgba(74,222,128,.3); }
.align-divergence { background: rgba(251,191,36,.1); color: var(--gold); border: 1px solid rgba(251,191,36,.3); }
.align-reversal { background: rgba(248,113,113,.1); color: var(--red); border: 1px solid rgba(248,113,113,.3); }

/* Verdict */
.conclusion-panel { background: linear-gradient(135deg, rgba(251,191,36,.05) 0%, rgba(96,165,250,.05) 100%); padding: 20px; border-top: 1px solid rgba(251,191,36,.2); }
.conclusion-header { font-size: 1em; font-weight: 800; color: var(--gold); margin-bottom: 16px; letter-spacing: .05em; }
.conclusion-body { display: flex; gap: 16px; flex-wrap: wrap; }
.score-recommendation { flex: 1; min-width: 120px; text-align: center; }
.rec-label { font-size: .75em; color: var(--text-secondary); }
.rec-score { font-size: 2.5em; font-weight: 900; color: var(--gold); letter-spacing: .05em; }
.rec-label-sub { font-size: .8em; color: var(--text-secondary); margin-top: 4px; }
.verdict-block { flex: 2; min-width: 180px; }
.verdict-main { font-size: 1.1em; font-weight: 700; margin-bottom: 6px; }
.verdict-conf { font-size: .85em; color: var(--green); margin-bottom: 8px; }
.verdict-scores { display: flex; gap: 6px; flex-wrap: wrap; }
.verdict-note { margin-top: 8px; font-size: .78em; color: var(--text-secondary); }
.risk-block { flex: 1; min-width: 100px; text-align: center; padding: 12px; border-radius: 10px; }
.risk-bg-低 { background: rgba(74,222,128,.08); border: 1px solid rgba(74,222,128,.2); }
.risk-bg-中 { background: rgba(251,191,36,.08); border: 1px solid rgba(251,191,36,.2); }
.risk-bg-高 { background: rgba(248,113,113,.08); border: 1px solid rgba(248,113,113,.2); }
.risk-label { font-size: .75em; color: var(--text-secondary); }
.risk-value { font-size: 1.2em; font-weight: 700; margin-top: 4px; }
.btts-note { font-size: .75em; color: var(--text-secondary); margin-top: 4px; }

.footer { text-align: center; padding: 30px; color: var(--text-secondary); font-size: .8em; border-top: 1px solid var(--border); }
.disclaimer { background: rgba(248,113,113,.05); border: 1px solid rgba(248,113,113,.2); border-radius: 8px; padding: 12px 16px; margin: 20px auto; max-width: 700px; color: #f87171; font-size: .82em; }
"""


def render_match_html(match_key, collected_data, ai_analysis=None):
    """
    渲染单场比赛的完整HTML (含v28.4全套卡片)
    
    collected_data: 阶段1的原始数据(dict)
    ai_analysis: AI填充的分析数据(dict)，包含:
      - tactic_analysis: 战术分析文字
      - similar_ref: 类似对手参照
      - synthesis: 双面融合结论
      - lineup_info: 首发阵容信息
      - player_league_data: 关键球员联赛数据
      - 推演: 综合推演
    """
    if ai_analysis is None:
        ai_analysis = {}
    
    # ===== 从采集数据提取基础信息 =====
    s1 = collected_data.get("stage_one", {})
    s2 = collected_data.get("stage_two", {})
    s3 = collected_data.get("stage_three", {})
    s4 = collected_data.get("stage_four", {})
    
    home_name = s1.get("home", {}).get("name", "?")
    away_name = s1.get("away", {}).get("name", "?")
    
    elo_h = s1.get("home", {}).get("elo", 1700)
    elo_a = s1.get("away", {}).get("elo", 1700)
    fifa_h = s1.get("home", {}).get("fifa_rank", 50)
    fifa_a = s1.get("away", {}).get("fifa_rank", 50)
    level_h = s1.get("home", {}).get("strength_level", "?")
    level_a = s1.get("away", {}).get("strength_level", "?")
    elo_diff = elo_h - elo_a
    
    fix = collected_data.get("fixture", {})
    venue = fix.get("venue", "")
    city = fix.get("city", "")
    time_utc = fix.get("time_utc", "")
    league_round = fix.get("league_round", "小组赛")
    
    if time_utc:
        try:
            utc_dt = datetime.fromisoformat(time_utc.replace("Z", "+00:00"))
            bj_dt = utc_dt + timedelta(hours=8)
            time_cn = bj_dt.strftime("%H:%M 北京时间")
        except:
            time_cn = ""
    else:
        time_cn = ""
    
    # ===== 赔率数据 =====
    pinnacle = s4.get("oddspapi_pinnacle", {})
    o12 = pinnacle.get("1x2", {})
    ah = pinnacle.get("ah_main", {})
    ou = pinnacle.get("ou25", {})
    btts = pinnacle.get("btts", {})
    dc = pinnacle.get("dc", {})
    
    # 计算融合概率
    if o12:
        euro_prob = odds_to_prob(o12["home"], o12["draw"], o12["away"])
        elo_prob = compute_elo_prob(elo_h, elo_a)
        final_prob = blended_prob(euro_prob, elo_prob, 0.6, 0.4)
    else:
        elo_prob = compute_elo_prob(elo_h, elo_a)
        final_prob = elo_prob
    
    # xG估算
    xg_ratio = (elo_h/max(elo_a,1)) ** 0.5
    base_xg = 1.2
    xg_h = base_xg * xg_ratio
    xg_a = base_xg / xg_ratio
    if ou:
        try:
            over_p = 1/ou["over"]; under_p = 1/ou["under"]
            total_p = over_p+under_p; over_pct = over_p/total_p
            implied_total = max(1.5, min(-2.5/math.log(max(over_pct,0.01)), 5.0))
            xg_h = round(implied_total*elo_h/(elo_h+elo_a), 2)
            xg_a = round(implied_total*elo_a/(elo_h+elo_a), 2)
        except: pass
    
    poisson = poisson_btts(xg_h, xg_a)
    if btts:
        try:
            btts_p = (1/btts["yes"])/(1/btts["yes"]+1/btts["no"])
            final_prob["btts"] = round(btts_p, 4)
        except: pass
    if ou:
        try:
            ou_p = (1/ou["over"])/(1/ou["over"]+1/ou["under"])
            final_prob["over25"] = round(ou_p, 4)
            final_prob["under25"] = round(1-ou_p, 4)
        except: pass
    final_prob.update(poisson)
    
    h_pct = round(final_prob["home"]*100, 1)
    d_pct = round(final_prob["draw"]*100, 1)
    a_pct = round(final_prob["away"]*100, 1)
    over25 = round(final_prob.get("over25", 0.5)*100, 1)
    btts_pct = round(final_prob.get("btts", 0.4)*100, 1)
    
    risk, risk_icon = risk_level(final_prob["home"], final_prob["draw"], final_prob["away"])
    
    top_scores = final_prob.get("top_scores", [("1:0",10), ("0:0",8), ("1:1",7)])
    score1 = top_scores[0][0]
    score2 = top_scores[1][0] if len(top_scores)>1 else "0:0"
    
    # 推荐
    if final_prob["home"] > final_prob["away"] and final_prob["home"] > final_prob["draw"]:
        fav, verdict = home_name, f"{home_name}胜"
        fav_prob = final_prob["home"]
    elif final_prob["away"] > final_prob["home"] and final_prob["away"] > final_prob["draw"]:
        fav, verdict = away_name, f"{away_name}胜"
        fav_prob = final_prob["away"]
    else:
        fav, verdict = "平局", "平局"
        fav_prob = final_prob["draw"]
    
    # ===== 状态数据 =====
    form_h = s2.get("form_summary", {}).get("home", {})
    form_a = s2.get("form_summary", {}).get("away", {})
    recent_h = s2.get("recent_form_home", [])
    recent_a = s2.get("recent_form_away", [])
    injuries = s2.get("injuries", [])
    players_h = s2.get("players_home", [])
    players_a = s2.get("players_away", [])
    
    form_badge_class = lambda b: f"form-badge-{b}"
    
    # ===== AI分析数据 =====
    tactic_text = ai_analysis.get("tactic_analysis", "")
    similar_ref = ai_analysis.get("similar_ref", {})
    synthesis = ai_analysis.get("synthesis", {})
    lineup_info = ai_analysis.get("lineup_info", {})
    player_data = ai_analysis.get("player_league_data", {})
    推演 = ai_analysis.get("match_prediction", "")
    
    fusion_verdict = synthesis.get("fusion_verdict", "")
    fusion_score = synthesis.get("fusion_score", score1)
    fusion_conf = synthesis.get("fusion_conf", "")
    alignment = synthesis.get("alignment", "待分析")
    theory_dir = synthesis.get("theory_dir", "")
    practice_dir = synthesis.get("practice_dir", "")
    gap_desc = synthesis.get("gap", "")
    risk_flag = synthesis.get("risk_flag", f"{risk_icon} 风险: {risk}")
    
    # ===== 开始渲染HTML =====
    html_parts = []
    H = html_parts.append
    
    H(f"""<div class="match-card" id="{home_name}vs{away_name}">
  
  <!-- Match Header -->
  <div class="match-header">
    <div class="match-meta">
      <span class="round-badge">{league_round}</span>
      {"<span class='time-badge'>"+time_cn+"</span>" if time_cn else ""}
      {"<span class='venue-badge'>"+city+" · "+venue+"</span>" if venue else ""}
    </div>
    <div class="teams-row">
      <div class="team home-team">
        <div class="team-name">{home_name}</div>
        <div class="elo-badge">ELO {elo_h} · FIFA #{fifa_h}</div>
      </div>
      <div class="vs-center">
        <div class="vs-text">VS</div>
        <div class="risk-badge risk-{risk.lower()}">{risk_icon} 风险: {risk}</div>
      </div>
      <div class="team away-team">
        <div class="team-name">{away_name}</div>
        <div class="elo-badge">ELO {elo_a} · FIFA #{fifa_a}</div>
      </div>
    </div>
    <div class="elo-bar">
      <div class="elo-bar-home" style="width:{elo_h/(elo_h+elo_a)*100:.1f}%">{elo_h}</div>
      <div class="elo-bar-away" style="width:{elo_a/(elo_h+elo_a)*100:.1f}%">{elo_a}</div>
    </div>
  </div>""")
    
    # 一、基础实力
    H(f"""  <!-- 一、基础实力分析 -->
  <div class="section">
    <div class="section-title">📊 一、基础实力分析</div>
    <div class="stat-grid">
      <div class="stat-col">
        <div class="stat-team-name home-color">{home_name}</div>
        <div class="stat-row"><span>ELO评级</span><span>{elo_h}</span></div>
        <div class="stat-row"><span>FIFA世界排名</span><span><span class="fifa-rank-row">#{fifa_h}<span class="fifa-badge">{level_h}</span></span></span></div>
        <div class="stat-row"><span>场均xG</span><span>{xg_h:.2f}</span></div>
        <div class="stat-row"><span>实力等级</span><span>{level_h}</span></div>
      </div>
      <div class="stat-col">
        <div class="stat-team-name away-color">{away_name}</div>
        <div class="stat-row"><span>ELO评级</span><span>{elo_a}</span></div>
        <div class="stat-row"><span>FIFA世界排名</span><span><span class="fifa-rank-row">#{fifa_a}<span class="fifa-badge">{level_a}</span></span></span></div>
        <div class="stat-row"><span>场均xG</span><span>{xg_a:.2f}</span></div>
        <div class="stat-row"><span>实力等级</span><span>{level_a}</span></div>
      </div>
    </div>
    <div class="elo-diff-bar">
      ELO差距: <strong>{abs(elo_diff)}</strong> 分 ({'★ '+home_name+' 占优' if elo_diff>0 else ('★ '+away_name+' 占优' if elo_diff<0 else '势均力敌')})
      &nbsp;|&nbsp; FIFA排名差: #{abs(fifa_h-fifa_a)}
    </div>
  </div>""")
    
    # 二、状态分析 (近期国际赛战绩)
    H(f"""  <!-- 二、状态分析：近期国际赛战绩 -->
  <div class="section">
    <div class="section-title">🔄 二、状态分析（近期国际赛战绩）</div>""")
    
    # 主队状态卡
    rec_str_h = form_h.get("record", "??????")
    badge_cls = form_badge_class(form_h.get("badge","ok"))
    fs_detail_h = ""
    if recent_h:
        matches_str = " | ".join([f"{r['outcome']}{r['score']}" for r in recent_h[:6]])
        goals_str = f" 进{form_h.get('gf',0)} 失{form_h.get('ga',0)}"
        fs_detail_h = f"<div class='form-detail'>近期: {matches_str}{goals_str} | PPG: {form_h.get('ppg','?.?')}</div>"
    H(f"""    <div class="form-card">
      <div class="form-header">
        <span class="form-team-name home-color">🔥 {home_name} 近期状态</span>
        <span class="form-record {badge_cls}">{rec_str_h}</span>
      </div>
      <div class='form-detail'>{form_h.get('form_string', '?')} | PPG: {form_h.get('ppg', '?')}</div>
      {fs_detail_h}
    </div>""")
    
    # 客队状态卡
    rec_str_a = form_a.get("record", "??????")
    badge_cls_a = form_badge_class(form_a.get("badge","ok"))
    fs_detail_a = ""
    if recent_a:
        matches_str = " | ".join([f"{r['outcome']}{r['score']}" for r in recent_a[:6]])
        goals_str = f" 进{form_a.get('gf',0)} 失{form_a.get('ga',0)}"
        fs_detail_a = f"<div class='form-detail'>近期: {matches_str}{goals_str} | PPG: {form_a.get('ppp','?.?')}</div>"
    H(f"""    <div class="form-card">
      <div class="form-header">
        <span class="form-team-name away-color">🔥 {away_name} 近期状态</span>
        <span class="form-record {badge_cls_a}">{rec_str_a}</span>
      </div>
      <div class='form-detail'>{form_a.get('form_string', '?')} | PPG: {form_a.get('ppp', '?')}</div>
      {fs_detail_a}
    </div>
  </div>""")
    
    # 三、战术克制分析 (星级力量 + AI战术推演)
    sp_h = s3.get("star_power_home", {})
    sp_a = s3.get("star_power_away", {})
    
    sp_h_size = sp_h.get("total_squad_size", "?")
    sp_a_size = sp_a.get("total_squad_size", "?")
    
    H(f"""  <!-- 三、战术克制分析 -->
  <div class="section">
    <div class="section-title">⚔️ 三、战术克制分析（含星级力量）</div>
    <div class="tactic-split">
      <div class="tactic-side">
        <div class="tactic-team-name home-color">🏠 {home_name} 战术风格</div>
        <div class="analysis-text-small">{tactic_text or f'{home_name}战术分析待AI填充...基于ELO {elo_h} / FIFA #{fifa_h}'}</div>
        <div class="star-power-box">
          <div class="sp-title">⭐ 星级力量</div>
          <div class="analysis-text-small">{ai_analysis.get('star_power_home_text', f'阵容{sp_h_size}人 | 详情待补充')}</div>
        </div>
      </div>
      <div class="tactic-side">
        <div class="tactic-team-name away-color">✈️ {away_name} 战术风格</div>
        <div class="analysis-text-small">{ai_analysis.get('tactic_away_text', f'{away_name}战术分析待AI填充...基于ELO {elo_a} / FIFA #{fifa_a}')}</div>
        <div class="star-power-box">
          <div class="sp-title">⭐ 星级力量</div>
          <div class="analysis-text-small">{ai_analysis.get('star_power_away_text', f'阵容{sp_a_size}人 | 详情待补充')}</div>
        </div>
      </div>
    </div>""")
    
    # 首发伤病阵容检测
    H(f"""    <!-- 首发伤病阵容检测 -->
    <div class="lineup-section" style="margin-top:12px;">
      <div style="font-weight:700;font-size:.85em;margin-bottom:8px;">👟 首发·伤病·阵容检测</div>
      <div class="lineup-side">
        <div class="lineup-team home-color">{home_name}</div>
        <div class="player-list">""")
    if players_h:
        for p in players_h[:11]:
            confirmed = "confirmed" if p.get("number") else ""
            H(f"<span class='player-chip {confirmed}'>{p.get('name','?')}<small>({p.get('position','?')})</small></span>")
    elif lineup_info.get("home_lineup"):
        for p in lineup_info["home_lineup"]:
            H(f"<span class='player-chip confirmed'>{p}</span>")
    else:
        H("<span class='player-chip'>待确认首发...</span>")
    H("""</div>
      </div>
      <div class="lineup-side">
        <div class="lineup-team away-color">{away_name}</div>
        <div class="player-list">""")
    if players_a:
        for p in players_a[:11]:
            confirmed = "confirmed" if p.get("number") else ""
            H(f"<span class='player-chip {confirmed}'>{p.get('name','?')}<small>({p.get('position','?')})</small></span>")
    elif lineup_info.get("away_lineup"):
        for p in lineup_info["away_lineup"]:
            H(f"<span class='player-chip confirmed'>{p}</span>")
    else:
        H("<span class='player-chip'>待确认首发...</span>")
    H("""</div>
      </div>
""")
    if injuries:
        H('<div style="margin-top:8px;">')
        H('<span style="font-size:.8em;color:var(--red);">⚠️ 伤病:</span>')
        for inj in injuries[:8]:
            H(f'<span class="injury-item">• {inj["player"]}({inj.get("reason","?")}) [{inj.get("status","?")}]</span>')
        H('</div>')
    H("""    </div>
  </div>""")
    
    # 关键球员联赛数据
    pd_h = player_data.get("home_players", []) if isinstance(player_data, dict) else []
    pd_a = player_data.get("away_players", []) if isinstance(player_data, dict) else []
    
    H(f"""  <!-- 关键球员近1-2年联赛数据 -->
  <div class="section">
    <div class="section-title">⚽ 关键球员近1-2年联赛数据</div>
    <div class="similar-grid">
      <div class="similar-item">
        <div class="similar-item-title home-color">{home_name} 关键球员</div>""")
    if pd_h:
        for p in pd_h[:4]:
            H(f"<div>• <strong>{p.get('name','?')}</strong>: {p.get('club','?')} {p.get('stats','?')}</div>")
    else:
        H(f"<div class='analysis-text-small'>待AI联网补充(SRC/StatMuse/Transfermarkt)</div>")
    H(f"""      </div>
      <div class="similar-item">
        <div class="similar-item-title away-color">{away_name} 关键球员</div>""")
    if pd_a:
        for p in pd_a[:4]:
            H(f"<div>• <strong>{p.get('name','?')}</strong>: {p.get('club','?')} {p.get('stats','?')}</div>")
    else:
        H(f"<div class='analysis-text-small'>待AI联网补充(SRC/StatMuse/Transfermarkt)</div>")
    H("""      </div>
    </div>
  </div>""")
    
    # 四、盘口与赔率分析
    H(f"""  <!-- 四、盘口与赔率分析 -->
  <div class="section">
    <div class="section-title">📈 四、盘口与赔率分析 (Pinnacle)</div>""")
    
    if o12:
        H(f"""    <div class="odds-grid">
      <div class="odds-card">
        <div class="odds-card-title">欧赔 1X2</div>
        <div class="odds-card-row"><span class="home-color">{home_name}胜</span><span class="odds-num">{o12['home']:.2f}</span><span class="implied-prob">{round(1/o12['home']*100,1)}%</span></div>
        <div class="odds-card-row"><span class="gold-color">平局</span><span class="odds-num">{o12['draw']:.2f}</span><span class="implied-prob">{round(1/o12['draw']*100,1)}%</span></div>
        <div class="odds-card-row"><span class="away-color">{away_name}胜</span><span class="odds-num">{o12['away']:.2f}</span><span class="implied-prob">{round(1/o12['away']*100,1)}%</span></div>
      </div>""")
        
        if ah:
            ls = f"{ah['line']:+.2f}"
            H(f"""      <div class="odds-card">
        <div class="odds-card-title">亚盘 主盘 {ls}</div>
        <div class="odds-card-row"><span class="home-color">{home_name} {ls}</span><span class="odds-num">{ah['home']:.2f}</span></div>
        <div class="odds-card-row"><span class="away-color">{away_name} {abs(ah['line']):+.2f}</span><span class="odds-num">{ah['away']:.2f}</span></div>
      </div>""")
        
        if ou:
            H(f"""      <div class="odds-card">
        <div class="odds-card-title">大小球 2.5</div>
        <div class="odds-card-row"><span>大2.5</span><span class="odds-num">{ou['over']:.2f}</span><span class="implied-prob">{round(1/ou['over']*100,1)}%</span></div>
        <div class="odds-card-row"><span>小2.5</span><span class="odds-num">{ou['under']:.2f}</span><span class="implied-prob">{round(1/ou['under']*100,1)}%</span></div>
      </div>""")
        
        if btts:
            H(f"""      <div class="odds-card">
        <div class="odds-card-title">BTTS 双方进球</div>
        <div class="odds-card-row"><span>是</span><span class="odds-num">{btts['yes']:.2f}</span><span class="implied-prob">{round(1/btts['yes']*100,1)}%</span></div>
        <div class="odds-card-row"><span>否</span><span class="odds-num">{btts['no']:.2f}</span><span class="implied-prob">{round(1/btts['no']*100,1)}%</span></div>
      </div>""")
        
        H("    </div>")
        
        # 亚盘完整表
        all_ah = pinnacle.get("all_ah", {})
        if all_ah:
            H('<div class="ah-table"><div class="ah-table-title">完整亚盘盘口</div><div class="ah-lines">')
            for lk in sorted(all_ah.keys(), key=float):
                ld = all_ah[lk]; lf=float(lk)
                H(f"<span class='ah-chip'>{lf:+.2f}: 主{ld.get('home','?')}/客{ld.get('away','?')}</span>")
            H("</div></div>")
        
        # 大小完整表
        all_ou = pinnacle.get("all_ou", {})
        if all_ou:
            H('<div class="ah-table"><div class="ah-table-title">完整大小球盘口</div><div class="ah-lines">')
            for lk in sorted(all_ou.keys(), key=float):
                ld = all_ou[lk]; lf=float(lk)
                H(f"<span class='ah-chip'>{lf:.1f}: 大{ld.get('over','?')}/小{ld.get('under','?')}</span>")
            H("</div></div>")
    else:
        H("""    <div class="analysis-text-small">赔率数据采集中...</div>""")
    H("  </div>")
    
    # 五、概率模型
    H(f"""  <!-- 五、概率模型 -->
  <div class="section">
    <div class="section-title">🎯 五、概率模型 (ELO + Pinnacle欧赔 + 泊松)</div>
    <div class="prob-row">
      <div class="prob-col home-prob">
        <div class="prob-label">{home_name} 胜</div>
        <div class="prob-bar"><div class="prob-fill" style="width:{h_pct}%;background:var(--blue-bright)"></div></div>
        <div class="prob-value home-color">{h_pct}%</div>
      </div>
      <div class="prob-col draw-prob">
        <div class="prob-label">平局</div>
        <div class="prob-bar"><div class="prob-fill" style="width:{d_pct}%;background:var(--gold)"></div></div>
        <div class="prob-value gold-color">{d_pct}%</div>
      </div>
      <div class="prob-col away-prob">
        <div class="prob-label">{away_name} 胜</div>
        <div class="prob-bar"><div class="prob-fill" style="width:{a_pct}%;background:var(--orange)"></div></div>
        <div class="prob-value away-color">{a_pct}%</div>
      </div>
    </div>
    <div class="sub-probs">
      <span>大2.5球: <strong>{over25}%</strong> / 小2.5球: <strong>{100-over25:.1f}%</strong></span>
      <span style="margin-left:2em">BTTS(双方进球): <strong>{btts_pct}%</strong></span>
    </div>
    <div class="score-matrix">
      <div class="score-matrix-title">泊松比分概率矩阵 (Top 5)</div>
      <div class="score-chips">
        {''.join(f"<span class='score-chip'>{s} <em>({p}%)</em></span>" for s,p in top_scores[:5])}
      </div>
    </div>
  </div>""")
    
    # 六、综合推演 (AI填充)
    H(f"""  <!-- 六、综合推演 -->
  <div class="section">
    <div class="section-title">🎬 六、综合推演 (超极分析师三位一体)</div>
    <div class="analysis-text-small">{推演 or '''• <strong>控球节奏</strong>: 待AI推演...
• <strong>先进球概率</strong>: 待AI推演...
• <strong>落后变化</strong>: 待AI推演...
• <strong>关键变量</strong>: 待AI推演...
• <strong>终局比分</strong>: 待AI推演...'''}</div>""")
    
    # 关键变量
    H(f"""    <div style="margin-top:10px;padding:10px;background:rgba(251,191,36,.05);border:1px solid rgba(251,191,36,.15);border-radius:8px;font-size:.82em;color:var(--text-secondary);">
      🔑 关键变量: {synthesis.get('key_vars', f'ELO差距{abs(elo_diff)} · FIFA排名差#{abs(fifa_h-fifa_a)} · Pinnacle一致性')}
    </div>
  </div>""")
    
    # 七、双面融合 + 最终结论
    align_cls = {"✅高度一致":"align-consistent","基本一致":"align-consistent",
                 "⚡分歧":"align-divergence","⚡盲区":"align-divergence",
                 "🚨反转":"align-reversal"}.get(alignment, "align-divergence")
    
    H(f"""  <!-- 七、双面融合 + 最终结论 -->
  <div class="conclusion-panel">
    <div class="conclusion-header">⚡ 七、专业分析推理链 (层力星+战术推演)</div>
    
    <!-- 双面融合面板 -->
    <div class="fusion-panel">
      <div class="fusion-header">
        <div class="theory-side">
          <div class="side-label theory-label">📐 理论面 (模型+市场) — 6信号+探源</div>
          <div class="side-content">{theory_dir or f'ELO:ELO {elo_h}→胜率{final_prob["home"]*100:.0f}% | 欧赔:Pinnacle主{o12.get("home","?")} | 亚盘:{ah.get("line","?")} | Poly:-- | xG:{xg_h:.1f}:{xg_a:.1f} | 大小球:{"大"+str(ou.get("over","?")) if ou else "--"}'}</div>
        </div>
        <div class="practice-side">
          <div class="side-label practice-label">🛠️ 实际面 (战术+真实条件) — 5信号+推理</div>
          <div class="side-content">{practice_dir or f'战术:待填充 | 克制度:待计算(0-10) | 可用性:待评估 | 类似对手:待查询 | 平局基线:28%(小组赛)'}</div>
        </div>
      </div>
      <div style="margin-top:8px;">
        <strong>融合判断:</strong>
        <span class="alignment-badge {align_cls}">{alignment}</span>
        {f'<div style="margin-top:6px;font-size:.82em;color:var(--text-secondary);">差距: {gap_desc}</div>' if gap_desc else ''}
      </div>
      
      <div style="margin-top:12px;padding:10px;background:rgba(0,0,0,.15);border-radius:8px;">
        <div style="font-weight:700;font-size:.9em;color:var(--gold);margin-bottom:6px;">🏆 融合结论</div>
        <div class="analysis-text-small" style="font-size:.9em;line-height:1.8;">{fusion_verdict or '待AI深度推理后填充...'}</div>
      </div>
    </div>

    <div class="conclusion-body" style="margin-top:16px;">
      <div class="score-recommendation">
        <div class="rec-label">最可能比分</div>
        <div class="rec-score">{fusion_score or score1}</div>
        <div class="rec-label-sub">次选: {score2}</div>
      </div>
      <div class="verdict-block">
        <div class="verdict-main">主推: <strong>{verdict}</strong></div>
        <div class="verdict-conf">置信度: {round(fav_prob*100,1)}% | 融合信度: {fusion_conf or '?'}</div>
        <div class="verdict-scores">
          {''.join(f"<span class='score-chip'>{s} ({p}%)</span>" for s,p in top_scores[:4])}
        </div>
        <div class="verdict-note">{risk_flag}</div>
      </div>
      <div class="risk-block risk-bg-{risk.lower()}">
        <div class="risk-label">风险等级</div>
        <div class="risk-value">{risk_icon} {risk}</div>
        <div class="btts-note">BTTS: {btts_pct}%</div>
        <div class="btts-note">大2.5: {over25}%</div>
      </div>
    </div>
  </div>
</div>""")

    return "".join(html_parts)


def generate_full_html(target_date, collected_data, analyses_dict=None):
    """生成完整的HTML报告"""
    date_cn = format_date_cn(target_date)
    now_bj = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M 北京时间")
    
    matches_html = ""
    for mk, md in collected_data.get("matches", {}).items():
        ai = analyses_dict.get(mk, {}) if analyses_dict else {}
        matches_html += render_match_html(mk, md, ai)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026世界杯 {date_cn} 量化分析报告 v30.0</title>
<style>
{CSS_TEMPLATE}
</style>
</head>
<body>

<div class="header">
  <h1>🏆 2026世界杯 <span>{date_cn}</span> 量化分析报告</h1>
  <div class="subtitle">v30.0 · v28.4完整推理链 · 双面融合 · 博彩风控模型 · 生成于 {now_bj}</div>
  <div class="identity-tags">
    <span class="id-tag">📊 ELO+FIFA评级</span>
    <span class="id-tag">⚡ xG泊松模型</span>
    <span class="id-tag">📈 Pinnacle全盘口</span>
    <span class="id-tag">⚔️ 战术克制分析</span>
    <span class="id-tag">⭐ 星级力量</span>
    <span class="id-tag">🔄 近期状态</span>
    <span class="id-tag">🔗 双面融合</span>
    <span class="id-tag">🏦 博彩风控</span>
  </div>
</div>

<div class="container">

<div class="disclaimer">
  ⚠️ 本报告仅供量化研究参考，基于数学模型与统计分析。足球存在高度不确定性，任何分析均无法保证结果。请理性看待预测数据。
</div>

{matches_html}

</div>

<div class="footer">
  <p>数据来源: API-FOOTBALL · OddsPAPI.io(Pinnacle) · ELO/FIFA评级 · xG模型 · 泊松分布</p>
  <p style="margin-top:6px">worldcup.imiaozhan.com | v30.0 两阶段架构</p>
</div>

</body>
</html>"""
    
    return html


# ====================================================
# 主入口
# ====================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="世界杯2026完整报告生成器 v30.0")
    parser.add_argument("date", nargs="?", default=None, help="目标日期 YYYY-MM-DD (默认后天)")
    parser.add_argument("--deploy", action="store_true", help="生成后部署到GitHub Pages")
    parser.add_argument("--summary-only", action="store_true", help="只输出数据摘要(不生成HTML)")
    args = parser.parse_args()
    
    target_date = args.date or bj_date_offset(2)
    
    print(f"\n{'='*70}")
    print(f"  世界杯2026 完整报告生成器 v30.0 (阶段2: 本地AI推理)")
    print(f"  目标日期: {target_date} (北京时间)")
    print(f"{'='*70}\n")
    
    # 加载数据
    data = load_collected_data(target_date)
    if not data:
        sys.exit(1)
    
    # 输出摘要
    summary = summarize_for_ai(data)
    print(summary)
    
    if args.summary_only:
        print("\n✅ 摘要模式完成。如需生成完整报告，请去掉 --summary-only 参数")
        sys.exit(0)
    
    # 生成HTML（使用原始数据作为基础，AI分析字段留空供填充）
    print("【生成HTML报告...】")
    html = generate_full_html(target_date, data, {})
    
    # 保存
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{target_date}-分析报告.htm"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    size_kb = len(html.encode("utf-8")) // 1024
    print(f"✅ 报告已保存: {report_path} ({size_kb}KB)")
    
    if args.deploy:
        pages_dir = PROJECT_ROOT / "worldcup2026-pages" / "分析"
        pages_dir.mkdir(parents=True, exist_ok=True)
        deploy_path = pages_dir / f"{target_date}-分析报告.htm"
        shutil.copy(report_path, deploy_path)
        print(f"✅ 已复制到: {deploy_path}")
        
        try:
            os.chdir(PROJECT_ROOT / "worldcup2026-pages")
            subprocess.run(["git", "add", "."], check=True)
            commit_msg = f"v30.0 {target_date} 完整分析报告 (本地AI推理)"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push"], check=True)
            print(f"✅ 已推送到 GitHub")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git操作失败: {e}")

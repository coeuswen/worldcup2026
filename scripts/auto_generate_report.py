#!/usr/bin/env python3
"""
世界杯2026 自动报告生成器 v29.0
职业足球量化分析师 + 博彩风控模型 + 战术分析师

每天北京时间12:00触发，生成后天的世界杯比赛分析报告
使用七步分析框架：基础实力→状态→战术→盘口→概率→推演→结论

用法:
  python auto_generate_report.py                    # 生成后天报告
  python auto_generate_report.py 2026-06-21         # 生成指定日期报告
  python auto_generate_report.py --deploy            # 生成并部署到GitHub Pages
"""
import sys
import os
import json
import math
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 添加scripts目录到路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from api_data_collector import (
    collect_match_data, bj_date_offset, 
    parse_euro_odds, odds_to_prob, compute_elo_prob, 
    blended_prob, poisson_btts, af_get_standings,
    APIFOOTBALL_KEY, AF_HEADERS
)
import requests

# ====================================================
# ELO评级库（2026世界杯前更新）
# ====================================================
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
    # 中文名映射
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

# ====================================================
# 七步分析框架核心
# ====================================================

def compute_elo_rating(home_name, away_name):
    """从名称获取ELO评级"""
    h = ELO_2026.get(home_name, ELO_2026.get(home_name.replace(" ", ""), 1800))
    a = ELO_2026.get(away_name, ELO_2026.get(away_name.replace(" ", ""), 1800))
    return h, a

def compute_final_probs(elo_home, elo_away, euro_odds=None, xg_home=None, xg_away=None):
    """
    融合多信号计算最终概率
    优先级: 欧赔 > ELO > xG泊松
    """
    elo_prob = compute_elo_prob(elo_home, elo_away)
    
    if euro_odds:
        euro_prob = odds_to_prob(euro_odds["home"], euro_odds["draw"], euro_odds["away"])
        final_prob = blended_prob(euro_prob, elo_prob, 0.6, 0.4)
    else:
        final_prob = elo_prob
    
    # xG泊松修正
    if xg_home and xg_away:
        poisson = poisson_btts(xg_home, xg_away)
        final_prob["btts"] = poisson["btts"]
        final_prob["over25"] = poisson["over25"]
        final_prob["under25"] = poisson["under25"]
        final_prob["top_scores"] = poisson["top_scores"]
    
    return final_prob

def risk_level(home_prob, away_prob, draw_prob):
    """根据概率分布评估风险等级"""
    max_prob = max(home_prob, away_prob, draw_prob)
    margin = max_prob - min(home_prob, away_prob, draw_prob)
    
    if max_prob >= 0.55 and margin >= 0.25:
        return "低", "🟢"
    elif max_prob >= 0.45 and margin >= 0.15:
        return "中", "🟡"
    else:
        return "高", "🔴"

def determine_favorite(home_name, away_name, probs):
    """确定最终推荐"""
    h, d, a = probs["home"], probs["draw"], probs["away"]
    if h > a and h > d:
        fav = home_name
        fav_prob = h
        verdict = f"{home_name}胜"
    elif a > h and a > d:
        fav = away_name
        fav_prob = a
        verdict = f"{away_name}胜"
    else:
        fav = "平局"
        fav_prob = d
        verdict = "平局"
    return fav, fav_prob, verdict

def format_date_cn(date_str):
    """将YYYY-MM-DD格式化为中文"""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{d.month}月{d.day}日"

# ====================================================
# HTML报告生成
# ====================================================

def generate_match_html(home, away, mk, match_data, probs, euro_odds, xg_h, xg_a, analysis_text):
    """生成单场比赛的HTML分析卡片"""
    
    fix = match_data.get("fixture", {})
    risk, risk_icon = risk_level(probs["home"], probs["away"], probs["draw"])
    fav, fav_prob, verdict = determine_favorite(home, away, probs)
    
    # 比分推荐
    top_scores = probs.get("top_scores", [("1:0", 10), ("0:0", 8), ("1:1", 7)])
    score1 = top_scores[0][0] if top_scores else "1:0"
    score2 = top_scores[1][0] if len(top_scores) > 1 else "0:0"
    
    # 概率百分比
    h_pct = round(probs["home"] * 100, 1)
    d_pct = round(probs["draw"] * 100, 1)
    a_pct = round(probs["away"] * 100, 1)
    
    over25 = round(probs.get("over25", 0.5) * 100, 1)
    btts = round(probs.get("btts", 0.4) * 100, 1)
    
    # ELO评级
    elo_h, elo_a = compute_elo_rating(home, away)
    elo_diff = elo_h - elo_a
    
    # 欧赔字符串
    if euro_odds:
        odds_str = f"主{euro_odds['home']:.2f} / 平{euro_odds['draw']:.2f} / 客{euro_odds['away']:.2f}"
    else:
        odds_str = "赔率数据待更新"
    
    # 场地和时间
    venue = fix.get("venue", "")
    city = fix.get("city", "")
    time_utc = fix.get("time_utc", "")
    if time_utc:
        try:
            utc_dt = datetime.fromisoformat(time_utc.replace("Z", "+00:00"))
            bj_dt = utc_dt + timedelta(hours=8)
            time_cn = bj_dt.strftime("%H:%M 北京时间")
        except:
            time_cn = ""
    else:
        time_cn = ""
    
    html = f"""
<div class="match-card" id="{home}vs{away}">
  <!-- 比赛头部 -->
  <div class="match-header">
    <div class="match-meta">
      <span class="round-badge">{fix.get("league_round", "小组赛")}</span>
      {"<span class='time-badge'>" + time_cn + "</span>" if time_cn else ""}
      {"<span class='venue-badge'>" + city + " · " + venue + "</span>" if venue else ""}
    </div>
    <div class="teams-row">
      <div class="team home-team">
        <div class="team-name">{home}</div>
        <div class="elo-badge">ELO {elo_h}</div>
      </div>
      <div class="vs-center">
        <div class="vs-text">VS</div>
        <div class="risk-badge risk-{risk.lower()}">{risk_icon} 风险: {risk}</div>
      </div>
      <div class="team away-team">
        <div class="team-name">{away}</div>
        <div class="elo-badge">ELO {elo_a}</div>
      </div>
    </div>
  </div>

  <!-- 概率模型 -->
  <div class="section">
    <div class="section-title">📊 概率模型 (ELO + 欧赔融合)</div>
    <div class="prob-row">
      <div class="prob-col home-prob">
        <div class="prob-label">{home} 胜</div>
        <div class="prob-bar"><div class="prob-fill" style="width:{h_pct}%;background:var(--blue-bright)"></div></div>
        <div class="prob-value home-color">{h_pct}%</div>
      </div>
      <div class="prob-col draw-prob">
        <div class="prob-label">平局</div>
        <div class="prob-bar"><div class="prob-fill" style="width:{d_pct}%;background:var(--gold)"></div></div>
        <div class="prob-value gold-color">{d_pct}%</div>
      </div>
      <div class="prob-col away-prob">
        <div class="prob-label">{away} 胜</div>
        <div class="prob-bar"><div class="prob-fill" style="width:{a_pct}%;background:var(--orange)"></div></div>
        <div class="prob-value away-color">{a_pct}%</div>
      </div>
    </div>
    <div class="sub-probs">
      <span>进球数: 大于2.5球 {over25}% / 小于2.5球 {100-over25:.1f}%</span>
      <span style="margin-left:2em">BTTS(双方进球): {btts}%</span>
    </div>
  </div>

  <!-- 赔率分析 -->
  <div class="section">
    <div class="section-title">📈 盘口与赔率分析</div>
    <div class="odds-row">
      <div class="odds-item">
        <div class="odds-label">欧赔</div>
        <div class="odds-value">{odds_str}</div>
      </div>
      <div class="odds-item">
        <div class="odds-label">ELO差</div>
        <div class="odds-value">{elo_diff:+d} ({home if elo_diff > 0 else away} 占优)</div>
      </div>
      <div class="odds-item">
        <div class="odds-label">场均xG</div>
        <div class="odds-value">{home} {xg_h:.2f} / {away} {xg_a:.2f}</div>
      </div>
    </div>
  </div>

  <!-- 七步分析 -->
  <div class="section analysis-section">
    <div class="section-title">🔬 深度分析</div>
    <div class="analysis-text">{analysis_text}</div>
  </div>

  <!-- 最终结论 -->
  <div class="conclusion-panel">
    <div class="conclusion-header">⚡ 量化分析结论</div>
    <div class="conclusion-body">
      <div class="score-recommendation">
        <div class="rec-label">最可能比分</div>
        <div class="rec-score">{score1}</div>
        <div class="rec-label-sub">次选: {score2}</div>
      </div>
      <div class="verdict-block">
        <div class="verdict-main">主推: <strong>{verdict}</strong></div>
        <div class="verdict-conf">置信度: {round(fav_prob*100, 1)}%</div>
        <div class="verdict-scores">
          {''.join(f'<span class="score-chip">{s} ({p}%)</span>' for s, p in top_scores[:3])}
        </div>
      </div>
      <div class="risk-block risk-bg-{risk.lower()}">
        <div class="risk-label">风险等级</div>
        <div class="risk-value">{risk_icon} {risk}</div>
        <div class="btts-note">BTTS: {btts}%</div>
      </div>
    </div>
  </div>
</div>
"""
    return html

def generate_full_report(target_date, match_data_all, analysis_inputs):
    """
    生成完整HTML报告
    match_data_all: collect_match_data()的返回值
    analysis_inputs: 手动/AI填写的七步分析数据
    """
    date_cn = format_date_cn(target_date)
    now_cn = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M 北京时间")
    
    matches_html = ""
    for mk, md in match_data_all.items():
        if mk not in analysis_inputs:
            continue
        ai = analysis_inputs[mk]
        home = md["fixture"]["home"]
        away = md["fixture"]["away"]
        probs = ai.get("probs", {"home": 0.4, "draw": 0.3, "away": 0.3})
        euro_odds = ai.get("euro_odds")
        xg_h = ai.get("xg_home", 1.3)
        xg_a = ai.get("xg_away", 0.9)
        analysis_text = ai.get("analysis_text", "分析数据更新中...")
        matches_html += generate_match_html(home, away, mk, md, probs, euro_odds, xg_h, xg_a, analysis_text)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026世界杯 {date_cn} 量化分析报告 v29.0</title>
<style>
:root {{
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
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg-deep); color: var(--text-primary); font-family: 'SF Pro Display', -apple-system, 'Helvetica Neue', sans-serif; }}

/* 顶部头部 */
.header {{
  background: linear-gradient(135deg, #0a0f1e 0%, #1a1040 50%, #0a1628 100%);
  padding: 40px 20px;
  text-align: center;
  border-bottom: 1px solid var(--border);
}}
.header h1 {{ font-size: 2em; font-weight: 800; letter-spacing: 0.02em; }}
.header h1 span {{ color: var(--gold); }}
.header .subtitle {{ color: var(--text-secondary); margin-top: 8px; font-size: 0.9em; }}
.identity-tags {{ margin-top: 12px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }}
.id-tag {{ background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.3); color: var(--blue-bright); padding: 4px 12px; border-radius: 20px; font-size: 0.8em; }}

/* 主容器 */
.container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}

/* 比赛卡片 */
.match-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  margin-bottom: 24px;
  overflow: hidden;
}}

/* 比赛头部 */
.match-header {{
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 20px;
  border-bottom: 1px solid var(--border);
}}
.match-meta {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
.round-badge {{ background: rgba(251,191,36,0.15); color: var(--gold); padding: 3px 10px; border-radius: 12px; font-size: 0.8em; border: 1px solid rgba(251,191,36,0.3); }}
.time-badge {{ background: rgba(96,165,250,0.1); color: var(--blue-bright); padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }}
.venue-badge {{ background: rgba(167,139,250,0.1); color: var(--purple); padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }}
.teams-row {{ display: flex; align-items: center; gap: 20px; }}
.team {{ flex: 1; }}
.team-name {{ font-size: 1.5em; font-weight: 700; }}
.elo-badge {{ font-size: 0.8em; color: var(--text-secondary); margin-top: 4px; }}
.home-team {{ text-align: right; }}
.vs-center {{ text-align: center; min-width: 120px; }}
.vs-text {{ font-size: 1.2em; font-weight: 800; color: var(--text-secondary); }}
.risk-badge {{ margin-top: 6px; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 600; display: inline-block; }}
.risk-低 {{ background: rgba(74,222,128,0.1); color: var(--green); border: 1px solid rgba(74,222,128,0.3); }}
.risk-中 {{ background: rgba(251,191,36,0.1); color: var(--gold); border: 1px solid rgba(251,191,36,0.3); }}
.risk-高 {{ background: rgba(248,113,113,0.1); color: var(--red); border: 1px solid rgba(248,113,113,0.3); }}

/* 分区 */
.section {{ padding: 16px 20px; border-bottom: 1px solid var(--border); }}
.section-title {{ font-size: 0.85em; font-weight: 700; color: var(--text-secondary); margin-bottom: 12px; letter-spacing: 0.05em; text-transform: uppercase; }}

/* 概率条 */
.prob-row {{ display: flex; gap: 12px; }}
.prob-col {{ flex: 1; }}
.prob-label {{ font-size: 0.8em; color: var(--text-secondary); margin-bottom: 6px; }}
.prob-bar {{ background: rgba(255,255,255,0.06); border-radius: 4px; height: 8px; overflow: hidden; margin-bottom: 4px; }}
.prob-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s ease; }}
.prob-value {{ font-size: 1.4em; font-weight: 800; }}
.home-color {{ color: var(--blue-bright); }}
.gold-color {{ color: var(--gold); }}
.away-color {{ color: var(--orange); }}
.sub-probs {{ margin-top: 12px; font-size: 0.82em; color: var(--text-secondary); }}

/* 赔率行 */
.odds-row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.odds-item {{ flex: 1; min-width: 150px; }}
.odds-label {{ font-size: 0.75em; color: var(--text-secondary); margin-bottom: 4px; }}
.odds-value {{ font-size: 0.9em; font-weight: 600; color: var(--text-primary); }}

/* 分析文本 */
.analysis-text {{
  font-size: 0.88em;
  line-height: 1.8;
  color: var(--text-secondary);
  white-space: pre-wrap;
}}

/* 结论面板 */
.conclusion-panel {{
  background: linear-gradient(135deg, rgba(251,191,36,0.05) 0%, rgba(96,165,250,0.05) 100%);
  padding: 20px;
  border-top: 1px solid rgba(251,191,36,0.2);
}}
.conclusion-header {{ font-size: 1em; font-weight: 800; color: var(--gold); margin-bottom: 16px; letter-spacing: 0.05em; }}
.conclusion-body {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.score-recommendation {{ flex: 1; min-width: 120px; text-align: center; }}
.rec-label {{ font-size: 0.75em; color: var(--text-secondary); }}
.rec-score {{ font-size: 2.5em; font-weight: 900; color: var(--gold); letter-spacing: 0.05em; }}
.rec-label-sub {{ font-size: 0.8em; color: var(--text-secondary); margin-top: 4px; }}
.verdict-block {{ flex: 2; min-width: 180px; }}
.verdict-main {{ font-size: 1.1em; font-weight: 700; margin-bottom: 6px; }}
.verdict-conf {{ font-size: 0.85em; color: var(--green); margin-bottom: 8px; }}
.verdict-scores {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.score-chip {{ background: rgba(255,255,255,0.06); border: 1px solid var(--border); padding: 4px 10px; border-radius: 12px; font-size: 0.8em; color: var(--text-secondary); }}
.risk-block {{ flex: 1; min-width: 100px; text-align: center; padding: 12px; border-radius: 10px; }}
.risk-bg-低 {{ background: rgba(74,222,128,0.08); border: 1px solid rgba(74,222,128,0.2); }}
.risk-bg-中 {{ background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.2); }}
.risk-bg-高 {{ background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); }}
.risk-label {{ font-size: 0.75em; color: var(--text-secondary); }}
.risk-value {{ font-size: 1.2em; font-weight: 700; margin-top: 4px; }}
.btts-note {{ font-size: 0.75em; color: var(--text-secondary); margin-top: 4px; }}

/* 底部 */
.footer {{
  text-align: center;
  padding: 30px;
  color: var(--text-secondary);
  font-size: 0.8em;
  border-top: 1px solid var(--border);
}}
.disclaimer {{
  background: rgba(248,113,113,0.05);
  border: 1px solid rgba(248,113,113,0.2);
  border-radius: 8px;
  padding: 12px 16px;
  margin: 20px auto;
  max-width: 700px;
  color: #f87171;
  font-size: 0.82em;
}}
</style>
</head>
<body>

<div class="header">
  <h1>🏆 2026世界杯 <span>{date_cn}</span> 量化分析报告</h1>
  <div class="subtitle">v29.0 · 七步量化框架 · 博彩风控模型 · 生成于 {now_cn}</div>
  <div class="identity-tags">
    <span class="id-tag">📊 ELO评级</span>
    <span class="id-tag">⚡ xG模型</span>
    <span class="id-tag">📈 盘口分析</span>
    <span class="id-tag">🎯 泊松分布</span>
    <span class="id-tag">🔬 战术克制</span>
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
  <p>数据来源: API-FOOTBALL · Odds API · ELO评级系统 · xG模型</p>
  <p style="margin-top:6px">worldcup.imiaozhan.com | 每天北京时间12:00自动更新</p>
</div>

</body>
</html>"""
    
    return html

# ====================================================
# 主入口
# ====================================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="自动生成世界杯分析报告")
    parser.add_argument("date", nargs="?", default=None, help="目标日期 YYYY-MM-DD")
    parser.add_argument("--deploy", action="store_true", help="生成后部署到GitHub Pages")
    parser.add_argument("--data-only", action="store_true", help="只采集数据，不生成报告")
    args = parser.parse_args()
    
    # 默认后天
    target_date = args.date or bj_date_offset(2)
    print(f"\n{'='*60}")
    print(f"世界杯2026量化分析报告生成器 v29.0")
    print(f"目标日期: {target_date} (北京时间)")
    print(f"{'='*60}")
    
    # 步骤1: 采集数据
    match_data_all = collect_match_data(target_date)
    
    if args.data_only:
        print("\n✅ 数据采集完成（--data-only模式，跳过报告生成）")
        sys.exit(0)
    
    if not match_data_all:
        print(f"\n⚠️ {target_date} 无世界杯比赛，跳过报告生成")
        sys.exit(0)
    
    # 步骤2: 构建分析输入
    # 注意：xG、赔率、分析文本在API数据采集后自动填充
    # 这里为每场比赛生成基础分析数据
    analysis_inputs = {}
    
    for mk, md in match_data_all.items():
        home = md["fixture"]["home"]
        away = md["fixture"]["away"]
        
        # ELO概率
        elo_h, elo_a = compute_elo_rating(home, away)
        elo_prob = compute_elo_prob(elo_h, elo_a)
        
        # 尝试从API-FOOTBALL获取欧赔
        from api_data_collector import parse_euro_odds
        euro_odds = parse_euro_odds(md.get("odds_af", {}))
        
        # 融合概率
        if euro_odds:
            from api_data_collector import odds_to_prob, blended_prob
            euro_prob = odds_to_prob(euro_odds["home"], euro_odds["draw"], euro_odds["away"])
            final_prob = blended_prob(euro_prob, elo_prob, 0.6, 0.4)
        else:
            final_prob = elo_prob
        
        # xG估算（基于球队ELO，实际应从API获取历史xG）
        xg_ratio = (elo_h / elo_a) ** 0.5
        base_xg = 1.2  # 世界杯场均xG
        xg_h = round(base_xg * xg_ratio, 2)
        xg_a = round(base_xg / xg_ratio, 2)
        
        # 泊松概率
        from api_data_collector import poisson_btts
        poisson = poisson_btts(xg_h, xg_a)
        final_prob.update(poisson)
        
        # API-FOOTBALL预测文字
        pred_data = md.get("predictions", {})
        pred_advice = pred_data.get("predictions", {}).get("advice", "") if pred_data else ""
        
        # 构建分析文本（七步框架骨架，实际AI推演请在此补充）
        analysis_text = f"""【基础实力】{home}(ELO {elo_h}) vs {away}(ELO {elo_a})，差距 {abs(elo_h-elo_a)} 分。
{'ELO占优方：' + (home if elo_h > elo_a else away) + ' → 期望优势显著' if abs(elo_h-elo_a) > 100 else 'ELO差距较小，双方实力接近'}

【概率模型】主场胜率{elo_prob['home']*100:.1f}% / 平局{elo_prob['draw']*100:.1f}% / 客场胜率{elo_prob['away']*100:.1f}%
大于2.5球: {poisson['over25']*100:.1f}% | BTTS: {poisson['btts']*100:.1f}%

【盘口信号】{'欧赔: 主' + str(euro_odds['home']) + ' / 平' + str(euro_odds['draw']) + ' / 客' + str(euro_odds['away']) if euro_odds else '赔率数据采集中，以ELO为主'}

【最可能比分】{' | '.join([s + '(' + str(p) + '%)' for s, p in poisson['top_scores'][:3]])}

⚠️ 注：本场完整七步深度分析（战术克制/状态/推演/结论）将在正式报告中由AI推演填充"""
        
        analysis_inputs[mk] = {
            "probs": final_prob,
            "euro_odds": euro_odds,
            "xg_home": xg_h,
            "xg_away": xg_a,
            "analysis_text": analysis_text,
        }
    
    # 步骤3: 生成HTML
    print("\n[生成HTML报告...]")
    html = generate_full_report(target_date, match_data_all, analysis_inputs)
    
    # 保存报告
    report_name = f"{target_date}-分析报告.html"
    
    # 支持在GitHub Actions中输出到 分析/ 目录
    output_dir_env = os.environ.get("REPORT_OUTPUT_DIR")
    if output_dir_env:
        report_dir = Path(output_dir_env)
    else:
        # 本地或CI模式：输出到仓库根目录下的 分析/ 子目录
        report_dir = SCRIPT_DIR.parent / "分析"
    
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / report_name
    
    # 防止覆盖已有的手工制作报告
    if report_path.exists():
        existing_size = report_path.stat().st_size
        new_size = len(html.encode('utf-8'))
        if existing_size > new_size:
            print(f"⚠️ 已存在更详细的报告 ({existing_size//1024}KB > 自动生成 {new_size//1024}KB)，跳过覆盖")
            print(f"   如需强制覆盖，请先删除: {report_path}")
            sys.exit(0)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {report_path}")
    print(f"   文件大小: {len(html)//1024} KB")
    
    # 步骤4: 可选部署到GitHub Pages
    if args.deploy:
        pages_dir = PROJECT_ROOT / "worldcup2026-pages" / "分析"
        pages_dir.mkdir(parents=True, exist_ok=True)
        deploy_path = pages_dir / f"{target_date}-分析报告.html"
        shutil.copy(report_path, deploy_path)
        print(f"✅ 已复制到: {deploy_path}")
        
        # Git提交
        try:
            os.chdir(PROJECT_ROOT / "worldcup2026-pages")
            subprocess.run(["git", "add", "."], check=True)
            commit_msg = f"v29.0 {target_date} 量化分析报告 (自动生成)"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push"], check=True)
            print(f"✅ 已推送到 GitHub: {commit_msg}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git操作失败: {e}")

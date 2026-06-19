#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界杯2026 数据采集器 v30.0 — 两阶段架构·阶段1（纯数据采集）
职业足球量化分析师 + 博彩风控模型

GitHub Actions 每天12:00北京时间自动运行，采集后天比赛的一至四数据
输出结构化JSON文件 → 本地AI读取后进行深度推理推演

用法:
  python collect_data.py                     # 采集后天数据
  python collect_data.py 2026-06-21          # 采集指定日期
  python collect_data.py --list-dates        # 列出近期有比赛的日期

输出: data/YYYY-MM-DD.json (含一至四全部原始数据)
"""
import sys
import os
import json
import time
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 添加scripts目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from api_data_collector import (
    collect_match_data, bj_date_offset, bj_today,
    af_get_fixtures_by_date, af_get_team_stats,
    af_get_team_recent_fixtures, af_get_players,
    af_get_injuries, af_get_h2h, af_get_predictions,
    af_get_odds,
    oddspapi_get_wc_odds, oddspapi_get_participants, oddspapi_parse_fixture,
    parse_euro_odds, odds_to_prob, compute_elo_prob,
    APIFOOTBALL_KEY, AF_HEADERS,
    safe_get, _wait_for_rate_limit
)
import requests

# ELO评级库 (从auto_generate_report导入或直接定义)
try:
    from auto_generate_report import ELO_2026 as _ELO_EXT
    ELO_2026 = _ELO_EXT
except ImportError:
    # fallback: 使用FIFA_RANKINGS中的子集 + 默认值
    ELO_2026 = {}

# ====================================================
# FIFA世界排名映射 (2026年6月FIFA排名)
# ====================================================
FIFA_RANKINGS = {
    # === 世界前10 ===
    "阿根廷": 1, "France": 2, "法国": 2, "Spain": 3, "西班牙": 3,
    "England": 4, "英格兰": 4, "Brazil": 5, "巴西": 5,
    "Portugal": 6, "葡萄牙": 6, "Belgium": 7, "比利时": 7,
    "Netherlands": 8, "荷兰": 8, "Germany": 9, "德国": 9,
    "Colombia": 10, "哥伦比亚": 10,
    # === 11-20 ===
    "Italy": 11, "意大利": 11, "Uruguay": 12, "乌拉圭": 12,
    "Croatia": 13, "克罗地亚": 13, "Morocco": 14, "摩洛哥": 14,
    "Japan": 15, "日本": 15, "Switzerland": 16, "瑞士": 16,
    "Senegal": 17, "塞内加尔": 17, "Mexico": 18, "墨西哥": 18,
    "USA": 19, "美国": 19, "Denmark": 20, "丹麦": 20,
    # === 21-40 ===
    "Austria": 21, "奥地利": 21, "Turkey": 22, "土耳其": 22,
    "South Korea": 23, "韩国": 23, "Australia": 24, "澳大利亚": 24,
    "Ecuador": 25, "厄瓜多尔": 25, "Serbia": 26, "塞尔维亚": 26,
    "Poland": 27, "波兰": 27, "Chile": 28, "智利": 28,
    "Canada": 29, "加拿大": 29, "Czechia": 30, "捷克": 30,
    "Algeria": 31, "阿尔及利亚": 31, "Egypt": 32, "埃及": 32,
    "Iran": 33, "伊朗": 33, "Saudi Arabia": 34, "沙特阿拉伯": 34,
    "Norway": 35, "挪威": 35, "Qatar": 36, "卡塔尔": 36,
    "Paraguay": 37, "巴拉圭": 37, "Scotland": 38, "苏格兰": 38,
    "Nigeria": 39, "尼日利亚": 39, "Ghana": 40, "加纳": 40,
    # === 41-60 ===
    "Sweden": 41, "瑞典": 41, "Peru": 42, "秘鲁": 42,
    "Venezuela": 43, "委内瑞拉": 43, "Tunisia": 44, "突尼斯": 44,
    "Romania": 45, "罗马尼亚": 45, "Ivory Coast": 46, "科特迪瓦": 46,
    "Uzbekistan": 47, "乌兹别克斯坦": 47, "Jamaica": 48, "牙买加": 48,
    "Costa Rica": 49, "哥斯达黎加": 49, "Panama": 50, "巴拿马": 50,
    "South Africa": 51, "南非": 51, "Honduras": 52, "洪都拉斯": 52,
    "Bosnia & Herzegovina": 53, "波黑": 53, "Iraq": 54, "伊拉克": 54,
    "China": 55, "中国": 55, "New Zealand": 56, "新西兰": 56,
    "Haiti": 57, "海地": 57, "DR Congo": 58, "民主刚果": 58,
    "Cameroon": 59, "喀麦隆": 59, "Jordon": 60, "约旦": 60,
    # === 61+ ===
    "Cape Verde": 61, "佛得角": 61, "Curacao": 62, "库拉索": 62,
}


def get_fifa_rank(team_name):
    """获取球队FIFA排名"""
    # 先精确匹配
    if team_name in FIFA_RANKINGS:
        return FIFA_RANKINGS[team_name]
    # 尝试去除空格
    cleaned = team_name.replace(" ", "")
    if cleaned in FIFA_RANKINGS:
        return FIFA_RANKINGS[cleaned]
    return 99  # 默认未排名


def get_elo(team_name):
    """获取球队ELO评级"""
    if team_name in ELO_2026:
        return ELO_2026[team_name]
    cleaned = team_name.replace(" ", "")
    if cleaned in ELO_2026:
        return ELO_2026[cleaned]
    return 1700  # 默认值


def get_strength_level(elo, fifa_rank):
    """根据ELO和FIFA排名确定实力等级描述"""
    if elo >= 1950 and fifa_rank <= 10:
        return "世界顶尖", "👑"
    elif elo >= 1850 and fifa_rank <= 20:
        return "世界强队", "⭐"
    elif elo >= 1750 and fifa_rank <= 40:
        return "世界中游", "🔷"
    else:
        return "挑战者/黑马", "⚡"


# ====================================================
# 核心数据采集函数
# ====================================================

def collect_full_data(target_date=None):
    """
    采集指定日期的完整比赛数据（一至四阶段纯数据）

    返回: {
        "meta": {target_date, collected_at, match_count},
        "matches": {
            "主队vs客队": {
                "stage_one": {...基础实力...},
                "stage_two": {...状态分析...},
                "stage_three": {...战术克制...},
                "stage_four": {...盘口赔率...}
            }
        }
    }
    """
    if target_date is None:
        target_date = bj_date_offset(2)

    bj_tz = timezone(timedelta(hours=8))
    now_bj = datetime.now(bj_tz)

    print(f"\n{'='*70}")
    print(f"  世界杯2026 数据采集器 v30.0")
    print(f"  目标日期: {target_date} (北京时间)")
    print(f"  采集时间: {now_bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间")
    print(f"{'='*70}\n")

    result = {
        "meta": {
            "target_date": target_date,
            "collected_at": now_bj.isoformat(),
            "timezone": "Asia/Shanghai",
            "version": "30.0",
        },
        "matches": {}
    }

    # ═══ Step 1: 获取比赛列表 ═══
    print("【Step 1/5】获取世界杯比赛列表...")
    fixtures = af_get_fixtures_by_date(target_date)
    print(f"  找到 {len(fixtures)} 场世界杯比赛")

    if not fixtures:
        print(f"  ⚠️ {target_date} 无世界杯比赛数据")
        result["meta"]["status"] = "no_matches"
        return result

    for fix in fixtures:
        home = fix["home"]
        away = fix["away"]
        mk = f"{home}vs{away}"
        print(f"\n  ▸ {home} vs {away}")

    # ═══ Step 2: 获取OddsPAPI赔率数据 ═══
    print(f"\n【Step 2/5】获取OddsPAPI.io(Pinnacle)世界杯赔率...")
    oddspapi_fixtures = oddspapi_get_wc_odds(bookmaker="pinnacle")
    participant_map = oddspapi_get_participants()
    print(f"  OddsPAPI: {len(oddspapi_fixtures)} 场赛事, {len(participant_map)} 个参赛方")

    # 按北京日期筛选
    odds_by_match = {}
    for fx in oddspapi_fixtures:
        try:
            st_str = fx.get("startTime", "")
            if not st_str:
                continue
            st_dt = datetime.fromisoformat(st_str.replace("Z", "+00:00"))
            st_bj = st_dt.astimezone(bj_tz)
            st_bj_date = st_bj.strftime("%Y-%m-%d")
            if st_bj_date == target_date:
                parsed = oddspapi_parse_fixture(fx, participant_map)
                if parsed and parsed.get("1x2"):
                    odds_by_match[parsed.get("fixtureId", "")] = parsed
                    p1 = parsed.get("home_name", "?")
                    p2 = parsed.get("away_name", "?")
                    odds_1x2 = parsed.get("1x2", {})
                    print(f"  ✅ {p1} vs {p2} | 欧赔: 主{odds_1x2.get('home','?')}/平{odds_1x2.get('draw','?')}/客{odds_1x2.get('away','?')}")
        except Exception as e:
            pass

    print(f"  匹配到 {len(odds_by_match)} 场当天的Pinnacle赔率")

    # ═══ Step 3: 逐场采集详细数据 ═══
    print(f"\n【Step 3/5】逐场采集API-FOOTBALL详细数据...")
    
    for i, fix in enumerate(fixtures):
        home = fix["home"]
        away = fix["away"]
        mk = f"{home}vs{away}"
        fixture_id = fix.get("fixture_id")
        home_id = fix.get("home_id")
        away_id = fix.get("away_id")

        print(f"\n  ┌─[{i+1}/{len(fixtures)}] {mk}")
        
        match_entry = {}

        # ========== 一、基础实力分析 ==========
        print(f"  │  📊 一、基础实力分析...")
        
        elo_h = get_elo(home)
        elo_a = get_elo(away)
        fifa_h = get_fifa_rank(home)
        fifa_a = get_fifa_rank(away)
        level_h, icon_h = get_strength_level(elo_h, fifa_h)
        level_a, icon_a = get_strength_level(elo_a, fifa_a)

        stage_one = {
            "home": {"name": home, "elo": elo_h, "fifa_rank": fifa_h, "strength_level": level_h, "icon": icon_h},
            "away": {"name": away, "elo": elo_a, "fifa_rank": fifa_a, "strength_level": level_a, "icon": icon_a},
            "elo_diff": elo_h - elo_a,
            "fifa_rank_diff": fifa_a - fifa_h,  # 排名差距(越小越强)
            "dominant_side": home if elo_h > elo_a else (away if elo_a > elo_h else "均势"),
        }

        # 球队统计 (API-FOOTBALL)
        if home_id:
            _wait_for_rate_limit()
            home_stats = af_get_team_stats(home_id)
            if home_stats:
                stage_one["home"]["stats"] = _extract_team_stats(home_stats)
        if away_id:
            _wait_for_rate_limit()
            away_stats = af_get_team_stats(away_id)
            if away_stats:
                stage_one["away"]["stats"] = _extract_team_stats(away_stats)

        match_entry["stage_one"] = stage_one

        # ========== 二、状态分析 ==========
        print(f"  │  🔄 二、状态分析...")

        stage_two = {
            "recent_form_home": [],
            "recent_form_away": [],
            "injuries": [],
            "players_home": [],
            "players_away": [],
        }

        # 近期比赛记录
        if home_id:
            _wait_for_rate_limit()
            recent_h = af_get_team_recent_fixtures(home_id, last=6)
            if recent_h:
                stage_two["recent_form_home"] = _extract_recent_form(recent_h, home)
        if away_id:
            _wait_for_rate_limit()
            recent_a = af_get_team_recent_fixtures(away_id, last=6)
            if recent_a:
                stage_two["recent_form_away"] = _extract_recent_form(recent_a, away)

        # 伤病信息
        if fixture_id:
            _wait_for_rate_limit()
            injuries = af_get_injuries(fixture_id)
            if injuries:
                stage_two["injuries"] = _extract_injuries(injuries)

        # 球员名单
        if home_id:
            _wait_for_rate_limit()
            players_h = af_get_players(home_id)
            if players_h:
                stage_two["players_home"] = _extract_players(players_h)
        if away_id:
            _wait_for_rate_limit()
            players_a = af_get_players(away_id)
            if players_a:
                stage_two["players_away"] = _extract_players(players_a)

        # 计算状态摘要
        form_h = stage_two["recent_form_home"]
        form_a = stage_two["recent_form_away"]
        stage_two["form_summary"] = {
            "home": _calc_form_summary(form_h),
            "away": _calc_form_summary(form_a),
        }

        match_entry["stage_two"] = stage_two

        # ========== 三、战术克制 ==========
        print(f"  │  ⚔️ 三、战术克制分析...")

        stage_three = {
            "formation_home": None,
            "formation_away": None,
            "tactic_note": None,
            "star_power_home": None,
            "star_power_away": None,
        }

        # 从球员名单推断阵型/星级力量
        players_h_list = stage_two.get("players_home", [])
        players_a_list = stage_two.get("players_away", [])
        
        if players_h_list:
            stage_three["star_power_home"] = _estimate_star_power(players_h_list, home)
        if players_a_list:
            stage_three["star_power_away"] = _estimate_star_power(players_a_list, away)

        match_entry["stage_three"] = stage_three

        # ========== 四、盘口与赔率分析 ==========
        print(f"  │  📈 四、盘口与赔率分析...")

        stage_four = {
            "oddspapi_pinnacle": {},
            "af_odds": {},
            "af_predictions": {},
            "h2h": [],
        }

        # OddsPAPI赔率 (通过时间匹配)
        fix_time = fix.get("time_utc", "")
        matched_odds = None
        for fid, odds in odds_by_match.items():
            ot = odds.get("startTime", "")
            if fix_time and ot:
                try:
                    ft_dt = datetime.fromisoformat(fix_time.replace("Z", "+00:00"))
                    ot_dt = datetime.fromisoformat(ot.replace("Z", "+00:00"))
                    diff = abs((ft_dt - ot_dt).total_seconds())
                    if diff < 7200:  # 2小时内匹配
                        matched_odds = odds
                        print(f"  │  ✅ OddsPAPI Pinnacle匹配成功 (差{diff/60:.0f}分钟)")
                        break
                except:
                    pass
        
        if matched_odds:
            stage_four["oddspapi_pinnacle"] = matched_odds

        # API-FOOTBALL赔率和预测
        if fixture_id:
            _wait_for_rate_limit()
            af_odds = af_get_odds(fixture_id)
            if af_odds:
                euro = parse_euro_odds(af_odds)
                if euro:
                    stage_four["af_odds"] = euro
            
            _wait_for_rate_limit()
            pred = af_get_predictions(fixture_id)
            if pred:
                stage_four["af_predictions"] = {
                    "advice": pred.get("predictions", {}).get("advice", ""),
                    "percent": pred.get("predictions", {}).get("percent", {}),
                    "winner": pred.get("predictions", {}).get("winner", {}).get("name", ""),
                    "comment": pred.get("predictions", {}).get("comment", ""),
                }

        # H2H历史交锋
        if home_id and away_id:
            _wait_for_rate_limit()
            h2h = af_get_h2h(home_id, away_id, last=5)
            if h2h:
                stage_four["h2h"] = _extract_h2h(h2h, home, away)

        match_entry["stage_four"] = stage_four

        # ========== 汇总本场比赛 ==========
        result["matches"][mk] = match_entry
        print(f"  └─✅ {mk} 数据采集完成")

    # ═══ Step 4: 元数据更新 ═══
    result["meta"]["match_count"] = len(result["matches"])
    result["meta"]["status"] = "success"
    has_pinnacle = any(
        m.get("stage_four", {}).get("oddspapi_pinnacle", {}).get("1x2")
        for m in result["matches"].values()
    )
    result["meta"]["has_pinnacle_odds"] = has_pinnacle

    print(f"\n{'='*70}")
    print(f"  ✅ 数据采集完成!")
    print(f"  日期: {target_date}")
    print(f"  场次: {len(result['matches'])}")
    print(f"  Pinnacle赔率: {'✅' if has_pinnacle else '❌'}")
    print(f"{'='*70}\n")

    return result


# ====================================================
# 数据提取辅助函数
# ====================================================

def _extract_team_stats(stats_raw):
    """从API-FOOTBALL统计中提取关键指标"""
    try:
        league = stats_raw.get("league", {})
        fixtures = stats_raw.get("fixtures", {})
        goals = stats_raw.get("goals", {}) if isinstance(stats_raw.get("goals"), dict) else {}
        biggest = stats_raw.get("biggest", {} if isinstance(stats_raw.get("biggest"), dict) else lambda: None)
        
        played = fixtures.get("played", 0)
        wins = fixtures.get("wins", 0)
        draws = fixtures.get("draws", 0)
        losses = fixtures.get("losses", 0)
        
        gf = goals.get("for", 0) if isinstance(goals, dict) else 0
        ga = goals.get("against", 0) if isinstance(goals, dict) else 0
        
        return {
            "played": played,
            "wins": wins, "draws": draws, "losses": losses,
            "points": wins * 3 + draws,
            "gf": gf, "ga": ga,
            "avg_gf": round(gf / max(played, 1), 2),
            "avg_ga": round(ga / max(played, 1), 2),
            "clean_sheets": getattr(biggest, 'get', lambda k: 0)("clean_sheet") if callable(getattr(biggest, 'get', None)) else 0,
            "failed_to_score": 0,
        }
    except Exception as e:
        return {"error": str(e), "raw_keys": list(stats_raw.keys()) if stats_raw else []}


def _extract_recent_form(fixtures_list, team_name):
    """提取近期比赛战绩为标准格式"""
    results = []
    for f in fixtures_list[:6]:
        teams = f.get("teams", {})
        home_t = teams.get("home", {}).get("name", "")
        away_t = teams.get("away", {}).get("name", "")
        goals = f.get("goals", {})
        home_g = goals.get("home", 0)
        away_g = goals.get("away", 0)
        status_short = f.get("status", {}).get("short", "")
        
        # 判断主队胜负
        is_home = (team_name == home_t)
        if is_home:
            opponent = away_t
            my_g, op_g = home_g, away_g
        else:
            opponent = home_t
            my_g, op_g = away_g, home_g
        
        if my_g > op_g:
            outcome = "W"
        elif my_g < op_g:
            outcome = "L"
        else:
            outcome = "D"
        
        # 只保留非友谊赛
        league_name = f.get("league", {}).get("name", "")
        
        results.append({
            "opponent": opponent,
            "home_away": "主场" if is_home else "客场",
            "score": f"{my_g}:{op_g}",
            "outcome": outcome,
            "league": league_name,
            "date": f.get("fixture", {}).get("date", "")[:10],
            "status": status_short,
        })
    
    return results


def _calc_form_summary(form_list):
    """计算状态摘要"""
    if not form_list:
        return {"record": "", "badge": "unknown", "wins": 0, "draws": 0, "losses": 0, 
                "gf": 0, "ga": 0, "form_string": ""}
    
    record_parts = []
    w = d = l = gf = ga = 0
    for f in form_list:
        o = f["outcome"]
        record_parts.append(o)
        if o == "W": w += 1
        elif o == "D": d += 1
        else: l += 1
        s = f["score"].split(":")
        gf += int(s[0]) if len(s) == 2 else 0
        ga += int(s[1]) if len(s) == 2 else 0
    
    total = w + d + l
    points_per_game = (w * 3 + d) / max(total, 1)
    
    # 状态徽章
    if points_per_game >= 2.0:
        badge = "hot"   # 🔥 状态火热
    elif points_per_game >= 1.5:
        badge = "good"  # 👍 状态良好
    elif points_per_game >= 1.0:
        badge = "ok"    # ➖ 状态一般
    else:
        badge = "poor"  # ↓ 状态低迷
    
    return {
        "record": "".join(record_parts),
        "badge": badge,
        "wins": w, "draws": d, "losses": l,
        "gf": gf, "ga": ga,
        "form_string": f"{w}胜{d}平{l}负",
        "ppg": round(points_per_game, 2),
    }


def _extract_injuries(injuries_list):
    """提取伤病信息"""
    result = []
    for inj in injuries_list[:15]:
        player = inj.get("player", {})
        team = inj.get("team", {})
        result.append({
            "player": player.get("name", ""),
            "team": team.get("name", ""),
            "reason": player.get("reason", ""),
            "status": player.get("status", ""),  # Injured / Doubtful / Suspended
            "position": player.get("position", ""),
        })
    return result


def _extract_players(players_list):
    """提取球员名单"""
    result = []
    for p in players_list[:30]:
        result.append({
            "name": p.get("name", ""),
            "position": p.get("position", ""),
            "age": p.get("age", ""),
            "number": p.get("number", ""),
            # API-FOOTBALL球员通常没有俱乐部信息，需要额外查询
            "club": "",
        })
    return result


def _estimate_star_power(player_list, team_name):
    """基于球员名单估算星级力量（粗略版本，本地AI会补充）"""
    total_players = len(player_list)
    positions = {}
    for p in player_list:
        pos = p.get("position", "?")
        positions[pos] = positions.get(pos, 0) + 1
    
    return {
        "total_squad_size": total_players,
        "positions": positions,
        # 注意：巨星名单/五大联赛人数/第二得分点 需要联网验证
        # 这里只提供基础数据骨架
        "note": "★ 星级力量详情需本地AI联网补充(Transfermarkt/SRC)",
    }


def _extract_h2h(h2h_list, home, away):
    """提取历史交锋"""
    result = []
    for h in h2h_list[:5]:
        teams = h.get("teams", {})
        ht = teams.get("home", {}).get("name", "")
        at = teams.get("away", {}).get("name", "")
        goals = h.get("goals", {})
        hg = goals.get("home", 0)
        ag = goals.get("away", 0)
        result.append({
            "home": ht, "away": at,
            "score": f"{hg}:{ag}",
            "date": h.get("fixture", {}).get("date", "")[:10],
        })
    return result


# ====================================================
# JSON输出与保存
# ====================================================

def save_json(data, output_dir=None):
    """保存JSON数据文件"""
    target_date = data["meta"]["target_date"]
    
    if output_dir is None:
        # 支持环境变量覆盖输出目录
        env_dir = os.environ.get("DATA_OUTPUT_DIR")
        if env_dir:
            output_dir = Path(env_dir)
        else:
            output_dir = SCRIPT_DIR.parent / "data"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / f"{target_date}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    size_kb = len(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')) // 1024
    print(f"  💾 JSON已保存: {filepath} ({sizeKB}KB)")
    return filepath


def list_available_dates(days_ahead=14):
    """列出近期有世界杯比赛的日期"""
    bj_tz = timezone(timedelta(hours=8))
    today = datetime.now(bj_tz).strftime("%Y-%m-%d")
    
    print(f"扫描未来{days_ahead}天的世界杯比赛...\n")
    
    found_dates = []
    for i in range(1, days_ahead + 1):
        d = (datetime.now(bj_tz) + timedelta(days=i)).strftime("%Y-%m-%d")
        fixtures = af_get_fixtures_by_date(d)
        wc_count = len(fixtures)
        if wc_count > 0:
            found_dates.append((d, wc_count))
            matches_str = ", ".join([f"{f['home']}vs{f['away']}" for f in fixtures[:4]])
            print(f"  {d}: {wc_count}场比赛 → {matches_str}")
            if wc_count > 4:
                print(f"       ... 还有{wc_count-4}场")
    
    if not found_dates:
        print("  未找到任何世界杯比赛")
    else:
        print(f"\n共发现 {len(found_dates)} 个比赛日")
    
    return found_dates


# ====================================================
# 主入口
# ====================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="世界杯2026数据采集器 v30.0")
    parser.add_argument("date", nargs="?", default=None, help="目标日期 YYYY-MM-DD (默认后天)")
    parser.add_argument("--list-dates", action="store_true", help="列出近期有比赛的日期")
    parser.add_argument("--output-dir", default=None, help="自定义输出目录")
    args = parser.parse_args()
    
    if args.list_dates:
        list_available_dates()
        sys.exit(0)
    
    target_date = args.date or bj_date_offset(2)
    
    # 采集数据
    data = collect_full_data(target_date)
    
    # 保存JSON
    if data["meta"].get("status") == "success":
        save_json(data, args.output_dir)
        
        # 打印数据概览
        print("\n📋 数据概览:")
        for mk, md in data["matches"].items():
            so = md.get("stage_one", {})
            sf = md.get("stage_four", {})
            pinnacle = sf.get("oddspapi_pinnacle", {})
            odds_1x2 = pinnacle.get("1x2", {})
            
            h_info = so.get("home", {})
            a_info = so.get("away", {})
            print(f"  • {mk}")
            print(f"    实力: ELO {h_info.get('elo','?')}({h_info.get('strength_level','?')}) vs "
                  f"ELO {a_info.get('elo','?')}({a_info.get('strength_level','?')}) | "
                  f"FIFA #{h_info.get('fifa_rank','?')} vs #{a_info.get('fifa_rank','?')}")
            if odds_1x2:
                print(f"    赔率: 主{odds_1x2.get('home','?')}/平{odds_1x2.get('draw','?')}/客{odds_1x2.get('away','?')}")
            
            st2 = md.get("stage_two", {})
            fs_h = st2.get("form_summary", {}).get("home", {})
            fs_a = st2.get("form_summary", {}).get("away", {})
            print(f"    状态: 主队{fs_h.get('form_string','?')}({fs_h.get('badge','?')}) vs "
                  f"客队{fs_a.get('form_string','?')}({fs_a.get('badge','?')})")
            
            injuries = st2.get("injuries", [])
            if injuries:
                print(f"    伤病: {len(injuries)}人")
            else:
                print(f"    伤病: ✅ 全主力健康(暂无API伤病数据)")
    else:
        print(f"\n⚠️ {target_date} 无数据")

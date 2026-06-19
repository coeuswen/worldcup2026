"""
世界杯2026 数据获取API封装器
职业足球量化分析师 + 博彩风控模型 v29.0
"""
import requests
import json
import time
from datetime import datetime, timedelta, timezone
import os

# ====================================================
# API 配置
# ====================================================
APIFOOTBALL_KEY = os.environ.get("APIFOOTBALL_KEY", "b91f9694b51423ae721ab18c1b43969d")
ODDS_KEY = os.environ.get("ODDS_KEY", "bc1d16ef05a8e298a2c393ac6417298c48831416bf76852686ab2b756d378026")
ODDSPAPI_KEY = os.environ.get("ODDSPAPI_KEY", "a05cd7c7-377d-46e7-882c-ea57ced180ee")
TAVILY_KEY = os.environ.get("TAVILY_KEY", "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")

APIFOOTBALL_BASE = "https://v3.football.api-sports.io"
ODDS_BASE = "https://api.odds-api.io/v3"
ODDSPAPI_BASE = "https://api.oddspapi.io/v4"
ODDSPAPI_WC_TOURNAMENT_ID = 16  # FIFA World Cup

# ====================================================
# 工具函数
# ====================================================
def bj_today():
    """获取北京时间今天日期"""
    bj_tz = timezone(timedelta(hours=8))
    return datetime.now(bj_tz).strftime("%Y-%m-%d")

def bj_date_offset(days=2):
    """获取北京时间 +N 天的日期"""
    bj_tz = timezone(timedelta(hours=8))
    return (datetime.now(bj_tz) + timedelta(days=days)).strftime("%Y-%m-%d")

# 全局限流控制（API-FOOTBALL免费层: 10次/分钟）
_request_timestamps = []
RATE_LIMIT_PER_MINUTE = 8  # 安全值，留2次余量

def _wait_for_rate_limit():
    """确保不超过每分钟请求限制"""
    now = time.time()
    # 清理60秒前的记录
    global _request_timestamps
    _request_timestamps = [t for t in _request_timestamps if now - t < 60]
    
    if len(_request_timestamps) >= RATE_LIMIT_PER_MINUTE:
        # 需要等待最早请求过期
        wait_time = 60 - (now - _request_timestamps[0]) + 1
        if wait_time > 0:
            print(f"  ⏳ 限流等待 {wait_time:.0f}s (已用 {len(_request_timestamps)}/{RATE_LIMIT_PER_MINUTE})")
            time.sleep(wait_time)
    
    now = time.time()
    _request_timestamps.append(now)

def safe_get(url, headers=None, params=None, timeout=15, retry=2):
    """带限流和重试的GET请求"""
    for attempt in range(retry + 1):
        _wait_for_rate_limit()
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:  # 限流
                print(f"  [429 限流] 等待60秒...")
                time.sleep(60)
                continue
            elif resp.status_code == 403:
                print(f"  [403 禁止访问] {url}")
                return None
            else:
                print(f"  [HTTP {resp.status_code}] {url}")
                return None
        except requests.Timeout:
            print(f"  [Timeout] {url} (attempt {attempt+1})")
            time.sleep(2)
        except Exception as e:
            print(f"  [Error] {url}: {e}")
            return None
    return None

# ====================================================
# API-FOOTBALL 数据获取
# ====================================================
AF_HEADERS = {"x-apisports-key": APIFOOTBALL_KEY}

def af_get_fixtures_by_date(date_str):
    """
    获取指定日期的世界杯比赛
    date_str: "YYYY-MM-DD"
    返回: [{"home": "捷克", "away": "南非", "fixture_id": 123, "time_utc": "...", "venue": "..."}]
    """
    data = safe_get(
        f"{APIFOOTBALL_BASE}/fixtures",
        headers=AF_HEADERS,
        params={"date": date_str, "timezone": "Asia/Shanghai"}
    )
    if not data:
        return []
    
    results = []
    for r in data.get("response", []):
        league = r.get("league", {})
        if "World Cup" not in league.get("name", ""):
            continue
        fixture = r.get("fixture", {})
        teams = r.get("teams", {})
        venue = fixture.get("venue", {})
        results.append({
            "fixture_id": fixture.get("id"),
            "home": teams.get("home", {}).get("name", ""),
            "home_id": teams.get("home", {}).get("id"),
            "away": teams.get("away", {}).get("name", ""),
            "away_id": teams.get("away", {}).get("id"),
            "time_utc": fixture.get("date", ""),
            "venue": venue.get("name", ""),
            "city": venue.get("city", ""),
            "league_round": league.get("round", ""),
            "status": fixture.get("status", {}).get("short", ""),
        })
    return results

def af_get_team_stats(team_id, league_id=1, season=2026):
    """获取球队赛季统计"""
    data = safe_get(
        f"{APIFOOTBALL_BASE}/teams/statistics",
        headers=AF_HEADERS,
        params={"team": team_id, "league": league_id, "season": season}
    )
    if not data:
        return {}
    return data.get("response", {})

def af_get_team_recent_fixtures(team_id, last=10):
    """获取球队最近N场比赛结果（用于计算FORM）"""
    data = safe_get(
        f"{APIFOOTBALL_BASE}/fixtures",
        headers=AF_HEADERS,
        params={"team": team_id, "last": last, "season": 2026}
    )
    if not data:
        return []
    return data.get("response", [])

def af_get_players(team_id, season=2026):
    """获取球队球员名单"""
    data = safe_get(
        f"{APIFOOTBALL_BASE}/players/squads",
        headers=AF_HEADERS,
        params={"team": team_id}
    )
    if not data:
        return []
    resp = data.get("response", [])
    if resp:
        return resp[0].get("players", [])
    return []

def af_get_injuries(fixture_id):
    """获取比赛伤病信息"""
    data = safe_get(
        f"{APIFOOTBALL_BASE}/injuries",
        headers=AF_HEADERS,
        params={"fixture": fixture_id}
    )
    if not data:
        return []
    return data.get("response", [])

def af_get_h2h(home_id, away_id, last=10):
    """获取两队历史对决记录"""
    data = safe_get(
        f"{APIFOOTBALL_BASE}/fixtures/headtohead",
        headers=AF_HEADERS,
        params={"h2h": f"{home_id}-{away_id}", "last": last}
    )
    if not data:
        return []
    return data.get("response", [])

def af_get_standings(league_id=1, season=2026):
    """获取积分榜"""
    data = safe_get(
        f"{APIFOOTBALL_BASE}/standings",
        headers=AF_HEADERS,
        params={"league": league_id, "season": season}
    )
    if not data:
        return []
    resp = data.get("response", [])
    if resp:
        return resp[0].get("league", {}).get("standings", [])
    return []

def af_get_odds(fixture_id):
    """获取比赛赔率（API-FOOTBALL自带赔率）"""
    data = safe_get(
        f"{APIFOOTBALL_BASE}/odds",
        headers=AF_HEADERS,
        params={"fixture": fixture_id}
    )
    if not data:
        return {}
    resp = data.get("response", [])
    return resp[0] if resp else {}

def af_get_predictions(fixture_id):
    """获取API-FOOTBALL的预测（包含胜率、建议）"""
    data = safe_get(
        f"{APIFOOTBALL_BASE}/predictions",
        headers=AF_HEADERS,
        params={"fixture": fixture_id}
    )
    if not data:
        return {}
    resp = data.get("response", [])
    return resp[0] if resp else {}

# ====================================================
# Odds API 数据获取
# ====================================================
def odds_get_worldcup_events():
    """获取Odds API中的世界杯赛事"""
    data = safe_get(
        f"{ODDS_BASE}/events",
        params={"apiKey": ODDS_KEY, "sport": "football", "limit": 200}
    )
    if not isinstance(data, list):
        return []
    wc = [e for e in data if "world cup" in e.get("league", {}).get("name", "").lower() or 
           "fifa world cup" in e.get("league", {}).get("name", "").lower()]
    return wc

def odds_get_event_odds(event_id, bookmakers="Bet365,William Hill,Unibet,Pinnacle"):
    """获取赛事的多书商赔率"""
    data = safe_get(
        f"{ODDS_BASE}/odds",
        params={"apiKey": ODDS_KEY, "eventId": event_id, "bookmakers": bookmakers},
        timeout=15
    )
    return data or {}

# ====================================================
# OddsPAPI.io 数据获取 (独立限流: 1秒/请求)
# ====================================================
_oddsapi_last_request = 0

def _oddspapi_get(url, params, timeout=20):
    """OddsPAPI专用GET请求（1秒限流，不消耗API-FOOTBALL配额）"""
    global _oddsapi_last_request
    now = time.time()
    elapsed = now - _oddsapi_last_request
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    
    params_with_key = {**params, "apiKey": ODDSPAPI_KEY}
    try:
        resp = requests.get(url, params=params_with_key, timeout=timeout)
        _oddsapi_last_request = time.time()
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            retry_after = float(resp.json().get("error", {}).get("retryMs", 1000)) / 1000
            print(f"  [OddsPAPI 429] 等待 {retry_after}s...")
            time.sleep(retry_after + 0.2)
            return _oddspapi_get(url, params, timeout)
        else:
            print(f"  [OddsPAPI {resp.status_code}] {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  [OddsPAPI Error] {e}")
        return None

def oddspapi_get_wc_odds(bookmaker="pinnacle"):
    """
    获取世界杯全部赛事的Pinnacle赔率
    返回: [{fixtureId, startTime, participant1Id, participant2Id, odds: {...}}, ...]
    """
    data = _oddspapi_get(
        f"{ODDSPAPI_BASE}/odds-by-tournaments",
        params={
            "tournamentIds": str(ODDSPAPI_WC_TOURNAMENT_ID),
            "bookmaker": bookmaker,
            "oddsFormat": "decimal",
            "verbosity": "3"
        }
    )
    if not isinstance(data, list):
        return []
    return data

def oddspapi_get_participants():
    """获取世界杯参赛球队ID→名称映射"""
    data = _oddspapi_get(
        f"{ODDSPAPI_BASE}/participants",
        params={"sportId": "10", "tournamentIds": str(ODDSPAPI_WC_TOURNAMENT_ID)}
    )
    if not isinstance(data, dict):
        return {}
    return data

def _extract_market_price(market_data, outcome_idx="0"):
    """从market数据中提取price"""
    outcomes = market_data.get("outcomes", {})
    for oid, odata in outcomes.items():
        player = odata.get("players", {}).get(outcome_idx, {})
        if "price" in player:
            return player["price"], player.get("bookmakerOutcomeId", "")
    return None, ""

def oddspapi_parse_fixture(fixture_data, participant_map=None):
    """
    解析单场比赛的OddsPAPI赔率数据
    返回结构化赔率: {1x2, ah_main, ou_main, btts, ou_15, dc, all_ah, all_ou}
    """
    if not fixture_data:
        return {}
    
    bk_odds = fixture_data.get("bookmakerOdds", {})
    if not bk_odds:
        return {}
    
    # 取第一个bookmaker
    bk_name = list(bk_odds.keys())[0]
    bk_data = bk_odds[bk_name]
    markets = bk_data.get("markets", {})
    
    result = {
        "bookmaker": bk_name,
        "participant1Id": fixture_data.get("participant1Id"),
        "participant2Id": fixture_data.get("participant2Id"),
        "startTime": fixture_data.get("startTime"),
        "fixtureId": fixture_data.get("fixtureId"),
    }
    
    if participant_map:
        p1id = str(fixture_data.get("participant1Id", ""))
        p2id = str(fixture_data.get("participant2Id", ""))
        result["home_name"] = participant_map.get(p1id, f"Team-{p1id}")
        result["away_name"] = participant_map.get(p2id, f"Team-{p2id}")
    
    # market 101: 1X2 (胜平负/欧赔)
    if "101" in markets:
        m = markets["101"]
        home_price, _ = _extract_market_price_for_outcome(m, "101")
        draw_price, _ = _extract_market_price_for_outcome(m, "102")
        away_price, _ = _extract_market_price_for_outcome(m, "103")
        if home_price and draw_price and away_price:
            result["1x2"] = {"home": home_price, "draw": draw_price, "away": away_price}
    
    # market 104: BTTS (双方进球)
    if "104" in markets:
        m = markets["104"]
        yes_price, _ = _extract_market_price_for_outcome(m, "104")
        no_price, _ = _extract_market_price_for_outcome(m, "105")
        if yes_price and no_price:
            result["btts"] = {"yes": yes_price, "no": no_price}
    
    # market 1010: O/U 2.5 (大小球主线)
    if "1010" in markets:
        m = markets["1010"]
        over_price, _ = _extract_market_price_for_outcome(m, "1010")
        under_price, _ = _extract_market_price_for_outcome(m, "1011")  # 可能是不同的outcome key
        if not over_price:
            over_price, over_label = _extract_market_price_by_label(m, "over")
            under_price, under_label = _extract_market_price_by_label(m, "under")
        if over_price and under_price:
            result["ou25"] = {"over": over_price, "under": under_price}
    
    # market 108: O/U 1.5
    if "108" in markets:
        m = markets["108"]
        over_price, _ = _extract_market_price_by_label(m, "over")
        under_price, _ = _extract_market_price_by_label(m, "under")
        if over_price and under_price:
            result["ou15"] = {"over": over_price, "under": under_price}
    
    # 亚洲盘主线: 找 -0.5, -1.0, -1.5 等常见盘口
    ah_lines = {}
    for mid, mdata in markets.items():
        # 亚盘market的outcome label格式: "-0.5/home", "-1.0/away" 等
        for oid, odata in mdata.get("outcomes", {}).items():
            player = odata.get("players", {}).get("0", {})
            label = player.get("bookmakerOutcomeId", "")
            price = player.get("price")
            if price and "/" in label:
                try:
                    line_str, side = label.split("/")
                    line = float(line_str)
                    if side in ("home", "away") and line in [-2.0, -1.5, -1.0, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]:
                        key = f"{line}"
                        if key not in ah_lines:
                            ah_lines[key] = {}
                        ah_lines[key][side] = price
                except (ValueError, IndexError):
                    pass
    
    # 选主盘（最接近-0.5或-1.0的）
    if ah_lines:
        # 找最有意义的盘口
        for preferred in ["-0.5", "-1.0", "-0.75", "-1.5", "0", "0.25", "-0.25"]:
            if preferred in ah_lines and "home" in ah_lines[preferred] and "away" in ah_lines[preferred]:
                result["ah_main"] = {
                    "line": float(preferred),
                    "home": ah_lines[preferred]["home"],
                    "away": ah_lines[preferred]["away"]
                }
                break
        result["all_ah"] = ah_lines
    
    # 大小球各盘口
    ou_lines = {}
    for mid, mdata in markets.items():
        for oid, odata in mdata.get("outcomes", {}).items():
            player = odata.get("players", {}).get("0", {})
            label = player.get("bookmakerOutcomeId", "")
            price = player.get("price")
            if price and "/" in label:
                try:
                    line_str, side = label.split("/")
                    if side in ("over", "under"):
                        line = float(line_str)
                        key = f"{line}"
                        if key not in ou_lines:
                            ou_lines[key] = {}
                        ou_lines[key][side] = price
                except (ValueError, IndexError):
                    pass
    if ou_lines:
        result["all_ou"] = ou_lines
    
    # 双重机会 (market 10208)
    if "10208" in markets:
        m = markets["10208"]
        home_or_draw, _ = _extract_market_price_by_label(m, "home")
        draw_or_away, _ = _extract_market_price_by_label(m, "away")
        # 实际上是 1X, X2, 12
        for oid, odata in m.get("outcomes", {}).items():
            player = odata.get("players", {}).get("0", {})
            label = player.get("bookmakerOutcomeId", "")
            price = player.get("price")
            if price:
                if label == "home":
                    result.setdefault("dc", {})["1x"] = price
                elif label == "draw":
                    result.setdefault("dc", {})["x2"] = price
                elif label == "away":
                    result.setdefault("dc", {})["12"] = price
    
    return result

def _extract_market_price_for_outcome(market_data, outcome_id):
    """从指定outcome ID提取price"""
    outcomes = market_data.get("outcomes", {})
    if outcome_id in outcomes:
        player = outcomes[outcome_id].get("players", {}).get("0", {})
        return player.get("price"), player.get("bookmakerOutcomeId", "")
    return None, ""

def _extract_market_price_by_label(market_data, label_keyword):
    """通过label关键字提取price (如 'over', 'under', 'home', 'away', 'draw')"""
    for oid, odata in market_data.get("outcomes", {}).items():
        player = odata.get("players", {}).get("0", {})
        label = player.get("bookmakerOutcomeId", "")
        if label_keyword in label.lower():
            return player.get("price"), label
    return None, ""

# ====================================================
# 综合数据采集器
# ====================================================
def collect_match_data(target_date=None):
    """
    采集指定日期的所有世界杯比赛数据
    target_date: "YYYY-MM-DD"，默认为北京时间后天
    返回: {match_key: {...完整数据...}, ...}
    
    优化: API-FOOTBALL免费层8次/分钟，优先获取关键数据
          OddsPAPI独立限流(1秒/请求)，获取欧赔/亚盘/大小球
    """
    if target_date is None:
        target_date = bj_date_offset(2)
    
    print(f"\n{'='*60}")
    print(f"数据采集: {target_date}")
    print(f"{'='*60}")
    
    # Step 1: 获取比赛列表 (1次API-FOOTBALL调用)
    print("\n[1/4] 获取比赛列表...")
    fixtures = af_get_fixtures_by_date(target_date)
    print(f"  找到 {len(fixtures)} 场世界杯比赛")
    
    if not fixtures:
        print("  ⚠️ 当天无世界杯比赛")
        return {}
    
    # Step 2: 一次性获取OddsPAPI世界杯全部赔率 (2次OddsPAPI调用，不消耗API-FOOTBALL配额)
    print("\n[2/4] 获取OddsPAPI世界杯赔率...")
    oddspapi_fixtures = oddspapi_get_wc_odds(bookmaker="pinnacle")
    participant_map = oddspapi_get_participants()
    print(f"  OddsPAPI: {len(oddspapi_fixtures)} 场赛事, {len(participant_map)} 个参赛方")
    
    # 按日期筛选OddsPAPI比赛 (startTime是UTC)
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    target_start = target_dt - timedelta(hours=12)  # UTC比北京晚8小时，留余量
    target_end = target_dt + timedelta(hours=12)
    
    # 解析并匹配赔率
    odds_by_fixture = {}
    for fx in oddspapi_fixtures:
        try:
            st = datetime.fromisoformat(fx.get("startTime", "").replace("Z", "+00:00"))
            st_naive = st.replace(tzinfo=None)
            # 转为北京时间
            bj_tz = timezone(timedelta(hours=8))
            st_bj = st.astimezone(bj_tz)
            st_bj_str = st_bj.strftime("%Y-%m-%d")
            
            if st_bj_str == target_date:
                parsed = oddspapi_parse_fixture(fx, participant_map)
                if parsed:
                    # 用startTime作为匹配key
                    odds_by_fixture[fx["fixtureId"]] = parsed
                    print(f"  ✅ {parsed.get('home_name','?')} vs {parsed.get('away_name','?')} | 1X2={parsed.get('1x2','无')}")
        except Exception as e:
            pass
    
    print(f"  匹配到 {len(odds_by_fixture)} 场当天的赔率数据")
    
    # Step 3: 逐场采集API-FOOTBALL关键数据 (每场2次调用: predictions + odds)
    all_data = {}
    for i, fix in enumerate(fixtures):
        home = fix["home"]
        away = fix["away"]
        mk = f"{home}vs{away}"
        print(f"\n[3/4] 采集 {mk} ({i+1}/{len(fixtures)})...")
        
        match_data = {
            "fixture": fix,
            "home_stats": {},
            "away_stats": {},
            "h2h": [],
            "home_players": [],
            "away_players": [],
            "injuries": [],
            "odds_af": {},
            "odds_oddspapi": {},
            "predictions": {},
        }
        
        # 优先级1: 预测数据（含胜率/建议）— API-FOOTBALL
        if fix["fixture_id"]:
            match_data["predictions"] = af_get_predictions(fix["fixture_id"])
        
        # 优先级2: 赔率数据 — API-FOOTBALL
        if fix["fixture_id"]:
            match_data["odds_af"] = af_get_odds(fix["fixture_id"])
        
        # 优先级3: OddsPAPI赔率（通过startTime匹配）
        fix_time = fix.get("time_utc", "")
        for fid, odds in odds_by_fixture.items():
            odds_time = odds.get("startTime", "")
            # 模糊匹配时间（允许时差）
            if fix_time and odds_time:
                try:
                    ft = fix_time.replace("Z", "+00:00")
                    ot = odds_time.replace("Z", "+00:00")
                    ft_dt = datetime.fromisoformat(ft)
                    ot_dt = datetime.fromisoformat(ot)
                    diff = abs((ft_dt - ot_dt).total_seconds())
                    if diff < 7200:  # 2小时内
                        match_data["odds_oddspapi"] = odds
                        print(f"    OddsPAPI匹配成功 (时间差{diff/60:.0f}分钟)")
                        break
                except:
                    pass
        
        # 优先级4: 伤病信息（如有余量）
        if fix["fixture_id"] and len(_request_timestamps) < RATE_LIMIT_PER_MINUTE * 3:
            match_data["injuries"] = af_get_injuries(fix["fixture_id"])
        
        all_data[mk] = match_data
    
    print(f"\n[4/4] ✅ 数据采集完成: {len(all_data)} 场比赛")
    return all_data

# ====================================================
# 数据解析工具
# ====================================================
def parse_euro_odds(odds_data):
    """
    从API-FOOTBALL赔率数据中提取欧赔（胜/平/负）
    返回: {"home": 1.85, "draw": 3.40, "away": 2.10} 或 None
    """
    if not odds_data:
        return None
    
    bookmakers_list = odds_data.get("bookmakers", [])
    for bm in bookmakers_list:
        bm_name = bm.get("name", "")
        for bet in bm.get("bets", []):
            if bet.get("name") in ["Match Winner", "1X2"]:
                values = bet.get("values", [])
                result = {}
                for v in values:
                    val = v.get("value", "")
                    odd = float(v.get("odd", 0))
                    if val == "Home":
                        result["home"] = odd
                    elif val == "Draw":
                        result["draw"] = odd
                    elif val == "Away":
                        result["away"] = odd
                if len(result) == 3:
                    return result
    return None

def parse_asian_handicap(odds_data):
    """从API-FOOTBALL赔率数据中提取亚盘"""
    if not odds_data:
        return None
    
    for bm in odds_data.get("bookmakers", []):
        for bet in bm.get("bets", []):
            if "Asian Handicap" in bet.get("name", ""):
                values = bet.get("values", [])
                return {"raw": values[:4]}
    return None

def odds_to_prob(home_odds, draw_odds, away_odds):
    """
    赔率转真实概率（去除庄家抽水）
    返回: {"home": 0.52, "draw": 0.26, "away": 0.22}
    """
    raw_h = 1 / home_odds
    raw_d = 1 / draw_odds
    raw_a = 1 / away_odds
    total = raw_h + raw_d + raw_a
    return {
        "home": round(raw_h / total, 4),
        "draw": round(raw_d / total, 4),
        "away": round(raw_a / total, 4),
        "overround": round((total - 1) * 100, 2)  # 庄家抽水%
    }

def compute_elo_prob(elo_home, elo_away):
    """
    ELO评级计算胜率（含主场优势+60ELO）
    返回: {"home": 0.55, "draw": 0.25, "away": 0.20}
    """
    # 世界杯中性场地，主场优势减半
    elo_diff = elo_home - elo_away + 30  # 中性场地30分优势
    
    # 胜率（两队）
    home_win_prob = 1 / (1 + 10 ** (-elo_diff / 400))
    
    # 平局概率（基于ELO差距）
    elo_abs = abs(elo_diff)
    draw_prob = max(0.12, 0.28 - elo_abs * 0.0008)
    
    # 重新分配
    home_prob = home_win_prob * (1 - draw_prob)
    away_prob = (1 - home_win_prob) * (1 - draw_prob)
    
    return {
        "home": round(home_prob, 4),
        "draw": round(draw_prob, 4),
        "away": round(away_prob, 4)
    }

def blended_prob(euro_prob, elo_prob, weight_euro=0.6, weight_elo=0.4):
    """融合欧赔概率和ELO概率"""
    return {
        "home": round(euro_prob["home"] * weight_euro + elo_prob["home"] * weight_elo, 4),
        "draw": round(euro_prob["draw"] * weight_euro + elo_prob["draw"] * weight_elo, 4),
        "away": round(euro_prob["away"] * weight_euro + elo_prob["away"] * weight_elo, 4),
    }

def poisson_btts(xg_home, xg_away):
    """
    泊松分布计算BTTS和大小球概率
    """
    import math
    def poisson_prob(k, lam):
        return (lam**k) * math.exp(-lam) / math.factorial(k)
    
    # 计算各比分概率矩阵
    scores = {}
    for h in range(6):
        for a in range(6):
            scores[(h, a)] = poisson_prob(h, xg_home) * poisson_prob(a, xg_away)
    
    # BTTS
    btts = sum(p for (h, a), p in scores.items() if h > 0 and a > 0)
    
    # 大于2.5球
    over25 = sum(p for (h, a), p in scores.items() if h + a > 2)
    
    # 最可能比分（前5）
    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "btts": round(btts, 4),
        "over25": round(over25, 4),
        "under25": round(1 - over25, 4),
        "top_scores": [(f"{h}:{a}", round(p*100, 2)) for (h,a), p in top_scores]
    }

# ====================================================
# 主程序
# ====================================================
if __name__ == "__main__":
    import sys
    
    # 可传入日期参数，默认为后天
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = bj_date_offset(2)
    
    print(f"目标日期: {target_date}")
    
    # 采集数据
    match_data = collect_match_data(target_date)
    
    # 保存到JSON
    output_path = f"F:/works/worldcup/2026-world-cup-predictor-3.3.7/.workbuddy/data/raw_{target_date}.json"
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(match_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✅ 数据已保存至: {output_path}")

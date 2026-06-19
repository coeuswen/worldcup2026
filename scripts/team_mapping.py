#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
2026世界杯 48支球队 英文→中文名称映射表
包含 ELO 评级 + FIFA 排名 (2026年6月)

使用方法:
  from team_mapping import TEAM_CN, ELO_2026, FIFA_RANKINGS, get_team_info
  name_cn = TEAM_CN.get("Spain", "西班牙")  # 英文→中文
  elo = ELO_2026.get("西班牙", 1600)  # 中文查ELO
  fifa = FIFA_RANKINGS.get("Spain", 99)  # 英文查FIFA rank
"""

# ====================================================
# 英文→中文名称映射 (48支参赛队 + 补充)
# ====================================================
TEAM_CN = {
    # Group A
    "Mexico": "墨西哥", "South Africa": "南非",
    "South Korea": "韩国", "Korea Republic": "韩国",
    "Czech Republic": "捷克", "Czechia": "捷克",
    "Denmark": "丹麦", "North Macedonia": "北马其顿",
    "Republic of Ireland": "爱尔兰", "Ireland": "爱尔兰",
    
    # Group B
    "Canada": "加拿大",
    "Bosnia and Herzegovina": "波黑", "Bosnia & Herzegovina": "波黑",
    "Italy": "意大利", "Northern Ireland": "北爱尔兰",
    "Wales": "威尔士", "Qatar": "卡塔尔", "Switzerland": "瑞士",
    
    # Group C
    "Brazil": "巴西", "Morocco": "摩洛哥",
    "Haiti": "海地", "Scotland": "苏格兰",
    
    # Group D
    "United States": "美国", "USA": "美国",
    "Paraguay": "巴拉圭", "Australia": "澳大利亚",
    "Turkey": "土耳其", "Türkiye": "土耳其",
    "Kosovo": "科索沃", "Romania": "罗马尼亚",
    "Slovakia": "斯洛伐克",
    
    # Group E
    "Germany": "德国", "Curaçao": "库拉索",
    "Ecuador": "厄瓜多尔", "Côte d'Ivoire": "科特迪瓦",
    "Ivory Coast": "科特迪瓦",
    
    # Group F
    "Netherlands": "荷兰", "Japan": "日本",
    "Sweden": "瑞典", "Tunisia": "突尼斯",
    "Albania": "阿尔巴尼亚", "Poland": "波兰",
    "Ukraine": "乌克兰",
    
    # Group G
    "Belgium": "比利时", "Egypt": "埃及",
    "Iran": "伊朗", "IR Iran": "伊朗",
    "New Zealand": "新西兰",
    
    # Group H
    "Spain": "西班牙", "Saudi Arabia": "沙特阿拉伯",
    "Uruguay": "乌拉圭", "Cape Verde": "佛得角",
    "Cape Verde Islands": "佛得角", "Cabo Verde": "佛得角",
    
    # Group I
    "France": "法国", "Senegal": "塞内加尔",
    "Norway": "挪威", "Iraq": "伊拉克",
    "Bolivia": "玻利维亚", "Suriname": "苏里南",
    
    # Group J
    "Argentina": "阿根廷", "Algeria": "阿尔及利亚",
    "Austria": "奥地利", "Jordan": "约旦",
    
    # Group K
    "Portugal": "葡萄牙", "Colombia": "哥伦比亚",
    "Uzbekistan": "乌兹别克斯坦",
    "Congo DR": "民主刚果", "Jamaica": "牙买加",
    "New Caledonia": "新喀里多尼亚",
    
    # Group L
    "England": "英格兰", "Croatia": "克罗地亚",
    "Ghana": "加纳", "Panama": "巴拿马",
    
    # Additional national teams (may appear in similar references)
    "Serbia": "塞尔维亚", "Chile": "智利",
    "Nigeria": "尼日利亚", "Cameroon": "喀麦隆",
    "Greece": "希腊", "Hungary": "匈牙利",
    "Russia": "俄罗斯", "Venezuela": "委内瑞拉",
    "Peru": "秘鲁", "Costa Rica": "哥斯达黎加",
    "Finland": "芬兰", "Norway": "挪威",
    "Bulgaria": "保加利亚",
}

# ====================================================
# ELO 评级 (2026年6月)
# ====================================================
ELO_2026 = {
    # 英文key
    "Brazil": 2080, "France": 2054, "England": 2030, "Argentina": 2025,
    "Portugal": 2015, "Spain": 2010, "Netherlands": 2000, "Germany": 1995,
    "Belgium": 1975, "Croatia": 1960, "Italy": 1950, "Uruguay": 1940,
    "USA": 1920, "Mexico": 1910, "Colombia": 1900, "Senegal": 1895,
    "Morocco": 1890, "Japan": 1880, "Switzerland": 1870, "Denmark": 1865,
    "Australia": 1855, "South Korea": 1850, "Ecuador": 1840, "Serbia": 1835,
    "Czechia": 1830, "Austria": 1825, "Turkey": 1820, "Poland": 1810,
    "Sweden": 1780, "Chile": 1800, "Canada": 1795, "Algeria": 1790,
    "Egypt": 1785, "Ivory Coast": 1750, "Tunisia": 1700, "Nigeria": 1735,
    "Iran": 1770, "Saudi Arabia": 1760, "Qatar": 1730, "South Africa": 1720,
    "Paraguay": 1715, "Haiti": 1680, "Bosnia & Herzegovina": 1760,
    "Scotland": 1795, "Norway": 1790, "Greece": 1720, "Cameroon": 1710,
    "Wales": 1740, "Ukraine": 1730, "Romania": 1690, "Slovakia": 1670,
    "Congo DR": 1650, "Jamaica": 1630, "New Caledonia": 1400,
    "Cape Verde": 1560, "Curaçao": 1490, "New Zealand": 1550,
    "Iraq": 1620, "Jordan": 1570, "Uzbekistan": 1660, "Panama": 1620,
    "Ghana": 1680, "Bolivia": 1600, "Suriname": 1420,
    "Kosovo": 1640, "Albania": 1660, "North Macedonia": 1590,
    "Northern Ireland": 1610, "Ireland": 1670,
    
    # 中文key (same values - auto-generated)
    "巴西": 2080, "法国": 2054, "英格兰": 2030, "阿根廷": 2025,
    "葡萄牙": 2015, "西班牙": 2010, "荷兰": 2000, "德国": 1995,
    "比利时": 1975, "克罗地亚": 1960, "意大利": 1950, "乌拉圭": 1940,
    "美国": 1920, "墨西哥": 1910, "哥伦比亚": 1900, "塞内加尔": 1895,
    "摩洛哥": 1890, "日本": 1880, "瑞士": 1870, "丹麦": 1865,
    "澳大利亚": 1855, "韩国": 1850, "厄瓜多尔": 1840, "塞尔维亚": 1835,
    "捷克": 1830, "奥地利": 1825, "土耳其": 1820, "波兰": 1810,
    "瑞典": 1780, "智利": 1800, "加拿大": 1795, "阿尔及利亚": 1790,
    "埃及": 1785, "科特迪瓦": 1750, "突尼斯": 1700, "尼日利亚": 1735,
    "伊朗": 1770, "沙特阿拉伯": 1760, "卡塔尔": 1730, "南非": 1720,
    "巴拉圭": 1715, "海地": 1680, "波黑": 1760, "苏格兰": 1795,
    "挪威": 1790, "希腊": 1720, "喀麦隆": 1710,
    "威尔士": 1740, "乌克兰": 1730, "罗马尼亚": 1690, "斯洛伐克": 1670,
    "民主刚果": 1650, "牙买加": 1630, "新喀里多尼亚": 1400,
    "佛得角": 1560, "库拉索": 1490, "新西兰": 1550,
    "伊拉克": 1620, "约旦": 1570, "乌兹别克斯坦": 1660, "巴拿马": 1620,
    "加纳": 1680, "玻利维亚": 1600, "苏里南": 1420,
    "科索沃": 1640, "阿尔巴尼亚": 1660, "北马其顿": 1590,
    "北爱尔兰": 1610, "爱尔兰": 1670,
}

# ====================================================
# FIFA 世界排名 (2026年6月, 赛前)
# 来源: ESPN/FIFA
# ====================================================
FIFA_RANKINGS = {
    "Argentina": 1, "Spain": 2, "France": 3, "England": 4, "Portugal": 5,
    "Brazil": 6, "Morocco": 7, "Netherlands": 8, "Belgium": 9, "Germany": 10,
    "Croatia": 11, "Italy": 12, "Colombia": 13, "Mexico": 14, "Senegal": 15,
    "Uruguay": 16, "USA": 17, "Japan": 18, "Switzerland": 19, "Iran": 20,
    "Denmark": 21, "Turkey": 22, "Ecuador": 23, "Austria": 24, "South Korea": 25,
    "Nigeria": 26, "Australia": 27, "Algeria": 28, "Egypt": 29, "Canada": 30,
    "Norway": 31, "Ukraine": 32, "Ivory Coast": 33, "Panama": 34,
    "Poland": 36, "Wales": 37, "Sweden": 38,
    "Czechia": 40, "Paraguay": 41, "Scotland": 42, "Serbia": 43,
    "Tunisia": 45, "Congo DR": 46, "Slovakia": 47,
    "Uzbekistan": 50, "Qatar": 56, "Iraq": 57,
    "South Africa": 60, "Saudi Arabia": 61, "Jordan": 63,
    "Bosnia & Herzegovina": 64, "Cape Verde": 67,
    "Ghana": 73, "Curaçao": 82, "Haiti": 83, "New Zealand": 85,
    "North Macedonia": 72, "Albania": 65, "Kosovo": 68,
    "Romania": 39, "Northern Ireland": 59, "Ireland": 55,
    "Jamaica": 62, "New Caledonia": 155, "Bolivia": 86, "Suriname": 138,
    
    # 中文key
    "阿根廷": 1, "西班牙": 2, "法国": 3, "英格兰": 4, "葡萄牙": 5,
    "巴西": 6, "摩洛哥": 7, "荷兰": 8, "比利时": 9, "德国": 10,
    "克罗地亚": 11, "意大利": 12, "哥伦比亚": 13, "墨西哥": 14, "塞内加尔": 15,
    "乌拉圭": 16, "美国": 17, "日本": 18, "瑞士": 19, "伊朗": 20,
    "丹麦": 21, "土耳其": 22, "厄瓜多尔": 23, "奥地利": 24, "韩国": 25,
    "尼日利亚": 26, "澳大利亚": 27, "阿尔及利亚": 28, "埃及": 29, "加拿大": 30,
    "挪威": 31, "乌克兰": 32, "科特迪瓦": 33, "巴拿马": 34,
    "波兰": 36, "威尔士": 37, "瑞典": 38,
    "捷克": 40, "巴拉圭": 41, "苏格兰": 42, "塞尔维亚": 43,
    "突尼斯": 45, "民主刚果": 46, "斯洛伐克": 47,
    "乌兹别克斯坦": 50, "卡塔尔": 56, "伊拉克": 57,
    "南非": 60, "沙特阿拉伯": 61, "约旦": 63,
    "波黑": 64, "佛得角": 67,
    "加纳": 73, "库拉索": 82, "海地": 83, "新西兰": 85,
    "北马其顿": 72, "阿尔巴尼亚": 65, "科索沃": 68,
    "罗马尼亚": 39, "北爱尔兰": 59, "爱尔兰": 55,
    "牙买加": 62, "新喀里多尼亚": 155, "玻利维亚": 86, "苏里南": 138,
}

def get_team_info(name: str) -> dict:
    """根据名称获取球队完整信息 (支持英文/中文)"""
    cn = TEAM_CN.get(name, name)
    elo = ELO_2026.get(name, ELO_2026.get(cn, 1600))
    fifa = FIFA_RANKINGS.get(name, FIFA_RANKINGS.get(cn, 99))
    return {"name_cn": cn, "name_en": name if name != cn else None, "elo": elo, "fifa_rank": fifa}

def resolve_cn(name: str) -> str:
    """将英文名解析为中文名"""
    return TEAM_CN.get(name, name)

if __name__ == "__main__":
    # Test
    test_teams = ["Uruguay", "Cape Verde Islands", "Spain", "Saudi Arabia", "Belgium", "Iran", "New Zealand", "Egypt"]
    for t in test_teams:
        info = get_team_info(t)
        print(f"  {t:30s} → {info['name_cn']:10s} | ELO:{info['elo']} | FIFA:#{info['fifa_rank']}")
    
    print(f"\n  共 {len(TEAM_CN)} 支球队名称映射")
    print(f"  ELO数据: {len(ELO_2026)//2} 支球队 (中英文双key)")
    print(f"  FIFA排名: {len(FIFA_RANKINGS)//2} 支球队 (中英文双key)")

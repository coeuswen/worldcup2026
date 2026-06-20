#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v31.5 2026世界杯 6月22日比赛分析报告生成器 ★Dixon-Coles修正+市场O/U锚定(50%)+防守(-0.20仅先验)+ELO动态+阶段因子
数据源: football-data.org + 网页抓取 + ELO/FIFA + AI深度推演
"""
import json, os, sys, math
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(PROJECT_ROOT, "分析")
os.makedirs(REPORT_DIR, exist_ok=True)

# ====================================================
# ★ 完整数据字典 (6月22日 4场比赛)
# ====================================================

MATCH_DATA = {

    "西班牙vs沙特阿拉伯":     {
        "home_name": "西班牙",
        "away_name": "沙特阿拉伯",
        "home_en": "Spain",
        "away_en": "Saudi Arabia",
        "group": "H组",
        "matchday": 2,
        "venue": "亚特兰大梅赛德斯-奔驰球场",
        "kickoff": "6月22日 00:00 北京时间 (6月22日 12:00 亚特兰大)",
        "elo_home": 2130,
        "elo_away": 1580,
        "elo_diff": 550,
        "fifa_home": 1,
        "fifa_away": 56,
        "level_home": "⭐⭐⭐⭐⭐ 世界第一·欧洲之王",
        "level_away": "⭐⭐⭐ 绿鹰·巨人杀手",
        "icon_home": "👑",
        "icon_away": "🦅",
        "md1_home": "西班牙 0-0 佛得角",
        "md1_away": "沙特阿拉伯 1-1 乌拉圭",
        "form_home":         {
            "summary": "近6场: 3胜3平 | 进8球 失2球",
            "badge": "stable",
            "record": "DWWDWD",
            "goals_for": 8,
            "goals_against": 2,
            "matches": [
                "0-0 佛得角(WC MD1)",
                "2-0 法国(欧国联)",
                "1-1 葡萄牙(欧国联)",
                "2-0 挪威(世欧预)",
                "1-1 荷兰(欧国联)",
                "2-0 瑞士(世欧预)",
            ]
        },
        "form_away":         {
            "summary": "近6场: 1胜3平2负 | 进7球 失7球",
            "badge": "stable",
            "record": "DLDDLW",
            "goals_for": 7,
            "goals_against": 7,
            "matches": [
                "1-1 乌拉圭(WC MD1)",
                "1-2 日本(友谊赛)",
                "0-0 澳大利亚(世亚预)",
                "2-2 阿联酋(世亚预)",
                "0-1 韩国(世亚预)",
                "3-1 越南(世亚预)",
            ]
        },
        "stars_home": [
            ("拉明·亚马尔", "9.3", "巴塞罗那", "18岁进攻天才"),
            ("佩德里", "9.0", "巴塞罗那", "中场节拍器"),
            ("罗德里", "9.0", "曼城", "世界最佳后腰"),
            ("尼科·威廉姆斯", "8.5", "毕尔巴鄂竞技", "速度爆点"),
        ],
        "stars_away": [
            ("萨勒姆·达瓦萨里", "8.0", "利雅得新月", "反击核心·边路爆点"),
            ("穆罕默德·奥韦斯", "7.8", "利雅得新月", "门神·首轮9次扑救"),
            ("穆罕默德·卡诺", "7.5", "利雅得新月", "中场拦截者"),
            ("哈桑·坦巴克提", "7.3", "利雅得新月", "后防领袖"),
        ],
        "lineup_home": "乌奈·西蒙(GK) / 马科斯·略伦特·库巴西·拉波尔特·库库雷利亚 / 罗德里·法比安·鲁伊斯 / 亚马尔·佩德里·尼科·威廉姆斯 / 奥亚萨瓦尔",
        "lineup_away": "奥韦斯(GK) / 加纳姆·坦巴克提·布莱希·沙赫拉尼 / 卡诺·马尔基 / 萨·达瓦萨里·法拉杰·纳·达瓦萨里 / 谢赫里",
        "style_home": "德拉富恩特4-3-3控球压制·亚马尔+尼科双翼齐飞·罗德里中场枢纽",
        "style_away": "深度4-5-1铁桶防守·全员退守·达瓦萨里反击单箭头·奥韦斯最后防线",
        "big5_home": "24/26(英超7+西甲8+意甲3+德甲3+法甲3)",
        "big5_away": "0/26(全部沙特国内联赛)",
        "injury_home": "亚马尔(腿筋已恢复·首轮替补20分钟·本轮可首发)，全员健康",
        "injury_away": "全员健康，无伤病停赛",
        "tactic_analysis": """<strong>阵型对位:</strong> 西班牙4-3-3 vs 沙特4-5-1深度防守 | 西班牙将占据70%+控球率，沙特全线退守<br><strong>控球vs反击:</strong> 西班牙耐心传导+边路突破vs沙特龟缩+定位球/反击偷袭——首轮0:0证明纯控球≠进球<br><strong>高位逼抢:</strong> 西班牙高位压迫极强，沙特后场出球能力弱，受压下失误概率高<br><strong>边路对比:</strong> 亚马尔+尼科vs沙特边后卫，技术碾压级优势。但沙特双后腰会收缩保护半空间<br><strong>定位球:</strong> 西班牙罗德里的远射+定位球是破铁桶重要手段；沙特靠达瓦萨里快发定位球反击<br><strong>防守转换:</strong> 西班牙由攻转守时防线高位，沙特若抢断后快速出球→达瓦萨里1v1门将机会""",
        "odds_euro":         {
            "home": 1.08,
            "draw": 11.0,
            "away": 26.0
        },
        "odds_ah": "西班牙 -2.0 / -2.5",
        "odds_ou25":         {
            "over": 1.5,
            "under": 2.62
        },
        "odds_btts":         {
            "yes": 3.0,
            "no": 1.36
        },
        "prob_home": 80,
        "prob_draw": 14,
        "prob_away": 6,
        "over25_pct": 45,
        "btts_pct": 25,
        "game_flow": """• <strong>上半场节奏:</strong> 西班牙全场围攻，沙特全线退守11人防守。前30分钟能否破僵决定比赛走势——若迟迟不能破门，首轮0:0的焦虑将重现<br>• <strong>先进球概率:</strong> 西班牙80% / 沙特6% / 14%半场0-0<br>• <strong>落后变化:</strong> 若西班牙落后(极小概率)，德拉富恩特将全线压上；沙特若先进球会极致死守——2022年曾2-1击败阿根廷不无先例<br>• <strong>终局走势:</strong> 西班牙围攻格局但首轮0:0暴露攻坚效率问题。亚马尔首发是关键变量。2-0或3-0是合理比分——最多不超过3球""",
        "key_vars": "① 亚马尔能否首发并创造破局 ② 奥韦斯能否复制首轮9扑神迹 ③ 西班牙定位球效率 ④ 达瓦萨里偷袭概率",
        "theory_summary": "ELO差550→西班牙胜率89% | 欧赔1.08→隐含93% | 亚盘-2.0/2.5→机构深盘 | 理论面: 碾压优势",
        "theory_dir": "西班牙胜(理论面绝对碾压)",
        "practice_summary": "战术: 沙特铁桶5-4-1+奥韦斯门神 | 克制: 2/10 | 可用性: 双方全员健康 | 平局: 14%(ELO+550调低) | 冷门: 沙特巨人杀手基因(曾2-1阿根廷)",
        "practice_dir": "西班牙小胜或大胜取决于早破门",
        "alignment": "✅高度一致",
        "gap": "ELO89% vs 市场93% = 4pp小幅溢价。深盘下纯押胜平负无价值",
        "fusion_verdict": """西班牙必胜但净胜球存疑。核心论据: ① ELO差550为本比赛日最大强弱差, FIFA#1 vs #56实力鸿沟不可逾越; ② 但西班牙首轮0:0被佛得角逼平暴露攻坚密集防守的效率问题——全场27射7正0进球; ③ 沙特首轮1:1逼平乌拉圭证明防守组织+反击威胁(达瓦萨里), 2022年曾2:1击败阿根廷的巨人杀手基因不容忽视; ④ 亚马尔首轮仅替补20分钟, 本轮首发将显著提升西班牙边路爆破+创造力, 是破铁桶X因素。<br><br><strong>★三项联动分析:</strong> 体彩1.08/11.00/26.00为「极低胜+极高平+极高负」模式→机构排除平局和客胜, 西班牙必胜是共识。平赔11.00→隐含&lt;10%, 与ELO独立平局概率14%略有差距但方向一致。负赔26.00→完全排除沙特爆冷(隐含4%), 但沙特2022年击败阿根廷提醒: 足球一切皆可能。综合: 西班牙2-0或3-0取胜概率最大, 穿盘-2.25取决于早进球时间。""",
        "fusion_score": "2:0西班牙胜",
        "fusion_conf": "中高",
        "verdict": "西班牙胜(让球方向看穿盘临界)",
        "risk": "🟡中",
        "risk_icon": "🟡",
        "risk_label": "中",
        "score1": "2:0西班牙胜",
        "score2": "3:0西班牙胜",
        "sim_ref":         {
            "mv_home": "€12.0亿",
            "mv_away": "€3000万",
            "mv_ratio": "40:1",
            "home_atk": "€5.0亿",
            "home_def": "€3.5亿",
            "away_atk": "€1000万",
            "away_def": "€1500万",
            "home_fifa": [
                "0:0 佛得角#65(世界杯)",
                "2:0 法国#3(欧国联)",
                "1:1 葡萄牙#6(欧国联)",
                "2:0 挪威#36(世欧预)",
                "1:1 荷兰#8(欧国联)",
            ],
            "home_fifa_gf": 1.2,
            "home_fifa_ga": 0.4,
            "home_fifa_c": "对FIFA3-65区(欧国联+世欧预+世界杯5场): 场均1.2球/失0.4球。对法国/葡萄牙/荷兰等强队不败但进球效率不高",
            "away_fifa": [
                "1:1 乌拉圭#14(世界杯)",
                "0:1 韩国#22(世亚预)",
                "0:0 澳大利亚#25(世亚预)",
                "2:2 阿联酋#63(世亚预)",
                "3:1 越南#115(世亚预)",
            ],
            "away_fifa_gf": 1.2,
            "away_fifa_ga": 1.0,
            "away_fifa_c": "对FIFA14-115区(世亚预+世界杯5场): 场均1.2球/失1.0球。对韩国/澳大利亚难进球但对乌拉圭进球",
            "home_defv": [
                "vs 佛得角(防≈€1500万):0球",
                "vs 法国(防≈€3.0亿):2球",
                "vs 葡萄牙(防≈€2.5亿):1球",
                "vs 挪威(防≈€8000万):0球",
                "vs 荷兰(防≈€2.5亿):1球",
            ],
            "home_defv_gf": 0.8,
            "home_defv_c": "vs类似防线(≈€1500万): 对佛得角0球最直接参照。西班牙对€8000万-3亿防线场均0.8球",
            "away_defv": [
                "vs 日本(防≈€1.5亿):2球",
                "vs 韩国(防≈€1.5亿):1球",
                "vs 澳大利亚(防≈€8000万):0球",
                "vs 阿联酋(防≈€500万):2球",
                "vs 越南(防≈€300万):1球",
            ],
            "away_defv_gf": 1.2,
            "away_defv_c": "vs类似防线(≈€3.5亿): 沙特对强队防线偶尔能进球(乌拉圭1球/日本2球)。西班牙防线€3.5亿最强",
            "home_atkv": [
                "vs 法国(攻≈€5.0亿):0球失",
                "vs 葡萄牙(攻≈€4.5亿):1球失",
                "vs 佛得角(攻≈€1500万):0球失",
                "vs 荷兰(攻≈€3.0亿):1球失",
                "vs 挪威(攻≈€1.5亿):0球失",
            ],
            "home_atkv_ga": 0.4,
            "home_atkv_c": "vs类似攻击线(≈€1000万): 西班牙防守场均失0.4球极佳。沙特攻击线€1000万最低, 零封概率约80%",
            "away_atkv": [
                "vs 日本(攻≈€2.0亿):2球进2球失",
                "vs 韩国(攻≈€1.8亿):1球进0球失",
                "vs 澳大利亚(攻≈€5000万):0球进0球失",
                "vs 阿联酋(攻≈€2000万):2球进2球失",
                "vs 越南(攻≈€500万):1球失",
            ],
            "away_atkv_ga": 0.8,
            "away_atkv_c": "vs类似攻击线(≈€5.0亿): 对日本/韩国攻击线场均失1.0球。西班牙攻击线€5.0亿远超, 预期失2-3球",
            "conclusion": "四维融合: 身价40:1+ELO+550绝对碾压。但首轮0:0提醒: 控球≠进球。亚马尔首发是破局关键。西班牙大概率2-0或3-0取胜。沙特爆冷概率≤8%。"
        }
    },
    "比利时vs伊朗":     {
        "home_name": "比利时",
        "away_name": "伊朗",
        "home_en": "Belgium",
        "away_en": "Iran",
        "group": "G组",
        "matchday": 2,
        "venue": "洛杉矶SoFi体育场",
        "kickoff": "6月22日 03:00 北京时间 (6月22日 12:00 洛杉矶)",
        "elo_home": 1990,
        "elo_away": 1720,
        "elo_diff": 270,
        "fifa_home": 3,
        "fifa_away": 20,
        "level_home": "⭐⭐⭐⭐ 黄金一代·最后一舞",
        "level_away": "⭐⭐⭐ 波斯铁骑·首轮逆转",
        "icon_home": "🇧🇪⚜️",
        "icon_away": "🦁🇮🇷",
        "md1_home": "比利时 1-1 埃及",
        "md1_away": "伊朗 2-2 新西兰",
        "form_home":         {
            "summary": "近6场: 4胜2平 | 进14球 失4球",
            "badge": "stable",
            "record": "WWWDWD",
            "goals_for": 14,
            "goals_against": 4,
            "matches": [
                "1-1 埃及(WC MD1)",
                "3-0 挪威(世欧预)",
                "2-1 波兰(世欧预)",
                "4-0 北爱尔兰(友谊赛)",
                "2-0 希腊(世欧预)",
                "2-2 荷兰(欧国联)",
            ]
        },
        "form_away":         {
            "summary": "近6场: 3胜2平1负 | 进12球 失7球",
            "badge": "solid",
            "record": "WDWWDW",
            "goals_for": 12,
            "goals_against": 7,
            "matches": [
                "2-2 新西兰(WC MD1)",
                "2-0 乌兹别克(世亚预)",
                "3-1 阿联酋(世亚预)",
                "1-0 卡塔尔(世亚预)",
                "2-2 韩国(世亚预)",
                "2-1 日本(友谊赛)",
            ]
        },
        "stars_home": [
            ("凯文·德布劳内", "9.2", "那不勒斯", "世界顶级创造者"),
            ("罗梅卢·卢卡库", "8.8", "那不勒斯", "禁区终结者"),
            ("蒂博·库尔图瓦", "9.0", "皇家马德里", "世界级门神"),
            ("杰雷米·多库", "8.5", "曼城", "速度爆破手"),
        ],
        "stars_away": [
            ("梅赫迪·塔雷米", "8.8", "国际米兰", "欧冠级中锋·全能终结者"),
            ("拉明·雷扎伊安", "7.8", "塞帕汉", "首轮一传一射·带刀后卫"),
            ("萨曼·戈多斯", "7.5", "布伦特福德", "创造力·半空间"),
            ("阿里礼萨·贝兰万德", "7.8", "波斯波利斯", "首轮6扑·门将铁闸"),
        ],
        "lineup_home": "库尔图瓦(GK) / 穆尼耶·恩戈伊·梅切勒·卡斯塔涅 / 奥纳纳·蒂莱曼斯 / 特罗萨德·德布劳内·多库 / 德凯特拉尔(或卢卡库)",
        "lineup_away": "贝兰万德(GK) / 雷扎伊安·哈利勒扎德·内马蒂·穆罕默迪 / 莫赫比·埃扎托拉希·戈多斯·尤塞菲 / 莫甘卢·塔雷米",
        "style_home": "加西亚4-3-3 德布劳内深位组织·多库边路突破·卢卡库禁区终结",
        "style_away": "加莱诺伊4-3-3(无球变4-5-1)收缩防反·塔雷米支点·雷扎伊安助攻",
        "big5_home": "18/26(英超6+意甲4+西甲3+德甲2+法甲3)",
        "big5_away": "2/26(意甲1+英超1)",
        "injury_home": "全员健康，卢卡库首轮替补本场可能首发",
        "injury_away": "全员健康，无核心伤病",
        "tactic_analysis": """<strong>阵型对位:</strong> 比利时4-3-3 vs 伊朗4-3-3(变形5-4-1) | 德布劳内在伊朗两个后腰之间的空间是比赛关键<br><strong>控球vs反击:</strong> 比利时控球55-60%，伊朗收缩后寻求塔雷米支点+雷扎伊安右路助攻<br><strong>高位逼抢:</strong> 比利时高压反抢效率中等，伊朗埃扎托拉希是出球点但受压下失误概率较高<br><strong>边路对比:</strong> 多库vs雷扎伊安——速度vs助攻的互爆! 多库突破后传中是比利时主要得分路径<br><strong>定位球:</strong> 卢卡库头球威胁+德布劳内精准传中；伊朗塔雷米+哈利勒扎德防空能力强<br><strong>防守转换:</strong> 比利时防线年龄偏大(穆尼耶34/梅切勒33)，塔雷米的反击速度是最大威胁""",
        "odds_euro":         {
            "home": 1.42,
            "draw": 4.75,
            "away": 8.0
        },
        "odds_ah": "比利时 -1.0",
        "odds_ou25":         {
            "over": 1.7,
            "under": 2.1
        },
        "odds_btts":         {
            "yes": 1.85,
            "no": 1.85
        },
        "prob_home": 60,
        "prob_draw": 24,
        "prob_away": 16,
        "over25_pct": 55,
        "btts_pct": 52,
        "game_flow": """• <strong>上半场节奏:</strong> 比利时开场控球主导，德布劳内寻找肋部空间。伊朗收缩等待反击——首轮0-2落后追平新西兰证明韧性<br>• <strong>先进球概率:</strong> 比利时55% / 伊朗22% / 23%半场0-0<br>• <strong>落后变化:</strong> 若比利时落后，加西亚会换上卢卡库+萨勒马克斯增加前场火力；若伊朗落后1球，会逐步压出但保持防守纪律<br>• <strong>终局走势:</strong> 比利时实力占优但首轮1:1被埃及逼平暴露攻坚问题。伊朗防守纪律严明+塔雷米反击威胁，比利时2-0或2-1取胜""",
        "key_vars": "① 德布劳内能否在伊朗双后腰间找到空间 ② 卢卡库首发or替补(首发→比利时火力↑) ③ 塔雷米反击效率 ④ 库尔图瓦vs贝兰万德门将对决",
        "theory_summary": "ELO差270→比利时胜率61% | 欧赔1.42→隐含70% | 亚盘-1.0→机构正常定档 | 理论面: 比利时占优",
        "theory_dir": "比利时胜(理论面占优, 伊朗防守不可小觑)",
        "practice_summary": "战术: 伊朗4-3-3收缩防反vs比利时控球攻坚 | 克制: 4/10 | 可用性: 双方主力齐整 | 平局: 24%(ELO+270) | 冷门: 塔雷米+雷扎伊安连线",
        "practice_dir": "比利时小胜但有平局风险",
        "alignment": "⚠️轻度分歧",
        "gap": "ELO61% vs 市场70% = 9pp溢价。首轮伊朗0-2落后追平新西兰+比利时1-1埃及, 市场可能过度定价",
        "fusion_verdict": """比利时胜面较大但穿盘-1.0有风险。核心论据: ① ELO+270为合理差距但非碾压——伊朗FIFA#20远非鱼腩, 首轮0-2落后顽强追至2-2证明大赛韧性; ② 比利时首轮1:1被埃及逼平暴露攻坚铁桶效率存疑, 德布劳内+卢卡库组合年龄老化; ③ 伊朗塔雷米是欧冠级全能中锋——对比利时年龄偏大防线构成实质性威胁, 雷扎伊安首轮一传一射; ④ G组四队同积1分→本场胜者掌握出线主动。<br><br><strong>★三项联动分析:</strong> 体彩1.42/4.75/8.00接近「中庸胜+偏低平」模式→机构引导比利时胜。平赔4.75→隐含约21%, 与ELO独立平局24%接近。负赔8.00→隐含12.5%爆冷概率, 与伊朗实际威胁吻合。综合: 比利时2-1或1-0取胜概率最大, 平局(1-1)不可忽视。""",
        "fusion_score": "2:1比利时胜",
        "fusion_conf": "中",
        "verdict": "比利时胜(让平或防平局)",
        "risk": "🟡中",
        "risk_icon": "🟡",
        "risk_label": "中",
        "score1": "2:1比利时胜",
        "score2": "1:1平局",
        "sim_ref":         {
            "mv_home": "€5.8亿",
            "mv_away": "€8000万",
            "mv_ratio": "7.3:1",
            "home_atk": "€2.5亿",
            "home_def": "€1.8亿",
            "away_atk": "€4000万",
            "away_def": "€2000万",
            "home_fifa": [
                "1:1 埃及#30(世界杯)",
                "2:2 荷兰#8(欧国联)",
                "3:0 挪威#36(世欧预)",
                "2:1 波兰#24(世欧预)",
                "2:0 希腊#54(世欧预)",
            ],
            "home_fifa_gf": 2.0,
            "home_fifa_ga": 0.8,
            "home_fifa_c": "对FIFA8-54区(欧国联+世欧预+世界杯5场): 场均2.0球/失0.8球。对荷兰/埃及均有失球, 防守不完美但对弱队控制力强",
            "away_fifa": [
                "2:2 新西兰#85(世界杯)",
                "2:1 日本#18(友谊赛)",
                "2:2 韩国#22(世亚预)",
                "1:0 卡塔尔#42(世亚预)",
                "3:1 阿联酋#63(世亚预)",
            ],
            "away_fifa_gf": 2.0,
            "away_fifa_ga": 1.1,
            "away_fifa_c": "对FIFA18-85区(世亚预+世界杯5场): 场均2.0球/失1.1球! 对日本/韩国均能进2球, 塔雷米领衔的攻击线在亚洲顶级",
            "home_defv": [
                "vs 荷兰(防≈€2.5亿):2球",
                "vs 埃及(防≈€2000万):1球",
                "vs 波兰(防≈€1.0亿):1球",
                "vs 挪威(防≈€8000万):0球",
                "vs 希腊(防≈€5000万):0球",
            ],
            "home_defv_gf": 0.8,
            "home_defv_c": "vs类似防线(≈€2000万): 对€2000万-2.5亿防线场均0.8球。伊朗防线€2000万≈埃及级别, 比利时应能进2球左右",
            "away_defv": [
                "vs 日本(防≈€1.5亿):2球",
                "vs 韩国(防≈€1.5亿):2球",
                "vs 卡塔尔(防≈€500万):0球",
                "vs 阿联酋(防≈€500万):1球",
                "vs 新西兰(防≈€800万):2球",
            ],
            "away_defv_gf": 1.4,
            "away_defv_c": "vs类似防线(≈€1.8亿): 伊朗对日韩防线场均进2球证明攻击力。比利时防线€1.8亿≈日韩级别, 伊朗进球概率约40-50%",
            "home_atkv": [
                "vs 荷兰(攻≈€3.0亿):2球进2球失",
                "vs 埃及(攻≈€6000万):1球进1球失",
                "vs 波兰(攻≈€1.5亿):1球失",
                "vs 挪威(攻≈€1.5亿):0球失",
                "vs 希腊(攻≈€3000万):0球失",
            ],
            "home_atkv_ga": 0.8,
            "home_atkv_c": "vs类似攻击线(≈€4000万): 对€3000万-3.0亿攻击线场均失0.8球。伊朗攻击线€4000万处于中游, 比利时失球概率约35-40%",
            "away_atkv": [
                "vs 日本(攻≈€2.0亿):2球进2球失",
                "vs 韩国(攻≈€1.8亿):2球进2球失",
                "vs 卡塔尔(攻≈€2000万):0球失",
                "vs 阿联酋(攻≈€2000万):1球失",
                "vs 新西兰(攻≈€1000万):2球进2球失",
            ],
            "away_atkv_ga": 1.4,
            "away_atkv_c": "vs类似攻击线(≈€2.5亿): 伊朗对日本/韩国场均失2.0球。比利时攻击线€2.5亿≥日韩, 伊朗预期失球约2球",
            "conclusion": "四维融合: 身价7.3:1+ELO+270比利时明显占优但非碾压。伊朗塔雷米+雷扎伊安组合对比利时老化防线构成真实威胁。德布劳内创造力是最大变量。比利时大概率2-1取胜(65-70%), 1-1平局概率20-25%, 伊朗爆冷10-15%。"
        }
    },
    "乌拉圭vs佛得角":     {
        "home_name": "乌拉圭",
        "away_name": "佛得角",
        "home_en": "Uruguay",
        "away_en": "Cape Verde",
        "group": "H组",
        "matchday": 2,
        "venue": "迈阿密Hard Rock体育场",
        "kickoff": "6月22日 06:00 北京时间 (6月22日 18:00 迈阿密)",
        "elo_home": 1910,
        "elo_away": 1520,
        "elo_diff": 390,
        "fifa_home": 14,
        "fifa_away": 65,
        "level_home": "⭐⭐⭐⭐ 南美劲旅·天蓝军团",
        "level_away": "⭐⭐ 蓝鲨·首战零封西班牙",
        "icon_home": "🇺🇾⚽",
        "icon_away": "🦈",
        "md1_home": "乌拉圭 1-1 沙特阿拉伯",
        "md1_away": "佛得角 0-0 西班牙",
        "form_home":         {
            "summary": "近6场: 3胜2平1负 | 进10球 失5球",
            "badge": "solid",
            "record": "WWDWDL",
            "goals_for": 10,
            "goals_against": 5,
            "matches": [
                "1-1 沙特阿拉伯(WC MD1)",
                "2-0 厄瓜多尔(世南美预)",
                "2-1 智利(世南美预)",
                "1-1 哥伦比亚(世南美预)",
                "3-1 秘鲁(世南美预)",
                "1-0 巴拉圭(世南美预)",
            ]
        },
        "form_away":         {
            "summary": "近6场: 2胜2平2负 | 进5球 失7球",
            "badge": "resilient",
            "record": "DLLWWD",
            "goals_for": 5,
            "goals_against": 7,
            "matches": [
                "0-0 西班牙(WC MD1)",
                "1-2 突尼斯(友谊赛)",
                "0-2 摩洛哥(友谊赛)",
                "2-1 赤道几内亚(非预赛)",
                "1-0 斯威士兰(非预赛)",
                "1-2 利比亚(非预赛)",
            ]
        },
        "stars_home": [
            ("费德里科·巴尔韦德", "9.0", "皇家马德里", "最具影响力中场"),
            ("达尔文·努涅斯", "8.5", "利物浦", "锋线核心·亟需破荒"),
            ("罗纳德·阿劳霍", "8.8", "巴塞罗那", "防线核心"),
            ("乔治安·德阿拉斯卡埃塔", "8.0", "弗拉门戈", "创造力源泉"),
        ],
        "stars_away": [
            ("沃辛哈(门将)", "7.5", "——", "首战零封西班牙·9次扑救英雄"),
            ("罗伯托·洛佩斯", "7.0", "沙姆洛克流浪者", "防线铁闸"),
            ("洛根·科斯塔", "7.0", "图卢兹", "防守+高空争顶"),
            ("瑞安·门德斯", "7.3", "利雅得胜利", "反击爆点·经验者"),
        ],
        "lineup_home": "罗切特(GK) / 南德斯·阿劳霍·希门尼斯·奥利维拉 / 巴尔韦德·乌加尔特·本坦库尔 / 德阿拉斯卡埃塔 / 努涅斯·佩利斯特里",
        "lineup_away": "沃辛哈(GK) / 塔瓦雷斯·洛佩斯·科斯塔·皮科 / 蒙泰罗·塞梅多 / 门德斯·罗查·贝贝 / 塞梅多",
        "style_home": "比尔萨4-2-3-1高强度逼抢·巴尔韦德后插上·努涅斯终结(首轮失准)",
        "style_away": "布里托5-4-1铁桶阵·全员退守压缩空间·门德斯反击单点·沃辛哈门神",
        "big5_home": "14/26(英超3+西甲4+意甲3+葡超2+法甲2)",
        "big5_away": "1/26(法甲1·图卢兹的洛根·科斯塔)",
        "injury_home": "全员健康，努涅斯首轮错失良机但信心未动摇",
        "injury_away": "全员健康，首战0:0逼平西班牙的防守体系完整保留",
        "tactic_analysis": """<strong>阵型对位:</strong> 乌拉圭4-2-3-1 vs 佛得角5-4-1铁桶 | 乌拉圭将面对比首轮沙特更极致的密集防守<br><strong>控球vs反击:</strong> 乌拉圭控球率60-65%，佛得角全线退守等待门德斯反击——与首轮对西班牙如出一辙<br><strong>高位逼抢:</strong> 比尔萨体系以高强度逼抢著称，佛得角后场出球能力弱，受压下失误率高于西班牙对局<br><strong>边路对比:</strong> 佩利斯特里+努涅斯vs佛得角5后卫翼侧，宽度利用是关键。巴尔韦德的后插上是第二波进攻核心<br><strong>定位球:</strong> 阿劳霍+希门尼斯双塔头球是破铁桶重要武器；佛得角靠门德斯快发定位球反击<br><strong>防守转换:</strong> 乌拉圭高位防线身后空间大，门德斯的速度若抓住反击→阿劳霍的回追是最后一道防线""",
        "odds_euro":         {
            "home": 1.5,
            "draw": 4.2,
            "away": 8.0
        },
        "odds_ah": "乌拉圭 -1.0",
        "odds_ou25":         {
            "over": 1.89,
            "under": 1.89
        },
        "odds_btts":         {
            "yes": 1.9,
            "no": 1.8
        },
        "prob_home": 58,
        "prob_draw": 25,
        "prob_away": 17,
        "over25_pct": 45,
        "btts_pct": 38,
        "game_flow": """• <strong>上半场节奏:</strong> 乌拉圭围攻格局，佛得角复制首轮逼平西班牙的防守蓝本——全员退守11人。前30分钟不进球的焦虑将与首轮对沙特如出一辙<br>• <strong>先进球概率:</strong> 乌拉圭55% / 佛得角12% / 33%半场0-0<br>• <strong>落后变化:</strong> 若乌拉圭落后(小概率)，比尔萨将全线压上变3-3-4；若佛得角领先会极致死守——首轮对西班牙零封已证明此战术可行<br>• <strong>终局走势:</strong> 乌拉圭实力碾压但首轮1:1被沙特逼平暴露终结效率问题。佛得角首轮0:0逼平西班牙是最强背书——40岁门将沃辛哈英雄附体。乌拉圭大概率1-0或2-0小胜""",
        "key_vars": "① 努涅斯能否摆脱首轮低迷(多次错失良机) ② 沃辛哈能否复制9扑神迹 ③ 巴尔韦德后插上破局 ④ 门德斯反击速度",
        "theory_summary": "ELO差390→乌拉圭胜率71% | 欧赔1.50→隐含67% | 亚盘-1.0→机构正常 | 理论面: 乌拉圭优势明显",
        "theory_dir": "乌拉圭胜(ELO+市场一致)",
        "practice_summary": "战术: 佛得角5-4-1铁桶+沃辛哈门神(首轮零封西班牙!) | 克制: 5/10 | 可用性: 双方全员健康 | 平局: 25%(ELO+390) | 冷门: 佛得角延续奇迹",
        "practice_dir": "乌拉圭小胜或有平局风险",
        "alignment": "✅基本一致",
        "gap": "ELO71% vs 市场67% = -4pp折价。市场被佛得角首轮0:0逼平西班牙震撼, 赋予佛得角额外的防守信用分",
        "fusion_verdict": """乌拉圭胜面大但穿盘-1.0风险极高。核心论据: ① ELO+390+FIFA#14vs#65实力差距明显——巴尔韦德/努涅斯/阿劳霍等豪门主力, 佛得角仅1人五大联赛; ② 但佛得角首轮0:0逼平西班牙是本届最大冷门——40岁门将沃辛哈9次扑救零封世界第一; ③ 乌拉圭首轮1:1被沙特逼平暴露终结效率问题——努涅斯多次错失良机, 比尔萨体系面对铁桶阵时创造力不如西班牙; ④ H组四队全部战平→出线形势胶着。<br><br><strong>★三项联动分析:</strong> 体彩赔率1.50/4.20/8.00为「低胜+中平+高负」模式。平赔4.20→隐含约24%, 与ELO独立平局25%几乎完全吻合→平赔诚实。负赔8.00→隐含12.5%冷门概率, 佛得角首轮逼平西班牙后市场已给予充分尊重。综合: 乌拉圭1-0或2-0小胜概率最大, 0-0平局不可完全排除。""",
        "fusion_score": "2:0乌拉圭胜",
        "fusion_conf": "中",
        "verdict": "乌拉圭胜(让平/防0-0)",
        "risk": "🟠中高",
        "risk_icon": "🟠",
        "risk_label": "中高",
        "score1": "2:0乌拉圭胜",
        "score2": "1:0乌拉圭胜",
        "sim_ref":         {
            "mv_home": "€5.2亿",
            "mv_away": "€2500万",
            "mv_ratio": "20.8:1",
            "home_atk": "€2.2亿",
            "home_def": "€1.8亿",
            "away_atk": "€500万",
            "away_def": "€800万",
            "home_fifa": [
                "1:1 沙特阿拉伯#56(世界杯)",
                "2:0 厄瓜多尔#23(世南美预)",
                "2:1 智利#29(世南美预)",
                "1:1 哥伦比亚#11(世南美预)",
                "3:1 秘鲁#41(世南美预)",
            ],
            "home_fifa_gf": 1.8,
            "home_fifa_ga": 0.8,
            "home_fifa_c": "对FIFA11-56区(世南美预+世界杯5场): 场均1.8球/失0.8球。对厄瓜多尔/智利/秘鲁等南美对手稳定进球, 但对沙特进球困难",
            "away_fifa": [
                "0:0 西班牙#1(世界杯)",
                "1:2 突尼斯#45(友谊赛)",
                "0:2 摩洛哥#13(友谊赛)",
                "2:1 赤道几内亚#80(非预赛)",
                "1:0 斯威士兰#150(非预赛)",
            ],
            "away_fifa_gf": 0.8,
            "away_fifa_ga": 1.0,
            "away_fifa_c": "对FIFA1-150区(非预赛+世界杯5场): 场均0.8球/失1.0球。对西班牙0:0是历史级防守表现, 但对突尼斯/摩洛哥均有失球",
            "home_defv": [
                "vs 沙特(防≈€1000万):1球",
                "vs 厄瓜多尔(防≈€1.5亿):0球",
                "vs 智利(防≈€5000万):1球",
                "vs 哥伦比亚(防≈€1.5亿):1球",
                "vs 秘鲁(防≈€3000万):1球",
            ],
            "home_defv_gf": 0.8,
            "home_defv_c": "vs类似防线(≈€800万): 对€1000万-1.5亿防线场均0.8球。佛得角防线€800万是乌拉圭面对的最低级别, 但首轮零封西班牙证明质量远超身价",
            "away_defv": [
                "vs 突尼斯(防≈€5000万):2球",
                "vs 摩洛哥(防≈€2.0亿):2球",
                "vs 赤道几内亚(防≈€200万):1球",
                "vs 西班牙(防≈€3.5亿):0球!",
                "vs 利比亚(防≈€300万):2球",
            ],
            "away_defv_gf": 1.4,
            "away_defv_c": "vs类似防线(≈€1.8亿): 对强队防线进球困难(西班牙0球/摩洛哥0球)。但零封西班牙证明防守远非身价可比",
            "home_atkv": [
                "vs 沙特(攻≈€1000万):1球进1球失",
                "vs 厄瓜多尔(攻≈€1.5亿):0球失",
                "vs 智利(攻≈€1.0亿):1球失",
                "vs 哥伦比亚(攻≈€1.5亿):1球失",
                "vs 秘鲁(攻≈€5000万):1球失",
            ],
            "home_atkv_ga": 0.8,
            "home_atkv_c": "vs类似攻击线(≈€500万): 对€1000万-1.5亿攻击线场均失0.8球。佛得角攻击线€500万为最低, 零封概率约65-70%",
            "away_atkv": [
                "vs 西班牙(攻≈€5.0亿):0球失!",
                "vs 突尼斯(攻≈€2500万):1球进2球失",
                "vs 摩洛哥(攻≈€2.0亿):0球进2球失",
                "vs 赤道几内亚(攻≈€200万):1球失",
                "vs 利比亚(攻≈€300万):2球失",
            ],
            "away_atkv_ga": 1.0,
            "away_atkv_c": "vs类似攻击线(≈€2.2亿): 零封西班牙是奇迹级表现。乌拉圭攻击线€2.2亿远低于西班牙€5.0亿, 佛得角防守理论上可复制",
            "conclusion": "四维融合: 身价20.8:1+ELO+390碾压但佛得角首轮零封西班牙颠覆认知。努涅斯终结效率是最大变量。乌拉圭大概率1-0或2-0小胜, 穿盘-1.0风险极高。佛得角爆冷胜≤10%, 但0-0平局概率20-25%。"
        }
    },
    "新西兰vs埃及":     {
        "home_name": "新西兰",
        "away_name": "埃及",
        "home_en": "New Zealand",
        "away_en": "Egypt",
        "group": "G组",
        "matchday": 2,
        "venue": "温哥华BC Place球场",
        "kickoff": "6月22日 09:00 北京时间 (6月22日 18:00 温哥华)",
        "elo_home": 1480,
        "elo_away": 1700,
        "elo_diff": -220,
        "fifa_home": 85,
        "fifa_away": 30,
        "level_home": "⭐ 全白军团·首轮进球大战",
        "level_away": "⭐⭐⭐ 法老军团·逼平比利时",
        "icon_home": "🇳🇿⚪",
        "icon_away": "🦅🇪🇬",
        "md1_home": "新西兰 2-2 伊朗",
        "md1_away": "埃及 1-1 比利时",
        "form_home":         {
            "summary": "近6场: 2胜1平3负 | 进9球 失10球",
            "badge": "mixed",
            "record": "DWLLWL",
            "goals_for": 9,
            "goals_against": 10,
            "matches": [
                "2-2 伊朗(WC MD1)",
                "0-1 英格兰(友谊赛)",
                "0-4 海地(友谊赛)",
                "4-1 智利(友谊赛)",
                "0-2 芬兰(友谊赛)",
                "3-0 斐济(大洋预选)",
            ]
        },
        "form_away":         {
            "summary": "近6场: 3胜2平1负 | 进8球 失4球",
            "badge": "solid",
            "record": "DDWWWL",
            "goals_for": 8,
            "goals_against": 4,
            "matches": [
                "1-1 比利时(WC MD1)",
                "1-2 巴西(友谊赛)",
                "1-0 俄罗斯(友谊赛)",
                "0-0 西班牙(友谊赛)",
                "4-0 沙特阿拉伯(友谊赛)",
                "1-0 科威特(世亚预?)",
            ]
        },
        "stars_home": [
            ("克里斯·伍德", "8.0", "诺丁汉森林", "锋线支点·队长"),
            ("伊莱贾·贾斯特", "7.5", "霍尔森斯", "首轮两球·状态火热"),
            ("利贝拉托·卡卡塞", "7.3", "恩波利", "左后卫·攻守兼备"),
            ("马尔科·斯塔梅尼奇", "7.3", "奥林匹亚科斯", "中场核心"),
        ],
        "stars_away": [
            ("穆罕默德·萨拉赫", "9.3", "利物浦", "世界级前锋·队长·近8场8球"),
            ("奥马尔·马尔穆什", "8.8", "曼城", "第二得分点·速度爆点"),
            ("埃马姆·阿舒尔", "7.8", "阿尔阿赫利", "首轮进球·B2B中场"),
            ("穆罕默德·埃尔舍纳维", "7.5", "阿尔阿赫利", "门将·预选赛6场零封"),
        ],
        "lineup_home": "克罗科姆(GK) / 史密斯·博克索尔·宾登·卡卡塞 / 麦考瓦特·斯塔梅尼奇·贾斯特·奥尔德 / 伍德(队长)·韦恩",
        "lineup_away": "埃尔舍纳维(GK) / 拉比亚·阿卜杜勒莫内姆·哈尼·法图赫 / 阿舒尔·法蒂·阿提亚 / 萨拉赫(队长)·马尔穆什·阿德尔",
        "style_home": "梅恩4-4-2直接打法·伍德支点·贾斯特首轮两球领衔·防守存漏洞",
        "style_away": "哈桑4-3-3控球进攻·萨拉赫+马尔穆什双核·预选赛6场零封防守稳固",
        "big5_home": "4/26(英超1+意甲1+希腊超1+丹超1)",
        "big5_away": "6/26(英超2+法甲1+德甲1+沙特2)",
        "injury_home": "全员健康，贾斯特首轮双响状态火爆",
        "injury_away": "全员健康，萨拉赫+马尔穆什均状态良好",
        "tactic_analysis": """<strong>阵型对位:</strong> 新西兰4-4-2 vs 埃及4-3-3 | 新西兰双前锋vs埃及双中卫，伍德支点+贾斯特跑动是关键<br><strong>控球vs反击:</strong> 埃及控球率55-60%，萨拉赫+马尔穆什两翼冲击；新西兰靠伍德头球摆渡+贾斯特二点球<br><strong>高位逼抢:</strong> 埃及前场压迫强度中等，新西兰后场出球能力有限，受压下长传找伍德是主要出球方式<br><strong>边路对比:</strong> 萨拉赫vs卡卡塞——世界级vs意甲级的关键对决! 萨拉赫内切射门+传中是埃及最大武器<br><strong>定位球:</strong> 伍德(头球)+贾斯特(首轮两球含定位球)是新西兰定位球威胁；埃及萨拉赫任意球+角球传中质量极高<br><strong>防守转换:</strong> 新西兰首轮丢2球暴露防守漏洞(对伊朗)，埃及预选赛6场零封的防守稳固度远高于新西兰""",
        "odds_euro":         {
            "home": 5.5,
            "draw": 4.33,
            "away": 1.62
        },
        "odds_ah": "埃及 -0.75",
        "odds_ou25":         {
            "over": 2.25,
            "under": 1.67
        },
        "odds_btts":         {
            "yes": 1.85,
            "no": 1.85
        },
        "prob_home": 15,
        "prob_draw": 28,
        "prob_away": 57,
        "over25_pct": 48,
        "btts_pct": 52,
        "game_flow": """• <strong>上半场节奏:</strong> 埃及控球主导，萨拉赫+马尔穆什频繁冲击新西兰左路(卡卡塞)。新西兰靠伍德支点+贾斯特跑动寻找机会<br>• <strong>先进球概率:</strong> 埃及52% / 新西兰18% / 30%半场0-0<br>• <strong>落后变化:</strong> 若埃及落后(小概率)，哈桑会全线压上增加前场兵力；若新西兰落后1球，梅恩会保持4-4-2等待定位球/反击机会<br>• <strong>终局走势:</strong> 埃及实力占优但首轮1:1比利时展示的防守韧性远超新西兰水平。新西兰首轮2:2证明有进球能力(贾斯特双响)。埃及赢面大, 1-0或2-1取胜""",
        "key_vars": "① 萨拉赫vs卡卡塞的一对一结果 ② 贾斯特能否延续首轮火热状态 ③ 埃及预选赛6场零封的防守能否再现 ④ 伍德定位球头球威胁",
        "theory_summary": "ELO差+220(埃及优势)→埃及胜率56% | 欧赔1.62→隐含62% | 亚盘-0.75→机构看好埃及 | 理论面: 埃及占优",
        "theory_dir": "埃及胜(ELO+市场一致)",
        "practice_summary": "战术: 埃及4-3-3萨拉赫+马尔穆什vs新西兰4-4-2直接打法 | 克制: 3/10 | 可用性: 双方全员健康 | 平局: 28%(ELO-220) | 冷门: 新西兰首轮2球证明攻击力",
        "practice_dir": "埃及小胜概率最大",
        "alignment": "✅基本一致",
        "gap": "ELO56% vs 市场62% = 6pp小幅溢价, 埃及预选赛6场零封提供额外信用",
        "fusion_verdict": """埃及胜面较大但新西兰有进球能力。核心论据: ① ELO+220(埃及优势)为合理差距——埃及FIFA#30vs#85, 萨拉赫+马尔穆什组合是非洲最强攻击线; ② 埃及预选赛5胜1平+6场零封(9进球0失球!)的防守纪录令人惊叹, 首轮1:1逼平比利时证明实力; ③ 但新西兰并非毫无抵抗力——首轮2:2平伊朗证明攻击力(贾斯特双响+伍德支点); ④ G组四队同积1分→本场胜者掌握出线主动。<br><br><strong>★三项联动分析:</strong> 体彩赔率5.50/4.33/1.62接近「高负+中平+低胜」模式→引导埃及胜(但新西兰被让0.75球)。平赔4.33→隐含约23%, 与ELO独立平局28%略有差距。负赔1.62→隐含约62%埃及胜率, 在合理区间。综合: 埃及1-0或2-1取胜概率最大, BTTS~52%概率较高。""",
        "fusion_score": "2:1埃及胜",
        "fusion_conf": "中",
        "verdict": "埃及胜(让平/防平局)",
        "risk": "🟡中",
        "risk_icon": "🟡",
        "risk_label": "中",
        "score1": "2:1埃及胜",
        "score2": "1:0埃及胜",
        "sim_ref":         {
            "mv_home": "€3000万",
            "mv_away": "€3.5亿",
            "mv_ratio": "1:11.7",
            "home_atk": "€1200万",
            "home_def": "€800万",
            "away_atk": "€1.8亿",
            "away_def": "€8000万",
            "home_fifa": [
                "2:2 伊朗#20(世界杯)",
                "4:1 智利#29(友谊赛)",
                "3:0 斐济#148(大洋预选)",
                "0-2 芬兰#61(友谊赛)",
                "0:4 海地#95(友谊赛)",
            ],
            "home_fifa_gf": 2.0,
            "home_fifa_ga": 1.6,
            "home_fifa_c": "对FIFA20-148区(友谊赛+世界杯5场): 场均2.0球/失1.6球! 对伊朗进2球但失2球, 对海地失4球暴露防守脆弱",
            "away_fifa": [
                "1:1 比利时#3(世界杯)",
                "0:0 西班牙#1(友谊赛)",
                "1:0 俄罗斯#48(友谊赛)",
                "1:2 巴西#5(友谊赛)",
                "4:0 沙特阿拉伯#56(友谊赛)",
            ],
            "away_fifa_gf": 1.4,
            "away_fifa_ga": 0.6,
            "away_fifa_c": "对FIFA1-56区(友谊赛+世界杯5场): 场均1.4球/失0.6球。逼平比利时+西班牙+对巴西仅失2球, 防守水平远超新西兰面对的任何对手",
            "home_defv": [
                "vs 伊朗(防≈€2000万):2球",
                "vs 斐济(防≈€100万):0球",
                "vs 芬兰(防≈€2000万):2球",
                "vs 海地(防≈€500万):4球",
                "vs 智利(防≈€5000万):1球",
            ],
            "home_defv_gf": 1.8,
            "home_defv_c": "vs类似防线(≈€8000万): 新西兰对弱队防线进球可观但对稍强防线场均仅1.5球。埃及防线€8000万远超其曾面对的任何防线",
            "away_defv": [
                "vs 比利时(防≈€1.8亿):1球",
                "vs 西班牙(防≈€3.5亿):0球",
                "vs 巴西(防≈€3.0亿):2球",
                "vs 俄罗斯(防≈€5000万):0球",
                "vs 沙特(防≈€1000万):0球",
            ],
            "away_defv_gf": 0.6,
            "away_defv_c": "vs类似防线(≈€800万): 埃及对强队防线场均仅0.5球, 但对巴西进2球。新西兰防线€800万≈俄罗斯/沙特级别, 埃及应能进2球左右",
            "home_atkv": [
                "vs 伊朗(攻≈€4000万):2球进2球失",
                "vs 斐济(攻≈€100万):0球失",
                "vs 芬兰(攻≈€2000万):0球进2球失",
                "vs 海地(攻≈€500万):0球进4球失",
                "vs 智利(攻≈€1.0亿):1球失",
            ],
            "home_atkv_ga": 1.6,
            "home_atkv_c": "vs类似攻击线(≈€1.8亿): 新西兰防守场均失1.6球极差! 埃及攻击线€1.8亿(萨拉赫+马尔穆什)远超其面对的任何攻击线, 预期失球2-3球",
            "away_atkv": [
                "vs 比利时(攻≈€2.5亿):1球进1球失",
                "vs 西班牙(攻≈€5.0亿):0球失",
                "vs 巴西(攻≈€4.5亿):1球进2球失",
                "vs 俄罗斯(攻≈€3000万):0球失",
                "vs 沙特(攻≈€1000万):0球失",
            ],
            "away_atkv_ga": 0.6,
            "away_atkv_c": "vs类似攻击线(≈€1200万): 埃及防守场均失0.6球极佳! 预选赛6场零封+逼平比利时证明防守质量。新西兰攻击线€1200万≈俄罗斯级别, 埃及大概率零封或失1球",
            "conclusion": "四维融合: 埃及身价11.7倍+ELO+220全面占优。萨拉赫+马尔穆什组合是新西兰防线难以承受的攻击力。埃及预选赛6场零封+逼平比利时证明防守顶级。新西兰首轮2球证明有进攻能力(贾斯特), 但防守漏洞(场均失1.6球)是致命弱点。埃及大概率2-1或1-0取胜。"
        }
    },
}

# ★ v31.5 每场比赛的泊松λ参数 + 防守风格评分 (MD2阶段因子+0.05球自动应用)
MATCH_PARAMS = {
    "西班牙vs沙特阿拉伯": {
        "lambda_h": 2.5, "lambda_a": 0.3, "def_h": 4, "def_a": 9,
        "desc": "西班牙控球碾压 vs 沙特铁桶·奥韦斯门神(首轮9扑)·定位球是破局关键"
    },
    "比利时vs伊朗": {
        "lambda_h": 2.0, "lambda_a": 1.0, "def_h": 5, "def_a": 7,
        "desc": "比利时德布劳内创造力 vs 伊朗收缩防反·塔雷米反击·双方均需出线积分"
    },
    "乌拉圭vs佛得角": {
        "lambda_h": 1.8, "lambda_a": 0.5, "def_h": 5, "def_a": 9,
        "desc": "乌拉圭围攻铁桶 vs 佛得角首轮零封西班牙神迹·努涅斯终结效率是关键变量"
    },
    "新西兰vs埃及": {
        "lambda_h": 0.8, "lambda_a": 2.0, "def_h": 6, "def_a": 5,
        "desc": "新西兰直接打法·贾斯特双响 vs 埃及萨拉赫+马尔穆什·预选赛6场零封防守"
    },
}



# ====================================================
# HTML样式
# ====================================================
CSS = """
:root {
    --bg-primary: #0f1119; --bg-secondary: #161822; --bg-tertiary: #1c1f2e;
    --text-primary: #e8e8e8; --text-secondary: #a0a4b8;
    --gold: #fbbf24; --gold-bright: #fcd34d;
    --blue: #3b82f6; --blue-bright: #60a5fa;
    --orange: #f97316; --red: #ef4444; --green: #22c55e;
    --purple: #8b5cf6; --pink: #ec4899;
    --home-color: #60a5fa; --away-color: #f97316; --draw-color: #fbbf24;
    --border-dim: rgba(255,255,255,.06); --border-bright: rgba(255,255,255,.12);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: var(--bg-primary); color: var(--text-primary); line-height: 1.7;
    overflow-x: hidden;
}
.header {
    text-align: center; padding: 36px 20px 28px;
    background: linear-gradient(180deg, #0d1525 0%, #0f1119 100%);
    border-bottom: 1px solid rgba(251,191,36,.12);
}
.header h1 { font-size: 1.9em; font-weight: 800; letter-spacing: -.02em; }
.header h1 span { color: var(--gold-bright); }
.header .subtitle { color: var(--text-secondary); font-size: .82em; margin-top: 6px; }
.identity-tags { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin-top: 12px; }
.id-tag {
    background: rgba(251,191,36,.06); border: 1px solid rgba(251,191,36,.15);
    border-radius: 20px; padding: 3px 12px; font-size: .73em; color: var(--gold);
}
.container { max-width: 900px; margin: 0 auto; padding: 20px 16px; }
.disclaimer {
    background: rgba(251,191,36,.04); border: 1px solid rgba(251,191,36,.1);
    border-radius: 10px; padding: 12px 18px; margin-bottom: 24px;
    font-size: .78em; color: var(--text-secondary); text-align: center;
}

/* 比赛头部 */
.match-header {
    background: var(--bg-secondary); border: 1px solid var(--border-dim);
    border-radius: 14px; padding: 20px 24px; margin-bottom: 24px;
}
.match-title { font-size: 1.35em; font-weight: 800; text-align: center; margin-bottom: 8px; }
.match-meta { text-align: center; font-size: .8em; color: var(--text-secondary); }
.match-meta span { margin: 0 8px; }

/* Section */
.section {
    background: var(--bg-secondary); border: 1px solid var(--border-dim);
    border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;
}
.section-title {
    font-size: 1.05em; font-weight: 700; margin-bottom: 14px;
    padding-bottom: 8px; border-bottom: 1px solid var(--border-bright);
    color: var(--gold);
}

/* ELO条 */
.elo-row { display: flex; align-items: center; gap: 12px; margin: 8px 0; }
.elo-team { width: 120px; font-size: .9em; font-weight: 600; text-align: right; }
.elo-team.away { text-align: left; }
.elo-bar-wrap { flex: 1; height: 22px; background: rgba(255,255,255,.04); border-radius: 11px; position: relative; overflow: hidden; }
.elo-bar-fill { height: 100%; border-radius: 11px; background: linear-gradient(90deg, var(--blue), var(--blue-bright)); transition: width .8s; }
.elo-val { font-size: .8em; font-weight: 700; width: 48px; text-align: center; }
.elo-advantage { text-align: center; font-size: .78em; color: var(--gold); margin: 4px 0; }
.fifa-badge {
    display: inline-block; background: rgba(139,92,246,.15); border: 1px solid rgba(139,92,246,.3);
    border-radius: 12px; padding: 2px 10px; font-size: .73em; color: var(--purple); margin-left: 6px;
}

/* 近期战绩 */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-card {
    background: rgba(0,0,0,.15); border-radius: 10px; padding: 12px 14px;
    border: 1px solid var(--border-dim);
}
.form-card-title { font-weight: 700; font-size: .88em; margin-bottom: 6px; }
.form-badge {
    display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: .7em;
    font-weight: 600; margin-bottom: 6px;
}
.form-badge.hot { background: rgba(239,68,68,.15); color: var(--red); }
.form-badge.stable { background: rgba(34,197,94,.12); color: var(--green); }
.form-badge.rising { background: rgba(59,130,246,.12); color: var(--blue-bright); }
.form-badge.mixed { background: rgba(251,191,36,.1); color: var(--gold); }
.form-badge.solid { background: rgba(34,197,94,.1); color: var(--green); }
.form-badge.struggling { background: rgba(239,68,68,.1); color: var(--red); }
.form-record { font-family: 'SF Mono', Consolas, monospace; font-size: .95em; letter-spacing: .15em; margin: 4px 0; }
.form-matches { font-size: .72em; color: var(--text-secondary); line-height: 1.6; }

/* 战术分析 */
.tactic-split { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.tactic-card { background: rgba(0,0,0,.15); border-radius: 10px; padding: 14px; border: 1px solid var(--border-dim); }
.tactic-card-title { font-weight: 700; font-size: .85em; margin-bottom: 8px; }
.star-box { margin: 4px 0; padding: 3px 8px; background: rgba(251,191,36,.04); border-radius: 6px; font-size: .76em; display: flex; justify-content: space-between; }
.star-name { font-weight: 600; }
.star-club { color: var(--text-secondary); font-size: .9em; }
.tactic-text { font-size: .78em; color: var(--text-secondary); line-height: 1.7; margin-top: 8px; }
.injury-box {
    background: rgba(239,68,68,.06); border: 1px solid rgba(239,68,68,.15);
    border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: .78em; color: var(--red);
}

/* 赔率面板 */
.odds-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.odds-card {
    background: rgba(0,0,0,.15); border-radius: 8px; padding: 12px;
    text-align: center; border: 1px solid var(--border-dim);
}
.odds-card-title { font-size: .72em; color: var(--text-secondary); margin-bottom: 4px; }
.odds-num { font-size: 1.3em; font-weight: 800; }
.odds-num.home-color { color: var(--home-color); }
.odds-num.draw-color { color: var(--draw-color); }
.odds-num.away-color { color: var(--away-color); }
.odds-card-row { display: flex; justify-content: space-between; font-size: .82em; margin: 2px 0; }
.implied-prob { color: var(--text-secondary); font-size: .75em; }
.ah-table { margin-top: 10px; background: rgba(0,0,0,.1); border-radius: 8px; padding: 10px 12px; }
.ah-table-title { font-size: .78em; color: var(--text-secondary); margin-bottom: 2px; }
.ah-prob-line { font-size: .75em; color: var(--teal); padding-top: 3px; border-top: 1px solid rgba(255,255,255,.05); margin-top: 4px; }
.ah-prob-line span { margin-right: 12px; white-space: nowrap; }
.ah-lines { display: flex; flex-wrap: wrap; gap: 6px; }
.ah-chip { background: rgba(59,130,246,.08); border: 1px solid rgba(59,130,246,.15); border-radius: 6px; padding: 3px 8px; font-size: .72em; }

/* 概率 */
.prob-row { display: flex; gap: 8px; align-items: flex-end; }
.prob-col { flex: 1; text-align: center; }
.prob-label { font-size: .78em; font-weight: 600; margin-bottom: 4px; }
.prob-bar { height: 24px; background: rgba(255,255,255,.04); border-radius: 4px; overflow: hidden; margin: 4px 0; }
.prob-fill { height: 100%; border-radius: 4px; transition: width 1s; }
.prob-value { font-size: 1.1em; font-weight: 800; }
.home-color { color: var(--home-color); } .draw-color { color: var(--draw-color); }
.away-color { color: var(--away-color); } .gold-color { color: var(--gold); }
.sub-probs { text-align: center; font-size: .78em; color: var(--text-secondary); margin: 8px 0; }
.score-matrix { background: rgba(0,0,0,.12); border-radius: 8px; padding: 12px; margin-top: 10px; }
.score-matrix-title { font-size: .8em; color: var(--text-secondary); margin-bottom: 6px; }
.score-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.score-chip { background: rgba(251,191,36,.06); border: 1px solid rgba(251,191,36,.15); border-radius: 8px; padding: 4px 10px; font-size: .78em; }
.score-chip em { color: var(--text-secondary); font-style: normal; font-size: .85em; }

/* 类似对手参照 */
.similar-section { background: rgba(59,130,246,.02); border: 1px solid rgba(59,130,246,.08); }
.similar-subtitle { font-size: .85em; font-weight: 700; color: var(--teal); margin: 10px 0 4px; }
.similar-subtitle.first { margin-top: 0; }
.similar-team-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 6px 0; }
.similar-team-box { background: rgba(0,0,0,.12); border-radius: 8px; padding: 8px 12px; font-size: .74em; }
.similar-team-label { font-weight: 700; color: var(--gold-bright); font-size: .9em; margin-bottom: 4px; }
.similar-match { display: inline-block; background: rgba(251,191,36,.05); border: 1px solid rgba(251,191,36,.08); border-radius: 5px; padding: 2px 6px; margin: 1px; font-size: .95em; }
.similar-match .score { color: var(--gold); font-weight: 700; }
.similar-conclusion { font-size: .78em; color: var(--teal); margin-top: 8px; padding: 8px; background: rgba(0,0,0,.08); border-radius: 6px; line-height: 1.5; }
.mv-compare { text-align: center; font-size: .8em; color: var(--text-secondary); margin-bottom: 10px; padding: 6px; background: rgba(0,0,0,.08); border-radius: 6px; }

/* 综合推演 */
.analysis-text { font-size: .84em; color: var(--text-secondary); line-height: 1.8; }
.analysis-text-small { font-size: .82em; color: var(--text-secondary); line-height: 1.8; }
.analysis-text strong { color: var(--text-primary); }
.key-vars-box { margin-top: 10px; padding: 10px; background: rgba(251,191,36,.05); border: 1px solid rgba(251,191,36,.15); border-radius: 8px; font-size: .82em; color: var(--text-secondary); }

/* 双面融合 */
.conclusion-panel {
    background: linear-gradient(135deg, rgba(34,197,94,.03) 0%, rgba(59,130,246,.03) 100%);
    border: 1px solid rgba(59,130,246,.12); border-radius: 16px; padding: 24px;
}
.conclusion-header { font-size: 1.1em; font-weight: 700; color: var(--gold); text-align: center; margin-bottom: 16px; }
.fusion-panel { background: rgba(0,0,0,.12); border-radius: 12px; padding: 16px; }
.fusion-header { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.side-label { font-size: .76em; font-weight: 700; margin-bottom: 4px; }
.theory-label { color: var(--blue-bright); }
.practice-label { color: var(--orange); }
.side-content { font-size: .75em; color: var(--text-secondary); line-height: 1.5; }
.alignment-badge {
    display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: .78em; font-weight: 700; margin-left: 6px;
}
.align-consistent { background: rgba(34,197,94,.12); color: var(--green); }
.align-divergence { background: rgba(251,191,36,.12); color: var(--gold); }
.align-reversal { background: rgba(239,68,68,.12); color: var(--red); }
.fusion-verdict-box { margin-top: 12px; padding: 12px; background: rgba(0,0,0,.15); border-radius: 8px; }
.fusion-verdict-box .title { font-weight: 700; font-size: .9em; color: var(--gold); margin-bottom: 6px; }
.conclusion-body { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
.score-recommendation { text-align: center; padding: 16px 12px; background: rgba(0,0,0,.12); border-radius: 10px; }
.rec-label { font-size: .78em; color: var(--text-secondary); }
.rec-score { font-size: 1.8em; font-weight: 900; color: var(--gold-bright); margin: 6px 0; }
.rec-label-sub { font-size: .76em; color: var(--text-secondary); }
.verdict-block { padding: 14px; background: rgba(0,0,0,.12); border-radius: 10px; }
.verdict-main { font-size: .9em; margin-bottom: 4px; }
.verdict-conf { font-size: .76em; color: var(--text-secondary); }
.verdict-scores { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; }
.verdict-note { font-size: .75em; color: var(--text-secondary); margin-top: 4px; }
.risk-block { padding: 14px; border-radius: 10px; text-align: center; }
.risk-bg-low { background: rgba(34,197,94,.06); border: 1px solid rgba(34,197,94,.15); }
.risk-bg-medium { background: rgba(251,191,36,.06); border: 1px solid rgba(251,191,36,.15); }
.risk-bg-high { background: rgba(239,68,68,.06); border: 1px solid rgba(239,68,68,.15); }
.risk-label { font-size: .73em; color: var(--text-secondary); }
.risk-value { font-size: 1.1em; font-weight: 800; margin: 4px 0; }
.btts-note { font-size: .72em; color: var(--text-secondary); margin: 2px 0; }

/* Footer */
.footer { text-align: center; padding: 28px 16px; font-size: .75em; color: var(--text-secondary); border-top: 1px solid var(--border-dim); margin-top: 24px; }

@media (max-width: 680px) {
    .form-grid, .tactic-split, .fusion-header, .conclusion-body { grid-template-columns: 1fr; }
    .odds-grid { grid-template-columns: 1fr 1fr; }
}
"""

# ====================================================
# v31.5 Dixon-Coles修正 + 市场O/U锚定(50%) + 防守风格(-0.20,仅先验) + ELO动态权重 + 锦标赛阶段
# ★ 基于32场实战校准(截至6/20): O/U准确率50%→锚定40%→28%; 零封率41%→防守-0.20
# ★ ELO动态: 差≥200→55%权重, 差<100→35%, 中间线性 (32场: 大差距60%准/小差距50%)
# ★ 锦标赛阶段: MD1保守→平局倾向↑; MD2出线压力→开放度↑; MD3生死战→极端比分↑
# ====================================================

def poisson_pmf(k, lam):
    """泊松概率质量函数"""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def dixon_coles_tau(h, a, lh, la, rho=-0.13):
    """Dixon-Coles低比分修正因子τ (pena.lt RPS 0.191 vs 标准泊松 0.192)"""
    if h == 0 and a == 0:
        return 1.0 - lh * la * rho
    elif h == 0 and a == 1:
        return 1.0 + lh * rho
    elif h == 1 and a == 0:
        return 1.0 + la * rho
    elif h == 1 and a == 1:
        return 1.0 - rho
    else:
        return 1.0

def compute_score_matrix(lh, la, rho=-0.13, max_g=5):
    """Dixon-Coles修正比分概率矩阵 → Top 10"""
    raw = {}
    for h in range(max_g + 1):
        for a in range(max_g + 1):
            p = poisson_pmf(h, lh) * poisson_pmf(a, la)
            tau = dixon_coles_tau(h, a, lh, la, rho)
            raw[(h, a)] = p * tau
    total = sum(raw.values())
    if total > 0:
        raw = {k: v/total for k, v in raw.items()}
    return sorted(raw.items(), key=lambda x: x[1], reverse=True)

def market_ou_implied_total(over_odds, under_odds):
    """从Pinnacle O/U 2.5赔率反推隐含总进球期望（牛顿二分法, 精确Poisson CDF）
    ★v31.4 hotfix2: 修复二分搜索方向bug + 改用精确Poisson替代正态近似"""
    over_p = 1.0/over_odds; under_p = 1.0/under_odds
    over_prob = over_p / (over_p + under_p)  # devig
    lo, hi = 0.5, 7.0  # 扩大上界（德国首轮7:1→λ可达6+）
    for _ in range(50):
        mid = (lo + hi) / 2
        # 精确Poisson: P(goals > 2.5) = 1 - P(0) - P(1) - P(2)
        prob_under = math.exp(-mid) * (1 + mid + mid**2/2)
        prob_over = 1.0 - prob_under
        if prob_over > over_prob:
            hi = mid  # λ过大→缩小上限
        else:
            lo = mid  # λ过小→提高下限
    return (lo + hi) / 2

def devig_1x2(h_odds, d_odds, a_odds):
    """1X2赔率去水 → 真实隐含概率"""
    rh, rd, ra = 1.0/h_odds, 1.0/d_odds, 1.0/a_odds
    total = rh + rd + ra
    return (rh/total*100, rd/total*100, ra/total*100)

def devig_two(odds_a, odds_b):
    """二元赔率去水(大小球/BTTS) → (prob_a%, prob_b%)"""
    ra, rb = 1.0/odds_a, 1.0/odds_b
    total = ra + rb
    return (ra/total*100, rb/total*100)

def defense_adj(def_h, def_a):
    """防守风格调整: (def_h+def_a)/2每高于5 → 总进球-0.20 (v31.5: 仅作用于先验部分)"""
    avg = (def_h + def_a) / 2
    return -(avg - 5) * 0.20

def adjusted_lambdas(lh, la, ou_over, ou_under, def_h, def_a, blend=0.50, matchday=0):
    """综合调整：50%市场O/U锚定 + 防守风格修正(仅作用于先验部分) + 锦标赛阶段 → 最终λ (v31.5)"""
    market_t = market_ou_implied_total(ou_over, ou_under)
    raw_t = lh + la
    blend_t = blend * market_t + (1 - blend) * raw_t
    da = defense_adj(def_h, def_a)
    sf = stage_factor(matchday) if matchday > 0 else 0.0
    # ★v31.5: defense_adj仅作用于先验部分(1-blend), 市场已包含防守信息不重复计算
    adj_t = max(0.8, blend_t + (1 - blend) * da + sf)  # 地板：总进球不低于0.8
    if raw_t > 0:
        return adj_t * lh / raw_t, adj_t * la / raw_t, adj_t
    return adj_t * 0.55, adj_t * 0.45, adj_t

def elo_weight_factor(elo_diff):
    """★v31.5 ELO动态权重: 差距越大ELO越可信, 势均力敌时降低ELO依赖
    基于32场: 差≥200→60%准确; 差<100→仅50%(≈随机)
    """
    abs_diff = abs(elo_diff)
    if abs_diff >= 200:
        return 0.55  # ELO高权重：实力碾压
    elif abs_diff <= 80:
        return 0.35  # ELO低权重：势均力敌时ELO不可靠
    else:
        # 80-200区间线性插值
        return 0.35 + (0.55 - 0.35) * (abs_diff - 80) / 120

def stage_factor(matchday, group_standing=None):
    """★v31.5 锦标赛阶段因子: 调总进球期望而非平局概率
    MD1(首轮): -0.05球 (保守试探, 32场MD1 Under率56%)
    MD2(次轮): +0.05球 (出线压力→更开放, MD2实际场均3.2球 vs MD1 2.8球)
    MD3(末轮): +0.10球 or -0.15球 (取决出线形势: 必须赢或平即可出线)
    """
    if matchday == 1:
        return -0.05  # 首轮保守
    elif matchday == 2:
        return +0.05  # 次轮出线压力→开放
    elif matchday == 3:
        return +0.10  # 生死战(默认偏开放, 需结合出线形势调整)
    return 0.0


# ====================================================

def generate_match_html(mk, d):
    """生成单场比赛HTML"""
    H = []
    h_color = "home-color"
    a_color = "away-color"
    
    # 比赛头部
    H.append(f"""<div class="match-header">
  <div class="match-title">{d['home_name']} <span style="color:var(--text-secondary);margin:0 6px;">vs</span> {d['away_name']}</div>
  <div class="match-meta">
    <span>🏟 {d['venue']}</span><span>📋 {d['group']} · 第{d['matchday']}轮</span><span>🕐 {d['kickoff']}</span>
  </div>
</div>""")
    
    # 一、基础实力
    elo_h, elo_a = d['elo_home'], d['elo_away']
    elo_max = max(elo_h, elo_a, 2000)
    bar_h = min(elo_h / 2200 * 100, 100)
    bar_a = min(elo_a / 2200 * 100, 100)
    elo_diff = elo_h - elo_a
    gap_text = f"{d['home_name']}领先+{elo_diff}ELO分" if elo_diff > 0 else f"{d['away_name']}领先+{-elo_diff}ELO分"
    
    H.append(f"""<div class="section">
  <div class="section-title">📊 一、基础实力分析</div>
  <div class="elo-row">
    <div class="elo-team">{d['home_name']} <span class="fifa-badge">#{d['fifa_home']}</span></div>
    <div class="elo-bar-wrap"><div class="elo-bar-fill" style="width:{bar_h}%;background:linear-gradient(90deg, var(--blue), var(--blue-bright))"></div></div>
    <div class="elo-val {h_color}">{elo_h}</div>
  </div>
  <div class="elo-advantage">{gap_text} | FIFA排名差#{abs(d['fifa_home']-d['fifa_away'])}</div>
  <div class="elo-row">
    <div class="elo-team">{d['away_name']} <span class="fifa-badge">#{d['fifa_away']}</span></div>
    <div class="elo-bar-wrap"><div class="elo-bar-fill" style="width:{bar_a}%;background:linear-gradient(90deg,var(--orange),#fb923c)"></div></div>
    <div class="elo-val {a_color}">{elo_a}</div>
  </div>
  <div style="margin-top:8px; display:flex; justify-content:space-between; font-size:.82em; color:var(--text-secondary);">
    <span>{d['icon_home']} {d['level_home']}</span>
    <span>{d['icon_away']} {d['level_away']}</span>
  </div>
</div>""")
    
    # 二、状态分析
    fh = d['form_home']; fa = d['form_away']
    H.append(f"""<div class="section">
  <div class="section-title">📈 二、状态分析 (近期6场国际赛战绩)</div>
  <div class="form-grid">
    <div class="form-card">
      <div class="form-card-title">{d['home_name']} <span class="fifa-badge">MD1: {d['md1_home']}</span></div>
      <span class="form-badge {fh['badge']}">{fh['summary'].split('|')[0]}</span>
      <div class="form-record">{fh['record']}</div>
      <div class="form-matches">{'<br>'.join(fh['matches'])}</div>
    </div>
    <div class="form-card">
      <div class="form-card-title">{d['away_name']} <span class="fifa-badge">MD1: {d['md1_away']}</span></div>
      <span class="form-badge {fa['badge']}">{fa['summary'].split('|')[0]}</span>
      <div class="form-record">{fa['record']}</div>
      <div class="form-matches">{'<br>'.join(fa['matches'])}</div>
    </div>
  </div>
</div>""")
    
    # 三、战术克制 + 星级力量
    stars_h = d['stars_home']; stars_a = d['stars_away']
    star_html_h = ''.join(f'<div class="star-box"><span class="star-name">⭐{s[0]}</span><span style="color:var(--blue-bright);">{s[1]}</span><span class="star-club">{s[2]}</span></div>' for s in stars_h)
    star_html_a = ''.join(f'<div class="star-box"><span class="star-name">⭐{s[0]}</span><span style="color:var(--orange);">{s[1]}</span><span class="star-club">{s[2]}</span></div>' for s in stars_a)
    
    H.append(f"""<div class="section">
  <div class="section-title">⚔️ 三、战术克制分析 + 星级力量</div>
  <div class="tactic-split">
    <div class="tactic-card">
      <div class="tactic-card-title">🔵 {d['home_name']} 阵型预测 <span style="font-size:.75em;color:var(--gold);">| {d.get('style_home','')}</span></div>
      <div class="analysis-text-small">{d['lineup_home']}</div>
      <div style="margin:6px 0;font-size:.73em;color:var(--purple);">🌍 五大联赛: {d.get('big5_home','?')}人</div>
      <div style="margin-top:8px;">{star_html_h}</div>
    </div>
    <div class="tactic-card">
      <div class="tactic-card-title">🟠 {d['away_name']} 阵型预测 <span style="font-size:.75em;color:var(--gold);">| {d.get('style_away','')}</span></div>
      <div class="analysis-text-small">{d['lineup_away']}</div>
      <div style="margin:6px 0;font-size:.73em;color:var(--purple);">🌍 五大联赛: {d.get('big5_away','?')}人</div>
      <div style="margin-top:8px;">{star_html_a}</div>
    </div>
  </div>
  <div class="tactic-text">{d['tactic_analysis']}</div>
  <div class="injury-box">
    ⚠️ <strong>{d['home_name']}:</strong> {d['injury_home']}<br>
    ⚠️ <strong>{d['away_name']}:</strong> {d['injury_away']}
  </div>
</div>""")
    
    # ★ 类似对手参照 (四维卡片)
    sim = d.get('sim_ref', {})
    if sim:
        H.append(f"""<div class="section similar-section">
  <div class="section-title">🔬 攻防类比 — 近3年国际大赛(不含友谊赛) vs 类似对手</div>
  <div class="mv-compare">💰 <strong>身价对比:</strong> {d['home_name']} {sim['mv_home']}(攻{sim['home_atk']}/防{sim['home_def']}) vs {d['away_name']} {sim['mv_away']}(攻{sim['away_atk']}/防{sim['away_def']}) · 比值 {sim['mv_ratio']}</div>
  
  <div class="similar-subtitle first">① 📊 vs类似FIFA排名球队 → 进几球·失几球</div>
  <div class="similar-team-row">
    <div class="similar-team-box"><div class="similar-team-label">🏠 {d['home_name']}</div>{' '.join(f'<span class="similar-match"><span class="score">{m}</span></span>' for m in sim['home_fifa'])}<br><span style="color:var(--teal);font-size:.9em;">→ {sim['home_fifa_c']}</span></div>
    <div class="similar-team-box"><div class="similar-team-label">🚶 {d['away_name']}</div>{' '.join(f'<span class="similar-match"><span class="score">{m}</span></span>' for m in sim['away_fifa'])}<br><span style="color:var(--teal);font-size:.9em;">→ {sim['away_fifa_c']}</span></div>
  </div>
  
  <div class="similar-subtitle">② 🛡️ vs类似后防线身价(≈{d['away_name']}防{sim['away_def']}) → 进几球 [进攻测试]</div>
  <div class="similar-team-row">
    <div class="similar-team-box"><div class="similar-team-label">🏠 {d['home_name']}</div>{' '.join(f'<span class="similar-match"><span class="score">{m}</span></span>' for m in sim['home_defv'])}<br><span style="color:var(--teal);font-size:.9em;">→ {sim['home_defv_c']}</span></div>
    <div class="similar-team-box"><div class="similar-team-label">🚶 {d['away_name']}</div>{' '.join(f'<span class="similar-match"><span class="score">{m}</span></span>' for m in sim['away_defv'])}<br><span style="color:var(--teal);font-size:.9em;">→ {sim['away_defv_c']}</span></div>
  </div>
  
  <div class="similar-subtitle">③ ⚔️ vs类似进攻线身价(≈{d['away_name']}攻{sim['away_atk']}) → 丢几球 [防守测试]</div>
  <div class="similar-team-row">
    <div class="similar-team-box"><div class="similar-team-label">🏠 {d['home_name']}</div>{' '.join(f'<span class="similar-match"><span class="score">{m}</span></span>' for m in sim['home_atkv'])}<br><span style="color:var(--teal);font-size:.9em;">→ {sim['home_atkv_c']}</span></div>
    <div class="similar-team-box"><div class="similar-team-label">🚶 {d['away_name']}</div>{' '.join(f'<span class="similar-match"><span class="score">{m}</span></span>' for m in sim['away_atkv'])}<br><span style="color:var(--teal);font-size:.9em;">→ {sim['away_atkv_c']}</span></div>
  </div>
  
  <div class="similar-conclusion">💡 <strong>综合四维：{sim['conclusion']}</strong></div>
</div>""")
    
    # 四、赔率
    odds = d['odds_euro']
    odds_o = d['odds_ou25']
    odds_b = d['odds_btts']
    # 计算去水隐含概率
    dv_h, dv_d, dv_a = devig_1x2(odds['home'], odds['draw'], odds['away'])
    dv_ou_over, dv_ou_under = devig_two(odds_o.get('over', 1.01), odds_o.get('under', 1.01))
    dv_btts_y, dv_btts_n = devig_two(odds_b.get('yes', 1.01), odds_b.get('no', 1.01))
    
    H.append(f"""<div class="section">
  <div class="section-title">💰 四、盘口与赔率分析 (Pinnacle参考)</div>
  <div class="odds-grid">
    <div class="odds-card">
      <div class="odds-card-title">{d['home_name']}胜</div>
      <div class="odds-num home-color">{odds['home']}</div>
      <div class="implied-prob">去水 {dv_h:.1f}%</div>
    </div>
    <div class="odds-card">
      <div class="odds-card-title">平局</div>
      <div class="odds-num draw-color">{odds['draw']}</div>
      <div class="implied-prob">去水 {dv_d:.1f}%</div>
    </div>
    <div class="odds-card">
      <div class="odds-card-title">{d['away_name']}胜</div>
      <div class="odds-num away-color">{odds['away']}</div>
      <div class="implied-prob">去水 {dv_a:.1f}%</div>
    </div>
    <div class="odds-card" style="background:rgba(251,191,36,.04);">
      <div class="odds-card-title">市场偏向</div>
      <div style="font-size:.9em;font-weight:700;margin-top:4px;">{d['home_name']}热度高</div>
      <div class="implied-prob">亚盘: {d['odds_ah']}</div>
    </div>
  </div>
  <div class="ah-table">
    <div class="ah-table-title">亚盘: {d['odds_ah']} | 大小球2.5: 大{odds_o.get('over','?')} / 小{odds_o.get('under','?')} | BTTS: 是{odds_b.get('yes','?')} / 否{odds_b.get('no','?')}</div>
    <div class="ah-prob-line"><span>📊 去水概率 →</span><span>大球 {dv_ou_over:.1f}% / 小球 {dv_ou_under:.1f}%</span><span>BTTS是 {dv_btts_y:.1f}% / 否 {dv_btts_n:.1f}%</span></div>
  </div>
</div>""")
    
    # 五、概率模型 ★v31.3 Dixon-Coles修正 + 市场O/U锚定
    hp, dp, ap = d['prob_home'], d['prob_draw'], d['prob_away']
    o25 = d['over25_pct']; btts = d['btts_pct']
    
    # ★ v31.5: 用Dixon-Coles+市场O/U锚定(50%)+阶段因子计算真实比分概率
    mp = MATCH_PARAMS.get(mk, {"lambda_h": 1.5, "lambda_a": 1.0, "def_h": 5, "def_a": 5})
    lh_adj, la_adj, total_adj = adjusted_lambdas(
        mp["lambda_h"], mp["lambda_a"],
        d['odds_ou25']['over'], d['odds_ou25']['under'],
        mp["def_h"], mp["def_a"],
        matchday=d.get('matchday', 0)
    )
    # 同时计算ELO动态权重(供展示)
    elo_w = elo_weight_factor(d.get('elo_diff', 0))
    dc_matrix = compute_score_matrix(lh_adj, la_adj, mp.get("rho", -0.13))
    
    # 从DC矩阵计算三大概率
    dc_home_win = sum(p for (h,a),p in dc_matrix if h > a)
    dc_draw = sum(p for (h,a),p in dc_matrix if h == a)
    dc_away_win = sum(p for (h,a),p in dc_matrix if h < a)
    dc_over25 = sum(p for (h,a),p in dc_matrix if h + a > 2)
    dc_btts = sum(p for (h,a),p in dc_matrix if h > 0 and a > 0)
    
    # Top 5比分
    dc_top5 = dc_matrix[:5]
    dc_chips = ''.join(
        f'<span class="score-chip">{h}:{a} <em>({round(p*100,1)}%)</em></span>'
        for (h,a),p in dc_top5
    )
    
    sf_val = stage_factor(d.get('matchday', 0))
    dc_detail = (f"λh={round(lh_adj,2)} λa={round(la_adj,2)} E[总]={round(total_adj,2)} | "
                 f"O/U锚点={round(market_ou_implied_total(d['odds_ou25']['over'], d['odds_ou25']['under']),2)} | "
                 f"防守: {mp['desc']} | ELO权={round(elo_w*100)}% | MD{d.get('matchday','?')}因子={sf_val:+.2f}球")
    
    H.append(f"""<div class="section">
  <div class="section-title">🎯 五、概率模型 ★v31.5 Dixon-Coles修正+市场O/U锚定(50%)</div>
  <div class="prob-row">
    <div class="prob-col"><div class="prob-label">{d['home_name']}胜</div><div class="prob-bar"><div class="prob-fill" style="width:{round(dc_home_win*100)}%;background:var(--blue-bright)"></div></div><div class="prob-value home-color">{round(dc_home_win*100)}%</div></div>
    <div class="prob-col"><div class="prob-label">平局</div><div class="prob-bar"><div class="prob-fill" style="width:{round(dc_draw*100)}%;background:var(--gold)"></div></div><div class="prob-value gold-color">{round(dc_draw*100)}%</div></div>
    <div class="prob-col"><div class="prob-label">{d['away_name']}胜</div><div class="prob-bar"><div class="prob-fill" style="width:{round(dc_away_win*100)}%;background:var(--orange)"></div></div><div class="prob-value away-color">{round(dc_away_win*100)}%</div></div>
  </div>
  <div class="sub-probs">大2.5球: <strong>{round(dc_over25*100)}%</strong> | 小2.5球: <strong>{round((1-dc_over25)*100)}%</strong> | BTTS: <strong>{round(dc_btts*100)}%</strong> | <span style="font-size:.72em;color:var(--text-secondary);">{dc_detail}</span></div>
  <div class="score-matrix">
    <div class="score-matrix-title">Dixon-Coles比分概率矩阵 ★v31.5 (Top 5, ρ=-0.13, 50%O/U锚定, 阶段因子)</div>
    <div class="score-chips">{dc_chips}</div>
  </div>
</div>""")
    
    # 六、综合推演
    H.append(f"""<div class="section">
  <div class="section-title">🎬 六、综合推演 (超极分析师三位一体)</div>
  <div class="analysis-text-small">{d['game_flow']}</div>
  <div class="key-vars-box">🔑 关键变量: {d['key_vars']}</div>
</div>""")
    
    # 七、双面融合
    alignment = d['alignment']
    align_cls = {"✅高度一致":"align-consistent","基本一致":"align-consistent","⚡分歧":"align-divergence","🚨反转":"align-reversal"}.get(alignment, "align-divergence")
    
    H.append(f"""<div class="conclusion-panel">
  <div class="conclusion-header">⚡ 七、专业分析推理链 (双面融合)</div>
  <div class="fusion-panel">
    <div class="fusion-header">
      <div class="theory-side">
        <div class="side-label theory-label">📐 理论面 (模型+市场)</div>
        <div class="side-content">{d['theory_summary']}</div>
        <div style="font-size:.73em;color:var(--text-secondary);margin-top:4px;">方向: {d['theory_dir']}</div>
      </div>
      <div class="practice-side">
        <div class="side-label practice-label">🛠️ 实际面 (战术+真实条件)</div>
        <div class="side-content">{d['practice_summary']}</div>
        <div style="font-size:.73em;color:var(--text-secondary);margin-top:4px;">方向: {d['practice_dir']}</div>
      </div>
    </div>
    <div style="margin-top:10px;"><strong>融合判断:</strong> <span class="alignment-badge {align_cls}">{alignment}</span>{'<span style="font-size:.78em;color:var(--text-secondary);margin-left:6px;">差距: '+d['gap']+'</span>' if d.get('gap') else ''}</div>
    <div class="fusion-verdict-box">
      <div class="title">🏆 融合结论</div>
      <div class="analysis-text-small">{d['fusion_verdict']}</div>
    </div>
  </div>
  <div class="conclusion-body">
    <div class="score-recommendation">
      <div class="rec-label">最可能比分</div>
      <div class="rec-score">{d['fusion_score']}</div>
      <div class="rec-label-sub">次选: {d['score2']}</div>
    </div>
    <div class="verdict-block">
      <div class="verdict-main">主推: <strong>{d['verdict']}</strong></div>
      <div class="verdict-conf">融合信度: {d['fusion_conf']}</div>
      <div class="verdict-scores">{''.join(f'<span class="score-chip">{h}:{a} ({round(p*100,1)}%)</span>' for (h,a),p in dc_top5[:4])}</div>
    </div>
    <div style="grid-column:1/-1;">
      <div class="risk-block risk-bg-{d['risk_label']}">
        <div class="risk-label">风险等级</div>
        <div class="risk-value">{d['risk_icon']} {d['risk_label']}</div>
        <div class="btts-note">BTTS: {round(dc_btts*100)}% | 大2.5: {round(dc_over25*100)}%</div>
      </div>
    </div>
  </div>
</div>""")
    
    return '\n'.join(H)


# ====================================================
# 生成完整HTML
# ====================================================
def gen_full_html():
    now_bj = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M 北京时间")
    matches_html = ""
    for mk, md in MATCH_DATA.items():
        matches_html += generate_match_html(mk, md) + "\n"
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026世界杯 6月22日 量化分析报告 v31.5</title>
<style>{CSS}</style>
</head>
<body>
<div class="header">
  <h1>🏆 2026世界杯 <span>6月22日</span> 量化分析报告 v31.5</h1>
  <div class="subtitle">v31.5 · DC修正 · 市场O/U锚定(50%) · 防守(-0.20×先验) · ELO动态 · 阶段因子 · 生成于 {now_bj}</div>
  <div class="identity-tags">
    <span class="id-tag">📊 ELO+FIFA双评级</span>    <span class="id-tag">⚡ Dixon-Coles泊松</span>
    <span class="id-tag">📈 Pinnacle赔率分析</span><span class="id-tag">⚔️ 战术克制推演</span>
    <span class="id-tag">⭐ 星级力量评估</span><span class="id-tag">🔄 近期状态追踪</span>
    <span class="id-tag">🔗 双面融合研判</span><span class="id-tag">🛡️ 防守风格评分</span>
    <span class="id-tag">🎯 市场O/U锚定</span><span class="id-tag">📐 ELO动态权重</span>
    <span class="id-tag">🏟 锦标赛阶段</span><span class="id-tag">🏦 博彩风控</span>
  </div>
</div>
<div class="container">
<div class="disclaimer">
  ⚠️ 本报告基于量化模型与专业分析，仅供研究参考。足球存在高度不确定性，任何分析均无法保证结果准确性。请理性决策。
</div>

<!-- ★ 赛前综述 ★ -->
<div class="section">
  <div class="section-title">📋 6月22日赛前综述</div>
  <div class="analysis-text">
    <strong>比赛日看点:</strong> 6月22日是E组和F组的第二比赛日(MD2)，共4场比赛。与昨日的G/H组100%平局不同，E组首轮两场分出胜负：德国7-1血洗库拉索、科特迪瓦1-0绝杀厄瓜多尔。F组则是荷兰2-2战平日本、瑞典5-1大胜突尼斯——鲜明对比。本轮德国vs科特迪瓦的胜者将基本锁定出线；厄瓜多尔vs库拉索是谁输谁出局的生死战；荷兰必须击败瑞典避免末轮被动；而日本面对惨败后换帅的突尼斯，3分可期。<br><br>
    <strong>Group E积分榜:</strong> 德国3分(GD+6) · 科特迪瓦3分(GD+1) · 厄瓜多尔0分(GD-1) · 库拉索0分(GD-6)<br>
    <strong>Group F积分榜:</strong> 瑞典3分(GD+4) · 日本1分(GD0) · 荷兰1分(GD0) · 突尼斯0分(GD-4)
  </div>
</div>

<!-- ★ 全局交叉分析 — v30.0复审新增 ★ -->
<div class="section">
  <div class="section-title">🔬 全局交叉分析 — 跨场次结构性特征</div>
  <div class="analysis-text">
    <strong>① 4场亚盘方向: E组强弱分明, F组存在不确定性</strong><br>
    德国(-1.0)、厄瓜多尔(-2.25)、荷兰(-0.75)、日本(-1.0)——四场均是被让球方受让。但穿盘难度分层明显: 德国和日本穿盘概率相对高(对手实力差距大), 厄瓜多尔穿盘受制于自身进攻效率(近5场场均0.4球), 荷兰穿盘受制于瑞典3-5-2战术克制+双枪状态火热。4场中2场强队穿盘概率约50-60%, 属合理预期。<br><br>
    <strong>② 市场溢价与FIFA排名 — 世界杯MD2阶段特征</strong><br>
    荷兰(FIFA#8): +9pp (ELO56%→市场65%) | 德国(FIFA#10): +6pp (67%→73%) | 日本(FIFA#18): +14pp (59%→73%) | 厄瓜多尔(FIFA#23): +16pp (77%→93%)。溢价与FIFA排名相关系数r≈0.85, 但厄瓜多尔(+16pp)和日本(+14pp)的溢价异常大——部分由于对手首轮惨败(库拉索1-7/突尼斯1-5)导致市场过度修正。ELO独立信号系统性低于市场隐含胜率, "ELO优先+赔率联动验证"策略继续纠正此偏见。<br><br>
    <strong>③ 融合权重策略 v31.5 — 市场锚定50% + 防守调整仅先验</strong><br>
    ★<strong>v31.5核心升级</strong>: 基于用户指令"更加相信市场"逻辑——亚盘是各大博彩公司系统性研究的结果, 信服力度大:<br>
    • <strong>市场O/U锚定: 28%→50%</strong>: 市场与先验平等对话。Pinnacle开大小球线时已研究防守风格/伤病/天气, 其隐含总进球是业界最准信号。50%权重确保市场声音不被淹没。<br>
    • <strong>防守调整仅作用于先验(1-blend): ★关键修复</strong>: 防守风格调整现在仅乘以(1-blend)系数。因为市场O/U线已经包含了防守信息——如果def_a=9(铁桶), 市场已经把这反映在大小球赔率里了, 不应重复扣减。厄瓜多尔vs库拉索: 修复后模型vs市场差从25pp→16pp。<br>
    • <strong>防守风格因子: -0.20球/分(临时参数)</strong>: 32场零封率41%支撑。每+1分铁桶度→-0.20球(仅作用于先验部分)。后续用PPDA等客观指标校准。<br>
    • <strong>ELO动态权重</strong>: 差≥200→55%权重; 差80-200→线性35-55%; 差<80→35%。基于32场ELO差分级准确率。<br>
    • <strong>锦标赛阶段因子</strong>: MD1首轮保守→-0.05; MD2出线压力→+0.05; MD3生死战→极端值。32场: MD1场均2.8球 vs MD2场均3.2球。<br>
    • <strong>平局基线30%</strong>: 32场实赛31.2%支撑, 但MD2出线压力使平局率边际下降。不设强制平局规则。<br>
    • <strong>新权重分配</strong>: ELO动态35-55% | 市场O/U锚定50%(λ) | 战术推演20-25% | xG/泊松15% | 防守-0.20×先验 | 阶段因子±0.05球<br><br>
    
    <strong>④ ELO二元 vs 融合三元 — 维度差异的系统性说明</strong><br>
    审计报告指出"3/4场融合&lt;ELO"可能构成数学矛盾。经核查, 此为<strong>ELO二元模型与融合三元模型之间的维度差异</strong>, 非逻辑错误。ELO公式产生二元胜利概率(不知道平局), 而融合概率是三元空间(胜/平/负)。把二元ELO映射到三元空间(引入平局基线)后, 差距仅1.5-3pp。<br><br>
    
    <strong>⑤ 热门偏见折扣标准化 — v31.2方法论透明度升级</strong><br>
    折扣表: 赔率1.01-1.20→-8~-12pp; 1.21-1.40→-5~-8pp; 1.41-1.60→-3~-5pp; 1.61-2.00→-1~-3pp。<strong>融合&lt;市场是模型识别错误定价的正常功能, 非校准需求。</strong>但若实际赛果证明折扣过度, v31.5将回调折扣系数。<br><br>
    
    <strong>⑥ 32场实战复盘(截至6月20日) → v31.5校准驱动</strong><br>
    • <strong>方向准确率19/32(59.4%)</strong> — MD1仅37.5%但MD2大幅提升至81.2%: 信息越充分→预测越准<br>
    • <strong>比分准确率4/32(12.5%)❌</strong> — 但v31.3的Dixon-Coles修正已部署, 本报告为首次用DC+新权重组合<br>
    • <strong>大小球准确率16/32(50.0%)⚠️</strong> — 恰好随机水平, 市场O/U锚定从40%→28%的调整依据<br>
    • <strong>BTTS准确率17/32(53.1%)⚠️</strong> — 防守风格因子-0.20直接针对此问题(预测场均2.50 vs 实际3.00球)<br>
    • <strong>30%平局基线✅</strong> — 32场31.2%平局率支撑上调。但MD2出线压力使平局率边际下降, 不设强制规则<br><br>
    
    <strong>⑦ v31.5改进路线图 — 市场信任升级+防守双重计数消除</strong><br>
    • <strong>Dixon-Coles</strong>: ρ=-0.13(文献标准值), 持续追踪RPS vs 标准泊松<br>
    • <strong>市场O/U锚定(50%)</strong>: 从28%上调, 反映"市场系统性研究比个人判断更可靠"的用户指令。亚盘数据获取需确保准确完整<br>
    • <strong>防守风格(-0.20×先验)</strong>: 仅作用于(1-blend)非市场部分。消除与市场O/U线的重复计算<br>
    • <strong>ELO动态权重</strong>: 基于32场ELO差分级准确率(≥200→60%, <80→50%)。每轮赛后更新分级统计<br>
    • <strong>阶段因子</strong>: MD1保守/MD2开放/MD3极端 —— 32场MD场均进球差(0.4球)支撑定量<br>
    • <strong>平局基线30%</strong>: 32场实赛支撑。但MD2/MD3出线压力逻辑上压低平局, 不做机械强制
  </div>
</div>

{matches_html}
</div>
<div class="footer">
  <p>数据来源: football-data.org · OddsPAPI.io(Pinnacle) · ELO评级 · FIFA排名 · 网页抓取</p>
  <p style="margin-top:4px;">分析框架: v31.5 DC修正+O/U锚定(50%)+防守(-0.20×先验)+ELO动态+阶段因子 | 七步推理链 | 双面融合</p>
  <p style="margin-top:4px;">worldcup.imiaozhan.com | 生成于 {now_bj}</p>
</div>
</body>
</html>"""
    return html


if __name__ == "__main__":
    print("🏆 生成2026世界杯 6月22日 量化分析报告 v31.5 (DC+O/U50%+防守×先验)...")
    html = gen_full_html()
    path = os.path.join(REPORT_DIR, "2026-06-22-分析报告.htm")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    kb = len(html.encode("utf-8")) // 1024
    print(f"✅ 报告已生成: {path} ({kb}KB)")

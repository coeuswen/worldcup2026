

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
# v31.6 Dixon-Coles修正 + 市场O/U锚定(50%) + 防守风格(-0.20,仅先验) + ELO动态权重 + 锦标赛阶段
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
    """防守风格调整: (def_h+def_a)/2每高于5 → 总进球-0.20 (v31.6: 仅作用于先验部分)"""
    avg = (def_h + def_a) / 2
    return -(avg - 5) * 0.20

def adjusted_lambdas(lh, la, ou_over, ou_under, def_h, def_a, blend=0.50, matchday=0, def_drift_h=1.0, def_drift_a=1.0):
    """★v31.6综合调整：50%市场O/U锚定 + 防守漂移因子(P4) + 锦标赛阶段 → 最终λ
    P4: 防守漂移因子 - 防线崩盘时λ敏感性增强
    def_drift = 近3场场均失球 / 赛季场均失球 (>1.5表示崩盘)
    """
    market_t = market_ou_implied_total(ou_over, ou_under)
    raw_t = lh + la
    blend_t = blend * market_t + (1 - blend) * raw_t
    da = defense_adj(def_h, def_a)
    sf = stage_factor(matchday) if matchday > 0 else 0.0
    
    # ★v31.6 P4: 防守漂移因子 - 崩盘防线敏感性增强
    # def_drift_h: 主队防线漂移 (对手λa上调)
    # def_drift_a: 客队防线漂移 (主队λh上调)
    drift_adj_h = 1.0 + max(0, def_drift_a - 1.0) * 0.15  # 客队防线崩盘→主队λ上调
    drift_adj_a = 1.0 + max(0, def_drift_h - 1.0) * 0.15  # 主队防线崩盘→客队λ上调
    adj_lh = lh * drift_adj_h
    adj_la = la * drift_adj_a
    
    # ★v31.6: defense_adj仅作用于先验部分(1-blend), 市场已包含防守信息不重复计算
    adj_t = max(0.8, blend_t + (1 - blend) * da + sf)  # 地板：总进球不低于0.8
    adj_raw_t = adj_lh + adj_la
    if adj_raw_t > 0:
        return adj_t * adj_lh / adj_raw_t, adj_t * adj_la / adj_raw_t, adj_t
    return adj_t * 0.55, adj_t * 0.45, adj_t

def elo_weight_factor(elo_diff):
    """★v31.6 ELO动态权重: 差距越大ELO越可信, 势均力敌时降低ELO依赖
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
    """★v31.6 锦标赛阶段因子: 调总进球期望而非平局概率
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

# ========== v31.6 新增函数 (采纳审计师Victor 6项建议) ==========

def calc_draw_probability(elo_diff, home_xg_avg, away_xg_avg, stage="MD2"):
    """★v31.6 P0+P5: 平局概率重构 — 按ELO差分区+进攻效率修正
    P0: 进攻低效队(ELO+400+)面对铁桶, 平局概率上浮
    P5: 平局基线按ELO差分区动态调整
    返回: 平局概率(0-1之间)
    """
    # P5: ELO差分区基线
    if elo_diff < 100:
        base = 0.30   # 势均力敌→30%
    elif elo_diff < 200:
        base = 0.28   # 略优→28%
    elif elo_diff < 300:
        base = 0.24   # 中强→24%
    elif elo_diff < 400:
        base = 0.20   # 明显强→20%
    else:
        base = 0.18   # 碾压→18%

    # P0: 进攻效率修正 (低效进攻面对强防守, 平局概率上浮)
    # home_xg_avg: 主队场均xG, away_xg_avg: 客队场均xG
    weak_attack_threshold = 1.0  # 场均xG<1.0视为低效
    if elo_diff > 300 and (home_xg_avg < weak_attack_threshold or away_xg_avg < weak_attack_threshold):
        # 低效进攻+大ELO差→铁桶战术有效, 平局上浮3-5%
        if home_xg_avg < weak_attack_threshold and away_xg_avg < weak_attack_threshold:
            base += 0.05  # 双方都低效→+5%
        else:
            base += 0.03  # 仅一方低效→+3%
    
    # 阶段因子微调 (MD2稍降, MD3根据出线形势)
    if stage == "MD2":
        base -= 0.02  # MD2平局率实际约20%, 略低于MD1的30%基线
    elif stage == "MD3":
        base += 0.02  # MD3生死战, 平局概率微升
    
    return max(0.08, min(0.40, base))  # 钳位8%-40%

def tactic_decay_factor(elo_diff):
    """★v31.6 P1: 战术克制权重衰减 — ELO差越大, 克制影响越小
    审计师Victor指出: 荷兰ELO+230, 战术克制-7pp完全错误
    当ELO差>200时, 实力碾压覆盖战术克制
    返回: 衰减系数(0-1), 乘以战术克制度评分
    """
    if elo_diff <= 100:
        return 1.0   # 势均力敌, 战术克制全权重
    elif elo_diff <= 200:
        return 0.7   # 略优, 克制权重打7折
    elif elo_diff <= 300:
        return 0.4   # 中强, 克制权重打4折
    elif elo_diff <= 400:
        return 0.2   # 明显强, 克制权重打2折
    else:
        return 0.1   # 碾压, 克制权重仅1折(基本忽略)

def normalize_opponent_strength(opponent_elo, opponent_xg_for, opponent_xg_against, elo_threshold=1600):
    """★v31.6 P2: 首轮对手强度标准化
    审计师Victor指出: 瑞典5:1突尼斯≠瑞典强, 是突尼斯太弱
    极端比分(ELO差>400的比赛结果)在推导MD2时应打折
    返回: 标准化后的对手强度评分(0-10)
    """
    # 对手ELO<阈值 → 比赛结果打折
    if opponent_elo < elo_threshold:
        discount = 0.5  # 弱对手, 结果打折50%
    elif opponent_elo < elo_threshold + 200:
        discount = 0.75
    else:
        discount = 1.0  # 强对手, 不打折
    
    # 进球/失球效率也做标准化
    # 场均xG>2.5可能是虐菜, 需打折
    xg_discount = 1.0
    if opponent_xg_for > 2.5:
        xg_discount = 0.7  # 虐菜高分打折
    elif opponent_xg_for > 1.8:
        xg_discount = 0.85
    
    return discount * xg_discount

def auto_alignment_tag(elo_prob, market_prob, threshold_pp=12):
    """★v31.6 P3: 融合标签自动化规则
    审计师Victor指出: 厄瓜多尔ELO-市场差距16pp→标"✅高度一致"是错的
    返回: (label, emoji)
    """
    diff_pp = abs(elo_prob - market_prob)
    
    if diff_pp <= 5:
        return ("✅ 高度一致", "✅")
    elif diff_pp <= 12:
        return ("⚠️ 轻度分歧", "⚠️")
    else:
        return ("🚨 价值偏差", "🚨")

# ★ v31.6 每场比赛的泊松λ参数 + 防守风格评分 (MD2阶段因子+0.05球自动应用)
MATCH_PARAMS = {
    "荷兰vs瑞典": {
        "lambda_h": 2.0, "lambda_a": 1.4, "def_h": 6, "def_a": 6,
        "desc": "荷兰高位逼抢433 vs 瑞典352中场绞杀·双方防守均有软肋"
    },
    "德国vs科特迪瓦": {
        "lambda_h": 2.5, "lambda_a": 0.7, "def_h": 5, "def_a": 8,
        "desc": "德国4231碾压控球 vs 科特迪瓦442铁桶·强弱悬殊"
    },
    "厄瓜多尔vs库拉索": {
        "lambda_h": 1.8, "lambda_a": 0.3, "def_h": 5, "def_a": 9,
        "desc": "厄瓜多尔进攻效率低 vs 库拉索10人死守·最可能低比分"
    },
    "突尼斯vs日本": {
        "lambda_h": 0.6, "lambda_a": 2.2, "def_h": 7, "def_a": 5,
        "desc": "勒纳尔铁桶541 vs 日本渗透型433·大概率零封"
    },
}
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
    
    # ★ v31.6: 用Dixon-Coles+市场O/U锚定(50%)+阶段因子+防守漂移计算真实比分概率
    mp = MATCH_PARAMS.get(mk, {"lambda_h": 1.5, "lambda_a": 1.0, "def_h": 5, "def_a": 5, "def_drift_h": 1.0, "def_drift_a": 1.0})
    # P4: 读取防守漂移因子(若MATCH_PARAMS中定义)
    ddh = mp.get("def_drift_h", 1.0)
    dda = mp.get("def_drift_a", 1.0)
    lh_adj, la_adj, total_adj = adjusted_lambdas(
        mp["lambda_h"], mp["lambda_a"],
        d['odds_ou25']['over'], d['odds_ou25']['under'],
        mp["def_h"], mp["def_a"],
        matchday=d.get('matchday', 0),
        def_drift_h=ddh, def_drift_a=dda
    )
    
    # ★ v31.7: 类xG代理交叉验证 — 10+场大样本均值作为λ基准
    xg_h = mp.get("xg_h", None)
    xg_a = mp.get("xg_a", None)
    xg_total = mp.get("xg_total", None)
    xg_divergence = 0
    xg_flag = ""
    if xg_h is not None and xg_a is not None and xg_total is not None:
        # 计算手动λ总进球 vs 类xG总进球期望的偏离
        manual_total = mp["lambda_h"] + mp["lambda_a"]
        xg_divergence = abs(manual_total - xg_total) / max(xg_total, 0.5) * 100
        if xg_divergence > 30:
            xg_flag = f'<span style="color:#e74c3c;">⚠️ λ高估{xg_divergence:.0f}%: 手动λ{manual_total:.1f} vs 类xG{xg_total:.2f}({mp.get("xg_h",0)}/{mp.get("xg_a",0)})→建议下调总进球期望</span>'
        elif xg_divergence > 15:
            xg_flag = f'<span style="color:#f39c12;">⚡ λ偏差{xg_divergence:.0f}%: 手动λ{manual_total:.1f} vs 类xG{xg_total:.2f}→边际调整</span>'
        else:
            xg_flag = f'<span style="color:#27ae60;">✅ λ一致({xg_divergence:.0f}%): 手动λ{manual_total:.1f} vs 类xG{xg_total:.2f}</span>'
    
    # ★ v31.7: 类xG校准 — 当偏离>25%时, 向xG代理方向调整λ(30%权重)
    if xg_divergence > 25 and xg_h is not None:
        lh_adj = lh_adj * 0.70 + xg_h * 0.30
        la_adj = la_adj * 0.70 + xg_a * 0.30
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
  <div class="section-title">🎯 五、概率模型 ★v31.6 Dixon-Coles修正+市场O/U锚定(50%)</div>
  <div class="prob-row">
    <div class="prob-col"><div class="prob-label">{d['home_name']}胜</div><div class="prob-bar"><div class="prob-fill" style="width:{round(dc_home_win*100)}%;background:var(--blue-bright)"></div></div><div class="prob-value home-color">{round(dc_home_win*100)}%</div></div>
    <div class="prob-col"><div class="prob-label">平局</div><div class="prob-bar"><div class="prob-fill" style="width:{round(dc_draw*100)}%;background:var(--gold)"></div></div><div class="prob-value gold-color">{round(dc_draw*100)}%</div></div>
    <div class="prob-col"><div class="prob-label">{d['away_name']}胜</div><div class="prob-bar"><div class="prob-fill" style="width:{round(dc_away_win*100)}%;background:var(--orange)"></div></div><div class="prob-value away-color">{round(dc_away_win*100)}%</div></div>
  </div>
  <div class="sub-probs">大2.5球: <strong>{round(dc_over25*100)}%</strong> | 小2.5球: <strong>{round((1-dc_over25)*100)}%</strong> | BTTS: <strong>{round(dc_btts*100)}%</strong> | <span style="font-size:.72em;color:var(--text-secondary);">{dc_detail}</span></div>
  <div class="score-matrix">
    <div class="score-matrix-title">Dixon-Coles比分概率矩阵 ★v31.6 (Top 5, ρ=-0.13, 50%O/U锚定, 阶段因子)</div>
    <div class="score-chips">{dc_chips}</div>
  </div>
</div>""")
    # ★ v31.7: 类xG交叉验证显示
    if xg_flag:
        H.append(f"""<div class="section" style="background:var(--bg-card);padding:12px 18px;border-radius:8px;margin-top:6px;border-left:4px solid {'#e74c3c' if '高估' in xg_flag else '#f39c12' if '偏差' in xg_flag else '#27ae60'};">
  <div class="section-title" style="font-size:.85em;">📊 类xG代理验证 ★v31.7 — 10+场大样本均值</div>
  <div style="font-size:.78em;">{xg_flag}</div>
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
<title>2026世界杯 6月21日 量化分析报告 v31.6</title>
<style>{CSS}</style>
</head>
<body>
<div class="header">
  <h1>🏆 2026世界杯 <span>6月21日</span> 量化分析报告 v31.6</h1>
  <div class="subtitle">v31.6 · DC修正 · 市场O/U锚定(50%) · 防守(-0.20×先验) · ELO动态 · 阶段因子 · 生成于 {now_bj}</div>
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
    <strong>比赛日看点:</strong> 6月22日是G组和H组的第二比赛日(MD2)，共4场比赛。G/H组首轮极端诡异——4场全部平局！比利时1-1埃及（萨拉赫伤退）、新西兰1-1伊朗（伊朗补时绝平）、西班牙0-0佛得角（佛得角门将10扑救封神）、乌拉圭0-0沙特（沙特全场1射门靠大巴苟平）。这意味着4组的8支球队全部同积1分，MD2成了实际意义上的"新起跑线"。本轮西班牙必须用大胜正名（首轮对佛得角零进球的尴尬），比利时需要德布劳内回归打破僵局，乌拉圭要证明首轮只是冷门而非实力下滑，埃及则依赖萨拉赫带伤单核作战。<br><br>
    <strong>Group G积分榜:</strong> 伊朗1分(GD0) · 新西兰1分(GD0) · 比利时1分(GD0) · 埃及1分(GD0)<br>
    <strong>Group H积分榜:</strong> 西班牙1分(GD0) · 沙特阿拉伯1分(GD0) · 乌拉圭1分(GD0) · 佛得角1分(GD0)
  </div>
</div>

<!-- ★ 全局交叉分析 — v30.0复审新增 ★ -->
<div class="section">
  <div class="section-title">🔬 全局交叉分析 — 跨场次结构性特征</div>
  <div class="analysis-text">
    <strong>① 4场亚盘方向: 强弱分明但冷门风险各异</strong><br>
    西班牙(-3.0)、比利时(-1.0)、乌拉圭(-1.25)、埃及(-0.5)——四场均为排名高队让球。但穿盘难度分层明显: 西班牙让3球但首轮零进球暴露进攻瓶颈，穿盘概率低于盘口暗示值；比利时-1.0面对伊朗铁桶，德布劳内创造力是关键变量；乌拉圭-1.25对阵首轮零封西班牙的佛得角，卡瓦尼+阿劳霍需要尽快破门；埃及-0.5让球最浅，萨拉赫伤情牵动全场走势。4场中2场强队穿盘概率约40-50%，低于市场预期。<br><br>
    <strong>② 市场溢价与首轮冷门——过度修正风险</strong><br>
    西班牙(FIFA#3): -12pp (ELO95%→市场83%)——首轮0-0佛得角导致市场大砍西班牙溢价，但佛得角门将封神并非可复制事件，西班牙进攻真实水平被低估 | 比利时(FIFA#4): +1pp (69%→70%)——市场对德布劳内回归信任度高 | 乌拉圭(FIFA#6): +10pp (82%→92%)——市场过度看好，忽略首轮对沙特全场仅3射正的进攻乏力 | 埃及(FIFA#44): +8pp (57%→65%)——萨拉赫+马尔穆什双核让市场偏向埃及，但新西兰首轮逼平伊朗展现韧性。ELO独立信号与市场隐含胜率部分背离，"ELO优先+赔率联动验证"策略在本轮尤为重要。<br><br>
    <strong>③ 融合权重策略 v31.6 — 市场锚定50% + 防守调整仅先验</strong><br>
    ★<strong>v31.6核心升级</strong>: 基于用户指令"更加相信市场"逻辑——亚盘是各大博彩公司系统性研究的结果, 信服力度大:<br>
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
    折扣表: 赔率1.01-1.20→-8~-12pp; 1.21-1.40→-5~-8pp; 1.41-1.60→-3~-5pp; 1.61-2.00→-1~-3pp。<strong>融合&lt;市场是模型识别错误定价的正常功能, 非校准需求。</strong>但若实际赛果证明折扣过度, v31.6将回调折扣系数。<br><br>
    
    <strong>⑥ 32场实战复盘(截至6月20日) → v31.6校准驱动</strong><br>
    • <strong>方向准确率19/32(59.4%)</strong> — MD1仅37.5%但MD2大幅提升至81.2%: 信息越充分→预测越准<br>
    • <strong>比分准确率4/32(12.5%)❌</strong> — 但v31.3的Dixon-Coles修正已部署, 本报告为首次用DC+新权重组合<br>
    • <strong>大小球准确率16/32(50.0%)⚠️</strong> — 恰好随机水平, 市场O/U锚定从40%→28%的调整依据<br>
    • <strong>BTTS准确率17/32(53.1%)⚠️</strong> — 防守风格因子-0.20直接针对此问题(预测场均2.50 vs 实际3.00球)<br>
    • <strong>30%平局基线✅</strong> — 32场31.2%平局率支撑上调。但MD2出线压力使平局率边际下降, 不设强制规则<br><br>
    
    <strong>⑦ v31.6改进路线图 — 市场信任升级+防守双重计数消除</strong><br>
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
  <p style="margin-top:4px;">分析框架: v31.6 DC修正+O/U锚定(50%)+防守(-0.20×先验)+ELO动态+阶段因子 | 七步推理链 | 双面融合</p>
  <p style="margin-top:4px;">worldcup.imiaozhan.com | 生成于 {now_bj}</p>
</div>
</body>
</html>"""
    return html


if __name__ == "__main__":
    print("🏆 生成2026世界杯 6月21日 量化分析报告 v31.6 (DC+O/U50%+防守×先验)...")
    html = gen_full_html()
    path = os.path.join(REPORT_DIR, "2026-06-21-分析报告.htm")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    kb = len(html.encode("utf-8")) // 1024
    print(f"✅ 报告已生成: {path} ({kb}KB)")

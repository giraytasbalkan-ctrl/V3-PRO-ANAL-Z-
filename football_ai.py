# football_ai.py
import math

class MatchAnalyzer:
    def form_score(self, wins, draws, losses): return (wins * 3) + draws
    def attack_score(self, goals_for, matches): return 0 if matches == 0 else round(goals_for / matches, 2)
    def defence_score(self, goals_against, matches): return 0 if matches == 0 else round(goals_against / matches, 2)

    def expected_goals(self, team_attack, opp_defence, own_injury="Tam Kadro (Eksik Yok)", opp_injury="Tam Kadro (Eksik Yok)", h2h_hw=0, h2h_draw=0, h2h_aw=0, motivation="Orta Sıra / Rahat (Normal)", fatigue="Fikstür Rahat (Dinlenmiş)", league_mult=1.0, momentum_mult=1.0):
        xg_base = ((team_attack + opp_defence) / 2) * league_mult * momentum_mult
        
        if own_injury == "Hücumda 1 Kritik Eksik": xg_base *= 0.85
        elif own_injury == "Hücumda 2+ Eksik (Kriz)": xg_base *= 0.70
        elif own_injury == "Orta Sahada 1 Kritik Eksik": xg_base *= 0.90
        elif own_injury == "Orta Sahada 2+ Eksik (Kriz)": xg_base *= 0.80
            
        if opp_injury == "Savunmada 1 Kritik Eksik": xg_base *= 1.15
        elif opp_injury == "Savunmada 2+ Eksik (Kriz)": xg_base *= 1.30
        elif opp_injury == "Orta Sahada 1 Kritik Eksik": xg_base *= 1.10
        elif opp_injury == "Orta Sahada 2+ Eksik (Kriz)": xg_base *= 1.20
            
        if fatigue == "Hafta İçi Maç Yaptı (Yorgun)": xg_base *= 0.90
            
        if motivation == "Şampiyonluk / Kupa Yarışı (Yüksek)": xg_base *= 1.10
        elif motivation == "Kümede Kalma Savaşı (Kritik/Agresif)": xg_base *= 1.15
            
        total_h2h = h2h_hw + h2h_draw + h2h_aw
        if total_h2h > 0:
            h2h_diff = (h2h_hw - h2h_aw) / total_h2h  
            xg_base *= (1.0 + (h2h_diff * 0.10))      
            
        return round(xg_base, 2)
        
    def calculate_corners(self, home_xg, away_xg):
        home_corners = min(10.0, max(1.5, 3.0 + (home_xg * 1.5)))
        away_corners = min(10.0, max(1.5, 3.0 + (away_xg * 1.5)))
        total_corners = home_corners + away_corners
        
        if total_corners >= 10.0: corner_market = "🚩 9.5 ÜST"
        elif total_corners >= 8.5: corner_market = "⚖️ 8.5 - 9.5 Arası"
        else: corner_market = "🛡️ 8.5 ALT"
            
        return round(home_corners, 1), round(away_corners, 1), round(total_corners, 1), corner_market

    def live_chaos_xg(self, base_xg, minute):
        remaining_ratio = (90.0 - minute) / 90.0
        if minute >= 75:
            return base_xg * remaining_ratio * 1.25
        elif minute >= 60:
            return base_xg * remaining_ratio * 1.10
        return base_xg * remaining_ratio

    def advanced_probability_matrix(self, home_xg, away_xg, ht_home_xg, ht_away_xg, ht_zero_penalty=1.0):
        def poisson(lam, k):
            return (math.exp(-lam) * (lam ** k)) / math.factorial(k)
        
        adj_ht_home_xg = ht_home_xg * ht_zero_penalty
        adj_ht_away_xg = ht_away_xg * ht_zero_penalty
        
        tg_probs = {"TG 0-1": 0.0, "TG 2-3": 0.0, "TG 4-5": 0.0, "TG 6+": 0.0}
        score_matrix = {}
        ms_probs = {'1': 0.0, 'X': 0.0, '2': 0.0}
        over_25_p = 0.0
        combo_probs = {}
        heatmap_data = {}
        
        for h in range(8):
            for a in range(8):
                p = poisson(home_xg, h) * poisson(away_xg, a)
                score_matrix[f"{h} - {a}"] = (p, h, a, h + a)
                heatmap_data[f"{h}-{a}"] = p
                
                tot = h + a
                res = '1' if h > a else ('2' if a > h else 'X')
                
                if tot <= 1: tg_probs["TG 0-1"] += p
                elif tot <= 3: tg_probs["TG 2-3"] += p
                elif tot <= 5: tg_probs["TG 4-5"] += p
                else: tg_probs["TG 6+"] += p
                
                ms_probs[res] += p
                if tot >= 3: over_25_p += p
                
                c_15 = 'ALT' if tot <= 1 else 'ÜST'
                c_25 = 'ALT' if tot <= 2 else 'ÜST'
                c_35 = 'ALT' if tot <= 3 else 'ÜST'
                
                combo_probs[f"MS {res} ve 1.5 {c_15}"] = combo_probs.get(f"MS {res} ve 1.5 {c_15}", 0) + p
                combo_probs[f"MS {res} ve 2.5 {c_25}"] = combo_probs.get(f"MS {res} ve 2.5 {c_25}", 0) + p
                combo_probs[f"MS {res} ve 3.5 {c_35}"] = combo_probs.get(f"MS {res} ve 3.5 {c_35}", 0) + p

        under_25_p = 1.0 - over_25_p
        fair_odds = {
            'MS 1': round(1.0 / ms_probs['1'], 2) if ms_probs['1'] > 0 else 99.0,
            'MS X': round(1.0 / ms_probs['X'], 2) if ms_probs['X'] > 0 else 99.0,
            'MS 2': round(1.0 / ms_probs['2'], 2) if ms_probs['2'] > 0 else 99.0,
            '2.5 ÜST': round(1.0 / over_25_p, 2) if over_25_p > 0 else 99.0,
            '2.5 ALT': round(1.0 / under_25_p, 2) if under_25_p > 0 else 99.0
        }

        dominant_band = max(tg_probs, key=tg_probs.get)
        dominant_ms = max(ms_probs, key=ms_probs.get)
        
        band_ranges = {"TG 0-1": [0, 1], "TG 2-3": [2, 3], "TG 4-5": [4, 5], "TG 6+": range(6, 20)}
        allowed_goals = band_ranges[dominant_band]
        
        best_score = "0 - 0"
        max_score_weight = -1.0
        
        for score_str, (prob, h, a, total_goals) in score_matrix.items():
            if total_goals in allowed_goals:
                res = '1' if h > a else ('2' if a > h else 'X')
                weight = prob * (1.8 if res == dominant_ms else 1.0)
                if weight > max_score_weight:
                    max_score_weight = weight
                    best_score = score_str
                    
        ht_score_matrix = {}
        ht_over_15_p = 0.0
        ht_zero_zero_prob = 0.0
        ht_combo_probs = {}
        
        for h1 in range(5):
            for a1 in range(5):
                p_ht = poisson(adj_ht_home_xg, h1) * poisson(adj_ht_away_xg, a1)
                ht_score_matrix[f"{h1} - {a1}"] = p_ht
                tot_ht = h1 + a1
                ht_res = '1' if h1 > a1 else ('2' if a1 > h1 else '0')
                
                if h1 == 0 and a1 == 0: ht_zero_zero_prob = p_ht
                if tot_ht >= 2: ht_over_15_p += p_ht
                
                c_ht_15 = 'Alt' if tot_ht <= 1 else 'Üst'
                ht_combo_probs[f"İY {ht_res} ve 1.5 {c_ht_15}"] = ht_combo_probs.get(f"İY {ht_res} ve 1.5 {c_ht_15}", 0) + p_ht

        best_ht_score = max(ht_score_matrix, key=ht_score_matrix.get)
        total_ht_xg = adj_ht_home_xg + adj_ht_away_xg
        
        if ht_zero_zero_prob >= 0.40: ht_market = f"🔒 İY KİTLENİR (0-0 Adayı - %{int(ht_zero_zero_prob*100)})"
        elif total_ht_xg >= 1.15 and ht_over_15_p >= 0.35: ht_market = f"⚡ İY 1.5 ÜST (İY Skor: {best_ht_score})"
        elif total_ht_xg >= 0.90: ht_market = f"⚽ İY 0.5 ÜST (İY Skor: {best_ht_score})"
        else: ht_market = f"🔒 İY 1.5 ALT (İY Skor: {best_ht_score})"

        all_combos = {**combo_probs, **ht_combo_probs}
        sniper_candidates = []
        for name, prob in all_combos.items():
            if prob > 0.20:
                fair_odd = round(1.0 / prob, 2)
                if fair_odd < 5.0:
                    sniper_candidates.append({"name": name, "prob": prob, "odd": fair_odd})
                    
        sniper_candidates.sort(key=lambda x: x['prob'], reverse=True)
        
        final_snipers = []
        seen_base = set()
        for sc in sniper_candidates:
            base_type = sc['name'].split(' ve ')[0]
            if base_type not in seen_base:
                final_snipers.append(sc)
                seen_base.add(base_type)
            if len(final_snipers) == 3: break
            
        if len(final_snipers) < 3: final_snipers = sniper_candidates[:3]

        return best_score, best_ht_score, ht_market, tg_probs, fair_odds, ht_zero_zero_prob, final_snipers, heatmap_data

    # YENİ: MANUEL LABORATUVAR İÇİN ÖZEL DEV MATRİS FONKSİYONU
    def manual_probability_matrix(self, home_xg, away_xg, ht_home_xg, ht_away_xg):
        def poisson(lam, k):
            return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

        ms_probs = {'1': 0.0, 'X': 0.0, '2': 0.0}
        tg_probs = {"0-1": 0.0, "2-3": 0.0, "4-5": 0.0, "6+": 0.0}
        over_15, over_25, over_35 = 0.0, 0.0, 0.0
        kg_var_p = 0.0
        combo_25_kg = 0.0
        score_matrix = {}

        for h in range(8):
            for a in range(8):
                p = poisson(home_xg, h) * poisson(away_xg, a)
                score_matrix[f"{h}-{a}"] = p
                tot = h + a
                res = '1' if h > a else ('2' if a > h else 'X')
                ms_probs[res] += p

                if tot <= 1: tg_probs["0-1"] += p
                elif tot <= 3: tg_probs["2-3"] += p
                elif tot <= 5: tg_probs["4-5"] += p
                else: tg_probs["6+"] += p

                if tot > 1.5: over_15 += p
                if tot > 2.5: over_25 += p
                if tot > 3.5: over_35 += p
                if h > 0 and a > 0:
                    kg_var_p += p
                    if tot > 2.5:
                        combo_25_kg += p

        ht_probs = {'1': 0.0, 'X': 0.0, '2': 0.0}
        ht_over_05, ht_over_15 = 0.0, 0.0
        ht_kg_var_p = 0.0

        for h1 in range(6):
            for a1 in range(6):
                p_ht = poisson(ht_home_xg, h1) * poisson(ht_away_xg, a1)
                tot_ht = h1 + a1
                ht_res = '1' if h1 > a1 else ('2' if a1 > h1 else 'X')
                ht_probs[ht_res] += p_ht
                if tot_ht > 0.5: ht_over_05 += p_ht
                if tot_ht > 1.5: ht_over_15 += p_ht
                if h1 > 0 and a1 > 0: ht_kg_var_p += p_ht

        sh_home_xg = max(0, home_xg - ht_home_xg)
        sh_away_xg = max(0, away_xg - ht_away_xg)
        total_ht = ht_home_xg + ht_away_xg
        total_sh = sh_home_xg + sh_away_xg

        if total_sh > total_ht + 0.15: half_market = "İkinci Yarı Daha Gollü Geçer"
        elif total_ht > total_sh + 0.15: half_market = "İlk Yarı Daha Gollü Geçer"
        else: half_market = "Yarılar Eşit / Çok Yakın"

        return {
            "ms_1": ms_probs['1'], "ms_x": ms_probs['X'], "ms_2": ms_probs['2'],
            "iy_1": ht_probs['1'], "iy_x": ht_probs['X'], "iy_2": ht_probs['2'],
            "o15": over_15, "u15": 1-over_15, "o25": over_25, "u25": 1-over_25, "o35": over_35, "u35": 1-over_35,
            "iy_o05": ht_over_05, "iy_u05": 1-ht_over_05, "iy_o15": ht_over_15, "iy_u15": 1-ht_over_15,
            "kg_var": kg_var_p, "kg_yok": 1-kg_var_p, "iy_kg_var": ht_kg_var_p, "iy_kg_yok": 1-ht_kg_var_p,
            "tg": tg_probs, "combo_25_kg": combo_25_kg, "half_most": half_market, "heatmap": score_matrix
        }

    def confidence(self, form, attack, defence):
        score = 50 + form + (attack * 8) - (defence * 5)
        return round(max(0, min(100, score)))

    def real_comment(self, home, away, home_xg, away_xg):
        xg_diff = home_xg - away_xg
        if xg_diff >= 0.40: return f"🎯 **{home}** matematiği ve verileriyle net favori."
        elif xg_diff <= -0.40: return f"⚠️ **{away}** rakibine karşı istatistiksel üstünlüğe sahip."
        else: return f"⚔️ Taktiksel kördüğüm! Güç dengeleri ve veriler maçı ortada bırakıyor."
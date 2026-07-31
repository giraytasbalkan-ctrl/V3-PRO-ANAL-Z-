import math

class MatchAnalyzer:
    def form_score(self, wins, draws, losses): 
        # Form skoru sadece puan değil, aynı zamanda momentumdur.
        return (wins * 3) + draws

    def attack_score(self, goals_for, matches): 
        return 0 if matches == 0 else round(goals_for / matches, 2)
        
    def defence_score(self, goals_against, matches): 
        return 0 if matches == 0 else round(goals_against / matches, 2)

    def expected_goals(self, team_attack, opp_defence, team_form_pts, matches_played, own_injury="Tam Kadro (Eksik Yok)", opp_injury="Tam Kadro (Eksik Yok)", h2h_hw=0, h2h_draw=0, h2h_aw=0, motivation="Orta Sıra / Rahat (Normal)", fatigue="Fikstür Rahat (Dinlenmiş)", league_mult=1.0, momentum_mult=1.0):
        
        base_xg = ((team_attack + opp_defence) / 2) * league_mult * momentum_mult
        
        # Form Çarpanı: Takımın aldığı puanın maksimum puana oranına göre momentum hesaplanır.
        max_possible_pts = matches_played * 3
        if max_possible_pts > 0:
            form_ratio = team_form_pts / max_possible_pts
            # Form çarpanı xG'yi %15 artırabilir veya %15 azaltabilir.
            form_mult = 0.85 + (form_ratio * 0.30) 
            base_xg *= form_mult

        if own_injury == "Hücumda 1 Kritik Eksik": base_xg *= 0.85
        elif own_injury == "Hücumda 2+ Eksik (Kriz)": base_xg *= 0.70
        elif own_injury == "Orta Sahada 1 Kritik Eksik": base_xg *= 0.90
        elif own_injury == "Orta Sahada 2+ Eksik (Kriz)": base_xg *= 0.80
            
        if opp_injury == "Savunmada 1 Kritik Eksik": base_xg *= 1.15
        elif opp_injury == "Savunmada 2+ Eksik (Kriz)": base_xg *= 1.30
        elif opp_injury == "Orta Sahada 1 Kritik Eksik": base_xg *= 1.10
        elif opp_injury == "Orta Sahada 2+ Eksik (Kriz)": base_xg *= 1.20
            
        if fatigue == "Hafta İçi Maç Yaptı (Yorgun)": base_xg *= 0.90
            
        if motivation == "Şampiyonluk / Kupa Yarışı (Yüksek)": base_xg *= 1.10
        elif motivation == "Kümede Kalma Savaşı (Kritik/Agresif)": base_xg *= 1.15
            
        # Tarihsel Ağırlık (Zamanla sönen etki)
        total_h2h = h2h_hw + h2h_draw + h2h_aw
        if total_h2h > 0:
            h2h_diff = (h2h_hw - h2h_aw) / total_h2h  
            base_xg *= (1.0 + (h2h_diff * 0.05))      
            
        return round(base_xg, 2)
        
    def calculate_corners(self, home_xg, away_xg):
        # MANTIK DÜZELTMESİ: Sadece takımın kendi hücum potansiyeline (xG) odaklanan saf formül
        home_corners = min(11.0, max(2.5, 3.5 + (home_xg * 1.8)))
        away_corners = min(11.0, max(2.5, 3.0 + (away_xg * 1.8)))
        total_corners = home_corners + away_corners
        
        if total_corners >= 10.5: corner_market = "🚩 10.5 ÜST"
        elif total_corners >= 9.0: corner_market = "⚖️ 9 - 10 Arası"
        else: corner_market = "🛡️ 8.5 ALT"
            
        return round(home_corners, 1), round(away_corners, 1), round(total_corners, 1), corner_market

    def manual_probability_matrix(self, home_xg, away_xg, ht_home_xg, ht_away_xg):
        def poisson(lam, k):
            return (math.exp(-lam) * (lam ** k)) / math.factorial(k)
            
        # Dixon-Coles Düzeltme Algoritması (0-0, 1-0 gibi skorları gerçeğe uyarlar)
        def dixon_coles_correction(h_goals, a_goals, h_xg, a_xg, rho=0.15):
            if h_goals == 0 and a_goals == 0:
                return max(0, 1 - (h_xg * a_xg * rho))
            elif h_goals == 0 and a_goals == 1:
                return max(0, 1 + (h_xg * rho))
            elif h_goals == 1 and a_goals == 0:
                return max(0, 1 + (a_xg * rho))
            elif h_goals == 1 and a_goals == 1:
                return max(0, 1 - rho)
            return 1.0

        ms_probs = {'1': 0.0, 'X': 0.0, '2': 0.0}
        tg_probs = {"0-1": 0.0, "2-3": 0.0, "4-5": 0.0, "6+": 0.0}
        over_15, over_25, over_35 = 0.0, 0.0, 0.0
        kg_var_p = 0.0
        combo_25_kg = 0.0
        score_matrix = {}

        for h in range(8):
            for a in range(8):
                base_p = poisson(home_xg, h) * poisson(away_xg, a)
                p = base_p * dixon_coles_correction(h, a, home_xg, away_xg)
                
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

        total_prob = sum(ms_probs.values())
        if total_prob > 0:
            for k in ms_probs: ms_probs[k] /= total_prob
            for k in tg_probs: tg_probs[k] /= total_prob
            over_15 /= total_prob
            over_25 /= total_prob
            over_35 /= total_prob
            kg_var_p /= total_prob
            combo_25_kg /= total_prob
            for k in score_matrix: score_matrix[k] /= total_prob

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
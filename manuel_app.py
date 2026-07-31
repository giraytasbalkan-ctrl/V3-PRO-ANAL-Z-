import streamlit as st
import pandas as pd
import datetime
import hashlib
from football_ai import MatchAnalyzer

# --- 1. STREAMLIT SAYFA AYARI (EN BAŞTA OLMAK ZORUNDA) ---
st.set_page_config(page_title="Manuel Laboratuvar", page_icon="🧪", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="st-"] { font-size: 14px !important; }
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: bold; color: #00e676; }
        [data-testid="stMetricLabel"] { font-size: 0.95rem !important; opacity: 0.9; }
    </style>
""", unsafe_allow_html=True)

# --- 2. KULLANICI VERİTABANI ---
MUSTERILER = {
    "giray_admin": {
        "sifre": "patron123", # İçeri rahat girmen için geçici olarak düz metin bıraktık
        "bitis_tarihi": "2030-12-31" 
    },
    "ilk_musteri": {
        "sifre": "deneme20", # İçeri rahat girmen için geçici olarak düz metin bıraktık
        "bitis_tarihi": "2026-08-20" 
    }
}

# --- 3. GÜVENLİK KAPISI (LOGIN EKRANI) ---
def login_ekrani():
    st.markdown("<h1 style='text-align: center; color: #f39c12;'>Giray Taşbalkan | Veri Laboratuvarı</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white;'>V3 Pro Analiz Terminaline Giriş</h3>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        # .strip() komutu ile yanlışlıkla konulan boşlukları otomatik siliyoruz!
        kullanici_adi = st.text_input("Kullanıcı Adı").strip()
        sifre = st.text_input("Şifre", type="password").strip()
        submit_button = st.form_submit_button("Sisteme Giriş Yap")
        
        if submit_button:
            girilen_hash = hashlib.sha256(sifre.encode()).hexdigest()
            
            if kullanici_adi in MUSTERILER:
                kayitli_sifre = MUSTERILER[kullanici_adi]["sifre"]
                
                # AKILLI KONTROL: Sistem hem düz metni hem de güvenlik kodunu (hash) kabul eder
                if kayitli_sifre == girilen_hash or kayitli_sifre == sifre:
                    bitis_str = MUSTERILER[kullanici_adi]["bitis_tarihi"]
                    bitis_tarihi = datetime.datetime.strptime(bitis_str, "%Y-%m-%d").date()
                    bugun = datetime.date.today()
                    
                    if bugun <= bitis_tarihi:
                        st.session_state["logged_in"] = True
                        st.session_state["kullanici"] = kullanici_adi
                        st.success("✅ Şifre onaylandı! Terminale bağlanılıyor...")
                        st.rerun()
                    else:
                        st.error("⚠️ Süreniz Dolmuştur! VIP üyeliğe geçmek için lütfen iletişime geçin.")
                else:
                    st.error("❌ Hatalı şifre girdiniz!")
            else:
                st.error("❌ Hatalı kullanıcı adı girdiniz!")

# --- 4. VIP ALAN (MANUAL ANALİZ PROGRAMIN) ---
def ana_uygulama():
    st.sidebar.title(f"Hoş Geldin, {st.session_state['kullanici']}")
    st.sidebar.markdown("---")
    
    if st.session_state["kullanici"] == "giray_admin":
        with st.sidebar.expander("🔐 Yeni Müşteri Şifre Üretici"):
            st.write("Müşteriye vereceğiniz şifreyi yazın, sisteme eklenecek kod aşağıda çıksın.")
            yeni_sifre = st.text_input("Şifre Yazın:", type="password", key="new_pass")
            if yeni_sifre:
                st.code(hashlib.sha256(yeni_sifre.strip().encode()).hexdigest())
        st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Çıkış Yap"):
        st.session_state["logged_in"] = False
        st.rerun()

    st.title("🧪 Özel Veri Laboratuvarı (V3 Pro Motoru)")
    st.markdown("API'de olmayan amatör ligleri veya varsayımsal senaryoları burada özgürce test et.")
    st.markdown("---")

    def sf(p): return round(1.0 / p, 2) if p > 0.01 else 99.0
    def pct(p): return int(p * 100)

    with st.form("manuel_veri_formu"):
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🏠 Ev Sahibi Takım")
            st.write("📊 **Genel Sezon Performansı**")
            h_col1, h_col2, h_col3 = st.columns(3)
            h_m = h_col1.number_input("Oynanan Maç", min_value=1, value=10, key="hm")
            h_w = h_col2.number_input("Galibiyet", min_value=0, value=5, key="hw")
            h_d = h_col3.number_input("Beraberlik", min_value=0, value=3, key="hd")
            
            h_col4, h_col5 = st.columns(2)
            h_gf = h_col4.number_input("Toplam Atılan Gol", min_value=0, value=15, key="hgf")
            h_ga = h_col5.number_input("Toplam Yenilen Gol", min_value=0, value=10, key="hga")

            st.write("🏟️ **Sadece İç Saha Performansı**")
            hh_col1, hh_col2, hh_col3 = st.columns(3)
            hh_m = hh_col1.number_input("İç Saha Maç Sayısı", min_value=1, value=5, key="hhm")
            hh_gf = hh_col2.number_input("İç Saha Atılan", min_value=0, value=8, key="hhgf")
            hh_ga = hh_col3.number_input("İç Saha Yenilen", min_value=0, value=4, key="hhga")

        with c2:
            st.subheader("✈️ Deplasman Takımı")
            st.write("📊 **Genel Sezon Performansı**")
            a_col1, a_col2, a_col3 = st.columns(3)
            a_m = a_col1.number_input("Oynanan Maç ", min_value=1, value=10, key="am")
            a_w = a_col2.number_input("Galibiyet ", min_value=0, value=4, key="aw")
            a_d = a_col3.number_input("Beraberlik ", min_value=0, value=2, key="ad")
            
            a_col4, a_col5 = st.columns(2)
            a_gf = a_col4.number_input("Toplam Atılan Gol ", min_value=0, value=12, key="agf")
            a_ga = a_col5.number_input("Toplam Yenilen Gol ", min_value=0, value=14, key="aga")

            st.write("🚌 **Sadece Dış Saha Performansı**")
            aa_col1, aa_col2, aa_col3 = st.columns(3)
            aa_m = aa_col1.number_input("Dış Saha Maç Sayısı", min_value=1, value=5, key="aam")
            aa_gf = aa_col2.number_input("Dış Saha Atılan", min_value=0, value=5, key="aagf")
            aa_ga = aa_col3.number_input("Dış Saha Yenilen", min_value=0, value=8, key="aaga")
            
        submit = st.form_submit_button("🚀 Laboratuvar Analizini Başlat", use_container_width=True)

    if submit:
        if (h_w + h_d) > h_m:
            st.error("❌ HATA: Ev sahibi takımın Galibiyet ve Beraberlik toplamı oynanan maçtan büyük olamaz!")
            st.stop()
        if (a_w + a_d) > a_m:
            st.error("❌ HATA: Deplasman takımının Galibiyet ve Beraberlik toplamı oynanan maçtan büyük olamaz!")
            st.stop()
            
        with st.spinner("Yapay Zeka Laboratuvar Verilerini İşliyor..."):
            ai = MatchAnalyzer()
            
            h_att = ai.attack_score(h_gf, h_m)
            h_def = ai.defence_score(h_ga, h_m)
            h_loss = h_m - h_w - h_d
            h_form = ai.form_score(h_w, h_d, h_loss)
            
            a_att = ai.attack_score(a_gf, a_m)
            a_def = ai.defence_score(a_ga, a_m)
            a_loss = a_m - a_w - a_d
            a_form = ai.form_score(a_w, a_d, a_loss)
            
            home_xg = ai.expected_goals(h_att, a_def, h_form, h_m)
            away_xg = ai.expected_goals(a_att, h_def, a_form, a_m)
            
            h_ht_att = ai.attack_score(hh_gf * 0.42, hh_m)
            h_ht_def = ai.defence_score(hh_ga * 0.42, hh_m)
            a_ht_att = ai.attack_score(aa_gf * 0.42, aa_m)
            a_ht_def = ai.defence_score(aa_ga * 0.42, aa_m)
            
            ht_home_xg = round((h_ht_att + a_ht_def) / 2, 2)
            ht_away_xg = round((a_ht_att + h_ht_def) / 2, 2)
            
            h_corn, a_corn, total_corn, corn_market = ai.calculate_corners(home_xg, away_xg)
            res = ai.manual_probability_matrix(home_xg, away_xg, ht_home_xg, ht_away_xg)
            
            st.markdown("---")
            st.header("📈 Profesyonel Yapay Zeka Çıktıları")
            
            tab1, tab2, tab3 = st.tabs(["🎯 Ana ve Gol Pazarları", "🧩 Çifte Şans & Özel Pazarlar", "🌡️ Skor Isı Haritası"])
            
            with tab1:
                st.markdown("#### 1️⃣ Maç ve Yarı Sonucu (1-X-2)")
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                col1.metric("MS 1", sf(res['ms_1']), f"%{pct(res['ms_1'])}")
                col2.metric("MS X", sf(res['ms_x']), f"%{pct(res['ms_x'])}")
                col3.metric("MS 2", sf(res['ms_2']), f"%{pct(res['ms_2'])}")
                col4.metric("İY 1", sf(res['iy_1']), f"%{pct(res['iy_1'])}")
                col5.metric("İY X", sf(res['iy_x']), f"%{pct(res['iy_x'])}")
                col6.metric("İY 2", sf(res['iy_2']), f"%{pct(res['iy_2'])}")
                
                st.markdown("#### 2️⃣ Alt / Üst (Gol Limitleri)")
                u1, u2, u3, u4, u5, u6 = st.columns(6)
                u1.metric("1.5 ÜST", sf(res['o15']), f"%{pct(res['o15'])}")
                u2.metric("2.5 ÜST", sf(res['o25']), f"%{pct(res['o25'])}")
                u3.metric("3.5 ÜST", sf(res['o35']), f"%{pct(res['o35'])}")
                u4.metric("İY 0.5 ÜST", sf(res['iy_o05']), f"%{pct(res['iy_o05'])}")
                u5.metric("İY 1.5 ÜST", sf(res['iy_o15']), f"%{pct(res['iy_o15'])}")
                u6.metric("İY 1.5 ALT", sf(res['iy_u15']), f"%{pct(res['iy_u15'])}")
                
                st.markdown("#### 3️⃣ Karşılıklı Gol (KG) Pazarları")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("KG VAR", sf(res['kg_var']), f"%{pct(res['kg_var'])}")
                k2.metric("KG YOK", sf(res['kg_yok']), f"%{pct(res['kg_yok'])}")
                k3.metric("İY KG VAR", sf(res['iy_kg_var']), f"%{pct(res['iy_kg_var'])}")
                k4.metric("İY KG YOK", sf(res['iy_kg_yok']), f"%{pct(res['iy_kg_yok'])}")

            with tab2:
                st.markdown("#### 🛡️ Çifte Şans Seçenekleri")
                cs_1x = res['ms_1'] + res['ms_x']
                cs_12 = res['ms_1'] + res['ms_2']
                cs_x2 = res['ms_x'] + res['ms_2']
                iy_cs_1x = res['iy_1'] + res['iy_x']
                iy_cs_x2 = res['iy_x'] + res['iy_2']
                
                cs1, cs2, cs3, cs4, cs5 = st.columns(5)
                cs1.metric("MS 1-X", sf(cs_1x), f"%{pct(cs_1x)}")
                cs2.metric("MS 1-2", sf(cs_12), f"%{pct(cs_12)}")
                cs3.metric("MS X-2", sf(cs_x2), f"%{pct(cs_x2)}")
                cs4.metric("İY 1-X", sf(iy_cs_1x), f"%{pct(iy_cs_1x)}")
                cs5.metric("İY X-2", sf(iy_cs_x2), f"%{pct(iy_cs_x2)}")

                st.markdown("#### 📊 Toplam Gol Bantları")
                t1, t2, t3, t4 = st.columns(4)
                t1.metric("0-1 Gol", sf(res['tg']['0-1']), f"%{pct(res['tg']['0-1'])}")
                t2.metric("2-3 Gol", sf(res['tg']['2-3']), f"%{pct(res['tg']['2-3'])}")
                t3.metric("4-5 Gol", sf(res['tg']['4-5']), f"%{pct(res['tg']['4-5'])}")
                t4.metric("6+ Gol", sf(res['tg']['6+']), f"%{pct(res['tg']['6+'])}")
                
                st.markdown("#### 🔮 Sistem Özel Matrisi")
                sp1, sp2, sp3 = st.columns(3)
                sp1.metric("Korner Beklentisi", f"{total_corn} Adet", corn_market)
                sp2.metric("Yarı Hakimiyeti", res['half_most'])
                sp3.metric("Kombo: 2.5 ÜST ve KG VAR", sf(res['combo_25_kg']), f"%{pct(res['combo_25_kg'])}")

            with tab3:
                st.markdown("#### 🌡️ Maç Skoru Isı Haritası (İlk 5x5 İhtimal)")
                matrix = []
                for h in range(5):
                    row_data = {}
                    for a in range(5):
                        prob = res['heatmap'].get(f"{h}-{a}", 0) * 100
                        row_data[f"Dep {a} Gol"] = f"%{prob:.1f}"
                    matrix.append(row_data)
                df_heatmap = pd.DataFrame(matrix, index=[f"Ev {h} Gol" for h in range(5)])
                st.dataframe(df_heatmap, use_container_width=True)

# --- 5. MOTORUN BEYNİ (YÖNLENDİRİCİ) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_ekrani()
else:
    ana_uygulama()
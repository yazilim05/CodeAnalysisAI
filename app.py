"""
app.py
═══════════════════════════════════════════════════════════════════════════════
CodeAnalysis AI — Kurumsal Beyaz Tema & Kusursuz Hizalama (Final)
═══════════════════════════════════════════════════════════════════════════════
"""
import sys
import difflib
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(page_title='CodeAnalysis AI', page_icon='🤖', layout='wide', initial_sidebar_state='expanded')
st.markdown('\n<style>\n@import url(\'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@400;600;800&display=swap\');\n\n:root {\n    --bg-main:        #F8FAFC; \n    --bg-sidebar:     #FFFFFF; \n    --bg-card:        #FFFFFF; \n    --text-dark:      #0F172A; \n    --border-color:   #E2E8F0; \n    --primary-blue:   #4F46E5; \n    --danger-red:     #E11D48; \n    --success-green:  #10B981; \n    --warning-orange: #F59E0B; \n    --font-mono:      \'JetBrains Mono\', monospace;\n    --font-display:   \'Outfit\', sans-serif;\n}\n\nhtml, body, .stApp { background-color: var(--bg-main) !important; color: var(--text-dark) !important; }\np, span, div, li, h1, h2, h3, h4, h5, h6, label, .stMarkdown p { color: var(--text-dark) !important; font-family: var(--font-display) !important; }\n.block-container { padding: 1.5rem 3rem 8rem !important; max-width: 980px !important; }\n#MainMenu, footer, header { visibility: hidden; }\n\n[data-testid="stSidebar"] { background-color: var(--bg-sidebar) !important; border-right: 1px solid var(--border-color) !important; }\n[data-testid="stSidebar"] hr { border-color: var(--border-color) !important; }\n[data-testid="stSidebar"] .stTextInput > div > div > input { background-color: #F1F5F9 !important; border: 1px solid #CBD5E1 !important; color: var(--text-dark) !important; font-family: var(--font-mono) !important; border-radius: 6px !important; }\n[data-testid="stSidebar"] .stTextInput > div > div > input:focus { border-color: var(--primary-blue) !important; box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2) !important; }\n\n[data-testid="stSidebar"] .stButton > button { width: 100% !important; background-color: var(--primary-blue) !important; border: none !important; border-radius: 8px !important; padding: 0.6rem 1rem !important; transition: all 0.2s !important; }\n[data-testid="stSidebar"] .stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; font-size: 14px !important; text-transform: uppercase !important; }\n[data-testid="stSidebar"] .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important; }\n\n.btn-temizle .stButton > button { background-color: #64748B !important; }\n.btn-temizle .stButton > button * { color: #FFFFFF !important; }\n\n.refactor-buyuk-btn .stButton > button { width: 100% !important; background-color: var(--danger-red) !important; border: none !important; padding: 1.2rem 2rem !important; border-radius: 12px !important; transition: all 0.2s !important; }\n.refactor-buyuk-btn .stButton > button * { color: #FFFFFF !important; font-size: 16px !important; font-weight: 800 !important; text-transform: uppercase !important; }\n.refactor-buyuk-btn .stButton > button:hover { transform: scale(1.02) !important; box-shadow: 0 8px 20px rgba(225, 29, 72, 0.4) !important; }\n\n.dokumante-btn .stButton > button { width: 100% !important; background-color: var(--success-green) !important; border: none !important; padding: 1rem !important; border-radius: 10px !important; }\n.dokumante-btn .stButton > button * { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase !important; }\n.ayir-btn .stButton > button { width: 100% !important; background-color: var(--warning-orange) !important; border: none !important; padding: 1rem !important; border-radius: 10px !important; }\n.ayir-btn .stButton > button * { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase !important; }\n\n[data-testid="stChatMessageContent"] { background-color: var(--bg-card) !important; border: 1px solid var(--border-color) !important; border-radius: 12px !important; padding: 1.2rem 1.5rem !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important; }\n[data-testid="stExpander"] { background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; border-radius: 10px !important; }\n\n[data-testid="stCodeBlock"] { background-color: #F8FAFC !important; border: 1px solid #CBD5E1 !important; border-radius: 8px !important; }\n[data-testid="stCodeBlock"] pre { background-color: #F8FAFC !important; }\n[data-testid="stCodeBlock"] code, [data-testid="stCodeBlock"] span { color: #0F172A !important; background-color: transparent !important; text-shadow: none !important; font-family: var(--font-mono) !important; font-weight: 600 !important; }\ncode { font-family: var(--font-mono) !important; background: #E2E8F0 !important; color: #DC2626 !important; border-radius: 4px !important; padding: 2px 6px !important; font-weight: 700 !important; }\n\n[data-testid="metric-container"] { background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }\n[data-testid="metric-container"] label { font-weight: 700 !important; color: #64748B !important; }\n[data-testid="metric-container"] div { color: #0F172A !important; }\n</style>\n', unsafe_allow_html=True)

def _sema_cizdir(mermaid_kodu):
    """Otonom Docstring: _sema_cizdir metodu."""
    st.markdown("<h3 style='color:#0F172A; margin-bottom: 0;'>🗺️ Proje Bağımlılık Şeması</h3>", unsafe_allow_html=True)
    html_kodu = f"""\n    <div class="mermaid" style="display: flex; justify-content: center; background: white; padding-top: 10px;">\n        {mermaid_kodu}\n    </div>\n    <script type="module">\n        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';\n        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});\n    </script>\n    """
    components.html(html_kodu, height=350, scrolling=True)

def _ajan_basligi():
    """Otonom Docstring: _ajan_basligi metodu."""
    st.markdown('\n    <div style="display: flex; align-items: center; gap: 18px; padding: 1rem 0 1.5rem; margin-bottom: 1.5rem; border-bottom: 2px solid #E2E8F0;">\n        <div style="width: 56px; height: 56px; background-color: #4F46E5; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 28px; color: white;">🤖</div>\n        <div>\n            <div style="font-size: 1.8rem; font-weight: 800; color: #0F172A;">CodeAnalysis AI</div>\n            <div style="font-size: 13px; color: #4F46E5; font-weight:700;">Kurumsal Analiz & Otonom Refactor Motoru</div>\n        </div>\n    </div>\n    ', unsafe_allow_html=True)

def _bos_durum():
    """Otonom Docstring: _bos_durum metodu."""
    st.markdown('\n    <div style="text-align: center; padding: 5rem 2rem; background: #FFFFFF; border-radius: 20px; border: 2px dashed #CBD5E1;">\n        <div style="font-size: 4rem; margin-bottom: 1rem;">🔭</div>\n        <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A; margin-bottom: 0.5rem;">Sistem Hazır</div>\n        <div style="font-size: 15px; color: #64748B;">Sol panelden bir <b>Dosya Yolu</b> veya <b>Klasör Yolu</b> girerek analizi başlatın.</div>\n    </div>\n    ', unsafe_allow_html=True)

def _kategori_etiketi(kategori: str, seviye: str) -> str:
    """Otonom Docstring: _kategori_etiketi metodu."""
    renkler = {'kritik': ('#FFFFFF', '#E11D48'), 'uyari': ('#000000', '#F59E0B'), 'bilgi': ('#FFFFFF', '#3B82F6')}
    fg, bg = renkler.get(seviye, ('#FFFFFF', '#64748B'))
    return f'<span style="display:inline-block;background:{bg};color:{fg};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:800;text-transform:uppercase;">{kategori}</span>'

def _diff_goster(once: str, sonra: str):
    """Otonom Docstring: _diff_goster metodu."""
    st.markdown("<div style='margin: 2rem 0 1rem; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px;'><span style='font-size: 1.3rem; font-weight: 800; color: #0F172A;'>📐 Önce / Sonra Karşılaştırması</span></div>", unsafe_allow_html=True)
    sol, sag = st.columns(2)
    with sol:
        st.markdown("<div style='color:#E11D48; font-weight:800; margin-bottom:5px;'>📜 Orijinal Kod</div>", unsafe_allow_html=True)
        st.code(once, language='python', line_numbers=True)
    with sag:
        st.markdown("<div style='color:#10B981; font-weight:800; margin-bottom:5px;'>✨ Düzeltilmiş (Refactored) Kod</div>", unsafe_allow_html=True)
        st.code(sonra, language='python', line_numbers=True)

def _ajan_yukle():
    """Otonom Docstring: _ajan_yukle metodu."""
    for aday in [Path('core/agent.py'), Path(__file__).parent / 'core' / 'agent.py']:
        if aday.exists():
            if str(aday.parent) not in sys.path:
                sys.path.insert(0, str(aday.parent))
            try:
                import importlib
                import core.agent as ga
                importlib.reload(ga)
                return ga
            except Exception as e:
                return None
    return None

def _state_temizle_callback():
    """Otonom Docstring: _state_temizle_callback metodu."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def _sidebar():
    """Otonom Docstring: _sidebar metodu."""
    with st.sidebar:
        st.markdown("<div style='text-align: center; margin-bottom: 1.5rem;'><h2 style='color:#0F172A; font-weight:800; margin:0;'>CodeAnalysis</h2></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#4F46E5; margin-bottom:5px;'>📄 Tek Dosya Analizi</h4>", unsafe_allow_html=True)
        dosya_yolu = st.text_input('Dosya Yolu', key='dosya_yolu_input', label_visibility='collapsed', placeholder='örn. src/app.py')
        dosya_incele = st.button('🔭 Dosyayı İncele', use_container_width=True, key='btn_dosya_incele')
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#4F46E5; margin-bottom:5px;'>📁 Klasör Analizi</h4>", unsafe_allow_html=True)
        klasor_yolu = st.text_input('Klasör Yolu', key='klasor_yolu_input', label_visibility='collapsed', placeholder='örn. ./projem')
        klasor_incele = st.button('🔭 Projeyi İncele', use_container_width=True, key='btn_klasor_incele')
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="btn-temizle">', unsafe_allow_html=True)
        st.button('🗑 EKRANI TEMİZLE', use_container_width=True, key='btn_sifirla', on_click=_state_temizle_callback)
        st.markdown('</div>', unsafe_allow_html=True)
        return {'dosya_yolu': dosya_yolu, 'dosya_incele': dosya_incele, 'klasor_yolu': klasor_yolu, 'klasor_incele': klasor_incele}

def _tek_dosya_analizini_baslat(ga_modul, yol_str: str):
    """Otonom Docstring: _tek_dosya_analizini_baslat metodu."""
    for k in ['refactor_sonuc', 'dokumantasyon_sonuc', 'ayirma_sonuc']:
        if k in st.session_state:
            del st.session_state[k]
    yol = Path(yol_str.strip())
    if not yol.exists():
        st.error('❌ Dosya bulunamadı.')
        return
    with st.spinner('🔍 Mimari yapı inceleniyor...'):
        try:
            ajan = ga_modul.GelismisAjan(str(yol))
            elestiriler, metrikler = ajan.analiz_et()
            kusursuz, sebepler = ajan.kusursuz_mu()
            st.session_state.update({'mod': 'tek_dosya', 'elestiriler': elestiriler, 'metrikler': metrikler, 'aktif_dosya': str(yol), 'kusursuz': kusursuz, 'kusursuz_sebepler': sebepler})
        except Exception as e:
            st.error(f'❌ Hata: {e}')

def _klasor_analizini_baslat(klasor_str: str):
    """Otonom Docstring: _klasor_analizini_baslat metodu."""
    for k in ['refactor_sonuc', 'dokumantasyon_sonuc', 'ayirma_sonuc', 'elestiriler', 'aktif_dosya', 'kusursuz', 'kusursuz_sebepler', 'metrikler']:
        if k in st.session_state:
            del st.session_state[k]
    klasor = Path(klasor_str.strip())
    if not klasor.exists():
        st.error('❌ Klasör bulunamadı.')
        return
    st.session_state.update({'mod': 'klasor', 'aktif_klasor': str(klasor)})

def _render_tek_dosya_modu(ga_modul):
    """Otonom Docstring: _render_tek_dosya_modu metodu."""
    elestiriler, aktif_dosya = (st.session_state.get('elestiriler', []), st.session_state.get('aktif_dosya'))
    metrikler = st.session_state.get('metrikler', {})
    if not aktif_dosya:
        return
    st.markdown(f'### 📄 `{Path(aktif_dosya).name}` Detaylı Raporu')
    if metrikler:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Satır Sayısı (LOC)', metrikler.get('loc', 0))
        c2.metric('Sınıf Sayısı', metrikler.get('sinif_sayisi', 0))
        c3.metric('Fonksiyon Sayısı', metrikler.get('fonksiyon_sayisi', 0))
        cc_val = metrikler.get('cc_max', 0)
        spagetti_durumu = '🍝 Spagetti Riski!' if cc_val > 10 else '✨ Temiz Kod'
        delta_color = 'inverse' if cc_val > 10 else 'normal'
        c4.metric('Max Karmaşıklık (CC)', cc_val, spagetti_durumu, delta_color=delta_color)
    st.markdown('<hr>', unsafe_allow_html=True)
    if not elestiriler:
        st.success('Bu kod yapısal açıdan kusursuz. Eleştirilecek bir şey bulamadım!')
    for sira, e in enumerate(elestiriler, 1):
        baslik_renk = {'kritik': '#E11D48', 'uyari': '#D97706', 'bilgi': '#2563EB'}.get(e.seviye, '#0F172A')
        with st.chat_message('assistant', avatar='🤖'):
            st.markdown(f'<div style="margin-bottom:10px;">{_kategori_etiketi(e.kategori, e.seviye)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:1.15rem;font-weight:800;color:{baslik_renk};margin-bottom:8px;">{e.baslik}</div>', unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:15px;color:#334155;'>{e.mesaj}</span>", unsafe_allow_html=True)
            if e.cozum:
                st.markdown(f'<div style="margin-top:12px;padding-top:10px;border-top:1px dashed #E2E8F0;"><span style="color:#0F172A;font-weight:800;font-size:14px;">💡 Çözüm:</span> <span style="color:#475569;">{e.cozum}</span></div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    if 'refactor_sonuc' not in st.session_state:
        if st.session_state.get('kusursuz'):
            st.success('🎉 Otonom tamir gerektiren (AST ile düzeltilebilecek) yapısal bir kusur bulunamadı.')
        else:
            st.info("Bu dosyada otonom olarak düzeltilebilecek iç içe IF blokları veya eksik docstring'ler tespit edildi.")
            st.markdown('<div class="refactor-buyuk-btn">', unsafe_allow_html=True)
            if st.button('✨ KODU OTONOM OLARAK TAMİR ET (Değişiklikler Mevcut Dosyaya Kaydedilir)', key='btn_refactor_tamir', use_container_width=True):
                with st.spinner('🔬 Otonom ameliyat yapılıyor... Mevcut dosyanız güncelleniyor...'):
                    try:
                        ajan = ga_modul.GelismisAjan(aktif_dosya)
                        sonuc = ajan.refactor_et()
                        st.session_state['refactor_sonuc'] = {'basarili': sonuc.basarili, 'once_kod': sonuc.once_kod, 'sonra_kod': sonuc.sonra_kod, 'yedek_yolu': sonuc.yedek_yolu, 'islem_listesi': sonuc.islem_listesi, 'hata_mesaji': sonuc.hata_mesaji}
                        if sonuc.basarili:
                            st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f'❌ Hata: {e}')
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        sonuc = st.session_state['refactor_sonuc']
        if not sonuc['basarili']:
            st.error(f"**Başarısız oldu.**\n\n{sonuc['hata_mesaji']}")
        else:
            st.success('✅ **Değişiklikler mevcut projedeki dosyaya başarıyla kaydedildi!**')
            st.markdown('### Uygulanan İşlemler:')
            for islem in sonuc['islem_listesi']:
                st.markdown(f'- **{islem}**')
            st.markdown(f"\n📦 **Orijinal Kodun Yedeği:** `{sonuc['yedek_yolu']}`")
            _diff_goster(sonuc['once_kod'], sonuc['sonra_kod'])

def _render_klasor_modu(ga_modul):
    """Otonom Docstring: _render_klasor_modu metodu."""
    aktif_klasor = st.session_state.get('aktif_klasor')
    if not aktif_klasor:
        return
    with st.chat_message('assistant', avatar='📁'):
        st.markdown(f"<span style='font-size:16px;'>**`{Path(aktif_klasor).name}`** klasörü hedeflendi. İşlemi seçin:</span>", unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    col_doc, col_ayir = st.columns(2)
    with col_doc:
        st.markdown('<div class="dokumante-btn">', unsafe_allow_html=True)
        if st.button('📚 PROJEYİ DETAYLI README YAP', key='btn_dokumante', use_container_width=True):
            with st.spinner('📚 README.md üretiliyor...'):
                try:
                    sonuc = ga_modul.GelismisAjan.projeyi_dokumante_et(aktif_klasor)
                    st.session_state['dokumantasyon_sonuc'] = {'basarili': sonuc.basarili, 'cikti_yolu': sonuc.cikti_yolu, 'taranan_dosya': sonuc.taranan_dosya, 'sinif_sayisi': sonuc.sinif_sayisi, 'fonksiyon_sayisi': sonuc.fonksiyon_sayisi, 'md_uzunlugu': sonuc.md_uzunlugu, 'mermaid_kodu': sonuc.mermaid_kodu, 'hata_mesaji': sonuc.hata_mesaji}
                    if sonuc.basarili:
                        st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f'❌ Hata: {e}')
        st.markdown('</div>', unsafe_allow_html=True)
    with col_ayir:
        st.markdown('<div class="ayir-btn">', unsafe_allow_html=True)
        ayir_basildi = st.button("✂️ GOD CLASS'LARI AYIR", key='btn_ayir', use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    hedef_dosya_input = st.text_input('Ayırma Hedefi (Sadece Ayırma Butonu İçin Gereklidir)', key='ayirma_hedef_input', placeholder='örn. src/big_module.py')
    if ayir_basildi and st.session_state.get('ayirma_hedef_input'):
        with st.spinner('✂️ Analiz yapılıyor...'):
            try:
                ajan = ga_modul.GelismisAjan(str(Path(st.session_state['ayirma_hedef_input'])))
                sonuc = ajan.komponentlere_ayir(metod_esigi=10)
                st.session_state['ayirma_sonuc'] = {'basarili': sonuc.basarili, 'once_kod': sonuc.once_kod, 'sonra_kod': sonuc.sonra_kod, 'yedek_yolu': sonuc.yedek_yolu, 'olusturulan_dosyalar': sonuc.olusturulan_dosyalar, 'ayrilan_sinif_sayisi': sonuc.ayrilan_sinif_sayisi, 'hata_mesaji': sonuc.hata_mesaji}
                if sonuc.basarili and sonuc.ayrilan_sinif_sayisi > 0:
                    st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f'❌ Hata: {e}')
    if 'dokumantasyon_sonuc' in st.session_state:
        sonuc = st.session_state['dokumantasyon_sonuc']
        if not sonuc['basarili']:
            st.error(f"**Hata:**\n\n{sonuc['hata_mesaji']}")
        else:
            st.success(f"**README.md Başarıyla Projenizin İçine Üretildi!** (Dosya: `{sonuc['cikti_yolu']}`)")
            if sonuc.get('mermaid_kodu'):
                _sema_cizdir(sonuc['mermaid_kodu'])
            try:
                md_metni = Path(sonuc['cikti_yolu']).read_text(encoding='utf-8')
                st.markdown("<div style='margin-top: -40px;'></div>", unsafe_allow_html=True)
                with st.expander('📖 README Önizleme (Genişletmek için tıklayın)', expanded=False):
                    st.markdown(md_metni)
            except:
                pass
    if 'ayirma_sonuc' in st.session_state:
        sonuc = st.session_state['ayirma_sonuc']
        if not sonuc['basarili']:
            st.error(f"**Hata:**\n\n{sonuc['hata_mesaji']}")
        elif sonuc['ayrilan_sinif_sayisi'] == 0:
            st.info('**Ayrılacak God Class bulunamadı.** (Sınıflar makul boyutta).')
        else:
            st.success(f"### {sonuc['ayrilan_sinif_sayisi']} sınıf ayrı dosyalara çıkarıldı ve Orijinal Dosyaya Kaydedildi.")
            for sinif_adi, dosya_yolu in sonuc['olusturulan_dosyalar']:
                st.markdown(f'- 🧱 `{sinif_adi}` → 📄 `{Path(dosya_yolu).name}`')
            st.markdown(f"\n📦 **Yedek:** `{sonuc['yedek_yolu']}`")
            _diff_goster(sonuc['once_kod'], sonuc['sonra_kod'])

def main():
    """Otonom Docstring: main metodu."""
    _ajan_basligi()
    sb = _sidebar()
    ga = _ajan_yukle()
    if ga is None:
        return
    if sb['dosya_incele'] and sb['dosya_yolu']:
        _tek_dosya_analizini_baslat(ga, sb['dosya_yolu'])
    if sb['klasor_incele'] and sb['klasor_yolu']:
        _klasor_analizini_baslat(sb['klasor_yolu'])
    mod = st.session_state.get('mod')
    if mod == 'tek_dosya':
        _render_tek_dosya_modu(ga)
    elif mod == 'klasor':
        _render_klasor_modu(ga)
    else:
        _bos_durum()
if __name__ == '__main__':
    main()
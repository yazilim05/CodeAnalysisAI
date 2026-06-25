"""
mimari_rontgen.py
═══════════════════════════════════════════════════════════════════════════════
Otonom Mühendislik Ajanı — Mimari Röntgen Modülü
Katman: Dependency Graph + Topoloji Analizi

Görev:
    Bir Python projesinin dosyalar arası import ilişkilerini yönlü graf
    (DiGraph) olarak modelleyip matematiksel topoloji analizi yapar:
    - Döngüsel Bağımlılık (Circular Dependency) tespiti
    - God Object tespiti (Betweenness + In-degree Centrality)
    - Instability skoru (Martin metriği: Ce / Ca + Ce)
    - PNG olarak görsel harita çıktısı

Bağımlılıklar:
    pip install networkx matplotlib

Kullanım:
    python mimari_rontgen.py ./proje_klasoru
    ──── veya API olarak ────
    from mimari_rontgen import MimariRontgen
    rontgen = MimariRontgen("./src")
    rapor   = rontgen.analiz_et()
═══════════════════════════════════════════════════════════════════════════════
"""

import ast
import sys
import math
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import networkx as nx

try:
    import matplotlib
    matplotlib.use("Agg")                       # Ekransız (headless) render
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import LinearSegmentedColormap
    MPL_MEVCUT = True
except ImportError:
    MPL_MEVCUT = False
    print("[UYARI] matplotlib bulunamadı — PNG çıktısı devre dışı.")


# ══════════════════════════════════════════════════════════════════════════════
# SABITLER — Aşama 2 matematiksel eşikleri
# ══════════════════════════════════════════════════════════════════════════════

ESIK_GOD_OBJECT_INDEGREE   = 5      # Kaç dosya import ederse "God Object"
ESIK_BETWEENNESS_KRITIK    = 0.30   # Betweenness Centrality üst sınırı
ESIK_INSTABILITY_KIRILGAN  = 0.80   # Martin: I → 1.0 = tamamen kararsız


# ══════════════════════════════════════════════════════════════════════════════
# 1. VERİ YAPILARI
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class DugumAnalizi:
    """Tek bir .py dosyasına ait graf ve metrik özeti."""
    ad:               str
    in_degree:        int   = 0      # Kaç modül bu dosyayı import eder (afferent)
    out_degree:       int   = 0      # Bu dosya kaç modülü import eder (efferent)
    betweenness:      float = 0.0    # Ağ içindeki köprü rolü
    instability:      float = 0.0    # Ce / (Ca + Ce)  [Martin metriği]
    god_object:       bool  = False
    kritik_kopru:     bool  = False  # Betweenness > eşik
    dongusel:         bool  = False  # Herhangi bir döngünün içinde mi?


@dataclass
class AnalizRaporu:
    """Tüm proje topoloji analiz sonuçları."""
    proje_yolu:         str
    dosya_sayisi:       int                    = 0
    kenar_sayisi:       int                    = 0
    dongusel_baglar:    list[list[str]]        = field(default_factory=list)
    god_objects:        list[DugumAnalizi]     = field(default_factory=list)
    kritik_koprular:    list[DugumAnalizi]     = field(default_factory=list)
    kirilgan_moduller:  list[DugumAnalizi]     = field(default_factory=list)
    tum_dugumler:       list[DugumAnalizi]     = field(default_factory=list)
    saglik_puani:       float                  = 100.0
    png_yolu:           Optional[str]          = None

    # ── Sağlık puanı hesaplama ───────────────────────────────────
    def saglik_hesapla(self) -> float:
        """
        0-100 arası sistem sağlık puanı.
        Ceza mekanizması:
          - Her döngüsel bağımlılık  : -15 puan
          - Her God Object           : -10 puan
          - Her kritik köprü         : -5  puan
          - Her kırılgan modül       : -3  puan
        """
        puan = 100.0
        puan -= len(self.dongusel_baglar)  * 15
        puan -= len(self.god_objects)      * 10
        puan -= len(self.kritik_koprular)  * 5
        puan -= len(self.kirilgan_moduller)* 3
        self.saglik_puani = max(0.0, round(puan, 1))
        return self.saglik_puani


# ══════════════════════════════════════════════════════════════════════════════
# 2. IMPORT ÇÖZÜMLEYICI
# ══════════════════════════════════════════════════════════════════════════════

class _ImportCozumleyici(ast.NodeVisitor):
    """
    Bir kaynak dosyadaki import ifadelerini AST üzerinden toplar.
    Sadece proje içi modülleri (proje_modulleri kümesinde olanları) döner.
    """

    def __init__(self, proje_modulleri: set[str]):
        self.proje_modulleri = proje_modulleri
        self.bulunan_importlar: list[str] = []

    def visit_Import(self, node: ast.Import):
        """import X  /  import X as Y"""
        for alias in node.names:
            kok = alias.name.split(".")[0]       # "pkg.sub" → "pkg"
            if kok in self.proje_modulleri:
                self.bulunan_importlar.append(kok)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """from X import Y  /  from .X import Y"""
        if node.module is None:
            return                               # bare "from . import X"

        # Göreli import (".models" gibi) → mutlak kok al
        kok = node.module.split(".")[0]
        if node.level > 0:
            # Göreli: dosyanın paket adına göre çözümle (basit yaklaşım)
            kok = node.module.split(".")[0] if node.module else ""

        if kok and kok in self.proje_modulleri:
            self.bulunan_importlar.append(kok)
        self.generic_visit(node)


# ══════════════════════════════════════════════════════════════════════════════
# 3. ANA SINIF
# ══════════════════════════════════════════════════════════════════════════════

class MimariRontgen:
    """
    Proje bağımlılık grafını kuran ve analiz eden ana sınıf.

    Örnek:
        rontgen = MimariRontgen("./src")
        rapor   = rontgen.analiz_et()
        rontgen.png_kaydet("mimari_harita.png")
    """

    def __init__(self, proje_yolu: str):
        self.kok   = Path(proje_yolu).resolve()
        self.graf  = nx.DiGraph()
        self._rapor: Optional[AnalizRaporu] = None

        if not self.kok.exists():
            raise FileNotFoundError(f"Proje klasörü bulunamadı: {self.kok}")

    # ── Yardımcı: projedeki tüm .py modül adlarını topla ────────────────────

    def _proje_modulleri(self) -> set[str]:
        """
        __pycache__ ve venv dışındaki tüm .py dosyalarının
        stem adlarını döner (örn: "auth_service", "models").
        Bunlar grafte düğüm olacak.
        """
        harici = {"__pycache__", "venv", ".venv", "site-packages", "migrations"}
        return {
            p.stem
            for p in self.kok.rglob("*.py")
            if not any(part in harici for part in p.parts)
        }

    # ── Graf inşası ──────────────────────────────────────────────────────────

    def _grafi_kur(self) -> nx.DiGraph:
        """
        Her .py dosyasını düğüm, her proje-içi importu yönlü kenar olarak
        DiGraph'a ekler.
        Kenar anlamı: A → B  ≡  A, B'yi import eder
        """
        modüller  = self._proje_modulleri()
        harici    = {"__pycache__", "venv", ".venv", "site-packages"}

        # Önce tüm düğümleri ekle (izole olanlar da grafte görünsün)
        for m in modüller:
            self.graf.add_node(m)

        # Her dosyayı oku ve importlarını kenar yap
        for dosya in self.kok.rglob("*.py"):
            if any(p in harici for p in dosya.parts):
                continue

            kaynak_modul = dosya.stem
            try:
                kaynak = dosya.read_text(encoding="utf-8", errors="replace")
                agac   = ast.parse(kaynak, filename=str(dosya))
            except SyntaxError:
                continue                         # Bozuk dosyaları atla

            cozumleyici = _ImportCozumleyici(modüller)
            cozumleyici.visit(agac)

            for hedef in set(cozumleyici.bulunan_importlar):
                if hedef != kaynak_modul:        # Öz-döngü ekleme
                    self.graf.add_edge(kaynak_modul, hedef)

        return self.graf

    # ── Matematiksel analizler ───────────────────────────────────────────────

    def _dongusel_bagimliliklar(self) -> list[list[str]]:
        """
        nx.simple_cycles() → tüm basit döngüleri listeler.
        A→B→A  veya  A→B→C→A gibi döngüler "Mimari İhlal" olarak işaretlenir.
        """
        return [list(d) for d in nx.simple_cycles(self.graf)]

    def _betweenness_centrality(self) -> dict[str, float]:
        """
        Betweenness Centrality: bir düğümün kaç en-kısa-yolun
        üzerinden geçtiğinin normalleştirilmiş skoru.
        Yüksek değer → bu modül bir "köprü" → kaldırılırsa sistem çöker.
        """
        if len(self.graf.nodes) < 2:
            return {n: 0.0 for n in self.graf.nodes}
        return nx.betweenness_centrality(self.graf, normalized=True)

    def _dugum_analizleri(
        self,
        dongusel_kumesi: set[str],
        betweenness: dict[str, float],
    ) -> list[DugumAnalizi]:
        """Her düğüm için DugumAnalizi nesnesi üretir."""
        analizler = []
        for dugum in self.graf.nodes:
            ca = self.graf.in_degree(dugum)      # Afferent (beni import edenler)
            ce = self.graf.out_degree(dugum)     # Efferent (benim importlarım)
            instability = round(ce / (ca + ce), 4) if (ca + ce) > 0 else 1.0
            bw = round(betweenness.get(dugum, 0.0), 4)

            analizler.append(DugumAnalizi(
                ad              = dugum,
                in_degree       = ca,
                out_degree      = ce,
                betweenness     = bw,
                instability     = instability,
                god_object      = ca >= ESIK_GOD_OBJECT_INDEGREE,
                kritik_kopru    = bw >= ESIK_BETWEENNESS_KRITIK,
                dongusel        = dugum in dongusel_kumesi,
            ))
        return sorted(analizler, key=lambda d: d.in_degree, reverse=True)

    # ── Ana analiz ───────────────────────────────────────────────────────────

    def analiz_et(self) -> AnalizRaporu:
        """
        Grafı kurar ve tüm metrikleri hesaplar.
        Dönen AnalizRaporu nesnesi hem konsol hem PNG için kullanılır.
        """
        self._grafi_kur()

        donguler       = self._dongusel_bagimliliklar()
        betweenness    = self._betweenness_centrality()
        dongusel_kumesi = {m for d in donguler for m in d}

        dugumler = self._dugum_analizleri(dongusel_kumesi, betweenness)

        rapor = AnalizRaporu(
            proje_yolu      = str(self.kok),
            dosya_sayisi    = self.graf.number_of_nodes(),
            kenar_sayisi    = self.graf.number_of_edges(),
            dongusel_baglar = donguler,
            god_objects     = [d for d in dugumler if d.god_object],
            kritik_koprular = [d for d in dugumler if d.kritik_kopru],
            kirilgan_moduller = [
                d for d in dugumler
                if d.instability >= ESIK_INSTABILITY_KIRILGAN and d.out_degree > 0
            ],
            tum_dugumler    = dugumler,
        )
        rapor.saglik_hesapla()
        self._rapor = rapor
        return rapor

    # ══════════════════════════════════════════════════════════════════════════
    # PNG GÖRSEL ÇIKTISI
    # ══════════════════════════════════════════════════════════════════════════

    def png_kaydet(self, cikti_yolu: str = "mimari_harita.png") -> str:
        """
        Bağımlılık grafını renkli, etiketli PNG olarak kaydeder.

        Renk kodu:
            KIRMIZI  → God Object veya döngüsel bağımlılık içinde
            TURUNCU  → Kritik köprü (yüksek Betweenness)
            SARI     → Kırılgan modül (yüksek Instability)
            YEŞİL    → Sağlıklı düğüm
        """
        if not MPL_MEVCUT:
            print("[UYARI] matplotlib yok — PNG kaydedilemiyor.")
            return ""

        if self._rapor is None:
            self.analiz_et()

        rapor = self._rapor
        G     = self.graf
        n     = G.number_of_nodes()

        if n == 0:
            print("[UYARI] Grafte düğüm yok, PNG oluşturulmadı.")
            return ""

        # ── Düğüm metaverisi haritası ────────────────────────────────────────
        dugum_meta: dict[str, DugumAnalizi] = {
            d.ad: d for d in rapor.tum_dugumler
        }

        # ── Layout ──────────────────────────────────────────────────────────
        # spring_layout: kuvvet-yönlendirmeli — birbirine bağlı düğümler yakın
        tohum = 42
        if n <= 20:
            pos = nx.spring_layout(G, seed=tohum, k=2.5 / math.sqrt(n + 1))
        else:
            pos = nx.kamada_kawai_layout(G)   # Büyük graflar için daha düzenli

        # ── Renk ve boyut belirleme ──────────────────────────────────────────
        renk_map  = []
        boyut_map = []
        for dugum in G.nodes:
            meta = dugum_meta.get(dugum)
            if meta is None:
                renk_map.append("#95a5a6")
                boyut_map.append(800)
                continue

            if meta.god_object or meta.dongusel:
                renk_map.append("#e74c3c")      # Kırmızı — kritik
            elif meta.kritik_kopru:
                renk_map.append("#e67e22")      # Turuncu — köprü
            elif meta.instability >= ESIK_INSTABILITY_KIRILGAN:
                renk_map.append("#f1c40f")      # Sarı — kırılgan
            else:
                renk_map.append("#2ecc71")      # Yeşil — sağlıklı

            # In-degree'ye göre düğüm büyüklüğü (God Object daha büyük)
            boyut_map.append(900 + meta.in_degree * 300)

        # ── Şekil ve çizim ──────────────────────────────────────────────────
        en = max(14, n * 1.1)
        boy = max(10, n * 0.9)
        fig, ax = plt.subplots(figsize=(en, boy), facecolor="#1a1a2e")
        ax.set_facecolor("#16213e")

        # Kenarlar (döngüsel bağımlılıklar kırmızı, diğerleri gri)
        dongusel_kenari: set[tuple] = set()
        for dongu in rapor.dongusel_baglar:
            for i in range(len(dongu)):
                dongusel_kenari.add((dongu[i], dongu[(i + 1) % len(dongu)]))

        normal_kenarlar = [e for e in G.edges() if e not in dongusel_kenari]
        dongu_kenarlari = [e for e in G.edges() if e    in dongusel_kenari]

        # Normal kenarlar
        nx.draw_networkx_edges(
            G, pos,
            edgelist   = normal_kenarlar,
            ax         = ax,
            edge_color = "#4a4a8a",
            arrows     = True,
            arrowsize  = 18,
            arrowstyle = "-|>",
            width      = 1.2,
            alpha      = 0.7,
            connectionstyle = "arc3,rad=0.08",
            min_source_margin = 20,
            min_target_margin = 20,
        )

        # Döngüsel bağımlılık kenarları (parlak kırmızı)
        if dongu_kenarlari:
            nx.draw_networkx_edges(
                G, pos,
                edgelist   = dongu_kenarlari,
                ax         = ax,
                edge_color = "#ff4757",
                arrows     = True,
                arrowsize  = 22,
                arrowstyle = "-|>",
                width      = 2.5,
                alpha      = 0.95,
                connectionstyle = "arc3,rad=0.15",
                min_source_margin = 20,
                min_target_margin = 20,
            )

        # Düğümler
        nx.draw_networkx_nodes(
            G, pos,
            ax         = ax,
            node_color = renk_map,
            node_size  = boyut_map,
            alpha      = 0.92,
            linewidths = 1.5,
            edgecolors = "#ffffff",
        )

        # Etiketler
        nx.draw_networkx_labels(
            G, pos,
            ax        = ax,
            font_size = max(7, 10 - n // 10),
            font_color= "#ffffff",
            font_weight = "bold",
        )

        # ── Başlık ──────────────────────────────────────────────────────────
        saglik_renk = (
            "#e74c3c" if rapor.saglik_puani < 50 else
            "#f39c12" if rapor.saglik_puani < 75 else
            "#2ecc71"
        )
        ax.set_title(
            f"Mimari Röntgen — Bağımlılık Grafı\n"
            f"{rapor.dosya_sayisi} modül · {rapor.kenar_sayisi} bağımlılık · "
            f"Sağlık: {rapor.saglik_puani}/100",
            color="#ecf0f1", fontsize=14, pad=16,
            fontweight="bold",
        )

        # ── Lejant ──────────────────────────────────────────────────────────
        lejant = [
            mpatches.Patch(color="#e74c3c", label="God Object / Döngüsel Bağımlılık"),
            mpatches.Patch(color="#e67e22", label="Kritik Köprü (yüksek Betweenness)"),
            mpatches.Patch(color="#f1c40f", label=f"Kırılgan Modül (Instability ≥ {ESIK_INSTABILITY_KIRILGAN})"),
            mpatches.Patch(color="#2ecc71", label="Sağlıklı Modül"),
            mpatches.Patch(color="#ff4757", label="Döngüsel Bağımlılık Kenarı"),
        ]
        ax.legend(
            handles=lejant,
            loc="lower left",
            facecolor="#0f3460",
            edgecolor="#ffffff",
            labelcolor="#ecf0f1",
            fontsize=9,
            framealpha=0.85,
        )

        ax.axis("off")
        plt.tight_layout()

        cikti = Path(cikti_yolu)
        plt.savefig(cikti, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)

        if self._rapor:
            self._rapor.png_yolu = str(cikti.resolve())

        return str(cikti.resolve())


# ══════════════════════════════════════════════════════════════════════════════
# 4. KONSOL RAPORU
# ══════════════════════════════════════════════════════════════════════════════

# ANSI renk kodları
class R:
    KIRMIZI   = "\033[91m"
    TURUNCU   = "\033[93m"
    SARI      = "\033[33m"
    YESIL     = "\033[92m"
    MAVI      = "\033[94m"
    BEYAZ     = "\033[97m"
    GRI       = "\033[90m"
    KALIN     = "\033[1m"
    SIFIR     = "\033[0m"
    CYAN      = "\033[96m"


def _saglik_cubugu(puan: float, genislik: int = 30) -> str:
    """ASCII ilerleme çubuğu."""
    dolu = int(puan / 100 * genislik)
    bos  = genislik - dolu
    renk = R.KIRMIZI if puan < 50 else R.TURUNCU if puan < 75 else R.YESIL
    return f"{renk}{'█' * dolu}{'░' * bos}{R.SIFIR}"


def rapor_yazdir(rapor: AnalizRaporu) -> None:
    """
    Analiz raporunu terminal'e biçimli olarak yazdırır.
    """
    SEP  = f"{R.GRI}{'═' * 66}{R.SIFIR}"
    SEP2 = f"{R.GRI}{'─' * 66}{R.SIFIR}"

    print(f"\n{SEP}")
    print(f"{R.KALIN}{R.BEYAZ}  🔬 MİMARİ RÖNTGEN — BAĞIMLILIK TOPOLOJİSİ ANALİZİ{R.SIFIR}")
    print(f"{R.GRI}  {rapor.proje_yolu}{R.SIFIR}")
    print(SEP)

    # ── Genel topoloji ──────────────────────────────────────────────────────
    print(f"\n{R.KALIN}{R.CYAN}  [MİMARİ RÖNTGEN] Sistem Topolojisi{R.SIFIR}")
    print(f"  {'Modül Sayısı':<28}: {R.BEYAZ}{rapor.dosya_sayisi}{R.SIFIR}")
    print(f"  {'Bağımlılık Kenarı':<28}: {R.BEYAZ}{rapor.kenar_sayisi}{R.SIFIR}")
    print(f"  {'Döngüsel Bağımlılık':<28}: "
          f"{R.KIRMIZI if rapor.dongusel_baglar else R.YESIL}"
          f"{len(rapor.dongusel_baglar)}{R.SIFIR}")
    print(f"  {'God Object Adayı':<28}: "
          f"{R.KIRMIZI if rapor.god_objects else R.YESIL}"
          f"{len(rapor.god_objects)}{R.SIFIR}")

    print(f"\n  {'Sistem Sağlık Puanı':<28}: "
          f"{_saglik_cubugu(rapor.saglik_puani)} "
          f"{R.KALIN}{rapor.saglik_puani}/100{R.SIFIR}")
    print(SEP2)

    # ── Döngüsel bağımlılıklar ───────────────────────────────────────────────
    print(f"\n{R.KALIN}{R.KIRMIZI}  [SPAGETTİ ALARMI] Döngüsel Bağımlılıklar{R.SIFIR}")
    if rapor.dongusel_baglar:
        for i, dongu in enumerate(rapor.dongusel_baglar, 1):
            zincir = " → ".join(dongu) + f" → {dongu[0]}"
            print(f"  {R.KIRMIZI}✗{R.SIFIR} Döngü #{i}: {R.TURUNCU}{zincir}{R.SIFIR}")
            print(f"    {R.GRI}↳ Mimari İhlal: Bu bağlar bağımsız test/dağıtımı engeller.{R.SIFIR}")
    else:
        print(f"  {R.YESIL}✓ Döngüsel bağımlılık tespit edilmedi.{R.SIFIR}")
    print(SEP2)

    # ── God Object tespiti ───────────────────────────────────────────────────
    print(f"\n{R.KALIN}{R.TURUNCU}  [GOD OBJECT] Aşırı Bağımlılık Düğümleri{R.SIFIR}")
    if rapor.god_objects:
        baslik = f"  {'Modül':<22} {'In-deg':>7} {'Out-deg':>8} {'Betw.':>8} {'Durum'}"
        print(f"{R.GRI}{baslik}{R.SIFIR}")
        for d in sorted(rapor.god_objects, key=lambda x: x.in_degree, reverse=True):
            isaretler = []
            if d.dongusel:  isaretler.append("DÖNGÜ")
            if d.kritik_kopru: isaretler.append("KÖPRÜ")
            etiket = f"{R.KIRMIZI}[{' + '.join(isaretler)}]{R.SIFIR}" if isaretler else ""
            print(
                f"  {R.KIRMIZI}★{R.SIFIR} {d.ad:<22}"
                f" {R.BEYAZ}{d.in_degree:>7}{R.SIFIR}"
                f" {d.out_degree:>8}"
                f" {d.betweenness:>8.3f}"
                f"  {etiket}"
            )
            print(f"    {R.GRI}↳ Karar: Bu modülü soyut arayüze (ABC/Protocol) dönüştür.{R.SIFIR}")
    else:
        print(f"  {R.YESIL}✓ God Object tespit edilmedi.{R.SIFIR}")
    print(SEP2)

    # ── Kritik köprüler ──────────────────────────────────────────────────────
    print(f"\n{R.KALIN}{R.TURUNCU}  [KRİTİK KÖPRÜLER] Yüksek Betweenness Centrality{R.SIFIR}")
    if rapor.kritik_koprular:
        for d in sorted(rapor.kritik_koprular, key=lambda x: x.betweenness, reverse=True):
            bar = "█" * int(d.betweenness * 20)
            print(f"  {R.TURUNCU}⚠{R.SIFIR}  {d.ad:<24} BC={R.BEYAZ}{d.betweenness:.3f}{R.SIFIR}  {R.TURUNCU}{bar}{R.SIFIR}")
            print(f"    {R.GRI}↳ Karar: Facade veya Adapter pattern ile yükü dağıt.{R.SIFIR}")
    else:
        print(f"  {R.YESIL}✓ Kritik köprü tespit edilmedi.{R.SIFIR}")
    print(SEP2)

    # ── Kırılgan modüller ────────────────────────────────────────────────────
    print(f"\n{R.KALIN}{R.SARI}  [KIRILGANLIK] Martin Instability Skoru ≥ {ESIK_INSTABILITY_KIRILGAN}{R.SIFIR}")
    if rapor.kirilgan_moduller:
        for d in sorted(rapor.kirilgan_moduller, key=lambda x: x.instability, reverse=True):
            barlength = int(d.instability * 20)
            bar = "█" * barlength
            print(
                f"  {R.SARI}↯{R.SIFIR}  {d.ad:<24} "
                f"I={R.BEYAZ}{d.instability:.3f}{R.SIFIR}  "
                f"{R.SARI}{bar}{R.SIFIR}  "
                f"{R.GRI}(Ce={d.out_degree}, Ca={d.in_degree}){R.SIFIR}"
            )
    else:
        print(f"  {R.YESIL}✓ Kırılgan modül tespit edilmedi.{R.SIFIR}")
    print(SEP2)

    # ── Tüm modül özeti ──────────────────────────────────────────────────────
    print(f"\n{R.KALIN}{R.MAVI}  [OTONOM KARAR] Modül Sağlık Tablosu{R.SIFIR}")
    baslik = (
        f"  {'Modül':<24} {'Ca':>4} {'Ce':>4} "
        f"{'Betw':>7} {'I-Skor':>7}  {'Durum'}"
    )
    print(f"{R.GRI}{baslik}{R.SIFIR}")
    for d in rapor.tum_dugumler:
        if d.god_object or d.dongusel:
            renk = R.KIRMIZI; isaret = "✗"
        elif d.kritik_kopru:
            renk = R.TURUNCU; isaret = "⚠"
        elif d.instability >= ESIK_INSTABILITY_KIRILGAN and d.out_degree > 0:
            renk = R.SARI;   isaret = "↯"
        else:
            renk = R.YESIL;  isaret = "✓"

        print(
            f"  {renk}{isaret}{R.SIFIR} {d.ad:<24}"
            f" {d.in_degree:>4} {d.out_degree:>4}"
            f" {d.betweenness:>7.3f} {d.instability:>7.3f}"
            f"  {renk}{'KRİTİK' if d.god_object or d.dongusel else 'KÖPRÜ' if d.kritik_kopru else 'KIRILGAN' if d.instability >= ESIK_INSTABILITY_KIRILGAN and d.out_degree > 0 else 'SAĞLIKLI'}{R.SIFIR}"
        )

    print(f"\n{SEP}")
    if rapor.png_yolu:
        print(f"  {R.YESIL}📊 Graf kaydedildi → {rapor.png_yolu}{R.SIFIR}")
    print(f"  {R.GRI}Ca=Afferent (giren bağ) · Ce=Efferent (çıkan bağ) · "
          f"I=Instability · Betw=Betweenness Centrality{R.SIFIR}")
    print(SEP + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# 5. KLİ
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    hedef = sys.argv[1] if len(sys.argv) > 1 else "."
    png   = sys.argv[2] if len(sys.argv) > 2 else "mimari_harita.png"

    print(f"[MİMARİ RÖNTGEN] Taranıyor: {Path(hedef).resolve()}")

    rontgen = MimariRontgen(hedef)
    rapor   = rontgen.analiz_et()
    png_yol = rontgen.png_kaydet(png)
    rapor_yazdir(rapor)
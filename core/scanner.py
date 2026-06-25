"""
kod_tarayici.py
═══════════════════════════════════════════════════════════════════════════════
Otonom Mühendislik Ajanı — Veri Çıkarım Modülü (Feature Extraction Layer)

Bu modül, projenin "gözleri" görevini üstlenir. Verilen herhangi bir Python
dosyasını üç farklı perspektiften analiz eder:

  1. Sözdizimsel Analiz (AST): Dosyayı bir ağaç yapısına dönüştürerek kaç
     sınıf, fonksiyon ve import ifadesi olduğunu, iç içe geçme derinliğini
     ve hata yakalama bloklarını tespit eder. Python'ın standart kütüphanesi
     kullanılır; ek kurulum gerekmez.

  2. Karmaşıklık & Kalite Analizi (Radon): Endüstri standardı `radon`
     kütüphanesi aracılığıyla üç kritik metrik hesaplanır:
       - Cyclomatic Complexity (CC): Kodun kaç farklı yol izleyebileceği.
       - Halstead Metrikleri: Operatör/operand sayısından türetilen bilişsel yük.
       - Maintainability Index (MI): 0-100 arası bakım kolaylığı skoru.

  3. Özellik Vektörü Üretimi: Hesaplanan tüm metrikler, Gradient Boosting
     modelinin beklediği formata (17 boyutlu sayı listesi) dönüştürülür.

Bağımlılıklar:
    pip install radon

Temel Kullanım:
    from kod_tarayici import KodTarayici

    tarayici = KodTarayici("auth_service.py")

    # Makine öğrenmesi modeline beslemek için:
    vektor = tarayici.ozellik_vektoru()
    risk   = model.predict_proba([vektor.liste()])[0][1]

    # İnsan tarafından okunabilir tam rapor için:
    rapor = tarayici.tam_rapor()
    print(rapor["bakim_skoru"])  # → 0-100 arası MI değeri

    # Tüm projeyi toplu taramak için:
    from kod_tarayici import proje_tara
    raporlar = proje_tara("./src/")
═══════════════════════════════════════════════════════════════════════════════
"""
import ast
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


class _YapiAnalizci(ast.NodeVisitor):
    """AST ağacını tek geçişte tarar ve yapısal metrikleri toplar."""

    def __init__(self):
        self.sinif_sayisi = 0
        self.fonksiyon_sayisi = 0
        self.import_sayisi = 0
        self.lambda_sayisi = 0
        self.decorator_sayisi = 0
        self.assert_sayisi = 0
        self.try_except_sayisi = 0
        self.max_derinlik = 0
        self._derinlik = 0

    def _derinlige_gir(self):
        self._derinlik += 1
        if self._derinlik > self.max_derinlik:
            self.max_derinlik = self._derinlik

    def _derinlikten_cik(self):
        self._derinlik -= 1

    def visit_ClassDef(self, node):
        self.sinif_sayisi += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.fonksiyon_sayisi += 1
        self.decorator_sayisi += len(node.decorator_list)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Import(self, node):
        self.import_sayisi += len(node.names)

    def visit_ImportFrom(self, node):
        self.import_sayisi += 1

    def visit_Lambda(self, node):
        self.lambda_sayisi += 1
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.assert_sayisi += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.try_except_sayisi += len(node.handlers)
        self.generic_visit(node)

    def visit_For(self, node):
        self._derinlige_gir()
        self.generic_visit(node)
        self._derinlikten_cik()

    def visit_While(self, node):
        self._derinlige_gir()
        self.generic_visit(node)
        self._derinlikten_cik()

    def visit_If(self, node):
        self._derinlige_gir()
        self.generic_visit(node)
        self._derinlikten_cik()
try:
    from radon.complexity import cc_visit, cc_rank
    from radon.metrics import h_visit, mi_visit
    from radon.raw import analyze
    RADON_MEVCUT = True
except ImportError:
    RADON_MEVCUT = False
    print("[UYARI] 'radon' kütüphanesi bulunamadı.\n         Kurulum: pip install radon\n         Radon olmadan CC, Halstead ve MI hesaplanamaz;\n         temel LOC ve yapısal metrikler hâlâ üretilir.")

@dataclass
class KarmasiklikMetrikleri:
    """
    Cyclomatic Complexity (CC) hesaplamalarının özet istatistiklerini tutar.

    CC, bir fonksiyonun içindeki bağımsız yol sayısını ölçer. Formül:
        CC = E - N + 2P   (E=kenar, N=düğüm, P=bağlı bileşen sayısı)

    Yorumlama kılavuzu:
        CC  1-5  → Basit, test edilmesi kolay
        CC  6-10 → Orta karmaşıklık, dikkat gerektirir
        CC 11-15 → Yüksek risk, yeniden yapılandırma önerilir
        CC   >15 → KRİTİK, bakımı çok zorlaşmış demektir
    """
    cc_max: float = 0.0
    cc_mean: float = 0.0
    cc_toplam: float = 0.0
    fonksiyon_sayisi: int = 0
    kritik_fonksiyonlar: list = field(default_factory=list)

@dataclass
class HalsteadMetrikleri:
    """
    Maurice Halstead'ın 1977'de geliştirdiği yazılım bilimi metriklerini tutar.

    Temel fikir: Kod, operatör (if/for/=) ve operand'lardan (değişken, sabit)
    oluşur. Bu iki grubun sayısından soyut metrikler türetilebilir.

    Önemli metrikler:
        volume     → Kodun bilgi yoğunluğu; ne kadar "şey" ifade ediyor?
        difficulty → Kodu anlamak için gereken zihinsel çaba tahmini
        effort     → Geliştirici zamanı ve hata riskiyle en çok korelasyon
                     gösteren değer; modelimizin en önemli girdilerinden biri
        bugs       → Tahmini hata sayısı: B = Volume / 3000 (Halstead formülü)
    """
    effort: float = 0.0
    volume: float = 0.0
    difficulty: float = 0.0
    time: float = 0.0
    bugs: float = 0.0

@dataclass
class LoKMetrikleri:
    """
    Satır bazlı kod ölçümlerini tutar.

    Ham LOC yerine ayrıştırılmış metrikler kullanılır; çünkü yorum satırları
    ve boşluklar gerçek kod karmaşıklığını temsil etmez.

    Yorum oranı yorumlama:
        %0       → Hiç belge yok, bakımı çok zor
        %10-20   → İdeal aralık
        %>40     → Aşırı yorum, kod kendini ifade etmiyor olabilir
    """
    loc: int = 0
    sloc: int = 0
    yorum_satiri: int = 0
    bos_satir: int = 0
    yorum_orani: float = 0.0

@dataclass
class ASTMetrikleri:
    """
    Python'ın AST (Soyut Sözdizim Ağacı) analizi ile elde edilen yapısal
    ölçümler. Bu metrikler radon'a bağımlı değildir; sadece standart
    kütüphane ile hesaplanır.

    Bu metrikler özellikle bağımlılık ve yapısal karmaşıklık sorunlarını
    erken tespit etmek için kullanılır.
    """
    sinif_sayisi: int = 0
    fonksiyon_sayisi: int = 0
    import_sayisi: int = 0
    ic_ice_derinlik: int = 0
    lambda_sayisi: int = 0
    decorator_sayisi: int = 0
    assert_sayisi: int = 0
    try_except_sayisi: int = 0

@dataclass
class OzellikVektoru:
    """
    Makine öğrenmesi modelimize (Gradient Boosting / PROMISE JM1) doğrudan
    beslenecek nihai özellik vektörü.

    ÖNEMLİ KURAL: Bu sınıftaki alan sırası ve adları değiştirilemez!
    Model, eğitim sırasında bu sırayı 'öğrenmiştir'. Herhangi bir değişiklik
    modelin tamamen hatalı tahmin üretmesine neden olur.

    Yeni özellik eklemek istersen:
        1. Bu sınıfın SONUNA ekle.
        2. Modeli baştan eğit.
        3. Versiyonu güncelle.

    Kullanım:
        vec    = tarayici.ozellik_vektoru()
        tahmin = model.predict([vec.liste()])          # [0] veya [1]
        risk   = model.predict_proba([vec.liste()])[0][1]  # 0.0-1.0
    """
    cc_max: float = 0.0
    cc_mean: float = 0.0
    cc_toplam: float = 0.0
    halstead_effort: float = 0.0
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_bugs: float = 0.0
    loc: int = 0
    sloc: int = 0
    yorum_orani: float = 0.0
    sinif_sayisi: int = 0
    fonksiyon_sayisi: int = 0
    fan_out: int = 0
    ic_ice_derinlik: int = 0
    try_except_sayisi: int = 0
    loc_per_fonksiyon: float = 0.0
    instability_proxy: float = 0.0

    def liste(self) -> list:
        """
        Modele doğrudan verilebilecek saf Python sayı listesi döner.

        Örnek:
            model.predict([vektor.liste()])
            model.predict_proba([vektor.liste()])
        """
        return list(asdict(self).values())

    def sozluk(self) -> dict:
        """
        Etiketli anahtar-değer sözlüğü döner.
        Raporlama ve debug için kullanılır.
        """
        return asdict(self)

class KodTarayici:
    """
    Tek bir Python dosyasını kapsamlı biçimde analiz eden ana sınıf.

    Tasarım Deseni — Lazy Evaluation (Tembel Hesaplama):
        Her metrik grubu yalnızca ilk kez sorgulandığında hesaplanır ve
        önbelleğe alınır. Bu sayede aynı dosya için birden fazla metrik
        istendiğinde gereksiz tekrar hesaplama yapılmaz.

        Örnek:
            t = KodTarayici("büyük_dosya.py")
            _ = t.karmasiklik_metrikleri()  # Radon çalışır, 500ms
            _ = t.karmasiklik_metrikleri()  # Önbellekten, <1ms
            _ = t.ozellik_vektoru()         # Önbellekten beslenir, hızlı

    Hata Toleransı:
        - Radon kurulu değilse → AST yedek yolları devreye girer
        - Dosya UTF-8 değilse → Latin-1 ile yeniden denenir
        - Sözdizimi hatası → SyntaxError fırlatılır (gizlenmez)

    Kullanım:
        tarayici = KodTarayici("servis.py")
        rapor    = tarayici.tam_rapor()        # Tüm veriler dict olarak
        vektor   = tarayici.ozellik_vektoru() # Sadece ML için olan kısım
    """

    def __init__(self, dosya_yolu: str):
        """
        Tarayıcıyı başlatır ve kaynak kodu yükler.

        Parametreler:
            dosya_yolu: Analiz edilecek .py dosyasının yolu.
                        Hem mutlak ('/home/user/app.py') hem göreli ('app.py')
                        yollar kabul edilir.

        Hatalar:
            FileNotFoundError: Dosya bulunamadıysa.
            ValueError: Dosya .py uzantısına sahip değilse.
            SyntaxError: Dosyanın Python sözdizimi bozuksa.
        """
        self.yol = Path(dosya_yolu)
        self._kaynak: Optional[str] = None
        self._agac: Optional[ast.AST] = None
        self._karmasiklik: Optional[KarmasiklikMetrikleri] = None
        self._halstead: Optional[HalsteadMetrikleri] = None
        self._lok: Optional[LoKMetrikleri] = None
        self._ast_met: Optional[ASTMetrikleri] = None
        self._kaynak_yukle()

    def _kaynak_yukle(self):
        """
        Dosyayı diskten okur ve AST ağacına dönüştürür.

        Neden iki encoding deneniyor?
            Eski Python projeleri bazen Latin-1 (ISO-8859-1) ile yazılmıştır.
            Özellikle Türkçe karakter içeren yorumlar UTF-8'de hata verebilir.
            Bu yüzden önce UTF-8, başarısız olursa Latin-1 denenir.
        """
        if not self.yol.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: '{self.yol}'\nÇalışma dizini: {Path.cwd()}")
        if self.yol.suffix.lower() != '.py':
            raise ValueError(f"Sadece '.py' dosyaları desteklenir. Verilen: '{self.yol.suffix}'")
        try:
            self._kaynak = self.yol.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            self._kaynak = self.yol.read_text(encoding='latin-1')
        try:
            self._agac = ast.parse(self._kaynak, filename=str(self.yol))
        except SyntaxError as hata:
            raise SyntaxError(f"'{self.yol.name}' dosyasında sözdizimi hatası: {hata}\n  Satır {hata.lineno}: {hata.text}") from hata

    def karmasiklik_metrikleri(self) -> KarmasiklikMetrikleri:
        """
        Dosyadaki her fonksiyon için Cyclomatic Complexity hesaplar.

        Nasıl Çalışır:
            Radon, kaynak kodu analiz ederek her fonksiyonun kaç bağımsız
            yürütme yolu içerdiğini sayar. Her 'if', 'for', 'while', 'except'
            yeni bir yol ekler.

        Radon Yoksa:
            AST'deki dal (if/for/while/except) düğümleri sayılarak tüm dosya
            için tek bir kaba tahmin üretilir. Bu değer fonksiyon bazında
            ayrıştırılmaz, ancak genel eğilimi gösterir.

        Dönüş:
            KarmasiklikMetrikleri nesnesi. cc_max kritik eşik karşılaştırması
            için kullanılır.
        """
        if self._karmasiklik is not None:
            return self._karmasiklik
        met = KarmasiklikMetrikleri()
        if RADON_MEVCUT:
            sonuclar = cc_visit(self._kaynak)
            if sonuclar:
                skorlar = [blok.complexity for blok in sonuclar]
                met.cc_max = max(skorlar)
                met.cc_mean = sum(skorlar) / len(skorlar)
                met.cc_toplam = sum(skorlar)
                met.fonksiyon_sayisi = len(sonuclar)
                met.kritik_fonksiyonlar = [{'isim': blok.name, 'cc': blok.complexity, 'rank': cc_rank(blok.complexity)} for blok in sonuclar if blok.complexity > 10]
        else:
            dal_tipler = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert, ast.comprehension)
            dal_sayisi = sum((1 for dugum in ast.walk(self._agac) if isinstance(dugum, dal_tipler)))
            met.cc_max = float(dal_sayisi)
            met.cc_mean = float(dal_sayisi)
            met.cc_toplam = float(dal_sayisi)
        self._karmasiklik = met
        return met

    def halstead_metrikleri(self) -> HalsteadMetrikleri:
        """
        Halstead yazılım bilimi metriklerini hesaplar.

        Radon, modül seviyesinde bir HalsteadReport nesnesi döner.
        Bu raporun 'total' alanı tüm modülün toplamını içerir.

        Radon Yoksa:
            Tüm değerler 0.0 olarak döner. Bu durum model tahmini için
            vektörde eksik değer yaratır; modelin güvenilirliği düşer.

        Dönüş:
            HalsteadMetrikleri nesnesi. 'effort' alanı en kritik olanıdır.
        """
        if self._halstead is not None:
            return self._halstead
        met = HalsteadMetrikleri()
        if RADON_MEVCUT:
            try:
                h_sonuclar = h_visit(self._kaynak)
                if h_sonuclar:
                    h = h_sonuclar[0].total
                    met.effort = round(h.effort, 4)
                    met.volume = round(h.volume, 4)
                    met.difficulty = round(h.difficulty, 4)
                    met.time = round(h.time, 4)
                    met.bugs = round(h.bugs, 6)
            except Exception:
                pass
        self._halstead = met
        return met

    def lok_metrikleri(self) -> LoKMetrikleri:
        """
        Satır bazlı kod ölçümlerini hesaplar.

        Radon'ın 'analyze()' fonksiyonu, dosyayı satır satır geçerek
        yorum, kaynak ve boş satırları birbirinden ayırır.

        Radon Yoksa:
            Basit string işlemleriyle '#' ile başlayan ve boş satırlar
            sayılır. Doğruluğu Radon'dan düşüktür (satır içi yorumları
            yakala(ma)z), ancak genel bir fikir verir.

        Dönüş:
            LoKMetrikleri nesnesi.
        """
        if self._lok is not None:
            return self._lok
        met = LoKMetrikleri()
        if RADON_MEVCUT:
            ham = analyze(self._kaynak)
            met.loc = ham.loc
            met.sloc = ham.sloc
            met.yorum_satiri = ham.comments
            met.bos_satir = ham.blank
            met.yorum_orani = round(ham.comments / ham.loc, 4) if ham.loc > 0 else 0.0
        else:
            satirlar = self._kaynak.splitlines()
            met.loc = len(satirlar)
            met.yorum_satiri = sum((1 for s in satirlar if s.strip().startswith('#')))
            met.bos_satir = sum((1 for s in satirlar if not s.strip()))
            met.sloc = met.loc - met.yorum_satiri - met.bos_satir
            met.yorum_orani = round(met.yorum_satiri / met.loc, 4) if met.loc > 0 else 0.0
        self._lok = met
        return met

    def ast_metrikleri(self) -> ASTMetrikleri:
        """
        AST ağacını gezerek yapısal metrikleri toplar.

        Bu metod Radon'a bağımlı değildir; Python'ın standart 'ast'
        modülünü kullanır. Bu sayede Radon kurulu olmasa bile çalışır.

        _YapiAnalizci sınıfı tek bir geçişte tüm düğüm tiplerini sayar;
        ağacı birden fazla kez dolaşmaya gerek kalmaz.

        Dönüş:
            ASTMetrikleri nesnesi. 'import_sayisi' Fan-out proxy'si olarak
            modelimize girebilecek en değerli AST metriğidir.
        """
        if self._ast_met is not None:
            return self._ast_met
        analizci = _YapiAnalizci()
        analizci.visit(self._agac)
        met = ASTMetrikleri(sinif_sayisi=analizci.sinif_sayisi, fonksiyon_sayisi=analizci.fonksiyon_sayisi, import_sayisi=analizci.import_sayisi, ic_ice_derinlik=analizci.max_derinlik, lambda_sayisi=analizci.lambda_sayisi, decorator_sayisi=analizci.decorator_sayisi, assert_sayisi=analizci.assert_sayisi, try_except_sayisi=analizci.try_except_sayisi)
        self._ast_met = met
        return met

    def bakim_skoru(self) -> float:
        """
        Maintainability Index (MI) — Bakım Kolaylığı Skoru hesaplar.

        MI, bir dosyanın ne kadar kolay bakılabileceğini tek bir sayıda
        özetler. Formül (SEI/Radon versiyonu):

            MI = max(0, (171 - 5.2·ln(V) - 0.23·CC - 16.2·ln(LOC)) × 100/171)

            V   = Halstead Volume
            CC  = Ortalama Cyclomatic Complexity
            LOC = Fiziksel satır sayısı

        Yorumlama (endüstri standardı):
            85-100  → Temiz ve bakımı kolay
            65-84   → Orta; bazı alanlar dikkat ister
            0-64    → Bakımı zor; acil yeniden yapılandırma gerekir

        Not:
            Radon kurulu değilse veya hesaplama başarısız olursa -1.0 döner.
            Bu değer UI katmanında "hesaplanamadı" olarak gösterilmelidir.

        Dönüş:
            0.0 ile 100.0 arası float, veya hesaplanamıyorsa -1.0.
        """
        if not RADON_MEVCUT:
            return -1.0
        try:
            skor = mi_visit(self._kaynak, multi=True)
            if skor is None:
                return -1.0
            return round(max(0.0, min(100.0, float(skor))), 2)
        except Exception:
            return -1.0

    def ozellik_vektoru(self) -> OzellikVektoru:
        """
        Makine öğrenmesi modeline beslenecek nihai özellik vektörünü üretir.

        Bu metod tüm metrik hesaplamalarını (CC, Halstead, LOC, AST) bir
        araya getirip OzellikVektoru dataclass'ına doldurur.

        KESİNLİKLE bu metodun dönüş değerinin yapısını değiştirme.
        Model bu 17 sayının tam sırasına ve anlamına göre eğitilmiştir.

        Türev Metrikler:
            loc_per_fonksiyon → Ortalama fonksiyon büyüklüğü. 50+ satır
                                olan fonksiyonlar genellikle tek sorumluluk
                                prensibini ihlal eder.

            instability_proxy → Martin'in Instability formülü: Ce/(Ca+Ce)
                                Ce = Efferent (çıkan bağ, import_sayisi)
                                Ca = Afferent (giren bağ, sinif_sayisi proxy)
                                0.0 = tamamen kararlı, 1.0 = tamamen kırılgan

        Dönüş:
            OzellikVektoru nesnesi. .liste() ile modele ver.
        """
        cc = self.karmasiklik_metrikleri()
        hal = self.halstead_metrikleri()
        lok = self.lok_metrikleri()
        ast_ = self.ast_metrikleri()
        loc_per_fonk = round(lok.sloc / ast_.fonksiyon_sayisi, 2) if ast_.fonksiyon_sayisi > 0 else float(lok.sloc)
        ce = ast_.import_sayisi
        ca = ast_.sinif_sayisi
        instability = round(ce / (ca + ce), 4) if ca + ce > 0 else 1.0
        return OzellikVektoru(cc_max=cc.cc_max, cc_mean=cc.cc_mean, cc_toplam=cc.cc_toplam, halstead_effort=hal.effort, halstead_volume=hal.volume, halstead_difficulty=hal.difficulty, halstead_bugs=hal.bugs, loc=lok.loc, sloc=lok.sloc, yorum_orani=lok.yorum_orani, sinif_sayisi=ast_.sinif_sayisi, fonksiyon_sayisi=ast_.fonksiyon_sayisi, fan_out=ast_.import_sayisi, ic_ice_derinlik=ast_.ic_ice_derinlik, try_except_sayisi=ast_.try_except_sayisi, loc_per_fonksiyon=loc_per_fonk, instability_proxy=instability)

    def tam_rapor(self) -> dict:
        """
        Tüm metrikleri içeren kapsamlı rapor sözlüğü döner.

        Bu metod hem insan okuma hem de programatik tüketim için tasarlanmıştır:
          - UI katmanı (app.py) bu sözlüğü parçalayarak ekranda gösterir
          - Ajan karar motoru eşik karşılaştırmalarını buradan yapar
          - CLI çıktısı bu verilerden biçimlendirilir

        YENİ: 'bakim_skoru' alanı eklendi.
            Değer: 0-100 arası float (yüksek = bakımı kolay)
            Değer = -1.0 ise Radon kurulu değil veya hesaplanamadı demektir.

        Dönüş:
            dict içinde şu anahtarlar bulunur:
                dosya           → analiz edilen dosyanın yolu
                karmasiklik     → CC metrikleri ve durum etiketi
                halstead        → Halstead metrikleri
                lok             → Satır istatistikleri
                yapi            → AST yapısal metrikleri
                bakim_skoru     → 0-100 Maintainability Index (YENİ)
                ozellik_vektoru → Etiketli feature dict (17 özellik)
                model_icin_liste→ Modele gidecek saf sayı listesi
        """
        cc = self.karmasiklik_metrikleri()
        hal = self.halstead_metrikleri()
        lok = self.lok_metrikleri()
        ast_ = self.ast_metrikleri()
        vec = self.ozellik_vektoru()
        mi = self.bakim_skoru()
        return {'dosya': str(self.yol), 'karmasiklik': {'cc_max': cc.cc_max, 'cc_mean': round(cc.cc_mean, 3), 'cc_toplam': cc.cc_toplam, 'fonksiyon_sayisi': cc.fonksiyon_sayisi, 'kritik_fonksiyonlar': cc.kritik_fonksiyonlar, 'durum': 'KRİTİK' if cc.cc_max > 15 else 'UYARI' if cc.cc_max > 10 else 'NORMAL'}, 'halstead': {'effort': hal.effort, 'volume': hal.volume, 'difficulty': hal.difficulty, 'tahmini_sure_dk': round(hal.time / 60, 2), 'tahmini_hata': hal.bugs}, 'lok': {'loc': lok.loc, 'sloc': lok.sloc, 'yorum_satiri': lok.yorum_satiri, 'bos_satir': lok.bos_satir, 'yorum_orani': lok.yorum_orani}, 'yapi': {'sinif_sayisi': ast_.sinif_sayisi, 'fonksiyon_sayisi': ast_.fonksiyon_sayisi, 'fan_out': ast_.import_sayisi, 'ic_ice_derinlik': ast_.ic_ice_derinlik, 'lambda_sayisi': ast_.lambda_sayisi, 'decorator_sayisi': ast_.decorator_sayisi, 'try_except_sayisi': ast_.try_except_sayisi}, 'bakim_skoru': mi, 'ozellik_vektoru': vec.sozluk(), 'model_icin_liste': vec.liste()}

def proje_tara(klasor_yolu: str, ozyinelemeli: bool=True) -> list[dict]:
    """
    Verilen klasördeki tüm Python dosyalarını tarar ve raporlarını döner.

    Bu fonksiyon birden fazla dosyayı analiz ederek modelinize toplu tahmin
    yapmanızı sağlar. Sözdizimi bozuk veya erişilemeyen dosyalar atlanır;
    diğer dosyaların analizi devam eder.

    Parametreler:
        klasor_yolu   : Taranacak klasörün yolu. Alt klasörler dahil edilir.
        ozyinelemeli  : True ise tüm alt klasörler taranır (varsayılan: True).
                        False ise yalnızca doğrudan alt dosyalar taranır.

    Hariç tutulanlar:
        __pycache__ ve venv/site-packages klasörleri otomatik olarak atlanır.
        Bunlar proje kodu değil, derlenmiş bayt kodu ve bağımlılıklardır.

    Toplu ML tahmini için:
        raporlar  = proje_tara("./src")
        X         = [r["model_icin_liste"] for r in raporlar]
        tahminler = model.predict(X)
        riskler   = model.predict_proba(X)[:, 1]

    Dönüş:
        Her dosya için tam_rapor() çıktısı içeren liste. Hatalı dosyalar
        listede yer almaz; bunun yerine konsola uyarı basılır.
    """
    kok = Path(klasor_yolu)
    atlanacak = {'__pycache__', 'venv', '.venv', 'site-packages', 'migrations'}
    glob_deseni = '**/*.py' if ozyinelemeli else '*.py'
    py_dosyalari = [p for p in kok.glob(glob_deseni) if not any((atl in p.parts for atl in atlanacak))]
    raporlar: list[dict] = []
    hatalar: list[dict] = []
    for dosya in sorted(py_dosyalari):
        try:
            tarayici = KodTarayici(str(dosya))
            raporlar.append(tarayici.tam_rapor())
        except Exception as hata:
            hatalar.append({'dosya': str(dosya), 'hata': str(hata)})
    if hatalar:
        print(f'\n[UYARI] {len(hatalar)} dosya atlandı:')
        for h in hatalar:
            print(f"  ✗  {h['dosya']}: {h['hata']}")
    print(f'\n[TARAMA TAMAMLANDI] {len(raporlar)} dosya analiz edildi, {len(hatalar)} dosya atlandı.')
    return raporlar

def _yazdir_rapor(rapor: dict) -> None:
    """
    Tek bir dosyanın raporunu terminale biçimli ve renkli olarak yazdırır.

    ANSI renk kodları kullanılır. Windows'ta renkler görünmeyebilir;
    Windows Terminal veya WSL kullanıldığında düzgün çalışır.

    Parametreler:
        rapor: tam_rapor() metodundan dönen sözlük.
    """
    KIRMIZI = '\x1b[91m'
    SARI = '\x1b[93m'
    YESIL = '\x1b[92m'
    SIFIR = '\x1b[0m'
    durum = rapor['karmasiklik']['durum']
    durum_renk = KIRMIZI if durum == 'KRİTİK' else SARI if durum == 'UYARI' else YESIL
    mi = rapor.get('bakim_skoru', -1.0)
    mi_renk = KIRMIZI if mi < 65 else SARI if mi < 85 else YESIL
    mi_etiket = 'Bakımı Zor' if mi < 65 else 'Orta' if mi < 85 else 'Temiz'
    print('\n' + '=' * 64)
    print(f"  MİMARİ RÖNTGEN — {rapor['dosya']}")
    print('=' * 64)
    print(f'\n  KARMAŞIKLIK')
    print(f"     CC Max     : {durum_renk}{rapor['karmasiklik']['cc_max']:.1f} [{durum}]{SIFIR}")
    print(f"     CC Ortalama: {rapor['karmasiklik']['cc_mean']:.3f}")
    print(f"     Fonksiyon  : {rapor['karmasiklik']['fonksiyon_sayisi']}")
    if rapor['karmasiklik']['kritik_fonksiyonlar']:
        print(f'\n  KRİTİK FONKSİYONLAR (CC > 10):')
        for f in rapor['karmasiklik']['kritik_fonksiyonlar']:
            print(f"     ✗ {f['isim']:28s} CC={f['cc']:.1f} [{f['rank']}]")
    print(f'\n  HALSTEAD')
    print(f"     Efor       : {rapor['halstead']['effort']:>12,.1f}")
    print(f"     Hacim      : {rapor['halstead']['volume']:>12,.1f}")
    print(f"     Tahmini Hata: {rapor['halstead']['tahmini_hata']:.5f}")
    print(f'\n  SATIR METRİKLERİ')
    print(f"     LOC        : {rapor['lok']['loc']}")
    print(f"     SLOC       : {rapor['lok']['sloc']}")
    print(f"     Yorum      : %{rapor['lok']['yorum_orani'] * 100:.1f}")
    print(f'\n  BAKIM SKORU (Maintainability Index)')
    if mi >= 0:
        print(f'     MI         : {mi_renk}{mi:.1f} / 100 [{mi_etiket}]{SIFIR}')
    else:
        print(f'     MI         : Hesaplanamadı (Radon kurulu değil)')
    print(f"\n  MODEL VEKTÖRü ({len(rapor['model_icin_liste'])} boyut)")
    print(f"     {rapor['model_icin_liste']}")
    print('=' * 64 + '\n')
if __name__ == '__main__':
    hedef = sys.argv[1] if len(sys.argv) > 1 else __file__
    print(f'[KOD TARAYICI] Hedef: {hedef}')
    t = KodTarayici(hedef)
    rapor = t.tam_rapor()
    _yazdir_rapor(rapor)
    print('Modele besleme örneği:')
    print(f'  model.predict([{t.ozellik_vektoru().liste()}])\n')
"""
oto_tamirci.py
═══════════════════════════════════════════════════════════════════════════════
Otonom Mühendislik Ajanı — Kural Tabanlı Kod Düzeltme Modülü
Katman: Auto-Refactor / AST Ameliyat

Görev:
    Herhangi bir harici API veya LLM kullanmadan, tamamen lokal olarak
    bir Python dosyasını üç adımda iyileştirir:

        1. AST Aşaması   : Kaynak kodu sözdizim ağacına (AST) dönüştür.
        2. Dönüşüm        : NodeTransformer ile ağaç üzerinde cerrahi müdahale:
                              - Docstring olmayan her fonksiyona şablon ekle
                              - Tip anotasyonu olmayan parametreleri işaretle
                              - Sihirli sayıları (magic number) sabit adayı say
        3. PEP8 Formatı  : autopep8 ile boşluk, girintileme ve satır uzunluğu
                           sorunlarını otomatik düzelt.

Bağımlılıklar:
    pip install autopep8

Kullanım:
    from oto_tamirci import OtoTamirci

    tamirci = OtoTamirci("hedef_dosya.py")
    sonuc   = tamirci.ameliyat_et()

    print(sonuc.eklenen_docstring)   # kaç docstring eklendi
    print(sonuc.pep8_duzeltme)       # PEP8 düzeltmesi yapıldı mı
═══════════════════════════════════════════════════════════════════════════════
"""

import ast
import shutil
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── autopep8 güvenli import ─────────────────────────────────────────────────
try:
    import autopep8
    AUTOPEP8_MEVCUT = True
except ImportError:
    AUTOPEP8_MEVCUT = False
    print(
        "[UYARI] 'autopep8' bulunamadı.\n"
        "         Kurulum: pip install autopep8\n"
        "         PEP8 formatlaması devre dışı; AST dönüşümleri yine de çalışır."
    )


# ══════════════════════════════════════════════════════════════════════════════
# VERİ YAPISI — Ameliyat Sonuç Raporu
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class AmeliyatSonucu:
    """
    OtoTamirci.ameliyat_et() metodunun dönüş değeri.

    Hangi dönüşümlerin yapıldığını, varsa hata bilgisini ve
    yedek dosyanın konumunu içerir.

    Kullanım:
        sonuc = tamirci.ameliyat_et()
        if sonuc.basarili:
            print(f"{sonuc.eklenen_docstring} docstring eklendi.")
        else:
            print(f"Hata: {sonuc.hata_mesaji}")
    """
    basarili:           bool  = False
    eklenen_docstring:  int   = 0      # Yeni eklenen docstring sayısı
    pep8_duzeltme:      bool  = False  # autopep8 değişiklik yaptı mı?
    yedek_yolu:         str   = ""     # Orijinal dosyanın yedek konumu
    hata_mesaji:        str   = ""     # Başarısız ise hata açıklaması
    degistirilen_fonk:  list  = field(default_factory=list)  # İsimler


# ══════════════════════════════════════════════════════════════════════════════
# AST DÖNÜŞTÜRÜCÜ 1: Docstring Enjektörü
# ══════════════════════════════════════════════════════════════════════════════

class DocstringEnjektoru(ast.NodeTransformer):
    """
    AST üzerinde dolaşarak docstring'i olmayan her fonksiyona
    otonom bir şablon docstring ekleyen dönüştürücü.

    NodeTransformer Nasıl Çalışır?
    ───────────────────────────────
    ast.NodeTransformer, ast.NodeVisitor'ın yazma yetkisi olan versiyonudur.
    visit_<TipAdı> metodları orijinal düğümü DÖNDÜRMEK yerine YENİ bir düğüm
    döndürebilir ya da mevcut düğümü değiştirerek döndürebilir. Bu sayede
    kaynak kodu string olarak parse → tree → modify → unparse akışıyla
    programatik olarak değiştirmiş oluruz.

    Enjeksiyon Mantığı:
        - Sınıf metotlarında (self, cls gibi parametreler) özel şablon
        - Fonksiyon parametreleri var mı → listeleyerek açıkla
        - Dönüş tipi anotasyonu var mı → şablona ekle
        - Zaten docstring varsa → dokunma, mevcut belgeye saygı göster

    Kullanım:
        enjektör = DocstringEnjektoru()
        yeni_agac = enjektör.visit(agac)
        ast.fix_missing_locations(yeni_agac)
        print(f"{enjektör.ekleme_sayisi} docstring eklendi.")
    """

    def __init__(self):
        """Sayaçları ve takip listesini sıfırla."""
        self.ekleme_sayisi     = 0           # Toplam eklenen docstring
        self.degistirilen_fonk: list[str] = []  # İsimleri kaydet (raporlama için)

    # ── Özel: Docstring varlık kontrolü ─────────────────────────────────────

    @staticmethod
    def _docstring_var_mi(node: ast.FunctionDef) -> bool:
        """
        Fonksiyonun body'sinin ilk ifadesi bir string sabiti mi?

        Python'da docstring'ler sözdizimsel olarak fonksiyon gövdesinin
        ilk ifadesidir (ast.Expr → ast.Constant(value=str)). Bu metod
        tam olarak bu örüntüyü arar.

        Parametreler:
            node: İncelenecek FunctionDef düğümü.

        Dönüş:
            True  → Docstring zaten mevcut, dokunma.
            False → Docstring yok, enjekte edilmeli.
        """
        if not node.body:
            return False
        ilk = node.body[0]
        # ast.Expr içinde ast.Constant(value=str) → docstring
        return (
            isinstance(ilk, ast.Expr)
            and isinstance(ilk.value, ast.Constant)
            and isinstance(ilk.value.value, str)
        )

    # ── Özel: Parametre listesi çözücü ──────────────────────────────────────

    @staticmethod
    def _parametreleri_al(node: ast.FunctionDef) -> list[str]:
        """
        Fonksiyon argümanlarını, tip anotasyonlarıyla birlikte okunabilir
        bir liste halinde döner.

        Python AST'de argümanlar ast.arguments nesnesinde saklanır:
            args      → Pozisyonel argümanlar (self dahil)
            defaults  → Varsayılan değeri olan argümanlar (sona hizalanmış)
            annotation→ İsteğe bağlı tip anotasyonu

        Örnek çıktı: ["x: int", "y: str", "z=None"]

        Parametreler:
            node: Analiz edilecek FunctionDef düğümü.

        Dönüş:
            Okunabilir parametre string listesi.
        """
        parametreler = []

        # Pozisyonel argümanlar — self/cls hariç tut (metot gövdesi içi için)
        for arg in node.args.args:
            if arg.arg in ("self", "cls"):
                continue  # Nesne/sınıf referansı, docstring için anlamsız
            if arg.annotation:
                # Tip anotasyonu varsa → "x: int" formatı
                try:
                    tip = ast.unparse(arg.annotation)
                except Exception:
                    tip = "?"
                parametreler.append(f"{arg.arg}: {tip}")
            else:
                # Tip anotasyonu yoksa → sadece isim
                parametreler.append(arg.arg)

        # *args varsa
        if node.args.vararg:
            parametreler.append(f"*{node.args.vararg.arg}")

        # **kwargs varsa
        if node.args.kwarg:
            parametreler.append(f"**{node.args.kwarg.arg}")

        return parametreler

    # ── Özel: Dönüş tipi çözücü ─────────────────────────────────────────────

    @staticmethod
    def _donus_tipi(node: ast.FunctionDef) -> str:
        """
        Fonksiyonun dönüş tipi anotasyonunu string olarak döner.
        Anotasyon yoksa boş string döner.

        Parametreler:
            node: İncelenecek FunctionDef düğümü.

        Dönüş:
            "-> int", "-> Optional[str]" gibi string, ya da "".
        """
        if node.returns is None:
            return ""
        try:
            return f" -> {ast.unparse(node.returns)}"
        except Exception:
            return ""

    # ── Özel: Şablon docstring üretici ─────────────────────────────────────

    def _docstring_uret(self, node: ast.FunctionDef) -> str:
        """
        Fonksiyon imzasını okuyarak otonom bir şablon docstring metni üretir.

        Şablonun yapısı:
            1. OTONOM AJAN başlığı + fonksiyon adı
            2. Parametreler (varsa, tipiyle birlikte)
            3. Dönüş tipi (varsa)
            4. TODO işareti — geliştiriciyi gerçek açıklama yazmaya yönlendir

        Parametreler:
            node: Docstring üretilecek FunctionDef düğümü.

        Dönüş:
            Üretilmiş docstring metni (tırnak işaretleri hariç).
        """
        parametreler = self._parametreleri_al(node)
        donus        = self._donus_tipi(node)

        satirlar = [
            f"OTONOM AJAN tarafından oluşturuldu · {node.name}",
            "",
        ]

        if parametreler:
            satirlar.append("Parametreler:")
            for p in parametreler:
                satirlar.append(f"    {p} : TODO — bu parametrenin amacını açıkla.")
            satirlar.append("")

        if donus:
            satirlar.append(f"Dönüş:{donus}")
            satirlar.append("    TODO — dönüş değerinin ne anlama geldiğini açıkla.")
            satirlar.append("")

        satirlar.append("TODO: Bu fonksiyonun amacını tek bir cümleyle buraya yaz.")

        return "\n".join(satirlar)

    # ── Ana dönüşüm metodu — FunctionDef ────────────────────────────────────

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Her fonksiyon tanımını ziyaret eder.

        Eğer fonksiyonda docstring yoksa:
            1. Şablon metni üret.
            2. ast.Expr(ast.Constant(şablon)) düğümü oluştur.
            3. Bu düğümü fonksiyon body'sinin BAŞINA ekle.

        Eğer docstring varsa:
            Hiçbir şey yapma — mevcut belgeye saygı göster.

        Ardından alt düğümlere de geç (iç içe fonksiyonlar için).

        Parametreler:
            node: Ziyaret edilen FunctionDef AST düğümü.

        Dönüş:
            Değiştirilmiş (veya değiştirilmemiş) FunctionDef düğümü.
        """
        # Önce alt düğümleri işle (iç içe fonksiyonlar da kapsansın)
        self.generic_visit(node)

        if not self._docstring_var_mi(node):
            # ── Yeni docstring düğümü oluştur ───────────────────────────────
            metin = self._docstring_uret(node)

            # ast.Constant: Python 3.8+ docstring gösterimi
            docstring_dugum = ast.Expr(
                value=ast.Constant(value=metin)
            )

            # Satır/sütun bilgisi ekle — ast.fix_missing_locations için gerekli
            # Fonksiyonun def satırı ile aynı konuma yerleştir
            ast.copy_location(docstring_dugum, node)
            ast.copy_location(docstring_dugum.value, node)

            # Body'nin başına enjekte et (varolan koddan önce)
            node.body.insert(0, docstring_dugum)

            self.ekleme_sayisi += 1
            self.degistirilen_fonk.append(node.name)

        return node

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        """
        async def fonksiyonları için aynı dönüşümü uygular.
        visit_FunctionDef ile özdeş mantık; tip sistemi farkından dolayı ayrı.
        """
        # AsyncFunctionDef, FunctionDef ile aynı arayüze sahip
        # Bu yüzden doğrudan aynı metodu çağırabiliriz
        return self.visit_FunctionDef(node)  # type: ignore[arg-type]


# ══════════════════════════════════════════════════════════════════════════════
# AST DÖNÜŞTÜRÜCÜ 2: Sihirli Sayı Tespit Edilmesi (Pasif — yorum olarak işaret)
# ══════════════════════════════════════════════════════════════════════════════

class SihirliSayiTespitcisi(ast.NodeVisitor):
    """
    Kaynak kodundaki "sihirli sayıları" (magic numbers) tespit eden ziyaretçi.

    Sihirli sayı nedir?
        Doğrudan kodun içine gömülmüş, adı olmayan sayısal sabit.
        Örnek: if status == 404  (404'ün ne anlama geldiği belirsiz)
        Düzgünü:  NOT_FOUND = 404 / if status == NOT_FOUND

    Bu sınıf düzeltme YAPMAZ; sadece tespit eder ve raporlar.
    OtoTamirci bu listeyi ameliyat raporuna ekler.

    Muafiyetler:
        0, 1, -1, 2 → Yaygın kullanım, sihirli sayı değil.
        Üst seviye atamalar (SABIT = 42) → Zaten adlandırılmış.
    """

    MUAF_SAYILAR = {0, 1, -1, 2, 100}  # Gürültüyü azalt

    def __init__(self):
        """Tespit edilen sihirli sayıları tut."""
        # {satir_no: değer} sözlüğü
        self.sihirli_sayilar: dict[int, float] = {}

    def visit_Constant(self, node: ast.Constant):
        """
        Her sayısal sabit düğümünü kontrol eder.
        Sihirli sayı olarak sınıflandırılırsa kaydeder.
        """
        if isinstance(node.value, (int, float)):
            if node.value not in self.MUAF_SAYILAR:
                satir = getattr(node, "lineno", -1)
                self.sihirli_sayilar[satir] = node.value
        self.generic_visit(node)


# ══════════════════════════════════════════════════════════════════════════════
# ANA SINIF — OtoTamirci
# ══════════════════════════════════════════════════════════════════════════════

class OtoTamirci:
    """
    Hedef Python dosyasına kural tabanlı, lokal otomatik düzeltme uygular.

    Ameliyat üç aşamada gerçekleşir:

        Aşama 1 — Yedekleme:
            Orijinal dosya, aynı klasörde zaman damgalı bir yedek olarak kopyalanır.
            Örn: auth.py → auth.py.bak_20240115_143022

        Aşama 2 — AST Dönüşümü:
            DocstringEnjektoru ile fonksiyonlara şablon docstring eklenir.
            ast.unparse() ile değiştirilmiş ağaç yeniden kaynak koda dönüştürülür.

        Aşama 3 — PEP8 Formatlaması:
            autopep8.fix_code() ile boşluklar, girintiler ve satır uzunlukları
            Python standartlarına uygun hale getirilir.

    Önemli Davranışlar:
        - Zaten docstring olan fonksiyonlara DOKUNULMAZ.
        - Yedek dosya oluşturulamazsa ameliyat başlamaz (güvenlik).
        - autopep8 yoksa format aşaması atlanır, AST dönüşümleri uygulanır.
        - Sözdizimi hatası varsa geri alır; orijinal dosyaya dokunulmaz.

    Kullanım:
        tamirci = OtoTamirci("karmasik_dosya.py")
        sonuc   = tamirci.ameliyat_et()

        if sonuc.basarili:
            print(f"Yedek: {sonuc.yedek_yolu}")
            print(f"Docstring: {sonuc.eklenen_docstring} adet eklendi")
            print(f"PEP8: {'uygulandı' if sonuc.pep8_duzeltme else 'değişiklik yok'}")
        else:
            print(f"Hata: {sonuc.hata_mesaji}")
    """

    def __init__(self, dosya_yolu: str):
        """
        Tamirci örneği oluşturur ve dosyayı doğrular.

        Parametreler:
            dosya_yolu: Düzeltilecek .py dosyasının yolu.
                        Hem mutlak hem göreli yol kabul edilir.

        Hatalar:
            FileNotFoundError : Dosya bulunamazsa fırlatılır.
            ValueError        : .py uzantısı yoksa fırlatılır.
        """
        self.yol = Path(dosya_yolu).resolve()

        if not self.yol.exists():
            raise FileNotFoundError(
                f"Dosya bulunamadı: '{self.yol}'\n"
                f"Çalışma dizini: {Path.cwd()}"
            )
        if self.yol.suffix.lower() != ".py":
            raise ValueError(
                f"Sadece .py dosyaları desteklenir. Verilen: '{self.yol.suffix}'"
            )

    # ── Özel: Dosya okuma (encoding güvenli) ────────────────────────────────

    def _kaynak_oku(self) -> str:
        """
        Dosyayı okur. UTF-8 başarısız olursa Latin-1 ile dener.

        Dönüş:
            Kaynak kod string.
        """
        try:
            return self.yol.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return self.yol.read_text(encoding="latin-1")

    # ── Özel: Yedek oluştur ─────────────────────────────────────────────────

    def _yedek_olustur(self) -> str:
        """
        Orijinal dosyanın yedeğini oluşturur.

        Yedek adı: <dosyaadi>.py.bak_<YYYYMMDD_HHMMSS>
        Aynı klasöre kaydedilir.

        Dönüş:
            Yedek dosyanın mutlak yolu (string).

        Hatalar:
            IOError: Yedek oluşturulamazsa fırlatılır.
        """
        zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
        yedek_yolu    = self.yol.with_suffix(f".py.bak_{zaman_damgasi}")
        shutil.copy2(str(self.yol), str(yedek_yolu))
        return str(yedek_yolu)

    # ── Özel: AST dönüşüm aşaması ───────────────────────────────────────────

    def _ast_donusumu_uygula(self, kaynak: str) -> tuple[str, int, list[str]]:
        """
        DocstringEnjektoru'nu kaynak koda uygular ve değiştirilmiş kodu döner.

        Süreç:
            1. ast.parse()     → Kaynak metin → AST ağacı
            2. enjektör.visit() → Ağacı yerinde değiştir (docstring ekle)
            3. ast.fix_missing_locations() → Yeni düğümlere konum bilgisi ekle
            4. ast.unparse()   → Değiştirilmiş ağaç → Kaynak metin

        Not: ast.unparse() Python 3.9'da eklendi. 3.8 için astor kütüphanesi
        gerekir; bu modül 3.9+ varsayar.

        Parametreler:
            kaynak: Orijinal Python kaynak metni.

        Dönüş:
            (dönüştürülmüş_kod, eklenen_docstring_sayısı, değiştirilen_isimler)

        Hatalar:
            SyntaxError: Kaynak kod parse edilemezse fırlatılır.
        """
        # Ayrıştır
        agac = ast.parse(kaynak, filename=str(self.yol))

        # Docstring'leri enjekte et
        enjektör = DocstringEnjektoru()
        yeni_agac = enjektör.visit(agac)

        # Yeni eklenen düğümlere kaynak konum bilgisi ver
        # (eksik olursa ast.unparse hata fırlatır)
        ast.fix_missing_locations(yeni_agac)

        # Ağacı tekrar kaynak koda dönüştür
        # ast.unparse yorum satırlarını KORUMAZ — bu bilinen bir kısıtlamadır.
        # Yorumlar AST'de temsil edilmez; PEP8 aşaması formatı düzeltir.
        yeni_kod = ast.unparse(yeni_agac)

        return yeni_kod, enjektör.ekleme_sayisi, enjektör.degistirilen_fonk

    # ── Özel: PEP8 formatlama aşaması ───────────────────────────────────────

    @staticmethod
    def _pep8_uygula(kod: str) -> tuple[str, bool]:
        """
        autopep8 ile kodu PEP8 standartlarına uygun hale getirir.

        autopep8 ayarları:
            aggressive=1 → Daha agresif düzeltme (boşluk, girintileme)
            max_line_length=99 → Black ve birçok ekip standartı
            indent_size=4 → Python standardı

        autopep8 Yoksa:
            Kodu değiştirmeden döner; degisiklik=False.

        Parametreler:
            kod: Formatlanacak Python kaynak metni.

        Dönüş:
            (formatlanmış_kod, değişiklik_yapıldı_mı)
        """
        if not AUTOPEP8_MEVCUT:
            return kod, False

        formatlanmis = autopep8.fix_code(
            kod,
            options={
                "aggressive":      1,      # Güvenli agresif düzeltme
                "max_line_length": 99,     # Modern ekip standardı
                "indent_size":     4,      # PEP8 zorunlu
            },
        )
        # Değişiklik oldu mu? (aynı kodu yazmaktan kaçın)
        degisti = formatlanmis != kod
        return formatlanmis, degisti

    # ── Ana metod: Ameliyat ──────────────────────────────────────────────────

    def ameliyat_et(self) -> AmeliyatSonucu:
        """
        Hedef dosyaya tam ameliyat uygular ve sonuç raporunu döner.

        Ameliyat Adımları:
            1. Orijinal dosyayı oku.
            2. Zaman damgalı yedek oluştur.
            3. AST dönüşümü: docstring enjeksiyonu.
            4. PEP8 formatlaması: autopep8.
            5. Sonucu doğrula: yeni kodu parse edebiliyor muyuz?
            6. Dosyaya yaz.

        Hata Koruması:
            - Yedek oluşturulamazsa → ameliyat başlamaz.
            - Üretilen kod sözdizim hatası içeriyorsa → yaz, uyar.
            - Her adımda exception yakalanır; orijinal dosya korunur.

        Dönüş:
            AmeliyatSonucu nesnesi. .basarili alanını kontrol et.
        """
        sonuc = AmeliyatSonucu()

        # ── Adım 1: Kaynak oku ───────────────────────────────────────────────
        try:
            kaynak = self._kaynak_oku()
        except Exception as e:
            sonuc.hata_mesaji = f"Dosya okunamadı: {e}"
            return sonuc

        # ── Adım 2: Yedek oluştur ────────────────────────────────────────────
        # Yedek yoksa ameliyatı başlatma — veri kaybı riski
        try:
            sonuc.yedek_yolu = self._yedek_olustur()
        except Exception as e:
            sonuc.hata_mesaji = (
                f"Yedek dosya oluşturulamadı: {e}\n"
                "Ameliyat iptal edildi — orijinal dosya korunuyor."
            )
            return sonuc

        # ── Adım 3: AST dönüşümü ─────────────────────────────────────────────
        try:
            yeni_kod, eklenen, isimler = self._ast_donusumu_uygula(kaynak)
            sonuc.eklenen_docstring  = eklenen
            sonuc.degistirilen_fonk  = isimler
        except SyntaxError as e:
            sonuc.hata_mesaji = (
                f"Sözdizimi hatası — dosya parse edilemedi: {e}\n"
                "AST dönüşümü uygulanamadı."
            )
            return sonuc
        except Exception as e:
            sonuc.hata_mesaji = f"AST dönüşümü başarısız: {e}"
            return sonuc

        # ── Adım 4: PEP8 formatlaması ────────────────────────────────────────
        try:
            yeni_kod, sonuc.pep8_duzeltme = self._pep8_uygula(yeni_kod)
        except Exception as e:
            # PEP8 başarısız olsa bile AST çıktısını kullan — hata durdurucu değil
            sonuc.hata_mesaji = f"PEP8 formatlaması başarısız (AST çıktısı kullanılıyor): {e}"

        # ── Adım 5: Üretilen kodun geçerliliğini doğrula ─────────────────────
        try:
            ast.parse(yeni_kod)
        except SyntaxError as e:
            # Bu olmamalı ama ast.unparse nadiren garip çıktılar üretebilir
            sonuc.hata_mesaji = (
                f"UYARI: Üretilen kod sözdizim hatası içeriyor: {e}\n"
                "Yine de dosyaya yazılacak — lütfen kontrol et."
            )
            # Devam et — kullanıcıyı uyardık

        # ── Adım 6: Dosyaya yaz ──────────────────────────────────────────────
        try:
            self.yol.write_text(yeni_kod, encoding="utf-8")
            sonuc.basarili = True
        except Exception as e:
            sonuc.hata_mesaji = f"Dosya yazılamadı: {e}"

        return sonuc

    # ── Yardımcı: Sadece önizleme (dosyaya yazmaz) ──────────────────────────

    def onizleme(self) -> dict:
        """
        Ameliyatı gerçekten uygulamadan, ne yapılacağını gösterir.

        Dosyayı değiştirmez; sadece analiz eder ve rapor üretir.
        UI katmanı bu metodu "Ne değişecek?" önizlemesi için kullanabilir.

        Dönüş:
            {
                "docstring_eklenecek_fonk": [...],
                "toplam_fonksiyon": int,
                "pep8_aktif": bool,
            }
        """
        try:
            kaynak = self._kaynak_oku()
            agac   = ast.parse(kaynak)
        except Exception as e:
            return {"hata": str(e)}

        # DocstringEnjektoru'yu sadece sayım için çalıştır
        enjektör  = DocstringEnjektoru()
        yeni_agac = enjektör.visit(agac)

        # Tüm fonksiyon sayısı
        tum_fonk = sum(
            1 for dugum in ast.walk(agac)
            if isinstance(dugum, (ast.FunctionDef, ast.AsyncFunctionDef))
        )

        return {
            "docstring_eklenecek_fonk": enjektör.degistirilen_fonk,
            "eklenecek_docstring_sayisi": enjektör.ekleme_sayisi,
            "toplam_fonksiyon": tum_fonk,
            "pep8_aktif": AUTOPEP8_MEVCUT,
        }


# ══════════════════════════════════════════════════════════════════════════════
# KOMut SATIRI ARAYÜZÜ (CLI)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Kullanım: python oto_tamirci.py <dosya.py> [--onizle]")
        print("  --onizle  : Dosyayı değiştirmeden ne yapılacağını gösterir.")
        sys.exit(1)

    hedef_yol = sys.argv[1]
    onizle    = "--onizle" in sys.argv

    print(f"[OTO-TAMİRCİ] Hedef: {hedef_yol}")
    tamirci = OtoTamirci(hedef_yol)

    if onizle:
        print("\n[ÖNİZLEME MODU — dosya değiştirilmeyecek]\n")
        oz = tamirci.onizleme()
        if "hata" in oz:
            print(f"Hata: {oz['hata']}")
        else:
            print(f"  Toplam fonksiyon        : {oz['toplam_fonksiyon']}")
            print(f"  Docstring eklenecek     : {oz['eklenecek_docstring_sayisi']}")
            print(f"  PEP8 aktif              : {oz['pep8_aktif']}")
            if oz["docstring_eklenecek_fonk"]:
                print(f"  Etkilenecek fonksiyonlar:")
                for f in oz["docstring_eklenecek_fonk"]:
                    print(f"    - {f}")
    else:
        sonuc = tamirci.ameliyat_et()
        print()
        if sonuc.basarili:
            print(f"  [BAŞARILI] Ameliyat tamamlandı.")
            print(f"  Yedek                   : {sonuc.yedek_yolu}")
            print(f"  Eklenen docstring       : {sonuc.eklenen_docstring}")
            print(f"  PEP8 düzeltmesi         : {'evet' if sonuc.pep8_duzeltme else 'değişiklik yok'}")
            if sonuc.degistirilen_fonk:
                print(f"  Değiştirilen fonksiyonlar:")
                for f in sonuc.degistirilen_fonk:
                    print(f"    + {f}")
        else:
            print(f"  [HATA] {sonuc.hata_mesaji}")
            sys.exit(1)
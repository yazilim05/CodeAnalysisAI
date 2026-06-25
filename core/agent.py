"""
gelismis_ajan.py
═══════════════════════════════════════════════════════════════════════════════
CodeAnalysis AI — Gelişmiş Karar & Refactor Motoru
═══════════════════════════════════════════════════════════════════════════════
"""
import ast
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
try:
    from radon.complexity import cc_visit
    RADON_MEVCUT = True
except ImportError:
    RADON_MEVCUT = False
TIP_SOZLUGU = {'int': 'tam sayı', 'float': 'ondalık', 'str': 'metin', 'bool': 'boolean', 'list': 'liste', 'dict': 'sözlük', 'tuple': 'demet', 'set': 'küme', 'None': 'boş', 'Any': 'herhangi tip', 'Optional': 'isteğe bağlı'}

@dataclass
class MimariElestiri:
    seviye: str
    kategori: str
    baslik: str
    mesaj: str
    cozum: str = ''

@dataclass
class RefactorSonucu:
    basarili: bool = False
    once_kod: str = ''
    sonra_kod: str = ''
    yedek_yolu: str = ''
    islem_listesi: list = field(default_factory=list)
    hata_mesaji: str = ''

@dataclass
class DokumantasyonSonucu:
    basarili: bool = False
    cikti_yolu: str = ''
    taranan_dosya: int = 0
    sinif_sayisi: int = 0
    fonksiyon_sayisi: int = 0
    md_uzunlugu: int = 0
    mermaid_kodu: str = ''
    hata_mesaji: str = ''

@dataclass
class KomponentAyirmaSonucu:
    basarili: bool = False
    once_kod: str = ''
    sonra_kod: str = ''
    yedek_yolu: str = ''
    olusturulan_dosyalar: list = field(default_factory=list)
    ayrilan_sinif_sayisi: int = 0
    hata_mesaji: str = ''

def _kosul_tersle(test: ast.expr) -> ast.expr:
    """Otonom Docstring: _kosul_tersle metodu."""
    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        op = test.ops[0]
        ters_op_map = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.GtE, ast.Gt: ast.LtE, ast.LtE: ast.Gt, ast.GtE: ast.Lt, ast.Is: ast.IsNot, ast.IsNot: ast.Is, ast.In: ast.NotIn, ast.NotIn: ast.In}
        for orig_tip, ters_tip in ters_op_map.items():
            if isinstance(op, orig_tip):
                yeni = ast.Compare(left=test.left, ops=[ters_tip()], comparators=test.comparators)
                ast.copy_location(yeni, test)
                return yeni
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return test.operand
    yeni = ast.UnaryOp(op=ast.Not(), operand=test)
    ast.copy_location(yeni, test)
    return yeni

def _docstring_var_mi(node) -> bool:
    """Otonom Docstring: _docstring_var_mi metodu."""
    if not getattr(node, 'body', None):
        return False
    ilk = node.body[0]
    return isinstance(ilk, ast.Expr) and isinstance(ilk.value, ast.Constant) and isinstance(ilk.value.value, str)

class GuardClauseTransformer(ast.NodeTransformer):

    def __init__(self):
        """Otonom Docstring: __init__ metodu."""
        self.donusum_sayisi = 0
        self.degistirilen_fonk = []

    def visit_AsyncFunctionDef(self, node):
        """Otonom Docstring: visit_AsyncFunctionDef metodu."""
        return self.visit_FunctionDef(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Otonom Docstring: visit_FunctionDef metodu."""
        self.generic_visit(node)
        if not node.body:
            return node
        docstring_dugum, gercek_govde = (None, node.body)
        if _docstring_var_mi(node):
            docstring_dugum, gercek_govde = (node.body[0], node.body[1:])
        if not gercek_govde:
            return node
        guards, mevcut = ([], gercek_govde)
        while len(mevcut) == 1 and isinstance(mevcut[0], ast.If) and (not mevcut[0].orelse) and (len(mevcut[0].body) >= 1):
            if_node = mevcut[0]
            guard = ast.If(test=_kosul_tersle(if_node.test), body=[ast.Return(value=ast.Constant(value=None))], orelse=[])
            ast.copy_location(guard, if_node)
            ast.fix_missing_locations(guard)
            guards.append(guard)
            mevcut = if_node.body
        if not (len(guards) >= 2 or (len(guards) == 1 and len(mevcut) >= 2)):
            return node
        node.body = ([docstring_dugum] if docstring_dugum else []) + guards + mevcut
        self.donusum_sayisi += 1
        self.degistirilen_fonk.append(node.name)
        ast.fix_missing_locations(node)
        return node

class AkilliDocstringEnjektoru(ast.NodeTransformer):

    def __init__(self):
        """Otonom Docstring: __init__ metodu."""
        self.ekleme_sayisi = 0
        self.degistirilen_fonk = []

    def visit_AsyncFunctionDef(self, node):
        """Otonom Docstring: visit_AsyncFunctionDef metodu."""
        return self.visit_FunctionDef(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Otonom Docstring: visit_FunctionDef metodu."""
        self.generic_visit(node)
        if _docstring_var_mi(node):
            return node
        metin = f'Otonom Docstring: {node.name} metodu.'
        ds_node = ast.Expr(value=ast.Constant(value=metin))
        ast.copy_location(ds_node, node)
        node.body.insert(0, ds_node)
        self.ekleme_sayisi += 1
        self.degistirilen_fonk.append(node.name)
        return node

class _DerinYapiTarayici(ast.NodeVisitor):

    def __init__(self):
        """Otonom Docstring: __init__ metodu."""
        self.sinif_metod_sayilari = {}
        self.genis_imza_fonk = []
        self.derin_ic_ice_fonk = []
        self.toplam_fonksiyon = 0
        self._mevcut_sinif = None
        self._derinlik = 0
        self._derinlik_max_fonk = {}

    def visit_ClassDef(self, node):
        """Otonom Docstring: visit_ClassDef metodu."""
        eski = self._mevcut_sinif
        self._mevcut_sinif = node.name
        self.sinif_metod_sayilari[node.name] = sum((1 for c in node.body if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))))
        self.generic_visit(node)
        self._mevcut_sinif = eski

    def visit_FunctionDef(self, node):
        """Otonom Docstring: visit_FunctionDef metodu."""
        self.toplam_fonksiyon += 1
        param_sayisi = len([a for a in node.args.args if a.arg not in ('self', 'cls')])
        if param_sayisi > 5:
            self.genis_imza_fonk.append((node.name, param_sayisi))
        eski_derinlik = self._derinlik
        self._derinlik = 0
        self._derinlik_max_fonk[node.name] = 0
        self.generic_visit(node)
        if self._derinlik_max_fonk.get(node.name, 0) >= 4:
            self.derin_ic_ice_fonk.append((node.name, self._derinlik_max_fonk[node.name]))
        self._derinlik = eski_derinlik

    def visit_AsyncFunctionDef(self, node):
        """Otonom Docstring: visit_AsyncFunctionDef metodu."""
        return self.visit_FunctionDef(node)

    def _derinlige_gir(self):
        """Otonom Docstring: _derinlige_gir metodu."""
        self._derinlik += 1

    def _derinlikten_cik(self):
        """Otonom Docstring: _derinlikten_cik metodu."""
        self._derinlik -= 1

    def visit_For(self, node):
        """Otonom Docstring: visit_For metodu."""
        self._derinlige_gir()
        self.generic_visit(node)
        self._derinlikten_cik()

    def visit_While(self, node):
        """Otonom Docstring: visit_While metodu."""
        self._derinlige_gir()
        self.generic_visit(node)
        self._derinlikten_cik()

    def visit_If(self, node):
        """Otonom Docstring: visit_If metodu."""
        self._derinlige_gir()
        self.generic_visit(node)
        self._derinlikten_cik()

class MimariElestirmen:

    def __init__(self, cc_max, cc_kritik, derin_yapi, toplam_loc, fan_out, sinif_sayisi, instability):
        """Otonom Docstring: __init__ metodu."""
        self.cc_max = cc_max
        self.cc_kritik = cc_kritik
        self.dy = derin_yapi
        self.fan_out = fan_out
        self.instability = instability

    def elestirileri_uret(self):
        """Otonom Docstring: elestirileri_uret metodu."""
        elestiriler = []
        if self.cc_max > 15:
            elestiriler.append(MimariElestiri('kritik', 'Spagetti Kod', 'Karmaşıklık Sınırı Aşıldı!', "Kodun karmaşıklığı 15'in üzerinde. Bu tam bir spagetti koddur ve test edilmesi, okunması çok zordur.", 'Fonksiyonu daha küçük parçalara bölün (Extract Method).'))
        elif self.cc_max > 10:
            elestiriler.append(MimariElestiri('uyari', 'Karmaşıklık', 'Spagettiye Gidiyor', "Karmaşıklık seviyesi 10'un üzerinde. Kısa süre sonra kontrol edilemez hale gelecek.", 'İç içe if bloklarını erken dönüşlerle (Guard Clauses) düzeltin.'))
        for f, d in self.dy.derin_ic_ice_fonk:
            if d >= 4:
                elestiriler.append(MimariElestiri('uyari', 'Performans', 'Derin İç İçe Bloklar', f'`{f}` fonksiyonunda okumayı zorlaştıran iç içe {d} katman var.', 'İç döngüleri ayrı bir fonksiyona çıkarın.'))
        if self.fan_out > 12 and self.instability > 0.85:
            elestiriler.append(MimariElestiri('kritik', 'Mimari', 'God Module (Aşırı Bağımlı)', 'Bu dosya projedeki her şeye bağımlı hale gelmiş.', 'Dosyayı sorumluluklarına göre birden fazla modüle ayırın.'))
        for s_ad, ms in self.dy.sinif_metod_sayilari.items():
            if ms > 15:
                elestiriler.append(MimariElestiri('kritik', 'Mimari', 'God Class Tespiti', f'`{s_ad}` sınıfında {ms} metod var. Çok fazla iş yapıyor.', 'Sınıfı daha küçük sınıflara ayırın.'))
        return elestiriler

class GelismisAjan:

    def __init__(self, dosya_yolu: str):
        """Otonom Docstring: __init__ metodu."""
        self.yol = Path(dosya_yolu).resolve()
        try:
            self._kaynak = self.yol.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            self._kaynak = self.yol.read_text(encoding='latin-1')
        self._agac = ast.parse(self._kaynak, filename=str(self.yol))

    def analiz_et(self) -> tuple:
        """Otonom Docstring: analiz_et metodu."""
        cc_max = 0.0
        cc_kritik = []
        if RADON_MEVCUT:
            try:
                sonuclar = cc_visit(self._kaynak)
                if sonuclar:
                    cc_max = max((b.complexity for b in sonuclar))
                    cc_kritik = [{'isim': b.name, 'cc': b.complexity} for b in sonuclar if b.complexity > 10]
            except:
                pass
        dy = _DerinYapiTarayici()
        dy.visit(self._agac)
        fan_out = sum((1 for n in ast.walk(self._agac) if isinstance(n, (ast.Import, ast.ImportFrom))))
        sinif_sayisi = len(dy.sinif_metod_sayilari)
        instability = round(fan_out / (sinif_sayisi + fan_out), 4) if sinif_sayisi + fan_out > 0 else 1.0
        toplam_loc = len(self._kaynak.splitlines())
        elestirmen = MimariElestirmen(cc_max, cc_kritik, dy, toplam_loc, fan_out, sinif_sayisi, instability)
        elestiriler = elestirmen.elestirileri_uret()
        metrikler = {'loc': toplam_loc, 'cc_max': cc_max, 'fonksiyon_sayisi': dy.toplam_fonksiyon, 'sinif_sayisi': sinif_sayisi}
        return (elestiriler, metrikler)

    def refactor_et(self) -> RefactorSonucu:
        """Otonom Docstring: refactor_et metodu."""
        sonuc = RefactorSonucu(once_kod=self._kaynak)
        zaman = datetime.now().strftime('%Y%m%d_%H%M%S')
        sonuc.yedek_yolu = str(self.yol.with_suffix(f'.py.bak_{zaman}'))
        shutil.copy2(str(self.yol), sonuc.yedek_yolu)
        agac = ast.parse(self._kaynak)
        gt = GuardClauseTransformer()
        agac = gt.visit(agac)
        ast.fix_missing_locations(agac)
        dt = AkilliDocstringEnjektoru()
        agac = dt.visit(agac)
        ast.fix_missing_locations(agac)
        if gt.donusum_sayisi > 0:
            sonuc.islem_listesi.append(f'{gt.donusum_sayisi} fonksiyon düzleştirildi.')
        if dt.ekleme_sayisi > 0:
            sonuc.islem_listesi.append(f'{dt.ekleme_sayisi} fonksiyona docstring eklendi.')
        if not sonuc.islem_listesi:
            sonuc.islem_listesi.append('Refactor edilecek bir durum bulunamadı.')
        yeni_kod = ast.unparse(agac)
        self.yol.write_text(yeni_kod, encoding='utf-8')
        sonuc.basarili = True
        sonuc.sonra_kod = yeni_kod
        return sonuc

    def kusursuz_mu(self) -> tuple:
        """Otonom Docstring: kusursuz_mu metodu."""
        sebepler = []
        for d in ast.walk(self._agac):
            if isinstance(d, ast.If) and (not d.orelse) and (len(d.body) == 1) and isinstance(d.body[0], ast.If):
                sebepler.append('İç içe if blokları tespit edildi (AST ile düzeltilebilir).')
                break
        docstring_eksik = 0
        for d in ast.walk(self._agac):
            if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef)) and (not _docstring_var_mi(d)):
                docstring_eksik += 1
        if docstring_eksik > 0:
            sebepler.append(f'{docstring_eksik} fonksiyonda docstring eksik (AST ile eklenebilir).')
        return (len(sebepler) == 0, sebepler)

    def komponentlere_ayir(self, metod_esigi=10):
        """Otonom Docstring: komponentlere_ayir metodu."""
        return KomponentAyirici(str(self.yol), metod_esigi).ayir()

    @staticmethod
    def projeyi_dokumante_et(klasor_yolu):
        """Otonom Docstring: projeyi_dokumante_et metodu."""
        return OtonomDokumantasyonJeneratoru(klasor_yolu).dokumante_et()

class OtonomDokumantasyonJeneratoru:

    def __init__(self, klasor_yolu):
        """Otonom Docstring: __init__ metodu."""
        self.kok = Path(klasor_yolu).resolve()

    def _dosya_yapisini_cikar(self, yol: Path):
        """Otonom Docstring: _dosya_yapisini_cikar metodu."""
        try:
            kaynak = yol.read_text(encoding='utf-8')
        except:
            try:
                kaynak = yol.read_text(encoding='latin-1')
            except:
                return None
        try:
            agac = ast.parse(kaynak)
        except:
            return None
        cc_map = {}
        if RADON_MEVCUT:
            try:
                for b in cc_visit(kaynak):
                    cc_map[b.name] = b.complexity
            except:
                pass
        siniflar = []
        fonksiyonlar = []
        for dugum in agac.body:
            if isinstance(dugum, ast.ClassDef):
                metotlar = [{'ad': c.name, 'parametreler': [a.arg for a in c.args.args if a.arg != 'self'], 'donus_tipi': '—', 'docstring': ast.get_docstring(c) or '', 'cc': cc_map.get(c.name, '—')} for c in dugum.body if isinstance(c, ast.FunctionDef)]
                siniflar.append({'ad': dugum.name, 'docstring': ast.get_docstring(dugum) or '', 'metotlar': metotlar, 'satir': getattr(dugum, 'lineno', 0)})
            elif isinstance(dugum, ast.FunctionDef):
                fonksiyonlar.append({'ad': dugum.name, 'parametreler': [a.arg for a in dugum.args.args], 'donus_tipi': '—', 'docstring': ast.get_docstring(dugum) or '', 'cc': cc_map.get(dugum.name, '—')})
        return {'modul_docstring': ast.get_docstring(agac) or '', 'siniflar': siniflar, 'fonksiyonlar': fonksiyonlar, 'satir_sayisi': len(kaynak.splitlines())}

    def _md_fonksiyon_tablosu(self, fonksiyonlar, metot_modu=False):
        """Otonom Docstring: _md_fonksiyon_tablosu metodu."""
        if not fonksiyonlar:
            return '*Tanımlı fonksiyon yok.*\n'
        tablo = f"| {('🔧 Metot' if metot_modu else '⚙️ Fonksiyon')} | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |\n|---|---|---|---|---|\n"
        for f in fonksiyonlar:
            p_metni = ' · '.join((f'`{p}`' for p in f['parametreler'])) if f['parametreler'] else '—'
            doc = f['docstring'].replace('\n', ' ')[:100] if f['docstring'] else '*—*'
            cc_deger = f.get('cc', '—')
            if isinstance(cc_deger, int) and cc_deger > 10:
                cc_deger = f'**{cc_deger} (Spagetti!)**'
            tablo += f"| `{f['ad']}()` | {p_metni} | `{f['donus_tipi']}` | {cc_deger} | {doc} |\n"
        return tablo + '\n'

    def dokumante_et(self):
        """Otonom Docstring: dokumante_et metodu."""
        sonuc = DokumantasyonSonucu()
        dosyalar = [p for p in self.kok.rglob('*.py') if 'venv' not in p.parts and 'bak' not in p.name]
        toplam_cc = 0
        cc_sayilan = 0
        spagetti_fonksiyon_sayisi = 0
        for yol in dosyalar:
            try:
                for b in cc_visit(yol.read_text(encoding='utf-8', errors='ignore')):
                    toplam_cc += b.complexity
                    cc_sayilan += 1
                    if b.complexity > 10:
                        spagetti_fonksiyon_sayisi += 1
            except:
                pass
        ortalama_cc = round(toplam_cc / cc_sayilan, 2) if cc_sayilan > 0 else 0
        spagetti_mesaj = f'⚠️ Projede **{spagetti_fonksiyon_sayisi}** adet aşırı karmaşık (Spagetti) fonksiyon tespit edildi.' if spagetti_fonksiyon_sayisi > 0 else '✨ Projede spagetti kod tespit edilmedi.'
        md = f'# 📐 CodeAnalysis AI Raporu\n> 🏛 Proje: `{self.kok.name}`\n> 🧠 Ortalama Karmaşıklık: **{ortalama_cc}**\n> {spagetti_mesaj}\n\n---\n'
        try:
            mermaid_kodu = BagimlilikHaritalayici(str(self.kok)).mermaid_uret()
        except:
            mermaid_kodu = ''
        for yol in dosyalar:
            yapi = self._dosya_yapisini_cikar(yol)
            if not yapi:
                continue
            md += f'## 📄 Modül: `{yol.name}`\n\n'
            for s in yapi['siniflar']:
                ikon = ' ⚠️ God Class Riski!' if len(s['metotlar']) >= 10 else ''
                md += f"#### 🟣 `{s['ad']}` *({len(s['metotlar'])} metot{ikon})*\n\n"
                md += self._md_fonksiyon_tablosu(s['metotlar'], True)
            md += '### ⚙️ Fonksiyonlar\n\n' + self._md_fonksiyon_tablosu(yapi['fonksiyonlar'])
        cikti = self.kok / 'README.md'
        cikti.write_text(md, encoding='utf-8')
        sonuc.basarili = True
        sonuc.cikti_yolu = str(cikti)
        sonuc.mermaid_kodu = mermaid_kodu
        return sonuc

class KomponentAyirici:

    def __init__(self, dosya, metod_esigi):
        """Otonom Docstring: __init__ metodu."""
        self.yol = Path(dosya)
        self.esik = metod_esigi
        try:
            self._kaynak = self.yol.read_text(encoding='utf-8')
        except:
            self._kaynak = self.yol.read_text(encoding='latin-1')

    def ayir(self):
        """Otonom Docstring: ayir metodu."""
        sonuc = KomponentAyirmaSonucu(once_kod=self._kaynak)
        try:
            agac = ast.parse(self._kaynak)
        except Exception as e:
            sonuc.hata_mesaji = str(e)
            return sonuc
        hedefler = [d for d in agac.body if isinstance(d, ast.ClassDef) and sum((1 for c in d.body if isinstance(c, ast.FunctionDef))) > self.esik]
        if not hedefler:
            sonuc.basarili = True
            sonuc.sonra_kod = self._kaynak
            sonuc.hata_mesaji = 'Ayrılacak God Class bulunamadı.'
            return sonuc
        zaman = datetime.now().strftime('%Y%m%d_%H%M%S')
        sonuc.yedek_yolu = str(self.yol.with_suffix(f'.py.bak_{zaman}'))
        shutil.copy2(str(self.yol), sonuc.yedek_yolu)
        importlar = [d for d in agac.body if isinstance(d, (ast.Import, ast.ImportFrom))]
        olusturulanlar = []
        eklenenler = []
        for h in hedefler:
            modul_adi = f'bilesen_{h.name}'
            yeni_yol = self.yol.parent / f'{modul_adi}.py'
            yeni_modul = ast.Module(body=importlar + [h], type_ignores=[])
            ast.fix_missing_locations(yeni_modul)
            yeni_yol.write_text(ast.unparse(yeni_modul), encoding='utf-8')
            olusturulanlar.append((h.name, str(yeni_yol)))
            eklenenler.append((h.name, modul_adi))
        yeni_govde = [d for d in agac.body if not (isinstance(d, ast.ClassDef) and d.name in [h.name for h in hedefler])]
        for s_ad, m_ad in eklenenler:
            yeni_import = ast.ImportFrom(module=m_ad, names=[ast.alias(name=s_ad, asname=None)], level=0)
            ast.fix_missing_locations(yeni_import)
            yeni_govde.insert(0, yeni_import)
        agac.body = yeni_govde
        ast.fix_missing_locations(agac)
        sonuc.sonra_kod = ast.unparse(agac)
        self.yol.write_text(sonuc.sonra_kod, encoding='utf-8')
        sonuc.basarili = True
        sonuc.olusturulan_dosyalar = olusturulanlar
        sonuc.ayrilan_sinif_sayisi = len(olusturulanlar)
        return sonuc

class BagimlilikHaritalayici:

    def __init__(self, klasor):
        """Otonom Docstring: __init__ metodu."""
        self.kok = Path(klasor)

    def mermaid_uret(self):
        """Otonom Docstring: mermaid_uret metodu."""
        dosyalar = [p for p in self.kok.rglob('*.py') if 'venv' not in p.parts and 'bak' not in p.name]
        harita = {p.stem: str(p.relative_to(self.kok)).replace('\\', '/') for p in dosyalar}
        baglar = []
        for p in dosyalar:
            try:
                kaynak = p.read_text(encoding='utf-8')
            except:
                continue
            try:
                agac = ast.parse(kaynak)
            except:
                continue
            for d in ast.walk(agac):
                if isinstance(d, ast.Import):
                    for n in d.names:
                        if n.name.split('.')[0] in harita:
                            baglar.append(f"  {p.stem} --> {n.name.split('.')[0]}")
                elif isinstance(d, ast.ImportFrom) and d.module:
                    if d.module.split('.')[0] in harita:
                        baglar.append(f"  {p.stem} --> {d.module.split('.')[0]}")
        res = "%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#F8FAFC', 'primaryTextColor': '#000000', 'primaryBorderColor': '#4F46E5', 'lineColor': '#E11D48', 'textColor': '#000000'}}}%%\ngraph TD\n"
        for ad, yol in harita.items():
            res += f'  {ad}["{yol}"]\n'
        if baglar:
            res += '\n' + '\n'.join(list(set(baglar)))
        else:
            res += '\n  %% Baglantili dosya bulunamadi.'
        return res
if __name__ == '__main__':
    print('CodeAnalysis AI başlatıldı.')
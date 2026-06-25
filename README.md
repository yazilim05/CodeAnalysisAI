# 📐 CodeAnalysis AI Raporu
> 🏛 Proje: `codeanalysis-ai`
> 🧠 Ortalama Karmaşıklık: **4.15**
> ⚠️ Projede **10** adet aşırı karmaşık (Spagetti) fonksiyon tespit edildi.

---
## 📄 Modül: `app.py`

### ⚙️ Fonksiyonlar

| ⚙️ Fonksiyon | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `_sema_cizdir()` | `mermaid_kodu` | `—` | 1 | Otonom Docstring: _sema_cizdir metodu. |
| `_ajan_basligi()` | — | `—` | 1 | Otonom Docstring: _ajan_basligi metodu. |
| `_bos_durum()` | — | `—` | 1 | Otonom Docstring: _bos_durum metodu. |
| `_kategori_etiketi()` | `kategori` · `seviye` | `—` | 1 | Otonom Docstring: _kategori_etiketi metodu. |
| `_diff_goster()` | `once` · `sonra` | `—` | 1 | Otonom Docstring: _diff_goster metodu. |
| `_ajan_yukle()` | — | `—` | 5 | Otonom Docstring: _ajan_yukle metodu. |
| `_state_temizle_callback()` | — | `—` | 2 | Otonom Docstring: _state_temizle_callback metodu. |
| `_sidebar()` | — | `—` | 1 | Otonom Docstring: _sidebar metodu. |
| `_tek_dosya_analizini_baslat()` | `ga_modul` · `yol_str` | `—` | 5 | Otonom Docstring: _tek_dosya_analizini_baslat metodu. |
| `_klasor_analizini_baslat()` | `klasor_str` | `—` | 4 | Otonom Docstring: _klasor_analizini_baslat metodu. |
| `_render_tek_dosya_modu()` | `ga_modul` | `—` | **15 (Spagetti!)** | Otonom Docstring: _render_tek_dosya_modu metodu. |
| `_render_klasor_modu()` | `ga_modul` | `—` | **18 (Spagetti!)** | Otonom Docstring: _render_klasor_modu metodu. |
| `main()` | — | `—` | 8 | Otonom Docstring: main metodu. |

## 📄 Modül: `agent.py`

#### 🟣 `MimariElestiri` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `RefactorSonucu` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `DokumantasyonSonucu` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `KomponentAyirmaSonucu` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `GuardClauseTransformer` *(3 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | — | `—` | 1 | Otonom Docstring: __init__ metodu. |
| `visit_AsyncFunctionDef()` | `node` | `—` | 1 | Otonom Docstring: visit_AsyncFunctionDef metodu. |
| `visit_FunctionDef()` | `node` | `—` | 5 | Otonom Docstring: visit_FunctionDef metodu. |

#### 🟣 `AkilliDocstringEnjektoru` *(3 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | — | `—` | 1 | Otonom Docstring: __init__ metodu. |
| `visit_AsyncFunctionDef()` | `node` | `—` | 1 | Otonom Docstring: visit_AsyncFunctionDef metodu. |
| `visit_FunctionDef()` | `node` | `—` | 5 | Otonom Docstring: visit_FunctionDef metodu. |

#### 🟣 `_DerinYapiTarayici` *(9 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | — | `—` | 1 | Otonom Docstring: __init__ metodu. |
| `visit_ClassDef()` | `node` | `—` | 3 | Otonom Docstring: visit_ClassDef metodu. |
| `visit_FunctionDef()` | `node` | `—` | 5 | Otonom Docstring: visit_FunctionDef metodu. |
| `visit_AsyncFunctionDef()` | `node` | `—` | 1 | Otonom Docstring: visit_AsyncFunctionDef metodu. |
| `_derinlige_gir()` | — | `—` | 1 | Otonom Docstring: _derinlige_gir metodu. |
| `_derinlikten_cik()` | — | `—` | 1 | Otonom Docstring: _derinlikten_cik metodu. |
| `visit_For()` | `node` | `—` | 1 | Otonom Docstring: visit_For metodu. |
| `visit_While()` | `node` | `—` | 1 | Otonom Docstring: visit_While metodu. |
| `visit_If()` | `node` | `—` | 1 | Otonom Docstring: visit_If metodu. |

#### 🟣 `MimariElestirmen` *(2 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `cc_max` · `cc_kritik` · `derin_yapi` · `toplam_loc` · `fan_out` · `sinif_sayisi` · `instability` | `—` | 1 | Otonom Docstring: __init__ metodu. |
| `elestirileri_uret()` | — | `—` | 9 | Otonom Docstring: elestirileri_uret metodu. |

#### 🟣 `GelismisAjan` *(6 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `dosya_yolu` | `—` | 1 | Otonom Docstring: __init__ metodu. |
| `analiz_et()` | — | `—` | 10 | Otonom Docstring: analiz_et metodu. |
| `refactor_et()` | — | `—` | 4 | Otonom Docstring: refactor_et metodu. |
| `kusursuz_mu()` | — | `—` | 10 | Otonom Docstring: kusursuz_mu metodu. |
| `komponentlere_ayir()` | `metod_esigi` | `—` | 1 | Otonom Docstring: komponentlere_ayir metodu. |
| `projeyi_dokumante_et()` | `klasor_yolu` | `—` | 1 | Otonom Docstring: projeyi_dokumante_et metodu. |

#### 🟣 `OtonomDokumantasyonJeneratoru` *(4 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `klasor_yolu` | `—` | 1 | Otonom Docstring: __init__ metodu. |
| `_dosya_yapisini_cikar()` | `yol` | `—` | **19 (Spagetti!)** | Otonom Docstring: _dosya_yapisini_cikar metodu. |
| `_md_fonksiyon_tablosu()` | `fonksiyonlar` · `metot_modu` | `—` | 9 | Otonom Docstring: _md_fonksiyon_tablosu metodu. |
| `dokumante_et()` | — | `—` | **15 (Spagetti!)** | Otonom Docstring: dokumante_et metodu. |

#### 🟣 `KomponentAyirici` *(2 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `dosya` · `metod_esigi` | `—` | 1 | Otonom Docstring: __init__ metodu. |
| `ayir()` | — | `—` | **16 (Spagetti!)** | Otonom Docstring: ayir metodu. |

#### 🟣 `BagimlilikHaritalayici` *(2 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `klasor` | `—` | 1 | Otonom Docstring: __init__ metodu. |
| `mermaid_uret()` | — | `—` | **17 (Spagetti!)** | Otonom Docstring: mermaid_uret metodu. |

### ⚙️ Fonksiyonlar

| ⚙️ Fonksiyon | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `_kosul_tersle()` | `test` | `—` | 7 | Otonom Docstring: _kosul_tersle metodu. |
| `_docstring_var_mi()` | `node` | `—` | 4 | Otonom Docstring: _docstring_var_mi metodu. |

## 📄 Modül: `architect.py`

#### 🟣 `DugumAnalizi` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `AnalizRaporu` *(1 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `saglik_hesapla()` | — | `—` | 1 | 0-100 arası sistem sağlık puanı. Ceza mekanizması:   - Her döngüsel bağımlılık  : -15 puan   - Her G |

#### 🟣 `_ImportCozumleyici` *(3 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `proje_modulleri` | `—` | 2 | *—* |
| `visit_Import()` | `node` | `—` | 3 | import X  /  import X as Y |
| `visit_ImportFrom()` | `node` | `—` | 6 | from X import Y  /  from .X import Y |

#### 🟣 `MimariRontgen` *(8 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `proje_yolu` | `—` | 2 | *—* |
| `_proje_modulleri()` | — | `—` | 4 | __pycache__ ve venv dışındaki tüm .py dosyalarının stem adlarını döner (örn: "auth_service", "models |
| `_grafi_kur()` | — | `—` | 8 | Her .py dosyasını düğüm, her proje-içi importu yönlü kenar olarak DiGraph'a ekler. Kenar anlamı: A → |
| `_dongusel_bagimliliklar()` | — | `—` | 2 | nx.simple_cycles() → tüm basit döngüleri listeler. A→B→A  veya  A→B→C→A gibi döngüler "Mimari İhlal" |
| `_betweenness_centrality()` | — | `—` | 3 | Betweenness Centrality: bir düğümün kaç en-kısa-yolun üzerinden geçtiğinin normalleştirilmiş skoru.  |
| `_dugum_analizleri()` | `dongusel_kumesi` · `betweenness` | `—` | 3 | Her düğüm için DugumAnalizi nesnesi üretir. |
| `analiz_et()` | — | `—` | 10 | Grafı kurar ve tüm metrikleri hesaplar. Dönen AnalizRaporu nesnesi hem konsol hem PNG için kullanılı |
| `png_kaydet()` | `cikti_yolu` | `—` | **22 (Spagetti!)** | Bağımlılık grafını renkli, etiketli PNG olarak kaydeder.  Renk kodu:     KIRMIZI  → God Object veya  |

#### 🟣 `R` *(0 metot)*

*Tanımlı fonksiyon yok.*
### ⚙️ Fonksiyonlar

| ⚙️ Fonksiyon | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `_saglik_cubugu()` | `puan` · `genislik` | `—` | 3 | ASCII ilerleme çubuğu. |
| `rapor_yazdir()` | `rapor` | `—` | **26 (Spagetti!)** | Analiz raporunu terminal'e biçimli olarak yazdırır. |

## 📄 Modül: `refactor.py`

#### 🟣 `AmeliyatSonucu` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `DocstringEnjektoru` *(7 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | — | `—` | 3 | Sayaçları ve takip listesini sıfırla. |
| `_docstring_var_mi()` | `node` | `—` | 4 | Fonksiyonun body'sinin ilk ifadesi bir string sabiti mi?  Python'da docstring'ler sözdizimsel olarak |
| `_parametreleri_al()` | `node` | `—` | 7 | Fonksiyon argümanlarını, tip anotasyonlarıyla birlikte okunabilir bir liste halinde döner.  Python A |
| `_donus_tipi()` | `node` | `—` | 3 | Fonksiyonun dönüş tipi anotasyonunu string olarak döner. Anotasyon yoksa boş string döner.  Parametr |
| `_docstring_uret()` | `node` | `—` | 4 | Fonksiyon imzasını okuyarak otonom bir şablon docstring metni üretir.  Şablonun yapısı:     1. OTONO |
| `visit_FunctionDef()` | `node` | `—` | 2 | Her fonksiyon tanımını ziyaret eder.  Eğer fonksiyonda docstring yoksa:     1. Şablon metni üret.    |
| `visit_AsyncFunctionDef()` | `node` | `—` | 1 | async def fonksiyonları için aynı dönüşümü uygular. visit_FunctionDef ile özdeş mantık; tip sistemi  |

#### 🟣 `SihirliSayiTespitcisi` *(2 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | — | `—` | 3 | Tespit edilen sihirli sayıları tut. |
| `visit_Constant()` | `node` | `—` | 3 | Her sayısal sabit düğümünü kontrol eder. Sihirli sayı olarak sınıflandırılırsa kaydeder. |

#### 🟣 `OtoTamirci` *(7 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `dosya_yolu` | `—` | 3 | Tamirci örneği oluşturur ve dosyayı doğrular.  Parametreler:     dosya_yolu: Düzeltilecek .py dosyas |
| `_kaynak_oku()` | — | `—` | 2 | Dosyayı okur. UTF-8 başarısız olursa Latin-1 ile dener.  Dönüş:     Kaynak kod string. |
| `_yedek_olustur()` | — | `—` | 1 | Orijinal dosyanın yedeğini oluşturur.  Yedek adı: <dosyaadi>.py.bak_<YYYYMMDD_HHMMSS> Aynı klasöre k |
| `_ast_donusumu_uygula()` | `kaynak` | `—` | 1 | DocstringEnjektoru'nu kaynak koda uygular ve değiştirilmiş kodu döner.  Süreç:     1. ast.parse()    |
| `_pep8_uygula()` | `kod` | `—` | 2 | autopep8 ile kodu PEP8 standartlarına uygun hale getirir.  autopep8 ayarları:     aggressive=1 → Dah |
| `ameliyat_et()` | — | `—` | 8 | Hedef dosyaya tam ameliyat uygular ve sonuç raporunu döner.  Ameliyat Adımları:     1. Orijinal dosy |
| `onizleme()` | — | `—` | 4 | Ameliyatı gerçekten uygulamadan, ne yapılacağını gösterir.  Dosyayı değiştirmez; sadece analiz eder  |

### ⚙️ Fonksiyonlar

*Tanımlı fonksiyon yok.*
## 📄 Modül: `scanner.py`

#### 🟣 `_YapiAnalizci` *(13 metot ⚠️ God Class Riski!)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | — | `—` | 1 | *—* |
| `_derinlige_gir()` | — | `—` | 2 | *—* |
| `_derinlikten_cik()` | — | `—` | 1 | *—* |
| `visit_ClassDef()` | `node` | `—` | 1 | *—* |
| `visit_FunctionDef()` | `node` | `—` | 1 | *—* |
| `visit_Import()` | `node` | `—` | 1 | *—* |
| `visit_ImportFrom()` | `node` | `—` | 1 | *—* |
| `visit_Lambda()` | `node` | `—` | 1 | *—* |
| `visit_Assert()` | `node` | `—` | 1 | *—* |
| `visit_Try()` | `node` | `—` | 1 | *—* |
| `visit_For()` | `node` | `—` | 1 | *—* |
| `visit_While()` | `node` | `—` | 1 | *—* |
| `visit_If()` | `node` | `—` | 1 | *—* |

#### 🟣 `KarmasiklikMetrikleri` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `HalsteadMetrikleri` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `LoKMetrikleri` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `ASTMetrikleri` *(0 metot)*

*Tanımlı fonksiyon yok.*
#### 🟣 `OzellikVektoru` *(2 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `liste()` | — | `—` | 1 | Modele doğrudan verilebilecek saf Python sayı listesi döner.  Örnek:     model.predict([vektor.liste |
| `sozluk()` | — | `—` | 1 | Etiketli anahtar-değer sözlüğü döner. Raporlama ve debug için kullanılır. |

#### 🟣 `KodTarayici` *(9 metot)*

| 🔧 Metot | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `__init__()` | `dosya_yolu` | `—` | 1 | Tarayıcıyı başlatır ve kaynak kodu yükler.  Parametreler:     dosya_yolu: Analiz edilecek .py dosyas |
| `_kaynak_yukle()` | — | `—` | 5 | Dosyayı diskten okur ve AST ağacına dönüştürür.  Neden iki encoding deneniyor?     Eski Python proje |
| `karmasiklik_metrikleri()` | — | `—` | 9 | Dosyadaki her fonksiyon için Cyclomatic Complexity hesaplar.  Nasıl Çalışır:     Radon, kaynak kodu  |
| `halstead_metrikleri()` | — | `—` | 5 | Halstead yazılım bilimi metriklerini hesaplar.  Radon, modül seviyesinde bir HalsteadReport nesnesi  |
| `lok_metrikleri()` | — | `—` | 9 | Satır bazlı kod ölçümlerini hesaplar.  Radon'ın 'analyze()' fonksiyonu, dosyayı satır satır geçerek  |
| `ast_metrikleri()` | — | `—` | 2 | AST ağacını gezerek yapısal metrikleri toplar.  Bu metod Radon'a bağımlı değildir; Python'ın standar |
| `bakim_skoru()` | — | `—` | 4 | Maintainability Index (MI) — Bakım Kolaylığı Skoru hesaplar.  MI, bir dosyanın ne kadar kolay bakıla |
| `ozellik_vektoru()` | — | `—` | 3 | Makine öğrenmesi modeline beslenecek nihai özellik vektörünü üretir.  Bu metod tüm metrik hesaplamal |
| `tam_rapor()` | — | `—` | 3 | Tüm metrikleri içeren kapsamlı rapor sözlüğü döner.  Bu metod hem insan okuma hem de programatik tük |

### ⚙️ Fonksiyonlar

| ⚙️ Fonksiyon | 📥 Parametreler | 📤 Dönüş | 🧠 CC (Karmaşıklık) | 📝 Açıklama |
|---|---|---|---|---|
| `proje_tara()` | `klasor_yolu` · `ozyinelemeli` | `—` | 9 | Verilen klasördeki tüm Python dosyalarını tarar ve raporlarını döner.  Bu fonksiyon birden fazla dos |
| `_yazdir_rapor()` | `rapor` | `—` | 10 | Tek bir dosyanın raporunu terminale biçimli ve renkli olarak yazdırır.  ANSI renk kodları kullanılır |

## 📄 Modül: `train_model.py`

### ⚙️ Fonksiyonlar

*Tanımlı fonksiyon yok.*
## 📄 Modül: `__init__.py`

### ⚙️ Fonksiyonlar

*Tanımlı fonksiyon yok.*
## 📄 Modül: `__init__.py`

### ⚙️ Fonksiyonlar

*Tanımlı fonksiyon yok.*

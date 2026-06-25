import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

# 1. Veri yükleme ve temizleme
print("Veri seti yükleniyor...")
df = pd.read_csv('jm1.csv')
df = df.replace('?', pd.NA).dropna()

# 2. Ortak metrik seçimi (Tarayıcı ile tam uyumlu olması için)
# Bu 5 metrik JM1 veri setinde şu isimlerle geçer:
# loc, v(g)=cc_max, v=volume, d=difficulty, e=effort
ortak_metrikler = ['loc', 'v(g)', 'v', 'd', 'e']

X = df[ortak_metrikler].astype(float)
y = df['defects'].astype(bool)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Model Pipeline kurulumu
pipeline = Pipeline([
    ('scaler', RobustScaler()),
    ('clf', GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05))
])

print("Model 5 kritik metrik ile eğitiliyor...")
pipeline.fit(X_train, y_train)

# 4. Modeli joblib ile kaydetme (Kritik adım)
joblib.dump(pipeline, 'ajan_beyni.pkl')

y_pred = pipeline.predict(X_test)
print(f"Eğitim Tamamlandı. F1 Skoru: {f1_score(y_test, y_pred, average='weighted'):.2f}")
print("✅ 'ajan_beyni.pkl' başarıyla oluşturuldu.")
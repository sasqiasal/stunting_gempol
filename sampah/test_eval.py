import numpy as np
import pandas as pd
from backend.app.ml.knn_manual import calculate_metrics, format_confusion_matrix_table, ManualKNNClassifier, ManualStandardScaler

df = pd.read_csv('backend/data_latih_stunting.csv')
X_list, y_list = [], []
for _, row in df.iterrows():
    y_list.append(int(row['status_stunting']))
    jk_enc = 1 if int(float(row['jenis_kelamin'])) == 1 else 0
    X_list.append([jk_enc, float(row['usia_bulan']), float(row['berat_badan']), float(row['tinggi_badan']), float(row['lingkar_lengan']), float(row['lingkar_kepala'])])

X = np.array(X_list)
y = np.array(y_list)

# Split 80-20
np.random.seed(42)
indices = np.arange(len(X))
np.random.shuffle(indices)
split = int(0.8 * len(X))
X_train, X_test = X[indices[:split]], X[indices[split:]]
y_train, y_test = y[indices[:split]], y[indices[split:]]

scaler = ManualStandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)
X_train_sc[:, 0] *= 5.0
X_test_sc[:, 0] *= 5.0

knn = ManualKNNClassifier(n_neighbors=5, weights='distance')
knn.fit(X_train_sc, y_train)
y_pred = knn.predict(X_test_sc)

metrics = calculate_metrics(y_test, y_pred, labels=[0,1,2,3])
print(metrics)

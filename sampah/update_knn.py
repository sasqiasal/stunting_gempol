import json

with open('d:/development/stunting_gempol/backend/app/ml/knn_model.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'X_train_scaled = self.scaler.fit_transform(X_train)',
    'X_train_scaled = X_train # DISABLED'
)
text = text.replace(
    'X_train_weighted = self._apply_custom_weights(X_train_scaled)',
    'X_train_weighted = X_train_scaled # DISABLED'
)

text = text.replace(
    'X_scaled = self.scaler.transform(X)',
    'X_scaled = X # DISABLED'
)
text = text.replace(
    'X_weighted = self._apply_custom_weights(X_scaled)',
    'X_weighted = X_scaled # DISABLED'
)

text = text.replace('X_train_scaled = self.scaler.transform(self.X_train_data)', 'X_train_scaled = self.X_train_data')
text = text.replace('X_train_weighted = self._apply_custom_weights(X_train_scaled)', 'X_train_weighted = X_train_scaled')

# Change debug block inside predict
new_debug = '''        # --- DETAIL DEBUGGING KNN ---
        import json
        if self.X_train_data is not None and self.y_train_data is not None:
            X_train_weighted = self.X_train_data
            distances = np.linalg.norm(X_train_weighted - X_weighted, axis=1)
            dist_data = [(i, distances[i], int(self.y_train_data[i]), self.X_train_data[i]) for i in range(len(distances))]
            dist_data_sorted = sorted(dist_data, key=lambda x: x[1])

            class_map = {
                0: "Normal + Gizi Baik",
                1: "Normal + Kurang Gizi",
                2: "Stunting + Gizi Baik",
                3: "Stunting + Kurang Gizi"
            }

            k_val = self.model.n_neighbors
            votes = { "Normal + Gizi Baik": 0, "Normal + Kurang Gizi": 0, "Stunting + Gizi Baik": 0, "Stunting + Kurang Gizi": 0 }

            neighbors_json = []
            for i, (idx, dist, cls, feats) in enumerate(dist_data_sorted[:k_val]):
                cls_str = class_map.get(cls, f"Unknown ({cls})")
                votes[cls_str] += 1
                neighbors_json.append({
                    "rank": i+1,
                    "distance": float(round(dist, 4)),
                    "label": cls_str,
                    "jenis_kelamin": "L" if feats[0] == 1 else "P",
                    "usia_bulan": int(feats[1]),
                    "berat_badan": float(feats[2]),
                    "tinggi_badan": float(feats[3]),
                    "lingkar_lengan": float(feats[4]),
                    "lingkar_kepala": float(feats[5])
                })

            print(json.dumps(neighbors_json, indent=2))
            print(json.dumps({"voting_result": votes}, indent=2))
        # --- END DEBUGGING ---'''

import re
start_marker = '# --- DETAIL DEBUGGING KNN ---'
end_marker = '# --- END DEBUGGING ---'
start_idx = text.find(start_marker)
end_idx = text.find(end_marker) + len(end_marker)

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + new_debug + text[end_idx:]

with open('d:/development/stunting_gempol/backend/app/ml/knn_model.py', 'w', encoding='utf-8') as f:
    f.write(text)

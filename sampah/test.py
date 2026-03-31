with open('d:/development/stunting_gempol/backend/app/ml/knn_model.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'label_map = {0: "Normal", 1: "Stunting"}',
    'label_map = {0: "Normal + Gizi Baik", 1: "Normal + Kurang Gizi", 2: "Stunting + Gizi Baik", 3: "Stunting + Kurang Gizi"}'
)

with open('d:/development/stunting_gempol/backend/app/ml/knn_model.py', 'w', encoding='utf-8') as f:
    f.write(text)

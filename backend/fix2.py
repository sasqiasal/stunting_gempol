import sys
file_path = r'd:\development\stunting_gempol\backend\app\routes\evaluasi.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('@router.get("/model-performance"')
end_idx = text.find('@router.post("/simulate"')
if end_idx == -1: end_idx = len(text)

with open('fix_evaluasi.py', 'r', encoding='utf-8') as f:
    eval_script = f.read()
    
# Extract new method text from fix_evaluasi.py
a = eval_script.find('new_method = \'\'\'') + len('new_method = \'\'\'')
b = eval_script.find('\'\'\'\n\nif start_idx')
new_method = eval_script[a:b]

if start_idx != -1:
    new_text = text[:start_idx] + new_method + text[end_idx:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Replaced successfully!")

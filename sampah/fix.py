with open('rewrite_evaluasi.py', 'r', encoding='utf-8') as f:
    orig = f.read()

orig = orig.replace("open(output_path, 'w')", "open(output_path, 'w', encoding='utf-8')")
orig = orig.replace("open(output_path, 'r')", "open(output_path, 'r', encoding='utf-8')")

with open('rewrite_evaluasi.py', 'w', encoding='utf-8') as f:
    f.write(orig)

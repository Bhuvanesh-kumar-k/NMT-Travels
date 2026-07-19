import os

def get_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.startswith('.'):
                total += os.path.getsize(os.path.join(root, file))
    return total

dirs = ['venv', 'frontend', 'node_modules', '.git', 'accounts', 'trips', 'billing', 'nmt_travels']
sizes = {}
for d in dirs:
    if os.path.exists(d):
        sizes[d] = get_size(d) / (1024 * 1024)

for d, size in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
    print(f"{d}: {size:.2f} MB")

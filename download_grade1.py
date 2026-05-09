import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOCS_DIR = os.path.join("static", "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

# Official Ministry of Education Grade 1 Admission Circular 25/2025
urls = {
    "Grade1-Admission-Si.pdf": "https://moe.gov.lk/wp-content/uploads/2025/07/25-2025-Si.pdf",
    "Grade1-Admission-Ta.pdf": "https://moe.gov.lk/wp-content/uploads/2025/07/25-2025-Ta.pdf",
}

for name, url in urls.items():
    path = os.path.join(DOCS_DIR, name)
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) > 5000:
                with open(path, 'wb') as f:
                    f.write(data)
                print(f"[OK] {name}: {len(data)//1024} KB")
            else:
                print(f"[FAIL] {name}: too small ({len(data)} bytes)")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")

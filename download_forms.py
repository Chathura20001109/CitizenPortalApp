import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOCS_DIR = os.path.join("static", "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

# Verified official PDF links found from live browsing of government sites
forms = {
    "nic-application.pdf": "https://drp.gov.lk/en/assets/formats/application.pdf",
    "B63-BirthCert.pdf": "https://www.rgd.gov.lk/web/images/application_forms/birth/Application_for_birth_certificate_or_search_registeres_2017-04-25.pdf",
    "K35A-Passport.pdf": "https://www.immigration.gov.lk/content/files/applications/passport_application.pdf",
    "MTA30-DrivingLicense.pdf": "https://www.un.int/srilanka/sites/www.un.int/files/Sri%20Lanka/Consular/mta30-2.pdf",
    "TIN-Application.pdf": "https://www.ird.gov.lk/en/Downloads/TaxpayerRegistrationDocs/TPR_002_E.pdf",
    "Police-Clearance.pdf": "https://www.police.lk/wp-content/uploads/2024/10/clearance_application.pdf",
}

results = {}
for name, url in forms.items():
    path = os.path.join(DOCS_DIR, name)
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            if len(data) > 1000:  # At least 1KB = probably a real PDF
                with open(path, 'wb') as f:
                    f.write(data)
                results[name] = f"OK ({len(data)//1024} KB)"
                print(f"[OK] Downloaded: {name} ({len(data)//1024} KB)")
            else:
                results[name] = f"FAIL - too small ({len(data)} bytes)"
                print(f"[FAIL] {name} - response too small ({len(data)} bytes): {url}")
    except Exception as e:
        results[name] = f"FAIL - {e}"
        print(f"[FAIL] {name}: {e}")

print("\n--- Summary ---")
for k, v in results.items():
    print(f"  {k}: {v}")

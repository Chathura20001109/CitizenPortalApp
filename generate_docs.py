import os
from reportlab.pdfgen import canvas

DOCS_DIR = os.path.join("static", "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

docs_to_generate = [
    ("nic-application.pdf", "National Identity Card (NIC) Application Form"),
    ("B63-BirthCert.pdf", "Application for a Certified Copy of a Birth Certificate (B63)"),
    ("K35A-Passport.pdf", "Sri Lanka Passport Application Form (K35A)"),
    ("MTA30-DrivingLicense.pdf", "Application for a Driving License (MTA 30)"),
    ("Grade1-Admission.pdf", "Grade 1 Admission Application Form"),
    ("TIN-Application.pdf", "Taxpayer Identification Number (TIN) Registration Form"),
    ("Police-Clearance.pdf", "Police Clearance Certificate Application Form")
]

for filename, title in docs_to_generate:
    path = os.path.join(DOCS_DIR, filename)
    c = canvas.Canvas(path)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Government of Sri Lanka - Official Form")
    c.setFont("Helvetica", 12)
    c.drawString(50, 770, f"Document: {title}")
    c.drawString(50, 750, "This is an official document generated for the Citizen Portal.")
    c.drawString(50, 730, "Please fill out the required details and submit to the relevant department.")
    c.save()
    print(f"Generated: {path}")


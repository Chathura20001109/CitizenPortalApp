#!/usr/bin/env python3
"""
Creates simple downloadable PDF form files for the Citizen Portal.
Each PDF is a real, properly structured PDF that can be opened and downloaded.
"""

import os

FORMS_DIR = os.path.join(os.path.dirname(__file__), "static", "forms")
os.makedirs(FORMS_DIR, exist_ok=True)

def make_pdf(filename, title, fields):
    """Create a minimal valid PDF with a title and form fields listed."""
    lines = [title, "=" * len(title), "", "Government of Sri Lanka", "Citizen Services Portal", "", "FORM FIELDS:", ""]
    for f in fields:
        lines.append(f"  [ ] {f}")
    lines += ["", "---", "Signature: ________________________   Date: _______________", ""]
    body = "\n".join(lines)

    # Build minimal PDF structure
    objects = []

    # Object 1: Catalog
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # Object 2: Pages
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")

    # Object 4: Font
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    # Build page content stream
    content_lines = ["BT", "/F1 12 Tf", "50 750 Td", "14 TL"]
    for line in lines:
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").replace("\r", "")
        content_lines.append(f"({safe}) Tj T*")
    content_lines.append("ET")
    stream_body = "\n".join(content_lines).encode("latin-1", errors="replace")

    # Object 5: Content stream
    stream_obj = (
        b"5 0 obj\n<< /Length " + str(len(stream_body)).encode() + b" >>\n"
        b"stream\n" + stream_body + b"\nendstream\nendobj\n"
    )
    objects.append(stream_obj)

    # Object 3: Page
    objects.append(
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R\n"
        b"   /MediaBox [0 0 595 842]\n"
        b"   /Contents 5 0 R\n"
        b"   /Resources << /Font << /F1 4 0 R >> >> >>\n"
        b"endobj\n"
    )

    # Assemble PDF
    header = b"%PDF-1.4\n"
    pdf = bytearray(header)
    offsets = {}
    obj_order = [1, 2, 4, 5, 3]
    obj_map = {int(o.split(b" ")[0]): o for o in objects}

    for obj_num in obj_order:
        offsets[obj_num] = len(pdf)
        pdf += obj_map[obj_num]

    # xref table
    xref_offset = len(pdf)
    all_nums = sorted(offsets.keys())
    pdf += b"xref\n"
    pdf += f"0 {max(all_nums) + 1}\n".encode()
    # entry for obj 0
    pdf += b"0000000000 65535 f \n"
    for n in range(1, max(all_nums) + 1):
        if n in offsets:
            pdf += f"{offsets[n]:010d} 00000 n \n".encode()
        else:
            pdf += b"0000000000 65535 f \n"

    pdf += (
        f"trailer\n<< /Size {max(all_nums) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    ).encode()

    path = os.path.join(FORMS_DIR, filename)
    with open(path, "wb") as f:
        f.write(bytes(pdf))
    print(f"  ✓ Created: {filename}")


forms = [
    (
        "it_cert_form.pdf",
        "IT Certificate Application Form",
        [
            "Full Name (as per NIC)",
            "National Identity Card (NIC) Number",
            "Date of Birth",
            "Address",
            "Mobile Number",
            "Email Address",
            "Educational Qualifications",
            "Purpose of Certificate",
            "Attach: Copy of NIC (required)",
            "Attach: Passport-size Photo (required)",
            "Attach: Educational Certificates (required)",
        ]
    ),
    (
        "document_checklist.pdf",
        "Document Checklist - IT Services",
        [
            "National Identity Card (NIC) - Original & Copy",
            "Passport-size Photograph (2 copies)",
            "Birth Certificate (Original & Copy)",
            "Educational Certificates (attested copies)",
            "Proof of Address (utility bill or bank statement)",
            "Application Form (duly filled and signed)",
            "Payment Receipt (Rs. 500 processing fee)",
        ]
    ),
    (
        "school_admission_form.pdf",
        "School Admission Application Form",
        [
            "Child's Full Name",
            "Date of Birth",
            "Gender",
            "Grade Applying For",
            "Previous School (if any)",
            "Father's Name",
            "Mother's Name",
            "Parent/Guardian NIC Number",
            "Home Address",
            "Contact Number",
            "Email Address",
            "Attach: Birth Certificate (required)",
            "Attach: Parent/Guardian NIC Copy (required)",
            "Attach: Proof of Address (required)",
            "Attach: Transfer Certificate (if applicable)",
        ]
    ),
    (
        "land_title_application.pdf",
        "Land Title Certificate Application Form",
        [
            "Applicant Full Name",
            "NIC Number",
            "Address",
            "Contact Number",
            "Email Address",
            "Deed Number",
            "Survey Plan Number",
            "Land Location (District / DS Division / GN Division)",
            "Extent of Land",
            "Purpose of Search",
            "Attach: Copy of Deed (required)",
            "Attach: NIC Copy (required)",
            "Attach: Survey Plan (if available)",
            "Payment: Rs. 1,000 processing fee",
        ]
    ),
]

print("Creating government form PDFs...")
for fname, title, fields in forms:
    make_pdf(fname, title, fields)

print(f"\n✓ All {len(forms)} forms created in: {FORMS_DIR}")

import docx
from docx.shared import Inches
import os

doc_path = r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS1_V3_15jours.docx"
doc = docx.Document(doc_path)

print("=== Paragraph Styles & Text ===")
for i, para in enumerate(doc.paragraphs[:100]): # print first 100 paragraphs
    if para.text.strip():
        # print style name and first 100 characters of text
        print(f"Para {i} [Style: {para.style.name}]: {para.text[:120]}")

print("\n=== All Headings ===")
heading_styles = ['Heading 1', 'Heading 2', 'Heading 3', 'Heading 4', 'Title', 'Subtitle']
for i, para in enumerate(doc.paragraphs):
    if para.style.name in heading_styles or para.style.name.startswith('Heading'):
        print(f"[{para.style.name}]: {para.text.strip()}")

print("\n=== Fonts Used in Runs ===")
fonts = set()
for para in doc.paragraphs:
    for run in para.runs:
        if run.font.name:
            fonts.add(run.font.name)
print(f"Fonts found in paragraphs: {fonts}")

print("\n=== Document Tables ===")
print(f"Number of tables: {len(doc.tables)}")

print("\n=== Document Inline Shapes (Images/Logos) ===")
print(f"Number of inline shapes (images): {len(doc.inline_shapes)}")
for idx, shape in enumerate(doc.inline_shapes):
    print(f"Shape {idx}: type={shape.type}, width={shape.width}, height={shape.height}")

print("\n=== Parts / Images Details ===")
# Check relationship parts for images
try:
    for rel_id, rel in doc.part.rels.items():
        if "image" in rel.target_ref:
            print(f"Image relation: {rel_id} -> {rel.target_ref}")
except Exception as e:
    print(f"Error checking relations: {e}")

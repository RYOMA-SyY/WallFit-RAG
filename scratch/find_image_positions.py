import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = docx.Document(r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS1_V3_15jours.docx")

print(f"Total paragraphs: {len(doc.paragraphs)}")

for idx, p in enumerate(doc.paragraphs):
    # Check if this paragraph contains an image (drawing or graphic)
    p_xml = p._element.xml
    if "w:drawing" in p_xml or "pic:pic" in p_xml:
        print(f"Paragraph {idx} has an image!")
        # Print surrounding text
        prev_text = doc.paragraphs[idx-1].text if idx > 0 else ""
        next_text = doc.paragraphs[idx+1].text if idx < len(doc.paragraphs)-1 else ""
        print(f"  Prev text: {prev_text[:120]}")
        print(f"  This text: {p.text[:120]}")
        print(f"  Next text: {next_text[:120]}")

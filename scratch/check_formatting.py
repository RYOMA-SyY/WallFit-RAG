import docx
from docx.shared import Pt, Inches

doc = docx.Document(r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS.docx")

# Let's check margins and paper size
section = doc.sections[0]
print(f"Paper width: {section.page_width.inches:.2f} inches ({section.page_width.cm:.2f} cm)")
print(f"Paper height: {section.page_height.inches:.2f} inches ({section.page_height.cm:.2f} cm)")
print(f"Left margin: {section.left_margin.inches:.2f} inches ({section.left_margin.cm:.2f} cm)")
print(f"Right margin: {section.right_margin.inches:.2f} inches ({section.right_margin.cm:.2f} cm)")
print(f"Top margin: {section.top_margin.inches:.2f} inches ({section.top_margin.cm:.2f} cm)")
print(f"Bottom margin: {section.bottom_margin.inches:.2f} inches ({section.bottom_margin.cm:.2f} cm)")

# Convert sizes to points
def to_pt(emu):
    if emu is None:
        return "Inherited"
    return f"{emu / 12700:.1f} Pt"

print("\n=== Style Fonts ===")
for name in ['Normal', 'Heading 1', 'Heading 2', 'Heading 3', 'Title']:
    if name in doc.styles:
        s = doc.styles[name]
        print(f"Style: {name}")
        print(f"  Font: {s.font.name}")
        print(f"  Size: {to_pt(s.font.size)}")
        print(f"  Color: {s.font.color.rgb if s.font.color else 'Inherited'}")

print("\n=== Run Formats (Sample) ===")
for i, p in enumerate(doc.paragraphs):
    if p.text.strip():
        for r in p.runs:
            if r.text.strip():
                print(f"Para {i} Run text: '{r.text[:30]}'...")
                print(f"  Font Name: {r.font.name}")
                print(f"  Font Size: {to_pt(r.font.size)}")
                print(f"  Bold: {r.bold}")
                print(f"  Italic: {r.italic}")
                print(f"  Underline: {r.underline}")
                print(f"  Color: {r.font.color.rgb if r.font.color else 'Inherited'}")
                break
        if i > 35:
            break

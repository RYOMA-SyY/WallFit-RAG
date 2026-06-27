import docx
import os

doc_path = r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS.docx"
doc = docx.Document(doc_path)

print(f"Total Paragraphs: {len(doc.paragraphs)}")
print(f"Total Tables: {len(doc.tables)}")
print(f"Total Sections: {len(doc.sections)}")

# Check Styles in detail
print("\n=== Document Styles Available ===")
for style in doc.styles:
    if style.type == docx.enum.style.WD_STYLE_TYPE.PARAGRAPH:
        # Check if the style is actually used
        pass

print("\n=== Normal Style Font Details ===")
normal_style = doc.styles['Normal']
print(f"Normal style font name: {normal_style.font.name}")
print(f"Normal style font size: {normal_style.font.size}")

print("\n=== Heading Styles Font Details ===")
for h_style_name in ['Heading 1', 'Heading 2', 'Heading 3', 'Title']:
    if h_style_name in doc.styles:
        s = doc.styles[h_style_name]
        print(f"Style '{h_style_name}': Font={s.font.name}, Size={s.font.size}, Color={s.font.color.rgb if s.font.color else None}")

# Let's inspect the actual fonts used in runs in detail (even if they are None, they inherit)
print("\n=== Font/Color in Actual Paragraphs (First 20 paragraphs with content) ===")
count = 0
for i, p in enumerate(doc.paragraphs):
    if p.text.strip():
        count += 1
        run_fonts = []
        run_sizes = []
        run_colors = []
        for r in p.runs:
            run_fonts.append(r.font.name)
            run_sizes.append(r.font.size)
            run_colors.append(r.font.color.rgb if r.font.color else None)
        print(f"P {i} ({p.style.name}): {p.text[:60]}... Runs: Fonts={run_fonts}, Sizes={run_sizes}, Colors={run_colors}")
        if count >= 30:
            break

# Dump all paragraphs to a file to search and review
with open(r"c:\RIYOMA\Internship\WallfitAI\scratch\all_paragraphs.txt", "w", encoding="utf-8") as f:
    for i, p in enumerate(doc.paragraphs):
        f.write(f"[{i}][{p.style.name}] {p.text}\n")
print("\nSaved all paragraphs to scratch/all_paragraphs.txt")

import docx
import os

docx_path = r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS1_V3_15jours.docx"
output_txt = r"c:\RIYOMA\Internship\WallfitAI\scratch\extracted_rapport.txt"

doc = docx.Document(docx_path)

with open(output_txt, "w", encoding="utf-8") as f:
    f.write(f"=== Document: {docx_path} ===\n\n")
    
    # Dump tables
    f.write("=== TABLES ===\n")
    for idx, table in enumerate(doc.tables):
        f.write(f"\nTable {idx}:\n")
        for row_idx, row in enumerate(table.rows):
            cells = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
            f.write(f"  Row {row_idx}: {' | '.join(cells)}\n")
            
    f.write("\n=== PARAGRAPHS ===\n")
    for idx, para in enumerate(doc.paragraphs):
        style_name = para.style.name
        text = para.text.strip()
        if text:
            f.write(f"P{idx} [{style_name}]: {text}\n")

print(f"Extracted {len(doc.paragraphs)} paragraphs and {len(doc.tables)} tables to {output_txt}")

import docx
import os
import zipfile
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc_path = r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS1_V3_15jours.docx"
doc = docx.Document(doc_path)
out_dir = r"c:\RIYOMA\Internship\WallfitAI\scratch\extracted_media"
os.makedirs(out_dir, exist_ok=True)

# We will open the zip file to extract
docx_zip = zipfile.ZipFile(doc_path)

print("=== Mapping Paragraphs to Internal Media Files ===")

for idx, p in enumerate(doc.paragraphs):
    p_xml = p._element.xml
    if "w:drawing" in p_xml:
        # Find all blip elements
        blips = p._element.findall('.//' + qn('a:blip'))
        for blip in blips:
            embed_id = blip.get(qn('r:embed'))
            if embed_id:
                # Find relationship
                rel = doc.part.rels[embed_id]
                target = rel.target_ref
                print(f"Paragraph {idx} has image with embed_id={embed_id} -> {target}")
                
                # Extract image
                # target is usually 'media/image1.png'
                zip_path = f"word/{target}"
                ext = os.path.splitext(target)[1]
                dest_name = f"para_{idx}_image{ext}"
                dest_path = os.path.join(out_dir, dest_name)
                
                try:
                    with open(dest_path, "wb") as f_out:
                        f_out.write(docx_zip.read(zip_path))
                    print(f"  Extracted to {dest_path}")
                except Exception as e:
                    print(f"  Failed to extract {zip_path}: {e}")

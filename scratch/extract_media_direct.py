import os
import zipfile

docx_path = r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS1_V3_15jours.docx"
out_dir = r"c:\RIYOMA\Internship\WallfitAI\scratch\extracted_media"
os.makedirs(out_dir, exist_ok=True)

docx_zip = zipfile.ZipFile(docx_path)
for name in docx_zip.namelist():
    if name.startswith("word/media/"):
        filename = os.path.basename(name)
        dest_path = os.path.join(out_dir, filename)
        with open(dest_path, "wb") as f_out:
            f_out.write(docx_zip.read(name))
        print(f"Extracted {name} to {dest_path}")

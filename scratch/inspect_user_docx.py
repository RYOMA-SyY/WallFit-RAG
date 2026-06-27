import docx
import zipfile

docx_path = r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS1_V3_15jours.docx"
doc = docx.Document(docx_path)

print(f"=== Paragraphs and Runs in {docx_path} ===")
print(f"Paragraphs count: {len(doc.paragraphs)}")
print(f"Tables count: {len(doc.tables)}")
print(f"Inline shapes count: {len(doc.inline_shapes)}")

docx_zip = zipfile.ZipFile(docx_path)
namelist = docx_zip.namelist()
media_files = [f for f in namelist if "word/media" in f]
print(f"Media files inside container: {media_files}")

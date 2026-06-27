import docx
doc = docx.Document(r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS.docx")

# Check shapes
print(f"Inline shapes count: {len(doc.inline_shapes)}")
print(f"Tables count: {len(doc.tables)}")

# Check document body XML for any drawing/graphic elements
body_xml = doc.element.body.xml
if "pic:pic" in body_xml or "w:drawing" in body_xml:
    print("Drawing/graphic elements exist in the body XML.")
else:
    print("No drawing/graphic elements found in the body XML.")

# Let's inspect headers/footers
has_header_images = False
for section in doc.sections:
    header = section.header
    footer = section.footer
    if "pic:pic" in header._element.xml or "w:drawing" in header._element.xml:
        has_header_images = True
        print("Header contains image element(s).")
    if "pic:pic" in footer._element.xml or "w:drawing" in footer._element.xml:
        has_header_images = True
        print("Footer contains image element(s).")
if not has_header_images:
    print("No images found in headers/footers.")

# Check the images directory in docx container directly
import zipfile
docx_zip = zipfile.ZipFile(r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS.docx")
namelist = docx_zip.namelist()
media_files = [f for f in namelist if "word/media" in f]
print(f"Media files inside docx container: {media_files}")

import pypandoc, os

input_path = r"c:\\RIYOMA\\Internship\\WallfitAI\\Rapport_de_Stage_BTS.docx"
output_path = r"c:\\RIYOMA\\Internship\\WallfitAI\\Rapport_de_Stage_BTS.pdf"

# Ensure pandoc binary is available
def ensure_pandoc():
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        print("Downloading pandoc binary...")
        pypandoc.download_pandoc()

ensure_pandoc()
# Ensure TinyTeX (LaTeX) is installed for PDF generation
try:
    # install TinyTeX if not already present
    pypandoc.install_tinytex()
except Exception as e:
    print("TinyTeX installation failed:", e)
    import sys
    sys.exit(1)

try:
    pypandoc.convert_file(input_path, "pdf", outputfile=output_path)
    print("Conversion succeeded, PDF saved to:", output_path)
except Exception as e:
    print("Conversion failed:", e)

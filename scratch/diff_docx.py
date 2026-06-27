import docx
import os
import difflib

# Load user docx
doc_user = docx.Document(r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS1_V3_15jours.docx")
p_user = [p.text.strip() for p in doc_user.paragraphs if p.text.strip()]

# Let's inspect generate_report.py by extracting all body strings
# Or we can run generate_report.py to generate a temporary docx and compare them
import sys
sys.path.append(r"c:\RIYOMA\Internship\WallfitAI\scratch")
from generate_report import create_report

# Temporarily generate docx from script
# We will modify create_report to save as temp.docx temporarily
import inspect
import re

# Read generate_report.py content
with open(r"c:\RIYOMA\Internship\WallfitAI\scratch\generate_report.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace output file in code so it writes to temp.docx
temp_code = code.replace(
    'out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Rapport_de_Stage_BTS.docx")',
    'out_path = r"c:\\RIYOMA\\Internship\\WallfitAI\\scratch\\temp_generated.docx"'
)

exec(temp_code, globals())
create_report()

doc_gen = docx.Document(r"c:\RIYOMA\Internship\WallfitAI\scratch\temp_generated.docx")
p_gen = [p.text.strip() for p in doc_gen.paragraphs if p.text.strip()]

print(f"User paragraphs: {len(p_user)}, Temp generated paragraphs: {len(p_gen)}")

# Compute diff
diff = list(difflib.unified_diff(p_gen, p_user, fromfile="Generated", tofile="User", n=1))
print(f"Diff lines count: {len(diff)}")
for line in diff[:30]:
    print(line)

# Clean up temp file
if os.path.exists(r"c:\RIYOMA\Internship\WallfitAI\scratch\temp_generated.docx"):
    os.remove(r"c:\RIYOMA\Internship\WallfitAI\scratch\temp_generated.docx")

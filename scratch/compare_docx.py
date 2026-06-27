import docx

doc_user = docx.Document(r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS1_V3_15jours.docx")
doc_generated = docx.Document(r"c:\RIYOMA\Internship\WallfitAI\Rapport_de_Stage_BTS.docx")

p_user = [p.text.strip() for p in doc_user.paragraphs if p.text.strip()]
p_gen = [p.text.strip() for p in doc_generated.paragraphs if p.text.strip()]

print(f"User paragraphs count (non-empty): {len(p_user)}")
print(f"Generated paragraphs count (non-empty): {len(p_gen)}")

mismatches = 0
for idx, (u, g) in enumerate(zip(p_user, p_gen)):
    if u != g:
        print(f"Mismatch at index {idx}:")
        print(f"  User: {u[:100]}...")
        print(f"  Gen : {g[:100]}...")
        mismatches += 1
        if mismatches > 5:
            break
            
if mismatches == 0 and len(p_user) == len(p_gen):
    print("Documents are identical in text!")
else:
    print(f"Found differences or length mismatch. Identical so far: {mismatches == 0}")

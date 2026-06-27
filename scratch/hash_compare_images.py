import os
import hashlib

extracted_dir = r"c:\RIYOMA\Internship\WallfitAI\scratch\extracted_media"
generated_dir = r"c:\RIYOMA\Internship\WallfitAI\scratch\images"

def get_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

ext_hashes = {}
for name in os.listdir(extracted_dir):
    p = os.path.join(extracted_dir, name)
    if os.path.isfile(p):
        ext_hashes[name] = get_hash(p)

gen_hashes = {}
for name in os.listdir(generated_dir):
    p = os.path.join(generated_dir, name)
    if os.path.isfile(p):
        gen_hashes[name] = get_hash(p)

print("=== Extracted Images Hashes ===")
for name, h in ext_hashes.items():
    print(f"{name}: {h}")

print("\n=== Generated Images Hashes ===")
for name, h in gen_hashes.items():
    print(f"{name}: {h}")

print("\n=== Matches ===")
for ext_name, ext_hash in ext_hashes.items():
    matched = False
    for gen_name, gen_hash in gen_hashes.items():
        if ext_hash == gen_hash:
            print(f"Extracted {ext_name} matches Generated {gen_name}")
            matched = True
            break
    if not matched:
        print(f"Extracted {ext_name} has NO match in Generated!")

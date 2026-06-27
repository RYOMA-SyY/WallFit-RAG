"""
Indexing script for WallfitAI.
Builds the Chroma vector store and saves chunks.pkl for hybrid retrieval.
"""

import os
import pickle
import shutil
import pandas as pd
from dotenv import load_dotenv
from datasets import load_dataset
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment
load_dotenv()

# Config
DATASET_DIR = "./DataSet"
DB_DIR = "./chroma_db"
EMBED_MODEL = os.environ.get("WALLFIT_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DEVICE = os.environ.get("WALLFIT_EMBED_DEVICE", "cpu")

TRUSTED_SOURCES = [
    "ijerph-20-01739.pdf",
    "mcPHASES.pdf",
    "nihms-75542.pdf",
    "exercise_dataset.csv",
    "gym_members_exercise_tracking.csv",
    "health_fitness_dataset.csv"
]

HF_DATASETS = [
    "hammamwahab/fitness-qa",
    "chibbss/fitness-chat-prompt-completion-dataset",
    "onurSakar/GYM-Exercise",
    "its-myrto/fitness-question-answers"
]

def mask_sensitive_data(text):
    import re
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b', '[PHONE]', text)
    text = re.sub(r'(?i)(api[_-]?key|secret|password|passwd|token|auth)[:=]\s*[\w-]{16,}', r'\1:[MASKED]', text)
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
    return text

def load_local_documents(root_dir):
    documents = []
    print(f"--- Loading Local Documents from {root_dir} ---")
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename not in TRUSTED_SOURCES and not filename.endswith(('.pdf', '.docx', '.csv', '.txt', '.md')):
                continue
            
            filepath = os.path.join(dirpath, filename)
            ext = filename.lower().split('.')[-1]
            try:
                if ext == 'pdf':
                    print(f"  [PDF] {filename}")
                    docs = PyPDFLoader(filepath).load()
                    for d in docs:
                        d.page_content = mask_sensitive_data(d.page_content)
                    documents.extend(docs)
                elif ext == 'docx':
                    print(f"  [DOCX] {filename}")
                    docs = Docx2txtLoader(filepath).load()
                    for d in docs:
                        d.page_content = mask_sensitive_data(d.page_content)
                    documents.extend(docs)
                elif ext in ('txt', 'md'):
                    print(f"  [{ext.upper()}] {filename}")
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    masked = mask_sensitive_data(content)
                    documents.append(Document(page_content=masked, metadata={'source': filepath}))
                elif ext == 'csv':
                    print(f"  [CSV] {filename}")
                    df = pd.read_csv(filepath, nrows=1000)
                    masked = mask_sensitive_data(df.to_string(index=False))
                    documents.append(Document(page_content=masked, metadata={'source': filepath}))
            except Exception as e:
                print(f"  [SKIP] {filename}: {e}")
    return documents

def load_hf_datasets(dataset_ids, max_rows=1000):
    documents = []
    print("\n--- Loading HuggingFace Datasets ---")
    for ds_id in dataset_ids:
        print(f"  [HF] {ds_id}...")
        try:
            ds = load_dataset(ds_id, split='train')
            count = 0
            for row in ds:
                if count >= max_rows: break
                text = "\n".join([f"{k}: {v}" for k,v in row.items() if isinstance(v, str)])
                if len(text) > 20:
                    documents.append(Document(
                        page_content=mask_sensitive_data(text),
                        metadata={'source': ds_id, 'type': 'hf_dataset'}
                    ))
                    count += 1
            print(f"       -> {count} entries.")
        except Exception as e:
            print(f"       -> ERROR: {e}")
    return documents

def main():
    if os.path.exists(DB_DIR):
        print(f"Clearing old database at {DB_DIR}...")
        shutil.rmtree(DB_DIR)
    
    local_docs = load_local_documents(DATASET_DIR)
    hf_docs = load_hf_datasets(HF_DATASETS)
    all_docs = local_docs + hf_docs
    
    if not all_docs:
        print("No documents found!")
        return

    print(f"\nTotal docs: {len(all_docs)}. Splitting...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=2800, chunk_overlap=400)
    chunks = splitter.split_documents(all_docs)
    print(f"Created {len(chunks)} chunks.")

    print("Embedding and building vector store (this may take a minute)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL, model_kwargs={'device': EMBED_DEVICE})
    
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    # Save chunks.pkl for BM25 (required by engine.py)
    chunks_path = os.path.join(DB_DIR, "chunks.pkl")
    with open(chunks_path, "wb") as f:
        pickle.dump(chunks, f)
    
    print(f"DONE! Database built at {DB_DIR}")
    print(f"Indexed {vector_db._collection.count()} chunks.")
    print(f"Saved {chunks_path} for hybrid retrieval.")

if __name__ == "__main__":
    main()

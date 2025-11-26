import pandas as pd
import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from tqdm import tqdm 

load_dotenv()

DATASET_PATH = os.path.join("Dataset", "mtsamples.csv")
INDEX_PATH = "faiss_medical_index"

# PART 1: Data Preparation
print("PART 1: Data Preparation ")

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}. Please ensure the folder 'Dataset' exists.")

print(f"Loading data from {DATASET_PATH}...")
df = pd.read_csv(DATASET_PATH)

df_clean = df.dropna(subset=['transcription'])
if 'Unnamed: 0' in df_clean.columns:
    df_clean = df_clean.drop(columns=['Unnamed: 0'])

print(f"Data cleaned. Processing {len(df_clean)} records...")

def prepare_context(row):
    return f"""
    medical_specialty: {row['medical_specialty']}
    sample_name: {row['sample_name']}
    transcription: {row['transcription']}
    """

df_clean['text_for_rag'] = df_clean.apply(prepare_context, axis=1)

print("Splitting text into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " ", ""]
)

documents = []
for index, row in df_clean.iterrows():
    chunks = text_splitter.split_text(row['text_for_rag'])
    for chunk in chunks:
        doc = Document(
            page_content=chunk,
            metadata={
                'source_id': index,
                'specialty': row['medical_specialty']
            }
        )
        documents.append(doc)

print(f"Prepared {len(documents)} document chunks.")

# PART 2: Vector Store Creation
print("\n--- PART 2: Vector Store Creation ---")

print("Initializing HuggingFace Embedding Model (Local & Free)...")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print(f"Creating FAISS Index with Progress Bar...")

batch_size = 32
total_docs = len(documents)

# Create the vector store with the first batch to initialize it
vector_store = FAISS.from_documents(documents[:batch_size], embeddings)

# Process the rest in batches with a progress bar
for i in tqdm(range(batch_size, total_docs, batch_size), desc="Embedding Documents"):
    batch = documents[i : i + batch_size]
    vector_store.add_documents(batch)

print(f"\nSaving index to folder: '{INDEX_PATH}'...")
vector_store.save_local(INDEX_PATH)

print("Success! Database created.")
print(f"You can now create your 'app.py' and load '{INDEX_PATH}' to query it.")
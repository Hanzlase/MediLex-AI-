import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# Import the official Cohere integration
from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# --- Configuration ---
load_dotenv()
# Load Cohere Key
COHERE_API_KEY = os.getenv("cohere_api_key")
INDEX_PATH = "faiss_medical_index"

if not COHERE_API_KEY:
    raise ValueError(" Error: 'cohere_api_key' missing in .env")

if not os.path.exists(INDEX_PATH):
    raise FileNotFoundError(f" Error: Vector store not found at '{INDEX_PATH}'. Run Part 2 first.")

print(" Configuration loaded.")

# Step 1: Load the Vector Store
print("Loading Vector Store...")
# We keep HuggingFace embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_store = FAISS.load_local(
    INDEX_PATH, 
    embeddings, 
    allow_dangerous_deserialization=True
)
print("✅ Vector Store Loaded.")

# Step 2: Setup the Retriever 
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# Step 3: Setup the Cohere Model
print("Initializing Cohere Command R (08-2024)...")


llm = ChatCohere(
    model="command-r-08-2024",
    cohere_api_key=COHERE_API_KEY,
    temperature=0.3
)

#Step 4: Create the Prompt Template
system_prompt = (
    "You are an expert Medical Assistant. Use the provided context to answer the question. "
    "If the answer is not in the context, say 'I cannot find the answer in the provided medical records'. "
    "Always mention the 'Source ID' or 'Specialty' from the context metadata in your answer.\n\n"
    "Context:\n{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# Step 5: Build the Chain
def format_docs(docs):
    formatted = []
    for doc in docs:
        meta = doc.metadata
        formatted.append(f"Source ID: {meta.get('source_id')}\nSpecialty: {meta.get('specialty')}\nContent: {doc.page_content}")
    return "\n\n".join(formatted)

rag_chain_with_source = RunnableParallel(
    {"context": retriever, "input": RunnablePassthrough()}
)

answer_chain = (
    RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
    | prompt
    | llm
    | StrOutputParser()
)

rag_chain = rag_chain_with_source.assign(answer=answer_chain)

print("RAG Pipeline is ready!")

#Test Function
if __name__ == "__main__":
    test_question = "What are the symptoms of allergic rhinitis?"
    print(f"\n Testing Question: {test_question}")
    
    try:
        response = rag_chain.invoke(test_question)
        
        print("\n Answer:")
        print(response["answer"])
        
        print("\n Sources used:")
        for doc in response["context"]:
            print(f"- [ID: {doc.metadata.get('source_id')}] Specialty: {doc.metadata.get('specialty')}")
    except Exception as e:
        print(f"\n Error during generation: {e}")
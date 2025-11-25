<div align="center">

<img src="https://www.google.com/search?q=https://img.icons8.com/fluency/96/null/medical-doctor.png" alt="MediLex Logo" width="100" />

<h1>🩺 MediLex AI Assistant</h1>

<p>
<strong>A Next-Gen Clinical Decision Support System Powered by RAG & Cohere Command R</strong>
</p>

<p>
<a href="https://medilexai.streamlit.app/">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/🚀_View_Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" alt="Live Demo" />
</a>
<a href="https://github.com/Hanzlase/MediLex-AI-.git">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/📂_GitHub_Repo-181717?style=for-the-badge&logo=github" alt="GitHub Repo" />
</a>
</p>

<br />

<!-- Tech Stack Badges -->

<p>
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3.10%2B-3776AB%3Fstyle%3Dflat%26logo%3Dpython%26logoColor%3Dwhite" />
<img src="https://www.google.com/search?q=https://img.shields.io/badge/LangChain-🦜🔗-1C3C3C?style=flat" />
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Cohere-Command_R-390099%3Fstyle%3Dflat" />
<img src="https://www.google.com/search?q=https://img.shields.io/badge/FAISS-Vector_DB-005571%3Fstyle%3Dflat" />
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Streamlit-Frontend-FF4B4B%3Fstyle%3Dflat%26logo%3Dstreamlit%26logoColor%3Dwhite" />
<img src="https://www.google.com/search?q=https://img.shields.io/badge/HuggingFace-Embeddings-FFD21E%3Fstyle%3Dflat%26logo%3Dhuggingface%26logoColor%3Dblack" />
</p>
</div>

<hr />

📖 Overview

MediLex AI is an advanced Retrieval-Augmented Generation (RAG) system designed to assist medical professionals and students. It ingests raw medical transcriptions, indexes them for semantic search, and uses the Cohere Command R Large Language Model to answer complex clinical queries with precise source citations.

Unlike standard chatbots, MediLex is grounded—if the answer isn't in the medical records, it tells you, reducing hallucinations and ensuring reliability.

🏗️ System Architecture

graph LR
    A[📂 Medical Transcriptions CSV] -->|Cleaning & Chunking| B(Pre-processing)
    B -->|HuggingFace Embeddings| C[(FAISS Vector Store)]
    
    U[👤 User Query] -->|Streamlit UI| D{RAG Pipeline}
    D -->|Retrieve Top-k| C
    D -->|Context + Prompt| E[🧠 Cohere Command R]
    E -->|Grounded Answer| U


✨ Key Features

🏥 Specialized Knowledge: Trained on real-world medical transcriptions (Surgery, Radiology, SOAP notes).

📚 Citation-Aware: Every answer includes the Source ID and Specialty of the retrieved document.

🛡️ Hallucination Guard: Explicitly refuses to answer if the information is missing from the context.

🏎️ High Performance: Uses local HuggingFace Embeddings (all-MiniLM-L6-v2) for fast retrieval and Cohere Command R for accurate reasoning.

🌑 Professional UI: Dark-themed, distraction-free Streamlit interface optimized for clinical environments.

📂 Project Structure

MediLex-AI-/
├── 📂 Dataset/
│   └── mtsamples.csv          # Raw medical transcriptions
├── 📂 faiss_medical_index/    # Vector Database (Generated)
│   ├── index.faiss
│   └── index.pkl
├── 📜 .env                    # API Keys (Not uploaded to GitHub)
├── 📜 .gitignore              # Files to ignore
├── 📜 CareComply.py           # Ingestion Pipeline (ETL)
├── 📜 rag_backend.py          # RAG Logic & LLM Chain
├── 📜 app.py                  # Streamlit Frontend
├── 📜 requirements.txt        # Dependencies
├── 📜 test.md                 # Evaluation Questions
└── 📜 README.md               # Documentation


🚀 Local Setup Guide

1. Clone the Repository

git clone [https://github.com/Hanzlase/MediLex-AI-.git](https://github.com/Hanzlase/MediLex-AI-.git)
cd MediLex-AI-


2. Install Dependencies

pip install -r requirements.txt


3. Set Up Environment Keys

Create a .env file in the root directory:

cohere_api_key=YOUR_COHERE_API_KEY_HERE


4. Build the Vector Database

Run the ingestion script once to process the dataset:

python CareComply.py


> This processes mtsamples.csv, chunks the text, and saves the FAISS index locally.

5. Launch the App

streamlit run app.py


📊 Evaluation

The system was evaluated on 30 Test Cases across 5 medical specialties.

Specialty

Query Example

Status

Allergy

"Symptoms of allergic rhinitis?"

✅ Pass

Cardiology

"Procedure for cardiac catheterization?"

✅ Pass

Neurology

"Diagnosis of carpal tunnel?"

✅ Pass

Gastro

"Indications for colonoscopy?"

✅ Pass

Urology

"Treatment for kidney stones?"

✅ Pass

🤝 Contributors

Your Name - Lead Developer

<div align="center">
<small>Developed for Generative AI Project 04 | Fall 2025</small>
</div>
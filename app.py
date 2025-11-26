import streamlit as st
import time

# Import the RAG chain we built in Part 3
# This might take a few seconds to load the vector store on startup
from rag_backend import rag_chain

# --- Page Config ---
st.set_page_config(
    page_title="MediLex AI - Medical Assistant",
    page_icon="⚕️",
    layout="centered"
)

# Custom CSS for professional styling with mobile responsiveness
st.markdown("""
<style>
    /* Base styles */
    .main-header {
        font-size: clamp(1.5rem, 5vw, 2.5rem);
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: clamp(0.9rem, 3vw, 1.1rem);
        color: #4b5563;
        margin-bottom: 2rem;
        text-align: center;
        padding: 0 1rem;
    }
    .sidebar-header {
        font-size: clamp(1rem, 4vw, 1.2rem);
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 1rem;
    }
    .test-case-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .test-case-box:hover {
        background-color: #e0f2fe;
        border-color: #0284c7;
        transform: translateY(-1px);
    }
    .chat-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: clamp(10px, 3vw, 20px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .reference-section {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: clamp(12px, 3vw, 16px);
        margin-top: 16px;
    }
    .user-message {
        background-color: #1e3a8a;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 85%;
        margin-left: auto;
        word-wrap: break-word;
        font-size: clamp(0.9rem, 2.5vw, 1rem);
    }
    .assistant-message {
        background-color: #f1f5f9;
        color: #1f2937;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        margin-right: auto;
        word-wrap: break-word;
        font-size: clamp(0.9rem, 2.5vw, 1rem);
    }
    .stChatInput {
        position: sticky;
        bottom: 20px;
        background: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    /* Mobile-specific adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.75rem;
            margin-bottom: 0.25rem;
        }
        .sub-header {
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }
        .user-message, .assistant-message {
            max-width: 90%;
            padding: 10px 14px;
            font-size: 0.95rem;
        }
        .stButton button {
            font-size: 0.9rem;
            padding: 0.5rem;
        }
        .chat-container {
            padding: 10px;
        }
        /* Make expander more touch-friendly */
        .streamlit-expanderHeader {
            padding: 12px !important;
            font-size: 0.95rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }
        .sub-header {
            font-size: 0.85rem;
        }
        .user-message, .assistant-message {
            max-width: 95%;
            padding: 8px 12px;
            font-size: 0.9rem;
        }
    }
    
    /* Improve button touch targets on mobile */
    .stButton button {
        min-height: 44px;
        width: 100%;
    }
    
    /* Better spacing for metrics on mobile */
    @media (max-width: 768px) {
        [data-testid="metric-container"] {
            font-size: 0.85rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing_query" not in st.session_state:
    st.session_state.processing_query = None

# --- Header ---
st.markdown('<div class="main-header">MediLex AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Retrieval-Augmented Generation on Medical Transcriptions</div>', unsafe_allow_html=True)

# --- Sidebar: Test Cases ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">Quick Test Cases</div>', unsafe_allow_html=True)
    st.markdown("Select a question to get started:")
    
    test_cases = [
        "What are the symptoms of allergic rhinitis?",
        "Describe the procedure for a cardiac catheterization.",
        "What are the symptoms of atrial fibrillation?",
        "How is carpal tunnel syndrome diagnosed?",
        "What is the surgical approach for a rotator cuff repair?",
        "What are the indications for a colonoscopy?",
        "Describe the symptoms of GERD.",
        "What is the treatment for kidney stones?",
        "How is Type 2 Diabetes managed?",
    ]

    # Display test cases as clickable boxes
    for i, case in enumerate(test_cases):
        if st.button(case, key=f"test_case_{i}", use_container_width=True):
            # Set the query to be processed
            st.session_state.processing_query = case
            st.rerun()

# --- Display Chat History ---
with st.container():
    st.markdown("### Conversation History")
    
    if not st.session_state.messages:
        st.info("Start a conversation by typing a medical question or selecting a test case from the sidebar.")
    else:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

# --- Process Sidebar Query First ---
if st.session_state.processing_query:
    prompt = st.session_state.processing_query
    st.session_state.processing_query = None  # Reset immediately
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    
    # Generate and display response
    with st.spinner("Analyzing medical records..."):
        try:
            response = rag_chain.invoke(prompt)
            answer = response["answer"]
            sources = response["context"]
            
            # Display assistant response
            full_response = answer
            
            # Show the complete response at once (no streaming for sidebar clicks)
            st.markdown(f'<div class="assistant-message">{full_response}</div>', unsafe_allow_html=True)
            
            # Show Citations (Sources) in an Expander
            with st.expander("Reference Documents (Evidence)", expanded=False):
                st.markdown("**Supporting medical documents used in generating this response:**")
                
                for i, doc in enumerate(sources):
                    with st.container():
                        st.markdown(f"**Document {i+1}**")
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.metric("Source ID", doc.metadata.get('source_id', 'N/A'))
                            st.metric("Specialty", doc.metadata.get('specialty', 'N/A'))
                        with col2:
                            st.text_area(
                                f"Content preview {i+1}", 
                                value=doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else ""), 
                                height=120, 
                                key=f"sidebar_doc_{i}_{len(st.session_state.messages)}",
                                disabled=True
                            )
                    if i < len(sources) - 1:
                        st.divider()

            # Save assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred while processing your request: {str(e)}")
            st.info("Please try again or rephrase your question.")

# --- Regular Chat Input (Always visible) ---
if user_prompt := st.chat_input("Ask a medical question..."):
    # Process manual input
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.markdown(f'<div class="user-message">{user_prompt}</div>', unsafe_allow_html=True)

    # Generate Answer for manual input
    with st.spinner("Analyzing medical records..."):
        try:
            response = rag_chain.invoke(user_prompt)
            answer = response["answer"]
            sources = response["context"]
            
            # Display assistant response with streaming effect
            assistant_placeholder = st.empty()
            full_response = ""
            
            # Simulate stream typing only for manual input
            for chunk in answer.split():
                full_response += chunk + " "
                time.sleep(0.03)
                assistant_placeholder.markdown(f'<div class="assistant-message">{full_response}</div>', unsafe_allow_html=True)
            
            assistant_placeholder.markdown(f'<div class="assistant-message">{full_response}</div>', unsafe_allow_html=True)

            # Show Citations (Sources) in an Expander
            with st.expander("Reference Documents (Evidence)", expanded=False):
                st.markdown("**Supporting medical documents used in generating this response:**")
                
                for i, doc in enumerate(sources):
                    with st.container():
                        st.markdown(f"**Document {i+1}**")
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.metric("Source ID", doc.metadata.get('source_id', 'N/A'))
                            st.metric("Specialty", doc.metadata.get('specialty', 'N/A'))
                        with col2:
                            st.text_area(
                                f"Content preview {i+1}", 
                                value=doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else ""), 
                                height=120, 
                                key=f"chat_doc_{i}_{len(st.session_state.messages)}",
                                disabled=True
                            )
                    if i < len(sources) - 1:
                        st.divider()

            # Save assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred while processing your request: {str(e)}")
            st.info("Please try again or rephrase your question.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; font-size: clamp(0.8rem, 2vw, 0.9rem);'>"
    "MediLex AI - Medical Information Assistant | For educational and research purposes"
    "</div>", 
    unsafe_allow_html=True
)
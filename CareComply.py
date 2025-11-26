import gradio as gr
import time
from rag_backend import rag_chain

# --- Logic Function ---
def generate_response(message, history):
    """
    This function handles the interaction with the RAG chain.
    It returns the answer and formats the sources nicely.
    """
    if not message:
        return ""

    try:
        # 1. Call the RAG pipeline
        response = rag_chain.invoke(message)
        answer = response["answer"]
        sources = response["context"]

        # 2. Format Sources (Evidence) using Markdown
        # We create a collapsible details section for cleaner UI
        source_details = "\n\n<details><summary><b>📚 Click to view Medical Sources</b></summary>\n\n"
        
        for i, doc in enumerate(sources):
            source_id = doc.metadata.get('source_id', 'N/A')
            specialty = doc.metadata.get('specialty', 'Unknown')
            # Clean content for display (first 300 chars)
            content_snippet = doc.page_content[:300].replace("\n", " ") + "..."
            
            source_details += f"**Source #{i+1}** (ID: `{source_id}`)\n"
            source_details += f"*Specialty: {specialty}*\n"
            source_details += f"> {content_snippet}\n\n"
            source_details += "---\n"
        
        source_details += "</details>"

        # 3. Combine Answer + Sources
        final_output = f"{answer}\n{source_details}"
        
        return final_output

    except Exception as e:
        error_msg = f"⚠️ **An error occurred:** {str(e)}"
        return error_msg

# --- Custom UI Theme ---
theme = gr.themes.Soft(
    primary_hue="cyan",
    secondary_hue="slate",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"]
)

# --- Examples List ---
example_questions = [
    "What are the symptoms of allergic rhinitis?",
    "Describe the procedure for a cardiac catheterization.",
    "How is carpal tunnel syndrome diagnosed?",
    "What are the indications for a colonoscopy?",
    "What is the treatment for kidney stones?",
]

# --- Build the App ---
with gr.Blocks(theme=theme, title="MediLex AI") as demo:
    
    # Header Section
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(
                """
                # 🩺 **MediLex AI Assistant**
                ### *Retrieval-Augmented Generation (RAG) for Medical Queries*
                """
            )
    
    # Main Chat Layout
    # Updated for Gradio 5.0 compatibility: Removed unsupported button args and added type="messages"
    chat_interface = gr.ChatInterface(
        fn=generate_response, 
        type="messages", 
        chatbot=gr.Chatbot(
            height=600, 
            show_copy_button=True, 
            render_markdown=True,
            type="messages",
            avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/3774/3774299.png") # User (Default), Bot (Medical Icon)
        ),
        textbox=gr.Textbox(placeholder="Ask a medical question here...", container=False, scale=7),
        title=None,
        description=None,
        theme=theme,
        examples=example_questions,
        cache_examples=False,
    )

# --- Launch ---
if __name__ == "__main__":
    print("🚀 Launching MediLex Gradio App...")
    demo.launch()
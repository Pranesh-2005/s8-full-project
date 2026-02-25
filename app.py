"""
Gradio app for Multi-Document RAG Assistant
(Auto-loads documents from data/ directory)
"""

import gradio as gr
from backend.processing import process_documents_from_directory, get_available_files
from backend.rag import RAGEngine
from backend.llm import LLMClient

# -------------------------------
# Global state
# -------------------------------
rag_engine = RAGEngine()
llm_client = LLMClient()

# -------------------------------
# Auto-initialize on startup
# -------------------------------
def initialize_system():
    """Initialize the system by loading documents from data/ directory."""
    try:
        available_files = get_available_files("data")
        if not available_files:
            return "⚠️ No documents found in data/ directory. Please add PDF, TXT, or MD files to the data folder.", []
        
        print(f"📁 Found {len(available_files)} files: {available_files}")
        
        # Check if we already have an index with these files
        if rag_engine.get_chunk_count() > 0:
            return f"✅ Using existing index with {rag_engine.get_chunk_count()} chunks", available_files
        
        # Process and index documents
        chunks = process_documents_from_directory("data")
        if chunks:
            rag_engine.add_documents(chunks)
            return f"✅ Ready! Indexed {len(chunks)} chunks from {len(available_files)} documents.", available_files
        else:
            return "⚠️ No valid content extracted from documents", available_files
    except Exception as e:
        return f"❌ Error initializing system: {str(e)}", []

# Initialize system on startup
system_status, loaded_files = initialize_system()
print(f"System Status: {system_status}")

# -------------------------------
# Rebuild index function
# -------------------------------
def rebuild_index():
    """Rebuild the index from data/ directory."""
    try:
        chunk_count = rag_engine.rebuild_from_data("data")
        available_files = get_available_files("data")
        if chunk_count > 0:
            status = f"✅ Rebuilt index with {chunk_count} chunks from {len(available_files)} files"
        else:
            status = "⚠️ No documents found to index"
        return status, chunk_count, available_files
    except Exception as e:
        return f"❌ Error rebuilding index: {str(e)}", 0, []

# -------------------------------
# Search & generate answer
# -------------------------------
def search_and_answer(question, top_k, history):
    if not question.strip():
        return history, ""

    if rag_engine.get_chunk_count() == 0:
        error_msg = "⚠️ No documents loaded. Please add PDF, TXT, or MD files to the 'data/' directory and click 'Rebuild Index'."
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": error_msg})
        return history, ""

    try:
        # Search for relevant chunks
        results = rag_engine.search(question, top_k=top_k)

        if not results:
            no_results_msg = "⚠️ No relevant information found in the documents for this question."
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": no_results_msg})
            return history, ""

        # Generate answer
        answer = llm_client.generate_answer(question, results)

        # Add to chat history
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        return history, ""
    
    except Exception as e:
        error_msg = f"❌ Error processing question: {str(e)}"
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": error_msg})
        return history, ""

def get_system_info():
    """Get current system information."""
    current_files = get_available_files("data")
    chunk_count = rag_engine.get_chunk_count()
    
    info = f"""
**📊 System Status**

**📁 Documents in data/ folder:** {len(current_files)}
{chr(10).join([f"• {file}" for file in current_files]) if current_files else "• None"}

**🧠 Chunks Indexed:** {chunk_count}

**🤖 LLM Status:** {"✅ Azure OpenAI configured" if llm_client.has_token() else "⚠️ No Azure OpenAI token (using extractive fallback)"}

**💡 Usage:** Ask questions about the content in your documents. The system searches through all indexed chunks to provide relevant answers.
"""
    return info

# -------------------------------
# UI - Clean Chat Interface
# -------------------------------
with gr.Blocks(
    title="AI Document Assistant", 
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
        margin: auto;
    }
    """
) as demo:
    
    # Header
    gr.Markdown("""
    # 🤖 AI Document Assistant
    
    Ask questions about your documents. The system automatically loads all documents from the `data/` directory.
    """)
    
    # System info and controls
    with gr.Accordion("📊 System Information & Controls", open=False):
        system_info = gr.Markdown(get_system_info())
        
        with gr.Row():
            refresh_info_btn = gr.Button("🔄 Refresh Info", variant="secondary")
            rebuild_btn = gr.Button("🔨 Rebuild Index", variant="secondary")
        
        rebuild_status = gr.Markdown()
    
    # Main chat interface
    chatbot = gr.Chatbot(
        type="messages", 
        height=500,
        show_label=False,
        container=True,
        show_copy_button=True
    )
    
    # Input area
    with gr.Row():
        question = gr.Textbox(
            placeholder="Ask a question about your documents...",
            label="Your Question",
            scale=4,
            lines=1,
            max_lines=3
        )
        
        submit_btn = gr.Button("💬 Send", variant="primary", scale=1)
    
    # Advanced options
    with gr.Accordion("⚙️ Advanced Settings", open=False):
        top_k = gr.Slider(
            minimum=1,
            maximum=10,
            value=5,
            step=1,
            label="Number of document chunks to retrieve",
            info="Higher values provide more context but may include less relevant information"
        )
        
        clear_btn = gr.Button("🗑️ Clear Chat History", variant="secondary")

    # -------------------------------
    # Event handlers
    # -------------------------------
    
    # Submit on button click
    submit_btn.click(
        search_and_answer,
        inputs=[question, top_k, chatbot],
        outputs=[chatbot, question]
    )
    
    # Submit on Enter key
    question.submit(
        search_and_answer,
        inputs=[question, top_k, chatbot],
        outputs=[chatbot, question]
    )
    
    # Clear chat history
    clear_btn.click(
        lambda: [],
        outputs=[chatbot]
    )
    
    # Refresh system info
    refresh_info_btn.click(
        get_system_info,
        outputs=[system_info]
    )
    
    # Rebuild index
    rebuild_btn.click(
        rebuild_index,
        outputs=[rebuild_status, system_info, system_info]  # Update both status and info
    )
    
    # Show welcome message if system is ready
    if rag_engine.get_chunk_count() > 0:
        demo.load(
            lambda: [{
                "role": "assistant", 
                "content": f"👋 **Welcome to AI Document Assistant!**\n\nI'm ready to help you with questions about your documents. I have access to **{rag_engine.get_chunk_count()} chunks** of information from **{len(loaded_files)} documents**:\n\n" + 
                "\n".join([f"📄 {file}" for file in loaded_files]) + 
                f"\n\n💡 **What would you like to know?** You can ask about specific topics, request summaries, or explore relationships between different documents."
            }],
            outputs=[chatbot]
        )
    else:
        demo.load(
            lambda: [{
                "role": "assistant", 
                "content": "⚠️ **No documents loaded.**\n\nTo get started:\n1. Create a `data/` folder in your project directory\n2. Add PDF, TXT, or MD files to the folder\n3. Click '🔨 Rebuild Index' or restart the application\n\nI'll automatically load and index all your documents for instant searching!"
            }],
            outputs=[chatbot]
        )

# -------------------------------
# Launch
# -------------------------------
if __name__ == "__main__":
    demo.launch(
        debug=True
    )
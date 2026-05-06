"""
Paradox v2 — Gradio Web Interface
===================================
A premium holographic-style UI for interacting with the Paradox AGI.
"""

import gradio as gr
import time
import os
from ..config import CONFIG

# Use relative imports when running as a module, or simple imports for scripts
# For simplicity in this demo, we assume the API is running or we load the logic directly

def create_ui():
    # Import logic locally to avoid global loading before UI starts
    from ..llm.backbone import ParadoxBackbone
    from ..llm.generator import ParadoxGenerator
    from ..brain.regions import BrainRouter
    from ..brain.emotions import EmotionEngine
    from ..brain.memory import ConversationMemory
    from ..retrieval.vector_store import ParadoxVectorStore
    from ..retrieval.embedder import ParadoxEmbedder

    print("[UI] Loading Paradox Substrate...")
    backbone = ParadoxBackbone()
    adapter_path = os.path.join(CONFIG.training.output_dir, "final_adapter")
    if os.path.exists(adapter_path):
        backbone.load_adapter(adapter_path)
    
    generator = ParadoxGenerator(backbone=backbone)
    router = BrainRouter()
    emotions = EmotionEngine()
    memory = ConversationMemory()
    vector_store = ParadoxVectorStore()
    vector_store.load()
    embedder = ParadoxEmbedder()

    def chat_function(message, history):
        # 1. Routing
        region, conf = router.route_with_confidence(message)
        
        # 2. Retrieval
        q_emb = embedder.encode_query(message)
        context = vector_store.search(q_emb, top_k=CONFIG.retrieval.top_k, region_filter=region)
        context_texts = [c[0]["text"] for c in context]
        
        # 3. Generate
        # Convert Gradio history to Paradox history format
        p_history = []
        for h in history:
            p_history.append({"role": "user", "content": h[0]})
            p_history.append({"role": "assistant", "content": h[1]})
            
        gen_meta = generator.generate_with_metadata(
            query=message,
            context_chunks=context_texts,
            region=region,
            conversation_history=p_history,
            emotion_state=emotions.state
        )
        
        # 4. State Update
        emotions.stimulate_curiosity(len(message))
        emotions.apply_decay()
        memory.add_turn(message, gen_meta["response"], region, len(context_texts), emotions.state)
        
        response = gen_meta["response"]
        
        # Yield character by character to simulate streaming if desired, 
        # but here we return full for simplicity
        return response

    with gr.Blocks(theme=gr.themes.Soft(), title="Paradox AGI") as demo:
        gr.Markdown(
            """
            # ⚛️ PARADOX AGI: SOVEREIGN SUBSTRATE
            *v2.0 — Ascension Edition*
            """
        )
        
        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.ChatInterface(
                    fn=chat_function,
                    examples=["Explain the Quantum Absolute Unit theory.", "Analyze the relationship between entropy and intelligence."],
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 🧠 Brain State")
                curiosity_plot = gr.Label(label="Curiosity", value=f"{emotions.curiosity:.2f}")
                joy_plot = gr.Label(label="Joy", value=f"{emotions.joy:.2f}")
                fear_plot = gr.Label(label="Fear", value=f"{emotions.fear:.2f}")
                
                gr.Markdown("### 🔍 Retrieval Stats")
                kb_size = gr.Number(label="Knowledge Base Size (Chunks)", value=vector_store.total_vectors)
                
                refresh_btn = gr.Button("Refresh Stats")
                def refresh():
                    return emotions.curiosity, emotions.joy, emotions.fear, vector_store.total_vectors
                
                refresh_btn.click(refresh, outputs=[curiosity_plot, joy_plot, fear_plot, kb_size])

    return demo

if __name__ == "__main__":
    ui = create_ui()
    ui.launch(share=True)

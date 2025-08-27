import gradio as gr
from ai_gradio_streaming_ollama import get_ai_tutor_streaming_response
import types
   
def tutor_chat_wrapper(
    prompt: str,
    level: int,
    history: list[dict] | None
):
    """Bridge between Gradio Chatbot (messages API) and the streaming backend."""
    history = history or []

    # Append user message and a placeholder assistant message.
    history.append({"role": "user", "content": prompt})
    history.append({"role": "assistant", "content": ""})

    # Immediately clear the textbox.
    yield history, gr.update(value=""), history

    # Call your streaming function: (user_prompt, explanation_level_value).
    result = get_ai_tutor_streaming_response(prompt, level)

    # If generator, stream chunks into the last assistant message.
    if isinstance(result, types.GeneratorType):
        full_text = ""
        for chunk in result:
            full_text = chunk
            history[-1]["content"] = full_text
            # Update Chatbot and State (history); keep textbox as-is.
            yield history, gr.update(), history
    else:
        # Fallback if backend returns a single final string.
        history[-1]["content"] = str(result)
        yield history, gr.update(), history


def create_streaming_interface():
    """Create and return the Gradio interface."""
    with gr.Blocks(title="AI Tutor", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            <div style="display:flex;align-items:flex-end;gap:12px;">
              <h1 style="margin:0;font-size:2rem;">🎓 AI Tutor</h1>
              <span style="color:#6b7280;">
                Learn anything with tailored explanations
              </span>
            </div>
            <hr/>
            """
        )

        with gr.Row():
            # ---------- Left Column: Controls ----------
            with gr.Column(scale=1, min_width=330):
                gr.Markdown("### Controls")

                explanation_level = gr.Slider(
                    minimum=1,
                    maximum=5,
                    step=1,
                    value=3,
                    label="Explanation Level (1 = simple, 5 = technical)",
                    interactive=True,
                )

                user_input = gr.Textbox(
                    lines=3,
                    placeholder="Ask the AI tutor anything…",
                    label="Your Question",
                )

                with gr.Row():
                    submit_btn = gr.Button("Submit", variant="primary")
                    clear_btn = gr.Button("Clear")

                gr.Markdown(
                    """
                    **Tips**
                    - Use level 1–2 for simple explanations.
                    - Use level 4–5 for technical depth.
                    """
                )

            # ---------- Right Column: Assistant Chat ----------
            with gr.Column(scale=2):
                gr.Markdown("### Assistant")
                chat = gr.Chatbot(
                    type="messages",
                    label="AI Tutor Answer",
                    height=420,
                    show_copy_button=True,
                )
                # Store conversation messages (OpenAI-style dicts).
                state = gr.State([])

        # ---------- Events ----------
        submit_btn.click(
            fn=tutor_chat_wrapper,
            inputs=[user_input, explanation_level, state],
            outputs=[chat, user_input, state],
            show_progress=True,
        )

        user_input.submit(
            fn=tutor_chat_wrapper,
            inputs=[user_input, explanation_level, state],
            outputs=[chat, user_input, state],
            show_progress=True,
        )

        def clear_all():
            """Reset chat, input box, slider, and state."""
            return [], gr.update(value=""), gr.update(value=3), []

        clear_btn.click(
            fn=clear_all,
            inputs=[],
            outputs=[chat, user_input, explanation_level, state],
        )

    return demo


if __name__ == "__main__":
    create_streaming_interface().launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860,
    )
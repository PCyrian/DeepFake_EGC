from ui import app

if __name__ == "__main__":
    ui = app.build_ui()
    ui.launch(share=True, server_name="0.0.0.0", server_port=7860)

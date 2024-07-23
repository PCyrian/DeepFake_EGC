from ui.app import DeepFakeApp
import customtkinter as ctk

if __name__ == "__main__":
    root = ctk.CTk()
    app = DeepFakeApp(root)
    root.mainloop()

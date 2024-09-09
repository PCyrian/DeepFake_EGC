import customtkinter as ctk
from tkinter import filedialog, messagebox
from threading import Thread
import os
import torch
from time import time
from run_docker import run_video_retalking
from moviepy.editor import VideoFileClip
from TTS.api import TTS  # Import the TTS module


class DeepFakeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lip Sync Processor")
        self.root.geometry("600x500")

        self.video_file = ""
        self.tts_audio_file_template = "generated_audio_{iteration}.wav"
        self.output_video_file_template = "output_video_{iteration}.mp4"

        self.setup_ui()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Use GPU if available, otherwise fallback to CPU
        print("Using device: {}".format(self.device))

    def setup_ui(self):
        # Set up the UI components for the application
        self.label_video = ctk.CTkLabel(self.root, text="Select Face File (MP4 or Image):")
        self.label_video.pack(pady=10)

        self.button_video = ctk.CTkButton(self.root, text="Select File", command=self.select_video_file)
        self.button_video.pack(pady=10)

        self.textbox = ctk.CTkEntry(self.root, width=400, placeholder_text="Enter text for TTS")
        self.textbox.pack(pady=10)

        self.label_iterations = ctk.CTkLabel(self.root, text="Number of Iterations:")
        self.label_iterations.pack(pady=10)

        self.entry_iterations = ctk.CTkEntry(self.root, width=100, placeholder_text="1")
        self.entry_iterations.pack(pady=10)

        self.button_process = ctk.CTkButton(self.root, text="Process", command=self.process_video)
        self.button_process.pack(pady=20)

    def select_video_file(self):
        # File dialog to select video or image
        self.video_file = filedialog.askopenfilename(
            filetypes=[("MP4 files", "*.mp4"), ("Image files", "*.jpg;*.jpeg;*.png")]
        )
        if self.video_file:
            self.label_video.configure(text=f"Selected: {os.path.basename(self.video_file)}")

    def extract_audio(self, video_file):
        try:
            # Extract audio from video
            clip = VideoFileClip(video_file)
            audio_file = video_file.replace(".mp4", "_extracted.wav")
            clip.audio.write_audiofile(audio_file)
            return audio_file
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None

    def generate_tts_audio(self, text, extracted_audio_file, tts_output_file, device):
        try:
            # Generate TTS audio using the provided function
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)
            tts.tts_to_file(text=text, speaker_wav=extracted_audio_file, file_path=tts_output_file, language='fr')
        except Exception as e:
            print(f"Error generating TTS audio: {e}")
            return None

    def process_video(self):
        # Validate input fields before starting the process
        if not self.video_file or not self.textbox.get() or not self.entry_iterations.get().isdigit():
            messagebox.showerror("Error", "Please select a video file, enter text for TTS, and specify the number of iterations.")
            return

        iterations = int(self.entry_iterations.get())
        text = self.textbox.get()

        def process_task():
            try:
                # Step 1: Extract audio from video
                extracted_audio_file = self.extract_audio(self.video_file)
                if not extracted_audio_file:
                    print("Failed to extract audio.")
                    return

                # Step 2: Iterate over the number of times specified
                for iteration in range(iterations):
                    tts_output_file = self.tts_audio_file_template.format(iteration=iteration)
                    output_video_file = self.output_video_file_template.format(iteration=iteration)

                    # Step 3: Generate TTS audio
                    self.generate_tts_audio(text, extracted_audio_file, tts_output_file, self.device)

                    # Step 4: Lip sync with new audio
                    run_video_retalking(self.video_file, tts_output_file, output_video_file)
                    print(f"Lip-synced video {iteration+1}/{iterations} saved to {output_video_file}")

            except Exception as e:
                print(f"Error during processing: {e}")

        # Run the process in a separate thread
        Thread(target=process_task).start()


if __name__ == "__main__":
    root = ctk.CTk()
    app = LipSyncApp(root)
    root.mainloop()

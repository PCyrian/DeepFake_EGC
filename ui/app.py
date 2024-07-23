import customtkinter as ctk
from tkinter import filedialog
from threading import Thread
from processing.video import extract_audio, replace_audio_in_video
from processing.audio import generate_tts_audio
from post_processing.cleaning import initial_cleaning
import os
import torch

class DeepFakeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DeepFake Video Processor")
        self.root.geometry("600x400")

        self.video_file = ""
        self.rough_tts_output_file = "rough_tts_output.mp3"
        self.tts_output_file = "tts_output.wav"
        self.output_video_file = "output_video.mp4"

        self.setup_ui()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def setup_ui(self):
        self.label_video = ctk.CTkLabel(self.root, text="Video File:")
        self.label_video.pack(pady=10)
        self.button_video = ctk.CTkButton(self.root, text="Select Video File", command=self.select_video_file)
        self.button_video.pack(pady=10)

        self.textbox = ctk.CTkEntry(self.root, width=400, placeholder_text="Enter text for TTS")
        self.textbox.pack(pady=10)

        self.button_process = ctk.CTkButton(self.root, text="Process", command=self.process_video)
        self.button_process.pack(pady=10)

    def select_video_file(self):
        self.video_file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        self.label_video.configure(text=f"Video File: {os.path.basename(self.video_file)}")

    def process_video(self):
        if not self.video_file or not self.textbox.get():
            print("Please select a video file and enter text for TTS.")
            return

        def process_task():
            try:
                audio_extraction_time, video = extract_audio(self.video_file, "extracted_audio.wav")
                tts_generation_time = generate_tts_audio(self.textbox.get(), "extracted_audio.wav", self.rough_tts_output_file, self.device)
                initial_cleaning(self.rough_tts_output_file, self.tts_output_file)
                audio_replacement_time, video_with_new_audio = replace_audio_in_video(video, self.tts_output_file, self.output_video_file)

                total_processing_time = audio_extraction_time + tts_generation_time + audio_replacement_time
                real_time_factor = total_processing_time / video_with_new_audio.duration

                print(f"Processing completed in {total_processing_time:.2f} seconds.")
                print(f"Real-time factor: {real_time_factor:.2f}")
            except Exception as e:
                print(f"Error during processing: {e}")

        Thread(target=process_task).start()

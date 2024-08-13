import customtkinter as ctk
from tkinter import filedialog
from threading import Thread
from processing.video import extract_audio, replace_audio_in_video
from processing.audio import generate_tts_audio
from post_processing.cleaning import initial_cleaning
import os
import torch
from time import time
from datetime import datetime


class DeepFakeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DeepFake Video Processor")
        self.root.geometry("600x500")

        self.video_file = ""
        self.rough_tts_output_file = "rough_tts_output.mp3"
        self.tts_output_file = "tts_output.wav"
        self.output_video_file_template = "output_video_{iteration}.mp4"

        self.setup_ui()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Use GPU if available, otherwise fallback to CPU
        print("Using device: {}".format(self.device))

    def setup_ui(self):
        # Set up the UI components for the application
        self.label_video = ctk.CTkLabel(self.root, text="Video File:")
        self.label_video.pack(pady=10)
        self.button_video = ctk.CTkButton(self.root, text="Select Video File", command=self.select_video_file)
        self.button_video.pack(pady=10)

        self.textbox = ctk.CTkEntry(self.root, width=400, placeholder_text="Enter text for TTS")
        self.textbox.pack(pady=10)

        self.label_iterations = ctk.CTkLabel(self.root, text="Number of Iterations:")
        self.label_iterations.pack(pady=10)
        self.entry_iterations = ctk.CTkEntry(self.root, width=100, placeholder_text="1")
        self.entry_iterations.pack(pady=10)

        self.button_process = ctk.CTkButton(self.root, text="Process", command=self.process_video)
        self.button_process.pack(pady=10)

    def select_video_file(self):
        # Open file dialog to select a video file
        self.video_file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        self.label_video.configure(text=f"Video File: {os.path.basename(self.video_file)}")

    def process_video(self):
        # Validate input fields before starting the process
        if not self.video_file or not self.textbox.get() or not self.entry_iterations.get().isdigit():
            print("Please select a video file, enter text for TTS, and specify the number of iterations.")
            return

        iterations = int(self.entry_iterations.get())

        def process_task():
            try:
                base_video_file = os.path.basename(self.video_file)

                extracted_audio_filename = "tmp/" + base_video_file + "-extracted_audio.wav"
                # Extract audio from the selected video file
                audio_extraction_time, video = extract_audio(self.video_file, extracted_audio_filename)


                for iteration in range(iterations):
                    total_time = 0
                    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                    tts_output_file = f"tmp/tts_{date_str}_{base_video_file}_{iteration}.wav"
                    output_video_file = f"output/video_{base_video_file}_{iteration}_{date_str}.mp4"
                    start_time = time()

                    # Generate TTS audio from text input
                    tts_generation_time = generate_tts_audio(self.textbox.get(), extracted_audio_filename, tts_output_file, self.device)
                    # Clean the generated TTS audio
                    initial_cleaning(tts_output_file, self.tts_output_file)
                    # Replace the original video audio with the new TTS audio
                    audio_replacement_time, video_with_new_audio = replace_audio_in_video(video, self.tts_output_file, output_video_file)

                    iteration_time = time() - start_time
                    total_time += iteration_time

                    total_processing_time = audio_extraction_time + tts_generation_time + audio_replacement_time
                    real_time_factor = total_processing_time / video_with_new_audio.duration

                    print(f"Iteration {iteration + 1} completed in {total_processing_time:.2f} seconds.")
                    print(f"Real-time factor: {real_time_factor:.2f}")
                    estimated_total_time = total_time * iterations
                    estimated_remaining_time = estimated_total_time - total_time
                    print(f"\033[94mEstimated total time for {iterations} iterations: {estimated_total_time:.2f} seconds\033[0m")
                    print(f"\033[94mEstimated remaining time: {estimated_remaining_time:.2f} seconds\033[0m")

            except Exception as e:
                print(f"Error during processing: {e}")

        # Start the processing in a new thread to keep the UI responsive
        Thread(target=process_task).start()

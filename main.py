import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from time import time
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from TTS.api import TTS
import torch
from cleaning import initial_cleaning

class VideoAudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Audio Processor")
        self.root.geometry("600x400")

        self.video_file = ""
        self.rough_tts_output_file = "rough_tts_output.mp3"
        self.tts_output_file = "tts_output.wav"
        self.output_video_file = "output_video.mp4"

        self.label_video = ctk.CTkLabel(root, text="Video File:")
        self.label_video.pack(pady=10)
        self.button_video = ctk.CTkButton(root, text="Select Video File", command=self.select_video_file)
        self.button_video.pack(pady=10)

        self.textbox = ctk.CTkEntry(root, width=400, placeholder_text="Enter text for TTS")
        self.textbox.pack(pady=10)

        self.button_process = ctk.CTkButton(root, text="Process", command=self.process_video)
        self.button_process.pack(pady=10)

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def select_video_file(self):
        self.video_file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        self.label_video.configure(text=f"Video File: {os.path.basename(self.video_file)}")

    def process_video(self):
        if not self.video_file or not self.textbox.get():
            print("Please select a video file and enter text for TTS.")
            return

        def extract_audio(video_file, extracted_audio_file):
            start_time = time()
            video = VideoFileClip(video_file)
            audio = video.audio
            audio.write_audiofile(extracted_audio_file)
            end_time = time()
            return end_time - start_time, video

        def generate_tts_audio(text, extracted_audio_file, tts_output_file):
            start_time = time()

            # Good enough at times, but a lot of kinks and artefacts remain to iron out.
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(self.device)
            tts.tts_to_file(text=text, speaker_wav=extracted_audio_file, file_path=tts_output_file, language='en')

            # Great quality output but the accent is out of bounds.
            #tts = TTS(model_name="tts_models/fr/css10/vits", progress_bar=True).to(self.device)
            #tts.tts_to_file(text=text, speaker_wav=extracted_audio_file, file_path=tts_output_file)

            end_time = time()
            return end_time - start_time

        def replace_audio_in_video(video, tts_output_file, output_video_file):
            start_time = time()
            new_audio = AudioFileClip(tts_output_file)

            if new_audio.duration < video.duration:
                loops = int(video.duration // new_audio.duration) + 1
                new_audio = concatenate_audioclips([new_audio] * loops).subclip(0, video.duration)
            else:
                new_audio = new_audio.subclip(0, video.duration)

            video_with_new_audio = video.set_audio(new_audio)
            video_with_new_audio.write_videofile(output_video_file, codec="libx264", audio_codec="aac")
            end_time = time()
            return end_time - start_time, video_with_new_audio

        def process_task():
            try:
                audio_extraction_time, video = extract_audio(self.video_file, "extracted_audio.wav")
                tts_generation_time = generate_tts_audio(self.textbox.get(), "extracted_audio.wav", self.rough_tts_output_file)
                initial_cleaning(self.rough_tts_output_file, self.tts_output_file)
                audio_replacement_time, video_with_new_audio = replace_audio_in_video(video, self.tts_output_file, self.output_video_file)

                total_processing_time = audio_extraction_time + tts_generation_time + audio_replacement_time
                real_time_factor = total_processing_time / video_with_new_audio.duration

                print(f"Processing completed in {total_processing_time:.2f} seconds.")
                print(f"Real-time factor: {real_time_factor:.2f}")
            except Exception as e:
                print(f"Error during processing: {e}")

        threading.Thread(target=process_task).start()

if __name__ == "__main__":
    root = ctk.CTk()
    app = VideoAudioApp(root)
    root.mainloop()

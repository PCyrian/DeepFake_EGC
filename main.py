import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from TTS.api import TTS
import torch

class VideoAudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Audio Processor")
        self.root.geometry("600x400")

        self.video_file = ""
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

    def select_video_file(self):
        self.video_file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        self.label_video.configure(text=f"Video File: {os.path.basename(self.video_file)}")

    def process_video(self):
        if not self.video_file or not self.textbox.get():
            print("Please select a video file and enter text for TTS.")
            return

        def process_task():
            try:
                video = VideoFileClip(self.video_file)
                audio = video.audio
                extracted_audio_file = "extracted_audio.wav"
                audio.write_audiofile(extracted_audio_file)

                tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=True).to('cuda' if torch.cuda.is_available() else 'cpu')
                text = self.textbox.get()
                tts.tts_to_file(text=text, speaker_wav=extracted_audio_file, file_path=self.tts_output_file, language="fr-fr")

                new_audio = AudioFileClip(self.tts_output_file)

                if new_audio.duration < video.duration:
                    loops = int(video.duration // new_audio.duration) + 1
                    new_audio = concatenate_audioclips([new_audio] * loops).subclip(0, video.duration)
                else:
                    new_audio = new_audio.subclip(0, video.duration)

                video_with_new_audio = video.set_audio(new_audio)
                video_with_new_audio.write_videofile(self.output_video_file, codec="libx264", audio_codec="aac")
                print("Processing completed.")
            except Exception as e:
                print(f"Error during processing: {e}")

        threading.Thread(target=process_task).start()


if __name__ == "__main__":
    root = ctk.CTk()
    app = VideoAudioApp(root)
    root.mainloop()

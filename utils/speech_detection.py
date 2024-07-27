from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from moviepy.editor import VideoFileClip
import os


def detect_speech_start(mp4_file_path, min_speech_duration=1):
    video = VideoFileClip(mp4_file_path)
    audio = video.audio
    audio_file_path = "temp_audio.wav"
    audio.write_audiofile(audio_file_path)
    audio = AudioSegment.from_wav(audio_file_path)
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)
    recognizer = sr.Recognizer()

    current_time = 0
    for chunk in chunks:
        chunk_duration = len(chunk) / 1000
        if chunk_duration >= min_speech_duration:
            with chunk.export(format="wav") as chunk_file:
                with sr.AudioFile(chunk_file) as source:
                    audio_data = recognizer.record(source)
                    try:
                        recognizer.recognize_google(audio_data)
                        print(f"Speech starts at {current_time:.2f} seconds")
                        os.remove(audio_file_path)
                        return current_time
                    except sr.UnknownValueError:
                        pass

        current_time += chunk_duration

    os.remove(audio_file_path)
    print("No speech detected with the specified duration.")
    return None


test_filepath = "D:/test_file0.mp4"
detect_speech_start(test_filepath, 2)

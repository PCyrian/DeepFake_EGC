from TTS.api import TTS
from time import time

def generate_tts_audio(text, extracted_audio_file, tts_output_file, device):
    start_time = time()

    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)
    tts.tts_to_file(text=text, speaker_wav=extracted_audio_file, file_path=tts_output_file, language='en')

    end_time = time()
    return end_time - start_time

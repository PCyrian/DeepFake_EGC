try:
    import ctypes
    print("ctypes imported successfully.")
except Exception as e:
    print(f"Failed to import ctypes: {e}")

try:
    import os
    print("os imported successfully.")
except Exception as e:
    print(f"Failed to import os: {e}")

try:
    import torch
    print("torch imported successfully.")
except Exception as e:
    print(f"Failed to import torch: {e}")

try:
    import whisper
    print("whisper imported successfully.")
except Exception as e:
    print(f"Failed to import whisper: {e}")

import threading


def run_local_whisper(mp3_filename):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("CUDA Available:", torch.cuda.is_available())
    print("CUDA Device Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU detected")

    model = whisper.load_model(name="base", device=device)
    audio = whisper.load_audio(mp3_filename)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    return result.text

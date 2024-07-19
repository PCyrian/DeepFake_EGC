import librosa
import soundfile as sf
import torch
import threading
import os
import numpy as np
from time import time

def initial_cleaning(input_file, output_file):
    start_time = time()
    y, sr = librosa.load(input_file, sr=None)
    y_smoothed = librosa.effects.time_stretch(y, rate=1.0)
    sf.write(output_file, y_smoothed, sr)
    end_time = time()
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Initial cleaning completed in {end_time - start_time:.2f} seconds.")
    print(f"Real-time factor: {(end_time - start_time) / duration:.2f}")

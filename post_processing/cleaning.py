import librosa
import soundfile as sf

def initial_cleaning(input_file, output_file):
    y, sr = librosa.load(input_file, sr=None)
    y_smoothed = librosa.effects.preemphasis(y)
    sf.write(output_file, y_smoothed, sr)

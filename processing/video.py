from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from time import time

def extract_audio(video_file, extracted_audio_file):
    start_time = time()
    video = VideoFileClip(video_file)
    audio = video.audio
    audio.write_audiofile(extracted_audio_file)
    end_time = time()
    return end_time - start_time, video

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

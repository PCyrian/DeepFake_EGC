import subprocess
import os


def run_video_retalking(video_file, audio_file, output_file):
    # Define the paths inside the container
    container_video_path = '/video-retalking/examples/face/input_video.mp4'
    container_audio_path = '/video-retalking/examples/audio/input_audio.wav'

    # Define the output directory inside the container and host
    container_output_dir = '/video-retalking/results'
    host_output_dir = os.path.dirname(output_file)

    container_name = "video_retalking-image"

    # Build the Docker command to run the container
    command = [
        "docker", "run", "--rm", "--gpus", "all",
        "--name", container_name,
        "-v", f"{video_file}:{container_video_path}",
        "-v", f"{audio_file}:{container_audio_path}",
        "-v", f"{host_output_dir}:{container_output_dir}",
        "video_retalking-image",
        "python3", "inference.py",
        "--face", container_video_path,
        "--audio", container_audio_path,
        "--outfile", f"{container_output_dir}/output.mp4"
    ]

    subprocess.run(command)

    print(f"Output video saved at: {output_file}")


video_file = "C:/Users/cyria/PycharmProjects/DockerFiles/Pujadas.mp4"
audio_file = "C:/Users/cyria/PycharmProjects/DockerFiles/EGC_speech.wav"
output_file = "C:/Users/cyria/PycharmProjects/DockerFiles/results/result_puja.mp4"

run_video_retalking(video_file, audio_file, output_file)

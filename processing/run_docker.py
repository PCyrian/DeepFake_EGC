import os
import subprocess
import time


def concatenate_videos(video_a, video_b, output_file):
    try:
        # Create a temporary text file with the paths of videos to concatenate because that's what ffmpeg expects
        concat_file_path = os.path.join(os.path.dirname(output_file), "concat_list.txt")
        with open(concat_file_path, "w") as f:
            f.write(f"file '{os.path.abspath(video_a)}'\n")
            f.write(f"file '{os.path.abspath(video_b)}'\n")

        # Build the ffmpeg command to concatenate the videos
        ffmpeg_command = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file_path,
            "-c", "copy", output_file
        ]

        # Capture output with UTF-8 encoding to prevent UnicodeDecodeError
        result = subprocess.run(ffmpeg_command, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError(f"Error during video concatenation: {result.stderr}")

        # Clean up the temporary file
        os.remove(concat_file_path)

        # Check if the output file was created and its size to avoid empty files
        if os.path.exists(output_file) and os.path.getsize(output_file) > 10240:  # 10KB size check
            print(f"Concatenated video successfully saved at: {output_file}")
            return True
        else:
            raise RuntimeError("Concatenation failed or output file is too small.")

    except Exception as e:
        print(f"Error in concatenating videos: {str(e)}")
        return False


def run_video_retalking(video_file, audio_file, output_file):
    start_time = time.time()

    # Define the paths inside the container
    container_video_path = '/video-retalking/examples/face/input_video.mp4'
    container_audio_path = '/video-retalking/examples/audio/input_audio.wav'

    # Get the host output directory and output file name
    host_output_dir = os.path.dirname(output_file)
    output_file_name = os.path.basename(output_file)

    # Define the output path inside the container, using the user-specified file name
    container_output_path = f"/video-retalking/results/{output_file_name}"

    container_name = "video_retalking-image"

    # Build the Docker command to run the container
    command = [
        "docker", "run", "--rm", "--gpus", "all",
        "--name", container_name,
        "-v", f"{os.path.abspath(video_file)}:{container_video_path}",
        "-v", f"{os.path.abspath(audio_file)}:{container_audio_path}",
        "-v", f"{os.path.abspath(host_output_dir)}:/video-retalking/results",
        "video_retalking-image",
        "python3", "inference.py",
        "--face", container_video_path,
        "--audio", container_audio_path,
        "--outfile", container_output_path
    ]

    try:
        # Run the command and output real-time logs
        result = subprocess.run(command, check=True)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Process completed in : {elapsed_time:.2f} seconds")
        print(f"Output video saved at: {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error in video retalking process: {e}")


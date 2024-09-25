import os
import copy
import logging
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Tuple
import torch
import gradio as gr
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.fx.resize import resize
from processing import audio
from processing.run_docker import run_video_retalking

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_video(
    video_file: gr.File,
    tts_text: str,
    use_video_audio: bool,
    audio_file: Optional[gr.File],
    iterations: int,
    archive_folder: str,
    downscale_percentage: int,
    task_name: str,
    task_list: List[Dict[str, Any]],
    task_index: int
) -> Generator[Tuple[List[Dict[str, Any]], str, Optional[str], gr.update, Optional[List[str]]], None, None]:
    """
    Processes a video by lip-syncing it with generated TTS audio.

    Yields:
        A tuple containing updated task list, status message, output video file path,
        updated task list display data, and a list of output files.
    """
    updated_task_list = copy.deepcopy(task_list)
    all_output_files = []

    if not video_file or not tts_text or not iterations:
        task_list_display = [[t['task_name'], t['status']] for t in updated_task_list]
        yield updated_task_list, f"Task '{task_name}': Please provide all inputs.", None, gr.update(value=task_list_display), None
        return

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logging.info(f"Task '{task_name}': Using device: {device}")

    video_file_path = video_file.name

    if not use_video_audio and not audio_file:
        task_list_display = [[t['task_name'], t['status']] for t in updated_task_list]
        yield updated_task_list, f"Task '{task_name}': Please provide an audio file or select 'Use Audio from Video'.", None, gr.update(value=task_list_display), None
        return

    def extract_audio(video_path: str) -> Optional[str]:
        """
        Extracts audio from the given video file.

        Args:
            video_path: Path to the video file.

        Returns:
            Path to the extracted audio file or None if extraction fails.
        """
        try:
            clip = VideoFileClip(video_path)
            audio_path = video_path.replace(".mp4", "_extracted.wav")
            clip.audio.write_audiofile(audio_path)
            return audio_path
        except Exception as e:
            logging.error(f"Task '{task_name}': Error extracting audio: {e}")
            return None

    try:
        # Update task status to "Processing"
        updated_task_list[task_index]['status'] = "Processing"
        task_list_display = [[t['task_name'], t['status']] for t in updated_task_list]
        yield updated_task_list, f"Task '{task_name}': Starting processing...", None, gr.update(value=task_list_display), None

        # Ensure archive folder exists or set to current working directory
        if archive_folder:
            os.makedirs(archive_folder, exist_ok=True)
        else:
            archive_folder = os.getcwd()

        extracted_audio_file = extract_audio(video_file_path) if use_video_audio else audio_file.name

        if not extracted_audio_file:
            logging.error(f"Task '{task_name}': Failed to obtain audio.")
            updated_task_list[task_index]['status'] = "Error"
            task_list_display = [[t['task_name'], t['status']] for t in updated_task_list]
            yield updated_task_list, f"Task '{task_name}': Failed to obtain audio.", None, gr.update(value=task_list_display), None
            return

        input_video_basename = os.path.splitext(os.path.basename(video_file_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if downscale_percentage < 100:
            task_msg = f"Task '{task_name}': Downscaling video to {downscale_percentage}%..."
            yield updated_task_list, task_msg, None, gr.update(value=task_list_display), None
            original_clip = VideoFileClip(video_file_path)
            downscale_factor = downscale_percentage / 100.0
            downscaled_clip = original_clip.fx(resize, downscale_factor)
            downscaled_video_file = os.path.join(archive_folder, f"{input_video_basename}_downscaled_{timestamp}.mp4")
            downscaled_clip.write_videofile(downscaled_video_file, codec='libx264')
            video_file_path = downscaled_video_file
            original_resolution = (original_clip.w, original_clip.h)
        else:
            original_resolution = None

        output_video_files = []

        for iteration in range(iterations):
            tts_output_file = os.path.join(archive_folder, f"{input_video_basename}_generated_audio_{timestamp}_{iteration}.wav")
            output_video_file = os.path.join(archive_folder, f"{input_video_basename}_output_video_{timestamp}_{iteration}.mp4")

            status_msg = f"Task '{task_name}': Synthesizing speech (Iteration {iteration + 1}/{iterations})..."
            yield updated_task_list, status_msg, None, gr.update(value=task_list_display), None
            audio.generate_tts_audio(tts_text, extracted_audio_file, tts_output_file, device)

            status_msg = f"Task '{task_name}': Lip syncing in progress (Iteration {iteration + 1}/{iterations})..."
            yield updated_task_list, status_msg, None, gr.update(value=task_list_display), None
            run_video_retalking(video_file_path, tts_output_file, output_video_file)
            logging.info(f"Task '{task_name}': Lip-synced video {iteration + 1}/{iterations} saved to {output_video_file}")

            output_video_files.append(output_video_file)
            all_output_files.append(output_video_file)

        status_msg = f"Task '{task_name}': Concatenating videos for comparison..."
        yield updated_task_list, status_msg, None, gr.update(value=task_list_display), None

        clips = []
        for output_video_file in output_video_files:
            clip = VideoFileClip(output_video_file)
            if original_resolution:
                status_msg = f"Task '{task_name}': Upscaling video to original resolution..."
                yield updated_task_list, status_msg, None, gr.update(value=task_list_display), None
                clip = clip.resize(newsize=original_resolution)
            clips.append(clip)

        original_clip = VideoFileClip(video_file.name)
        clips.append(original_clip)
        final_clip = concatenate_videoclips(clips)
        comparison_video_file = os.path.join(archive_folder, f"{input_video_basename}_comparison_video_{timestamp}.mp4")
        final_clip.write_videofile(comparison_video_file, codec='libx264')
        all_output_files.append(comparison_video_file)

        all_output_files = [os.path.abspath(file) for file in all_output_files]

        # Update task status to "Completed"
        updated_task_list[task_index]['status'] = "Completed"
        task_list_display = [[t['task_name'], t['status']] for t in updated_task_list]
        yield updated_task_list, f"Task '{task_name}': Processing complete!", comparison_video_file, gr.update(value=task_list_display), all_output_files

    except Exception as e:
        logging.error(f"Task '{task_name}': Error during processing: {e}")
        updated_task_list[task_index]['status'] = "Error"
        task_list_display = [[t['task_name'], t['status']] for t in updated_task_list]
        yield updated_task_list, f"Task '{task_name}': Error during processing: {e}", None, gr.update(value=task_list_display), None


def build_ui() -> gr.Blocks:
    """
    Builds the Gradio user interface for the lip-sync processor.

    Returns:
        A Gradio Blocks object representing the UI.
    """
    with gr.Blocks(title="DeepFake EGC") as demo:
        gr.Markdown("# DeepFake EGC")

        with gr.Row():
            with gr.Column():
                task_name = gr.Textbox(label="Task Name", placeholder="Enter a name for this task")
                video_file = gr.File(label="Select Face File (MP4 or Image)", file_types=['video', 'image'])
                tts_text = gr.Textbox(label="Enter text for TTS", placeholder="Enter text for TTS", lines=5)
                use_video_audio = gr.Checkbox(label="Use Audio from Video", value=True)
                audio_file = gr.File(label="Select Audio File", file_types=['audio'], visible=False)
                iterations = gr.Number(label="Number of Iterations", value=1, precision=0, minimum=1)
                downscale_percentage = gr.Slider(
                    label="Downscale Percentage",
                    minimum=10,
                    maximum=100,
                    value=100,
                    step=1,
                    info="Select the percentage to downscale the video. Processed video will be upscaled back to original resolution."
                )
                archive_folder = gr.Textbox(
                    label="Archive Folder Path",
                    placeholder="Enter the path to the archive folder",
                    value=os.getcwd()
                )
                add_task_button = gr.Button("Add Task")
                start_processing_button = gr.Button("Start Processing Tasks")
            with gr.Column():
                task_list = gr.State([])
                gr.Markdown("## Task Scheduler")
                task_list_display = gr.Dataframe(
                    headers=["Task Name", "Status"],
                    datatype=["str", "str"],
                    interactive=False,
                    value=[]
                )
                output_message = gr.Textbox(label="Status", interactive=False)
                output_video = gr.Video(label="Output Video")
                output_files = gr.File(label="Download Output Files", file_count="multiple")

        def toggle_audio_input(use_audio: bool) -> gr.update:
            """
            Toggles the visibility of the audio file input based on the checkbox.

            Args:
                use_audio: Boolean indicating whether to use video audio.

            Returns:
                An update object for the audio file component's visibility.
            """
            return gr.update(visible=not use_audio)

        # Set initial visibility of the audio file input
        audio_file.visible = not use_video_audio.value

        # Update visibility when the checkbox value changes
        use_video_audio.change(fn=toggle_audio_input, inputs=use_video_audio, outputs=audio_file)

        def add_task(
            name: str,
            video: Optional[gr.File],
            text: str,
            use_audio: bool,
            audio: Optional[gr.File],
            iter_count: float,
            archive: str,
            downscale: float,
            current_tasks: List[Dict[str, Any]]
        ) -> Tuple[List[Dict[str, Any]], gr.update]:
            """
            Adds a new task to the task list.

            Args:
                name: Name of the task.
                video: Video file input.
                text: Text for TTS.
                use_audio: Whether to use audio from video.
                audio: Audio file input.
                iter_count: Number of iterations.
                archive: Archive folder path.
                downscale: Downscale percentage.
                current_tasks: Current list of tasks.

            Returns:
                Updated task list and updated task list display data.
            """
            updated_tasks = copy.deepcopy(current_tasks)

            if not name:
                name = f"Task_{len(updated_tasks) + 1}"

            task = {
                'task_name': name,
                'video_file': video,
                'tts_text': text,
                'use_video_audio': use_audio,
                'audio_file': audio,
                'iterations': int(iter_count),
                'archive_folder': archive,
                'downscale_percentage': int(downscale),
                'status': 'Pending'
            }
            updated_tasks.append(task)
            display_data = [[t['task_name'], t['status']] for t in updated_tasks]
            return updated_tasks, gr.update(value=display_data)

        add_task_button.click(
            fn=add_task,
            inputs=[
                task_name, video_file, tts_text, use_video_audio, audio_file,
                iterations, archive_folder, downscale_percentage, task_list
            ],
            outputs=[task_list, task_list_display]
        )

        def start_processing(task_list_input: List[Dict[str, Any]]) -> Generator[Tuple[List[Dict[str, Any]], str, Optional[str], gr.update, Optional[List[str]]], None, None]:
            """
            Processes all tasks in the task list.

            Args:
                task_list_input: List of tasks to process.

            Yields:
                Updated task list, status message, output video, task list display, and output files.
            """
            if not task_list_input:
                yield task_list_input, "No tasks to process.", None, gr.update(), None
                return

            accumulated_output_files = []
            for index, task in enumerate(task_list_input):
                task_params = {
                    'video_file': task['video_file'],
                    'tts_text': task['tts_text'],
                    'use_video_audio': task['use_video_audio'],
                    'audio_file': task['audio_file'],
                    'iterations': task['iterations'],
                    'archive_folder': task['archive_folder'],
                    'downscale_percentage': task['downscale_percentage'],
                    'task_name': task['task_name'],
                    'task_list': task_list_input,
                    'task_index': index
                }
                for outputs in process_video(**task_params):
                    updated_tasks, status_msg, output_video_file, display_data, output_files = outputs
                    if output_files:
                        accumulated_output_files.extend(output_files)
                    yield updated_tasks, status_msg, output_video_file, gr.update(value=display_data), accumulated_output_files if output_files else None

        start_processing_button.click(
            fn=start_processing,
            inputs=[task_list],
            outputs=[task_list, output_message, output_video, task_list_display, output_files]
        )

        gr.Examples(
            examples=[
                ["Bienvenue à cette belle conférence de 2023 sur le partage de savoir"],
                ["Bien le bonjour, ceci est un texte d'exemple."],
                ["On ne choisit jamais une voie en informatique car c'est facile, mais car on pensait que ça le serait."]
            ],
            inputs=tts_text,
            label="Example Texts for TTS"
        )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch()

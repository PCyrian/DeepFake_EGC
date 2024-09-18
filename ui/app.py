import gradio as gr
import torch
from processing.run_docker import run_video_retalking
from moviepy.editor import VideoFileClip, concatenate_videoclips
from processing import audio
import os
from datetime import datetime
from moviepy.video.fx.resize import resize  # Corrected import

def process_video(
    video_file, tts_text, use_video_audio, audio_file, iterations,
    archive_folder, downscale_percentage, task_name, task_list, task_index
):
    if not video_file or not tts_text or not iterations:
        yield task_list, f"Task '{task_name}': Please provide all inputs.", None, None
        return

    iterations = int(iterations)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Task '{task_name}': Using device: {device}")

    video_file_path = video_file.name

    if not use_video_audio and not audio_file:
        yield task_list, f"Task '{task_name}': Please provide an audio file or select 'Use Audio from Video'.", None, None
        return

    def extract_audio(video_file_path):
        try:
            clip = VideoFileClip(video_file_path)
            audio_file = video_file_path.replace(".mp4", "_extracted.wav")
            clip.audio.write_audiofile(audio_file)
            return audio_file
        except Exception as e:
            print(f"Task '{task_name}': Error extracting audio: {e}")
            return None

    try:
        # Update task status to "Processing"
        task_list[task_index]['status'] = "Processing"
        task_list_display_data = [[t['task_name'], t['status']] for t in task_list]
        yield task_list, f"Task '{task_name}': Starting processing...", None, gr.update(value=task_list_display_data)

        extracted_audio_file = None

        # Get base name of the input video file
        input_video_basename = os.path.splitext(os.path.basename(video_file_path))[0]

        # Generate a timestamp for unique file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ensure archive folder exists
        if archive_folder:
            os.makedirs(archive_folder, exist_ok=True)
        else:
            archive_folder = os.getcwd()

        # Step 1: Extract or use provided audio
        if use_video_audio:
            yield task_list, f"Task '{task_name}': Extracting audio from video...", None, gr.update(value=task_list_display_data)
            extracted_audio_file = extract_audio(video_file_path)
        else:
            extracted_audio_file = audio_file.name

        if not extracted_audio_file:
            print(f"Task '{task_name}': Failed to obtain audio.")
            task_list[task_index]['status'] = "Error"
            task_list_display_data = [[t['task_name'], t['status']] for t in task_list]
            yield task_list, f"Task '{task_name}': Failed to obtain audio.", None, gr.update(value=task_list_display_data)
            return

        # Step 2: Downscale video if required
        if downscale_percentage < 100:
            yield task_list, f"Task '{task_name}': Downscaling video to {downscale_percentage}%...", None, gr.update(value=task_list_display_data)
            original_clip = VideoFileClip(video_file_path)
            downscale_factor = downscale_percentage / 100.0
            downscaled_clip = original_clip.fx(resize, downscale_factor)
            downscaled_video_file = os.path.join(
                archive_folder,
                f"{input_video_basename}_downscaled_{timestamp}.mp4"
            )
            downscaled_clip.write_videofile(downscaled_video_file, codec='libx264')
            video_file_path = downscaled_video_file
            original_resolution = (original_clip.w, original_clip.h)
        else:
            original_resolution = None  # No need to upscale later

        output_video_files = []

        # Step 3: Iterate over the number of times specified
        for iteration in range(iterations):
            tts_output_file = os.path.join(
                archive_folder,
                f"{input_video_basename}_generated_audio_{timestamp}_{iteration}.wav"
            )
            output_video_file = os.path.join(
                archive_folder,
                f"{input_video_basename}_output_video_{timestamp}_{iteration}.mp4"
            )

            # Step 4: Generate TTS audio
            yield task_list, f"Task '{task_name}': Synthesizing speech...", None, gr.update(value=task_list_display_data)
            audio.generate_tts_audio(tts_text, extracted_audio_file, tts_output_file, device)

            # Step 5: Lip sync with new audio
            yield task_list, f"Task '{task_name}': Lip syncing in progress...", None, gr.update(value=task_list_display_data)
            run_video_retalking(video_file_path, tts_output_file, output_video_file)
            print(f"Task '{task_name}': Lip-synced video {iteration + 1}/{iterations} saved to {output_video_file}")

            output_video_files.append(output_video_file)

        # Step 6: Concatenate the new video with the original one
        yield task_list, f"Task '{task_name}': Concatenating videos for comparison...", None, gr.update(value=task_list_display_data)
        clips = []
        for output_video_file in output_video_files:
            clip = VideoFileClip(output_video_file)
            if original_resolution:
                # Upscale back to original resolution
                yield task_list, f"Task '{task_name}': Upscaling video to original resolution...", None, gr.update(value=task_list_display_data)
                clip = clip.fx(resize, original_resolution)
            clips.append(clip)
        original_clip = VideoFileClip(video_file.name)
        clips.append(original_clip)
        final_clip = concatenate_videoclips(clips)
        comparison_video_file = os.path.join(
            archive_folder,
            f"{input_video_basename}_comparison_video_{timestamp}.mp4"
        )
        final_clip.write_videofile(comparison_video_file, codec='libx264')

        task_list[task_index]['status'] = "Completed"
        task_list_display_data = [[t['task_name'], t['status']] for t in task_list]
        yield task_list, f"Task '{task_name}': Processing complete!", comparison_video_file, gr.update(value=task_list_display_data)

    except Exception as e:
        print(f"Task '{task_name}': Error during processing: {e}")
        task_list[task_index]['status'] = "Error"
        task_list_display_data = [[t['task_name'], t['status']] for t in task_list]
        yield task_list, f"Task '{task_name}': Error during processing: {e}", None, gr.update(value=task_list_display_data)

def build_ui():
    with gr.Blocks(title="Lip Sync Processor") as demo:
        gr.Markdown("# Lip Sync Processor")

        with gr.Row():
            with gr.Column():
                task_name = gr.Textbox(label="Task Name", placeholder="Enter a name for this task")
                video_file = gr.File(label="Select Face File (MP4 or Image)", file_types=['video', 'image'])
                tts_text = gr.Textbox(
                    label="Enter text for TTS",
                    placeholder="Enter text for TTS",
                    lines=5
                )
                use_video_audio = gr.Checkbox(label="Use Audio from Video", value=True)
                audio_file = gr.File(label="Select Audio File", file_types=['audio'], visible=False)
                iterations = gr.Number(label="Number of Iterations", value=1, precision=0)
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
                    placeholder="Enter the path to the archive folder"
                )
                add_task_button = gr.Button("Add Task")
                start_processing_button = gr.Button("Start Processing Tasks")
            with gr.Column():
                task_list = gr.State([])
                task_list_display = gr.Dataframe(
                    headers=["Task Name", "Status"],
                    datatype=["str", "str"],
                    interactive=False,
                    value=[]
                )
                output_message = gr.Textbox(label="Status", interactive=False)
                output_video = gr.Video(label="Output Video")

        def toggle_audio_input(use_video_audio_value):
            return gr.update(visible=not use_video_audio_value)

        audio_file.visibility = not use_video_audio.value

        use_video_audio.change(fn=toggle_audio_input, inputs=use_video_audio, outputs=audio_file)

        def add_task(
            task_name, video_file, tts_text, use_video_audio, audio_file,
            iterations, archive_folder, downscale_percentage, task_list
        ):
            if not task_name:
                task_name = f"Task_{len(task_list)+1}"
            task = {
                'task_name': task_name,
                'video_file': video_file,
                'tts_text': tts_text,
                'use_video_audio': use_video_audio,
                'audio_file': audio_file,
                'iterations': iterations,
                'archive_folder': archive_folder,
                'downscale_percentage': downscale_percentage,
                'status': 'Pending'
            }
            task_list.append(task)
            task_list_display_data = [[t['task_name'], t['status']] for t in task_list]
            return task_list, gr.update(value=task_list_display_data)

        add_task_button.click(
            fn=add_task,
            inputs=[
                task_name, video_file, tts_text, use_video_audio, audio_file,
                iterations, archive_folder, downscale_percentage, task_list
            ],
            outputs=[task_list, task_list_display]
        )

        def start_processing(task_list):
            if not task_list:
                yield task_list, "No tasks to process.", None, gr.update()
                return
            for index, task in enumerate(task_list):
                task['task_index'] = index
                task_params = {k: v for k, v in task.items() if k not in ('status', 'task_index')}
                for outputs in process_video(**task_params, task_list=task_list, task_index=index):
                    yield outputs

        start_processing_button.click(
            fn=start_processing,
            inputs=[task_list],
            outputs=[task_list, output_message, output_video, task_list_display]
        )

        gr.Examples(
            examples=[
                ["Bienvenue à cette belle conférence de 2023 sur le partage de savoir"],
                ["Bien le bonjour, ceci est un text d'exemple."],
                ["On ne choisit jamais une voie en informatique car c'est facile, mais car on pensait que ça le serait."]
            ],
            inputs=tts_text,
            label="Example Texts for TTS"
        )

    return demo

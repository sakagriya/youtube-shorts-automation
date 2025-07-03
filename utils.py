import requests
import os
import subprocess

def download_file(url, output_filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_filename

def apply_ducking(video_path, audio_path, output_path):
    ducked_audio = "ducked_audio.mp3"
    duck_command = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-filter_complex", "volume=enable='between(t,0,20)':volume=1.0,sidechaincompressor=threshold=-30dB:ratio=5",
        ducked_audio
    ]
    subprocess.run(duck_command, check=True)

    merge_command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", ducked_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        output_path
    ]
    subprocess.run(merge_command, check=True)

    os.remove(ducked_audio)

def add_watermark(video_path, username):
    temp_output = "watermarked.mp4"
    watermark_text = f"Sumber: @{username}"
    watermark_command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf",
        f"drawtext=text='{watermark_text}':fontcolor=white@0.8:fontsize=24:x=10:y=10:shadowcolor=black:shadowx=1:shadowy=1",
        "-codec:a", "copy",
        temp_output
    ]
    subprocess.run(watermark_command, check=True)
    os.replace(temp_output, video_path)

def add_subtitle(video_path, subtitle_text):
    temp_output = "with_subs.mp4"

    drawtext_filter = (
        f"drawtext=text='{subtitle_text}':"
        "fontcolor=white@0.9:"
        "fontsize=30:"
        "box=1:boxcolor=black@0.5:boxborderw=5:"
        "x=(w-text_w)/2:y=h-(text_h*2)"
    )

    subtitle_command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", drawtext_filter,
        "-c:a", "copy",
        temp_output
    ]
    subprocess.run(subtitle_command, check=True)
    os.replace(temp_output, video_path)

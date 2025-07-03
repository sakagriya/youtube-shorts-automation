import requests
import os
import subprocess

def download_file(url, output_filename):
    print(f"⬇️ Downloading from {url} to {output_filename}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("✅ Download selesai:", output_filename)
    return output_filename

def apply_ducking(video_path, audio_path, output_path):
    print("🎚️ Mulai proses ducking audio...")
    ducked_audio = "/tmp/ducked_audio.mp3"
    duck_command = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-filter_complex", "volume=enable='between(t,0,20)':volume=1.0,sidechaincompressor=threshold=-30dB:ratio=5",
        ducked_audio
    ]
    print("▶️ Duck command:", ' '.join(duck_command))
    try:
        subprocess.run(duck_command, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ Error saat ducking audio:", e)
        raise

    merge_command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", ducked_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        output_path
    ]
    print("▶️ Merge command:", ' '.join(merge_command))
    try:
        subprocess.run(merge_command, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ Error saat merge audio dan video:", e)
        raise

    os.remove(ducked_audio)
    print("✅ Ducking selesai:", output_path)

def add_watermark(video_path, username):
    print("💧 Menambahkan watermark...")
    temp_output = "/tmp/watermarked.mp4"
    watermark_text = f"Sumber: @{username}"
    watermark_command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf",
        f"drawtext=text='{watermark_text}':fontcolor=white@0.8:fontsize=24:x=10:y=10:shadowcolor=black:shadowx=1:shadowy=1",
        "-codec:a", "copy",
        temp_output
    ]
    print("▶️ Watermark command:", ' '.join(watermark_command))
    try:
        subprocess.run(watermark_command, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ Error saat menambahkan watermark:", e)
        raise

    os.replace(temp_output, video_path)
    print("✅ Watermark selesai")

def add_subtitle(video_path, subtitle_text):
    print("🔤 Menambahkan subtitle...")
    temp_output = "/tmp/with_subs.mp4"
    subtitle_command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"drawtext=text='{subtitle_text}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-60:shadowcolor=black:shadowx=2:shadowy=2",
        "-c:a", "copy",
        temp_output
    ]
    print("▶️ Subtitle command:", ' '.join(subtitle_command))
    try:
        subprocess.run(subtitle_command, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ Error saat menambahkan subtitle:", e)
        raise

    os.replace(temp_output, video_path)
    print("✅ Subtitle selesai")

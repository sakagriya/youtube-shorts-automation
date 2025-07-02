from flask import Flask, request, jsonify
from utils import download_file, apply_ducking, add_watermark, add_subtitle
from youtube_uploader import upload_to_youtube
import os
from moviepy.editor import VideoFileClip, AudioFileClip

app = Flask(__name__)

@app.route('/run', methods=['POST'])  # <- Ganti dari '/process' ke '/run'
def process_video():
    try:
        data = request.json
        video_path = None
        audio_path = None
        subtitle_text = data.get('subtitle_text', '')
        username = data.get('username', 'Unknown')
        output_path = '/output/final_output.mp4'

        # 1. Ambil Video
        if 'video_url' in data:
            video_path = '/tmp/input_video.mp4'
            download_file(data['video_url'], video_path)
        elif 'video_file' in request.files:
            video_file = request.files['video_file']
            video_path = '/tmp/input_video.mp4'
            video_file.save(video_path)
        else:
            return jsonify({'error': 'No video input provided.'}), 400

        # 2. Ambil Audio (Voice Over)
        if 'audio_url' in data:
            audio_path = '/tmp/input_audio.mp3'
            download_file(data['audio_url'], audio_path)
        elif 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            audio_path = '/tmp/input_audio.mp3'
            audio_file.save(audio_path)

        # 3. Load Video Clip
        video_clip = VideoFileClip(video_path)

        # 4. Apply Ducking
        if audio_path:
            ducked_video = apply_ducking(video_clip, audio_path)
        else:
            ducked_video = video_clip

        # 5. Tambah Watermark
        watermarked_video = add_watermark(ducked_video, username)

        # 6. Tambah Subtitle
        final_video = add_subtitle(watermarked_video, subtitle_text)

        # 7. Export Video
        os.makedirs('/output', exist_ok=True)
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

        # 8. Upload ke YouTube
        video_title = data.get('title', 'Automated YouTube Shorts')
        video_description = data.get('description', 'Uploaded via Automation')
        video_tags = data.get('tags', ['shorts'])

        youtube_url = upload_to_youtube(output_path, video_title, video_description, video_tags)

        return jsonify({'status': 'success', 'youtube_url': youtube_url})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from utils import download_file, apply_ducking, add_watermark, add_subtitle
from youtube_uploader import upload_video_to_youtube
import os
from moviepy.editor import VideoFileClip
from config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def process_video():
    try:
        data = request.json
        video_path = None
        audio_path = None
        subtitle_text = data.get('subtitle_text', '')
        username = data.get('username', 'Unknown')
        output_path = '/tmp/final_output.mp4'

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
            ducked_path = '/tmp/ducked_video.mp4'
            apply_ducking(video_path, audio_path, ducked_path)
        else:
            ducked_path = video_path

        # 5. Tambah Watermark
        add_watermark(ducked_path, username)

        # 6. Tambah Subtitle
        add_subtitle(ducked_path, subtitle_text)

        # 7. Rename ke final_output
        os.rename(ducked_path, output_path)

        # 8. Upload ke YouTube
        video_title = data.get('title', 'Automated YouTube Shorts')
        video_description = data.get('description', 'Uploaded via Automation')
        video_tags = data.get('tags', ['shorts'])

        youtube_response = upload_video_to_youtube(
            video_file_path=output_path,
            title=video_title,
            description=video_description,
            client_id=YOUTUBE_CLIENT_ID,
            client_secret=YOUTUBE_CLIENT_SECRET,
            refresh_token=YOUTUBE_REFRESH_TOKEN
        )

        return jsonify({'status': 'success', 'youtube_url': f"https://youtube.com/watch?v={youtube_response['id']}"})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

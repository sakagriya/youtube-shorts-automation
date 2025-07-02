from flask import Flask, request, jsonify
from utils import download_file, apply_ducking, add_watermark, add_subtitles
from youtube_uploader import upload_video_to_youtube
import os
from config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN

app = Flask(__name__)

OUTPUT_FOLDER = "./output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/process", methods=["POST"])
def process_video():
    try:
        data = request.json

        video_path = None
        audio_path = None
        subtitle_path = None
        username = data.get("username", "unknown")

        # ==== Handle Video ====
        if "video_url" in data:
            video_path = download_file(data["video_url"], "input_video.mp4")
        elif "video_file" in data:
            video_path = data["video_file"]
        else:
            return jsonify({"error": "No video_url or video_file provided"}), 400

        # ==== Handle Audio (VO) ====
        if "audio_url" in data:
            audio_path = download_file(data["audio_url"], "input_audio.mp3")
        elif "audio_file" in data:
            audio_path = data["audio_file"]
        else:
            return jsonify({"error": "No audio_url or audio_file provided"}), 400

        # ==== Handle Subtitle ====
        if "subtitle_text" in data:
            subtitle_path = os.path.join(OUTPUT_FOLDER, "subtitles.srt")
            with open(subtitle_path, "w", encoding="utf-8") as f:
                f.write(data["subtitle_text"])

        # ==== Process ====
        output_path = os.path.join(OUTPUT_FOLDER, "final_output.mp4")
        apply_ducking(video_path, audio_path, output_path)
        add_watermark(output_path, username)
        if subtitle_path:
            add_subtitles(output_path, subtitle_path)

        # ==== Upload to YouTube ====
        youtube_response = upload_video_to_youtube(
            output_path,
            title=data.get("youtube_title", "Automated Shorts"),
            description=data.get("youtube_description", ""),
            client_id=YOUTUBE_CLIENT_ID,
            client_secret=YOUTUBE_CLIENT_SECRET,
            refresh_token=YOUTUBE_REFRESH_TOKEN
        )

        return jsonify({
            "status": "success",
            "youtube_response": youtube_response
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

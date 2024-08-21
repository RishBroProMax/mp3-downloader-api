from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
from uuid import uuid4
from pathlib import Path

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_mp3():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400
    
    try:
        # Temporary directory for the MP3 file
        download_dir = Path('/tmp') / str(uuid4())
        download_dir.mkdir(parents=True, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(download_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3')

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup the downloaded file
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(download_dir):
            os.rmdir(download_dir)

# Vercel uses 'app' variable to detect the Flask app
if __name__ == '__main__':
    app.run(debug=True)

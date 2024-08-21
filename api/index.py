from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import os
import shutil
import youtube_dl

app = FastAPI()

@app.get("/download")
async def download(url: str = Query(..., title="YouTube Video URL", description="The URL of the YouTube video to download as MP3")):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        return FileResponse(title, media_type='audio/mpeg', filename=title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")
    finally:
        if os.path.exists(title):
            os.remove(title)

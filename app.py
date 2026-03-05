#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, threading, uuid
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

jobs = {}  # job_id -> status dict

HTML = open(os.path.join(os.path.dirname(__file__), 'index.html'), encoding='utf-8').read()

@app.route('/')
def index():
    return HTML

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url', '').strip()
    quality = data.get('quality', 'best')
    audio_only = data.get('audio_only', False)
    if not url:
        return jsonify({'error': 'לא הוזן קישור'}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'downloading', 'percent': '0%', 'speed': '', 'filename': '', 'error': ''}
    threading.Thread(target=do_download, args=(job_id, url, quality, audio_only), daemon=True).start()
    return jsonify({'job_id': job_id})

def do_download(job_id, url, quality, audio_only):
    try:
        import yt_dlp
        output_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

        def hook(d):
            if d['status'] == 'downloading':
                jobs[job_id]['percent'] = d.get('_percent_str', '0%').strip()
                jobs[job_id]['speed'] = d.get('_speed_str', '').strip()
            elif d['status'] == 'finished':
                jobs[job_id]['filename'] = os.path.basename(d['filename'])

        if audio_only:
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'progress_hooks': [hook],
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            }
        elif quality == 'best':
            opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'outtmpl': output_template, 'progress_hooks': [hook]}
        else:
            opts = {'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best', 'outtmpl': output_template, 'progress_hooks': [hook]}

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not jobs[job_id]['filename']:
                ext = 'mp3' if audio_only else 'mp4'
                jobs[job_id]['filename'] = f"{info.get('title','video')}.{ext}"

        jobs[job_id]['status'] = 'done'
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)

@app.route('/status/<job_id>')
def status(job_id):
    return jsonify(jobs.get(job_id, {'status': 'not_found'}))

@app.route('/file/<filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    print("האתר פועל על: http://localhost:5000")
    app.run(debug=False, port=5000)

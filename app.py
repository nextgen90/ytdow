import os
from flask import Flask, render_template, request, jsonify
from yt_dlp import YoutubeDL
from threading import Thread
from werkzeug.utils import secure_filename
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():  # Use 'home' instead of 'index' to avoid conflict
    return render_template("index.html")

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

video_info = {}

def download_video(url, path):
    global video_info
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info:
                video_info['title'] = info.get('title', 'Unknown')
                video_info['filepath'] = ydl.prepare_filename(info)
                video_info['size'] = round(os.path.getsize(video_info['filepath']) / 1024 / 1024, 2)
            else:
                video_info['title'] = 'Not Found'
                video_info['filepath'] = 'N/A'
                video_info['size'] = 0
    except Exception as e:
        video_info['title'] = 'Error'
        video_info['filepath'] = 'N/A'
        video_info['size'] = 0
        video_info['error'] = str(e)


def progress_hook(d):
    global video_info
    if d['status'] == 'downloading':
        video_info['downloaded'] = d.get('_percent_str', '0%')
        video_info['speed'] = d.get('_speed_str', '0 KB/s')
    elif d['status'] == 'finished':
        video_info['downloaded'] = '100%'
        video_info['speed'] = 'Done'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    global video_info
    url = request.form['url']
    path = request.form.get('path', DOWNLOAD_FOLDER)

    video_info.clear()
    thread = Thread(target=download_video, args=(url, path))
    thread.start()
    return jsonify({"status": "started"})

@app.route('/info')
def info():
    return jsonify(video_info)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, render_template, send_from_directory
import yt_dlp
import os
import time
from threading import Timer

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# YouTube動画のダウンロード
def download_video(url):
    ydl_opts = {
        'format': 'best',  # 最良のフォーマットでダウンロード
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),  # ダウンロード先のファイル名
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        video_file = result['id'] + '.' + result['ext']  # ダウンロードしたファイルのパスを取得
        title = result.get('title', 'タイトル情報なし')  # タイトルを取得（ない場合はデフォルト値）
        return video_file, title

# 動画ファイルを一定時間後に削除
def delete_video(video_file):
    try:
        os.remove(os.path.join(DOWNLOAD_FOLDER, video_file))
        print(f"{video_file} has been deleted.")
    except Exception as e:
        print(f"Error deleting file {video_file}: {e}")

# ホームページ（URL入力フォーム）
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if url:
            video_file, title = download_video(url)

            # 動画ファイルを一定時間後に削除する（例: 5分後）
            Timer(3600, delete_video, args=[video_file]).start()

            return render_template('index.html', video_file=video_file, title=title)
    return render_template('index.html', video_file=None, title=None)

# ダウンロードした動画の再生
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

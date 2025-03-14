from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
import yt_dlp
import json
import os

class FetchThread(QThread):
    infoFetched = pyqtSignal(dict)
    errorOccurred = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        fetch_opts = {
            "quite": True,
            "skip_download": True,
            "writeinfojson": True,
            "overwrites": True,
            "outtmpl": "vid.%(ext)s",
        }

        try:
            with yt_dlp.YoutubeDL(fetch_opts) as ydl:
                ydl.download([self.url])
                with open("vid.info.json", "r", encoding="utf8") as info_file:
                    video_info = json.load(info_file)
                    self.infoFetched.emit(video_info)
        except Exception as e:
            self.errorOccurred.emit(str(e))
            

class DownloadThread(QThread):
    progressUpdated = pyqtSignal(int)
    downloadCompleted = pyqtSignal()
    errorOccurred = pyqtSignal(str)

    def __init__(self, format_id, output_path):
        super().__init__()
        self.format_id = format_id
        self.output_path = output_path
        self.ffmpeg_path = f"{os.getcwd()}\\ffmpeg"
        self.file_path = f"{os.getcwd()}\\vid.info.json"

    def run(self):
        ydl_opts = {
            "load_info_filename": True,
            'format': f'{self.format_id}+bestaudio/{self.format_id}+best[acodec!=none]/best',
            'ffmpeg_location': self.ffmpeg_path,
            'outtmpl': os.path.join(self.output_path, '%(id)s-%(height)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            "overwrites": True,
            "windowsfilenames":True,
            "restrictfilenames":True,
            # "trim_file_name":True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download_with_info_file(self.file_path)
            self.downloadCompleted.emit()
        except Exception as e:
            self.errorOccurred.emit(str(e))

    def progress_hook(self, p):
        if p['status'] == 'downloading':
            total_bytes = p.get('total_bytes') or p.get('total_bytes_estimate')
            downloaded_bytes = p.get('downloaded_bytes', 0)
            if total_bytes:
                percent = int((downloaded_bytes / total_bytes) * 100)
                self.progressUpdated.emit(percent)
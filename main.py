import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from design import Ui_Main
from workers import FetchThread, DownloadThread
import os


# main ui class
class MainWindow(QtWidgets.QMainWindow, Ui_Main):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        # self.setFixedSize(300,300)

        dest_path = os.getcwd()

        self.format_values = {}
        self.txtDest.setText(f"{dest_path}")

        self.btnFetch.clicked.connect(self.start_fetch_info)
        self.btnDownload.clicked.connect(self.start_download_video)
        self.btnBrowse.clicked.connect(self.browse_destination)

        self.statusBar1.showMessage("Ready")

    def start_fetch_info(self):
        url = self.txtUrl.text()
        if not url:
            QMessageBox.critical(self, "Error", "Enter a URL")
            return

        self.selectFormat.clear()
        self.btnFetch.setEnabled(False)
        self.btnDownload.setEnabled(False)
        self.btnBrowse.setEnabled(False)
        self.statusBar1.showMessage('Fetching Info...')

        self.fetchThread = FetchThread(url)
        self.fetchThread.infoFetched.connect(self.handle_info_fetched)
        self.fetchThread.errorOccurred.connect(self.handle_error)
        self.fetchThread.start()

    def handle_info_fetched(self, video_info):
        self.lblTitle.setText(video_info.get('title'))
        formats = video_info.get("formats", [])

        for fmt in formats:
            if fmt.get('height') and fmt.get('vcodec') != 'none'  and fmt.get('ext') != 'mp4':
                self.format_values[f"{fmt.get('height')}p | {fmt.get('fps', 'N/A')} fps | Resolution: {fmt.get('resolution', 'N/A')}"] = f"{fmt.get('format_id')}"

        if len(self.format_values) == 0:
            for fmt in formats:
                if fmt.get('height') and fmt.get('vcodec') != 'none':
                    self.format_values[f"{fmt.get('height')}p | {fmt.get('fps', 'N/A')} fps | Resolution: {fmt.get('resolution', 'N/A')}"] = f"{fmt.get('format_id')}"

        self.selectFormat.addItems(self.format_values.keys())
        self.btnFetch.setEnabled(True)
        self.btnDownload.setEnabled(True)
        self.btnBrowse.setEnabled(True)
        self.statusBar1.showMessage('Info Fetched')

    def start_download_video(self):
        selected_format = self.selectFormat.currentText()
        if not selected_format:
            QMessageBox.critical(self, "Error", "Select a format first")
            return

        self.btnFetch.setEnabled(False)
        self.btnDownload.setEnabled(False)
        self.btnBrowse.setEnabled(False)

        output_path = self.txtDest.text()
        format_id = self.format_values[selected_format]

        self.downloadThread = DownloadThread(format_id, output_path)
        self.downloadThread.progressUpdated.connect(self.progressBar.setValue)
        self.downloadThread.downloadCompleted.connect(self.handle_download_complete)
        self.downloadThread.errorOccurred.connect(self.handle_error)
        self.downloadThread.start()
        self.statusBar1.showMessage('Downloading...')

    def handle_download_complete(self):
        QMessageBox.information(self, "Success", "Download completed")
        self.progressBar.setValue(0)
        self.btnFetch.setEnabled(True)
        self.btnDownload.setEnabled(True)
        self.btnBrowse.setEnabled(True)
        self.statusBar1.showMessage('*** Download Completed ***')

    def handle_error(self, error):
        QMessageBox.critical(self, "Error", error)
        self.btnFetch.setEnabled(True)
        self.btnDownload.setEnabled(True)
        self.btnBrowse.setEnabled(True)

    def browse_destination(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Destination")
        if dir_path:
            self.txtDest.setText(dir_path)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
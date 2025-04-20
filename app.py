import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QComboBox, 
                           QProgressBar, QLabel, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import yt_dlp
from pathlib import Path
import shutil
from datetime import datetime
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# الإعدادات الثابتة
DOWNLOAD_DIR = "downloads"
TEMP_DIR = "temp"

# التأكد من وجود المجلدات المطلوبة
for dir_path in [DOWNLOAD_DIR, TEMP_DIR]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    status = pyqtSignal(str)

    def __init__(self, url, format_id, output_path, audio_only=False):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.output_path = output_path
        self.audio_only = audio_only

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    percentage = (downloaded / total) * 100
                    self.progress.emit(int(percentage))
                    self.status.emit(f"جاري التحميل: {percentage:.1f}%")
            except:
                pass
        elif d['status'] == 'finished':
            self.status.emit("اكتمل التحميل")

    def run(self):
        try:
            ydl_opts = {
                'format': self.format_id if not self.audio_only else 'bestaudio/best',
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }] if self.audio_only else [],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            self.finished.emit(True, "تم التحميل بنجاح")
        except Exception as e:
            logger.error(f"خطأ في التحميل: {str(e)}")
            self.finished.emit(False, f"خطأ في التحميل: {str(e)}")

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تحميل من YouTube")
        self.setMinimumWidth(600)
        self.setup_ui()

    def setup_ui(self):
        # الواجهة الرئيسية
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # حقل إدخال الرابط
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("أدخل رابط YouTube هنا...")
        url_layout.addWidget(self.url_input)
        
        self.check_button = QPushButton("فحص الرابط")
        self.check_button.clicked.connect(self.check_url)
        url_layout.addWidget(self.check_button)
        layout.addLayout(url_layout)

        # معلومات الفيديو
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        layout.addWidget(self.info_text)

        # خيارات التحميل
        options_layout = QHBoxLayout()
        
        # نوع التحميل
        self.download_type = QComboBox()
        self.download_type.addItems(["فيديو", "صوت فقط (MP3)"])
        self.download_type.currentIndexChanged.connect(self.update_formats)
        options_layout.addWidget(QLabel("نوع التحميل:"))
        options_layout.addWidget(self.download_type)
        
        # جودة الفيديو
        self.format_combo = QComboBox()
        self.format_combo.setEnabled(False)
        options_layout.addWidget(QLabel("الجودة:"))
        options_layout.addWidget(self.format_combo)
        
        layout.addLayout(options_layout)

        # شريط التقدم
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # حالة التحميل
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # زر التحميل
        self.download_button = QPushButton("بدء التحميل")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.video_info = None
        self.formats = []

    def check_url(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال رابط")
            return

        try:
            with yt_dlp.YoutubeDL() as ydl:
                self.video_info = ydl.extract_info(url, download=False)
                self.info_text.setText(f"العنوان: {self.video_info['title']}\n"
                                     f"المدة: {self.video_info.get('duration_string', 'غير متاح')}")
                
                self.formats = []
                for f in self.video_info['formats']:
                    if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') != 'none':
                        self.formats.append({
                            'format_id': f['format_id'],
                            'ext': f['ext'],
                            'resolution': f.get('resolution', 'N/A'),
                            'format_note': f.get('format_note', '')
                        })
                
                self.update_formats()
                self.download_button.setEnabled(True)
                
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"خطأ في الحصول على معلومات الفيديو: {str(e)}")

    def update_formats(self):
        self.format_combo.clear()
        if self.download_type.currentText() == "فيديو":
            self.format_combo.setEnabled(True)
            for f in self.formats:
                self.format_combo.addItem(
                    f"{f['resolution']} - {f['format_note']}", 
                    userData=f['format_id']
                )
        else:
            self.format_combo.setEnabled(False)

    def start_download(self):
        if not self.video_info:
            return

        # إنشاء مجلد مؤقت للتحميل
        temp_dir = os.path.join(TEMP_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(temp_dir, exist_ok=True)

        # إعداد خيارات التحميل
        is_audio = self.download_type.currentText() == "صوت فقط (MP3)"
        format_id = self.format_combo.currentData() if not is_audio else 'bestaudio/best'

        # بدء التحميل
        self.download_worker = DownloadWorker(
            self.video_info['webpage_url'],
            format_id,
            temp_dir,
            audio_only=is_audio
        )
        
        self.download_worker.progress.connect(self.progress_bar.setValue)
        self.download_worker.status.connect(self.status_label.setText)
        self.download_worker.finished.connect(self.download_finished)
        
        self.download_button.setEnabled(False)
        self.check_button.setEnabled(False)
        self.download_worker.start()

    def download_finished(self, success, message):
        self.download_button.setEnabled(True)
        self.check_button.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "نجاح", message)
        else:
            QMessageBox.warning(self, "خطأ", message)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # نمط موحد لجميع أنظمة التشغيل
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

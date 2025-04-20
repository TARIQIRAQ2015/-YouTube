import streamlit as st
import yt_dlp
import os
import time
from pathlib import Path
import shutil
import json
from datetime import datetime
import zipfile
import threading
from queue import Queue
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# الإعدادات الثابتة
DOWNLOAD_DIR = "downloads"
TEMP_DIR = "temp"
MAX_THREADS = 3

# التأكد من وجود المجلدات المطلوبة
for dir_path in [DOWNLOAD_DIR, TEMP_DIR]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# تكوين الصفحة
st.set_page_config(
    page_title="تحميل من YouTube",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تعيين منفذ مختلف
if not os.environ.get("STREAMLIT_SERVER_PORT"):
    os.environ["STREAMLIT_SERVER_PORT"] = "8502"

# تخصيص CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        color: white;
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        border: none;
        padding: 0.8rem;
        border-radius: 50px;
        font-size: 1.2rem;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.4);
    }
    .video-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .video-item {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .download-options {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class VideoDownloader:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        self.download_queue = Queue()
        self.progress_dict = {}
        self.download_threads = []

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            video_id = d.get('info_dict', {}).get('id', 'unknown')
            total = d.get('total_bytes', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            if total > 0:
                progress = (downloaded / total) * 100
                self.progress_dict[video_id] = progress

    def get_video_info(self, url):
        """الحصول على معلومات الفيديو أو قائمة التشغيل"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    # قائمة تشغيل
                    return {
                        'type': 'playlist',
                        'title': info.get('title', 'قائمة تشغيل'),
                        'entries': info['entries']
                    }
                else:
                    # فيديو واحد
                    return {
                        'type': 'video',
                        'title': info.get('title', 'فيديو'),
                        'entries': [info]
                    }
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الفيديو: {str(e)}")
            return None

    def get_formats(self, video_url):
        """الحصول على الصيغ المتاحة للفيديو"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                formats = []
                
                # تصفية الصيغ المتاحة
                for f in info['formats']:
                    if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') != 'none':
                        formats.append({
                            'format_id': f['format_id'],
                            'ext': f['ext'],
                            'resolution': f.get('resolution', 'N/A'),
                            'filesize': f.get('filesize', 0),
                            'format_note': f.get('format_note', '')
                        })
                
                return formats
        except Exception as e:
            logger.error(f"خطأ في الحصول على الصيغ: {str(e)}")
            return []

    def download_video(self, url, format_id, output_path, audio_only=False):
        """تحميل فيديو واحد"""
        try:
            ydl_opts = {
                'format': format_id if not audio_only else 'bestaudio/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }] if audio_only else [],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            logger.error(f"خطأ في تحميل الفيديو: {str(e)}")
            return False

    def create_zip(self, source_dir, output_path):
        """إنشاء ملف ZIP من المجلد"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            return True
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف ZIP: {str(e)}")
            return False

def main():
    st.title("📥 تحميل من YouTube")
    st.write("قم بلصق رابط الفيديو أو قائمة التشغيل للبدء")

    # إنشاء كائن VideoDownloader
    downloader = VideoDownloader()

    # حقل إدخال الرابط
    url = st.text_input("", placeholder="🔗 أدخل رابط YouTube هنا...")

    if url:
        info = downloader.get_video_info(url)
        
        if info:
            st.success(f"تم العثور على: {info['title']}")
            
            # خيارات التحميل
            st.markdown("### ⚙️ خيارات التحميل")
            col1, col2 = st.columns(2)
            
            with col1:
                download_type = st.radio(
                    "نوع التحميل",
                    ["فيديو", "صوت فقط (MP3)"]
                )
            
            with col2:
                if download_type == "فيديو":
                    formats = downloader.get_formats(url if info['type'] == 'video' else info['entries'][0]['url'])
                    format_options = {f"{f['resolution']} - {f['format_note']}": f['format_id'] for f in formats}
                    selected_format = st.selectbox("اختر الجودة", list(format_options.keys()))
                    format_id = format_options[selected_format]
                
            # عرض الفيديوهات
            st.markdown("### 📺 الفيديوهات المتاحة")
            
            for entry in info['entries']:
                with st.container():
                    st.markdown(f"""
                    <div class="video-item">
                        <h4>{entry['title']}</h4>
                        <small>المدة: {entry.get('duration_string', 'غير متاح')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # زر التحميل
            if st.button("🚀 بدء التحميل"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # إنشاء مجلد مؤقت للتحميل
                temp_dir = os.path.join(TEMP_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))
                os.makedirs(temp_dir, exist_ok=True)
                
                total_videos = len(info['entries'])
                downloaded = 0
                
                for entry in info['entries']:
                    video_url = entry['url']
                    status_text.text(f"جاري تحميل: {entry['title']}")
                    
                    if download_type == "فيديو":
                        success = downloader.download_video(video_url, format_id, temp_dir)
                    else:
                        success = downloader.download_video(video_url, 'bestaudio/best', temp_dir, audio_only=True)
                    
                    if success:
                        downloaded += 1
                        progress_bar.progress(downloaded / total_videos)
                
                if downloaded > 0:
                    # إنشاء ملف ZIP
                    zip_path = os.path.join(DOWNLOAD_DIR, f"youtube_downloads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
                    if downloader.create_zip(temp_dir, zip_path):
                        with open(zip_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ تحميل الملفات",
                                data=f,
                                file_name=os.path.basename(zip_path),
                                mime="application/zip"
                            )
                    
                    # تنظيف المجلد المؤقت
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
                    st.success(f"تم تحميل {downloaded} من {total_videos} فيديو بنجاح!")
                else:
                    st.error("حدث خطأ أثناء التحميل. الرجاء المحاولة مرة أخرى.")

if __name__ == "__main__":
    main()

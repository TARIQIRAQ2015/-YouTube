import streamlit as st
from pytube import Playlist, YouTube
import os
import re
import time
from datetime import datetime

# تكوين الصفحة
st.set_page_config(
    page_title="تحميل قائمة تشغيل YouTube",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تخصيص CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    .stButton > button {
        width: 100%;
        background-color: #ff0000;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 5px;
        font-size: 1.2rem;
        margin-top: 1rem;
    }
    .stButton > button:hover {
        background-color: #cc0000;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #cce5ff;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .title-box {
        text-align: center;
        padding: 2rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .download-stats {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
        padding: 1rem;
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown("""
<div class="title-box">
    <h1>📥 تحميل قائمة تشغيل YouTube</h1>
    <p style='font-size: 1.2rem;'>قم بلصق رابط قائمة التشغيل وسيتم تحميل كل الفيديوهات بأعلى جودة متاحة</p>
</div>
""", unsafe_allow_html=True)

# إنشاء مجلد التحميل
download_path = "downloads"
os.makedirs(download_path, exist_ok=True)

def format_size(size_bytes):
    """تحويل حجم الملف إلى صيغة مقروءة"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_video_info(url, retries=5, delay=2):
    """الحصول على معلومات الفيديو"""
    for attempt in range(retries):
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if stream:
                return {
                    'title': yt.title,
                    'stream': stream,
                    'size': stream.filesize,
                    'resolution': stream.resolution
                }
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(delay * (attempt + 1))  # زيادة وقت الانتظار مع كل محاولة
    return None

def download_video(video_info, output_path, retries=5):
    """تحميل الفيديو مع إعادة المحاولة"""
    for attempt in range(retries):
        try:
            video_info['stream'].download(output_path=output_path)
            return True, None
        except Exception as e:
            if attempt == retries - 1:
                return False, str(e)
            time.sleep(2 * (attempt + 1))
    return False, "فشل التحميل بعد عدة محاولات"

def is_valid_playlist_url(url):
    """التحقق من صحة رابط قائمة التشغيل"""
    playlist_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/playlist\?list=[\w-]+'
    return bool(re.match(playlist_pattern, url))

def download_playlist(url):
    """تحميل قائمة التشغيل مع عرض التقدم والإحصائيات"""
    if not is_valid_playlist_url(url):
        st.markdown('<div class="error-box">❌ الرابط غير صالح. يرجى التأكد من أنه رابط قائمة تشغيل YouTube صحيح.</div>', unsafe_allow_html=True)
        return

    try:
        with st.spinner("🔄 جاري التحقق من قائمة التشغيل..."):
            playlist = Playlist(url)
            video_urls = playlist.video_urls

        if not video_urls:
            st.markdown('<div class="error-box">❌ لم يتم العثور على أي فيديوهات في قائمة التشغيل. تأكد من أن القائمة عامة وتحتوي على فيديوهات.</div>', unsafe_allow_html=True)
            return

        total_videos = len(video_urls)
        st.markdown(f'<div class="success-box">📃 تم العثور على {total_videos} فيديو</div>', unsafe_allow_html=True)

        # إحصائيات التحميل
        col1, col2, col3 = st.columns(3)
        with col1:
            total_size_metric = st.empty()
        with col2:
            success_metric = st.empty()
        with col3:
            failed_metric = st.empty()

        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_downloads = 0
        failed_downloads = []
        total_size = 0

        for i, video_url in enumerate(video_urls, 1):
            try:
                status_text.markdown(f'<div class="info-box">⏳ جاري تحميل الفيديو {i} من {total_videos}</div>', unsafe_allow_html=True)
                
                # الحصول على معلومات الفيديو
                video_info = get_video_info(video_url)
                if video_info:
                    success, error = download_video(video_info, download_path)
                    if success:
                        successful_downloads += 1
                        total_size += video_info['size']
                        st.success(f"✅ تم تحميل: {video_info['title']} ({video_info['resolution']})")
                    else:
                        failed_downloads.append((i, video_info['title'], error))
                        st.warning(f"⚠️ فشل تحميل: {video_info['title']} - {error}")
                else:
                    failed_downloads.append((i, "غير معروف", "فشل في الحصول على معلومات الفيديو"))

                # تحديث الإحصائيات
                total_size_metric.markdown(f"💾 الحجم الكلي: {format_size(total_size)}")
                success_metric.markdown(f"✅ تم تحميل: {successful_downloads}")
                failed_metric.markdown(f"❌ فشل: {len(failed_downloads)}")
                
                progress_bar.progress((i) / total_videos)
                time.sleep(1)  # تأخير بين التحميلات

            except Exception as e:
                failed_downloads.append((i, "غير معروف", str(e)))
                continue

        # عرض النتائج النهائية
        if successful_downloads > 0:
            st.markdown(f'<div class="success-box">✅ تم تحميل {successful_downloads} فيديو بنجاح</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">📁 تم الحفظ في المجلد: {download_path}</div>', unsafe_allow_html=True)
        
        if failed_downloads:
            st.markdown('<div class="error-box">⚠️ الفيديوهات التي لم يتم تحميلها:</div>', unsafe_allow_html=True)
            for video_num, title, error in failed_downloads:
                st.write(f"- الفيديو رقم {video_num} ({title}): {error}")

    except Exception as e:
        st.markdown(f'<div class="error-box">❌ حدث خطأ: {str(e)}</div>', unsafe_allow_html=True)
        if "429" in str(e):
            st.warning("⚠️ تم تجاوز حد الطلبات. يرجى الانتظار قليلاً ثم المحاولة مرة أخرى.")

# حقل إدخال الرابط
playlist_url = st.text_input("", placeholder="🔗 أدخل رابط قائمة التشغيل هنا...")

# زر التحميل
if st.button("🚀 تحميل القائمة"):
    if playlist_url.strip():
        download_playlist(playlist_url)
    else:
        st.markdown('<div class="error-box">⚠️ الرجاء إدخال رابط صالح.</div>', unsafe_allow_html=True)

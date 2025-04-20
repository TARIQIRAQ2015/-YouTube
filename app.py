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
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 114, 255, 0.4);
    }
    .success-box {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 176, 155, 0.2);
    }
    .error-box {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff4949 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 73, 73, 0.2);
    }
    .info-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.2);
    }
    .title-box {
        text-align: center;
        padding: 2rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50px;
        padding: 0.5rem 1rem;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    .stTextInput > div > div:focus-within {
        border-color: #00c6ff;
    }
    .download-stats {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .progress-bar {
        border-radius: 50px !important;
        height: 20px !important;
    }
    .progress-bar > div {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
    }
    .url-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        word-break: break-all;
    }
    .instruction-box {
        background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(252, 70, 107, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown("""
<div class="title-box">
    <h1 style='font-size: 2.5rem; margin-bottom: 1rem;'>📥 تحميل قائمة تشغيل YouTube</h1>
    <p style='font-size: 1.2rem; opacity: 0.9;'>قم بلصق رابط قائمة التشغيل للحصول على روابط التحميل</p>
</div>
""", unsafe_allow_html=True)

def is_valid_playlist_url(url):
    """التحقق من صحة رابط قائمة التشغيل"""
    playlist_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/playlist\?list=[\w-]+'
    return bool(re.match(playlist_pattern, url))

def get_video_info(url, retries=3):
    """الحصول على معلومات الفيديو"""
    for attempt in range(retries):
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if stream:
                return {
                    'title': yt.title,
                    'url': stream.url,
                    'resolution': stream.resolution
                }
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(5)
    return None

def create_download_file(videos_info, file_path):
    """إنشاء ملف التحميل"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for video in videos_info:
                f.write(f"{video['url']}\n")
        return True
    except Exception as e:
        st.error(f"❌ خطأ في إنشاء ملف التحميل: {str(e)}")
        return False

def process_playlist(url):
    """معالجة قائمة التشغيل"""
    if not is_valid_playlist_url(url):
        st.markdown('<div class="error-box">❌ الرابط غير صالح. يرجى التأكد من أنه رابط قائمة تشغيل YouTube صحيح.</div>', unsafe_allow_html=True)
        return

    try:
        with st.spinner("🔄 جاري التحقق من قائمة التشغيل..."):
            playlist = Playlist(url)
            video_urls = playlist.video_urls

        if not video_urls:
            st.markdown('<div class="error-box">❌ لم يتم العثور على أي فيديوهات في قائمة التشغيل</div>', unsafe_allow_html=True)
            return

        total_videos = len(video_urls)
        st.markdown(f'<div class="success-box">📃 تم العثور على {total_videos} فيديو</div>', unsafe_allow_html=True)

        progress_bar = st.progress(0)
        status_text = st.empty()
        
        videos_info = []
        failed = 0

        for i, video_url in enumerate(video_urls, 1):
            try:
                status_text.markdown(f'<div class="info-box">⏳ جاري تحضير الفيديو {i} من {total_videos}</div>', unsafe_allow_html=True)
                
                video_info = get_video_info(video_url)
                if video_info:
                    videos_info.append(video_info)
                    st.markdown(f'<div class="url-box">✅ {video_info["title"]} ({video_info["resolution"]})</div>', unsafe_allow_html=True)
                else:
                    failed += 1
                    st.warning(f"⚠️ تعذر الحصول على رابط الفيديو رقم {i}")
                
                progress_bar.progress(i / total_videos)
                time.sleep(1)

            except Exception as e:
                failed += 1
                st.error(f"❌ خطأ في الفيديو {i}: {str(e)}")
                time.sleep(2)
                continue

        if videos_info:
            # إنشاء اسم الملف بناءً على التاريخ والوقت
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"youtube_links_{timestamp}.txt"
            file_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)
            
            if create_download_file(videos_info, file_path):
                st.markdown(f'<div class="success-box">✅ تم إنشاء ملف الروابط بنجاح!</div>', unsafe_allow_html=True)
                st.markdown("""
                <div class="instruction-box">
                    <h3>📝 خطوات التحميل:</h3>
                    <ol>
                        <li>افتح برنامج Internet Download Manager</li>
                        <li>اضغط على Tasks > Import > Import URLs from file</li>
                        <li>اختر الملف من مجلد Downloads باسم youtube_links_[التاريخ].txt</li>
                        <li>اضغط OK لبدء التحميل</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
                st.info(f"📁 مسار الملف: {file_path}")

        if failed > 0:
            st.markdown(f'<div class="error-box">⚠️ تعذر الحصول على {failed} روابط</div>', unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f'<div class="error-box">❌ حدث خطأ: {str(e)}</div>', unsafe_allow_html=True)

# حقل إدخال الرابط
playlist_url = st.text_input("", placeholder="🔗 أدخل رابط قائمة التشغيل هنا...")

# زر التحميل
if st.button("🚀 استخراج روابط التحميل"):
    if playlist_url.strip():
        process_playlist(playlist_url)
    else:
        st.markdown('<div class="error-box">⚠️ الرجاء إدخال رابط صالح.</div>', unsafe_allow_html=True)

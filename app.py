import streamlit as st
from pytube import Playlist, YouTube
import os
import re
import time
from datetime import datetime
import pyperclip

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
    .video-box {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .video-item {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .video-info {
        flex: 1;
        min-width: 200px;
    }
    .video-title {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .video-resolution {
        color: #00c6ff;
        font-size: 0.9rem;
    }
    .copy-button {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .copy-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3);
    }
    .copy-all-button {
        background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        margin: 1rem 0;
        display: block;
        width: 100%;
    }
    .copy-all-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(252, 70, 107, 0.3);
    }
    .stats-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown("""
<div class="title-box">
    <h1 style='font-size: 2.5rem; margin-bottom: 1rem;'>📥 تحميل قائمة تشغيل YouTube</h1>
    <p style='font-size: 1.2rem; opacity: 0.9;'>احصل على روابط التحميل المباشرة لقائمة التشغيل</p>
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
                    'resolution': stream.resolution,
                    'thumbnail': yt.thumbnail_url
                }
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(5)
    return None

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
        st.markdown(f'<div class="stats-box">📊 تم العثور على {total_videos} فيديو</div>', unsafe_allow_html=True)

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
            st.markdown('<div class="video-box">', unsafe_allow_html=True)
            
            # زر نسخ جميع الروابط
            all_urls = "\n".join([video['url'] for video in videos_info])
            st.markdown(f"""
            <button class="copy-all-button" onclick="
                navigator.clipboard.writeText('{all_urls}');
                this.innerHTML = '✅ تم نسخ جميع الروابط!';
                setTimeout(() => this.innerHTML = '📋 نسخ جميع الروابط', 2000);
            ">
                📋 نسخ جميع الروابط
            </button>
            """, unsafe_allow_html=True)
            
            # عرض معلومات كل فيديو
            for video in videos_info:
                st.markdown(f"""
                <div class="video-item">
                    <div class="video-info">
                        <div class="video-title">{video['title']}</div>
                        <div class="video-resolution">🎥 {video['resolution']}</div>
                    </div>
                    <button class="copy-button" onclick="
                        navigator.clipboard.writeText('{video['url']}');
                        this.innerHTML = '✅ تم النسخ!';
                        setTimeout(() => this.innerHTML = '📋 نسخ الرابط', 2000);
                    ">
                        📋 نسخ الرابط
                    </button>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

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

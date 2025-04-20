import streamlit as st
from pytube import Playlist, YouTube
import os
import re
import time
from datetime import datetime
import random

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
        font-size: 1.2rem;
    }
    .copy-all-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(252, 70, 107, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def get_video_info(url):
    """الحصول على معلومات الفيديو"""
    try:
        # إضافة وقت انتظار عشوائي بين 3 و 6 ثواني
        time.sleep(random.uniform(3, 6))
        
        # إضافة User-Agent للطلبات
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        yt.bypass_age_gate()
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if stream:
            return {
                'title': yt.title,
                'url': stream.url,
                'resolution': stream.resolution
            }
    except Exception as e:
        if 'HTTP Error 429' in str(e):
            # في حالة وجود خطأ 429، ننتظر وقتاً أطول
            time.sleep(random.uniform(10, 15))
            try:
                yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
                yt.bypass_age_gate()
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if stream:
                    return {
                        'title': yt.title,
                        'url': stream.url,
                        'resolution': stream.resolution
                    }
            except:
                pass
    return None

def process_playlist(url):
    """معالجة قائمة التشغيل"""
    try:
        # التحقق من صحة الرابط
        if not url.startswith('http'):
            url = 'https://' + url
        
        # محاولة الحصول على معلومات القائمة
        playlist = Playlist(url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")  # تحديث التعبير النمطي
        
        try:
            # محاولة الوصول إلى عنوان القائمة
            title = playlist.title
            st.write(f"قائمة التشغيل: {title}")
        except:
            pass
        
        # الحصول على روابط الفيديوهات
        video_urls = list(playlist.video_urls)
        
        if not video_urls:
            st.error("❌ لم يتم العثور على فيديوهات في القائمة")
            return
            
        st.write(f"تم العثور على {len(video_urls)} فيديو")
        
        # معالجة كل فيديو
        videos_info = []
        with st.spinner("جاري معالجة الفيديوهات..."):
            for i, video_url in enumerate(video_urls):
                info = get_video_info(video_url)
                if info:
                    videos_info.append(info)
                    # عرض معلومات الفيديو مباشرة
                    st.markdown(f"""
                    <div class="video-item">
                        <div class="video-info">
                            <div class="video-title">{info['title']}</div>
                            <div class="video-resolution">🎥 {info['resolution']}</div>
                        </div>
                        <button class="copy-button" onclick="
                            navigator.clipboard.writeText('{info['url']}');
                            this.innerHTML = '✅ تم النسخ!';
                            setTimeout(() => this.innerHTML = '📋 نسخ الرابط', 2000);
                        ">
                            📋 نسخ الرابط
                        </button>
                    </div>
                    """, unsafe_allow_html=True)
                
                # انتظار بين كل فيديو وآخر
                if i < len(video_urls) - 1:  # لا داعي للانتظار بعد آخر فيديو
                    time.sleep(random.uniform(2, 4))
        
        if videos_info:
            # إضافة زر نسخ جميع الروابط
            all_urls = "\n".join([v['url'] for v in videos_info])
            st.markdown(f"""
            <button class="copy-all-button" onclick="
                navigator.clipboard.writeText('{all_urls}');
                this.innerHTML = '✅ تم نسخ جميع الروابط!';
                setTimeout(() => this.innerHTML = '📋 نسخ جميع الروابط ({len(videos_info)})', 2000);
            ">
                📋 نسخ جميع الروابط ({len(videos_info)})
            </button>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"حدث خطأ: {str(e)}")
        st.write("الرجاء التأكد من صحة الرابط وحاول مرة أخرى")

# واجهة المستخدم
st.title("📥 تحميل قائمة تشغيل YouTube")
st.write("قم بلصق رابط قائمة التشغيل للحصول على روابط التحميل المباشرة")

# حقل إدخال الرابط
playlist_url = st.text_input("", placeholder="🔗 أدخل رابط قائمة التشغيل هنا...")

# زر استخراج الروابط
if st.button("🚀 استخراج روابط التحميل"):
    if playlist_url.strip():
        process_playlist(playlist_url.strip())
    else:
        st.warning("⚠️ الرجاء إدخال رابط قائمة التشغيل")

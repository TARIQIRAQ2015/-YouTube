import streamlit as st
from pytube import Playlist, YouTube
import os

# إعداد الصفحة
st.set_page_config(page_title="تحميل قائمة تشغيل YouTube", layout="centered")
st.title("📥 تحميل قائمة تشغيل من YouTube")
st.write("قم بلصق رابط قائمة التشغيل وسيتم تحميل كل الفيديوهات بأعلى جودة متاحة.")

# إدخال رابط قائمة التشغيل
playlist_url = st.text_input("🔗 أدخل رابط قائمة التشغيل هنا:")

# إنشاء مجلد التحميل
download_path = "downloads"
os.makedirs(download_path, exist_ok=True)

# دالة تحميل قائمة التشغيل
def download_playlist(url):
    try:
        playlist = Playlist(url)
        st.success(f"📃 عدد المقاطع: {len(playlist.video_urls)}")
        for i, video_url in enumerate(playlist.video_urls):
            yt = YouTube(video_url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            st.write(f"⬇️ تحميل ({i+1}/{len(playlist.video_urls)}): {yt.title}")
            stream.download(output_path=download_path)
        st.success("✅ تم التحميل بنجاح!")
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")

# زر التحميل
if st.button("🚀 تحميل القائمة"):
    if playlist_url.strip():
        download_playlist(playlist_url)
        st.info(f"📁 تم الحفظ في المجلد: `{download_path}`")
    else:
        st.warning("⚠️ الرجاء إدخال رابط صالح.")


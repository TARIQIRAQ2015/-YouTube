import streamlit as st
from pytube import Playlist, YouTube
import os
import re
import time

# إعداد الصفحة
st.set_page_config(page_title="تحميل قائمة تشغيل YouTube", layout="centered")
st.title("📥 تحميل قائمة تشغيل من YouTube")
st.write("قم بلصق رابط قائمة التشغيل وسيتم تحميل كل الفيديوهات بأعلى جودة متاحة.")

# إدخال رابط قائمة التشغيل
playlist_url = st.text_input("🔗 أدخل رابط قائمة التشغيل هنا:")

# إنشاء مجلد التحميل
download_path = "downloads"
os.makedirs(download_path, exist_ok=True)

def get_video_streams(yt, retries=3, delay=1):
    for i in range(retries):
        try:
            yt.check_availability()
            return yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(delay)
    return None

def download_video(url, output_path, retries=3):
    for _ in range(retries):
        try:
            yt = YouTube(url)
            stream = get_video_streams(yt)
            if stream:
                stream.download(output_path=output_path)
                return True, None
            return False, "لا توجد تدفقات متاحة"
        except Exception as e:
            if "429" in str(e):
                time.sleep(2)  # انتظر قليلاً قبل المحاولة مرة أخرى
                continue
            return False, str(e)
    return False, "تجاوز عدد المحاولات المسموح"

def is_valid_playlist_url(url):
    playlist_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/playlist\?list=[\w-]+'
    return bool(re.match(playlist_pattern, url))

def download_playlist(url):
    if not is_valid_playlist_url(url):
        st.error("❌ الرابط غير صالح. يرجى التأكد من أنه رابط قائمة تشغيل YouTube صحيح.")
        return

    try:
        st.info("🔄 جاري التحقق من قائمة التشغيل...")
        playlist = Playlist(url)
        video_urls = playlist.video_urls

        if not video_urls:
            st.error("❌ لم يتم العثور على أي فيديوهات في قائمة التشغيل. تأكد من أن القائمة عامة وتحتوي على فيديوهات.")
            return

        total_videos = len(video_urls)
        st.success(f"📃 تم العثور على {total_videos} فيديو")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_downloads = 0
        failed_downloads = []

        for i, video_url in enumerate(video_urls):
            status_text.write(f"⏳ جاري تحميل الفيديو {i+1} من {total_videos}")
            success, error = download_video(video_url, download_path)
            
            if success:
                successful_downloads += 1
            else:
                failed_downloads.append((i+1, error))
            
            progress_bar.progress((i + 1) / total_videos)
            time.sleep(0.5)  # تأخير قصير لتجنب تجاوز حد الطلبات

        # عرض ملخص النتائج
        if successful_downloads > 0:
            st.success(f"✅ تم تحميل {successful_downloads} فيديو بنجاح")
        
        if failed_downloads:
            st.warning("⚠️ بعض الفيديوهات لم يتم تحميلها:")
            for video_num, error in failed_downloads:
                st.write(f"- الفيديو رقم {video_num}: {error}")

    except Exception as e:
        st.error(f"❌ حدث خطأ: {str(e)}")
        if "429" in str(e):
            st.warning("⚠️ تم تجاوز حد الطلبات. يرجى الانتظار قليلاً ثم المحاولة مرة أخرى.")
        elif "400" in str(e):
            st.info("💡 نصائح للإصلاح:\n"
                   "1. تأكد من أن الرابط صحيح وأنه رابط قائمة تشغيل وليس رابط فيديو\n"
                   "2. تأكد من أن قائمة التشغيل عامة وليست خاصة\n"
                   "3. جرب نسخ الرابط مرة أخرى من YouTube")

# زر التحميل
if st.button("🚀 تحميل القائمة"):
    if playlist_url.strip():
        download_playlist(playlist_url)
        if os.path.exists(download_path) and os.listdir(download_path):
            st.info(f"📁 تم الحفظ في المجلد: `{download_path}`")
    else:
        st.warning("⚠️ الرجاء إدخال رابط صالح.")

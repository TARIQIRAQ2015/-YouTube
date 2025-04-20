import streamlit as st
from pytube import Playlist, YouTube
import os
import re

# إعداد الصفحة
st.set_page_config(page_title="تحميل قائمة تشغيل YouTube", layout="centered")
st.title("📥 تحميل قائمة تشغيل من YouTube")
st.write("قم بلصق رابط قائمة التشغيل وسيتم تحميل كل الفيديوهات بأعلى جودة متاحة.")

# إدخال رابط قائمة التشغيل
playlist_url = st.text_input("🔗 أدخل رابط قائمة التشغيل هنا:")

# إنشاء مجلد التحميل
download_path = "downloads"
os.makedirs(download_path, exist_ok=True)

# دالة للتحقق من صحة رابط قائمة التشغيل
def is_valid_playlist_url(url):
    # نمط للتحقق من روابط قوائم التشغيل في يوتيوب
    playlist_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/playlist\?list=[\w-]+'
    return bool(re.match(playlist_pattern, url))

# دالة تحميل قائمة التشغيل
def download_playlist(url):
    try:
        if not is_valid_playlist_url(url):
            st.error("❌ الرابط غير صالح. يرجى التأكد من أنه رابط قائمة تشغيل YouTube صحيح.")
            return

        st.info("🔄 جاري التحقق من قائمة التشغيل...")
        playlist = Playlist(url)
        
        # التحقق من وجود فيديوهات في القائمة
        video_urls = playlist.video_urls
        if not video_urls:
            st.error("❌ لم يتم العثور على أي فيديوهات في قائمة التشغيل. تأكد من أن القائمة عامة وتحتوي على فيديوهات.")
            return
            
        st.success(f"📃 عدد المقاطع: {len(video_urls)}")
        
        for i, video_url in enumerate(video_urls):
            try:
                yt = YouTube(video_url)
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if stream:
                    st.write(f"⬇️ تحميل ({i+1}/{len(video_urls)}): {yt.title}")
                    stream.download(output_path=download_path)
                else:
                    st.warning(f"⚠️ تعذر تحميل الفيديو: {yt.title} - لا توجد تدفقات متاحة")
            except Exception as video_error:
                st.warning(f"⚠️ تعذر تحميل الفيديو رقم {i+1}: {str(video_error)}")
                continue
                
        st.success("✅ تم التحميل بنجاح!")
    except Exception as e:
        st.error(f"❌ حدث خطأ: {str(e)}")
        if "Status code 400" in str(e):
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

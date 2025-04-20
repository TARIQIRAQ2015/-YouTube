#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
from urllib.parse import urlparse
import yt_dlp

def clear_screen():
    """تنظيف الشاشة حسب نظام التشغيل"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """طباعة ترويسة البرنامج"""
    clear_screen()
    print("\n" + "=" * 80)
    print(" استخراج روابط التحميل المباشرة من قوائم تشغيل يوتيوب ".center(80))
    print("=" * 80 + "\n")

def validate_youtube_url(url):
    """التحقق من صحة رابط يوتيوب"""
    parsed_url = urlparse(url)
    if 'youtube.com' not in parsed_url.netloc and 'youtu.be' not in parsed_url.netloc:
        return False
    return True

def get_video_formats(video_id):
    """الحصول على صيغ الفيديو المتاحة"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            formats = info.get('formats', [])
            return formats
        except Exception as e:
            print(f"خطأ في الحصول على صيغ الفيديو: {str(e)}")
            return []

def get_direct_url(video_id, format_code):
    """الحصول على الرابط المباشر للفيديو بصيغة محددة"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': format_code,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # إذا كان الكود يحتوي على + (مثل 137+140)، يجب استخراج روابط متعددة
            if '+' in format_code:
                # في هذه الحالة، نقوم بإعادة الرابط الأول فقط (الفيديو) لأن معظم برامج التحميل تستطيع التعامل مع هذا
                # يمكن تعديل هذا السلوك حسب الحاجة
                if 'requested_formats' in info and len(info['requested_formats']) > 0:
                    direct_url = info['requested_formats'][0]['url']
                    return direct_url
            else:
                if 'url' in info:
                    return info['url']
            
            return None
        except Exception as e:
            print(f"خطأ في الحصول على الرابط المباشر: {str(e)}")
            return None

def extract_playlist_videos(playlist_url):
    """استخراج معلومات الفيديوهات من قائمة التشغيل"""
    print("\nجاري استخراج معلومات قائمة التشغيل...")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            if 'entries' not in playlist_info:
                print("لم يتم العثور على فيديوهات في قائمة التشغيل!")
                return []
                
            videos = []
            for entry in playlist_info['entries']:
                if entry:
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                    })
            
            return videos
        except Exception as e:
            print(f"خطأ في استخراج قائمة التشغيل: {str(e)}")
            return []

def show_common_format_codes():
    """عرض أكواد الصيغ الشائعة للمستخدم"""
    print("\nأكواد الصيغ الشائعة:")
    print("-" * 50)
    print("18  - MP4 - 360p")
    print("22  - MP4 - 720p")
    print("137 - MP4 - 1080p (فيديو فقط، بدون صوت)")
    print("140 - M4A - 128k (صوت فقط)")
    print("251 - WEBM - 160k (صوت فقط)")
    print("137+140 - MP4 - 1080p مع صوت")
    print("136+140 - MP4 - 720p مع صوت")
    print("-" * 50)

def main():
    """الدالة الرئيسية للبرنامج"""
    print_header()
    
    # طلب رابط قائمة التشغيل
    while True:
        playlist_url = input("\nأدخل رابط قائمة تشغيل YouTube: ").strip()
        if not playlist_url:
            print("الرجاء إدخال رابط صحيح!")
            continue
            
        if not validate_youtube_url(playlist_url):
            print("الرابط غير صالح! يجب أن يكون رابط YouTube.")
            continue
            
        break
    
    # استخراج الفيديوهات من قائمة التشغيل
    videos = extract_playlist_videos(playlist_url)
    
    if not videos:
        print("لم يتم العثور على فيديوهات! تأكد من صحة الرابط وأنه يحتوي على فيديوهات متاحة.")
        return
    
    # عرض قائمة الفيديوهات
    print(f"\nتم العثور على {len(videos)} فيديو في قائمة التشغيل:")
    print("-" * 80)
    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['title']}")
    print("-" * 80)
    
    # طلب كود الصيغة المطلوبة
    show_common_format_codes()
    format_code = input("\nأدخل كود الجودة المطلوبة (مثلاً 22 لـ MP4 720p): ").strip()
    
    if not format_code:
        print("لم يتم إدخال كود صيغة! سيتم استخدام الصيغة الافتراضية (22 - MP4 720p)")
        format_code = "22"
    
    # استخراج الروابط المباشرة وحفظها
    print("\nجاري استخراج الروابط المباشرة...")
    print("-" * 80)
    
    # إنشاء ملف النصي
    with open("links.txt", "w", encoding="utf-8") as file:
        successful_links = 0
        failed_links = 0
        
        for i, video in enumerate(videos, 1):
            print(f"[{i}/{len(videos)}] جاري استخراج: {video['title']}")
            
            direct_url = get_direct_url(video['id'], format_code)
            
            if direct_url:
                # كتابة الرابط في الملف
                file.write(f"{direct_url}\n")
                print(f"✅ تم استخراج الرابط بنجاح!")
                successful_links += 1
            else:
                print(f"❌ فشل استخراج الرابط للفيديو: {video['title']}")
                failed_links += 1
            
            # فاصل بين الفيديوهات
            print("-" * 80)
    
    # عرض التقرير النهائي
    print("\n" + "=" * 50)
    print(f"تم الانتهاء من استخراج الروابط!")
    print(f"إجمالي الفيديوهات: {len(videos)}")
    print(f"الروابط الناجحة: {successful_links}")
    print(f"الروابط الفاشلة: {failed_links}")
    print(f"تم حفظ الروابط في ملف: {os.path.abspath('links.txt')}")
    print("=" * 50)
    print("\nيمكنك الآن استيراد الملف في Internet Download Manager للتحميل.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nتم إيقاف البرنامج بواسطة المستخدم!")
    except Exception as e:
        print(f"\n\nحدث خطأ غير متوقع: {str(e)}")
    
    input("\nاضغط ENTER للخروج...")

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
from PIL import Image, ImageTk
import json

# تعيين الثيم الافتراضي للتطبيق
ctk.set_appearance_mode("System")  # الوضع: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # السمة: "blue", "green", "dark-blue"

class YoutubePlaylistDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # إعداد النافذة الرئيسية
        self.title("مُنزِّل قوائم تشغيل يوتيوب")
        self.geometry("900x600")
        self.minsize(800, 550)
        
        # متغيرات التطبيق
        self.playlist_url = ctk.StringVar()
        self.selected_quality = ctk.StringVar(value="720p")
        self.videos_info = []
        self.output_folder = os.path.expanduser("~/Downloads")
        self.language = "ar"  # الافتراضي: العربية
        
        # محاولة تحميل الإعدادات
        self.load_settings()
        
        # إنشاء واجهة المستخدم
        self.create_ui()
    
    def load_settings(self):
        """تحميل إعدادات المستخدم من ملف"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.selected_quality.set(settings.get("preferred_quality", "720p"))
                    self.output_folder = settings.get("output_folder", os.path.expanduser("~/Downloads"))
                    self.language = settings.get("language", "ar")
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
    
    def save_settings(self):
        """حفظ إعدادات المستخدم إلى ملف"""
        try:
            settings = {
                "preferred_quality": self.selected_quality.get(),
                "output_folder": self.output_folder,
                "language": self.language
            }
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"خطأ في حفظ الإعدادات: {e}")
    
    def create_ui(self):
        """إنشاء واجهة المستخدم الرئيسية"""
        # إنشاء الإطار الرئيسي
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # إطار إدخال الرابط
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        # عنوان التطبيق
        title_label = ctk.CTkLabel(
            input_frame, 
            text="مُنزِّل قوائم تشغيل يوتيوب",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 20), sticky="ew")
        
        # حقل إدخال رابط قائمة التشغيل
        url_label = ctk.CTkLabel(input_frame, text="رابط قائمة التشغيل:")
        url_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        url_entry = ctk.CTkEntry(input_frame, textvariable=self.playlist_url, width=400)
        url_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        url_entry.bind("<Button-3>", self.show_context_menu)  # قائمة النقر بزر الماوس الأيمن
        
        fetch_button = ctk.CTkButton(
            input_frame, 
            text="جلب القائمة", 
            command=self.fetch_playlist
        )
        fetch_button.grid(row=1, column=2, padx=10, pady=10)
        
        # إطار الخيارات
        options_frame = ctk.CTkFrame(input_frame)
        options_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        options_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # اختيار الجودة
        quality_label = ctk.CTkLabel(options_frame, text="الجودة:")
        quality_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "mp3"]
        quality_menu = ctk.CTkOptionMenu(
            options_frame, 
            values=quality_options,
            variable=self.selected_quality
        )
        quality_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # زر اختيار مجلد الحفظ
        folder_button = ctk.CTkButton(
            options_frame, 
            text="اختيار مجلد الحفظ", 
            command=self.select_output_folder
        )
        folder_button.grid(row=0, column=2, padx=10, pady=10)
        
        # زر تبديل اللغة
        language_button = ctk.CTkButton(
            options_frame, 
            text="English/عربي", 
            command=self.toggle_language,
            width=100
        )
        language_button.grid(row=0, column=3, padx=10, pady=10)
        
        # إطار عرض الفيديوهات
        self.videos_frame = ctk.CTkScrollableFrame(main_frame)
        self.videos_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.videos_frame.grid_columnconfigure(0, weight=1)
        
        # إطار الأزرار السفلية
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # زر توليد ملف الروابط
        generate_button = ctk.CTkButton(
            bottom_frame, 
            text="توليد ملف الروابط (IDM)", 
            command=self.generate_links_file
        )
        generate_button.grid(row=0, column=0, padx=10, pady=10)
        
        # زر تحميل مباشر
        download_button = ctk.CTkButton(
            bottom_frame, 
            text="تحميل مباشر", 
            command=self.download_videos
        )
        download_button.grid(row=0, column=1, padx=10, pady=10)
        
        # شريط الحالة
        self.status_var = tk.StringVar(value="جاهز")
        status_label = ctk.CTkLabel(bottom_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=2, padx=10, pady=10)
        
        # شريط التقدم
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
    def show_context_menu(self, event):
        """عرض قائمة النقر بزر الماوس الأيمن"""
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="لصق", command=lambda: event.widget.paste())
        context_menu.add_command(label="نسخ", command=lambda: event.widget.copy())
        context_menu.add_command(label="قص", command=lambda: event.widget.cut())
        context_menu.post(event.x_root, event.y_root)
    
    def select_output_folder(self):
        """اختيار مجلد الحفظ"""
        folder = filedialog.askdirectory(initialdir=self.output_folder)
        if folder:
            self.output_folder = folder
            self.save_settings()
            self.status_var.set(f"تم تعيين مجلد الحفظ: {folder}")
    
    def toggle_language(self):
        """تبديل لغة الواجهة"""
        # هذه الوظيفة ستكون مُعدة للتوسعة المستقبلية
        if self.language == "ar":
            self.language = "en"
            messagebox.showinfo("Language", "Interface language will be changed to English on next restart")
        else:
            self.language = "ar"
            messagebox.showinfo("اللغة", "سيتم تغيير لغة الواجهة إلى العربية عند إعادة التشغيل")
        self.save_settings()
    
    def clear_videos_frame(self):
        """مسح إطار الفيديوهات"""
        for widget in self.videos_frame.winfo_children():
            widget.destroy()
    
    def fetch_playlist(self):
        """جلب معلومات قائمة التشغيل"""
        url = self.playlist_url.get().strip()
        if not url:
            messagebox.showerror("خطأ", "الرجاء إدخال رابط قائمة تشغيل صالح")
            return
        
        self.status_var.set("جاري جلب معلومات القائمة...")
        self.progress_bar.set(0)
        self.clear_videos_frame()
        
        # تنفيذ العملية في خيط منفصل
        threading.Thread(target=self._fetch_playlist_thread, args=(url,), daemon=True).start()
    
    def _fetch_playlist_thread(self, url):
        """خيط جلب معلومات قائمة التشغيل"""
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    self.videos_info = []
                    total_videos = len(info['entries'])
                    
                    for i, entry in enumerate(info['entries']):
                        # تحديث شريط التقدم
                        progress = (i + 1) / total_videos
                        self.after(10, lambda p=progress: self.progress_bar.set(p))
                        
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        
                        # جلب معلومات إضافية للفيديو
                        video_info = ydl.extract_info(video_url, download=False)
                        
                        self.videos_info.append({
                            'id': entry['id'],
                            'title': video_info.get('title', 'بدون عنوان'),
                            'url': video_url,
                            'duration': video_info.get('duration', 0),
                            'thumbnail': video_info.get('thumbnail', ''),
                            'formats': video_info.get('formats', [])
                        })
                        
                        # تحديث الواجهة
                        self.after(10, lambda i=i, v=self.videos_info[-1]: 
                                  self.add_video_to_ui(v, i+1, total_videos))
                    
                    self.after(100, lambda: self.status_var.set(f"تم جلب {total_videos} فيديو"))
                    self.after(100, lambda: self.progress_bar.set(1))
                else:
                    # إذا كان رابط فيديو واحد وليس قائمة
                    video_info = ydl.extract_info(url, download=False)
                    self.videos_info = [{
                        'id': video_info['id'],
                        'title': video_info.get('title', 'بدون عنوان'),
                        'url': url,
                        'duration': video_info.get('duration', 0),
                        'thumbnail': video_info.get('thumbnail', ''),
                        'formats': video_info.get('formats', [])
                    }]
                    
                    self.after(10, lambda v=self.videos_info[0]: 
                              self.add_video_to_ui(v, 1, 1))
                    
                    self.after(100, lambda: self.status_var.set("تم جلب الفيديو"))
                    self.after(100, lambda: self.progress_bar.set(1))
        
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("خطأ", f"حدث خطأ أثناء جلب القائمة: {str(e)}"))
            self.after(0, lambda: self.status_var.set("حدث خطأ"))
            self.after(0, lambda: self.progress_bar.set(0))
    
    def format_duration(self, seconds):
        """تنسيق المدة الزمنية"""
        if not seconds:
            return "غير معروف"
        
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            return f"{int(minutes):02d}:{int(seconds):02d}"
    
    def add_video_to_ui(self, video, index, total):
        """إضافة فيديو إلى واجهة المستخدم"""
        video_frame = ctk.CTkFrame(self.videos_frame)
        video_frame.grid(row=index-1, column=0, padx=5, pady=5, sticky="ew")
        video_frame.grid_columnconfigure(1, weight=1)
        
        # رقم الفيديو
        index_label = ctk.CTkLabel(video_frame, text=f"{index}/{total}")
        index_label.grid(row=0, column=0, padx=5, pady=5)
        
        # عنوان الفيديو
        title_label = ctk.CTkLabel(
            video_frame, 
            text=video['title'],
            anchor="w",
            justify="left",
            wraplength=500
        )
        title_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # مدة الفيديو
        duration_label = ctk.CTkLabel(
            video_frame, 
            text=self.format_duration(video['duration'])
        )
        duration_label.grid(row=0, column=2, padx=5, pady=5)
        
        # خانة اختيار
        video['selected'] = tk.BooleanVar(value=True)
        select_checkbox = ctk.CTkCheckBox(
            video_frame, 
            text="",
            variable=video['selected'],
            onvalue=True,
            offvalue=False
        )
        select_checkbox.grid(row=0, column=3, padx=5, pady=5)
    
    def get_download_url(self, video, quality):
        """الحصول على رابط التحميل المباشر بالجودة المطلوبة"""
        formats = video.get('formats', [])
        
        # إذا كان المطلوب هو MP3
        if quality == "mp3":
            for fmt in formats:
                if fmt.get('ext') == 'm4a' and fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    return fmt.get('url', '')
        
        # البحث عن الفيديو بالجودة المطلوبة
        height = int(quality.replace('p', ''))
        
        # ترتيب التنسيقات حسب الجودة
        video_formats = [f for f in formats if f.get('height') == height and f.get('vcodec') != 'none']
        
        if video_formats:
            # اختيار التنسيق الأفضل
            best_format = max(video_formats, key=lambda x: x.get('tbr', 0))
            return best_format.get('url', '')
        
        # إذا لم يتم العثور على الجودة المطلوبة، ابحث عن أقرب جودة
        all_heights = sorted([f.get('height', 0) for f in formats if f.get('height') and f.get('vcodec') != 'none'])
        
        if not all_heights:
            return ''
        
        # البحث عن أقرب جودة
        closest_height = min(all_heights, key=lambda x: abs(x - height))
        video_formats = [f for f in formats if f.get('height') == closest_height and f.get('vcodec') != 'none']
        
        if video_formats:
            best_format = max(video_formats, key=lambda x: x.get('tbr', 0))
            return best_format.get('url', '')
        
        return ''
    
    def generate_links_file(self):
        """توليد ملف الروابط لـ IDM"""
        if not self.videos_info:
            messagebox.showerror("خطأ", "لا توجد فيديوهات لتوليد الروابط")
            return
        
        quality = self.selected_quality.get()
        selected_videos = [v for v in self.videos_info if v.get('selected', tk.BooleanVar()).get()]
        
        if not selected_videos:
            messagebox.showerror("خطأ", "الرجاء اختيار فيديو واحد على الأقل")
            return
        
        self.status_var.set("جاري توليد ملف الروابط...")
        self.progress_bar.set(0)
        
        # تنفيذ العملية في خيط منفصل
        threading.Thread(target=self._generate_links_thread, args=(selected_videos, quality), daemon=True).start()
    
    def _generate_links_thread(self, videos, quality):
        """خيط توليد ملف الروابط"""
        try:
            links_file = os.path.join(self.output_folder, "youtube_links.txt")
            
            with open(links_file, "w", encoding="utf-8") as f:
                total_videos = len(videos)
                
                for i, video in enumerate(videos):
                    # تحديث شريط التقدم
                    progress = (i + 1) / total_videos
                    self.after(10, lambda p=progress: self.progress_bar.set(p))
                    
                    # الحصول على رابط التحميل المباشر
                    download_url = self.get_download_url(video, quality)
                    
                    if download_url:
                        # تنسيق IDM: رابط التحميل + اسم الملف
                        ext = "mp3" if quality == "mp3" else "mp4"
                        filename = f"{video['title']}.{ext}"
                        
                        # كتابة الرابط بتنسيق IDM
                        f.write(f"{download_url}\n")
                        f.write(f"      filename={filename}\n")
                        f.write("\n")
            
            self.after(100, lambda: self.status_var.set(f"تم توليد ملف الروابط: {links_file}"))
            self.after(100, lambda: self.progress_bar.set(1))
            self.after(100, lambda: messagebox.showinfo("تم", f"تم توليد ملف الروابط بنجاح في:\n{links_file}"))
            
            # فتح المجلد الذي يحتوي على الملف
            self.after(200, lambda: os.startfile(os.path.dirname(links_file)))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("خطأ", f"حدث خطأ أثناء توليد ملف الروابط: {str(e)}"))
            self.after(0, lambda: self.status_var.set("حدث خطأ"))
            self.after(0, lambda: self.progress_bar.set(0))
    
    def download_videos(self):
        """تحميل الفيديوهات مباشرة"""
        if not self.videos_info:
            messagebox.showerror("خطأ", "لا توجد فيديوهات للتحميل")
            return
        
        quality = self.selected_quality.get()
        selected_videos = [v for v in self.videos_info if v.get('selected', tk.BooleanVar()).get()]
        
        if not selected_videos:
            messagebox.showerror("خطأ", "الرجاء اختيار فيديو واحد على الأقل")
            return
        
        self.status_var.set("جاري التحميل...")
        self.progress_bar.set(0)
        
        # تنفيذ العملية في خيط منفصل
        threading.Thread(target=self._download_videos_thread, args=(selected_videos, quality), daemon=True).start()
    
    def _download_videos_thread(self, videos, quality):
        """خيط تحميل الفيديوهات"""
        try:
            total_videos = len(videos)
            
            for i, video in enumerate(videos):
                # تحديث شريط التقدم
                progress = (i + 1) / total_videos
                self.after(10, lambda p=progress: self.progress_bar.set(p))
                
                # تحديد خيارات التحميل
                if quality == "mp3":
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
                    }
                else:
                    height = quality.replace('p', '')
                    ydl_opts = {
                        'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]',
                        'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
                    }
                
                # تحميل الفيديو
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.after(0, lambda v=video: self.status_var.set(f"جاري تحميل: {v['title']}"))
                    ydl.download([video['url']])
            
            self.after(100, lambda: self.status_var.set(f"تم تحميل {total_videos} فيديو"))
            self.after(100, lambda: self.progress_bar.set(1))
            self.after(100, lambda: messagebox.showinfo("تم", f"تم تحميل {total_videos} فيديو بنجاح في:\n{self.output_folder}"))
            
            # فتح المجلد
            self.after(200, lambda: os.startfile(self.output_folder))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("خطأ", f"حدث خطأ أثناء التحميل: {str(e)}"))
            self.after(0, lambda: self.status_var.set("حدث خطأ"))
            self.after(0, lambda: self.progress_bar.set(0))

if __name__ == "__main__":
    app = YoutubePlaylistDownloader()
    app.mainloop()

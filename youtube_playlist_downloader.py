import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
from PIL import Image, ImageTk
import json
import pyperclip
import webbrowser
import time

# تعيين الثيم الافتراضي للتطبيق
ctk.set_appearance_mode("System")  # الوضع: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # السمة: "blue", "green", "dark-blue"

# قاموس الترجمات للدعم الكامل للغتين العربية والإنجليزية
translations = {
    "ar": {
        # العناوين الرئيسية
        "app_title": "مُنزِّل قوائم تشغيل يوتيوب",
        "playlist_url": "رابط قائمة التشغيل:",
        "fetch_playlist": "جلب القائمة",
        "quality": "الجودة:",
        "select_folder": "اختيار مجلد الحفظ",
        "switch_language": "English",
        "generate_links": "توليد ملف الروابط (IDM)",
        "download_direct": "تحميل مباشر",
        "ready": "جاهز",
        
        # رسائل الحالة
        "fetching_playlist": "جاري جلب معلومات القائمة...",
        "fetched_videos": "تم جلب {} فيديو",
        "fetched_video": "تم جلب الفيديو",
        "generating_links": "جاري توليد ملف الروابط...",
        "generated_links": "تم توليد ملف الروابط: {}",
        "downloading": "جاري تحميل: {}",
        "downloaded_videos": "تم تحميل {} فيديو",
        "set_folder": "تم تعيين مجلد الحفظ: {}",
        
        # رسائل الخطأ
        "error": "خطأ",
        "error_url": "الرجاء إدخال رابط قائمة تشغيل صالح",
        "error_no_videos": "لا توجد فيديوهات لتوليد الروابط",
        "error_no_selected": "الرجاء اختيار فيديو واحد على الأقل",
        "error_fetch": "حدث خطأ أثناء جلب القائمة: {}",
        "error_generate": "حدث خطأ أثناء توليد ملف الروابط: {}",
        "error_download": "حدث خطأ أثناء التحميل: {}",
        
        # رسائل النجاح
        "success": "تم",
        "success_links": "تم توليد ملف الروابط بنجاح في:\n{}",
        "success_download": "تم تحميل {} فيديو بنجاح في:\n{}",
        
        # قائمة السياق
        "paste": "لصق",
        "copy": "نسخ",
        "cut": "قص",
        
        # رسائل تغيير اللغة
        "language_changed": "سيتم تغيير لغة الواجهة إلى العربية عند إعادة التشغيل",
        
        # أزرار إضافية
        "select_all": "تحديد الكل",
        "deselect_all": "إلغاء تحديد الكل",
        "settings": "الإعدادات",
        "about": "حول",
        "dark_mode": "الوضع الداكن",
        "light_mode": "الوضع الفاتح",
        "system_mode": "وضع النظام",
        "theme": "السمة:",
        
        # الإعدادات
        "settings_title": "الإعدادات",
        "appearance": "المظهر",
        "language": "اللغة:",
        "default_quality": "الجودة الافتراضية:",
        "save_settings": "حفظ الإعدادات",
        "cancel": "إلغاء",
        
        # حول
        "about_title": "حول التطبيق",
        "about_description": "مُنزِّل قوائم تشغيل يوتيوب هو تطبيق مفتوح المصدر يساعدك على استخراج روابط التحميل المباشرة من قوائم تشغيل يوتيوب وتوليد ملف متوافق مع برنامج Internet Download Manager (IDM).",
        "version": "الإصدار: 1.0.0",
        "developer": "المطور: TARIQIRAQ2015",
        "close": "إغلاق"
    },
    "en": {
        # Main Titles
        "app_title": "YouTube Playlist Downloader",
        "playlist_url": "Playlist URL:",
        "fetch_playlist": "Fetch Playlist",
        "quality": "Quality:",
        "select_folder": "Select Folder",
        "switch_language": "عربي",
        "generate_links": "Generate Links File (IDM)",
        "download_direct": "Download Directly",
        "ready": "Ready",
        
        # Status Messages
        "fetching_playlist": "Fetching playlist information...",
        "fetched_videos": "Fetched {} videos",
        "fetched_video": "Video fetched",
        "generating_links": "Generating links file...",
        "generated_links": "Links file generated: {}",
        "downloading": "Downloading: {}",
        "downloaded_videos": "Downloaded {} videos",
        "set_folder": "Output folder set to: {}",
        
        # Error Messages
        "error": "Error",
        "error_url": "Please enter a valid playlist URL",
        "error_no_videos": "No videos to generate links",
        "error_no_selected": "Please select at least one video",
        "error_fetch": "Error fetching playlist: {}",
        "error_generate": "Error generating links file: {}",
        "error_download": "Error downloading: {}",
        
        # Success Messages
        "success": "Success",
        "success_links": "Links file successfully generated at:\n{}",
        "success_download": "Successfully downloaded {} videos to:\n{}",
        
        # Context Menu
        "paste": "Paste",
        "copy": "Copy",
        "cut": "Cut",
        
        # Language Change Messages
        "language_changed": "Interface language will be changed to English on next restart",
        
        # Additional Buttons
        "select_all": "Select All",
        "deselect_all": "Deselect All",
        "settings": "Settings",
        "about": "About",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "system_mode": "System Mode",
        "theme": "Theme:",
        
        # Settings
        "settings_title": "Settings",
        "appearance": "Appearance",
        "language": "Language:",
        "default_quality": "Default Quality:",
        "save_settings": "Save Settings",
        "cancel": "Cancel",
        
        # About
        "about_title": "About",
        "about_description": "YouTube Playlist Downloader is an open-source application that helps you extract direct download links from YouTube playlists and generate a file compatible with Internet Download Manager (IDM).",
        "version": "Version: 1.0.0",
        "developer": "Developer: TARIQIRAQ2015",
        "close": "Close"
    }
}

class YoutubePlaylistDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # إعداد النافذة الرئيسية
        self.geometry("1000x650")
        self.minsize(900, 600)
        
        # متغيرات التطبيق
        self.playlist_url = ctk.StringVar()
        self.selected_quality = ctk.StringVar(value="720p")
        self.videos_info = []
        self.output_folder = os.path.expanduser("~/Downloads")
        self.language = "ar"  # الافتراضي: العربية
        self.appearance_mode = ctk.StringVar(value="System")
        self.color_theme = ctk.StringVar(value="blue")
        
        # محاولة تحميل الإعدادات
        self.load_settings()
        
        # تطبيق الإعدادات
        self.apply_settings()
        
        # إنشاء واجهة المستخدم
        self.create_ui()
        
    def apply_settings(self):
        """تطبيق إعدادات المستخدم"""
        # تطبيق المظهر واللغة
        ctk.set_appearance_mode(self.appearance_mode.get())
        ctk.set_default_color_theme(self.color_theme.get())
        
        # تعيين عنوان التطبيق حسب اللغة
        self.title(translations[self.language]["app_title"])
        
        # تطبيق اتجاه النص حسب اللغة (RTL للعربية، LTR للإنجليزية)
        if hasattr(self, "main_frame"):
            if self.language == "ar":
                for widget in self.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(justify="right")
            else:
                for widget in self.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(justify="left")
    
    def load_settings(self):
        """تحميل إعدادات المستخدم من ملف"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.selected_quality.set(settings.get("preferred_quality", "720p"))
                    self.output_folder = settings.get("output_folder", os.path.expanduser("~/Downloads"))
                    self.language = settings.get("language", "ar")
                    self.appearance_mode.set(settings.get("appearance_mode", "System"))
                    self.color_theme.set(settings.get("color_theme", "blue"))
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
    
    def save_settings(self):
        """حفظ إعدادات المستخدم إلى ملف"""
        try:
            settings = {
                "preferred_quality": self.selected_quality.get(),
                "output_folder": self.output_folder,
                "language": self.language,
                "appearance_mode": self.appearance_mode.get(),
                "color_theme": self.color_theme.get()
            }
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"خطأ في حفظ الإعدادات: {e}")
            
    def get_text(self, key):
        """الحصول على النص المترجم حسب اللغة الحالية"""
        return translations[self.language].get(key, key)
    
    def create_ui(self):
        """إنشاء واجهة المستخدم الرئيسية"""
        # إنشاء الإطار الرئيسي
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # إنشاء شريط القوائم
        self.create_menu()
        
        # الإطار الرئيسي
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
    def create_menu(self):
        """إنشاء شريط القوائم"""
        menu_bar = tk.Menu(self)
        self.configure(menu=menu_bar)
        
        # قائمة الملف
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label=self.get_text("file") if hasattr(self, "get_text") else "ملف", menu=file_menu)
        file_menu.add_command(label=self.get_text("settings") if hasattr(self, "get_text") else "الإعدادات", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label=self.get_text("exit") if hasattr(self, "get_text") else "خروج", command=self.quit)
        
        # قائمة المظهر
        appearance_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label=self.get_text("appearance") if hasattr(self, "get_text") else "المظهر", menu=appearance_menu)
        appearance_menu.add_command(label=self.get_text("light_mode") if hasattr(self, "get_text") else "الوضع الفاتح", command=lambda: self.change_appearance_mode("Light"))
        appearance_menu.add_command(label=self.get_text("dark_mode") if hasattr(self, "get_text") else "الوضع الداكن", command=lambda: self.change_appearance_mode("Dark"))
        appearance_menu.add_command(label=self.get_text("system_mode") if hasattr(self, "get_text") else "وضع النظام", command=lambda: self.change_appearance_mode("System"))
        
        # قائمة المساعدة
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label=self.get_text("help") if hasattr(self, "get_text") else "مساعدة", menu=help_menu)
        help_menu.add_command(label=self.get_text("about") if hasattr(self, "get_text") else "حول", command=self.show_about)
        
    def change_appearance_mode(self, mode):
        """تغيير وضع المظهر"""
        ctk.set_appearance_mode(mode)
        self.appearance_mode.set(mode)
        self.save_settings()
    
    def open_settings(self):
        """فتح نافذة الإعدادات"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title(self.get_text("settings_title"))
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        settings_window.grab_set()  # جعل النافذة مودال
        
        # إطار الإعدادات
        settings_frame = ctk.CTkFrame(settings_window)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # عنوان
        title_label = ctk.CTkLabel(settings_frame, text=self.get_text("settings_title"), font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # اللغة
        language_frame = ctk.CTkFrame(settings_frame)
        language_frame.pack(fill="x", padx=10, pady=10)
        
        language_label = ctk.CTkLabel(language_frame, text=self.get_text("language"), width=120)
        language_label.pack(side="left", padx=10)
        
        language_var = ctk.StringVar(value=self.language)
        language_menu = ctk.CTkOptionMenu(language_frame, values=["ar", "en"], variable=language_var)
        language_menu.pack(side="left", padx=10, fill="x", expand=True)
        
        # الجودة الافتراضية
        quality_frame = ctk.CTkFrame(settings_frame)
        quality_frame.pack(fill="x", padx=10, pady=10)
        
        quality_label = ctk.CTkLabel(quality_frame, text=self.get_text("default_quality"), width=120)
        quality_label.pack(side="left", padx=10)
        
        quality_var = ctk.StringVar(value=self.selected_quality.get())
        quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "mp3"]
        quality_menu = ctk.CTkOptionMenu(quality_frame, values=quality_options, variable=quality_var)
        quality_menu.pack(side="left", padx=10, fill="x", expand=True)
        
        # المظهر
        theme_frame = ctk.CTkFrame(settings_frame)
        theme_frame.pack(fill="x", padx=10, pady=10)
        
        theme_label = ctk.CTkLabel(theme_frame, text=self.get_text("theme"), width=120)
        theme_label.pack(side="left", padx=10)
        
        theme_var = ctk.StringVar(value=self.color_theme.get())
        theme_menu = ctk.CTkOptionMenu(theme_frame, values=["blue", "green", "dark-blue"], variable=theme_var)
        theme_menu.pack(side="left", padx=10, fill="x", expand=True)
        
        # أزرار الإجراءات
        buttons_frame = ctk.CTkFrame(settings_frame)
        buttons_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        save_button = ctk.CTkButton(
            buttons_frame, 
            text=self.get_text("save_settings"),
            command=lambda: self.save_settings_dialog(settings_window, language_var.get(), quality_var.get(), theme_var.get())
        )
        save_button.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        cancel_button = ctk.CTkButton(
            buttons_frame, 
            text=self.get_text("cancel"),
            command=settings_window.destroy
        )
        cancel_button.pack(side="left", padx=10, pady=10, expand=True, fill="x")
    
    def save_settings_dialog(self, window, language, quality, theme):
        """حفظ الإعدادات من نافذة الإعدادات"""
        # حفظ الإعدادات الجديدة
        self.language = language
        self.selected_quality.set(quality)
        self.color_theme.set(theme)
        
        # تطبيق الإعدادات
        ctk.set_default_color_theme(theme)
        self.save_settings()
        
        # إغلاق النافذة
        window.destroy()
        
        # إظهار رسالة تأكيد
        messagebox.showinfo(
            self.get_text("success"),
            self.get_text("language_changed")
        )
    
    def show_about(self):
        """عرض معلومات حول التطبيق"""
        about_window = ctk.CTkToplevel(self)
        about_window.title(self.get_text("about_title"))
        about_window.geometry("500x300")
        about_window.resizable(False, False)
        about_window.grab_set()  # جعل النافذة مودال
        
        # إطار المعلومات
        about_frame = ctk.CTkFrame(about_window)
        about_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # عنوان
        title_label = ctk.CTkLabel(
            about_frame, 
            text=self.get_text("app_title"), 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # وصف
        desc_label = ctk.CTkLabel(
            about_frame, 
            text=self.get_text("about_description"),
            wraplength=450
        )
        desc_label.pack(pady=10)
        
        # معلومات إضافية
        version_label = ctk.CTkLabel(about_frame, text=self.get_text("version"))
        version_label.pack(pady=5)
        
        developer_label = ctk.CTkLabel(about_frame, text=self.get_text("developer"))
        developer_label.pack(pady=5)
        
        # زر إغلاق
        close_button = ctk.CTkButton(
            about_frame, 
            text=self.get_text("close"),
            command=about_window.destroy
        )
        close_button.pack(pady=20)
        
        # إطار إدخال الرابط
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        # عنوان التطبيق
        title_label = ctk.CTkLabel(
            input_frame, 
            text=self.get_text("app_title"),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 25), sticky="ew")
        
        # حقل إدخال رابط قائمة التشغيل
        url_label = ctk.CTkLabel(input_frame, text=self.get_text("playlist_url"), font=ctk.CTkFont(size=14))
        url_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")
        
        # إنشاء حقل إدخال مخصص مع دعم النسخ واللصق
        url_entry = ctk.CTkEntry(input_frame, textvariable=self.playlist_url, width=450, height=35, font=ctk.CTkFont(size=13))
        url_entry.grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        
        # إضافة دعم النسخ واللصق باستخدام اختصارات لوحة المفاتيح
        url_entry.bind("<Control-v>", lambda event: self.paste_clipboard(url_entry))
        url_entry.bind("<Control-c>", lambda event: self.copy_to_clipboard(url_entry.get()))
        url_entry.bind("<Control-x>", lambda event: self.cut_from_entry(url_entry))
        url_entry.bind("<Button-3>", self.show_context_menu)  # قائمة النقر بزر الماوس الأيمن
        
        # زر جلب القائمة بتصميم أكثر جاذبية
        fetch_button = ctk.CTkButton(
            input_frame, 
            text=self.get_text("fetch_playlist"), 
            command=self.fetch_playlist,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35,
            corner_radius=8
        )
        fetch_button.grid(row=1, column=2, padx=15, pady=15)
        
    # دوال النسخ واللصق
    def paste_clipboard(self, entry_widget):
        """لصق من الحافظة إلى حقل الإدخال"""
        try:
            entry_widget.insert("insert", pyperclip.paste())
        except Exception as e:
            print(f"خطأ في اللصق: {e}")
    
    def copy_to_clipboard(self, text):
        """نسخ النص إلى الحافظة"""
        try:
            pyperclip.copy(text)
        except Exception as e:
            print(f"خطأ في النسخ: {e}")
    
    def cut_from_entry(self, entry_widget):
        """قص من حقل الإدخال"""
        try:
            if entry_widget.selection_get():
                self.copy_to_clipboard(entry_widget.selection_get())
                entry_widget.delete("sel.first", "sel.last")
        except Exception as e:
            print(f"خطأ في القص: {e}")
        
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

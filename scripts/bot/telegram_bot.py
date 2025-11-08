"""
Interactive Telegram Bot for KKTC Emlak Scraper
================================================
Kullanıcıdan komut alabilir ve status raporlar
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from typing import Optional, Dict, Any

class TelegramBot:
    """Interactive Telegram Bot with command handling"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = 0
        self.commands = {
            '/start': self.cmd_start,
            '/status': self.cmd_status,
            '/files': self.cmd_files,
            '/progress': self.cmd_progress,
            '/disk': self.cmd_disk,
            '/health': self.cmd_health,
            '/help': self.cmd_help,
        }
    
    def send_message(self, text: str, parse_mode: str = 'Markdown'):
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def get_updates(self) -> list:
        """Get new messages from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('result', [])
            return []
        except Exception as e:
            print(f"Get updates error: {e}")
            return []
    
    def process_message(self, message: Dict[str, Any]):
        """Process incoming message"""
        text = message.get('text', '').strip()
        chat_id = message.get('chat', {}).get('id')
        
        # Only respond to authorized chat
        if str(chat_id) != str(self.chat_id):
            return
        
        print(f"📩 Received: {text}")
        
        # Find and execute command
        for cmd, handler in self.commands.items():
            if text.startswith(cmd):
                handler()
                return
        
        # Unknown command
        self.send_message(
            "❓ Bilinmeyen komut!\n\n"
            "Kullanılabilir komutlar için /help yazın"
        )
    
    def cmd_start(self):
        """Start command"""
        msg = (
            "🍓 *KKTC Emlak Scraper Bot*\n\n"
            "Raspberry Pi 5 üzerinde çalışan scraper'ı kontrol edebilirsiniz.\n\n"
            "📋 Komutlar için: /help"
        )
        self.send_message(msg)
    
    def cmd_help(self):
        """Help command"""
        msg = (
            "📚 *Kullanılabilir Komutlar:*\n\n"
            "📊 `/status` - Genel durum\n"
            "📄 `/files` - Toplanan dosyalar\n"
            "📈 `/progress` - Scan ilerlemesi\n"
            "💾 `/disk` - Disk kullanımı\n"
            "🩺 `/health` - Sistem sağlığı (CPU/RAM/Sıcaklık)\n"
            "❓ `/help` - Bu mesaj\n\n"
            "_Herhangi bir komut 24/7 kullanılabilir_"
        )
        self.send_message(msg)
    
    def cmd_status(self):
        """Status command - read from state file"""
        try:
            # Read state file
            state_file = Path('/app/data/cache/scraper_state.json')
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                completed = len(state.get('completed', []))
                failed = len(state.get('failed', []))
                current = state.get('current', {})
                
                if current:
                    status = "🏃 *ÇALIŞIYOR*"
                    current_name = current.get('name', 'N/A')
                else:
                    status = "⏸️ *BEKLEMEDE*"
                    current_name = "Yok"
                
                msg = (
                    f"{status}\n\n"
                    f"📊 *İlerleme:*\n"
                    f"   ✅ Tamamlanan: {completed}\n"
                    f"   ❌ Başarısız: {failed}\n"
                    f"   ⏳ Şu an: {current_name}\n\n"
                    f"🕐 Son güncelleme: {state.get('last_updated', 'N/A')[:19]}"
                )
            else:
                msg = "⚠️ State dosyası bulunamadı!\n\nScan henüz başlatılmadı."
            
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Hata: {str(e)}")
    
    def cmd_files(self):
        """Files command - count HTML files"""
        try:
            listings_dir = Path('/app/data/raw/listings')
            if listings_dir.exists():
                files = list(listings_dir.glob('*.html'))
                count = len(files)
                
                # Calculate size
                total_size = sum(f.stat().st_size for f in files)
                size_mb = total_size / 1024 / 1024
                
                msg = (
                    f"📄 *Toplanan Dosyalar:*\n\n"
                    f"   Toplam: {count:,} HTML dosya\n"
                    f"   Boyut: {size_mb:.1f} MB\n\n"
                    f"📁 Konum:\n"
                    f"   `/app/data/raw/listings/`\n\n"
                    f"💾 Pi'de:\n"
                    f"   `/home/ekrem/projects/emlak-scraper/data/raw/listings/`"
                )
            else:
                msg = "⚠️ Listings dizini bulunamadı!\n\nHenüz dosya toplanmadı."
            
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Hata: {str(e)}")
    
    def cmd_progress(self):
        """Progress command - detailed progress info"""
        try:
            # Try to read from state file first
            state_file = Path('/app/data/cache/scraper_state.json')
            state_data = None
            
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
            
            # Check for real-time batch progress file (updated every batch)
            progress_file = Path('/app/data/cache/batch_progress.json')
            batch_data = None
            
            if progress_file.exists():
                try:
                    with open(progress_file, 'r', encoding='utf-8') as f:
                        batch_data = json.load(f)
                except Exception as e:
                    print(f"Error reading progress file: {e}")
            
            # Build message with real-time data if available
            if batch_data:
                current_batch = batch_data.get('current_batch', 0)
                total_batches = batch_data.get('total_batches', 1)
                progress_pct = batch_data.get('progress_percent', 0)
                elapsed = batch_data.get('elapsed_minutes', 0)
                eta = batch_data.get('eta_minutes', 0)
                
                # Create progress bar
                bar_length = 10
                filled = int(bar_length * progress_pct / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                msg = (
                    f"📈 *Scan İlerlemesi* (Real-time)\n\n"
                    f"{bar} {progress_pct:.1f}%\n\n"
                    f"📊 *Batch İlerlemesi:*\n"
                    f"   🔄 Batch: {current_batch}/{total_batches}\n"
                    f"   ⏱️ Geçen: {elapsed:.1f} dakika\n"
                    f"   🎯 Kalan: {eta:.1f} dakika\n\n"
                )
                
                # Add state info if available
                if state_data:
                    completed = len(state_data.get('completed', []))
                    failed = len(state_data.get('failed', []))
                    current = state_data.get('current', {})
                    
                    msg += f"📋 *Config Durumu:*\n"
                    msg += f"   ✅ Tamamlanan: {completed}\n"
                    msg += f"   ❌ Başarısız: {failed}\n"
                    
                    if current:
                        msg += f"   ⏳ Şu an: {current.get('name', 'N/A')}\n"
                
                self.send_message(msg)
                return
            
            # Fallback to state file only
            if state_data:
                completed = state_data.get('completed', [])
                failed = state_data.get('failed', [])
                current = state_data.get('current', {})
                
                total_configs = 72
                completed_count = len(completed)
                failed_count = len(failed)
                remaining = total_configs - completed_count - failed_count
                
                if current:
                    remaining -= 1
                
                progress_pct = (completed_count / total_configs) * 100
                
                bar_length = 10
                filled = int(bar_length * progress_pct / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                msg = (
                    f"📈 *Scan İlerlemesi:*\n\n"
                    f"{bar} {progress_pct:.1f}%\n\n"
                    f"📊 *Detaylar:*\n"
                    f"   ✅ Tamamlanan: {completed_count}/{total_configs}\n"
                    f"   ❌ Başarısız: {failed_count}\n"
                    f"   ⏳ Kalan: {remaining}\n\n"
                )
                
                if current:
                    msg += f"🔄 *Şu an çalışan:*\n   {current.get('name', 'N/A')}\n\n"
                
                started = state_data.get('started_at', '')
                if started:
                    msg += f"🕐 Başlangıç: {started[:19]}\n"
                
                if completed:
                    last = completed[-1]
                    msg += f"✅ Son tamamlanan: {last.get('name', 'N/A')}\n"
            else:
                msg = "⚠️ İlerleme bilgisi bulunamadı!\n\nScan çalışmıyor olabilir."
            
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Hata: {str(e)}")
    
    def cmd_disk(self):
        """Disk command - disk usage info"""
        try:
            import shutil
            
            # Get disk usage
            total, used, free = shutil.disk_usage('/app/data')
            
            total_gb = total / (1024 ** 3)
            used_gb = used / (1024 ** 3)
            free_gb = free / (1024 ** 3)
            used_pct = (used / total) * 100
            
            # Status emoji
            if used_pct < 70:
                status = "✅ Normal"
            elif used_pct < 85:
                status = "⚠️ Dikkat"
            else:
                status = "❌ Kritik"
            
            msg = (
                f"💾 *Disk Kullanımı:*\n\n"
                f"   Kullanılan: {used_gb:.1f} GB\n"
                f"   Serbest: {free_gb:.1f} GB\n"
                f"   Toplam: {total_gb:.1f} GB\n"
                f"   Oran: {used_pct:.1f}%\n\n"
                f"📊 Durum: {status}"
            )
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Hata: {str(e)}")
    
    def cmd_health(self):
        """Health command - system health check"""
        try:
            import subprocess
            
            # Temperature (if available on Pi)
            try:
                temp_result = subprocess.run(
                    ['vcgencmd', 'measure_temp'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                temp = temp_result.stdout.strip().replace("temp=", "").replace("'C", "°C")
            except:
                temp = "N/A"
            
            # Memory
            import psutil
            mem = psutil.virtual_memory()
            mem_used_gb = mem.used / (1024 ** 3)
            mem_total_gb = mem.total / (1024 ** 3)
            mem_pct = mem.percent
            
            # CPU
            cpu_pct = psutil.cpu_percent(interval=1)
            
            # Disk
            disk = psutil.disk_usage('/app/data')
            disk_pct = disk.percent
            
            msg = (
                f"🩺 *Sistem Sağlığı:*\n\n"
                f"🌡️ *Sıcaklık:* {temp}\n"
                f"💻 *CPU:* {cpu_pct}%\n"
                f"💾 *RAM:* {mem_used_gb:.1f}/{mem_total_gb:.1f} GB ({mem_pct}%)\n"
                f"💿 *Disk:* {disk_pct}% kullanımda\n\n"
                f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.send_message(msg)
        except Exception as e:
            self.send_message(f"❌ Hata: {str(e)}")
    
    def run_polling(self, interval: int = 3):
        """Start polling for messages"""
        print(f"🤖 Bot başlatıldı! Chat ID: {self.chat_id}")
        print("📡 Mesajlar dinleniyor...")
        print("🛑 Durdurmak için Ctrl+C")
        print()
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update.get('update_id', 0)
                    
                    if 'message' in update:
                        self.process_message(update['message'])
                
                time.sleep(interval)
            
            except KeyboardInterrupt:
                print("\n🛑 Bot durduruldu")
                break
            except Exception as e:
                print(f"❌ Polling error: {e}")
                time.sleep(10)


# Main execution
if __name__ == "__main__":
    # Load from environment
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8567356269:AAH839-_n3--eykejU4TQBQ4eQS8FY_10yE')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '8386214866')
    
    if not TOKEN or not CHAT_ID:
        print("❌ TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID gerekli!")
        exit(1)
    
    bot = TelegramBot(TOKEN, CHAT_ID)
    
    # Send startup message
    bot.send_message(
        "🤖 *Bot Başlatıldı!*\n\n"
        "Artık komutları dinliyorum.\n"
        "Komutlar için: /help"
    )
    
    # Start polling
    bot.run_polling()

"""
Notification Manager for KKTC Emlak Scraper
Supports: Telegram Bot, Email (SMTP)
"""

import os
import time
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests module not available - Telegram notifications disabled")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available - using environment variables only")

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Manages notifications via Telegram and Email
    
    Configuration via environment variables:
        TELEGRAM_BOT_TOKEN - Telegram bot token
        TELEGRAM_CHAT_ID - Chat ID to send messages
        SMTP_HOST - SMTP server (default: smtp.gmail.com)
        SMTP_PORT - SMTP port (default: 587)
        SMTP_USER - Email username
        SMTP_PASSWORD - Email password (use app password for Gmail)
        NOTIFY_EMAIL - Recipient email address
        ENABLE_TELEGRAM - Enable/disable Telegram (default: true)
        ENABLE_EMAIL - Enable/disable Email (default: true)
    """
    
    def __init__(self):
        # Telegram config
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.enable_telegram = os.getenv('ENABLE_TELEGRAM', 'true').lower() == 'true'
        
        # Email config
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.notify_email = os.getenv('NOTIFY_EMAIL', '')
        self.enable_email = os.getenv('ENABLE_EMAIL', 'true').lower() == 'true'
        
        # Notification settings
        self.notify_on_start = os.getenv('NOTIFY_ON_START', 'true').lower() == 'true'
        self.notify_on_complete = os.getenv('NOTIFY_ON_COMPLETE', 'true').lower() == 'true'
        self.notify_on_error = os.getenv('NOTIFY_ON_ERROR', 'true').lower() == 'true'
        self.notify_every_n = int(os.getenv('NOTIFY_EVERY_N_CONFIGS', '5'))
        
        # Rate limiting
        self.last_telegram_time = 0
        self.min_telegram_interval = 1.0  # seconds
        
        # Validate config
        self._validate_config()
    
    def _validate_config(self):
        """Validate notification configuration"""
        if self.enable_telegram and not self.telegram_token:
            logger.warning("Telegram enabled but TELEGRAM_BOT_TOKEN not set")
            self.enable_telegram = False
        
        if self.enable_email and not self.smtp_user:
            logger.warning("Email enabled but SMTP_USER not set")
            self.enable_email = False
        
        if not (self.enable_telegram or self.enable_email):
            logger.warning("All notification methods disabled!")
    
    def send_telegram(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """
        Send Telegram message
        
        Args:
            message: Message text
            parse_mode: 'Markdown' or 'HTML'
        
        Returns:
            bool: Success status
        """
        if not self.enable_telegram or not REQUESTS_AVAILABLE:
            return False
        
        # Rate limiting
        now = time.time()
        if now - self.last_telegram_time < self.min_telegram_interval:
            time.sleep(self.min_telegram_interval)
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=5)
            self.last_telegram_time = time.time()
            
            if response.status_code == 200:
                logger.debug(f"Telegram sent: {message[:50]}...")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False
    
    def send_email(self, subject: str, body: str, html: bool = False) -> bool:
        """
        Send email via SMTP
        
        Args:
            subject: Email subject
            body: Email body (text or HTML)
            html: Whether body is HTML
        
        Returns:
            bool: Success status
        """
        if not self.enable_email:
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = self.notify_email
            msg['Subject'] = subject
            
            if html:
                part = MIMEText(body, 'html')
            else:
                part = MIMEText(body, 'plain')
            
            msg.attach(part)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.debug(f"Email sent: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False
    
    def notify_scan_started(self, total_configs: int):
        """Notify when scan starts"""
        if not self.notify_on_start:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Telegram
        telegram_msg = f"""
🚀 *Scan Started*

📊 Total configs: {total_configs}
🕐 Time: {timestamp}
🍓 Host: Raspberry Pi 5

_Monitoring in progress..._
"""
        self.send_telegram(telegram_msg.strip())
        
        # Email
        email_body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #4CAF50;">🚀 KKTC Emlak Scraper - Scan Started</h2>
    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
        <p><strong>Total Configs:</strong> {total_configs}</p>
        <p><strong>Start Time:</strong> {timestamp}</p>
        <p><strong>Host:</strong> Raspberry Pi 5</p>
    </div>
    <p>You will receive updates every {self.notify_every_n} configs and at completion.</p>
</body>
</html>
"""
        self.send_email(
            subject=f"🚀 Scraper Started - {total_configs} configs",
            body=email_body,
            html=True
        )
    
    def notify_config_completed(self, config_name: str, file_count: int, 
                               completed: int, total: int, duration: float):
        """Notify when a config completes"""
        # Only notify every N configs
        if completed % self.notify_every_n != 0:
            return
        
        if not self.notify_on_complete:
            return
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        duration_min = duration / 60
        
        # Telegram
        telegram_msg = f"""
✅ *Progress Update*

📍 Latest: {config_name}
📄 Files: {file_count}
📊 Progress: {completed}/{total} configs
⏱️ Duration: {duration_min:.1f} min
🕐 {timestamp}
"""
        self.send_telegram(telegram_msg.strip())
    
    def notify_config_failed(self, config_name: str, error: str, 
                            completed: int, total: int):
        """Notify when a config fails"""
        if not self.notify_on_error:
            return
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Telegram
        telegram_msg = f"""
❌ *Config Failed*

📍 Config: {config_name}
⚠️ Error: {error[:100]}
📊 Progress: {completed}/{total}
🕐 {timestamp}

_Continuing with next config..._
"""
        self.send_telegram(telegram_msg.strip())
    
    def notify_scan_finished(self, stats: Dict[str, Any]):
        """
        Notify when entire scan finishes
        
        Args:
            stats: Dictionary with scan statistics
                - total_configs: int
                - completed: int
                - failed: int
                - total_files: int
                - duration_minutes: float
                - data_size_mb: float
        """
        if not self.notify_on_complete:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Telegram
        telegram_msg = f"""
🎉 *Scan Completed!*

✅ Completed: {stats.get('completed', 0)}/{stats.get('total_configs', 0)}
❌ Failed: {stats.get('failed', 0)}
📄 Total Files: {stats.get('total_files', 0):,}
💾 Data Size: {stats.get('data_size_mb', 0):.1f} MB
⏱️ Duration: {stats.get('duration_minutes', 0):.1f} min
🕐 {timestamp}

_Ready for parsing!_
"""
        self.send_telegram(telegram_msg.strip())
        
        # Email (detailed)
        email_body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #4CAF50;">🎉 Scan Completed Successfully!</h2>
    
    <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3>📊 Statistics</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px;"><strong>Total Configs:</strong></td>
                <td style="padding: 8px;">{stats.get('total_configs', 0)}</td>
            </tr>
            <tr style="background: #f5f5f5;">
                <td style="padding: 8px;"><strong>Completed:</strong></td>
                <td style="padding: 8px; color: green;">{stats.get('completed', 0)}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Failed:</strong></td>
                <td style="padding: 8px; color: red;">{stats.get('failed', 0)}</td>
            </tr>
            <tr style="background: #f5f5f5;">
                <td style="padding: 8px;"><strong>Total Files:</strong></td>
                <td style="padding: 8px;">{stats.get('total_files', 0):,}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Data Size:</strong></td>
                <td style="padding: 8px;">{stats.get('data_size_mb', 0):.1f} MB</td>
            </tr>
            <tr style="background: #f5f5f5;">
                <td style="padding: 8px;"><strong>Duration:</strong></td>
                <td style="padding: 8px;">{stats.get('duration_minutes', 0):.1f} minutes</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Completion Time:</strong></td>
                <td style="padding: 8px;">{timestamp}</td>
            </tr>
        </table>
    </div>
    
    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3>🎬 Next Steps</h3>
        <ol>
            <li>Download data from Raspberry Pi</li>
            <li>Run HTML parser to generate CSV</li>
            <li>Verify data quality</li>
            <li>Export to Excel</li>
        </ol>
    </div>
    
    <p style="color: #666; font-size: 12px;">
        Host: Raspberry Pi 5<br>
        Project: KKTC Emlak Scraper v2.1.0
    </p>
</body>
</html>
"""
        self.send_email(
            subject=f"🎉 Scan Completed - {stats.get('total_files', 0):,} files collected",
            body=email_body,
            html=True
        )
    
    def notify_disk_warning(self, usage_percent: int, available_gb: float):
        """Notify when disk usage is high"""
        if usage_percent < 80:
            return
        
        telegram_msg = f"""
⚠️ *Disk Space Warning*

💾 Usage: {usage_percent}%
📊 Available: {available_gb:.1f} GB

_Consider cleanup if needed_
"""
        self.send_telegram(telegram_msg.strip())


# Singleton instance
_notifier: Optional[NotificationManager] = None


def get_notifier() -> NotificationManager:
    """Get singleton NotificationManager instance"""
    global _notifier
    if _notifier is None:
        _notifier = NotificationManager()
    return _notifier


# Convenience functions
def notify_scan_started(total_configs: int):
    """Shortcut to notify scan start"""
    get_notifier().notify_scan_started(total_configs)


def notify_config_completed(config_name: str, file_count: int,
                           completed: int, total: int, duration: float):
    """Shortcut to notify config completion"""
    get_notifier().notify_config_completed(
        config_name, file_count, completed, total, duration
    )


def notify_config_failed(config_name: str, error: str,
                        completed: int, total: int):
    """Shortcut to notify config failure"""
    get_notifier().notify_config_failed(config_name, error, completed, total)


def notify_scan_finished(stats: Dict[str, Any]):
    """Shortcut to notify scan finish"""
    get_notifier().notify_scan_finished(stats)


def notify_disk_warning(usage_percent: int, available_gb: float):
    """Shortcut to notify disk warning"""
    get_notifier().notify_disk_warning(usage_percent, available_gb)

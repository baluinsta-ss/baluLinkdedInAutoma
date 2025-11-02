import requests
import os

class NotificationService:
    """Telegram notification service"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    def send_message(self, text: str):
        """Send Telegram message"""
        
        if not self.bot_token or not self.chat_id:
            print(f"📱 Notification: {text}")
            return
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        try:
            requests.post(url, json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }, timeout=10)
        except:
            pass

import requests
from typing import List
from config import DISCORD_WEBHOOK
from model.post import Post


class DiscordNotifier:
    def __init__(self):
        pass

    def send_discord_message(self, post: List[Post]):
        """Gửi thông báo đến Discord với danh sách bài đăng mới"""
        
        for batch in self.chunk_list(post, 5):
            content = self.create_message(batch)
            data = {"content": content}
            response = requests.post(DISCORD_WEBHOOK, json=data)

            if response.status_code != 204:
                print(f"⚠ Lỗi gửi Discord: {response.status_code} - {response.text}")

    def create_message(self, batch: List[Post]) -> str:
        """Tạo nội dung tin nhắn Discord từ danh sách bài đăng"""
        
        message_lines = [f"📢 **{len(batch)} bài viết mới:**"]
        for post in batch:
            pd = post.posted_date.strftime("%H:%M %d-%m-%Y") if post.posted_date else ""
            message_lines.append(f"• [{pd}]\n[{post.title}]\n({post.url})")

        return "\n\n".join(message_lines)

    def chunk_list(self, lst, chunk_size):
        """Chia list thành các phần nhỏ"""
        
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

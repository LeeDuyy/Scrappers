import random
import time
from typing import List

from fetcher.chotot_scrapper import ChototScraper
from notifier.notify import DiscordNotifier
from storage.db_context import SessionLocal
from model.post import Post


class ChototProcessor:
    def __init__(self, url: str):
        self.scraper = ChototScraper(url)
        self.notifier = DiscordNotifier()

    def process_new_posts(self):
        """Xử lý bài đăng mới từ Chợ Tốt và gửi thông báo đến Discord."""
        
        # Lấy danh sách bài đăng mới
        posts = self.scraper.get_latest_posts()

        with SessionLocal() as session:
            existing_urls = set(row[0] for row in session.query(Post.url).all())
            new_posts: List[Post] = []

            for post in posts:
                if post.url in existing_urls:
                    continue

                new_posts.append(
                    Post(title=post.title, url=post.url, posted_date=post.posted_date)
                )

            if new_posts:
                # Lưu bài đăng mới vào cơ sở dữ liệu.
                session.add_all(new_posts)
                session.commit()
                session.close()

                # Gửi thông báo đến Discord.
                self.notifier.send_discord_message(new_posts)


if __name__ == "__main__":
    params = {
        "price": "0-3200000000",
        "size": "15-%2A",
        "price_million_per_m2": "100-%2A",
        "property_legal_document": "1",
        "house_type": "1%2C3%2C4"
    }
    
    URL = "https://www.nhatot.com/mua-ban-nha-dat-quan-binh-thanh-tp-ho-chi-minh"
    URL += "?" + "&".join(f"{key}={value}" for key, value in params.items())
    
    processor = ChototProcessor(URL)
    
    while True:
        try:
            print("\n🔍 Đang kiểm tra bài đăng mới...")
            processor.process_new_posts()

            # Tính toán thời gian chờ ngẫu nhiên từ 20 đến 40 phút
            delay = random.randint(20 * 60, 40 * 60)
            print(f"⏳ Lần quét tiếp theo sau {delay // 60} phút...\n")
            time.sleep(delay)
        
            processor.process_new_posts()
            
        except Exception as e:
            print(f"❗ Lỗi trong quá trình xử lý: {e}")
            time.sleep(60)
            
        finally:
            print("🔄 Đang chuẩn bị cho lần quét tiếp theo...")
            time.sleep(5)
            print("=========================================\n")

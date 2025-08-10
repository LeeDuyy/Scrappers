from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from typing import List, Dict
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

from config import NHATOT_DOMAIN
from model.post import Post


class ChototScraper:
    def __init__(self, search_url: str):
        """
        :param search_url: URL trang tìm kiếm trên Chợ Tốt theo tiêu chí đã lọc sẵn
        """
        self.search_url = search_url
        self.headers = {
            ":authority": "www.nhatot.com",
            ":method": "GET",
            ":path": "/mua-ban-nha-dat-tp-ho-chi-minh?price=0-3000000000",
            ":scheme": "https",
            "Referer": "https://www.nhatot.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-encoding": "gzip, deflate, br, zstd",
            "Accept-language": "en-US,en;q=0.9,vi;q=0.8",
            "Priority": "u=0, i",
            "sec-ch-ua": 'Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": 1,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Cookie": "_cfuvid=AXLGSJqduSkcAMA.riSPewtZwgyUBZTYEjNwpLj_ZoE-1754056953287-0.0.1.1-604800000; ct-slide_onboarding-cookie=true; location=tp-ho-chi-minh; regionParams={%22regionValue%22:13000%2C%22regionUrl%22:%22tp-ho-chi-minh%22%2C%22regionName%22:%22Tp%20H%E1%BB%93%20Ch%C3%AD%20Minh%22%2C%22subRegionValue%22:0%2C%22subRegionUrl%22:%22%22%2C%22subRegionName%22:%22T%E1%BA%A5t%20c%E1%BA%A3%22%2C%22empty_region%22:false}; loginRecommendation=false; cf_clearance=s5GnXtjs4CtZGzDVadGild1ueqf27LXSv_CxFd0yq1M-1754208682-1.2.1.1-4642KqPXOEK0a0AuBU6G2xm1h6MTS6VdSxOKRg6j77wpYR_3ZufX_b7OE30lbPPheRuC9dx5dBbH9iIbd1y4H0OrBGmMnS6A8DoWeU6ae.C7BqR5lmMp31ZqCBr5EvDMXYC4drQS8yxI60ZnAccV.0dO5AiheFTe1JWqeMoHh6Xt7CI93LeOvp9zkUGUGSPm3oVT2vbYcqZreCg04jRP6q6Qw5pdKIAIyb37SBpmXOs",
        }

    def fetch_html(self) -> str:
        """Lấy HTML từ trang tìm kiếm"""
        ua = UserAgent()
        random_ua = ua.random

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ],
            )

            context = browser.new_context(
                user_agent=random_ua,
                viewport={"width": 1280, "height": 800},
                locale="vi-VN",
            )

            page = context.new_page()
            page.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                """
            )
            page.goto(self.search_url)
            page.wait_for_load_state("networkidle")  # đợi trang ổn định

            self.scroll_to_bottom(page)

            html = page.content()

            # filename = f"chotot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            # with open(filename, "w", encoding="utf-8") as f:
            #     f.write(str(html))

            browser.close()

            return html

    def parse_posts(self, html: str) -> List[Post]:
        """
        Phân tích HTML để lấy thông tin bài đăng
        :return: Danh sách dict bài đăng [{id, title, price, link}, ...]
        """
        soup = BeautifulSoup(html, "lxml")
        posts: List[Post] = []
        list_ads = soup.find("div", class_="ListAds_ListAds__ANK2d")
        ul_tag = list_ads.find("ul")
        a_tags = ul_tag.find_all("a", class_="cqzlgv9")

        temps: List[str] = []

        for a_tag in a_tags:
            post_url = NHATOT_DOMAIN + a_tag.get("href")

            if post_url not in temps:
                name_div_tag = a_tag.find("div", class_="a1rmw1rw")

                if name_div_tag:
                    name_img_tag = name_div_tag.find("img")
                    post_title = name_img_tag.get("alt")

                    posted_date_span_tag = a_tag.find(
                        "span", class_=["1u6gyxh", "tx5yyjc"]
                    )
                    posted_date_string = posted_date_span_tag.text
                    posted_date = self.parse_relative_time(posted_date_string)

                    post = Post()
                    post.url = post_url
                    post.title = post_title
                    post.posted_date = posted_date

                    posts.append(post)
                    temps.append(post_url)

                    # print(post.title + " - " + post.posted_date)
                    # print(post_url)
                    # print("========================================\n")

            # break
            # filename = f"chotot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            # with open(filename, "w", encoding="utf-8") as f:
            #     f.write(str(a_tag))

        return posts

    def scroll_to_bottom(self, page, pause_time: float = 0.5, max_scrolls: int = 30):
        """Cuộn trang từ đầu đến cuối một cách từ từ và ổn định"""
        page.evaluate(
            f"""
            async () => {{
                let lastHeight = document.body.scrollHeight;
                let scrolls = 0;

                while (scrolls < {max_scrolls}) {{
                    window.scrollTo(0, document.body.scrollHeight);
                    await new Promise(resolve => setTimeout(resolve, {int(pause_time * 1000)}));
                    
                    const newHeight = document.body.scrollHeight;
                    if (newHeight === lastHeight) break;
                    lastHeight = newHeight;
                    scrolls++;
                }}
            }}
        """
        )

    def get_latest_posts(self) -> List[Dict]:
        """Lấy danh sách bài đăng mới"""
        html = self.fetch_html()
        posts = self.parse_posts(html)
        
        return posts

    def parse_relative_time(self, text: str) -> datetime:
        """Chuyển đổi chuỗi thời gian tương đối thành datetime"""
        
        now = datetime.now()
        parts = text.strip().split()

        if len(parts) < 2:
            raise ValueError(f"Chuỗi không hợp lệ: {text}")

        try:
            value = int(parts[0])
        except ValueError:
            pass  # nếu không thể chuyển đổi sang int, trả về thời gian hiện tại

        unit = parts[1].lower()

        if "giây" in unit:
            delta = timedelta(seconds=value)
        elif "phút" in unit:
            delta = timedelta(minutes=value)
        elif "giờ" in unit:
            delta = timedelta(hours=value)
        elif "ngày" in unit:
            delta = timedelta(days=value)
        elif "tuần" in unit:
            delta = timedelta(weeks=value)
        elif "tháng" in unit:
            delta = timedelta(days=30 * value)  # tạm tính 1 tháng = 30 ngày
        else:
            return now

        return now - delta

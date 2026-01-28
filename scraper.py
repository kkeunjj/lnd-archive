import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urljoin

class FinalLDScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.results = []
        self.limit_date = datetime.now() - timedelta(days=7) # 최근 7일 

    def parse_date(self, date_str):
        if not date_str: return None
        date_str = re.sub(r'(By\s.*?\s\|\s)', '', date_str, flags=re.I).strip()
        for fmt in ["%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"]:
            try: return datetime.strptime(date_str, fmt)
            except: continue
        return None

    def scrape_degreed(self, url, category):
        """Degreed 전용 정밀 수집기"""
        try:
            print(f"> Degreed ({category}) 정밀 수집 중...")
            res = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Degreed의 기사 카드는 보통 'post-card' 또는 'blog-post' 구조를 가집니다.
            # 진짜 제목은 <h3> 태그 내부에 위치합니다. 
            articles = soup.select('div.post-card, article.blog-post, div.blog-post')
            count = 0
            
            for art in articles:
                title_elem = art.select_one('h3 a, h2 a')
                if not title_elem: continue
                
                title = title_elem.get_text().strip()
                link = urljoin(url, title_elem['href'])
                
                # Degreed의 날짜는 주로 span.date 또는 time 태그에 있습니다. 
                date_elem = art.select_one('span.date, time, .post-date')
                date_text = date_elem.get_text() if date_elem else ""
                article_date = self.parse_date(date_text) or datetime.now()

                if self.limit_date <= article_date <= datetime.now():
                    self.results.append({
                        "date": article_date.strftime("%Y-%m-%d"),
                        "site": "Degreed",
                        "title": title,
                        "url": link,
                        "summary": category, # 카테고리 이름을 요약으로 사용
                        "category": category,
                        "tags": ["L&D", "Degreed"]
                    })
                    count += 1
            print(f"  - Degreed {count}개 완료")
        except Exception as e:
            print(f"  ! Degreed 오류: {e}")

    def scrape_general(self, name, url, category):
        """기타 6개 사이트 수집 (기존 로직 유지) """
        try:
            print(f"> {name} 수집 중...")
            res = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            count = 0
            for link in soup.find_all('a', href=True):
                title = link.get_text().strip()
                if len(title) > 35 and any(t in str(link.parent) for t in ['h2','h3','h4']):
                    self.results.append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "site": name, "title": title, "url": urljoin(url, link['href']),
                        "summary": title[:50], "category": category, "tags": [name]
                    })
                    count += 1
                    if count >= 3: break
            print(f"  - {name} {count}개 완료")
        except: pass

    def run(self):
        # 요청하신 Degreed 카테고리 5개 
        degreed_urls = [
            ("AI & 혁신", "https://degreed.com/experience/blog/category/ai-innovation-in-learning/"),
            ("기업 교육", "https://degreed.com/experience/blog/category/corporate-training/"),
            ("L&D 전략", "https://eu.degreed.com/experience/blog/category/learning-development-strategy/"),
            ("스킬 & 탤런트", "https://degreed.com/experience/blog/category/skills-talent-mobility/"),
            ("비즈니스 영향", "https://degreed.com/experience/blog/category/workforce-business-impact/")
        ]
        for cat, url in degreed_urls:
            self.scrape_degreed(url, cat)
            time.sleep(1)

        # 나머지 사이트들 
        others = [
            ("Josh Bersin", "https://joshbersin.com/", "TD"),
            ("SHRM", "https://www.shrm.org/topics-tools/news", "기타"),
            ("Unleash", "https://www.unleash.ai/learning-and-development/", "L&D 전략 및 LX"),
            ("DDI", "https://www.ddi.com/blogs", "리더십"),
            ("Wharton", "https://knowledge.wharton.upenn.edu/category/leadership/", "OD"),
            ("Korn Ferry", "https://www.kornferry.com/insights", "TD")
        ]
        for name, url, cat in others:
            self.scrape_general(name, url, cat)
            time.sleep(1)

        with open('articles.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scraper = FinalLDScraper()
    scraper.run()
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urljoin, urlparse

class MonthlyLDScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.results = []
        self.today = datetime.now()
        self.limit_date = self.today - timedelta(days=30)

    def classify_by_content(self, title):
        """제목 기반 자동 카테고리 분류"""
        t = title.lower()
        if any(k in t for k in ['ai', 'digital', 'tech', 'data', 'intelligence']): return "Tech"
        if any(k in t for k in ['leader', 'coach', 'culture', 'manager', 'lead']): return "리더십"
        if any(k in t for k in ['skill', 'talent', 'career', 'upskill', 'reskill']): return "TD"
        if any(k in t for k in ['change', 'org', 'transformation', 'od']): return "OD"
        if any(k in t for k in ['strategy', 'lxp', 'experience', 'learning']): return "L&D 전략 및 LX"
        return "기타"

    def parse_date(self, date_str):
        if not date_str: return None
        date_str = re.sub(r'(By\s.*?\s\|\s)', '', date_str, flags=re.I).strip()
        formats = ["%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d %Y"]
        for fmt in formats:
            try: return datetime.strptime(date_str, fmt)
            except: continue
        return None

    def scrape_site(self, name, url):
        try:
            print(f"> {name} 수집 중...")
            res = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 수집 대상 사이트의 기본 도메인 추출 (예: joshbersin.com)
            base_domain = urlparse(url).netloc
            
            count = 0
            existing_urls = {r['url'] for r in self.results}
            
            for link in soup.find_all('a', href=True):
                title = link.get_text().strip()
                href = urljoin(url, link['href'])
                
                # [핵심 추가] 외부 사이트 링크 필터링
                # 1. 링크에 기본 도메인이 포함되어 있는지 확인
                # 2. 혹은 상대 경로(/blog/...)로 시작하는지 확인
                if base_domain not in urlparse(href).netloc:
                    continue
                
                # 제목 길이 및 중복/노이즈 필터링
                if len(title) < 25 or href in existing_urls:
                    continue
                if any(x in href.lower() for x in ['/tag/', '/category/', '/author/', '/login', '/search']):
                    continue

                parent = link.find_parent(['article', 'div', 'li', 'section'])
                if not parent: continue
                
                # 날짜 탐색 및 검증
                date_text = ""
                time_tag = parent.find('time')
                if time_tag:
                    date_text = time_tag.get('datetime') or time_tag.text
                else:
                    date_match = re.search(r'([A-Z][a-z]{2,8}\s\d{1,2},\s\d{4})', parent.get_text())
                    if date_match: date_text = date_match.group()

                article_date = self.parse_date(date_text)
                final_date_obj = article_date if article_date else self.today
                
                if self.limit_date <= final_date_obj <= self.today:
                    category = self.classify_by_content(title)
                    self.results.append({
                        "date": final_date_obj.strftime("%Y-%m-%d"),
                        "site": name,
                        "title": title,
                        "url": href,
                        "summary": title,
                        "category": category,
                        "tags": ["L&D", name, category]
                    })
                    existing_urls.add(href)
                    count += 1
                    if count >= 8: break
            
            print(f"  - {count}개 수집 완료")
        except Exception as e:
            print(f"  ! {name} 오류: {e}")

    def run(self):
        targets = [
            ("Josh Bersin", "https://joshbersin.com/"),
            ("SHRM", "https://www.shrm.org/topics-tools/news"),
            ("Unleash", "https://www.unleash.ai/learning-and-development/"),
            ("DDI", "https://www.ddiworld.com/blog"),
            ("Wharton Knowledge", "https://knowledge.wharton.upenn.edu/category/leadership/"),
            ("Korn Ferry", "https://www.kornferry.com/insights")
        ]
        
        for name, url in targets:
            self.scrape_site(name, url)
            time.sleep(2)

        self.results.sort(key=lambda x: x['date'], reverse=True)
        with open('articles.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scraper = MonthlyLDScraper()
    scraper.run()
    print(f"\n✨ 완료! 지정된 도메인 내에서만 수집되었습니다.")
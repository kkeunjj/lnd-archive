import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urljoin

class WeeklyLDScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.results = []
        self.today = datetime.now()
        self.limit_date = self.today - timedelta(days=7) # 최근 7일 설정

    def parse_date(self, date_str):
        """다양한 날짜 형식을 시도하여 datetime 객체로 변환합니다."""
        if not date_str: return None
        date_str = re.sub(r'(By\s.*?\s\|\s)', '', date_str, flags=re.I).strip()
        
        formats = [
            "%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%Y-%m-%d", 
            "%m/%d/%Y", "%d/%m/%Y", "%b %d %Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # 숫자 패턴(2026-01-28 등) 추출
        match = re.search(r'(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{4})', date_str)
        if match:
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                try: return datetime.strptime(match.group(), fmt)
                except: pass
        return None

    def scrape_site(self, name, url, category):
        try:
            print(f"> {name} ({category}) 수집 중...")
            res = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            count = 0
            # 기사 링크 후보군 탐색
            for link in soup.find_all('a', href=True):
                title = link.get_text().strip()
                if len(title) < 30: continue 
                
                parent = link.find_parent(['article', 'div', 'li', 'section'])
                if not parent: continue
                
                # 날짜 찾기
                time_tag = parent.find('time')
                date_text = ""
                if time_tag:
                    date_text = time_tag.get('datetime') or time_tag.text
                else:
                    date_match = re.search(r'([A-Z][a-z]{2,8}\s\d{1,2},\s\d{4})', parent.get_text())
                    if date_match: date_text = date_match.group()

                article_date = self.parse_date(date_text)
                
                # 날짜가 없으면 일단 '오늘'로 간주하여 일주일 내에 포함시킴 (데이터 누락 방지)
                final_date_obj = article_date if article_date else self.today
                
                if self.limit_date <= final_date_obj <= self.today:
                    self.results.append({
                        "date": final_date_obj.strftime("%Y-%m-%d"),
                        "site": name,
                        "title": title,
                        "url": urljoin(url, link['href']),
                        "summary": title[:100] + "...",
                        "category": category,
                        "tags": ["L&D", name]
                    })
                    count += 1
                    if count >= 3: break # URL이 많아졌으므로 사이트/카테고리당 3개로 조정
            
            print(f"  - {count}개 성공")
        except Exception as e:
            print(f"  ! {name} 오류: {e}")

    def run(self):
        # 교체된 Degreed URL 5개 + 기존 6개 사이트
        targets = [
            ("Degreed", "https://degreed.com/experience/blog/category/ai-innovation-in-learning/", "AI & 혁신"),
            ("Degreed", "https://degreed.com/experience/blog/category/corporate-training/", "기업 교육"),
            ("Degreed", "https://eu.degreed.com/experience/blog/category/learning-development-strategy/", "L&D 전략"),
            ("Degreed", "https://degreed.com/experience/blog/category/skills-talent-mobility/", "스킬 & 탤런트"),
            ("Degreed", "https://degreed.com/experience/blog/category/workforce-business-impact/", "비즈니스 영향"),
            ("Josh Bersin", "https://joshbersin.com/", "TD"),
            ("SHRM", "https://www.shrm.org/topics-tools/news", "기타"),
            ("Unleash", "https://www.unleash.ai/learning-and-development/", "L&D 전략 및 LX"),
            ("DDI", "https://www.ddi.com/blogs", "리더십"),
            ("Wharton Knowledge", "https://knowledge.wharton.upenn.edu/category/leadership/", "OD"),
            ("Korn Ferry", "https://www.kornferry.com/insights", "TD")
        ]
        
        for name, url, cat in targets:
            self.scrape_site(name, url, cat)
            time.sleep(1)

        with open('articles.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scraper = WeeklyLDScraper()
    scraper.run()
    print("\n[완료] 최근 7일간의 아티클 수집을 완료했습니다.")
    time.sleep(2)
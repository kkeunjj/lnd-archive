import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urljoin

class MonthlyLDScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.results = []
        self.today = datetime.now()
        self.limit_date = self.today - timedelta(days=30) # 최근 30일로 변경

    def parse_date(self, date_str):
        """다양한 날짜 형식을 시도하여 datetime 객체로 변환합니다."""
        if not date_str: return None
        # 불필요한 공백 및 'By ...' 등의 텍스트 제거
        date_str = re.sub(r'(By\s.*?\s\|\s)', '', date_str, flags=re.I).strip()
        
        # 시도해볼 날짜 형식들
        formats = [
            "%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%Y-%m-%d", 
            "%m/%d/%Y", "%d/%m/%Y", "%b %d %Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # 숫자 패턴(2026-01-28 등) 직접 추출 시도
        match = re.search(r'(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{4})', date_str)
        if match:
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                try: return datetime.strptime(match.group(), fmt)
                except: pass
            
        return None

    def scrape_site(self, name, url, category):
        try:
            print(f"> {name} 수집 중 (최근 30일 타겟)...")
            res = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            count = 0
            # 1. 모든 링크를 돌며 제목이 긴 것들을 기사 후보로 선정
            for link in soup.find_all('a', href=True):
                title = link.get_text().strip()
                if len(title) < 30: continue 
                
                # 2. 링크 주변(부모 요소)에서 날짜 정보를 탐색
                parent = link.find_parent(['article', 'div', 'li', 'section'])
                if not parent: continue
                
                date_text = ""
                # time 태그 우선 확인
                time_tag = parent.find('time')
                if time_tag:
                    date_text = time_tag.get('datetime') or time_tag.text
                else:
                    # 텍스트 내에서 날짜 패턴(Jan 20, 2026 등) 검색
                    date_match = re.search(r'([A-Z][a-z]{2,8}\s\d{1,2},\s\d{4})', parent.get_text())
                    if date_match: date_text = date_match.group()

                article_date = self.parse_date(date_text)
                
                # 3. 30일 이내인 경우만 저장 (날짜를 아예 못 찾으면 안전하게 오늘 날짜로 일단 수집)
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
                    if count >= 5: break # 사이트당 최대 5개
            
            print(f"  - {count}개 수집 성공")
        except Exception as e:
            print(f"  ! {name} 오류 발생: {e}")

    def run(self):
        targets = [
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
    scraper = MonthlyLDScraper()
    scraper.run()
    print("\n[성공] 최근 한 달치 아티클 수집을 완료했습니다.")
    time.sleep(2)
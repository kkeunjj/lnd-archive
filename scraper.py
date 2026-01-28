import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from urllib.parse import urljoin

class LDScraper:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        self.results = []
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 지정하신 7개 타겟 사이트 설정
        self.targets = [
            {"name": "Degreed", "url": "https://degreed.com/experience/blog/", "selector": "h3 a, h2 a", "cat": "L&D 전략 및 LX"},
            {"name": "Josh Bersin", "url": "https://joshbersin.com/", "selector": ".post-title a, h3 a", "cat": "TD"},
            {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news", "selector": "h3 a", "cat": "기타"},
            {"name": "Unleash", "url": "https://www.unleash.ai/learning-and-development/", "selector": "h3 a", "cat": "L&D 전략 및 LX"},
            {"name": "DDI", "url": "https://www.ddi.com/blogs", "selector": "h4 a", "cat": "리더십"},
            {"name": "Wharton Knowledge", "url": "https://knowledge.wharton.upenn.edu/category/leadership/", "selector": ".article-title a, h2 a", "cat": "OD"},
            {"name": "Korn Ferry", "url": "https://www.kornferry.com/insights", "selector": "h3 a", "cat": "TD"}
        ]

    def run(self):
        print(f"[{self.today}] 7개 사이트 수집을 시작합니다.\n")
        
        for t in self.targets:
            try:
                print(f"> {t['name']} 접속 중...")
                res = requests.get(t['url'], headers=self.headers, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                items = soup.select(t['selector'])
                count = 0
                for item in items:
                    title = item.get_text().strip()
                    link = urljoin(res.url, item.get('href', ''))
                    
                    # 제목이 너무 짧거나 메뉴 항목인 경우 제외 (광고/메뉴 필터링)
                    if len(title) > 30 and count < 5:
                        self.results.append({
                            "date": self.today,
                            "site": t['name'],
                            "title": title,
                            "url": link,
                            "summary": title[:100] + "...",
                            "category": t['cat'],
                            "tags": ["L&D", t['name']]
                        })
                        count += 1
                print(f"  - {count}개 수집 완료")
                time.sleep(1) # 사이트 차단 방지용
            except Exception as e:
                print(f"  ! {t['name']} 오류: {e}")

        # 파일 저장
        with open('articles.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        
        print(f"\n[최종 성공] 총 {len(self.results)}개의 아티클이 articles.json에 저장되었습니다.")
        print("이제 이 파일을 GitHub에 올리거나 Netlify에서 확인하세요.")
        time.sleep(2)

if __name__ == "__main__":
    scraper = LDScraper()
    scraper.run()
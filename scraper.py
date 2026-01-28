import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time
from urllib.parse import urljoin
import urllib3

# SSL 경고 메시지 무시 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SimpleAccumulativeScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        }
        self.file_path = 'articles.json'
        self.existing_articles = self.load_existing_data()
        self.new_results = []

    def load_existing_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return []
        return []

    def classify_category(self, title):
        t = title.lower()
        if any(k in t for k in ['ai', 'digital', 'tech', 'data']): return "Tech"
        if any(k in t for k in ['leader', 'coach', 'culture', 'manager']): return "리더십"
        if any(k in t for k in ['skill', 'talent', 'career', 'upskill']): return "TD"
        if any(k in t for k in ['strategy', 'lxp', 'experience']): return "L&D 전략 및 LX"
        if any(k in t for k in ['change', 'org', 'transformation', 'od']): return "OD"
        return "기타"

    def scrape_site(self, name, url, default_cat):
        try:
            print(f"> {name} 수집 시도 중... (URL: {url})")
            # verify=False와 timeout 설정을 통해 접속 안정성 확보
            res = requests.get(url, headers=self.headers, timeout=30, verify=False)
            
            if res.status_code != 200:
                print(f"  ! {name} 접속 실패 (상태 코드: {res.status_code})")
                return

            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            count = 0
            existing_urls = {a['url'] for a in self.existing_articles}

            for link in links:
                title = link.get_text().strip()
                href = urljoin(url, link['href'])

                # 제목 길이 필터링 (너무 짧으면 무시) 및 중복 체크
                if len(title) < 20 or href in existing_urls or any(n['url'] == href for n in self.new_results):
                    continue
                
                # 광고 및 SNS 링크 제외
                if any(x in href for x in ['facebook', 'twitter', 'linkedin', 'instagram', 'wp-content']):
                    continue

                self.new_results.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "site": name,
                    "title": title,
                    "url": href,
                    "summary": title, # 제목을 요약으로 사용 (문제 3 해결)
                    "category": self.classify_category(title) if self.classify_category(title) != "기타" else default_cat,
                    "tags": [name]
                })
                count += 1
                if count >= 10: break

            print(f"  - {name} {count}개 완료")
        except Exception as e:
            print(f"  ! {name} 오류: {e}")

    def run(self):
        # 404가 발생하지 않도록 주소를 메인 페이지 위주로 재설정
        sites = [
            ("Degreed", "https://degreed.com/experience/blog/", "L&D 전략 및 LX"),
            ("Josh Bersin", "https://joshbersin.com/", "TD"),
            ("SHRM", "https://www.shrm.org/topics-tools/news", "기타"),
            ("Unleash", "https://www.unleash.ai/learning-and-development/", "L&D 전략 및 LX"),
            ("DDI", "https://www.ddi.com/blog/", "리더십"),
            ("Wharton", "https://knowledge.wharton.upenn.edu/category/leadership/", "OD"),
            ("Korn Ferry", "https://www.kornferry.com/insights", "TD")
        ]
        
        for name, url, cat in sites:
            self.scrape_site(name, url, cat)
            time.sleep(2)

        # 기존 데이터와 새 데이터 통합
        final_articles = self.new_results + self.existing_articles
        # URL 기준 중복 제거 및 날짜순 정렬
        unique_data = {v['url']: v for v in final_articles}.values()
        sorted_data = sorted(unique_data, key=lambda x: x['date'], reverse=True)

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(list(sorted_data)[:500], f, ensure_ascii=False, indent=4)
        print(f"\n✨ 업데이트 완료! 총 {len(sorted_data)}개 저장됨.")

if __name__ == "__main__":
    scraper = SimpleAccumulativeScraper()
    scraper.run()
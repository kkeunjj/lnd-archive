import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time
from urllib.parse import urljoin
import urllib3

# SSL 인증서 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LndArticleScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
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

    def classify_by_content(self, title):
        """
        [문제 4 해결] 사이트가 아닌 아티클 제목의 성격에 따라 카테고리 분류
        """
        t = title.lower()
        # 1. Tech (AI, 데이터, 기술)
        if any(k in t for k in ['ai', 'digital', 'tech', 'data', 'automation', 'intelligence', 'generative']):
            return "Tech"
        # 2. 리더십 (코칭, 문화, 관리자)
        if any(k in t for k in ['leader', 'coach', 'culture', 'manager', 'lead', 'executive', 'soft skill']):
            return "리더십"
        # 3. TD (인재 개발, 스킬, 커리어, 채용)
        if any(k in t for k in ['skill', 'talent', 'career', 'hiring', 'upskill', 'reskill', 'mobility']):
            return "TD"
        # 4. OD (조직 개발, 변화 관리, 트랜스포메이션)
        if any(k in t for k in ['change', 'org', 'transformation', 'od', 'design', 'structure']):
            return "OD"
        # 5. L&D 전략 및 LX (학습 전략, 경험 디자인)
        if any(k in t for k in ['strategy', 'lxp', 'experience', 'learning', 'curriculum', 'education']):
            return "L&D 전략 및 LX"
        
        return "기타"

    def scrape_site(self, name, url):
        try:
            print(f"> {name} 수집 시작...")
            res = requests.get(url, headers=self.headers, timeout=30, verify=False)
            
            if res.status_code != 200:
                print(f"  ! {name} 접속 실패 (코드: {res.status_code})")
                return

            soup = BeautifulSoup(res.text, 'html.parser')
            # <a> 태그를 모두 찾아 기사 후보 추출
            links = soup.find_all('a', href=True)
            
            count = 0
            existing_urls = {a['url'] for a in self.existing_articles}

            for link in links:
                title = link.get_text().strip()
                href = urljoin(url, link['href'])

                # 필터링: 제목이 너무 짧거나, 중복이거나, 특정 사이트 제외
                if len(title) < 25 or href in existing_urls or any(n['url'] == href for n in self.new_results):
                    continue
                if any(x in href for x in ['facebook', 'twitter', 'linkedin', 'instagram', 'wp-content', 'login']):
                    continue

                # 아티클 성격에 따른 카테고리 분류 (문제 4 핵심 해결)
                category = self.classify_by_content(title)

                self.new_results.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "site": name,
                    "title": title,
                    "url": href,
                    "summary": title, # 제목만 가져와서 깔끔하게 유지 (문제 3 해결)
                    "category": category,
                    "tags": [name, category]
                })
                count += 1
                if count >= 10: break # 한 사이트당 10개 신규 수집

            print(f"  - {name} {count}개 완료")
        except Exception as e:
            print(f"  ! {name} 에러: {e}")

    def run(self):
        # Degreed 제외, 나머지 사이트 목록
        sites = [
            ("Josh Bersin", "https://joshbersin.com/"),
            ("SHRM", "https://www.shrm.org/topics-tools/news"),
            ("Unleash", "https://www.unleash.ai/learning-and-development/"),
            ("DDI", "https://www.ddi.com/blog/"),
            ("Wharton", "https://knowledge.wharton.upenn.edu/category/leadership/"),
            ("Korn Ferry", "https://www.kornferry.com/insights")
        ]
        
        for name, url in sites:
            self.scrape_site(name, url)
            time.sleep(2)

        # 데이터 통합 (새로 찾은 것 + 기존 것)
        all_data = self.new_results + self.existing_articles
        
        # URL 기준 중복 제거 및 날짜순 정렬
        unique_data = {v['url']: v for v in all_data}.values()
        sorted_data = sorted(unique_data, key=lambda x: x['date'], reverse=True)

        # 최대 500개 유지
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(list(sorted_data)[:500], f, ensure_ascii=False, indent=4)
        
        print(f"\n✨ 완료! 총 {len(sorted_data)}개의 아티클이 저장되어 있습니다.")

if __name__ == "__main__":
    scraper = LndArticleScraper()
    scraper.run()
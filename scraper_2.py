import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

# 수집할 사이트 목록
targets = [
    {"name": "Degreed", "url": "https://degreed.com/experience/blog/", "category": "L&D 전략 및 LX"},
    {"name": "Josh Bersin", "url": "https://joshbersin.com/", "category": "TD"},
    {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news", "category": "기타"},
    {"name": "Unleash", "url": "https://www.unleash.ai/learning-and-development/", "category": "L&D 전략 및 LX"},
    {"name": "DDI", "url": "https://www.ddi.com/blogs", "category": "리더십"},
    {"name": "Wharton Knowledge", "url": "https://knowledge.wharton.upenn.edu/category/leadership/", "category": "OD"},
    {"name": "Korn Ferry", "url": "https://www.kornferry.com/insights", "category": "TD"}
]

def run_scraper():
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    today = datetime.now().strftime("%Y-%m-%d")
    
    for target in targets:
        try:
            print(f"> {target['name']} 수집 중...")
            res = requests.get(target['url'], headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            links = soup.select('a')
            count = 0
            for l in links:
                title = l.get_text().strip()
                url = l.get('href', '')
                
                # 진짜 기사 제목 같은 것만 골라내기
                if len(title) > 25 and url.startswith('http') and count < 5:
                    results.append({
                        "date": today,
                        "site": target['name'],
                        "title": title,
                        "url": url,
                        "summary": title[:100] + "...",
                        "category": target['category'],
                        "tags": ["L&D", target['name']]
                    })
                    count += 1
        except Exception as e:
            print(f"오류 발생 ({target['name']}): {e}")

    with open('articles.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"\n[성공] 총 {len(results)}개의 데이터를 articles.json에 저장했습니다.")

if __name__ == "__main__":
    run_scraper()
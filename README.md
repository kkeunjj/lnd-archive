# 📚 L&D 아티클 아카이브

L&D, HR, Leadership 관련 웹사이트에서 최신 아티클을 자동으로 수집하고 아카이빙하는 시스템입니다.

## 🌟 주요 기능

- ✅ **자동 스크래핑**: GitHub Actions로 매일 오전 9시 자동 실행
- ✅ **7개 사이트 모니터링**: Degreed, Josh Bersin, SHRM, Unleash, DDI, Wharton, Korn Ferry
- ✅ **실시간 필터링**: 사이트별, 카테고리별, 날짜별 필터
- ✅ **검색 기능**: 제목, 요약, 태그 검색
- ✅ **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원

## 📁 프로젝트 구조

```
ld-article-archive/
├── .github/
│   └── workflows/
│       └── scrape.yml          # GitHub Actions 자동화 설정
├── index.html                  # 메인 웹페이지
├── scraper.py                  # 아티클 수집 스크립트
├── articles.json               # 수집된 아티클 데이터
├── requirements.txt            # Python 패키지 목록
└── README.md                   # 프로젝트 설명서
```

## 🚀 시작하기

### 1. 로컬에서 실행

```bash
# 저장소 클론
git clone https://github.com/yourusername/ld-article-archive.git
cd ld-article-archive

# Python 패키지 설치
pip install -r requirements.txt

# 스크래퍼 실행
python scraper.py

# 로컬 서버 실행
python -m http.server 8000

# 브라우저에서 열기
# http://localhost:8000
```

### 2. GitHub Pages로 배포

1. GitHub에 저장소 업로드
2. Settings > Pages로 이동
3. Source: Deploy from a branch
4. Branch: main, Folder: / (root)
5. Save 클릭

배포 후 접속: `https://yourusername.github.io/ld-article-archive/`

### 3. Netlify로 배포

1. [Netlify](https://www.netlify.com/)에 로그인
2. "New site from Git" 클릭
3. GitHub 저장소 연결
4. Build settings:
   - Build command: (비워두기)
   - Publish directory: `/`
5. Deploy 클릭

## ⚙️ GitHub Actions 자동화

### 설정 방법

이미 `.github/workflows/scrape.yml` 파일이 포함되어 있어 자동으로 작동합니다.

**자동 실행 시간**: 매일 오전 9시 (한국 시간, UTC 0시)

### 수동 실행

1. GitHub 저장소 페이지 이동
2. "Actions" 탭 클릭
3. "Daily Article Scraper" 워크플로우 선택
4. "Run workflow" 버튼 클릭

### 작동 방식

1. **매일 오전 9시**: GitHub Actions가 자동으로 실행
2. **스크래퍼 실행**: `scraper.py`가 최신 아티클 수집
3. **변경사항 확인**: `articles.json` 파일이 업데이트되었는지 확인
4. **자동 커밋**: 변경사항이 있으면 자동으로 커밋 & 푸시
5. **웹사이트 업데이트**: GitHub Pages/Netlify가 자동으로 재배포

## 📊 모니터링 대상 사이트

| 사이트 | URL | 카테고리 |
|--------|-----|----------|
| Degreed | https://degreed.com/experience/blog/ | L&D 전략 및 LX |
| Josh Bersin | https://joshbersin.com/ | TD |
| SHRM | https://www.shrm.org/topics-tools/news | 기타 |
| Unleash | https://www.unleash.ai/learning-and-development/ | L&D 전략 및 LX |
| DDI | https://www.ddi.com/blogs | 리더십 |
| Wharton Knowledge | https://knowledge.wharton.upenn.edu/category/leadership/ | OD |
| Korn Ferry | https://www.kornferry.com/insights | TD |

## 🎨 카테고리

- **L&D 전략 및 LX**: 학습 전략, 학습 경험 디자인
- **OD**: 조직 개발, 변화 관리
- **TD**: 인재 개발, 스킬 기반 접근
- **리더십**: 리더십 개발, 코칭
- **Tech**: LXP, AI, 학습 분석
- **기타**: 기타 HR 관련 콘텐츠

## 🛠️ 커스터마이징

### 새로운 사이트 추가

`scraper.py` 파일을 수정하여 새로운 사이트를 추가할 수 있습니다:

```python
def scrape_new_site(self):
    """Scrape New Site"""
    try:
        url = "https://newsite.com/articles"
        response = requests.get(url, headers=self.headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 아티클 요소 찾기
        articles = soup.find_all('article', limit=10)
        
        for article in articles:
            # 제목, 링크, 날짜, 요약 추출
            # ...
            
            self.articles.append({
                'date': date,
                'site': 'New Site',
                'title': title,
                'url': link,
                'summary': summary,
                'category': 'Your Category',
                'tags': ['tag1', 'tag2']
            })
    except Exception as e:
        print(f"Error scraping New Site: {e}")
```

### 스크래핑 시간 변경

`.github/workflows/scrape.yml` 파일에서 cron 표현식 수정:

```yaml
schedule:
  # 매일 오후 2시 (UTC 5시)
  - cron: '0 5 * * *'
```

[Cron 표현식 생성기](https://crontab.guru/)

## 🔧 문제 해결

### 스크래핑이 실패하는 경우

1. **네트워크 문제**: GitHub Actions 로그 확인
2. **HTML 구조 변경**: 웹사이트의 HTML 선택자 업데이트 필요
3. **접근 차단**: User-Agent 변경 또는 요청 간격 조정

### GitHub Actions가 작동하지 않는 경우

1. **권한 확인**: Settings > Actions > General
   - "Read and write permissions" 선택
   - "Allow GitHub Actions to create and approve pull requests" 체크
2. **워크플로우 활성화**: Actions 탭에서 워크플로우 Enable 확인

### 로컬에서 CORS 에러가 발생하는 경우

파일을 직접 열지 말고 로컬 서버를 실행하세요:

```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js (npx 사용)
npx http-server
```

## 📄 라이선스

이 프로젝트는 개인 및 상업적 용도로 자유롭게 사용 가능합니다.

## 🤝 기여

개선 사항이나 버그 리포트는 언제든 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 Issue를 생성해주세요.

---

Made with ❤️ for L&D Professionals

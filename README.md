# 오토그리드 (AutoGrid) — 자동차 뉴스 큐레이션 사이트

국내외 자동차 뉴스와 BYD·전기차 이슈를 RSS로 모아 보여주는 정적 웹사이트입니다.
제목 + 짧은 요약 + 원문 링크만 게재하므로 저작권 문제 없이 운영할 수 있습니다.

## 구성

```
index.html            메인 페이지 (탭: 전체/국내/해외/공식·안전정보/BYD·전기차)
about.html             사이트 소개 (E-E-A-T 신뢰 신호)
sources.html           정보 출처 (참고하는 정책/통계/안전기관/제조사 뉴스룸 목록)
privacy.html           개인정보처리방침
contact.html           문의 페이지
data/news.json          뉴스 데이터 (자동 생성/갱신됨)
scripts/fetch_news.py   RSS 수집 스크립트
.github/workflows/update-news.yml   3시간마다 자동 수집 + GitHub Pages 배포
robots.txt / sitemap.xml
```

## 1) GitHub에 올리기

1. GitHub에서 새 저장소 생성 (예: `auto-news-hub`), Public으로 설정
2. 이 폴더의 파일을 그대로 저장소에 push
   ```bash
   cd auto-news-hub
   git init
   git add .
   git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/내계정/auto-news-hub.git
   git push -u origin main
   ```

## 2) GitHub Pages 켜기

1. 저장소 → Settings → Pages
2. Build and deployment → Source: **GitHub Actions** 선택
   (이미 포함된 `update-news.yml` 워크플로우가 자동으로 배포까지 처리합니다)
3. Actions 탭에서 `Update news feed` 워크플로우를 한 번 수동 실행 (workflow_dispatch)
   → 처음 몇 분 안에 `https://내계정.github.io/auto-news-hub/` 로 접속 가능

## 3) 새 도메인 연결 (무료 호스팅 + 커스텀 도메인)

1. 도메인을 구매합니다 (가비아, 후이즈, Namecheap 등)
2. 저장소 루트에 `CNAME` 파일을 만들고 도메인 한 줄만 입력 (예: `autogrid.kr`)
3. 도메인 등록업체 DNS 설정에서 아래 중 하나를 추가
   - A 레코드 4개를 GitHub Pages IP로 지정 (185.199.108.153 등, GitHub Pages 공식 문서 참고)
   - 또는 서브도메인이라면 CNAME 레코드로 `내계정.github.io` 지정
4. 저장소 Settings → Pages에서 Custom domain에 도메인 입력 후 저장, HTTPS 강제 옵션 체크
5. `robots.txt`와 `sitemap.xml`의 `YOUR-DOMAIN`을 실제 도메인으로 교체

## 4) 뉴스 소스 커스터마이징

`scripts/fetch_news.py` 상단 `FEEDS` 리스트에서 RSS 주소를 추가/삭제할 수 있습니다.
- 국내: 구글 뉴스 검색 RSS(`news.google.com/rss/search?q=검색어&hl=ko&gl=KR&ceid=KR:ko`)를 사용 중이며,
  검색어만 바꾸면 원하는 국내 매체 취합 범위를 조정할 수 있습니다.
- 해외: Electrek, InsideEVs, CnEVPost(BYD 전용 피드 포함), Motor1, Car and Driver, Teslarati 등
  이미 검증된 RSS를 기본 포함했습니다.
- 공식·안전정보(`category: "official"`): 국토교통부/리콜/판매량 통계는 구글 뉴스 검색 RSS로,
  NHTSA·IIHS·Euro NCAP은 영문 구글 뉴스 검색 RSS(`hl=en-US&gl=US&ceid=US:en`)로 취합합니다.
  KAMA, KAIDA, 자동차리콜센터, 각 제조사 뉴스룸, AAA, Consumer Reports, 중고차 플랫폼, MarkLines 등은
  공개 RSS를 제공하지 않아 자동 수집 대상이 아니며, `sources.html`에 참고 링크로만 안내합니다.
- 특정 언론사가 자체 RSS를 제공한다면(`사이트주소/feed` 또는 `/rss.xml`) FEEDS에 바로 추가 가능합니다.

BYD·전기차 자동 태깅은 `BYD_EV_KEYWORDS` 리스트로 판단합니다. 필요한 키워드를 추가하세요.

## 5) 광고(수익화) 켜기

1. Google AdSense에 사이트 등록 후 심사 신청
2. **심사가 끝나기 전에는 광고를 켜지 마세요.** `index.html` 상단의
   `window.ADSENSE_CLIENT = "";` 값이 비어 있으면 광고 스크립트가 로드되지 않고
   광고 자리도 자동으로 숨겨집니다 (이전 vorainfo.com 저품질 반려 경험 참고).
3. 승인 후 `ca-pub-XXXXXXXXXXXXXXXX` 형태의 값을 채워 넣으면 자동으로 광고가 노출됩니다.
4. 저장소 루트에 `ads.txt` 파일을 추가하고 AdSense가 안내하는 한 줄
   (`google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0`)을 넣어주세요.

### 승인 확률을 높이려면 (vorainfo.com 반려 경험 반영)
- `about.html`, `privacy.html`, `contact.html`을 실제 정보로 채워 신뢰 신호를 갖추세요.
- Search Console에 사이트를 등록하고 `sitemap.xml`을 제출해 색인이 되도록 하세요.
- 큐레이션 사이트 특성상 "제목+요약+링크"만 있으면 오리지널리티가 낮게 평가될 수 있으니,
  홈페이지 상단에 "이번 주 BYD·전기차 이슈 요약" 같은 직접 작성 코너를 주기적으로 추가하는 것을 권장합니다.

## 6) 로컬에서 데이터 미리 생성해보기

```bash
pip install -r scripts/requirements.txt
python scripts/fetch_news.py
```
`data/news.json`이 갱신됩니다. (참고: 이 작업 환경의 샌드박스는 외부 네트워크가 제한되어
있어 이 자리에서는 실제 수집 테스트를 하지 못했습니다. GitHub Actions에서는 정상적으로
외부 인터넷에 접속하므로 첫 워크플로우 실행 시 실제 뉴스로 채워집니다.)

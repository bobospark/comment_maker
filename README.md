# 🤖 Naver Blog Comment Agent (Gemini AI)

> **네이버 블로그 포스팅을 분석하여 진정성 있는 '서로이웃 신청' 댓글을 생성해주는 AI 에이전트입니다.**

이 프로젝트는 **Google Gemini API**를 활용하여 블로그 본문의 맥락을 이해하고, 정중한 공감과 함께 서로이웃 요청 멘트를 자동으로 구성해줍니다.

---

## ✨ 주요 기능 (Key Features)

* **🔍 스마트 본문 크롤링**: 네이버 블로그 특유의 `iframe` 구조를 분석하여 실제 본문 텍스트만 정확하게 추출합니다.
* **🧠 AI 문맥 분석**: Gemini Flash 모델이 포스팅의 핵심 주제를 2문장으로 요약하고 관련 댓글을 생성합니다.
* **📝 맞춤형 페르소나**: 사용자가 입력한 추가 문구(예: 직업, 관심사)를 댓글 문맥에 자연스럽게 녹여냅니다.
* **📜 히스토리 관리**: 최신 결과물은 강조해서 보여주고, 이전 작업들은 우측 히스토리에 차곡차곡 쌓여 언제든 다시 볼 수 있습니다.
* **📋 자동 줄바꿈 뷰어**: 긴 댓글도 가로 스크롤 없이 한눈에 읽을 수 있도록 최적화된 UI를 제공합니다.
* **🪵 상세 로깅 시스템**: 크롤링된 본문과 AI 응답 과정을 `blog_agent_log.txt`에 실시간으로 기록하여 검증이 가능합니다.

---

## 🛠️ 기술 스택 (Tech Stack)

* **Framework**: [Streamlit](https://streamlit.io/)
* **Language**: Python 3.9+
* **AI SDK**: `google-genai` (Google Gemini)
* **Scraping**: `BeautifulSoup4`, `Requests`

---

## 🚀 시작하기 (Quick Start)

### 1. 로컬 환경 설치
저장소를 클론한 후 필요한 패키지를 설치합니다.
```bash
git clone [https://github.com/bobospark/comment_maker.git](https://github.com/bobospark/comment_maker.git)
cd comment_maker
pip install -r requirements.txt
```
### 2. 앱 실행
```
streamlit run comment_maker.py
```

3. API Key 설

4. ⚠️ 주의사항 (Disclaimer)
* ** 본 도구는 소통의 보조 수단입니다. 네이버 운영 정책을 준수하기 위해 생성된 결과물을 확인 후 수동으로 등록하는 것을 권장합니다.

* ** 무료 티어 API 사용 시 호출 횟수 제한(429 Error)이 발생할 수 있습니다. 이 경우 잠시 후 다시 시도해 주세요.

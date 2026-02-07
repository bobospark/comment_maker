import streamlit as st
from google import genai
import requests
from bs4 import BeautifulSoup
import re
import logging
import os
import time
from datetime import datetime

# 1. 터미널 및 파일 로깅 설정
log_filename = "blog_agent_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 세션 상태 초기화
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_result' not in st.session_state:
    st.session_state.current_result = None

# [기능] 네이버 블로그 본문 크롤링
def get_naver_blog_content(url):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://section.blog.naver.com/"
    }
    try:
        url = url.strip()
        logger.info(f"==================== [분석 시작: {url}] ====================")
        response = session.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        iframe = soup.find('iframe', id='mainFrame')
        if not iframe: return None, "게시글 세부 주소를 입력해주세요."

        real_url = "https://blog.naver.com" + iframe['src']
        res = session.get(real_url, headers=headers, timeout=10)
        main_soup = BeautifulSoup(res.text, 'html.parser')
        
        selectors = ['div.se-main-container', 'div#post-view-area', 'div.se-viewer']
        content_element = None
        for s in selectors:
            content_element = main_soup.select_one(s)
            if content_element: break
        
        if not content_element: return None, "본문 태그를 찾지 못했습니다."
        
        text = content_element.get_text(separator="\n", strip=True)
        logger.info(f"--- [추출 본문 로그] ---\n{text[:500]}...\n----------------------")
        return text, None
    except Exception as e:
        logger.error(f"크롤링 에러: {e}")
        return None, str(e)

# [기능] Gemini 댓글 생성 (안전 모드)
def generate_comment_safe(api_key, model_name, content, extra_text):
    client = genai.Client(api_key=api_key)
    if len(content) > 2000:
        refined_content = content[:1000] + "\n...(중략)...\n" + content[-1000:]
    else:
        refined_content = content

    prompt = f"""
    네이버 블로그 소통 전문가로서 정중한 댓글을 작성하세요.
    1. 요약: 1문장 요약.
    2. 댓글: 본문 내용 공감 및 칭찬.
    3. 요청: 마지막에 "서로이웃 맺고 소통하며 지내고 싶어요 :)" 포함.
    4. 추가 문구: "{extra_text}"
    
    [본문]
    {refined_content}

    [출력 형식]
    댓글 :
    """

    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text, None
    except Exception as e:
        return None, str(e)

# 3. Streamlit UI 설정
st.set_page_config(page_title="Naver Blog History Agent", layout="wide")

# CSS 스타일 (자동 줄바꿈 및 깔끔한 박스)
st.markdown("""
    <style>
    .comment-box {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        padding: 20px;
        border-radius: 10px;
        font-size: 1rem;
        line-height: 1.6;
        color: #1f2937;
        white-space: pre-wrap;
        word-break: keep-all;
    }
    .extra-tag {
        display: inline-block;
        background-color: #e5e7eb;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #4b5563;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 네이버 블로그 댓글 에이전트")

with st.sidebar:
    st.header("🔑 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    
    selected_model = st.selectbox("모델 선택", ["gemini-2.0-flash", "gemini-2.5-flash-preview-09-2025", "gemini-3-flash-preview"])
    if st.button("전체 기록 삭제"):
        st.session_state.history = []
        st.session_state.current_result = None
        open(log_filename, "w", encoding="utf-8").close()
        st.rerun()

# 레이아웃 구성
col_input, col_history = st.columns([1, 1.2])

with col_input:
    st.subheader("📝 댓글 생성하기")
    url_input = st.text_input("🔗 블로그 게시글 주소", placeholder="https://blog.naver.com/...")
    extra_input = st.text_area("✍️ 내가 쓴 추가 문구", placeholder="예: LG 다니는 직장인입니다!")
    
    if st.button("🚀 댓글 생성하기", use_container_width=True):
        if not api_key or not url_input:
            st.warning("API Key와 URL을 입력해주세요.")
        else:
            with st.spinner("AI가 내용을 읽고 있습니다..."):
                # 새로운 생성 시 기존 결과는 히스토리로 이동 (가장 위로)
                if st.session_state.current_result:
                    st.session_state.history.insert(0, st.session_state.current_result)
                
                text, c_err = get_naver_blog_content(url_input)
                if not c_err:
                    res, a_err = generate_comment_safe(api_key, selected_model, text, extra_input)
                    if not a_err:
                        # 현재 결과 업데이트
                        st.session_state.current_result = {
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "url": url_input,
                            "extra": extra_input,
                            "comment": res
                        }
                        st.success("새로운 댓글이 생성되었습니다! 아래에서 확인하세요.")
                    else:
                        st.error(f"AI 에러: {a_err}")
                else:
                    st.error(c_err)

    # --- [새로 나온 결과 표시 영역] ---
    if st.session_state.current_result:
        st.markdown("---")
        st.markdown("### ✨ 최신 생성 결과")
        curr = st.session_state.current_result
        st.markdown(f"🕒 **생성 시간:** {curr['timestamp']}")
        st.link_button("🔗 해당 블로그 바로가기", curr['url'])
        
        if curr['extra']:
            st.markdown(f'<div class="extra-tag">요청 문구: {curr["extra"]}</div>', unsafe_allow_html=True)
            
        st.markdown(f'<div class="comment-box">{curr["comment"]}</div>', unsafe_allow_html=True)
        st.info("다음 댓글을 생성하면 이 내용은 오른쪽 히스토리로 이동합니다.")

with col_history:
    st.subheader("📜 작업 히스토리 (이전 기록)")
    if not st.session_state.history:
        st.write("이전 작업 기록이 없습니다.")
    else:
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"📌 [{item['timestamp']}] {item['url'][:40]}...", expanded=False):
                st.link_button("🔗 블로그 방문", item['url'])
                
                if item['extra']:
                    st.caption(f"💡 포함된 문구: {item['extra']}")
                
                st.markdown(f"""
                <div class="comment-box" style="font-size: 0.9rem; padding: 12px; background-color: #ffffff;">
                {item['comment']}
                </div>
                """, unsafe_allow_html=True)
                st.write("")
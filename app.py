import streamlit as st
import pandas as pd
import google.generativeai as genai
import base64
from pathlib import Path

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="큰틀전략 메이커",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 이미지 파일을 Base64로 인코딩하는 함수 ---
def img_to_base_64(image_path):
    """로컬 이미지 파일을 Base64 문자열로 변환합니다."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# --- UI 스타일 적용 함수 ---
def apply_ui_styles():
    """앱 전체에 적용될 CSS 스타일을 정의합니다."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
            
            :root {
                --primary-color: #2BA7D1;
                --primary-color-hover: #2596BC;
                --black-color: #0D1628;
                --secondary-color: #86929A;
                --divider-color: #E5E7EB;
                --bg-color: #F0F2F5;
                --icon-bg-color: rgba(43, 167, 209, 0.1);
            }

            /* 기본 배경/폰트 */
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
                background-color: var(--bg-color) !important;
                color: var(--black-color) !important;
            }
            [data-testid="stSidebar"] { background-color: #FFFFFF !important; color: var(--black-color) !important; }
            body { font-family: 'Noto Sans KR', sans-serif !important; }

            /* 헤더 / 푸터 숨김 */
            header[data-testid="stHeader"], footer { display: none !important; }

            div.block-container { padding: 1.5rem 1rem 2rem 1rem !important; }

            /* ========== 핵심: form wrapper를 보이지 않게(공간 제거 포함) ========== */
            /* form 기능은 유지하되 wrapper 자체를 화면에서 제거(공백 제거 목적) */
            .stForm, div[data-testid="stForm"], div[data-testid="stForm"] > div, div[data-testid="stForm"] > div > div {
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
                box-shadow: none !important;
                display: contents !important; /* wrapper 자체를 DOM 레이아웃 상에서 제거 */
            }

            .header-group {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 8px;
            }

            .icon-container {
                width: 80px; height: 80px;
                background-color: var(--icon-bg-color);
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                flex-shrink: 0;
            }
            .icon-container img { width: 64px; height: 64px; object-fit: contain; }

            .main-title { font-size: 28px; font-weight: 700; margin: 0; color: var(--black-color) !important; }
            .main-subtitle { font-size: 16px; color: var(--secondary-color) !important; margin-bottom: 1.5rem; }

            /* 상단 메뉴 블록 스타일 (원래대로 유지) */
            div[data-testid="stHorizontalBlock"] {
                border: 1px solid var(--divider-color) !important;
                background-color: white !important;
                border-radius: 14px;
                padding: 6px !important;
                margin-bottom: 1.5rem; 
            }
            div[data-testid="stHorizontalBlock"] .stButton button {
                background-color: white !important;
                color: var(--secondary-color) !important;
                border-radius: 10px;
                font-size: 14px;
                border: none;
                padding: 0.8rem 0;
            }
            div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"] {
                background-color: var(--primary-color) !important;
                color: white !important;
                font-weight: 700;
            }

            .content-area { margin-top: 0; }

            .form-container {
                background-color: white !important;
                padding: 1.75rem;
                border-radius: 16px;
                box-shadow: none !important;
            }

            /* ========== 핵심: '전략 저장하기' 와 'AI에게 추천받기' 버튼만 색 고정 ========== */
            /* form 내부(= .form-container)에 있는 제출/버튼 요소들을 목표로 지정.
               Streamlit DOM 구조가 달라질 수 있어 다양한 선택자를 함께 사용해 적용 가능성 높였습니다. */
            .form-container .stButton > button,
            .form-container button[type="submit"],
            .form-container button[kind="primary"],
            .form-container button[kind="formSubmit"] {
                background-color: var(--primary-color) !important;
                color: white !important;
                border-radius: 12px !important;
                padding: 12px 0 !important;
                font-size: 16px !important;
                font-weight: 600 !important;
                border: none !important;
            }
            .form-container .stButton > button:hover,
            .form-container button[type="submit"]:hover,
            .form-container button[kind="primary"]:hover,
            .form-container button[kind="formSubmit"]:hover {
                background-color: var(--primary-color-hover) !important;
            }

            /* 입력창 스타일 */
            .stTextInput input, .stTextArea textarea, input[type="text"], textarea, .stTextInput > div > input, .stTextArea > div > textarea {
                background-color: #FFFFFF !important;
                border: 1px solid var(--divider-color) !important;
                border-radius: 12px !important;
                color: var(--black-color) !important;
                padding: 10px 12px !important;
            }
            .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: var(--secondary-color) !important; }

            .strategy-item {
                background-color: white !important;
                border: 1px solid var(--divider-color) !important;
                border-radius: 12px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
                color: var(--black-color) !important;
            }
            .strategy-item .stButton button {
                background-color: #FEE2E2 !important;
                color: #EF4444 !important;
                font-size: 12px;
                border-radius: 8px;
            }

            /* 반응형 */
            @media (max-width: 640px) {
                .header-group { gap: 12px; }
                .main-title { font-size: 22px; }
            }
        </style>
    """, unsafe_allow_html=True)

# --- Streamlit Secrets에서 API 키 가져오기 ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    api_key_configured = True
except (KeyError, AttributeError):
    api_key_configured = False

# --- 데이터 및 상태 초기화 ---
if 'menu' not in st.session_state:
    st.session_state.menu = "✍️ 나의 큰틀전략"
if 'my_strategies' not in st.session_state:
    st.session_state.my_strategies = pd.DataFrame(columns=['이름', '큰틀전략'])
if 'ai_strategies' not in st.session_state:
    st.session_state.ai_strategies = []

# --- UI 렌더링 시작 ---
apply_ui_styles()

# --- 헤더 UI (아이콘 + 제목 왼쪽 정렬) ---
# icon.png 파일은 같은 폴더에 둬야 합니다.
try:
    icon_path = Path(__file__).parent / "icon.png"
except NameError:
    # 로컬 개발 환경에서 __file__이 없을 경우 대비
    icon_path = Path("icon.png")
# img_to_base_64 함수는 문자열 경로를 받도록 안전하게 전달
icon_base_64 = img_to_base_64(str(icon_path))

st.markdown('<div class="header-group">', unsafe_allow_html=True)
if icon_base_64:
    st.markdown(f'<div class="icon-container"><img src="data:image/png;base64,{icon_base_64}" alt="App Icon"></div>', unsafe_allow_html=True)
st.markdown('<p class="main-title">큰틀전략 메이커</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p class="main-subtitle">나만의 다짐을 기록하고, AI에게 영감을 얻고,<br>레전드에게 배우는 멘탈 관리</p>', unsafe_allow_html=True)

# --- 상단 메뉴 UI (콜백 방식) ---
def set_menu(menu_selection):
    st.session_state.menu = menu_selection

cols = st.columns(3)
menu_items = ["✍️ 나의 큰틀전략", "🤖 AI 전략 코치", "🏆 명예의 전당"]

for i, item in enumerate(menu_items):
    with cols[i]:
        is_active = (st.session_state.menu == item)
        try:
            button_type = "primary" if is_active else "secondary"
            st.button(
                item,
                key=f"button_{i}",
                use_container_width=True,
                type=button_type,
                on_click=set_menu,
                args=(item,)
            )
        except TypeError:
            # fallback — 'type' 인자가 없는 버전용
            st.button(
                item,
                key=f"button_{i}",
                use_container_width=True,
                on_click=set_menu,
                args=(item,)
            )

# --- 메인 화면 로직 ---
st.markdown('<div class="content-area">', unsafe_allow_html=True)

# 1. '나의 큰틀전략' 메뉴
if st.session_state.menu == "✍️ 나의 큰틀전략":
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    # form 기능은 유지하되 wrapper는 CSS로 보이지 않게 처리되어 공백이 없어집니다.
    with st.form("my_strategy_form"):
        st.text_input("이름 (또는 이니셜)", key="user_name")
        st.text_area("나의 큰틀전략은...", height=100, key="user_strategy")
        # 이 버튼은 form 내부의 submit 버튼으로 렌더되어 .form-container 관련 CSS로 색상이 고정됩니다.
        submitted = st.form_submit_button("전략 저장하기", use_container_width=True)

        if submitted and st.session_state.get("user_name") and st.session_state.get("user_strategy"):
            new_data = pd.DataFrame({'이름': [st.session_state.user_name], '큰틀전략': [st.session_state.user_strategy]})
            st.session_state.my_strategies = pd.concat([st.session_state.my_strategies, new_data], ignore_index=True)
            st.success("새로운 큰틀전략이 저장되었습니다!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("나의 큰틀전략 목록")
    if not st.session_state.my_strategies.empty:
        # reversed order: 최신이 위로
        for index, row in reversed(list(st.session_state.my_strategies.iterrows())):
            st.markdown('<div class="strategy-item">', unsafe_allow_html=True)
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.caption(f"작성자: {row['이름']}")
                st.write(f"**{row['큰틀전략']}**")
            with col2:
                if st.button("삭제", key=f"delete_{index}", use_container_width=True):
                    # 삭제 후 인덱스 리셋하여 꼬임 방지
                    st.session_state.my_strategies = st.session_state.my_strategies.drop(index).reset_index(drop=True)
                    # rerun으로 화면 갱신
                    try:
                        st.rerun()
                    except Exception:
                        # 구 버전 안전망
                        st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("아직 저장된 전략이 없습니다.")

# 2. 'AI 전략 코치' 메뉴
elif st.session_state.menu == "🤖 AI 전략 코치":
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("AI에게 당신의 상황을 이야기하고 **멘탈 코칭**을 받아보세요.")
    if not api_key_configured:
        st.error("AI 코치 기능을 사용하기 위한 API 키가 설정되지 않았습니다.")
    else:
        user_prompt = st.text_area("어떤 상황인가요?", placeholder="예: 너무 긴장돼요, 자신감이 떨어졌어요", height=100)
        # 이 버튼은 form-container 내부 버튼이므로 CSS로 색상이 고정됩니다.
        if st.button("AI에게 추천받기", use_container_width=True): 
            if user_prompt:
                with st.spinner('AI 코치가 당신만을 위한 전략을 구상 중입니다...'):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"""
                        You are a world-class performance psychologist. Your specialty is creating a 'Big-Picture Strategy' (큰틀전략).
                        An athlete is facing: '{user_prompt}'.
                        Create three distinct 'Big-Picture Strategies' for them in KOREAN.
                        For each, provide:
                        - **[전략]**: The core strategy phrase.
                        - **[해설]**: A brief explanation.
                        Format the output exactly like this:
                        [전략]: (Strategy in Korean)
                        [해설]: (Explanation in Korean)
                        ---
                        (Repeat for next two)
                        """
                        response = model.generate_content(prompt)
                        st.session_state.ai_strategies = []
                        # 방어적 처리: response.text가 없을 경우 오류 방지
                        text_out = getattr(response, "text", None)
                        if not text_out:
                            # 대체 구조 시도 (구버전/다른 SDK 포맷)
                            try:
                                # some SDKs put candidates / outputs
                                text_out = response.candidates[0].output
                            except Exception:
                                text_out = None
                        if not text_out:
                            st.error("AI 응답을 불러오지 못했습니다. (응답 포맷이 예상과 다릅니다.)")
                        else:
                            for block in text_out.split('---'):
                                if '[전략]:' in block and '[해설]:' in block:
                                    strategy = block.split('[전략]:')[1].split('[해설]:')[0].strip()
                                    explanation = block.split('[해설]:')[1].strip()
                                    st.session_state.ai_strategies.append({'strategy': strategy, 'explanation': explanation})
                    except Exception as e:
                        st.error(f"AI 호출 중 오류가 발생했습니다: {e}")
            else:
                st.warning("현재 상황을 입력해주세요.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.ai_strategies:
        st.subheader("AI 코치의 추천 큰틀전략")
        for item in st.session_state.ai_strategies:
            st.markdown('<div class="strategy-item">', unsafe_allow_html=True)
            st.markdown(f"#### 💡 {item['strategy']}")
            st.caption(item['explanation'])
            st.markdown('</div>', unsafe_allow_html=True)

# 3. '명예의 전당' 메뉴
elif st.session_state.menu == "🏆 명예의 전당":
    athletes_data = [
        {'선수': '김연아', '종목': '피겨 스케이팅', '전략': '무슨 일이 있더라도, 내가 할 수 있는 것에만 집중하고 최선을 다할 뿐이다.'},
        {'선수': '마이클 조던', '종목': '농구', '전략': '한계에 부딪히더라도, 그건 환상일 뿐이다.'},
        {'선수': '박지성', '종목': '축구', '전략': '쓰러질지언정 무릎은 꿇지 않는다.'},
        {'선수': '손흥민', '종목': '축구', '전략': '어제의 기쁨은 어제로 끝내고, 새로운 날을 준비한다.'},
        {'선수': '이상혁 \'페이커\'', '종목': 'e스포츠', '전략': '방심하지 않고, 이기든 지든 내 플레이를 하자.'},
    ]
    df_athletes = pd.DataFrame(athletes_data)
    
    sports = ['모두 보기'] + sorted(df_athletes['종목'].unique())
    selected_sport = st.selectbox('종목별로 보기', sports, label_visibility="collapsed")

    if selected_sport == '모두 보기':
        filtered_df = df_athletes
    else:
        filtered_df = df_athletes[df_athletes['종목'] == selected_sport]

    for index, row in filtered_df.iterrows():
        st.markdown(f"""
        <div class="strategy-item">
            <p style="font-size: 14px; color: var(--primary-color); font-weight: 700;">{row['선수']} <span style="font-size: 12px; color: var(--secondary-color); font-weight: 400;">({row['종목']})</span></p>
            <p style="font-size: 16px; color: var(--black-color); margin-top: 8px;">"{row['전략']}"</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

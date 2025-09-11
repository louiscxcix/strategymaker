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
                --black-color: #0D1628;
                --secondary-color: #86929A;
                --divider-color: #E5E7EB;
                --bg-color: #F0F2F5;
            }

            body, .stTextArea, .stButton>button, .stTextInput {
                font-family: 'Noto Sans KR', sans-serif;
            }

            .stApp {
                background-color: var(--bg-color);
            }
            
            header[data-testid="stHeader"], footer {
                display: none !important;
            }
            div.block-container {
                padding: 1.5rem 1rem 2rem 1rem !important;
            }
            
            .header-group {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 8px;
            }

            .icon-container {
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }
            .icon-container img {
                width: 128px !important;
                height: 128px !important;
                object-fit: contain !important;
            }

            .main-title {
                font-size: 28px;
                font-weight: 700;
                color: var(--black-color);
                margin: 0;
            }
            .main-subtitle {
                font-size: 16px;
                color: var(--secondary-color);
                text-align: left;
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }
            
            /* --- 메뉴 버튼 컨테이너 --- */
            div[data-testid="stHorizontalBlock"] {
                background-color: transparent !important;
                border: none !important;
                padding: 0 !important;
                margin-bottom: 1.5rem !important;
            }
            
            /* --- 메뉴 버튼 스타일 --- */
            div[data-testid="stHorizontalBlock"] .stButton > button {
                background-color: #FFFFFF !important;
                color: #444444 !important;
                border-radius: 10px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                border: 1px solid #DDDDDD !important;
                box-shadow: none !important;
                transition: none !important;
            }
            div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] {
                background-color: var(--primary-color) !important;
                color: #FFFFFF !important;
                font-weight: 700 !important;
                border: none !important;
            }
            
            /* --- 일반 버튼 (전략 저장하기, AI 추천받기) --- */
            .stButton > button,
            .stForm button,
            .stForm [data-testid="baseButton-secondary"] {
                background-color: #2BA7D1 !important;
                color: #FFFFFF !important;
                border-radius: 12px !important;
                padding: 12px 0 !important;
                font-size: 16px !important;
                font-weight: 600 !important;
                border: none !important;
                box-shadow: none !important;
            }
            .stButton > button:hover,
            .stForm button:hover {
                background-color: #2387A8 !important;
                color: #FFFFFF !important;
            }

            /* --- 입력창 스타일 (배경 흰색 & 테두리 구분) --- */
            .stTextInput input, .stTextArea textarea {
                background-color: #FFFFFF !important;
                border: 1px solid var(--divider-color) !important;
                border-radius: 12px !important;
                padding: 10px 12px !important;
            }

            /* --- 불필요한 form 배경 박스 제거 --- */
            .stForm, div[data-testid="stForm"] {
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
                box-shadow: none !important;
            }

            .strategy-item {
                background-color: white;
                border: 1px solid var(--divider-color);
                border-radius: 12px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
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
icon_path = Path(__file__).parent / "icon.png"
icon_base64 = img_to_base_64(icon_path)

st.markdown('<div class="header-group">', unsafe_allow_html=True)
if icon_base64:
    st.markdown(f'<div class="icon-container"><img src="data:image/png;base64,{icon_base64}" alt="App Icon"></div>', unsafe_allow_html=True)
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
        button_type = "primary" if is_active else "secondary"
        
        st.button(
            item, 
            key=f"button_{i}", 
            use_container_width=True, 
            type=button_type,
            on_click=set_menu,
            args=(item,)
        )


# --- 메인 화면 로직 ---
st.markdown('<div class="content-area">', unsafe_allow_html=True)

# 1. '나의 큰틀전략' 메뉴
if st.session_state.menu == "✍️ 나의 큰틀전략":
    with st.form("my_strategy_form"):
        st.text_input("이름 (또는 이니셜)", key="user_name")
        st.text_area("나의 큰틀전략은...", height=100, key="user_strategy")
        submitted = st.form_submit_button("전략 저장하기", use_container_width=True)

        if submitted and st.session_state.user_name and st.session_state.user_strategy:
            new_data = pd.DataFrame({'이름': [st.session_state.user_name], '큰틀전략': [st.session_state.user_strategy]})
            st.session_state.my_strategies = pd.concat([st.session_state.my_strategies, new_data], ignore_index=True)
            st.success("새로운 큰틀전략이 저장되었습니다!")
    
    st.subheader("나의 큰틀전략 목록")
    if not st.session_state.my_strategies.empty:
        for index, row in reversed(list(st.session_state.my_strategies.iterrows())):
            st.markdown('<div class="strategy-item">', unsafe_allow_html=True)
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.caption(f"작성자: {row['이름']}")
                st.write(f"**{row['큰틀전략']}**")
            with col2:
                if st.button("삭제", key=f"delete_{index}", use_container_width=True):
                    st.session_state.my_strategies = st.session_state.my_strategies.drop(index)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("아직 저장된 전략이 없습니다.")


# 2. 'AI 전략 코치' 메뉴
elif st.session_state.menu == "🤖 AI 전략 코치":
    st.markdown("AI에게 당신의 상황을 이야기하고 **멘탈 코칭**을 받아보세요.")
    if not api_key_configured:
        st.error("AI 코치 기능을 사용하기 위한 API 키가 설정되지 않았습니다.")
    else:
        user_prompt = st.text_area("어떤 상황인가요?", placeholder="예: 너무 긴장돼요, 자신감이 떨어졌어요", height=100)
        if st.button("AI에게 추천받기", use_container_width=True): 
            if user_prompt:
                with st.spinner('AI 코치가 당신만을 위한 전략을 구상 중입니다...'):
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
                    for block in response.text.split('---'):
                        if '[전략]:' in block and '[해설]:' in block:
                            strategy = block.split('[전략]:')[1].split('[해설]:')[0].strip()
                            explanation = block.split('[해설]:')[1].strip()
                            st.session_state.ai_strategies.append({'strategy': strategy, 'explanation': explanation})
            else:
                st.warning("현재 상황을 입력해주세요.")
    
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


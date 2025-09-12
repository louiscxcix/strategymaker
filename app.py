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
                --divider-color: #F1F1F1;
                --bg-color: #F9F8FB;
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

            div.block-container { padding: 2rem 1rem 3rem 1rem !important; }

            /* Form wrapper 자체를 화면에서 제거 */
            .stForm, div[data-testid="stForm"], div[data-testid="stForm"] > div, div[data-testid="stForm"] > div > div {
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
                box-shadow: none !important;
                display: contents !important; 
            }

            /* 헤더 그룹 */
            .header-group {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 8px;
            }
            .icon-container {
                width: 68px; height: 68px;
                background-color: var(--icon-bg-color);
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                flex-shrink: 0;
            }
            .icon-container img { width: 52px; height: 52px; object-fit: contain; }

            .main-title { font-size: 20px; font-weight: 700; margin: 0; color: var(--black-color) !important; }
            .main-subtitle { font-size: 13px; color: var(--secondary-color) !important; margin-bottom: 1.5rem; line-height: 1.5; }

            /* 상단 메뉴 블록 스타일 */
            div[data-testid="stHorizontalBlock"] {
                border: 1px solid var(--divider-color) !important;
                background-color: white !important;
                border-radius: 12px;
                padding: 4px !important;
                margin-bottom: 2rem; 
            }
            /* 상단 메뉴 버튼 공통 */
            div[data-testid="stHorizontalBlock"] .stButton button {
                background-color: transparent !important;
                color: var(--secondary-color) !important;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                border: none;
                padding: 0.6rem 0;
            }
            /* 활성화된 메뉴 버튼 */
            div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"] {
                background-color: var(--primary-color) !important;
                color: white !important;
                font-weight: 700;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05);
            }

            /* 입력폼 섹션 스타일 */
            .form-section {
                padding-bottom: 20px;
                margin-bottom: 20px;
                border-bottom: 1px solid var(--divider-color);
            }
            .input-label {
                font-size: 18px;
                font-weight: 700;
                color: var(--black-color);
                margin-bottom: 12px;
                line-height: 1.5;
            }
            .input-label.light {
                font-weight: 400;
                margin-bottom: 0;
            }
            .input-label.strong {
                margin-top: -4px;
            }

            /* 입력창 스타일 */
            .stTextInput input, .stTextArea textarea {
                background-color: #FFFFFF !important;
                border: 1px solid var(--divider-color) !important;
                border-radius: 12px !important;
                color: var(--black-color) !important;
                padding: 12px 14px !important;
            }

            /* 제출 버튼 컨테이너 ('전략 저장하기', 'AI에게 추천받기') */
            .submit-button-container .stButton button {
                background: var(--primary-color) !important;
                color: white !important;
                border-radius: 12px !important;
                padding: 14px 0 !important;
                font-size: 16px !important;
                font-weight: 700 !important;
                border: none !important;
                box-shadow: 0px 5px 10px rgba(43, 167, 209, 0.2);
            }
             .submit-button-container .stButton button:hover {
                background: var(--primary-color-hover) !important;
             }

            /* 목록 헤더 */
            .list-header { margin-top: 2rem; }
            .list-header .label { font-size: 12px; color: var(--secondary-color); }
            .list-header .title { font-size: 18px; font-weight: 700; color: var(--black-color); }

            /* 목록 아이템 (공통) */
            .strategy-item {
                background-color: transparent !important;
                border: none !important;
                border-bottom: 1px solid var(--divider-color) !important;
                border-radius: 0px;
                padding: 1.2rem 0.2rem;
                margin-bottom: 0rem;
                color: var(--black-color) !important;
            }
             /* 마지막 아이템은 밑줄 제거 */
            .strategy-item:last-child {
                border-bottom: none !important;
            }
            
            /* 삭제 버튼 */
            .strategy-item .stButton button {
                background-color: var(--divider-color) !important;
                color: var(--secondary-color) !important;
                font-size: 12px;
                font-weight: 500;
                border-radius: 8px;
                border: none;
            }
            .strategy-item .stButton button:hover {
                background-color: #e5e7eb !important;
                color: var(--black-color) !important;
            }

            /* 명예의 전당 카드 */
            .hall-of-fame-card {
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

# --- 헤더 UI (아이콘 + 제목) ---
icon_path = Path("icon.png")
icon_base_64 = img_to_base_64(str(icon_path))

st.markdown('<div class="header-group">', unsafe_allow_html=True)
if icon_base_64:
    st.markdown(f'<div class="icon-container"><img src="data:image/png;base64,{icon_base_64}" alt="App Icon"></div>', unsafe_allow_html=True)
st.markdown('<div><p class="main-title">큰틀전략</p></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">나만의 다짐을 기록하고, AI에게 영감을 얻고,<br>레전드에게 배우는 멘탈 관리</p>', unsafe_allow_html=True)


# --- 상단 메뉴 UI (콜백 방식) ---
def set_menu(menu_selection):
    st.session_state.menu = menu_selection

cols = st.columns(3)
menu_items = ["✍️ 나의 큰틀전략", "🤖 AI 전략 코치", "🏆 명예의 전당"]

for i, item in enumerate(menu_items):
    with cols[i]:
        st.button(
            item,
            key=f"button_{i}",
            use_container_width=True,
            type="primary" if st.session_state.menu == item else "secondary",
            on_click=set_menu,
            args=(item,)
        )

# --- 메인 화면 로직 ---
st.markdown('<div class="content-area">', unsafe_allow_html=True)

# 1. '나의 큰틀전략' 메뉴
if st.session_state.menu == "✍️ 나의 큰틀전략":
    with st.form("my_strategy_form"):
        # --- 이름 입력 섹션 ---
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="input-label">이름 (또는 이니셜)</p>', unsafe_allow_html=True)
        st.text_input("user_name_input", key="user_name", placeholder="이름을 입력하세요", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 큰틀전략 입력 섹션 ---
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="input-label">나의 큰틀전략은...</p>', unsafe_allow_html=True)
        st.text_area("user_strategy_input", height=100, key="user_strategy", placeholder="나만의 다짐이나 전략을 적어보세요", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- 저장 버튼 ---
        st.markdown('<div class="submit-button-container">', unsafe_allow_html=True)
        submitted = st.form_submit_button("전략 저장하기", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted and st.session_state.get("user_name") and st.session_state.get("user_strategy"):
            new_data = pd.DataFrame({'이름': [st.session_state.user_name], '큰틀전략': [st.session_state.user_strategy]})
            st.session_state.my_strategies = pd.concat([st.session_state.my_strategies, new_data], ignore_index=True)
            st.success("새로운 큰틀전략이 저장되었습니다!")
    
    # --- 나의 큰틀전략 목록 ---
    if not st.session_state.my_strategies.empty:
        st.markdown('<div class="list-header"><p class="label">큰틀전략</p><p class="title">나의 큰틀전략 목록</p></div>', unsafe_allow_html=True)
        for index, row in reversed(list(st.session_state.my_strategies.iterrows())):
            st.markdown('<div class="strategy-item">', unsafe_allow_html=True)
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.caption(f"작성자: {row['이름']}")
                st.write(f"**{row['큰틀전략']}**")
            with col2:
                if st.button("삭제", key=f"delete_{index}", use_container_width=True):
                    st.session_state.my_strategies = st.session_state.my_strategies.drop(index).reset_index(drop=True)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# 2. 'AI 전략 코치' 메뉴
elif st.session_state.menu == "🤖 AI 전략 코치":
    # --- ✨✨✨ UI 수정 시작 ✨✨✨ ---
    if not api_key_configured:
        st.error("AI 코치 기능을 사용하기 위한 API 키가 설정되지 않았습니다.")
    else:
        # --- AI 코치 입력 섹션 ---
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="input-label light">AI에게 상황을 말하고 코칭을 받아보세요</p><p class="input-label strong">어떤 상황인가요?</p>', unsafe_allow_html=True)
        user_prompt = st.text_area("ai_prompt_input", height=100, placeholder="예: 너무 긴장돼요, 자신감이 떨어졌어요", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 추천받기 버튼 ---
        st.markdown('<div class="submit-button-container">', unsafe_allow_html=True)
        if st.button("AI에게 추천받기", use_container_width=True): 
            if user_prompt:
                with st.spinner('AI 코치가 당신만을 위한 전략을 구상 중입니다...'):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"""
                        You are a world-class performance psychologist who creates 'Big-Picture Strategies' (큰틀전략) for athletes.
                        An athlete is facing this situation: '{user_prompt}'.

                        Generate FIVE completely different 'Big-Picture Strategies' for them in KOREAN.
                        Each strategy must come from a unique psychological angle (e.g., cognitive reframing, behavioral focus, mindfulness, motivational, process-oriented).

                        For each strategy, provide:
                        - **[전략]**: The core strategy phrase.
                        - **[해설]**: A very concise, single-sentence explanation (strictly under 50 characters).

                        Format the output exactly like this, separating each with '---':
                        [전략]: (Strategy in Korean)
                        [해설]: (Explanation in Korean, max 50 characters)
                        ---
                        (Repeat for all five strategies)
                        """
                        response = model.generate_content(prompt)
                        st.session_state.ai_strategies = []
                        text_out = getattr(response, "text", None) or ""
                        
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
    
    # --- AI 코치 추천 목록 ---
    if st.session_state.ai_strategies:
        st.markdown('<div class="list-header"><p class="label">큰틀전략</p><p class="title">AI 코치의 큰틀전략</p></div>', unsafe_allow_html=True)
        for item in st.session_state.ai_strategies:
            st.markdown('<div class="strategy-item">', unsafe_allow_html=True)
            st.markdown(f"##### 💡 {item['strategy']}")
            st.caption(item['explanation'])
            st.markdown('</div>', unsafe_allow_html=True)
    # --- ✨✨✨ UI 수정 끝 ✨✨✨ ---

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

    filtered_df = df_athletes if selected_sport == '모두 보기' else df_athletes[df_athletes['종목'] == selected_sport]

    for index, row in filtered_df.iterrows():
        st.markdown(f"""
        <div class="hall-of-fame-card">
            <p style="font-size: 14px; color: var(--primary-color); font-weight: 700;">{row['선수']} <span style="font-size: 12px; color: var(--secondary-color); font-weight: 400;">({row['종목']})</span></p>
            <p style="font-size: 16px; color: var(--black-color); margin-top: 8px;">"{row['전략']}"</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="큰틀전략 메이커",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed" # 사이드바를 기본적으로 닫아둠
)

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
                --gray-color: #898D99;
                --divider-color: #F1F1F1;
                --bg-color: #F0F2F5;
            }

            body, .stTextArea, .stButton>button, .stTextInput {
                font-family: 'Noto Sans KR', sans-serif;
            }

            .stApp {
                background-color: var(--bg-color);
            }
            
            /* Streamlit 헤더와 기본 여백 제거 */
            header[data-testid="stHeader"], footer {
                display: none !important;
            }
            div.block-container {
                padding: 1.5rem 1rem 2rem 1rem !important;
            }

            .main-title {
                font-size: 28px;
                font-weight: 700;
                color: var(--black-color);
                text-align: center;
                margin-bottom: 8px;
            }
            .main-subtitle {
                font-size: 16px;
                color: var(--secondary-color);
                text-align: center;
                margin-bottom: 2.5rem;
            }
            
            /* 메뉴 버튼 스타일 */
            div[data-testid="stHorizontalBlock"] > div {
                border: 1px solid var(--divider-color);
                background-color: white;
                padding: 0 !important;
                margin: 0 !important;
            }
            div[data-testid="stHorizontalBlock"] .stButton button {
                background-color: transparent;
                color: var(--secondary-color);
                border-radius: 0;
                width: 100%;
                font-size: 14px;
                font-weight: 500;
                border: none;
                padding: 1rem 0;
            }
            /* 활성 메뉴 버튼 스타일 */
            div[data-testid="stHorizontalBlock"] .stButton button.active-menu {
                color: var(--primary-color);
                border-bottom: 2px solid var(--primary-color);
                font-weight: 700;
            }
            
            /* 폼 컨테이너 스타일 */
            .form-container {
                background-color: white;
                padding: 2rem;
                border-radius: 16px;
                margin-top: 2rem;
            }
            
            h3 { /* Subheader 스타일 */
                font-size: 20px;
                font-weight: 700;
                color: var(--black-color);
                margin-top: 2rem;
            }
            
            /* 저장하기 버튼 스타일 */
            .stForm .stButton button {
                background-color: var(--primary-color);
                color: white;
                border-radius: 12px;
                padding: 14px 0;
                font-size: 16px;
                font-weight: 500;
                border: none;
            }
            
            /* 목록 컨테이너 스타일 */
            .strategy-item {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
            }
            .strategy-item .stButton button {
                background-color: #FEE2E2;
                color: #EF4444;
                font-size: 12px;
                border-radius: 8px;
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

st.markdown('<p class="main-title">큰틀전략 메이커</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">나만의 다짐을 기록하고, AI에게 영감을 얻고, 레전드에게 배우는 멘탈 관리</p>', unsafe_allow_html=True)

# --- 상단 메뉴 UI ---
cols = st.columns(3)
menu_items = ["✍️ 나의 큰틀전략", "🤖 AI 전략 코치", "🏆 명예의 전당"]
for i, item in enumerate(menu_items):
    with cols[i]:
        is_active = (st.session_state.menu == item)
        # HTML과 CSS를 사용하여 버튼 스타일 동적 변경
        st.markdown(f"""
        <div class="stButton">
            <button class="{'active-menu' if is_active else ''}" id="{item}" onclick="document.getElementById('{item}_hidden').click()">
                {item}
            </button>
        </div>
        """, unsafe_allow_html=True)
        # 숨겨진 버튼을 사용하여 상태 변경 트리거
        if st.button(item, key=f"{item}_hidden", use_container_width=True, type="secondary"):
            st.session_state.menu = item
            st.rerun()


# --- 메인 화면 로직 ---

# 1. '나의 큰틀전략' 메뉴
if st.session_state.menu == "✍️ 나의 큰틀전략":
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        with st.form("my_strategy_form"):
            st.text_input("이름 (또는 이니셜)", key="user_name")
            st.text_area("나의 큰틀전략은...", height=100, key="user_strategy")
            submitted = st.form_submit_button("전략 저장하기", use_container_width=True)

            if submitted and st.session_state.user_name and st.session_state.user_strategy:
                new_data = pd.DataFrame({'이름': [st.session_state.user_name], '큰틀전략': [st.session_state.user_strategy]})
                st.session_state.my_strategies = pd.concat([st.session_state.my_strategies, new_data], ignore_index=True)
                st.success("새로운 큰틀전략이 저장되었습니다!")
        st.markdown('</div>', unsafe_allow_html=True)
    
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
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("AI에게 당신의 상황을 이야기하고 **멘탈 코칭**을 받아보세요.")
    if not api_key_configured:
        st.error("AI 코치 기능을 사용하기 위한 API 키가 설정되지 않았습니다.")
    else:
        user_prompt = st.text_area("어떤 상황인가요?", placeholder="예: 너무 긴장돼요, 자신감이 떨어졌어요", height=100)
        if st.button("AI에게 추천받기", use_container_width=True, type="primary"):
            if user_prompt:
                with st.spinner('AI 코치가 당신만을 위한 전략을 구상 중입니다...'):
                    # (API 호출 로직은 기존과 동일)
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
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.ai_strategies:
        st.subheader("AI 코치의 추천 큰틀전략")
        for item in st.session_state.ai_strategies:
            with st.container(border=True):
                st.markdown(f"#### 💡 {item['strategy']}")
                st.caption(item['explanation'])

# 3. '명예의 전당' 메뉴
elif st.session_state.menu == "🏆 명예의 전당":
    athletes_data = [
        {'선수': '김연아', '종목': '피겨 스케이팅', '전략': '무슨 일이 있더라도, 내가 할 수 있는 것에만 집중하고 최선을 다할 뿐이다.'},
        {'선수': '마이클 조던', '종목': '농구', '전략': '한계에 부딪히더라도, 그건 환상일 뿐이다.'},
        {'선수': '박지성', '종목': '축구', '전략': '쓰러질지언정 무릎은 꿇지 않는다.'},
        {'선수': '손흥민', '종목': '축구', '전략': '어제의 기쁨은 어제로 끝내고, 새로운 날을 준비한다.'},
        {'선수': '이상혁 \'페이커\'', '종목': 'e스포츠', '전략': '방심하지 않고, 이기든 지든 내 플레이를 하자.'},
        # ... (이하 생략)
    ]
    df_athletes = pd.DataFrame(athletes_data)
    
    sports = ['모두 보기'] + sorted(df_athletes['종목'].unique())
    selected_sport = st.selectbox('종목별로 보기', sports)

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

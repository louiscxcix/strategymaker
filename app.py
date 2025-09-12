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
                --icon-bg-color: rgba(12, 124, 162, 0.04);
                --app-bg: linear-gradient(315deg, rgba(77, 0, 200, 0.03) 0%, rgba(29, 48, 78, 0.03) 100%), white;
            }

            /* 기본 배경/폰트 */
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
                background: var(--app-bg) !important;
                color: var(--black-color) !important;
            }
            body { font-family: 'Noto Sans KR', sans-serif !important; }

            /* 헤더 / 푸터 숨김 */
            header[data-testid="stHeader"], footer { display: none !important; }

            div.block-container { padding: 1.5rem 1rem 3rem 1rem !important; }

            /* Form wrapper 제거 */
            .stForm, div[data-testid="stForm"], div[data-testid="stForm"] > div {
                background: transparent !important; border: none !important; padding: 0 !important; margin: 0 !important; box-shadow: none !important; display: contents !important; 
            }

            /* 헤더 */
            .header-group { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; margin-bottom: 20px; }
            .icon-container { 
                width: 68px; height: 68px; padding: 8px; background: var(--icon-bg-color); border-radius: 50%; display: flex; justify-content: center; align-items: center; flex-shrink: 0; }
            .icon-container img { width: 52px; height: 52px; display: block; object-fit: contain; }
            .title-group { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; }
            .main-title { font-size: 20px; font-weight: 700; line-height: 32px; color: var(--black-color) !important; }
            .main-subtitle { font-size: 13px; font-weight: 400; line-height: 20px; color: var(--secondary-color) !important; }

            /* 상단 메뉴 */
            div[data-testid="stHorizontalBlock"] {
                background: white !important; border: 1px solid var(--divider-color) !important; border-radius: 12px; padding: 4px !important; margin-bottom: 20px; }
            div[data-testid="stHorizontalBlock"] .stButton button {
                background: transparent !important; color: var(--secondary-color) !important; border-radius: 8px; font-size: 12px; font-weight: 400; border: none; padding: 10px 4px; }
            div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"] {
                background: var(--primary-color) !important; color: white !important; font-weight: 700; box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.02); }

            /* 입력폼 */
            .form-section { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; width: 100%; padding-bottom: 20px; margin-bottom: 20px; border-bottom: 1px solid var(--divider-color); }
            .input-label { font-size: 18px; font-weight: 700; line-height: 28px; color: var(--black-color); }
            .input-label.light { font-weight: 400; }
            .stTextInput, .stTextArea { width: 100%; }
            .stTextInput input, .stTextArea textarea {
                background-color: white !important; border: 1px solid var(--divider-color) !important; border-radius: 12px !important; color: var(--black-color) !important; }
            .stTextArea textarea { min-height: 81px; }
            
            /* ================================================================== */
            /* ===== ✨ 버튼 스타일 강제 적용 (최종 수정) ✨ ===== */
            /* ================================================================== */
            
            /* '전략 저장하기' 폼 제출 버튼과 'AI에게 추천받기' 일반 버튼에 공통 스타일 적용 */
            div[data-testid="stForm"] button[type="submit"],
            .ai-button-container .stButton > button {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
                padding: 14px 36px !important;
                font-size: 14px !important;
                font-weight: 400 !important;
                color: white !important;
                background: linear-gradient(135deg, rgba(98, 120, 246, 0.20) 0%, rgba(29, 48, 78, 0) 100%), var(--primary-color) !important;
                border-radius: 12px !important;
                box-shadow: 0px 5px 10px rgba(26, 26, 26, 0.10) !important;
                border: none !important;
            }

            /* 버튼 호버 효과 */
            div[data-testid="stForm"] button[type="submit"]:hover,
            .ai-button-container .stButton > button:hover {
                color: white !important;
                background: var(--primary-color-hover) !important;
                box-shadow: 0px 2px 8px rgba(26, 26, 26, 0.10) !important;
            }
            /* ================================================================== */

            /* 목록 */
            .list-container { margin-top: 40px; }
            .list-header { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
            .list-header .label { font-size: 12px; color: var(--secondary-color); }
            .list-header .title { font-size: 18px; font-weight: 700; line-height: 28px; color: var(--black-color); }
            
            .strategy-item { padding: 16px 8px; border-bottom: 1px solid var(--divider-color); }
            .strategy-item:last-child { border-bottom: none; }
            .strategy-item .stButton button {
                background-color: var(--divider-color) !important; color: var(--secondary-color) !important; font-size: 12px; border-radius: 8px; border: none; }
            
            /* 명예의 전당 카드 */
            .hall-of-fame-card {
                background-color: white; border: 1px solid var(--divider-color); border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 1rem;}

            /* 반응형 디자인 */
            @media (max-width: 640px) {
                div.block-container { padding: 1rem 1rem 2rem 1rem !important; }
                .main-title { font-size: 18px; }
                .main-subtitle { font-size: 12px; }
                .input-label { font-size: 16px; }
                .list-header .title { font-size: 16px; }
                .header-group { flex-direction: row; align-items: center; }
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

# --- 헤더 UI ---
icon_path = Path("icon.png")
icon_base_64 = img_to_base_64(str(icon_path))

st.markdown('<div class="header-group">', unsafe_allow_html=True)
if icon_base_64:
    st.markdown(f'<div class="icon-container"><img src="data:image/png;base64,{icon_base_64}" alt="App Icon"></div>', unsafe_allow_html=True)
st.markdown('<div class="title-group"><p class="main-title">큰틀전략</p><p class="main-subtitle">나만의 다짐을 기록하고, AI에게 영감을 얻고,<br>레전드에게 배우는 멘탈 관리</p></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 상단 메뉴 UI ---
def set_menu(menu_selection):
    st.session_state.menu = menu_selection

cols = st.columns(3)
menu_items = ["✍️ 나의 큰틀전략", "🤖 AI 전략 코치", "🏆 명예의 전당"]
for i, item in enumerate(menu_items):
    with cols[i]:
        st.button(
            item, key=f"button_{i}", use_container_width=True,
            type="primary" if st.session_state.menu == item else "secondary",
            on_click=set_menu, args=(item,)
        )

# --- 메인 화면 로직 ---

# 1. '나의 큰틀전략' 메뉴
if st.session_state.menu == "✍️ 나의 큰틀전략":
    with st.form("my_strategy_form"):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="input-label">이름 (또는 이니셜)</p>', unsafe_allow_html=True)
        st.text_input("user_name_input", key="user_name", placeholder="이름을 입력하세요", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="input-label">나의 큰틀전략은?</p>', unsafe_allow_html=True)
        st.text_area("user_strategy_input", key="user_strategy", placeholder="나만의 다짐이나 전략을 적어보세요", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 폼 제출 버튼 (컨테이너 없이 직접 호출)
        submitted = st.form_submit_button("전략 저장하기")

        if submitted and st.session_state.get("user_name") and st.session_state.get("user_strategy"):
            new_data = pd.DataFrame({'이름': [st.session_state.user_name], '큰틀전략': [st.session_state.user_strategy]})
            st.session_state.my_strategies = pd.concat([st.session_state.my_strategies, new_data], ignore_index=True)
            st.success("새로운 큰틀전략이 저장되었습니다!")

    if not st.session_state.my_strategies.empty:
        st.markdown('<div class="list-container">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# 2. 'AI 전략 코치' 메뉴
elif st.session_state.menu == "🤖 AI 전략 코치":
    if not api_key_configured:
        st.error("AI 코치 기능을 사용하기 위한 API 키가 설정되지 않았습니다.")
    else:
        # --- AI 코치 입력 섹션 ---
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div><p class="input-label light">AI에게 상황을 말하고 코칭을 받아보세요</p><p class="input-label"><strong>어떤 상황인가요?</strong></p></div>', unsafe_allow_html=True)
        user_prompt = st.text_area("ai_prompt_input", height=100, placeholder="예: 너무 긴장돼요, 자신감이 떨어졌어요", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 추천받기 버튼 ---
        st.markdown('<div class="ai-button-container">', unsafe_allow_html=True)
        if st.button("AI에게 추천받기"): 
            if user_prompt:
                with st.spinner('AI 코치가 당신만을 위한 전략을 구상 중입니다...'):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"""
                        You are a world-class performance psychologist who creates 'Big-Picture Strategies' (큰틀전략) for athletes. An athlete is facing this situation: '{user_prompt}'.
                        Generate THREE completely different 'Big-Picture Strategies' for them in KOREAN. Each strategy must come from a unique psychological angle.
                        For each strategy, provide: - **[전략]**: The core strategy phrase. - **[해설]**: A detailed and helpful explanation of about 3-4 sentences. Explain the psychological principle behind the strategy and how the athlete can apply it in their situation.
                        Format the output exactly like this, separating each with '---':
                        [전략]: (Strategy in Korean)
                        [해설]: (Detailed explanation in Korean)
                        ---
                        (Repeat for all three strategies)
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
        st.markdown('<div class="list-container">', unsafe_allow_html=True)
        st.markdown('<div class="list-header"><p class="label">큰틀전략</p><p class="title">AI 코치의 큰틀전략</p></div>', unsafe_allow_html=True)
        for item in st.session_state.ai_strategies:
            st.markdown('<div class="strategy-item">', unsafe_allow_html=True)
            st.markdown(f"##### 💡 {item['strategy']}")
            st.caption(item['explanation'])
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# 3. '명예의 전당' 메뉴
elif st.session_state.menu == "🏆 명예의 전당":
    athletes_data = [
        {'선수': '김연아', '종목': '피겨 스케이팅', '전략': '무슨 일이 있더라도, 내가 할 수 있는 것에만 집중하고 최선을 다할 뿐이다.'},
        {'선수': '마이클 조던', '종목': '농구', '전략': '한계에 부딪히더라도, 그건 환상일 뿐이다.'},
        {'선수': '박지성', '종목': '축구', '전략': '쓰러질지언정 무릎은 꿇지 않는다.'},
        {'선수': '손흥민', '종목': '축구', '전략': '어제의 기쁨은 어제로 끝내고, 새로운 날을 준비한다.'},
        {'선수': '이상혁 \'페이커\'', '종목': 'e스포츠', '전략': '방심하지 않고, 이기든 지든 내 플레이를 하자.'},
        {'선수': '박태환', '종목': '수영', '전략': '심장이 터질 것 같아도, 포기하지 않으면 내일이 온다.'},
        {'선수': '장미란', '종목': '역도', '전략': '들 수 없는 바벨은 없다. 내가 들지 못했을 뿐이다.'},
        {'선수': '류현진', '종목': '야구', '전략': '마운드 위에서는 내가 최고라는 생각으로 던진다.'},
        {'선수': '김자인', '종목': '클라이밍', '전략': '가장 높은 곳을 향한 두려움은, 오직 내 안의 작은 속삭임일 뿐이다.'},
        {'선수': '리오넬 메시', '종목': '축구', '전략': '오늘의 노력이 내일의 나를 만든다.'},
        {'선수': '타이거 우즈', '종목': '골프', '전략': '아무리 힘들어도, 나는 항상 이길 수 있다고 믿는다.'},
        {'선수': '우사인 볼트', '종목': '육상', '전략': '나는 한계를 생각하지 않는다. 그저 달릴 뿐이다.'},
        {'선수': '세레나 윌리엄스', '종목': '테니스', '전략': '나는 다른 사람의 의견으로 나를 정의하지 않는다.'},
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
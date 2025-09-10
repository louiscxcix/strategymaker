import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="큰틀전략 메이커",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Streamlit Secrets에서 API 키 가져오기 ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    api_key_configured = True
except (KeyError, AttributeError):
    api_key_configured = False


# --- 데이터 저장을 위한 세션 상태 초기화 ---
if 'my_strategies' not in st.session_state:
    st.session_state.my_strategies = pd.DataFrame(columns=['이름', '큰틀전략'])
if 'ai_strategies' not in st.session_state:
    st.session_state.ai_strategies = []

# --- 사이드바 UI 구성 ---
with st.sidebar:
    st.title("멘탈 관리 파트너")
    if api_key_configured:
        st.success("AI 코치 기능이 활성화되었습니다!")
    else:
        st.warning("AI 코치 기능이 비활성화 상태입니다.")
        st.info("앱 배포 후, Streamlit Cloud의 Secrets에 Gemini API 키를 추가해야 AI 기능이 작동합니다.")

    st.markdown("---")
    
    menu = st.radio(
        "메뉴를 선택하세요",
        ("✍️ 나의 큰틀전략", "🤖 AI 전략 코치", "🏆 명예의 전당"),
        captions=("직접 만드는 나만의 다짐", "AI에게 영감을 얻어요", "레전드에게 배워요")
    )

# --- 메인 화면 로직 ---

# 1. '나의 큰틀전략' 메뉴 선택 시
if menu == "✍️ 나의 큰틀전략":
    st.header("✍️ 나의 큰틀전략 만들기")
    st.markdown("중요한 순간을 앞두고, **시합 전체를 관통할 핵심 정신 자세**를 적어보세요.")

    with st.form("my_strategy_form"):
        user_name = st.text_input("이름 (또는 이니셜)")
        user_strategy = st.text_area("나의 큰틀전략은...")
        submitted = st.form_submit_button("전략 저장하기")

        if submitted and user_name and user_strategy:
            new_data = pd.DataFrame({'이름': [user_name], '큰틀전략': [user_strategy]})
            st.session_state.my_strategies = pd.concat([st.session_state.my_strategies, new_data], ignore_index=True)
            st.success("새로운 큰틀전략이 저장되었습니다!")

    st.markdown("---")
    st.subheader("나의 큰틀전략 목록")

    if not st.session_state.my_strategies.empty:
        # 최신순으로 보여주기 위해 역순으로 반복
        for index, row in reversed(list(st.session_state.my_strategies.iterrows())):
            with st.container(border=True):
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.caption(f"작성자: {row['이름']}")
                    st.write(f"**{row['큰틀전략']}**")
                with col2:
                    # 각 항목별로 고유한 키를 가진 삭제 버튼 생성
                    if st.button("삭제", key=f"delete_{index}", use_container_width=True):
                        # 데이터프레임에서 해당 인덱스의 행을 삭제
                        st.session_state.my_strategies = st.session_state.my_strategies.drop(index)
                        st.rerun() # 화면을 새로고침하여 목록을 즉시 업데이트

    else:
        st.info("아직 저장된 전략이 없습니다. 첫 번째 큰틀전략을 만들어보세요!")


# 2. 'AI 전략 코치' 메뉴 선택 시
elif menu == "🤖 AI 전략 코치":
    st.header("🤖 AI 전략 코치")
    st.markdown("AI에게 당신의 상황을 이야기하고 **멘탈 코칭**을 받아보세요.")

    if not api_key_configured:
        st.error("AI 코치 기능을 사용하기 위한 API 키가 설정되지 않았습니다. 앱 관리자에게 문의하세요.")
    else:
        user_prompt = st.text_area("어떤 상황인가요? (예: 너무 긴장돼요, 자신감이 떨어졌어요)")
        
        if st.button("AI에게 추천받기"):
            if user_prompt:
                with st.spinner('AI 코치가 당신만을 위한 전략을 구상 중입니다...'):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"""
                        You are a world-class performance psychologist who mentors Olympic athletes. Your specialty is creating a 'Big-Picture Strategy' (큰틀전략), which is a core mental framework to maintain throughout a competition.

                        A 'Big-Picture Strategy' should be:
                        1.  **Concise and Powerful**: A short phrase that's easy to remember under pressure.
                        2.  **Action-Oriented**: Focuses on controllable actions or attitudes.
                        3.  **Positive**: Frames the situation constructively.

                        An athlete is currently facing the following situation (in Korean): '{user_prompt}'.

                        Based on their situation, create three distinct and detailed 'Big-Picture Strategies' for them in KOREAN.
                        For each strategy, provide:
                        -   **[전략]**: The core strategy phrase itself.
                        -   **[해설]**: A brief, one-sentence explanation of why this mindset is effective.

                        Format the output exactly like this for each of the three suggestions, with no extra text:
                        [전략]: (The strategy phrase in Korean)
                        [해설]: (The explanation in Korean)
                        ---
                        (Repeat for the next two strategies)
                        """
                        response = model.generate_content(prompt)
                        
                        st.session_state.ai_strategies = []
                        response_text = response.text
                        strategies_raw = response_text.split('---')
                        for block in strategies_raw:
                            if '[전략]:' in block and '[해설]:' in block:
                                try:
                                    strategy = block.split('[전략]:')[1].split('[해설]:')[0].strip()
                                    explanation = block.split('[해설]:')[1].strip()
                                    st.session_state.ai_strategies.append({'strategy': strategy, 'explanation': explanation})
                                except IndexError:
                                    continue

                    except Exception as e:
                        st.error(f"AI 호출 중 오류가 발생했습니다: {e}")
            else:
                st.warning("현재 상황을 입력해주세요.")

    if st.session_state.ai_strategies:
        st.subheader("AI 코치의 추천 큰틀전략")
        for i, item in enumerate(st.session_state.ai_strategies):
            with st.container(border=True):
                st.markdown(f"#### 💡 {item['strategy']}")
                st.caption(f"{item['explanation']}")

# 3. '명예의 전당' 메뉴 선택 시
elif menu == "🏆 명예의 전당":
    st.header("🏆 명예의 전당")
    st.markdown("레전드들은 어떤 마음으로 경기에 임했을까요?")

    athletes_data = [
        {'선수': '김연아', '종목': '피겨 스케이팅', '전략': '무슨 일이 있더라도, 내가 할 수 있는 것에만 집중하고 최선을 다할 뿐이다.'},
        {'선수': '마이클 조던', '종목': '농구', '전략': '한계에 부딪히더라도, 그건 환상일 뿐이다.'},
        {'선수': '박지성', '종목': '축구', '전략': '쓰러질지언정 무릎은 꿇지 않는다.'},
        {'선수': '손흥민', '종목': '축구', '전략': '어제의 기쁨은 어제로 끝내고, 새로운 날을 준비한다.'},
        {'선수': '이상혁 \'페이커\'', '종목': 'e스포츠', '전략': '방심하지 않고, 이기든 지든 내 플레이를 하자.'},
        {'선수': '세레나 윌리엄스', '종목': '테니스', '전략': '나는 내가 이길 것이라고 생각하지 않는 모든 경기를 져야 한다고 생각한다.'},
        {'선수': '무하마드 알리', '종목': '복싱', '전략': '지금은 고통이지만 남은 평생을 챔피언으로 살게 될 것이다.'},
        {'선수': '웨인 그레츠키', '종목': '아이스하키', '전략': '쏘지 않은 슛은 100% 빗나간다.'},
    ]
    df_athletes = pd.DataFrame(athletes_data)

    sports = ['모두 보기'] + sorted(df_athletes['종목'].unique())
    selected_sport = st.selectbox('종목별로 보기', sports)

    if selected_sport == '모두 보기':
        filtered_df = df_athletes
    else:
        filtered_df = df_athletes[df_athletes['종목'] == selected_sport]

    for index, row in filtered_df.iterrows():
        st.info(f"**{row['선수']}** ({row['종목']})")
        st.write(f"*{row['전략']}*")
        st.markdown("---")

import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💖", layout="centered")
st.title("💖 달콤살벌 연애상담소")
st.caption("연애 고민, 썸, 이별 이야기까지 무엇이든 들어드릴게요!")

# Streamlit Secrets에서 API 키 가져오기 및 설정
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API 키가 설정되지 않았습니다. Streamlit Secrets에 'GEMINI_API_KEY'를 등록해주세요.")
        st.stop()
except Exception as e:
    st.error(f"설정 불러오기 오류: {e}")
    st.stop()

# 세션 상태(Session State)로 채팅 기록 유지 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 당신의 연애 고민을 들어줄 AI 상담사입니다. 어떤 고민이 있으신가요? (비밀은 철저히 보장돼요!)"
        }
    ]

# 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력 받기
if user_input := st.chat_input("고민을 입력하세요..."):
    # 1. 사용자 메시지를 화면에 표시 및 기록 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. 챗봇 답변 생성 및 오류 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 모델 설정 (gemini-2.5-flash-lite)
            # 페르소나 부여를 위한 system_instruction 포함
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                system_instruction=(
                    "당신은 공감 능력이 뛰어나고 다정한 연애 상담 전문가입니다. "
                    "사용자의 연애 고민(썸, 이별, 짝사랑 등)을 진지하게 듣고, "
                    "친구처럼 친근하면서도 객관적인 조언을 제공해야 합니다. "
                    "이모티콘을 적절히 사용하여 따뜻한 분위기를 만들어주세요."
                )
            )

            # 대화 맥락 유지를 위해 이전 기록을 Gemini 형식에 맞게 변환
            # (Gemini API는 주로 'user'와 'model' 역할을 사용합니다)
            chat_history = []
            for msg in st.session_state.messages[:-1]:  # 방금 입력한 것 제외한 이전 기록들
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})

            # 채팅 세션 시작 및 답변 생성
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(user_input)
            
            # 답변 출력
            ai_response = response.text
            message_placeholder.write(ai_response)
            
            # 3. AI 답변을 기록에 저장
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

        except genai.types.generation_types.BlockedPromptException:
            message_placeholder.error("🚫 안전 정책에 위배되거나 부적절한 단어가 포함되어 답변을 생성할 수 없습니다.")
        except Exception as e:
            message_placeholder.error(f"⚠️ 오류가 발생했습니다: {e}\n잠시 후 다시 시도해주세요.")

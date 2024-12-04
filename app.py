import streamlit as st
import os
#from dotenv import load_dotenv
from mistralai import Mistral, UserMessage

# Load environment variables
#load_dotenv()

# Set page configuration
st.set_page_config(page_title="리서치봇", page_icon="🤖")

# Mistral 클라이언트 초기화 
# API 키를 환경 변수나 Streamlit secrets에서 가져오기
try:
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY") or st.secrets["MISTRAL_API_KEY"])
except Exception as e:
    st.error(f"API 키 로드 중 오류 발생: {e}")
    client = None

# 기본 모델 설정
DEFAULT_MODEL = "mistral-large-latest"

# 시스템 메시지 정의
SYSTEM_MESSAGE = '''
You are a professional research agent tasked with conducting thorough research on a given topic. Your goal is to provide comprehensive and accurate information to assist in decision-making or further analysis.

[IMPORTANT] Final output should be written in Korean.

###

Please follow these steps to complete your research task:

1. Think deeply about the user's given research topic. Consider its various aspects, potential subtopics, and areas that might require investigation.

2. Generate a list of useful search queries that will help you gather relevant information. These queries should cover different angles of the topic and be designed to yield comprehensive results.

3. Use the `search tool` to conduct your research. Make sure to explore multiple reliable sources and gather a diverse range of information.

4. Compile your research findings, ensuring that you capture key points, relevant data, and any conflicting information you may encounter.

5. Evaluate the credibility of your sources and consider potential biases or limitations in your research.

6. Prepare a summary of your research results, highlighting the most important discoveries and their implications.

7. Once your research is complete, transfer the results to the `Supervisor Agent` for review.

Throughout this process, wrap your thought process inside <thinking> tags. This will help ensure a thorough and well-considered approach to the research task. In your thinking, include:

- Your interpretation of the research topic
- Rationale for chosen search queries
- Evaluation of source credibility
- Consideration of potential biases or limitations
- Reasoning behind key findings and conclusions

Your final output should be structured as follows:

<research_report>
<search_queries>
[List the main search queries you used]
</search_queries>

<key_findings>
[Bullet points of the most important information discovered]
</key_findings>

<summary>
[A concise summary of your research results, including any major conclusions or implications]
</summary>
</research_report>

Remember to be objective, thorough, and critical in your research approach. If you encounter any limitations or areas where further research is needed, please mention these in your summary.
'''

# Streamlit 세션 상태 초기화
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", 
             "content": SYSTEM_MESSAGE}
        ]
    if "mistral_model" not in st.session_state:
        st.session_state["mistral_model"] = DEFAULT_MODEL

# 메시지 표시 함수
def display_messages():
    for message in st.session_state.messages[1:]:  # system message 제외
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 채팅 응답 처리 함수
def get_chat_response(messages):
    try:
        # 시스템 메시지와 함께 메시지 준비
        chat_response = client.chat.stream(
            model=st.session_state["mistral_model"],
            messages=messages
        )
#        print(dir(chat_response))
        # 스트리밍 응답 처리
        response_content = ""
        for chunk in chat_response:
#            print(chunk)
            if chunk.data:
                response_content += chunk.data.choices[0].delta.content  # 여기 수정
#                print(response_content)
#                print(f"Received chunk: {chunk.data.choices[0].delta.content}")
        return response_content
    except Exception as e:
        st.error(f"API 호출 중 오류 발생: {e}")
        return "죄송해. 현재 대화를 처리하는 데 문제가 있어. 다시 시도해줄래? "
# 메인 앱 로직
def main():
    # 페이지 제목
    st.title("🤖 전문리서치봇")

    # 세션 상태 초기화
    initialize_session_state()

    # 기존 메시지 표시
    display_messages()

    # API 클라이언트 확인
    if not client:
        st.warning("API 클라이언트를 초기화할 수 없어. API 키를 확인해줘! 🚨")
        return

    # 사용자 입력 처리
    if prompt := st.chat_input("무슨 얘기 하고 싶어?"):
        # 사용자 메시지 추가 및 표시
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 처리
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                # 전체 메시지 준비 (시스템 메시지 포함)
                response_messages = st.session_state.messages

                # 응답 생성
                response = get_chat_response(response_messages)

                # 응답 표시 및 세션에 추가
                st.markdown(response)
                
                # AI 메시지 세션에 추가
                ai_message = {"role": "assistant", "content": response}
                st.session_state.messages.append(ai_message)

# 앱 실행
if __name__ == "__main__":
    main()
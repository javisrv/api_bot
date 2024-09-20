import streamlit as st
from functions import write_stream, get_response

st.title("Pi Consulting challenge")


if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant",
                                      "content": """¡Hola! Soy tu asistente conversacional para el challenge de Pi Consulting 😊.\n
Estoy para ayudarte a responder cualquier duda que tengas.\n
¡Preguntame todo lo que necesites!\n
"""})

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Di algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            query_param = st.query_params
            response = get_response(prompt, st.session_state.conversation_id)
            stream = write_stream(str(response["respuesta"]))
            st.session_state.conversation_id = response["session_id"]
        except Exception as e:
            stream = write_stream(f"NSe ha producido un error: {e}")
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

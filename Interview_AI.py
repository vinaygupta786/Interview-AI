from langchain.prompts import (ChatPromptTemplate, AIMessagePromptTemplate, HumanMessagePromptTemplate)
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv(dotenv_path=r"you/path/for/API key")

apikey = os.getenv("MY_API_KEY")

def answer_question_about(topic, difficulty):
    
    final_txt = ""

    if 'started' not in st.session_state:
        st.session_state['started'] = False
        st.session_state['questions'] = []
        st.session_state['question_index'] = 0
        st.session_state['question_answers'] = {}

    if not st.session_state['started']:
        template = (
            "You are an interview question generator for this topic:\n {topic} and you have to generate 10 interview questions based on the provided topic. "
            "The questions will be for {difficulty} level."
        )
        human_msg = HumanMessagePromptTemplate.from_template(template)
        chat_prompt = ChatPromptTemplate.from_messages([human_msg])
        model = ChatOpenAI(api_key=apikey, temperature=1)

        result = model.invoke(chat_prompt.format_prompt(topic=topic, difficulty=difficulty)).content
        st.session_state['questions'] = result.split("\n")
        st.session_state['started'] = True

    question_index = st.session_state['question_index']
    questions = st.session_state['questions']
    
    if question_index < len(questions):
        st.title("Question {}/10".format(question_index + 1))
        st.header(f"{questions[question_index]}")
        
        answer = st.text_area(
            f"Your answer for Question {question_index + 1}", 
            key=f"answer_{question_index}",
            value=st.session_state['question_answers'].get(questions[question_index], "")
        )
        
        if answer:
            st.session_state['question_answers'][questions[question_index]] = answer
        if st.button("Next Question"):
            st.session_state['question_index'] += 1
            st.rerun()
    
    if question_index >= len(questions):
        st.header("Thank you for completing the questions!")
        st.write("Your answers:")
        for q, a in st.session_state['question_answers'].items():
            st.write(f"**{q}**")
            st.write(a)
        
       
        if st.button("Start Over"):
            st.session_state.clear()
            st.rerun()
        
        st.header("To enhance your given responses with AI, kindly click the 'Improve' button below and your given response will be updated by AI along with your given response.")
        
        if st.button("Improve"):
            for ques, ans in st.session_state['question_answers'].items():
                enhance_temp = (
                "You are an helpfull AI where you have to provide an enhanced response based"
                "on this interview question :\n {ques} and the given question's answer answered by the user is :{ans}"
                "If the given user answer is wrong tell them and provide the correct answer which can really help them to clear the interviews."
                "Also mention the key potins which will make interviewer happy."
                
            )
                human_msg_new = HumanMessagePromptTemplate.from_template(enhance_temp)
                chat_prompt_new = ChatPromptTemplate.from_messages([human_msg_new])
                model_new = ChatOpenAI(api_key=apikey, temperature=1)

                result_new = model_new.invoke(chat_prompt_new.format_prompt(ques=ques, ans=ans)).content
                
                final_txt += f"***{ques}*** \n\n your response is :\n\n {ans} and \n\n AI generated response is:\n\n {result_new}\n\n"
            st.download_button("Download", final_txt)


if 'topic' not in st.session_state:
    st.session_state['topic'] = ""
if 'difficulty' not in st.session_state:
    st.session_state['difficulty'] = "Intermediate"


if not st.session_state.get('started', False):
    topic = st.text_input("Enter topic:", key="topic_input", value=st.session_state['topic'])
    
    difficulty = st.radio("Select difficulty level:", options=["Beginner", "Intermediate", "Advanced"], 
                          index=["Beginner", "Intermediate", "Advanced"].index(st.session_state['difficulty']))

    if st.button("Start Interview"):
        if topic.strip():  
            st.session_state['topic'] = topic
            st.session_state['difficulty'] = difficulty
            answer_question_about(topic, difficulty)
        else:
            st.error("Please enter a topic")
else:
    answer_question_about(st.session_state['topic'], st.session_state['difficulty'])


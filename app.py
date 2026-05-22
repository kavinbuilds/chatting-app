import streamlit as st
from datetime import datetime
import sqlite3

# Connect to the SQLite database
conn=sqlite3.connect('chat.db')
c=conn.cursor()
#create the table that sores the user , message and tiime of message
c.execute('''CREATE TABLE IF NOT EXISTS CHAT(ID INTEGER PRIMARY KEY AUTOINCREMENT,USERNAME TEXT,MESSAGE TEXT,TIME TEXT)''')
conn.commit()
st.set_page_config(page_title="boss chat 🗣️", page_icon=":speech_balloon:", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>Welcome to Boss Chat 🗣️</h1>", unsafe_allow_html=True)
# Auto-refresh every 5 seconds to update the chat messages
# Get the username from the user
user=st.selectbox("select the username",["kavin😎","mano boss😎","dinesh bhai😎"])
messages=c.execute("select username,message,time from chat order by id desc").fetchall()
for username,message,time in messages:
    if username==user:
        if username == user:
            st.markdown(
            f"""
            <div style='text-align:right;
                        background-color:#DCF8C6;
                        padding:10px;
                        border-radius:10px;
                        margin:5px'>
                <b>{username}</b><br>
                {message}<br>
                <small>{time}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='text-align:left;
                        background-color:#E5E5EA;
                        padding:10px;
                        border-radius:10px;
                        margin:5px'>
                <b>{username}</b><br>
                {message}<br>
                <small>{time}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")
# Input for the user to send a message
message=st.text_input("Type your message here")
if st.button("send", key="send",type="primary",use_container_width=True,width="stretch"):
    if message.strip()!="":
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("insert into chat(username,message,time) values(?,?,?)", (user, message, time))
        conn.commit()
        st.rerun()

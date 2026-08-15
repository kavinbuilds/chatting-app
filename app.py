import streamlit as st
from datetime import datetime
import sqlite3
import os

# Connect to the SQLite database
os.makedirs("uploads",exist_ok=True)
conn=sqlite3.connect('chat.db')
c=conn.cursor()
#create the table that sores the user , message and tiime of message

# Create new table
c.execute("""
    CREATE TABLE IF NOT EXISTS CHAT(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        USERNAME TEXT,
        MESSAGE TEXT,
        AUDIO TEXT,
        IMAGE TEXT,
        TIME TEXT
    )
""")

conn.commit()
st.set_page_config(page_title="boss chat 🗣️", page_icon=":speech_balloon:", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>Welcome to Boss Chat 🗣️</h1>", unsafe_allow_html=True)
# Auto-refresh every 5 seconds to update the chat messages
# Get the username from the user
user=st.selectbox("select the username",["kavin😎","mano boss😎","dinesh bhai😎"])
messages=c.execute("select username,message,audio,image,time from chat order by id desc").fetchall()
chat_box = st.container(height=500, border=True)

with chat_box:

    for username, message, audio, image, time in messages:

        if username == user:
            alignment = "right"
            background = "#DCF8C6"
        else:
            alignment = "left"
            background = "#E5E5EA"

        # Text message
        if message:
            st.markdown(
                f"""
                <div style="
                    text-align:{alignment};
                    background-color:{background};
                    padding:10px;
                    border-radius:10px;
                    margin:5px;
                ">
                    <b>{username}</b><br>
                    {message}<br>
                    <small>{time}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Audio message
        if audio:
            st.audio(audio)

        # Image message
        if image:
            st.image(image, width=250)
# Input for the user to send a message
message=st.text_input("Type your message here")
audio=st.audio_input("record your audio ;")
image=st.file_uploader("share your image :",type=["jpeg","jpg","png"])
if st.button("send", key="send",type="primary",use_container_width=True,width="stretch"):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename_time=datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path=None
    image_path=None
    if audio:
        audio_path=f"uploads/audio{filename_time}.wav"
        with open(audio_path,"wb") as f:
            f.write(audio.getvalue())
    if image:
        image_path=f"uploads/image{filename_time}.png"
        with open(image_path,"wb") as f:
            f.write(image.getvalue())
    if message.strip()!="" or audio or image:
        c.execute("insert into chat(username,message,audio,image,time) values(?,?,?,?,?)", (user,message,audio_path,image_path,time))
        conn.commit()
        st.rerun()
# Clear chat
if st.button("🗑️ Clear Chat", key="delete", type="secondary"):

    st.session_state.confirm_delete = True


if st.session_state.get("confirm_delete", False):

    st.warning("⚠️ This will delete all messages and uploaded files!")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, delete everything", type="primary"):

            # Delete messages from database
            c.execute("DELETE FROM chat")
            conn.commit()

            # Delete uploaded audio/images
            for filename in os.listdir("uploads"):

                filepath = os.path.join("uploads", filename)

                if os.path.isfile(filepath):
                    os.remove(filepath)

            # Hide confirmation
            st.session_state.confirm_delete = False

            # Refresh
            st.rerun()

    with col2:
        if st.button("Cancel"):

            st.session_state.confirm_delete = False
            st.rerun()
        

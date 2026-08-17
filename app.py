import streamlit as st
from datetime import datetime
import sqlite3
import os
from streamlit_extras.stateful_chat import chat, add_message

# Create uploads folder
os.makedirs("uploads", exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect("chat.db")
c = conn.cursor()

# Create table
c.execute("""
CREATE TABLE IF NOT EXISTS CHAT (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USERNAME TEXT,
    MESSAGE TEXT,
    AUDIO TEXT,
    IMAGE TEXT,
    TIME TEXT
)
""")

conn.commit()

st.set_page_config(
    page_title="boss chat 🗣️",
    page_icon=":speech_balloon:",
    layout="centered"
)

# Get username
user = st.selectbox(
    "Select the username",
    ["kavin😎", "mano boss😎", "dinesh bhai😎"]
)

# Get messages
messages = c.execute(
    "SELECT username, message, audio, image, time FROM chat ORDER BY id DESC"
).fetchall()
user_colors = {
    "kavin😎": "#DCF8C6",
    "mano boss😎": "#D6E4FF",
    "dinesh bhai😎": "#FFD6E7"
}

for username, message, audio, image, time in messages:

        background = user_colors.get(username, "#E5E5EA")

        # Right side for current user
        if username == user:
            alignment = "right"
        else:
            alignment = "left"

        with st.container(border=True):

            # Username and time
            st.markdown(
                f"""
                <div style="
                    background-color:{background};
                    padding:10px;
                    border-radius:10px;
                ">
                    <b>{username}</b>
                    <small style="margin-left:10px;">
                        {time}
                    </small>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Text
            if message:
                st.markdown(
                    f"""
                    <div style="
                        text-align:{alignment};
                        padding:5px;
                    ">
                        {message}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Audio
            if audio:
                st.audio(audio)

            # Image
            if image:
                st.image(image, width=250)


# Chat input
message = st.chat_input("Type your message...")

# Audio input
audio = st.audio_input("Record your audio:")

# Image uploader
image = st.file_uploader(
    "Share your image:",
    type=["jpeg", "jpg", "png"]
)


# Send button
if st.button(
    "Send",
    key="send",
    type="primary",
    use_container_width=True
):

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    audio_path = None
    image_path = None

    # Save audio
    if audio:
        audio_path = f"uploads/audio_{filename_time}.wav"

        with open(audio_path, "wb") as f:
            f.write(audio.getvalue())

    # Save image
    if image:
        image_path = f"uploads/image_{filename_time}.png"

        with open(image_path, "wb") as f:
            f.write(image.getvalue())

    # Insert message
    if (message and message.strip() != "") or audio or image:

        c.execute(
            """
            INSERT INTO chat(username, message, audio, image, time)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user,
                message or "",
                audio_path,
                image_path,
                time
            )
        )

        conn.commit()
        st.rerun()


# Clear chat
if st.button(
    "🗑️ Clear Chat",
    key="delete",
    type="secondary"
):

    st.session_state.confirm_delete = True


# Delete confirmation
if st.session_state.get("confirm_delete", False):

    st.warning(
        "⚠️ This will delete all messages and uploaded files!"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Yes, delete everything",
            type="primary"
        ):

            # Delete messages
            c.execute("DELETE FROM chat")
            conn.commit()

            # Delete uploaded files
            for filename in os.listdir("uploads"):

                filepath = os.path.join(
                    "uploads",
                    filename
                )

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
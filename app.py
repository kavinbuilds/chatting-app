import streamlit as st
from datetime import datetime
import sqlite3
import os
import html


# --------------------------------------------------
# FOLDERS
# --------------------------------------------------

os.makedirs("uploads", exist_ok=True)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

conn = sqlite3.connect("chat.db", check_same_thread=False)
c = conn.cursor()

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


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="boss chat 🗣️",
    page_icon="💬",
    layout="centered"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("💬 Boss Chat 🗣️")


# --------------------------------------------------
# USERNAME
# --------------------------------------------------

user = st.selectbox(
    "Select the username",
    [
        "kavin😎",
        "mano boss😎",
        "dinesh bhai😎"
    ]
)


# --------------------------------------------------
# USER COLORS
# --------------------------------------------------

user_colors = {
    "kavin😎": "#DCF8C6",
    "mano boss😎": "#D6E4FF",
    "dinesh bhai😎": "#FFD6E7"
}


# --------------------------------------------------
# GET MESSAGES
# --------------------------------------------------

messages = c.execute(
    """
    SELECT username, message, audio, image, time
    FROM CHAT
    ORDER BY ID ASC
    """
).fetchall()


# --------------------------------------------------
# CHAT DISPLAY
# --------------------------------------------------

chats = st.container(
    height=400,
    border=True
)

with chats:

    if not messages:
        st.info("No messages yet. Start chatting! 💬")

    for username, message, audio, image, time in messages:

        # Get background color
        background = user_colors.get(
            username,
            "#E5E5EA"
        )

        # Current user's messages on right
        if username == user:
            alignment = "right"
        else:
            alignment = "left"

        # Message container
        with st.container(border=True):

            # Escape username and time
            safe_username = html.escape(username)
            safe_time = html.escape(time)

            # Username + time
            st.markdown(
                f"""
                <div style="
                    background-color: {background};
                    padding: 10px;
                    border-radius: 10px;
                    margin-bottom: 5px;
                ">
                    <b>{safe_username}</b>
                    <small style="
                        margin-left: 10px;
                        color: #555;
                    ">
                        {safe_time}
                    </small>
                </div>
                """,
                unsafe_allow_html=True
            )

            # --------------------------------------------------
            # TEXT MESSAGE
            # --------------------------------------------------

            if message and message.strip():

                safe_message = html.escape(message)

                st.markdown(
                    f"""
                    <div style="
                        text-align: {alignment};
                        padding: 10px;
                        word-wrap: break-word;
                    ">
                        {safe_message}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # --------------------------------------------------
            # AUDIO
            # --------------------------------------------------

            if audio:

                if os.path.exists(audio):
                    st.audio(audio)
                else:
                    st.warning("Audio file not found.")


            # --------------------------------------------------
            # IMAGE
            # --------------------------------------------------

            if image:

                if os.path.exists(image):
                    st.image(
                        image,
                        width=250
                    )
                else:
                    st.warning("Image file not found.")


# --------------------------------------------------
# SPACE
# --------------------------------------------------

st.write("")


# --------------------------------------------------
# TEXT INPUT
# --------------------------------------------------

message = st.chat_input(
    "Type your message..."
)


# --------------------------------------------------
# AUDIO INPUT
# --------------------------------------------------

audio = st.audio_input(
    "🎤 Record your audio:"
)


# --------------------------------------------------
# IMAGE UPLOADER
# --------------------------------------------------

image = st.file_uploader(
    "🖼️ Share your image:",
    type=[
        "jpeg",
        "jpg",
        "png"
    ]
)


# --------------------------------------------------
# SEND BUTTON
# --------------------------------------------------

if st.button(
    "📤 Send",
    key="send",
    type="primary",
    use_container_width=True
):

    # Check if anything was entered
    if (
        (message and message.strip())
        or audio
        or image
    ):

        # Current time
        now = datetime.now()

        time = now.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Unique filename
        filename_time = now.strftime(
            "%Y%m%d_%H%M%S_%f"
        )


        # --------------------------------------------------
        # AUDIO FILE
        # --------------------------------------------------

        audio_path = None

        if audio:

            audio_path = os.path.join(
                "uploads",
                f"audio_{filename_time}.wav"
            )

            with open(
                audio_path,
                "wb"
            ) as f:

                f.write(
                    audio.getvalue()
                )


        # --------------------------------------------------
        # IMAGE FILE
        # --------------------------------------------------

        image_path = None

        if image:

            # Keep everything as PNG
            image_path = os.path.join(
                "uploads",
                f"image_{filename_time}.png"
            )

            with open(
                image_path,
                "wb"
            ) as f:

                f.write(
                    image.getvalue()
                )


        # --------------------------------------------------
        # SAVE TO DATABASE
        # --------------------------------------------------

        c.execute(
            """
            INSERT INTO CHAT
            (
                USERNAME,
                MESSAGE,
                AUDIO,
                IMAGE,
                TIME
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user,
                message.strip()
                if message
                else "",
                audio_path,
                image_path,
                time
            )
        )

        conn.commit()

        # Refresh page
        st.rerun()

    else:

        st.warning(
            "Please type a message, record audio, or select an image."
        )


# --------------------------------------------------
# CLEAR CHAT BUTTON
# --------------------------------------------------

st.write("")

if st.button(
    "🗑️ Clear Chat",
    key="delete",
    type="secondary",
    use_container_width=True
):

    st.session_state.confirm_delete = True


# --------------------------------------------------
# DELETE CONFIRMATION
# --------------------------------------------------

if st.session_state.get(
    "confirm_delete",
    False
):

    st.warning(
        "⚠️ This will permanently delete all messages "
        "and uploaded files!"
    )

    col1, col2 = st.columns(2)


    # --------------------------------------------------
    # YES DELETE
    # --------------------------------------------------

    with col1:

        if st.button(
            "✅ Yes, delete everything",
            type="primary",
            use_container_width=True
        ):

            # Delete database messages
            c.execute(
                "DELETE FROM CHAT"
            )

            conn.commit()


            # Delete uploaded files
            for filename in os.listdir(
                "uploads"
            ):

                filepath = os.path.join(
                    "uploads",
                    filename
                )

                if os.path.isfile(
                    filepath
                ):

                    try:
                        os.remove(filepath)

                    except Exception as e:
                        st.warning(
                            f"Could not delete {filename}: {e}"
                        )


            # Reset confirmation
            st.session_state.confirm_delete = False

            # Refresh
            st.rerun()


    # --------------------------------------------------
    # CANCEL
    # --------------------------------------------------

    with col2:

        if st.button(
            "❌ Cancel",
            use_container_width=True
        ):

            st.session_state.confirm_delete = False

            st.rerun()
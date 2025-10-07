import openai
import io
import tempfile
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import wave
import numpy as np
import os
from openai import OpenAI
import re

# ========================== CONFIGURATION ==========================
st.set_page_config(
    page_title="Voice Assistant - Income Tax Bot",
    page_icon="🎙",
    layout="centered"
)

# ========================== STYLING ==========================
st.markdown("""
<style>
/* -------- GLOBAL -------- */
html, body, [class*="css"]  {
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* -------- CONTAINER -------- */
.voice-container {
    background: rgba(255, 255, 255, 0.25);
    border-radius: 20px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    padding: 25px 30px;
    margin-top: 15px;
}

/* -------- TITLE -------- */
.voice-title {
    font-family: 'Georgia', serif;
    text-align: center;
    color: #2c3e50;
    font-size: 1.8em;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 1rem;
}

/* -------- BUTTON -------- */
button[kind="primary"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1.1em !important;
    padding: 0.6em 1.4em !important;
    transition: all 0.3s ease-in-out !important;
}
button[kind="primary"]:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #4a90e2, #0077b6) !important;
    color: white !important;
}

/* -------- SUCCESS / INFO / WARNING -------- */
.stSuccess {
    background: rgba(223, 255, 223, 0.6) !important;
    border-left: 5px solid #28a745 !important;
    border-radius: 10px !important;
}
.stInfo {
    background: rgba(230, 245, 255, 0.6) !important;
    border-left: 5px solid #0077b6 !important;
    border-radius: 10px !important;
}
.stWarning {
    background: rgba(255, 249, 230, 0.6) !important;
    border-left: 5px solid #ffc107 !important;
    border-radius: 10px !important;
}

/* -------- EXPANDER -------- */
.streamlit-expanderHeader {
    font-weight: 600;
    color: #2c3e50;
    letter-spacing: 0.3px;
}
</style>
""", unsafe_allow_html=True)

# ========================== OPENAI CLIENT ==========================
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", None))

# ========================== TRANSCRIPTION ==========================
def transcribe_audio(audio_bytes_list):
    if not client.api_key:
        st.error("OpenAI API key missing. Please add it in Streamlit secrets.")
        return None

    audio_bytes = b''.join(audio_bytes_list)
    if not audio_bytes:
        return ""

    audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
    current_rate = 48000
    target_rate = 16000
    downsample_factor = current_rate // target_rate
    audio_array = audio_array[::downsample_factor]
    audio_int16 = (audio_array * 32767).astype(np.int16)

    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file_path = tmp_file.name
            with wave.open(tmp_file_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(target_rate)
                wf.writeframes(audio_int16.tobytes())

        with open(tmp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text.strip()
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return None
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

# ========================== FORM FIELD EXTRACTION ==========================
def extract_form_fields(text):
    fields = {}
    text_lower = text.lower()

    def parse_amount(match):
        if not match: return 0
        amount_str = match.group(0).lower().replace('₹', '').replace(',', '').strip()
        if 'lakh' in amount_str or 'lac' in amount_str:
            base = re.search(r"(\d+(\.\d+)?)", amount_str)
            return float(base.group(1)) * 100000 if base else 0
        if 'crore' in amount_str:
            base = re.search(r"(\d+(\.\d+)?)", amount_str)
            return float(base.group(1)) * 10000000 if base else 0
        direct_match = re.search(r"\d+\.?\d*", amount_str)
        return float(direct_match.group(0)) if direct_match else 0

    salary_match = re.search(r"(salary|income|pay).*?(\d[\d,.]*(?:\s(?:lakh|lac|crore))?)", text_lower)
    if salary_match:
        fields["basic_salary"] = int(parse_amount(salary_match))

    rent_paid_match = re.search(r"(rent paid|rent).*?(\d[\d,.]*(?:\s(?:lakh|lac|crore))?)", text_lower)
    if rent_paid_match:
        fields["rent_paid"] = int(parse_amount(rent_paid_match))

    tds_match = re.search(r"(tds|tax deducted).*?(\d[\d,.]*(?:\s(?:lakh|lac|crore))?)", text_lower)
    if tds_match:
        fields["tds_paid"] = int(parse_amount(tds_match))

    return {k: v for k, v in fields.items() if v > 0}

# ========================== PROCESS COMMAND ==========================
def process_command(command):
    if not command:
        return "Sorry, I couldn't hear that clearly. Please try again."

    command_lower = command.lower()
    if any(word in command_lower for word in ["fill", "form", "enter", "set"]):
        form_data = extract_form_fields(command)
        if form_data:
            st.session_state["fill_form_data"] = form_data
            return f"✅ Extracted: **{', '.join([f'{k}: ₹{v:,}' for k, v in form_data.items()])}**"
        else:
            return "I couldn't detect any valid values (e.g., salary or rent). Try saying: 'Set my salary to 8 lakh'."

    elif any(word in command_lower for word in ["tax", "doubt", "limit", "what is", "how much"]):
        qa_prompt = f"User has a question about Indian Income Tax for FY 2025-26: {command}"
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful Indian tax assistant for FY 2025-26. Provide short, correct answers."},
                    {"role": "user", "content": qa_prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error while fetching AI response: {e}"

    else:
        return "You can say: 'Set my salary to 8 lakh' or 'What is the 80C limit?'"

# ========================== STREAMLIT UI ==========================
def voice_assistant_ui():
    st.markdown('<div class="voice-container">', unsafe_allow_html=True)
    st.markdown('<div class="voice-title">🎙 Voice Assistant</div>', unsafe_allow_html=True)
    st.caption("Speak naturally — I’ll transcribe and process your tax questions or form inputs!")

    if 'audio_frames' not in st.session_state:
        st.session_state.audio_frames = []
    audio_frames = st.session_state.audio_frames

    class AudioProcessor:
        def recv_audio(self, frame: av.AudioFrame):
            audio_frames.append(frame.to_ndarray().tobytes())
            return frame

    webrtc_streamer(
        key="voice",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if st.button("🔊 Transcribe & Process Command", type="primary"):
        if audio_frames:
            with st.spinner("🎧 Listening and analyzing your voice..."):
                command = transcribe_audio(audio_frames)
                st.session_state.audio_frames = []
                if command:
                    st.success(f"🗣 You said: **{command}**")
                    response = process_command(command)
                    st.info(response)
                    if "fill_form_data" in st.session_state:
                        st.write("🧾 Extracted Data:", st.session_state["fill_form_data"])
                        if 'income_details' in st.session_state:
                            st.session_state.income_details.update(st.session_state["fill_form_data"])
                else:
                    st.warning("No clear voice detected. Please try again.")
        else:
            st.warning("No audio recorded. Please allow mic permission and speak clearly.")

    with st.expander("💡 How to Use"):
        st.write("""
        1. Click the **microphone icon** above to start recording.  
        2. Speak clearly, e.g.:
           - "Set my basic salary to 10 lakh"
           - "What is Section 80C limit?"
        3. Click **Transcribe & Process Command** to interpret your voice.
        4. Extracted values will auto-fill into the tax form.
        """)
    st.markdown("</div>", unsafe_allow_html=True)

# ========================== MAIN TEST ==========================
if __name__ == '__main__':
    if 'income_details' not in st.session_state:
        st.session_state.income_details = {"basic_salary": 0, "rent_paid": 0, "tds_paid": 0}
    voice_assistant_ui()
    st.json(st.session_state.get('fill_form_data', {}))

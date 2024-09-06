import streamlit as st
from streamlit_shadcn_ui import ui
from services.script_generator import generate_script
from services.audio_generator import generate_audio

st.set_page_config(page_title="Meditate for Me", page_icon="🧘", layout="wide")

def main():
    st.title("Meditate for Me")

    with st.container():
        st.header("How to Use")
        st.markdown("""
        1. Select one or more emotions that reflect your current state.
        2. Choose your meditation goals.
        3. Pick your desired outcomes from the meditation.
        4. Click the "Generate Meditation" button to create your personalized meditation.
        5. Listen to your custom meditation audio or read the script.
        """)

    emotions = ui.multi_select("Select Your Current Emotions", ["Happy", "Sad", "Anxious", "Calm", "Angry", "Excited"])
    goals = ui.multi_select("Select Your Meditation Goals", ["Relaxation", "Focus", "Better Sleep", "Stress Relief"])
    outcomes = ui.multi_select("Select Your Desired Outcomes", ["Feeling Calm", "Increased Energy", "Mental Clarity", "Emotional Balance"])

    if ui.button("Generate Meditation", disabled=not (emotions and goals and outcomes)):
        with st.spinner("Generating meditation..."):
            try:
                script = generate_script(goals, emotions, outcomes)
                audio_url = generate_audio(script)
                
                st.subheader("Your Personalized Meditation Script")
                st.write(script)
                
                st.subheader("Listen to Your Meditation")
                st.audio(audio_url)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

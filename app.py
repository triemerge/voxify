import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, ClientError
import contextlib

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Amazon Polly TTS Converter",
    page_icon="🗣️",
    layout="wide"
)

# --- Functions ---

@st.cache_resource
def get_polly_client():
    """
    Initialize the Amazon Polly client.
    Basic credential check is performed by attempting to create the client.
    Connection verification happens when fetching voices.
    """
    region_name = os.getenv("AWS_REGION", "us-east-1")
    
    try:
        client = boto3.client('polly', region_name=region_name)
        return client
    except Exception as e:
        st.error(f"Failed to initialize AWS Polly client: {e}")
        return None

@st.cache_data
def get_available_voices(_client):
    """
    Fetch available voices from Amazon Polly.
    Filters for 'neural' engine and English (US/UK) languages.
    """
    try:
        response = _client.describe_voices(
            Engine='neural',
            IncludeAdditionalLanguageCodes=False
        )
        
        voices = response.get('Voices', [])
        
        # Filter for US and UK English
        target_languages = ['en-US', 'en-GB']
        filtered_voices = [
            v for v in voices 
            if v.get('LanguageCode') in target_languages
        ]
        
        # Sort for better UX
        filtered_voices.sort(key=lambda x: (x['LanguageCode'], x['Name']))
        
        return filtered_voices
        
    except (BotoCoreError, ClientError) as error:
        st.error(f"Error fetching voices: {error}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return []

def synthesize_audio(client, text, voice_id):
    """
    Synthesize speech from text using Amazon Polly.
    Returns the audio stream as bytes.
    """
    try:
        response = client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine='neural',
            TextType='text' # Enforcing plain text per PRD
        )
        
        # Read the stream
        if 'AudioStream' in response:
            return response['AudioStream'].read()
            
    except (BotoCoreError, ClientError) as error:
        st.error(f"AWS Polly Error: {error}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    
    return None

# --- UI Layout ---

def main():
    st.title("Amazon Polly TTS Tool")
    
    # Initialize session state for audio persistence
    if 'audio_bytes' not in st.session_state:
        st.session_state['audio_bytes'] = None
    
    # Sidebar
    st.sidebar.header("Configuration")
    
    client = get_polly_client()
    
    if not client:
        st.warning("AWS Configuration missing or invalid. Please check your .env file or AWS credentials.")
        st.stop()

    # Voice Selection
    with st.spinner("Fetching available voices..."):
        voices = get_available_voices(client)
    
    if not voices:
        st.error("No voices found. Check your AWS connection and Region.")
        st.stop()
        
    voice_options = {f"{v['Name']} ({v['LanguageCode']} - {v['Gender']})": v['Id'] for v in voices}
    
    selected_voice_label = st.sidebar.selectbox(
        "Select Voice",
        options=list(voice_options.keys())
    )
    selected_voice_id = voice_options[selected_voice_label]
    
    st.sidebar.markdown("---")
    st.sidebar.info("Using **Neural** Engine\nOutput Format: **MP3**")

    # Main Area
    st.subheader("Text Input")
    text_input = st.text_area(
        "Enter text to convert (max 3000 chars):",
        height=200,
        max_chars=3000,
        help="Type or paste the text you want to convert to speech."
    )

    if st.button("Synthesize Speech", type="primary", disabled=not text_input):
        if not text_input.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Generating audio..."):
                audio_data = synthesize_audio(client, text_input, selected_voice_id)
                if audio_data:
                    st.session_state['audio_bytes'] = audio_data
                    st.success("Audio generated successfully!")
                else:
                    st.session_state['audio_bytes'] = None

    # Output Area (Persistent)
    if st.session_state['audio_bytes']:
        st.markdown("---")
        st.subheader("Playback & Download")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.audio(st.session_state['audio_bytes'], format='audio/mp3')
            
        with col2:
            st.download_button(
                label="Download MP3",
                data=st.session_state['audio_bytes'],
                file_name="polly_output.mp3",
                mime="audio/mp3"
            )

if __name__ == "__main__":
    main()

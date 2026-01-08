# Amazon Polly TTS Converter
# --------------------------
# A Streamlit application that converts text into speech using Amazon Polly's Neural engine.
# This application is Docker-ready and deployed on AWS EC2.
#
# Purpose:
# - To demonstrate how to use AWS SDK for Python (boto3) with Streamlit.
# - To create a user-friendly interface for generating high-quality voiceovers.
# - To show how to handle AWS credentials securely in a cloud environment.
#
# Author: Aditya Kumar Gupta
# Repository: https://github.com/triemerge/voxify

# Standard Library Imports
import os
import contextlib
from typing import Optional, List, Dict, Any

# Third-Party Imports
import boto3  # AWS SDK for Python, allows connection to Amazon Polly
import streamlit as st  # The framework used to building the web UI
from dotenv import load_dotenv  # For loading .env files locally (security best practice)
from botocore.exceptions import BotoCoreError, ClientError  # Specific AWS error types

# --- Configuration & Constants ---

# Load environment variables from a .env file if it exists.
# This is crucial for local development to keep keys out of the code.
# In production (Docker/AWS), these values usually come from the system environment.
load_dotenv()

# App-Wide Logic Configuration
PAGE_TITLE = "Amazon Polly TTS Converter" # Browser tab title
PAGE_ICON = "🗣️" # Browser tab icon
LAYOUT = "wide" # Use the full width of the browser

# AWS Polly Configuration
# We default to 'us-east-1' because it's the most reliable region for new features like Neural voices.
DEFAULT_REGION = "us-east-1" 

# We filter the voice list to only show US and UK English to keep the UI clean.
# Polly supports dozens of languages, but listing them all would be overwhelming for this specific tool.
TARGET_LANGUAGES = ['en-US', 'en-GB'] 

# 'neural' is the highest quality engine. 'standard' is cheaper but robotics.
# We hardcode 'neural' because the goal is high-quality output.
ENGINE = 'neural' 

# 'mp3' is the best format for general web playback. 'pcm' is for raw audio data.
OUTPUT_FORMAT = 'mp3'

# --- UI Styles & Content ---

# Custom CSS to force the footer to stay at the bottom of the screen.
# Streamlit doesn't have a native footer component, so we inject HTML/CSS.
# 'pointer-events: none' on the container allows users to click buttons BEHIND the transparent footer.
FOOTER_STYLE = """
<style>
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: transparent;
color: grey;
text-align: center;
padding: 10px;
font-size: 14px;
z-index: 1000;
pointer-events: none;
}
.footer a {
color: #ff4b4b;
text-decoration: none;
pointer-events: auto; /* Re-enable clicks on the actual links */
font-weight: bold;
}
.footer a:hover {
text-decoration: underline;
}
</style>
"""

# HTML for the "Welcome" popup modal.
# We use standard HTML inside Streamlit's markdown to get precise control over layout (centering, image borders).
WELCOME_MODAL_HTML = """
<div style="text-align: center; padding: 0px;">
<!-- Profile Picture with a border matching the theme color -->
<img src="https://github.com/triemerge.png" style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #ff4b4b; margin-bottom: 15px;">
<h2 style='margin-bottom: 5px; margin-top: 0px;'>Hi, I'm Aditya Kumar Gupta! 👋</h2>
<p style='font-size: 1.1em; color: #666; margin-bottom: 10px;'>
I built this tool to make AI Text-to-Speech simple and accessible.
</p>
<hr style="margin: 15px 0;">
<p style='margin-bottom: 15px;'>
Check out my other open-source projects or drop a star on the repo!
</p>
<!-- Custom styled button that looks cooler than standard HTML buttons -->
<a href="https://github.com/triemerge" target="_blank" style="
background-color: #333;
color: white;
padding: 12px 25px;
border-radius: 30px;
text-decoration: none;
font-weight: bold;
font-size: 1.1em;
display: inline-block;
transition: transform 0.2s;
box-shadow: 0 4px 15px rgba(0,0,0,0.2);
">
🚀 Follow on GitHub
</a>
<br><br>
</div>
"""

# --- Setup Streamlit Page ---
# This command MUST be the first Streamlit command run in the script.
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT
)

# --- Backend Logic (AWS Polly) ---

@st.cache_resource
def get_polly_client() -> Optional[Any]:
    """
    Initialize the Amazon Polly client using boto3.
    
    This function uses @st.cache_resource, meaning Streamlit loads the connection ONCE
    and reuses it for the entire session. This is much faster than connecting every time the page reloads.

    The client automatically looks for credentials in:
    1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) - This is what Docker uses.
    2. Shared credentials file (~/.aws/credentials) - This is what local development often uses.
    
    Returns:
        boto3.client: The initialized Polly client object, or None if initialization fails.
    """
    # Fallback to us-east-1 if no region is specified in the environment
    region_name = os.getenv("AWS_REGION", DEFAULT_REGION)
    
    try:
        client = boto3.client('polly', region_name=region_name)
        return client
    except Exception as e:
        # If we can't create a client (e.g., missing library), show an error on the UI
        st.error(f"Failed to initialize AWS Polly client: {e}")
        return None

@st.cache_data
def get_available_voices(_client) -> List[Dict[str, Any]]:
    """
    Fetch and filter available voices from Amazon Polly.
    
    This uses @st.cache_data because the list of AWS voices doesn't change often.
    Caching this prevents us from making a slow API call every time the user types a letter.
    
    Args:
        _client: The boto3 Polly client.
        
    Returns:
        List[Dict]: A list of dictionary objects representing the voices.
                    Example structure: [{'Id': 'Joanna', 'Name': 'Joanna', 'LanguageCode': 'en-US', ...}]
                    Returns an empty list on error.
    """
    try:
        # Request voices specifically for the 'neural' engine (higher quality)
        response = _client.describe_voices(
            Engine=ENGINE,
            IncludeAdditionalLanguageCodes=False
        )
        
        voices = response.get('Voices', [])
        
        # Filter Logic:
        # We look through the list of 50+ voices and keep only the ones
        # that match our target languages (US and UK English).
        filtered_voices = [
            v for v in voices 
            if v.get('LanguageCode') in TARGET_LANGUAGES
        ]
        
        # Sorting Logic:
        # Users expect lists to be organized. We sort first by Language (US vs UK),
        # and then alphabetically by Name (Amy, Brian, etc.).
        filtered_voices.sort(key=lambda x: (x['LanguageCode'], x['Name']))
        
        return filtered_voices
        
    except (BotoCoreError, ClientError) as error:
        # Specific AWS errors (like 'InvalidSignature' or 'NetworkError')
        st.error(f"Error fetching voices from AWS: {error}")
        return []
    except Exception as e:
        # Generic Python errors (like variable names wrong)
        st.error(f"Unexpected error while fetching voices: {e}")
        return []

def synthesize_audio(client, text: str, voice_id: str) -> Optional[bytes]:
    """
    Convert text to speech using Amazon Polly's synthesize_speech API.
    
    This is the core function of the app. It sends text to AWS cloud and gets back audio data.
    
    Args:
        client: The boto3 Polly client.
        text (str): The input text to convert.
        voice_id (str): The ID of the voice to use (e.g., 'Joanna').
        
    Returns:
        bytes: The raw audio data content, or None if failed.
    """
    try:
        response = client.synthesize_speech(
            Text=text,
            OutputFormat=OUTPUT_FORMAT, # Requesting mp3
            VoiceId=voice_id,
            Engine=ENGINE, # Forcing neural engine
            TextType='text' # We are sending plain text, not SSML code
        )
        
        # The 'AudioStream' in the response is a "StreamingBody".
        # We need to .read() it to get the actual bytes of the MP3 file.
        if 'AudioStream' in response:
            return response['AudioStream'].read()
            
    except (BotoCoreError, ClientError) as error:
        st.error(f"AWS Polly Synthesis Error: {error}")
    except Exception as e:
        st.error(f"An unexpected error occurred during synthesis: {e}")
    
    return None

# --- UI Components ---

def display_footer():
    """Renders the fixed footer at the bottom of the page using HTML injection."""
    footer_html = f"""
{FOOTER_STYLE}
<div class="footer">
Built with 💻 by <a href="https://github.com/triemerge" target="_blank">Aditya Kumar Gupta</a> | 
<a href="https://github.com/triemerge/voxify" target="_blank">Repo</a>
</div>
"""
    st.markdown(footer_html, unsafe_allow_html=True)

@st.dialog("✨ Welcome to Voxify", width="large")
def show_welcome_modal():
    """
    Displays the welcome modal with author information.
    Uses st.dialog() which creates a modal that dims the rest of the screen.
    """
    st.markdown(WELCOME_MODAL_HTML, unsafe_allow_html=True)
    
    # When the user clicks this button, we update 'session_state'.
    # st.rerun() forces the app to refresh, noticing the new state and hiding the modal.
    if st.button("Let's Get Started!", type="primary", use_container_width=True):
        st.session_state['welcome_shown'] = True
        st.rerun()

# --- Main Application Loop ---

def main():
    """Main execution function for the Streamlit app. This runs every time the user interacts."""
    
    st.title("Amazon Polly TTS Tool")
    
    # 1. Session State Initialization
    # Streamlit scripts re-run from top to bottom on every interaction.
    # 'session_state' is how we remember variables (like the generated audio) across re-runs.
    if 'audio_bytes' not in st.session_state:
        st.session_state['audio_bytes'] = None
    
    # 2. Show Welcome Modal
    # We check if 'welcome_shown' exists. If not, it means this is the user's first visit.
    if 'welcome_shown' not in st.session_state:
        show_welcome_modal()

    # 3. Display Persistent Footer
    display_footer()
    
    # 4. Initialize AWS Client
    client = get_polly_client()
    if not client:
        # If we can't connect, stop the app immediately so the user knows something is wrong.
        st.warning("⚠️ AWS Configuration missing or invalid. Please check your .env file or AWS credentials.")
        st.stop() 

    # 5. Sidebar Configuration
    st.sidebar.header("Configuration")
    
    # Fetch voices dynamically. The spinner shows a visual loading indicator while waiting for AWS.
    with st.spinner("Connecting to AWS Polly..."):
        voices = get_available_voices(client)
    
    if not voices:
        st.error("❌ No voices found. Check your AWS connection and Region.")
        st.stop()
        
    # Create a mapping for the Dropdown menu.
    # User sees: "Joanna (en-US - Female)"
    # Code sees: "Joanna" (The ID required by API)
    voice_options = {f"{v['Name']} ({v['LanguageCode']} - {v['Gender']})": v['Id'] for v in voices}
    
    selected_voice_label = st.sidebar.selectbox(
        "Select Voice",
        options=list(voice_options.keys())
    )
    # Retrieve the actual ID based on what the user picked
    selected_voice_id = voice_options[selected_voice_label]
    
    # Informative sidebar footer
    st.sidebar.markdown("---")
    st.sidebar.info(f"Engine: **{ENGINE.capitalize()}**\nFormat: **{OUTPUT_FORMAT.upper()}**")

    # 6. Main Content Area (Input)
    st.subheader("Text Input")
    text_input = st.text_area(
        "Enter text to convert (max 3000 chars):",
        height=200,
        max_chars=3000,
        help="Type or paste the text you want to convert to speech."
    )

    # 7. Synthesis Action
    # We disable the button if the text area is empty to prevent accidental empty API calls.
    if st.button("Synthesize Speech", type="primary", disabled=not text_input):
        if not text_input.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Generating audio..."):
                # Call our logic function
                audio_data = synthesize_audio(client, text_input, selected_voice_id)
                # Save the result to session state so it persists if the user clicks other things
                st.session_state['audio_bytes'] = audio_data
                
                if audio_data:
                    st.success("Audio generated successfully!")

    # 8. Output Area (Persistent)
    # We check if there is audio in the session state. If yes, we show the player.
    # This ensures the player doesn't disappear when you interact with other widgets.
    if st.session_state['audio_bytes']:
        st.markdown("---")
        st.subheader("Playback & Download")
        
        # Create two columns layout:
        # Col 1 (75%): The Audio Player
        # Col 2 (25%): The Download Button
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

# This check ensures that the main() function only runs if the script is executed directly
# (not imported as a module).
if __name__ == "__main__":
    main()

import streamlit as st
import requests
import time
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Session State Initialization ---
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("NAPKIN_API_KEY", "")
if "generated_image_bytes" not in st.session_state:
    st.session_state.generated_image_bytes = None
if "step" not in st.session_state:
    st.session_state.step = "api_key"
if "generating" not in st.session_state:
    st.session_state.generating = False

# --- Page Configuration ---
st.set_page_config(
    page_title="Napkin AI Visual Generator",
    page_icon="🖼️",
    layout="wide"
)
st.title("🖼️ Napkin AI Visual Generator")

# --- API Functions ---

def start_image_generation_job(prompt_text, api_key, width, height, context_before=None, context_after=None):
    """Step 1: Sends the request to start the job."""
    url = "https://api.napkin.ai/v1/visual"
    payload = {
        "content": prompt_text, "number_of_visuals": 1, "format": "png",
        "width": width, "height": height, "language": "en-US",
        "transparent_background": True
    }
    if context_before: payload["context_before"] = context_before
    if context_after: payload["context_after"] = context_after
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error ({e.response.status_code}): Failed to start job.")
        st.code(e.response.text)
        st.session_state.generating = False
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.session_state.generating = False
        return None

def check_job_status(job_id, api_key):
    """
    Step 2: Polls the job status with an increased timeout and a running timer.
    """
    status_url = f"https://api.napkin.ai/v1/visual/{job_id}/status"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # 1. Increase the timeout to 4 minutes (240 seconds)
    max_wait_time = 240 
    start_time = time.time()

    with st.status("✅ Request sent! Waiting for Napkin AI...", expanded=True) as status:
        while time.time() - start_time < max_wait_time:
            try:
                # 2. Add an elapsed time calculation
                elapsed_time = int(time.time() - start_time)
                
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                status_data = response.json()
                job_status = status_data.get("status", "unknown")

                # 3. Update the status label with the running timer
                status.update(label=f"AI Status: '{job_status.capitalize()}'... (Elapsed: {elapsed_time}s)")

                if job_status == "complete":
                    status.update(label="✅ Visual Created!", state="complete", expanded=False)
                    return status_data
                elif job_status == "failed":
                    status.update(label="❌ Visual Creation Failed.", state="error")
                    st.json(status_data)
                    return None
                
                time.sleep(5)

            except requests.exceptions.RequestException as e:
                status.update(label=f"API Error while checking status: {e}", state="error")
                return None
        
        status.update(label=f"Timeout after {max_wait_time} seconds. The job took too long.", state="error")
        return None

def download_final_image(image_url):
    """Step 3: Downloads the final image data."""
    try:
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading the final image: {str(e)}")
        return None

# --- STREAMLIT UI LOGIC (Unchanged from the previous version) ---

if st.session_state.step == "api_key":
    st.write("Please enter your Napkin AI API key to get started.")
    api_key_input = st.text_input(
        "Napkin AI API Key:", value=st.session_state.api_key, type="password",
        help="Your secret API key from the Napkin AI dashboard."
    )
    if st.button("Continue", type="primary"):
        if not api_key_input:
            st.error("Please enter your API key.")
        else:
            st.session_state.api_key = api_key_input
            st.session_state.step = "prompt"
            st.rerun()

elif st.session_state.step == "prompt":
    left_col, right_col = st.columns([1, 1])
    with left_col:
        st.subheader("Visual Content")
        prompt = st.text_area(
            "Main Content:", height=150,
            placeholder="A detailed description of the visual you want to create."
        )
        st.subheader("Optional Context")
        context_before = st.text_input("Context Before (e.g., a title or brand name):")
        context_after = st.text_input("Context After (e.g., a subtitle or slogan):")
        st.subheader("Image Dimensions")
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input("Width", 256, 2048, 1200, 64)
        with col2:
            height = st.number_input("Height", 256, 2048, 800, 64)

        if st.button("Generate Visual", type="primary", disabled=st.session_state.generating):
            if not prompt:
                st.error("Please enter the main content.")
            else:
                st.session_state.generating = True
                initial_response = start_image_generation_job(
                    prompt, st.session_state.api_key, width, height, context_before, context_after
                )
                if initial_response and initial_response.get("id"):
                    job_id = initial_response["id"]
                    final_status_data = check_job_status(job_id, st.session_state.api_key)
                    if final_status_data and final_status_data.get("generated_files"):
                        with st.spinner("🖼️ Final Image is ready. Downloading..."):
                            image_url = final_status_data["generated_files"][0]["url"]
                            image_bytes = download_final_image(image_url)
                            if image_bytes:
                                st.session_state.generated_image_bytes = image_bytes
                st.session_state.generating = False
                st.rerun()

        if st.button("Change API Key", disabled=st.session_state.generating):
            st.session_state.step = "api_key"
            st.rerun()

    with right_col:
        st.subheader("Final Image")
        if st.session_state.generated_image_bytes:
            try:
                image = Image.open(io.BytesIO(st.session_state.generated_image_bytes))
                st.image(image, caption="Generation Complete", use_column_width=True)
            except Exception as e:
                st.error(f"Could not display the image. Error: {e}")
        else:
            st.info("Your generated visual will appear here.")

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
if "step" not in st.session_state:
    st.session_state.step = "api_key"
if "job_id" not in st.session_state:
    st.session_state.job_id = None
if "job_status_message" not in st.session_state:
    st.session_state.job_status_message = None
if "final_image_url" not in st.session_state:
    st.session_state.final_image_url = None
if "generated_image_bytes" not in st.session_state:
    st.session_state.generated_image_bytes = None

# --- Page Configuration ---
st.set_page_config(page_title="Napkin AI Visual Generator", page_icon="🖼️", layout="wide")
st.title("🖼️ Napkin AI Visual Generator")

# --- API Functions ---

def start_image_generation_job(prompt_text, api_key, width, height, context_before=None, context_after=None):
    url = "https://api.napkin.ai/v1/visual"
    payload = {
        "content": prompt_text, "number_of_visuals": 1, "format": "png",
        "width": width, "height": height, "language": "en-US", "transparent_background": True
    }
    if context_before: payload["context_before"] = context_before
    if context_after: payload["context_after"] = context_after
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def get_job_status(job_id, api_key):
    status_url = f"https://api.napkin.ai/v1/visual/{job_id}/status"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(status_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error checking status: {e}")
        return None

def download_final_image(image_url):
    try:
        with st.spinner("Downloading final image..."):
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading the final image: {str(e)}")
        return None

# --- STREAMLIT UI LOGIC ---

if st.session_state.step == "api_key":
    st.write("Please enter your Napkin AI API key to get started.")
    api_key_input = st.text_input("Napkin AI API Key:", value=st.session_state.api_key, type="password")
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
        prompt = st.text_area("Main Content:", height=150)
        context_before = st.text_input("Context Before (Optional):")
        context_after = st.text_input("Context After (Optional):")
        st.subheader("Image Dimensions")
        width = st.number_input("Width", 256, 2048, 1200, 64)
        height = st.number_input("Height", 256, 2048, 800, 64)

        if st.button("1. Submit Generation Job", type="primary"):
            if prompt and st.session_state.api_key:
                with st.spinner("Submitting job to Napkin AI..."):
                    st.session_state.job_id = None
                    st.session_state.job_status_message = None
                    st.session_state.final_image_url = None
                    st.session_state.generated_image_bytes = None
                    response = start_image_generation_job(
                        prompt, st.session_state.api_key, width, height, context_before, context_after
                    )
                    if response and response.get("id"):
                        st.session_state.job_id = response["id"]
                        st.session_state.job_status_message = f"✅ Job submitted! Your Job ID is: {st.session_state.job_id}"
                    else:
                        st.session_state.job_status_message = "❌ Failed to submit job. Check API key and console for errors."
                st.rerun()
            else:
                st.error("Please provide a prompt and ensure your API key is set.")

        if st.session_state.job_id:
            st.info(st.session_state.job_status_message)
            if st.button("2. Check Status / Get Image"):
                with st.spinner(f"Checking status for Job ID: {st.session_state.job_id}..."):
                    status_data = get_job_status(st.session_state.job_id, st.session_state.api_key)
                    if status_data:
                        job_status = status_data.get("status", "unknown")
                        st.session_state.job_status_message = f"Job Status: '{job_status.capitalize()}'"
                        
                        # --- THE CRITICAL FIX IS HERE ---
                        # Convert to lowercase to handle "complete" and "Completed"
                        if job_status.lower() == "complete":
                            st.balloons()
                            image_url = status_data["generated_files"][0]["url"]
                            st.session_state.final_image_url = image_url
                            image_bytes = download_final_image(image_url)
                            if image_bytes:
                                st.session_state.generated_image_bytes = image_bytes
                st.rerun()

    with right_col:
        st.subheader("Result")
        if st.session_state.final_image_url:
            st.markdown("**Image URL:**")
            st.code(st.session_state.final_image_url, language=None)
        
        if st.session_state.generated_image_bytes:
            try:
                image = Image.open(io.BytesIO(st.session_state.generated_image_bytes))
                st.image(image, caption="Final Generated Image", use_column_width=True)
            except Exception as e:
                st.error(f"Could not display image. Error: {e}")
        elif st.session_state.job_id:
            st.info("Once the job is complete, your image will appear here.")
        else:
            st.info("Submit a job to see the result.")

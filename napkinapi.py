import streamlit as st
import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Session State Initialization ---
# A clean dictionary to hold all job-related state.
if "job" not in st.session_state:
    st.session_state.job = {
        "id": None,
        "status_message": "Submit a job to begin.",
        "image_bytes": None,
        "last_api_response": None,
        "error": None
    }
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("NAPKIN_API_KEY", "")
if "step" not in st.session_state:
    st.session_state.step = "api_key"

# --- Page Configuration ---
st.set_page_config(page_title="Napkin AI Visual Generator", page_icon="🖼️", layout="wide")
st.title("🖼️ Napkin AI Visual Generator")

# --- API Functions ---

def start_job(api_key, payload):
    """Submits the job and returns the server's response."""
    url = "https://api.napkin.ai/v1/visual"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.session_state.job["error"] = f"API Error on Job Submission: {e}"
        return None

def check_status(job_id, api_key):
    """Performs a single check of the job's status."""
    status_url = f"https://api.napkin.ai/v1/visual/{job_id}/status"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(status_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.session_state.job["error"] = f"API Error Checking Status: {e}"
        return None

def download_image(visual_id, api_key):
    """Downloads the image from the dedicated endpoint using the VISUAL ID."""
    download_url = f"https://api.napkin.ai/api/download-visual-file?visualId={visual_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(download_url, headers=headers, timeout=90)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.session_state.job["error"] = f"Download Error: {e}"
        return None

# --- Main App Logic ---

# Step 1: Get API Key
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

# Step 2: Main Interface
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
                st.session_state.job = {k: None for k in st.session_state.job} # Clear old job
                payload = {
                    "content": prompt, "number_of_visuals": 1, "format": "png",
                    "width": width, "height": height, "language": "en-US", "transparent_background": True,
                    "context_before": context_before, "context_after": context_after
                }
                with st.spinner("Submitting job to Napkin AI..."):
                    response = start_job(st.session_state.api_key, payload)
                if response and response.get("id"):
                    st.session_state.job["id"] = response["id"]
                    st.session_state.job["status_message"] = f"✅ Job submitted! Your Job ID is: {st.session_state.job['id']}"
                else:
                    st.session_state.job["status_message"] = "❌ Failed to submit job."
            else:
                st.error("Please provide a prompt and ensure your API key is set.")

        if st.session_state.job.get("id"):
            st.info(st.session_state.job.get("status_message"))
            if st.button("2. Check Status / Get Image"):
                job_id = st.session_state.job['id']
                api_key = st.session_state.api_key
                with st.spinner(f"Checking status for Job ID: {job_id}..."):
                    status_data = check_status(job_id, api_key)
                st.session_state.job["last_api_response"] = status_data

                if status_data:
                    job_status = status_data.get("status", "unknown")
                    st.session_state.job["status_message"] = f"Job Status: '{job_status.capitalize()}'"
                    
                    if job_status.lower() == "complete":
                        files = status_data.get("generated_files")
                        if files and isinstance(files, list) and len(files) > 0:
                            visual_id = files[0].get("visual_id")
                            if visual_id:
                                st.session_state.job["status_message"] = f"✅ Job Complete! Found Visual ID: {visual_id}. Now downloading..."
                                with st.spinner("Downloading image..."):
                                    image_bytes = download_image(visual_id, api_key)
                                if image_bytes:
                                    st.session_state.job["image_bytes"] = image_bytes
                                    st.session_state.job["status_message"] = "✅ Download successful!"
                                    st.balloons()
                            else:
                                st.session_state.job["error"] = "❌ Error: Job complete, but 'generated_files' data is missing."
                        
    with right_col:
        st.subheader("Result")
        
        if st.session_state.job.get("image_bytes"):
            try:
                image = Image.open(io.BytesIO(st.session_state.job["image_bytes"]))
                st.image(image, caption="Final Generated Image", use_column_width=True)
            except Exception as e:
                st.session_state.job["error"] = f"Could not display image: {e}"
        else:
            st.info(st.session_state.job.get("status_message", "Submit a job on the left to see the result."))

        if st.session_state.job.get("error"):
            st.error(st.session_state.job["error"])

        if st.session_state.job.get("last_api_response"):
            with st.expander("Last Raw API Response from Server"):
                st.json(st.session_state.job["last_api_response"])

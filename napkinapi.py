import streamlit as st
import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Session State Initialization ---
# A clean dictionary to hold all job-related state, preventing clutter
if "job" not in st.session_state:
    st.session_state.job = {
        "id": None,
        "status_message": None,
        "final_image_url": None,
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

def start_image_generation_job(prompt_text, api_key, width, height, context_before=None, context_after=None):
    """Submits the job and returns the server's response."""
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
        st.session_state.job["error"] = f"API Error on Job Submission: {e}"
        return None

def get_job_status(job_id, api_key):
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

def download_final_image(image_url, api_key):
    """Downloads the final image from its URL, providing authorization."""
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(image_url, headers=headers, timeout=90)
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

    # --- Left Column (Inputs) ---
    with left_col:
        st.subheader("Visual Content")
        prompt = st.text_area("Main Content:", height=150)
        context_before = st.text_input("Context Before (Optional):")
        context_after = st.text_input("Context After (Optional):")
        st.subheader("Image Dimensions")
        width = st.number_input("Width", 256, 2048, 1200, 64)
        height = st.number_input("Height", 256, 2048, 800, 64)

        # Button to start the whole process
        if st.button("1. Submit Generation Job", type="primary"):
            if prompt and st.session_state.api_key:
                with st.spinner("Submitting job to Napkin AI..."):
                    st.session_state.job = {k: None for k in st.session_state.job} # Clear old job
                    response = start_image_generation_job(
                        prompt, st.session_state.api_key, width, height, context_before, context_after
                    )
                    if response and response.get("id"):
                        st.session_state.job["id"] = response["id"]
                        st.session_state.job["status_message"] = f"✅ Job submitted! Your Job ID is: {st.session_state.job['id']}"
                    else:
                        st.session_state.job["status_message"] = "❌ Failed to submit job."
            else:
                st.error("Please provide a prompt and ensure your API key is set.")
            st.rerun()

        # Section for checking status
        if st.session_state.job.get("id"):
            st.info(st.session_state.job.get("status_message", "No status yet."))
            if st.button("2. Check Status / Get Image"):
                with st.spinner(f"Checking status for Job ID: {st.session_state.job['id']}..."):
                    status_data = get_job_status(st.session_state.job['id'], st.session_state.api_key)
                    st.session_state.job["last_api_response"] = status_data

                    if status_data:
                        job_status = status_data.get("status", "unknown")
                        st.session_state.job["status_message"] = f"Job Status: '{job_status.capitalize()}'"
                        
                        if job_status.lower() == "complete":
                            st.session_state.job["status_message"] = "✅ Job Complete! Found image data."
                            files = status_data.get("generated_files")
                            if files and isinstance(files, list) and len(files) > 0:
                                image_url = files[0].get("url")
                                if image_url:
                                    st.session_state.job["final_image_url"] = image_url
                                    image_bytes = download_final_image(image_url, st.session_state.api_key)
                                    if image_bytes:
                                        st.session_state.job["image_bytes"] = image_bytes
                                        st.session_state.job["status_message"] = "✅ Download successful!"
                                        st.balloons()
                st.rerun()

    # --- Right Column (Outputs) ---
    with right_col:
        st.subheader("Result")
        
        # Display the URL as soon as we have it
        if st.session_state.job.get("final_image_url"):
            st.markdown("**Image URL (for reference only):**")
            st.code(st.session_state.job["final_image_url"], language=None)
        
        # Display the image if we have the bytes
        if st.session_state.job.get("image_bytes"):
            try:
                image = Image.open(io.BytesIO(st.session_state.job["image_bytes"]))
                st.image(image, caption="Final Generated Image", use_column_width=True)
            except Exception as e:
                st.session_state.job["error"] = f"Could not display image: {e}"
        elif st.session_state.job.get("id"):
            st.info("Once the job is complete, the image and link will appear here.")
        else:
            st.info("Submit a job on the left to see the result.")

        # Display any errors that occurred
        if st.session_state.job.get("error"):
            st.error(st.session_state.job["error"])

        # Display the raw API response for debugging
        if st.session_state.job.get("last_api_response"):
            with st.expander("Last Raw API Response from Server"):
                st.json(st.session_state.job["last_api_response"])

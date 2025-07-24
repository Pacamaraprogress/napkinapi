import streamlit as st
import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Session State Initialization ---
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
def start_image_generation_job(api_key, payload):
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

def download_image_with_authorization(image_url, api_key):
    """Downloads the image from a protected URL with proper authorization."""
    st.write("Attempting to download image with authorization...")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        st.write(f"Sending request to: {image_url}")
        response = requests.get(image_url, headers=headers, timeout=90)
        
        # Debug information
        st.write(f"Response status code: {response.status_code}")
        st.write(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            st.error(f"Server returned non-200 status: {response.status_code}")
            if len(response.content) < 1000:  # If response is small, show it
                st.write(f"Response content: {response.content.decode('utf-8', errors='replace')}")
        
        response.raise_for_status()
        return response.content
        
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                st.session_state.job["error"] = "Download Failed: 401 Unauthorized. The API key was rejected by the server for the download."
            else:
                st.session_state.job["error"] = f"Download Failed: Server returned status {e.response.status_code}."
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request Exception: {e}")
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
        
        # Advanced options in an expander
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                width = st.number_input("Width", 256, 2048, 1200, 64)
            with col2:
                height = st.number_input("Height", 256, 2048, 800, 64)
                
            transparent_bg = st.checkbox("Transparent Background", value=True)
            file_format = st.selectbox("Format", ["png", "jpg"], index=0)

        if st.button("1. Submit Generation Job", type="primary"):
            if prompt and st.session_state.api_key:
                with st.spinner("Submitting job to Napkin AI..."):
                    st.session_state.job = {k: None for k in st.session_state.job}
                    payload = {
                        "content": prompt,
                        "number_of_visuals": 1,
                        "format": file_format,
                        "width": width,
                        "height": height,
                        "language": "en-US",
                        "transparent_background": transparent_bg
                    }
                    
                    # Add optional parameters only if they exist
                    if context_before:
                        payload["context_before"] = context_before
                    if context_after:
                        payload["context_after"] = context_after
                        
                    response = start_image_generation_job(st.session_state.api_key, payload)
                    if response and response.get("id"):
                        st.session_state.job["id"] = response["id"]
                        st.session_state.job["status_message"] = f"✅ Job submitted! Your Job ID is: {st.session_state.job['id']}"
                    else:
                        st.session_state.job["status_message"] = "❌ Failed to submit job."
            else:
                st.error("Please provide a prompt and ensure your API key is set.")
            st.rerun()

        if st.session_state.job.get("id"):
            st.info(st.session_state.job.get("status_message", "No status yet."))
            if st.button("2. Check Status / Get Image"):
                with st.spinner(f"Checking status for Job ID: {st.session_state.job['id']}..."):
                    status_data = get_job_status(st.session_state.job['id'], st.session_state.api_key)
                    st.session_state.job["last_api_response"] = status_data

                    if status_data:
                        job_status = status_data.get("status", "unknown")
                        st.session_state.job["status_message"] = f"Job Status: '{job_status.capitalize()}'"
                        
                        # Check for both "complete" and "completed" status
                        if job_status.lower() in ["complete", "completed"]:
                            files = status_data.get("generated_files")
                            if files and isinstance(files, list) and len(files) > 0:
                                image_url = files[0].get("url")
                                if image_url:
                                    st.session_state.job["final_image_url"] = image_url
                                    st.write("Downloading image from URL:", image_url)
                                    image_bytes = download_image_with_authorization(image_url, st.session_state.api_key)
                                    if image_bytes:
                                        st.session_state.job["image_bytes"] = image_bytes
                                        st.session_state.job["status_message"] = "✅ Download successful!"
                                        st.balloons()
                                    else:
                                        st.error("Failed to download the image. You might need to copy the URL and download it manually with proper authorization.")
                st.rerun()

    # --- Right Column (Outputs) ---
    with right_col:
        st.subheader("Result")
        
        if st.session_state.job.get("final_image_url"):
            st.markdown("**Image URL (for reference only):**")
            st.code(st.session_state.job["final_image_url"], language=None)
        
        if st.session_state.job.get("image_bytes"):
            try:
                image = Image.open(io.BytesIO(st.session_state.job["image_bytes"]))
                st.image(image, caption="Generated Image", use_column_width=True)
                
                # Add download button
                btn = st.download_button(
                    label="Download Image",
                    data=st.session_state.job["image_bytes"],
                    file_name=f"napkin-ai-image.png",
                    mime="image/png",
                )
                
            except Exception as e:
                st.session_state.job["error"] = f"Could not display image: {e}"
        elif st.session_state.job.get("id"):
            st.info("Once the job is complete, the image and link will appear here.")
        else:
            st.info("Submit a job on the left to see the result.")

        if st.session_state.job.get("error"):
            st.error(st.session_state.job["error"])

        if st.session_state.job.get("last_api_response"):
            with st.expander("Last Raw API Response from Server"):
                st.json(st.session_state.job["last_api_response"])

# Add footer with instructions
st.markdown("---")
st.markdown("""
### How to use
1. Enter your Napkin AI API key
2. Enter your image prompt and any optional context
3. Click "Submit Generation Job" to start the process
4. Use "Check Status / Get Image" to monitor and retrieve your image
5. Once complete, you can view and download your generated image
""")

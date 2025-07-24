import streamlit as st
import requests
import time
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Session State Initialization ---
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("NAPKIN_API_KEY", "")
if "generated_image_bytes" not in st.session_state:
    st.session_state.generated_image_bytes = None
if "step" not in st.session_state:
    st.session_state.step = "api_key"

st.set_page_config(page_title="Napkin AI Visual Generator", page_icon="🖼️", layout="wide")
st.title("🖼️ Napkin AI Visual Generator")

# --- CORRECTED API FUNCTIONS BASED ON YOUR JSON ---

def start_image_generation_job(prompt_text, api_key, width, height):
    """Step 1: Starts the generation job and returns the job ID."""
    url = "https://api.napkin.ai/v1/visual"
    
    # Payload structure from your JSON file
    payload = {
        "content": prompt_text,
        "number_of_visuals": 1,
        "format": "png",
        "width": width,
        "height": height,
        "transparent_background": True # Example parameter from your file
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        # The initial response contains the job ID
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error ({e.response.status_code}): Failed to start job.")
        st.code(e.response.text)
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def check_job_status(job_id, api_key):
    """Step 2: Polls the status of the generation job."""
    status_url = f"https://api.napkin.ai/v1/visual/{job_id}/status"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Polling loop with a timeout
    max_wait_time = 120  # 2 minutes timeout
    start_time = time.time()
    
    with st.spinner(f"Job submitted (ID: {job_id}). Waiting for image to be generated...") as spinner:
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                status_data = response.json()

                job_status = status_data.get("status")
                spinner.text = f"Job status: '{job_status}'... Waiting..."

                if job_status == "complete":
                    st.success("Image generation complete!")
                    # The final data contains the download URL
                    return status_data
                elif job_status == "failed":
                    st.error("Image generation failed.")
                    st.json(status_data)
                    return None
                
                # Wait before polling again
                time.sleep(5)

            except requests.exceptions.RequestException as e:
                st.error(f"API Error while checking status: {e}")
                return None
        
        st.error("Timeout: Image generation took too long.")
        return None

def download_image(image_url):
    """Step 3: Downloads the final image from the provided URL."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading final image: {str(e)}")
        return None

# --- STREAMLIT UI ---

# Step 1: API Key Entry
if st.session_state.step == "api_key":
    st.write("Please enter your Napkin AI API key to get started.")
    api_key_input = st.text_input(
        "Napkin AI API Key:", value=st.session_state.api_key, type="password"
    )
    if st.button("Continue"):
        if not api_key_input:
            st.error("Please enter your API key.")
        else:
            st.session_state.api_key = api_key_input
            st.session_state.step = "prompt"
            st.rerun()

# Step 2: Prompt and Generation
elif st.session_state.step == "prompt":
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Image Generation Prompt")
        prompt = st.text_area(
            "Enter the content for the visual:",
            height=150,
            placeholder="A detailed description of the visual you want to create."
        )

        st.subheader("Image Dimensions")
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input("Width", min_value=256, max_value=2048, value=1200, step=64)
        with col2:
            height = st.number_input("Height", min_value=256, max_value=2048, value=800, step=64)

        if st.button("Generate Image", type="primary"):
            if not prompt:
                st.error("Please enter a prompt.")
            elif not st.session_state.api_key:
                st.error("API Key is not set. Please go back and enter it.")
            else:
                # --- Execute the 3-step workflow ---
                initial_response = start_image_generation_job(prompt, st.session_state.api_key, width, height)
                
                if initial_response and initial_response.get("id"):
                    job_id = initial_response["id"]
                    final_status_data = check_job_status(job_id, st.session_state.api_key)
                    
                    if final_status_data and final_status_data.get("generated_files"):
                        image_url = final_status_data["generated_files"][0]["url"]
                        image_bytes = download_image(image_url)
                        
                        if image_bytes:
                            st.session_state.generated_image_bytes = image_bytes
                            st.rerun()

        if st.button("Change API Key"):
            st.session_state.step = "api_key"
            st.rerun()

    with right_col:
        st.subheader("Generated Image")
        if st.session_state.generated_image_bytes:
            try:
                image = Image.open(io.BytesIO(st.session_state.generated_image_bytes))
                st.image(image, caption="Generated Image", use_column_width=True)
                st.download_button(
                    label="Download Image",
                    data=st.session_state.generated_image_bytes,
                    file_name="napkin_ai_image.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Could not display the image. Error: {e}")
        else:
            st.info("Your generated image will appear here.")

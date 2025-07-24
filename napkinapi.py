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
# This ensures that variables persist between user interactions
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("NAPKIN_API_KEY", "")
if "generated_image_bytes" not in st.session_state:
    st.session_state.generated_image_bytes = None
if "step" not in st.session_state:
    st.session_state.step = "api_key"

# --- Page Configuration ---
st.set_page_config(
    page_title="Napkin AI Visual Generator",
    page_icon="🖼️",
    layout="wide"
)

st.title("🖼️ Napkin AI Visual Generator")

# --- API Functions ---

def start_image_generation_job(prompt_text, api_key, width, height):
    """
    Step 1: Sends the initial request to start the image generation job.
    Returns the server's response which should include a job ID.
    """
    url = "https://api.napkin.ai/v1/visual"

    # This payload structure is based on your working JSON file.
    # The 'language' field is now included to fix the 400 error.
    payload = {
        "content": prompt_text,
        "number_of_visuals": 1,
        "format": "png",
        "width": width,
        "height": height,
        "language": "en-US",  # <-- The critical fix is here
        "transparent_background": True
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error ({e.response.status_code}): Failed to start job.")
        # Show the exact error from the server (e.g., "validation failed...")
        st.code(e.response.text)
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def check_job_status(job_id, api_key):
    """
    Step 2: Polls the status of the generation job until it's complete or fails.
    """
    status_url = f"https://api.napkin.ai/v1/visual/{job_id}/status"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Set a timeout to prevent the app from waiting forever
    max_wait_time = 120  # 2 minutes
    start_time = time.time()

    with st.spinner(f"Job submitted (ID: {job_id}). Waiting for image...") as spinner:
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                status_data = response.json()
                job_status = status_data.get("status")

                spinner.text = f"Job status: '{job_status}'... Please wait."

                if job_status == "complete":
                    st.success("Image generation complete!")
                    return status_data
                elif job_status == "failed":
                    st.error("Image generation failed.")
                    st.json(status_data) # Show the failure reason
                    return None

                # Wait for 5 seconds before checking again
                time.sleep(5)

            except requests.exceptions.RequestException as e:
                st.error(f"API Error while checking status: {e}")
                return None

        st.error("Timeout: Image generation took too long.")
        return None

def download_final_image(image_url):
    """Step 3: Downloads the final image from the URL provided in the status response."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading the final image: {str(e)}")
        return None

# --- STREAMLIT UI LOGIC ---

# The app has two main steps: entering the API key, then the prompt.
if st.session_state.step == "api_key":
    st.write("Please enter your Napkin AI API key to get started.")
    api_key_input = st.text_input(
        "Napkin AI API Key:",
        value=st.session_state.api_key,
        type="password",
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
    # Use a two-column layout for the main interface
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
                # --- This is where the 3-step API process is called ---
                initial_response = start_image_generation_job(prompt, st.session_state.api_key, width, height)

                if initial_response and initial_response.get("id"):
                    job_id = initial_response["id"]
                    final_status_data = check_job_status(job_id, st.session_state.api_key)

                    if final_status_data and final_status_data.get("generated_files"):
                        # Get the URL from the completed job status
                        image_url = final_status_data["generated_files"][0]["url"]
                        image_bytes = download_final_image(image_url)

                        if image_bytes:
                            # Save the final image to the session state to be displayed
                            st.session_state.generated_image_bytes = image_bytes
                            st.rerun()

        # Button to go back and change the API key
        if st.button("Change API Key"):
            st.session_state.step = "api_key"
            st.rerun()

    with right_col:
        st.subheader("Generated Image")
        if st.session_state.generated_image_bytes:
            try:
                # Display the image and a download button
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
            # Placeholder message
            st.info("Your generated image will appear here.")

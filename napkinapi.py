import streamlit as st
import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# --- Session State Initialization ---
if "step" not in st.session_state:
    st.session_state.step = "api_key"
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("NAPKIN_API_KEY", "")
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "image_url" not in st.session_state:
    st.session_state.image_url = ""
if "api_response" not in st.session_state:
    st.session_state.api_response = None

st.set_page_config(
    page_title="Napkin AI Image Generator",
    page_icon="🖼️",
    layout="wide"
)

st.title("🖼️ Napkin AI Image Generator")

# --- MODIFIED AND CORRECTED API FUNCTION ---
def generate_image(prompt_text, api_key, aspect, style, auth_format, visual_type=None, background_color=None, color_theme=None):
    """
    Calls the Napkin AI API to generate an image.
    This function now accepts all parameters from the UI and handles different auth formats.
    """
    # Use a versioned URL, which is a common and safer practice
    url = "https://api.napkin.ai/api/v1/create-visual-request"

    # Build the payload, only including optional parameters if they have values
    payload = {
        "prompt": prompt_text,
        "aspectRatio": aspect,
        "style_id": style
    }
    if visual_type:
        payload["visual_type_hint"] = visual_type
    if background_color:
        payload["background_color"] = background_color
    if color_theme:
        payload["color_theme"] = color_theme

    # Dynamically set the authorization header based on user selection to fix 401 errors
    headers = {"Content-Type": "application/json"}
    if auth_format == "Bearer Token":
        headers["Authorization"] = f"Bearer {api_key}"
    elif auth_format == "API Key Header":
        headers["X-API-Key"] = api_key # A common alternative
    elif auth_format == "Raw Key": # Potentially a custom header for Napkin
        headers["NAPKIN-ACCOUNT-API-KEY"] = api_key


    try:
        response = requests.post(url, json=payload, headers=headers)
        # This will raise a detailed error for 4xx or 5xx status codes
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Give specific feedback for 401 Unauthorized errors
        if e.response.status_code == 401:
            st.error(f"API Error: 401 Unauthorized. The API key was rejected with the '{auth_format}' format. Please check your key and try a different auth format below.")
            st.warning(f"Request Headers Sent (key is hidden): {{'Authorization': '...', 'Content-Type': 'application/json'}}")
            st.json(f"Full Error: {e.response.text}") # Show the exact error from the server
        else:
            st.error(f"API Error: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: Could not connect to the API. {str(e)}")
        return None

def download_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

# --- Step 1: API Key Entry ---
if st.session_state.step == "api_key":
    st.write("First, please enter your Napkin AI API key to get started.")
    api_key = st.text_input(
        "Napkin AI API Key:",
        value=st.session_state.api_key,
        type="password",
        help="Your secret API key from the Napkin AI dashboard."
    )
    if st.button("Continue"):
        if not api_key:
            st.error("Please enter your Napkin AI API key to continue.")
        else:
            st.session_state.api_key = api_key
            st.session_state.step = "prompt"
            st.rerun()

# --- Step 2: Prompt and Generation ---
elif st.session_state.step == "prompt":
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Enter your prompt")
        prompt = st.text_area(
            "Image prompt:",
            height=100,
            placeholder="A vibrant cityscape at sunset, cyberpunk style"
        )

        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                image_width = st.number_input("Width", 256, 1024, 512, 64)
            with col2:
                image_height = st.number_input("Height", 256, 1024, 512, 64)
            aspect_ratio = f"{image_width}x{image_height}"

            style_categories = {
                # Your style categories dictionary... (omitted for brevity)
                 "Classic Art Styles": [
                    {"name": "Realistic", "id": "realistic", "description": "Photo-realistic rendering"},
                    {"name": "Cinematic", "id": "cinematic", "description": "Movie-like scenes"},
                 ]
            }
            style_category = st.selectbox("Style Category", list(style_categories.keys()))
            style_options = style_categories[style_category]
            style_names = [f"{s['name']} - {s['description']}" for s in style_options]
            selected_style_name = st.selectbox("Style", style_names)
            style = style_options[style_names.index(selected_style_name)]["id"]

            visual_type = st.selectbox("Visual Type Hint", ["None (Let AI decide)", "Chart/Graph", "Diagram"])
            background_color = st.color_picker("Background Color", "#FFFFFF")
            color_theme = st.selectbox("Color Theme", ["Default", "Vibrant", "Pastel"])

        # --- CRITICAL: API Debugging to solve 401 error ---
        with st.expander("API Authentication Settings", expanded=True):
            st.info("If you get a 401 Unauthorized Error, your API key is likely correct but the format is wrong. Try a different option.")
            auth_format = st.radio(
                "Authorization Format",
                ["Bearer Token", "API Key Header", "Raw Key"],
                index=0,
                help="Select the header format for the API key. 'Bearer Token' is most common."
            )
            st.session_state.auth_format = auth_format


        if st.button("Generate Image"):
            if not prompt:
                st.error("Please enter a prompt for your image.")
            else:
                with st.spinner("Generating your image..."):
                    # Prepare optional parameters
                    visual_type_param = None if visual_type == "None (Let AI decide)" else visual_type
                    color_theme_param = None if color_theme == "Default" else color_theme

                    # Make the corrected API call
                    result = generate_image(
                        prompt_text=prompt,
                        api_key=st.session_state.api_key,
                        aspect=aspect_ratio,
                        style=style,
                        auth_format=st.session_state.get("auth_format", "Bearer Token"),
                        visual_type=visual_type_param,
                        background_color=background_color,
                        color_theme=color_theme_param
                    )

                    if result and ("imageUrl" in result or "imageData" in result):
                        st.success("Image generated successfully!")
                        st.session_state.api_response = result
                        image_content = None

                        # Prioritize direct image data if available
                        if 'imageData' in result and result['imageData']:
                            image_content = io.BytesIO(result['imageData'])
                        # Fallback to downloading from URL
                        elif 'imageUrl' in result:
                            st.session_state.image_url = result["imageUrl"]
                            image_content = download_image(result["imageUrl"])

                        if image_content:
                            st.session_state.generated_image = image_content
                            st.rerun()
                        else:
                            st.error("API call succeeded but failed to retrieve image content.")
                    elif result is not None:
                         st.error("API call failed. Response did not contain an image URL or data.")
                         st.json(result)


        if st.button("Change API Key"):
            st.session_state.step = "api_key"
            st.rerun()

    with right_col:
        st.subheader("Generated Image")
        if st.session_state.generated_image:
            image_bytes = st.session_state.generated_image.getvalue() if isinstance(st.session_state.generated_image, io.BytesIO) else st.session_state.generated_image
            st.image(image_bytes, caption="Generated Image", use_column_width=True)

            st.download_button(
                label="Download Image",
                data=image_bytes,
                file_name="napkin_ai_image.png",
                mime="image/png"
            )
            st.text_input("Image URL:", value=st.session_state.image_url)
            with st.expander("API Response Details"):
                st.json(st.session_state.api_response)
        else:
            st.info("Your generated image will appear here.")

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Napkin AI")

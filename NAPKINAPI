import streamlit as st
import requests
import base64
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

st.set_page_config(
    page_title="Napkin AI Image Generator",
    page_icon="🖼️",
    layout="centered"
)

st.title("🖼️ Napkin AI Image Generator")
st.write("Generate beautiful AI images using Napkin AI's API")

# Sidebar for API key input
with st.sidebar:
    st.header("API Configuration")
    
    # Get API key from environment variable or user input
    default_api_key = os.getenv("NAPKIN_API_KEY", "")
    api_key = st.text_input("Napkin AI API Key", value=default_api_key, type="password")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app uses Napkin AI's API to generate images from text prompts.")
    st.markdown("Learn more at [napkin.ai](https://napkin.ai)")

# Main content
prompt = st.text_area("Enter your image prompt:", height=100, 
                      placeholder="A vibrant cityscape at sunset with neon lights reflecting in puddles, cyberpunk style")

# Advanced options collapsible section
with st.expander("Advanced Options"):
    col1, col2 = st.columns(2)
    with col1:
        image_width = st.number_input("Width", min_value=256, max_value=1024, value=512, step=64)
    with col2:
        image_height = st.number_input("Height", min_value=256, max_value=1024, value=512, step=64)
    
    aspect_ratio = f"{image_width}x{image_height}"
    
    style_options = [
        "Realistic", "Cinematic", "Anime", "Digital Art", "Pixel Art", 
        "Watercolor", "Oil Painting", "Sketch", "Illustration", "Photography",
        "3D Render", "Minimalist"
    ]
    style = st.selectbox("Style", options=style_options, index=0)

# Function to call Napkin AI API
def generate_image(prompt_text, api_key, aspect="512x512", style="Realistic"):
    url = "https://api.napkin.ai/api/create-visual-request"
    
    payload = {
        "prompt": prompt_text,
        "aspectRatio": aspect,
        "style": style
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Function to download image from URL
def download_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

# Generate button
if st.button("Generate Image"):
    if not api_key:
        st.error("Please enter your Napkin AI API key in the sidebar.")
    elif not prompt:
        st.error("Please enter a prompt for your image.")
    else:
        with st.spinner("Generating your image..."):
            # Make API call
            result = generate_image(
                prompt_text=prompt,
                api_key=api_key,
                aspect=aspect_ratio,
                style=style
            )
            
            if result and "imageUrl" in result:
                # Display success message
                st.success("Image generated successfully!")
                
                # Get image from URL
                image_content = download_image(result["imageUrl"])
                
                if image_content:
                    # Display the image
                    image = Image.open(io.BytesIO(image_content))
                    st.image(image, caption="Generated Image", use_column_width=True)
                    
                    # Create download button
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format="PNG")
                    img_bytes = img_buffer.getvalue()
                    
                    st.download_button(
                        label="Download Image",
                        data=img_bytes,
                        file_name="napkin_ai_image.png",
                        mime="image/png"
                    )
                    
                    # Display the image URL
                    st.text_input("Image URL:", value=result["imageUrl"])
                    
                    # Display JSON response for debugging
                    with st.expander("API Response Details"):
                        st.json(result)
            else:
                st.error("Failed to generate image. Please check your API key and try again.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Napkin AI")

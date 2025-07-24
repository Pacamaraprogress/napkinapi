import streamlit as st
import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Initialize session state for multi-step flow
if "step" not in st.session_state:
    st.session_state.step = "api_key"  # First step: enter API key
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("NAPKIN_API_KEY", "")
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "image_url" not in st.session_state:
    st.session_state.image_url = ""

st.set_page_config(
    page_title="Napkin AI Image Generator",
    page_icon="🖼️",
    layout="wide"  # Use wide layout for side-by-side display
)

st.title("🖼️ Napkin AI Image Generator")

# Function to call Napkin AI API
def generate_image(prompt_text, api_key, aspect="512x512", style="Realistic"):
    url = "https://api.napkin.ai/api/create-visual-request"
    
    payload = {
        "prompt": prompt_text,
        "aspectRatio": aspect,
        "style_id": style  # Using style_id instead of style
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
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

# Step 1: API Key Entry
if st.session_state.step == "api_key":
    st.write("First, please enter your Napkin AI API key to get started.")
    
    api_key = st.text_input(
        "Napkin AI API Key:", 
        value=st.session_state.api_key,
        type="password",
        help="Enter your Napkin AI API key. This is required to generate images."
    )
    
    if st.button("Continue"):
        if not api_key:
            st.error("Please enter your Napkin AI API key to continue.")
        else:
            st.session_state.api_key = api_key
            st.session_state.step = "prompt"
            st.experimental_rerun()

# Step 2: Prompt Entry and Image Generation
elif st.session_state.step == "prompt":
    # Set up two-column layout
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.subheader("Enter your prompt")
        
        prompt = st.text_area(
            "Image prompt:", 
            height=100,
            placeholder="A vibrant cityscape at sunset with neon lights reflecting in puddles, cyberpunk style"
        )
        
        # Advanced options in left column
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                image_width = st.number_input("Width", min_value=256, max_value=1024, value=512, step=64)
            with col2:
                image_height = st.number_input("Height", min_value=256, max_value=1024, value=512, step=64)
            
            aspect_ratio = f"{image_width}x{image_height}"
            
            # Create style categories with IDs from Napkin AI documentation
            style_categories = {
                "Colorful Styles": [
                    {"name": "Vibrant Strokes", "id": "CDQPRVVJCSTPRBBCD5Q6AWR", "description": "A flow of vivid lines for bold notes"},
                    {"name": "Glowful Breeze", "id": "CDQPRVVJCSTPRBBKDXK78", "description": "A swirl of cheerful color for laid-back planning"},
                    {"name": "Bold Canvas", "id": "CDQPRVVJCSTPRBB6DHGQ8", "description": "A vivid field of shapes for lively notes"},
                    {"name": "Radiant Blocks", "id": "CDQPRVVJCSTPRBB6D5P6RSB4", "description": "A bright spread of solid color for tasks"},
                    {"name": "Pragmatic Shades", "id": "CDQPRVVJCSTPRBB7E9GP8TB5DST0", "description": "A palette of blended hues for bold ideas"}
                ],
                "Casual Styles": [
                    {"name": "Carefree Mist", "id": "CDGQ6XB1DGPQ6VV6EG", "description": "A wisp of calm tones for playful tasks"},
                    {"name": "Lively Layers", "id": "CDGQ6XB1DGPPCTBCDHJP8", "description": "A breeze of soft color for bright ideas"}
                ],
                "Hand-drawn Styles": [
                    {"name": "Artistic Flair", "id": "D1GPWS1DCDQPRVVJCSTPR", "description": "A splash of hand-drawn color for creative thinking"},
                    {"name": "Sketch Notes", "id": "D1GPWS1DDHMPWSBK", "description": "A hand-drawn style for free-flowing ideas"}
                ],
                "Formal Styles": [
                    {"name": "Elegant Outline", "id": "CSQQ4VB1DGPP4V31CDNJTVKFBXK6JV3C", "description": "A refined black outline for professional clarity"},
                    {"name": "Subtle Accent", "id": "CSQQ4VB1DGPPRTB7D1T0", "description": "A light touch of color for professional documents"},
                    {"name": "Monochrome Pro", "id": "CSQQ4VB1DGPQ6TBECXP6ABB3DXP6YWG", "description": "A single-color approach for focused presentations"},
                    {"name": "Corporate Clean", "id": "CSQQ4VB1DGPPTVVEDXHPGWKFDNJJTSKCC5T0", "description": "A professional flat style for business diagrams"}
                ],
                "Monochrome Styles": [
                    {"name": "Minimal Contrast", "id": "DNQPWVV3D1S6YVB55NK6RRBM", "description": "A clean monochrome style for focused work"},
                    {"name": "Silver Beam", "id": "CXS62Y9DCSQP6XBK", "description": "A spotlight of gray scale ease with striking focus"}
                ],
                "Classic Art Styles": [
                    {"name": "Realistic", "id": "realistic", "description": "Photo-realistic rendering with natural lighting and details"},
                    {"name": "Cinematic", "id": "cinematic", "description": "Movie-like scenes with dramatic lighting and composition"},
                    {"name": "Anime", "id": "anime", "description": "Japanese animation style with distinctive characters and vibrant colors"},
                    {"name": "Digital Art", "id": "digital_art", "description": "Computer-generated artwork with sharp details and modern feel"},
                    {"name": "Watercolor", "id": "watercolor", "description": "Soft, flowing colors with transparent, painterly effects"},
                    {"name": "Oil Painting", "id": "oil_painting", "description": "Rich, textured paint with visible brushstrokes"},
                    {"name": "Pixel Art", "id": "pixel_art", "description": "Retro, blocky style reminiscent of classic video games"}
                ]
            }
            
            # First, select the style category
            style_category = st.selectbox("Style Category", options=list(style_categories.keys()))
            
            # Then, select the specific style from that category
            style_options = style_categories[style_category]
            style_index = 0
            
            # Create a formatted list of options with descriptions
            style_names = [f"{s['name']} - {s['description']}" for s in style_options]
            selected_style_name = st.selectbox("Style", options=style_names, index=style_index)
            
            # Extract the selected style's ID
            selected_style_index = style_names.index(selected_style_name)
            style = style_options[selected_style_index]["id"]
        
        if st.button("Generate Image"):
            if not prompt:
                st.error("Please enter a prompt for your image.")
            else:
                with st.spinner("Generating your image..."):
                    # Make API call
                    result = generate_image(
                        prompt_text=prompt,
                        api_key=st.session_state.api_key,
                        aspect=aspect_ratio,
                        style=style
                    )
                    
                    if result and "imageUrl" in result:
                        # Get image from URL
                        image_content = download_image(result["imageUrl"])
                        
                        if image_content:
                            # Store image in session state
                            st.session_state.generated_image = image_content
                            st.session_state.image_url = result["imageUrl"]
                            st.session_state.api_response = result
                            st.experimental_rerun()
                    else:
                        st.error("Failed to generate image. Please check your API key and try again.")
        
        # Option to change API key
        if st.button("Change API Key"):
            st.session_state.step = "api_key"
            st.experimental_rerun()
    
    with right_col:
        st.subheader("Generated Image")
        
        # Show generated image if available
        if st.session_state.generated_image:
            image = Image.open(io.BytesIO(st.session_state.generated_image))
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
            st.text_input("Image URL:", value=st.session_state.image_url)
            
            # Display JSON response for debugging
            with st.expander("API Response Details"):
                st.json(st.session_state.api_response)
        else:
            st.info("Your generated image will appear here. Enter a prompt on the left and click 'Generate Image'.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Napkin AI")

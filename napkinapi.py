import streamlit as st
import requests
import time
import io
from PIL import Image

st.set_page_config(page_title="Napkin AI - Minimal App", layout="wide")
st.title("Napkin AI - Minimal App")

# API Key input
api_key = st.text_input("Enter your Napkin AI API Key:", type="password")

col1, col2 = st.columns(2)

with col1:
    # Simple prompt input
    prompt = st.text_area("Enter your prompt:", height=150)
    
    # Simple style selector
    style = st.selectbox(
        "Select Style:", 
        [
            "CDQPRVVJCSTPRBBCD5Q6AWR",  # Vibrant Strokes
            "realistic",
            "cinematic",
            "anime",
            "digital_art"
        ],
        index=0
    )
    
    # Dimensions
    width = st.number_input("Width:", min_value=256, max_value=1024, value=512)
    height = st.number_input("Height:", min_value=256, max_value=1024, value=512)
    
    # Generate button
    if st.button("Generate Image"):
        if not api_key:
            st.error("Please enter your API key.")
        elif not prompt:
            st.error("Please enter a prompt.")
        else:
            with st.spinner("Generating image..."):
                try:
                    # Step 1: Submit request
                    url = "https://api.napkin.ai/v1/visual"
                    
                    payload = {
                        "format": "svg",
                        "content": prompt,
                        "language": "en-US",
                        "style_id": style,
                        "number_of_visuals": 1,
                        "transparent_background": False,
                        "inverted_color": False,
                        "width": width,
                        "height": height
                    }
                    
                    headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {api_key.strip()}'
                    }
                    
                    st.write("Sending request to API...")
                    response = requests.post(url, json=payload, headers=headers)
                    
                    if response.status_code != 200 and response.status_code != 201:
                        st.error(f"API Error: {response.status_code} - {response.text}")
                    else:
                        result = response.json()
                        st.write("Initial request successful!")
                        
                        # Step 2: Check status
                        if 'request_id' in result:
                            request_id = result['request_id']
                            st.write(f"Request ID: {request_id}")
                            
                            status_url = f"https://api.napkin.ai/v1/visual/{request_id}/status"
                            status_headers = {
                                'Accept': 'application/json',
                                'Authorization': f'Bearer {api_key.strip()}'
                            }
                            
                            file_id = None
                            max_attempts = 10
                            for attempt in range(max_attempts):
                                st.write(f"Checking status (attempt {attempt+1}/{max_attempts})...")
                                
                                status_response = requests.get(status_url, headers=status_headers)
                                if status_response.status_code != 200:
                                    st.error(f"Status check error: {status_response.status_code} - {status_response.text}")
                                    break
                                
                                status_data = status_response.json()
                                st.write(f"Status: {status_data.get('status', 'unknown')}")
                                
                                if status_data.get('status') == 'completed':
                                    files = status_data.get('files', [])
                                    if files:
                                        file_id = files[0].get('id')
                                        st.write(f"File ID: {file_id}")
                                        break
                                    else:
                                        st.error("No files found in completed status.")
                                        break
                                
                                time.sleep(2)
                            
                            # Step 3: Get the image
                            if file_id:
                                image_url = f"https://api.napkin.ai/v1/visual/{request_id}/file/{file_id}"
                                image_headers = {
                                    'Accept': 'image/svg+xml',
                                    'Authorization': f'Bearer {api_key.strip()}'
                                }
                                
                                st.write("Fetching image...")
                                image_response = requests.get(image_url, headers=image_headers)
                                
                                if image_response.status_code != 200:
                                    st.error(f"Image fetch error: {image_response.status_code} - {image_response.text}")
                                else:
                                    st.session_state.image_data = image_response.content
                                    st.session_state.image_url = image_url
                                    st.success("Image generated successfully!")
                            else:
                                st.error("Failed to get file ID or image generation timed out.")
                        else:
                            st.error("No request ID in response.")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with col2:
    st.subheader("Generated Image")
    
    if 'image_data' in st.session_state:
        # For SVG images
        svg_data = st.session_state.image_data.decode('utf-8')
        st.components.v1.html(svg_data, height=500)
        
        # Download button
        st.download_button(
            label="Download SVG",
            data=st.session_state.image_data,
            file_name="napkin_ai_image.svg",
            mime="image/svg+xml"
        )
    else:
        st.info("Your generated image will appear here.")

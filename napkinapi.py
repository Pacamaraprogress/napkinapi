import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="Napkin AI - Comprehensive Debug", layout="wide")
st.title("Napkin AI - Comprehensive API Debug")

# API Key input
api_key = st.text_input("Enter your Napkin AI API Key:", type="password")

# Create tabs for different tests
tab1, tab2, tab3 = st.tabs(["Create Visual", "Check Status", "Custom Test"])

with tab1:
    st.header("Test Create Visual Request")
    
    endpoint = st.selectbox(
        "Select Endpoint", 
        [
            "https://api.napkin.ai/api/create-visual-request",
            "https://api.napkin.ai/v1/visual"
        ],
        index=0
    )
    
    prompt = st.text_input("Prompt:", value="Test prompt for API debugging")
    
    col1, col2 = st.columns(2)
    with col1:
        width = st.number_input("Width:", min_value=256, max_value=1024, value=800)
    with col2:
        height = st.number_input("Height:", min_value=256, max_value=1024, value=600)
    
    aspect_ratio = f"{width}x{height}"
    
    style_id = st.text_input("Style ID:", value="CDQPRVVJCSTPRBBCD5Q6AWR")
    
    # Format selector
    format_type = st.radio(
        "Request Format:",
        ["Format 1: prompt/aspectRatio", "Format 2: content/width/height"],
        index=0
    )
    
    if st.button("Test Create Request"):
        if not api_key:
            st.error("Please enter your API key.")
        else:
            with st.spinner("Testing create visual request..."):
                try:
                    # Set up headers
                    headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {api_key.strip()}'
                    }
                    
                    # Set up payload based on selected format
                    if format_type == "Format 1: prompt/aspectRatio":
                        payload = {
                            "prompt": prompt,
                            "aspectRatio": aspect_ratio,
                            "style_id": style_id
                        }
                    else:
                        payload = {
                            "format": "svg",
                            "content": prompt,
                            "language": "en-US",
                            "style_id": style_id,
                            "number_of_visuals": 1,
                            "transparent_background": False,
                            "inverted_color": False,
                            "width": width,
                            "height": height
                        }
                    
                    # Display request details
                    st.subheader("Request Details:")
                    st.write(f"Endpoint: {endpoint}")
                    st.write("Headers:")
                    st.json(headers)
                    st.write("Payload:")
                    st.json(payload)
                    
                    # Make the request
                    response = requests.post(endpoint, headers=headers, json=payload)
                    
                    # Display response details
                    st.subheader("Response Status Code:")
                    st.write(response.status_code)
                    
                    st.subheader("Response Headers:")
                    st.json(dict(response.headers))
                    
                    st.subheader("Response Text:")
                    st.code(response.text)
                    
                    # Try to parse as JSON
                    try:
                        response_json = response.json()
                        st.subheader("Response JSON (parsed):")
                        st.json(response_json)
                        
                        # Store request ID if available
                        if 'request_id' in response_json:
                            st.success(f"Request ID found: {response_json['request_id']}")
                            st.session_state.request_id = response_json['request_id']
                        elif 'id' in response_json:
                            st.success(f"ID found: {response_json['id']}")
                            st.session_state.request_id = response_json['id']
                        elif 'requestId' in response_json:
                            st.success(f"Request ID found: {response_json['requestId']}")
                            st.session_state.request_id = response_json['requestId']
                        else:
                            st.warning("No request ID found in response.")
                    except:
                        st.error("Could not parse response as JSON.")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.header("Check Request Status")
    
    status_endpoint = st.selectbox(
        "Select Status Endpoint", 
        [
            "https://api.napkin.ai/api/get-visual-request-status",
            "https://api.napkin.ai/v1/visual/{request_id}/status"
        ],
        index=0
    )
    
    # Get request ID from previous tab or allow manual entry
    if 'request_id' in st.session_state:
        default_request_id = st.session_state.request_id
    else:
        default_request_id = ""
    
    request_id = st.text_input("Request ID:", value=default_request_id)
    
    if st.button("Check Status"):
        if not api_key:
            st.error("Please enter your API key.")
        elif not request_id:
            st.error("Please enter a request ID.")
        else:
            with st.spinner("Checking request status..."):
                try:
                    # Set up headers
                    headers = {
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {api_key.strip()}'
                    }
                    
                    # Format the endpoint URL if needed
                    if "{request_id}" in status_endpoint:
                        formatted_endpoint = status_endpoint.replace("{request_id}", request_id)
                    else:
                        formatted_endpoint = status_endpoint
                        # Add request ID as query parameter or in the body based on endpoint
                        if status_endpoint == "https://api.napkin.ai/api/get-visual-request-status":
                            formatted_endpoint = f"{status_endpoint}?requestId={request_id}"
                    
                    # Display request details
                    st.subheader("Request Details:")
                    st.write(f"Endpoint: {formatted_endpoint}")
                    st.write("Headers:")
                    st.json(headers)
                    
                    # Make the request
                    response = requests.get(formatted_endpoint, headers=headers)
                    
                    # Display response details
                    st.subheader("Response Status Code:")
                    st.write(response.status_code)
                    
                    st.subheader("Response Headers:")
                    st.json(dict(response.headers))
                    
                    st.subheader("Response Text:")
                    st.code(response.text)
                    
                    # Try to parse as JSON
                    try:
                        response_json = response.json()
                        st.subheader("Response JSON (parsed):")
                        st.json(response_json)
                        
                        # Check for image URL or file ID
                        if 'imageUrl' in response_json:
                            st.success(f"Image URL found: {response_json['imageUrl']}")
                            st.session_state.image_url = response_json['imageUrl']
                        elif 'files' in response_json and response_json['files']:
                            st.success(f"File ID found: {response_json['files'][0]['id']}")
                            st.session_state.file_id = response_json['files'][0]['id']
                    except:
                        st.error("Could not parse response as JSON.")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab3:
    st.header("Custom API Test")
    
    custom_endpoint = st.text_input("Custom Endpoint:", value="https://api.napkin.ai/api/create-visual-request")
    
    # Method selector
    method = st.radio("HTTP Method:", ["GET", "POST"], index=1)
    
    # Custom headers and payload
    custom_headers = st.text_area("Headers (JSON format):", value='''{
  "Content-Type": "application/json",
  "Accept": "application/json",
  "Authorization": "Bearer YOUR_API_KEY"
}''')
    
    custom_payload = st.text_area("Payload (JSON format):", value='''{
  "prompt": "Test prompt",
  "aspectRatio": "800x600",
  "style_id": "CDQPRVVJCSTPRBBCD5Q6AWR"
}''')
    
    if st.button("Send Custom Request"):
        if not api_key:
            st.error("Please enter your API key.")
        else:
            with st.spinner("Sending custom request..."):
                try:
                    # Parse and prepare headers
                    try:
                        headers = json.loads(custom_headers)
                        # Replace placeholder with actual API key
                        if "Authorization" in headers and "YOUR_API_KEY" in headers["Authorization"]:
                            headers["Authorization"] = headers["Authorization"].replace("YOUR_API_KEY", api_key.strip())
                    except:
                        st.error("Invalid JSON in headers.")
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key.strip()}"
                        }
                    
                    # Parse and prepare payload
                    try:
                        payload = json.loads(custom_payload)
                    except:
                        st.error("Invalid JSON in payload.")
                        payload = {}
                    
                    # Display request details
                    st.subheader("Request Details:")
                    st.write(f"Endpoint: {custom_endpoint}")
                    st.write(f"Method: {method}")
                    st.write("Headers:")
                    st.json(headers)
                    st.write("Payload:")
                    st.json(payload)
                    
                    # Make the request
                    if method == "GET":
                        response = requests.get(custom_endpoint, headers=headers, params=payload)
                    else:  # POST
                        response = requests.post(custom_endpoint, headers=headers, json=payload)
                    
                    # Display response details
                    st.subheader("Response Status Code:")
                    st.write(response.status_code)
                    
                    st.subheader("Response Headers:")
                    st.json(dict(response.headers))
                    
                    st.subheader("Response Text:")
                    st.code(response.text)
                    
                    # Try to parse as JSON
                    try:
                        response_json = response.json()
                        st.subheader("Response JSON (parsed):")
                        st.json(response_json)
                    except:
                        st.error("Could not parse response as JSON.")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Additional information
st.markdown("---")
st.subheader("API Documentation and Resources")
st.markdown("""
- Status endpoint: https://api.napkin.ai/api/get-visual-request-status
- Create request endpoint: https://api.napkin.ai/api/create-visual-request
- V1 endpoint: https://api.napkin.ai/v1/visual
""")

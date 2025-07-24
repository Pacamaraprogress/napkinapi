# --- REVISED generate_image FUNCTION ---
def generate_image(prompt_text, api_key, aspect, style, auth_format, visual_type=None, background_color=None, color_theme=None):
    """
    Calls the Napkin AI API to generate an image.
    This function now accepts all parameters from the UI and handles different auth formats.
    """
    url = "https://api.napkin.ai/api/v1/create-visual-request"

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

    headers = {"Content-Type": "application/json"}
    if auth_format == "Bearer Token":
        headers["Authorization"] = f"Bearer {api_key}"
    elif auth_format == "API Key Header":
        headers["X-API-Key"] = api_key # This is a likely candidate
    elif auth_format == "Raw Key":
        headers["NAPKIN-ACCOUNT-API-KEY"] = api_key # Custom header possibility

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error(f"API Error: 401 Unauthorized. The API key was rejected with the '{auth_format}' format. Please try a different auth format.")
            st.warning("Raw Error Message from Server:")
            # --- THIS IS THE FIX ---
            # Use st.text or st.code to display the raw server response, not st.json
            st.code(e.response.text, language=None)
        else:
            st.error(f"API Error: {str(e)}")
            st.code(f"Response Body: {e.response.text}", language=None)
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: Could not connect to the API. {str(e)}")
        return None

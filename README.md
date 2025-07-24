# Napkin AI Image Generator

![Napkin AI](https://img.shields.io/badge/Powered%20by-Napkin%20AI-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![Python](https://img.shields.io/badge/Python-3.7+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A Streamlit web application that interfaces with the Napkin AI API to generate images from text prompts. This app provides a user-friendly interface for creating AI-generated visuals with customizable styles, dimensions, and visual characteristics.

![App Screenshot](https://via.placeholder.com/800x450.png?text=Napkin+AI+Image+Generator+Screenshot)

## Features

- **User-friendly Interface**: Simple, step-by-step flow from API key to image generation
- **Extensive Style Options**: Access to all official Napkin AI styles with detailed descriptions
- **Advanced Customization**: Control image dimensions, background colors, and visual themes
- **Visual Type Guidance**: Specify the type of visual you want (charts, diagrams, flowcharts, etc.)
- **Image Download**: Easily download generated images in PNG format
- **Secure API Handling**: API keys are securely handled and not stored in the repository

## Demo

(Add a GIF or video of the app in action once deployed)

## Installation

### Prerequisites

- Python 3.7 or higher
- Napkin AI API key ([Get yours here](https://napkin.ai))
- Git (for cloning the repository)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/napkin-ai-streamlit.git
   cd napkin-ai-streamlit
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** (optional - for storing your API key):
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your Napkin AI API key.

## Usage

1. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Access the web interface**:
   Open your browser and go to `http://localhost:8501`

3. **Using the app**:
   - Enter your Napkin AI API key when prompted
   - Type your image prompt in the text area
   - Customize settings in the Advanced Options section if desired
   - Click "Generate Image" to create your visual
   - Download the generated image using the download button

## App Flow

1. **API Key Entry**:
   - Securely enter your Napkin AI API key
   - The key is stored only in your session and never logged or saved

2. **Prompt & Options**:
   - Enter text prompts on the left side
   - Customize dimensions, style, visual type, and colors

3. **Image Display**:
   - Generated images appear on the right side
   - Download images, view API response details, or generate new images

## Available Styles

The app includes all official Napkin AI styles categorized as:

- **Colorful Styles**: Vibrant Strokes, Glowful Breeze, Bold Canvas, etc.
- **Casual Styles**: Carefree Mist, Lively Layers
- **Hand-drawn Styles**: Artistic Flair, Sketch Notes
- **Formal Styles**: Elegant Outline, Subtle Accent, Monochrome Pro, etc.
- **Monochrome Styles**: Minimal Contrast, Silver Beam
- **Classic Art Styles**: Realistic, Cinematic, Anime, Digital Art, etc.

## Deployment Options

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Add your API key as a secret in the Streamlit Cloud settings

### Heroku

1. Create a `Procfile` with:
   ```
   web: streamlit run app.py
   ```
2. Add your API key as a Heroku config var
3. Deploy using the Heroku CLI or GitHub integration

### Other Platforms

The app can be deployed on any platform that supports Python applications, including:
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service
- Digital Ocean App Platform

## Security Considerations

- **API Key Security**: Never commit your API key to the repository
- **Environment Variables**: Use environment variables or secrets management for deployment
- **HTTPS**: Always use HTTPS in production to protect API key transmission

## Project Structure

```
napkin-ai-streamlit/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example           # Template for environment variables
├── .gitignore             # Git ignore file
├── README.md              # This file
└── assets/                # Images and other static assets
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Napkin AI](https://napkin.ai) for providing the image generation API
- [Streamlit](https://streamlit.io) for the web app framework
- All contributors and users of this application

## Contact

If you have any questions or feedback, please open an issue on this repository or reach out to [your contact information].

---

Made with ❤️ by [your name]

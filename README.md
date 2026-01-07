# Amazon Polly TTS Converter 🗣️

A lightweight, engineer-friendly tool to convert text into high-quality speech (MP3) using Amazon Polly's Neural engine. Built with Streamlit and Python.

## Features

- **Neural TTS**: Uses Amazon Polly's Neural engine for natural-sounding speech.
- **Dynamic Voice Fetching**: Automatically loads available English (US/UK) voices from your AWS account.
- **Secure Configuration**: Uses environment variables for credentials.
- **Instant Playback & Download**: Listen immediately or download the `.mp3` file.

## Prerequisites

- **Python 3.9+**
- **AWS Account** with basic permissions for Polly (`AmazonPollyFullAccess`).

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd voxify
```

### 2. Create a Virtual Environment (Recommended)
This keeps dependencies isolated.
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration (Crucial Step)
You need AWS credentials to run this app.

1.  **Duplicate the example config**:
    ```bash
    cp .env.example .env
    # Or manually rename a copy of .env.example to .env
    ```

2.  **Get your AWS Keys**:
    - Log in to the [AWS Console](https://console.aws.amazon.com/).
    - Go to **IAM** > **Users** > **Create user**.
    - Attach the `AmazonPollyFullAccess` policy directly.
    - Go to the **Security credentials** tab for that user.
    - Create an **Access Key** (select "Local code").
    - **COPY** the `Access Key ID` and `Secret Access Key`.

3.  **Update `.env`**:
    Open the `.env` file and paste your keys:
    ```ini
    AWS_ACCESS_KEY_ID=AKIA...
    AWS_SECRET_ACCESS_KEY=wJal...
    AWS_REGION=us-east-1
    ```

## Usage

Run the application locally:
```bash
streamlit run app.py
```
The app will open automatically at `http://localhost:8501`.

## Deployment

Since this is a standard Streamlit app, it can be easily deployed to:

- **Streamlit Community Cloud**:
    1. Push this code to GitHub.
    2. Connect your repo on Streamlit Cloud.
    3. In the "Advanced Settings" of setup, add your secrets (`AWS_ACCESS_KEY_ID`, etc.) exactly as they appear in your `.env`.

- **Docker / Custom Server**:
    Ensure the environment variables are exposed to the container/process.

## Structure

- `app.py`: Main application logic.
- `.env`: (Ignored by Git) Stores your private local secrets.
- `requirements.txt`: Python dependencies.

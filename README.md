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

## Docker Usage 🐳

You can run this application entirely inside a Docker container, avoiding any local Python setup.

### 1. Prerequisites
- **Docker Desktop**: Download and install from [docker.com](https://www.docker.com/products/docker-desktop/).
- Ensure your `.env` file is configured with your AWS keys (see "Configuration" above).

### 2. Build the Image
Open a terminal in the project folder and run:
```bash
docker build -t voxify-app .
```

### 3. Run the Container
We use `--env-file` to safely pass your AWS credentials into the container without hardcoding them.
```bash
docker run -p 8501:8501 --env-file .env voxify-app
```

The app will start at `http://localhost:8501`.

### 4. Stop the Container
To stop the app, press `Ctrl+C` in the terminal, or manage it via the Docker Desktop dashboard.

## Deployment

Since this is a standard Streamlit app, it can be easily deployed to:

- **Streamlit Community Cloud**:
    1. Push this code to GitHub.
    2. Connect your repo on Streamlit Cloud.
    3. In the "Advanced Settings" of setup, add your secrets (`AWS_ACCESS_KEY_ID`, etc.) exactly as they appear in your `.env`.

- **Cloud Container Services (AWS ECS, Google Cloud Run)**:
    - Build the Docker image.
    - Push it to a container registry (ECR/GCR).
    - Deploy ensuring environment variables (`AWS_ACCESS_KEY_ID`, etc.) are set in the cloud service's configuration.

## Structure

- `app.py`: Main application logic.
- `Dockerfile`: Instructions for building the Docker image.
- `.dockerignore`: Files to exclude from the Docker build (e.g., secrets, local envs).
- `.env`: (Ignored by Git) Stores your private local secrets.
- `requirements.txt`: Python dependencies.

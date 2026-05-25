# LINE Growth Chatbot

This project aims to create a LINE chatbot in Python that simulates growth and learning through user interactions, without relying on paid Large Language Model (LLM) APIs. The bot will develop a knowledge base, memory system, and emotional model over time, making its responses increasingly personalized and complex.

## Features

- **Autonomous Learning System**: Builds a knowledge base, memory, and emotional model through user conversations.
- **Conversational Generation**: Combines rule-based responses with a memory growth system, utilizing a local small model.
- **Growth Progression**: Evolves from simple to complex conversations, remembers past interactions, and exhibits emotional changes.
- **Free Deployment**: Designed for deployment on free platforms like Railway or Render.

## Technical Stack

- Python
- LINE Messaging API SDK
- Local data storage for knowledge and memory (e.g., SQLite or JSON files)
- Simple rule-based or small local model for dialogue generation

## Project Structure

```
line-growth-bot/
├── app.py
├── bot.py
├── config.py
├── requirements.txt
├── memory.json
└── README.md
```

- `app.py`: The main application file, handling LINE webhook events and integrating with the bot logic.
- `bot.py`: Contains the core logic of the growth bot, including knowledge base, memory, emotion model, and response generation.
- `config.py`: Stores configuration variables such as LINE Channel Access Token and Channel Secret.
- `requirements.txt`: Lists all Python dependencies required for the project.
- `memory.json`: A simple JSON file to store the bot's memory, knowledge, and emotional state.
- `README.md`: Project documentation.

## Deployment Guide

This section provides step-by-step instructions for deploying your LINE Growth Chatbot to free platforms like Railway or Render.

### General Steps

1.  **Prepare your code**: Ensure your project is ready for deployment. This typically involves having a `requirements.txt` file, a `Procfile` (for some platforms), and your application code.
2.  **Version Control**: Push your code to a Git repository (e.g., GitHub, GitLab, Bitbucket). This is essential for most modern deployment platforms.
3.  **Platform Configuration**: Configure environment variables on your chosen platform (e.g., `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_CHANNEL_SECRET`).
4.  **Build and Deploy**: The platform will automatically build and deploy your application.
5.  **Webhook Setup**: Once deployed, you will get a public URL. You need to set this URL as your webhook endpoint in the LINE Developers Console.

### Deployment to Railway

Railway is a modern infrastructure platform that allows you to deploy applications quickly. It offers a free tier for small projects.

1.  **Sign up for Railway**: Go to [Railway.app](https://railway.app/) and sign up using your GitHub account.
2.  **Create a New Project**: Click on "New Project" and then "Deploy from Git Repo".
3.  **Connect GitHub**: Authorize Railway to access your GitHub repositories and select the repository containing your `line-growth-bot` project.
4.  **Configure Environment Variables**: In your Railway project settings, navigate to the "Variables" tab. Add the following environment variables:
    -   `LINE_CHANNEL_ACCESS_TOKEN`: Your LINE Channel Access Token.
    -   `LINE_CHANNEL_SECRET`: Your LINE Channel Secret.
    -   `PORT`: `5000` (or any port you configure in `app.py`).
5.  **Deploy**: Railway will automatically detect your `Procfile` and `requirements.txt` and deploy your Flask application. The build logs will show the progress.
6.  **Get Public URL**: Once deployed, go to the "Settings" tab of your service and find the "Domains" section. Copy the generated public URL.

### Deployment to Render

Render is a unified platform to build and run all your apps and websites with automatic deploys from Git. It also has a free tier.

1.  **Sign up for Render**: Go to [Render.com](https://render.com/) and sign up using your GitHub or GitLab account.
2.  **New Web Service**: From your dashboard, click "New" -> "Web Service".
3.  **Connect Git Repository**: Connect your GitHub/GitLab account and select the repository for your `line-growth-bot` project.
4.  **Configure Service**: 
    -   **Name**: Choose a unique name for your service.
    -   **Region**: Select a region close to your users.
    -   **Branch**: `main` (or your default branch).
    -   **Root Directory**: `/` (or the directory containing your `app.py` if it's a subdirectory).
    -   **Runtime**: `Python 3`.
    -   **Build Command**: `pip install -r requirements.txt`.
    -   **Start Command**: `python app.py`.
    -   **Instance Type**: `Free`.
5.  **Add Environment Variables**: In the "Advanced" section, add environment variables:
    -   `LINE_CHANNEL_ACCESS_TOKEN`: Your LINE Channel Access Token.
    -   `LINE_CHANNEL_SECRET`: Your LINE Channel Secret.
    -   `PORT`: `10000` (Render typically uses port 10000 for web services, ensure your `app.py` is configured to use `os.environ.get("PORT", 5000)`).
6.  **Create Web Service**: Click "Create Web Service". Render will build and deploy your application.
7.  **Get Public URL**: Once deployed, the dashboard will show your service's public URL.

## LINE Developers Setup

To integrate your chatbot with LINE, you need to set up a LINE Developers account and create a Messaging API channel.

1.  **Create a LINE Developer Account**: If you don't have one, go to [LINE Developers Console](https://developers.line.biz/console/) and create an account.
2.  **Create a New Provider**: In the console, navigate to "Providers" and click "Create new provider". Give it a suitable name.
3.  **Create a New Channel**: Under your provider, click "Create a new channel" and choose "Messaging API".
4.  **Fill in Channel Details**: Provide the necessary information for your channel (App name, App description, Category, Subcategory, Email address, Privacy Policy URL, Terms of Use URL). Agree to the LINE Official Account Terms of Use and click "Create".
5.  **Get Channel Access Token and Channel Secret**: Once your channel is created, go to its settings page.
    -   **Channel Secret**: You'll find this under the "Basic settings" tab.
    -   **Channel Access Token**: Go to the "Messaging API" tab. Issue a new channel access token (long-lived) if one doesn't exist, or copy the existing one.
    -   **Important**: Keep these values secure. You will use them as environment variables (`LINE_CHANNEL_ACCESS_TOKEN` and `LINE_CHANNEL_SECRET`) in your deployment.
6.  **Enable Webhook**: In the "Messaging API" tab, scroll down to the "Webhook settings" section.
    -   **Webhook URL**: Enter the public URL of your deployed application followed by `/callback` (e.g., `https://your-app-name.railway.app/callback` or `https://your-app-name.onrender.com/callback`).
    -   **Enable Webhook**: Make sure the "Use webhook" toggle is turned ON.
    -   **Verify Webhook**: Click the "Verify" button to ensure LINE can reach your webhook endpoint. This step can only be completed after your application is deployed and running.
7.  **Disable Auto-reply messages and Greeting messages**: To prevent the LINE Official Account from sending default messages, go to the "LINE Official Account Manager" (accessible from the LINE Developers Console) for your channel. Under "Settings" -> "Response settings", turn off "Response mode" or set "Webhook" to ON and disable "Greeting messages" and "Auto-reply messages".

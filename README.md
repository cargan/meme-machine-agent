🤖 Meme Machine Agent

A smart AI assistant that turns your ideas into hilarious memes instantly. This project was built to demonstrate how local Artificial Intelligence can be used for creative and fun automation.
🌟 What is it?

Imagine you have a funny thought but don't want to spend 10 minutes looking for the right meme template and using a photo editor. Meme Machine Agent does the heavy lifting for you:

    You give a topic (e.g., "Monday mornings" or "Learning to code").

    The AI analyzes the mood and picks the perfect background from the 100 most popular memes on the internet.

    The Agent writes the joke, formats it, and saves a ready-to-use image to your computer.

🚀 How to use it

    Run the script in your terminal.

    Type in any topic you want.

    Wait a few seconds for the AI to "think."

    Find your brand new meme in the /memes folder!

🛠️ Technical Deep Dive (For Developers)

This project is built using a modern Agentic Workflow that connects local Large Language Models (LLMs) with external web APIs.
Architecture:

    Brain (LLM): Powered by Ollama (Llama 3) running locally. It handles the reasoning, template selection, and caption generation.

    Strict Output Control: Uses Ollama's JSON mode to ensure the model output is always a valid data structure, preventing parsing errors.

    Dynamic Discovery: Instead of hardcoded IDs, the script fetches the top 100 trending templates from the Imgflip API in real-time.

    Environment Safety: Sensitive credentials (API keys) are managed via Environment Variables (os.getenv), ensuring no secrets are leaked in the source code.

Tech Stack:

    Python 3.x (Primary Logic)

    Requests (API communication)

    Neovim (Development Environment)


Created as a weekend engineering challenge to master AI-Human interaction loops.

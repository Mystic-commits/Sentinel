# Sentinel
**Your Local-First AI Digital Janitor**

Sentinel is a safe, local-first AI agent designed to clean and organize your computer (Downloads, Desktop, etc.) with a premium, futuristic dashboard.

## 🚀 Core Goals
- **Safety First**: No direct filesystem operations by AI. All actions are planned, reviewed, and executed deterministically.
- **Privacy**, **Local Control**: Uses local LLMs (Ollama) and runs entirely on your machine.
- **Undoable**: Every operation is logged and reversible.

## 📂 Repository Structure
- **[sentinel-core](./sentinel-core)**: The brain. Pure Python logic, Planner, Scanner, Safety, and Executor.
- **[sentinel-api](./sentinel-api)**: FastAPI server providing local APIs and WebSockets.
- **[sentinel-cli](./sentinel-cli)**: Typer-based CLI for headless interaction.
- **[sentinel-web](./sentinel-web)**: Next.js + Tailwind Dashboard.
- **[sentinel-desktop](./sentinel-desktop)**: Tauri wrapper for native experience.

## 🛠 Tech Stack
- **Engine**: Python 3.11+
- **Frontend**: Next.js, Tailwind, Framer Motion
- **Desktop**: Tauri (Rust)
- **Model**: Ollama (Llama 3, Mistral, etc.)
- **DB**: SQLite

## ⚡ Getting Started
*(Coming Soon - see `docs/development.md`)*

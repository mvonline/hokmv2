# Hokm v2 - Complete Running Instructions

This project consists of three main components:
1.  **Machine Learning (ML)**: Python-based environment and training.
2.  **Backend**: Rust-based game server.
3.  **Frontend**: React + Pixi.js web interface.

Follow these steps to set up and run the entire system.

## 1. Machine Learning Setup

The ML component uses PettingZoo and Ray RLlib to train AI agents.

### Prerequisites
- Python 3.9+
- pip

### Steps
1.  Navigate to the project root.
2.  Install dependencies:
    ```bash
    pip install -r ml/requirements.txt
    ```
3.  Run the training script:
    ```bash
    python3 ml/train.py
    ```
    *This will run a self-play training session and save checkpoints to `./results`.*

## 2. Backend Setup

The backend is a high-performance game server written in Rust.

### Prerequisites
- Rust (latest stable)
- Cargo

### Steps
1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Run the server:
    ```bash
    cargo run
    ```
    *The server will start listening on `http://127.0.0.1:8080`.*

## 3. Frontend Setup

The frontend is a modern web application using React and Pixi.js for rendering.

### Prerequisites
- Node.js (v16+)
- npm

### Steps
1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
4.  Open your browser and go to the URL shown in the terminal (usually `http://localhost:5173`).

## How to Play

1.  Ensure the **Backend** is running (`cargo run`).
2.  Open the **Frontend** in your browser.
3.  You will see the game board rendered with Pixi.js.
4.  The frontend automatically connects to the backend via WebSocket.
5.  Click on the cards in your hand (bottom of the screen) to play them.
    *   *Note: Currently, the backend is in a "stub" mode where it receives moves but doesn't fully simulate the game logic yet. You will see "Playing card" logs in the browser console.*

## Troubleshooting

-   **Frontend Build Errors**: If you encounter errors related to `@pixi/react`, ensure you are using the compatible versions specified in `package.json` (Pixi.js v7).
-   **Connection Failed**: If the frontend says "Disconnected", make sure the backend is running on port 8080.

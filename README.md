# Parallax File Finder

A local file search agent that uses the model running on [Parallax](https://github.com/GradientHQ/parallax) for semantic refinement.

## Overview

This application indexes text files in a chosen directory and allows you to search them.
1.  **Basic Search**: Filters files using keyword matching.
2.  **AI-Assisted Refinement**: Sends candidates to the Parallax runtime to be re-ranked by the active model.

## Prerequisites

-   Python 3.8+
-   wxPython
-   Parallax

## Installation

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Parallax Setup

This application requires a running Parallax instance.

1.  **Start the Scheduler**:
    Run the Parallax scheduler with your desired model.
    ```bash
    parallax run -m {model-name} -n {number-of-worker-nodes}
    # Example:
    # parallax run -m Qwen/Qwen3-0.6B -n 1
    ```

2.  **Join Worker Nodes**:
    In a separate terminal (or on other machines), join the cluster:
    ```bash
    parallax join
    # Or if remote: parallax join -s {scheduler-address}
    ```

3.  **Verify Endpoint**:
    Ensure the scheduler is reachable at:
    `http://localhost:3001/v1/chat/completions`

## Usage

1.  Start the application:
    ```bash
    python ui_main.py
    ```
2.  **Browse** to select a folder containing text files.
3.  Click **INDEX** to scan the files.
4.  Type a query and click **SEARCH**.

## Configuration

Settings in `config.py`:
-   `PARALLAX_API_URL`: URL of the Parallax scheduler (default: `http://localhost:3001/v1/chat/completions`).
-   `TOP_K_CANDIDATES`: Number of files to send to Parallax for re-ranking.

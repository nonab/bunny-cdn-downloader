# Bunny CDN DRM Video Downloader

A command-line tool to automatically download DRM-protected videos hosted on Bunny CDN.

This script automates the process by visiting a webpage, extracting the `.m3u8` playlist and the decryption key, and then uses `N_M3U8DL-RE` to download the video.

## Features

-   **Automatic Extraction**: Automatically finds the encryption key and playlist URL from a given webpage.
-   **Download**: The primary function is to download videos directly.
-   **Print-Only Mode**: Includes a `--print-only` flag to generate and display download commands without executing them (a "dry run").
-   **Batch Processing**: Accepts a single URL or a text file containing multiple URLs (one per line).
-   **Prerequisite Check**: Verifies that the `N_M3U8DL-RE` downloader is installed and accessible before starting.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.7+**
2.  **pip** (Python's package installer)
3.  **N\_M3U8DL-RE**: This is the core downloader used by the script.
    -   Download the latest release from the [N\_m3u8DL-RE GitHub Releases page](https://github.com/nilaoda/N_m3u8DL-RE/releases).
    -   Place the executable in a folder that is included in your system's **PATH** environment variable.
4.  **FFmpeg**: `N_M3U8DL-RE` requires FFmpeg to merge the downloaded video and audio segments into a single file.
    -   Download the latest version from the official [FFmpeg website](https://ffmpeg.org/download.html).
    -   Like the downloader, ensure the `ffmpeg` executable is also placed in a folder that is part of your system's **PATH**.
       

## Installation

1.  **Clone or Download**:
    Save the Python script (`bunny_grabber.py`) into a new folder.

2.  **Navigate to the project directory**:
    ```sh
    cd bunny-drm-downloader
    ```

3.  **Create a Virtual Environment (Recommended)**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Python Packages**:
    Install the required packages using pip.
    ```sh
    pip install playwright
    ```

5.  **Install Chromium**:
    Playwright requires a browser binary to operate. Run the following command to install firefox.
    ```sh
    playwright install firefox
    ```

## Usage

The script can be run with a single URL or a path to a text file.

### To Download Videos (Default)

-   **From a single URL**:
    ```sh
    python bunny_grabber.py "https://iframe.mediadelivery.net/embed/00000/00000000-0000-0000-0000-000000000000)"
    ```

-   **From a file containing multiple URLs**:
    Create a file (e.g., `links.txt`) with one URL on each line.
    ```sh
    python bunny_grabber.py links.txt
    ```

### To Print Commands Without Downloading (`--print-only`)

-   **From a single URL**:
    ```sh
    python bunny_key_grabber.py --print-only "https://iframe.mediadelivery.net/embed/00000/00000000-0000-0000-0000-000000000000)"
    ```

-   **From a file**:
    ```sh
    python bunny_key_grabber.py --print-only links.txt
    ```

## Disclaimer

This tool is intended for personal and educational use only. Please respect the copyright and terms of service of the content you are accessing. The user is solely responsible for their actions when using this script.

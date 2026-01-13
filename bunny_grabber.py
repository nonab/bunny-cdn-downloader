import sys
import re
import subprocess
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

def load_urls(file):
    path = Path(file)
    if not path.exists():
        print(f"Error: File '{file}' not found.")
        sys.exit(1)
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]

def sanitize_filename(title):
    return re.sub(r'[\\/:"*?<>|]+', '_', title)

print_only_mode = "--print-only" in sys.argv
if print_only_mode:
    sys.argv.remove("--print-only")

if len(sys.argv) < 2:
    print("Usage: python bunny_key_grabber.py [--print-only] <filename_or_url>")
    sys.exit(1)

if not print_only_mode and not shutil.which("N_M3U8DL-RE"):
    print("N_M3U8DL-RE not found, make sure you get it from https://github.com/nilaoda/N_m3u8DL-RE/releases and add to PATH and re-execute the script")
    sys.exit(1)

input_arg = sys.argv[1]
urls = []

if input_arg.lower().startswith(("http://", "https://")):
    urls = [input_arg]
else:
    print(f"Detected file mode: {input_arg}")
    urls = load_urls(input_arg)

commands_list = []

get_media_playlist_js = """
async (masterPlaylistUrl) => {
    const response = await fetch(masterPlaylistUrl);
    const masterPlaylistContent = await response.text();

    let mediaPlaylistUrl = null;
    for (const line of masterPlaylistContent.trim().split('\\n')) {
        if (line.trim() && !line.startsWith("#")) {
            // Construct full URL from relative path
            mediaPlaylistUrl = new URL(line.trim(), masterPlaylistUrl).href;
            break;
        }
    }

    const mediaResponse = await fetch(mediaPlaylistUrl);
    return await mediaResponse.text();
}
"""

print("--- Starting URL Processing ---")
with sync_playwright() as p:
    browser = p.firefox.launch(
        headless=True,
        firefox_user_prefs={"media.volume_scale": "0.0"}
    )
    context = browser.new_context()
    
    for page_url in urls:
        print("\n==============================")
        print("Processing:", page_url)
        page = context.new_page()
        state = {"hex_key": None, "playlist_url": None, "title": None}
        cmd = None

        def on_response(response):
            if "b-cdn.net" in response.url and "/key/" in response.url:
                try: state["hex_key"] = response.body().hex()
                except Exception: pass

        def on_request(request):
            if "b-cdn.net" in request.url and request.url.endswith("playlist.m3u8"):
                state["playlist_url"] = request.url

        page.on("response", on_response)
        page.on("request", on_request)

        try:
            page.goto(page_url, wait_until="domcontentloaded", timeout=60000, referer="https://iframe.mediadelivery.net/")
            page_title = page.title()
            if page_title and page_title.strip():
                state["title"] = sanitize_filename(page_title)
        except Exception as e:
            print(f"Error loading page: {e}")
            page.close()
            continue

        max_wait, elapsed = 15, 0
        while not state["playlist_url"] and elapsed < max_wait:
            page.wait_for_timeout(500)
            elapsed += 0.5

        if not state["playlist_url"]:
            print("Could not find a master playlist (.m3u8) on this page.")
            page.close()
            continue
        
        try:
            print("Found master playlist. Fetching content to check for DRM...")
            media_playlist_content = page.evaluate(get_media_playlist_js, state["playlist_url"])
        except Exception as e:
            print(f"Failed to fetch or parse playlist content: {e}")
            page.close()
            continue
            
        is_drm = "#EXT-X-KEY" in media_playlist_content
        
        cmd_parts = ["N_M3U8DL-RE"]
        if state["title"]:
            cmd_parts.append(f'--save-name "{state["title"]}"')
        cmd_parts.append("-sv best")

        if is_drm:
            print("DRM protected video detected. Waiting for key...")
            key_wait_max, key_elapsed = 5, 0
            while not state["hex_key"] and key_elapsed < key_wait_max:
                page.wait_for_timeout(500)
                key_elapsed += 0.5
            
            if state["hex_key"]:
                print("Encryption key found!")
                cmd_parts.append(f'--custom-hls-key "{state["hex_key"]}"')
                cmd_parts.append(f'"{state["playlist_url"]}"')
                cmd_parts.append('--header "Referer: https://iframe.mediadelivery.net/"')
                cmd = " ".join(cmd_parts)
            else:
                print("Error: Found DRM playlist but could not capture the encryption key.")
        else:
            print("Non-DRM video detected.")
            cmd_parts.append(f'"{state["playlist_url"]}"')
            cmd_parts.append('--header "Referer: https://iframe.mediadelivery.net/"')
            cmd = " ".join(cmd_parts)
        
        if cmd:
            commands_list.append(cmd)
            print("Command generated successfully.")
        
        page.close()
    browser.close()
print("\n--- URL Processing Finished ---")

if commands_list:
    print("\n==============================")
    if print_only_mode:
        print("--- Print-Only Mode ---")
        print("The following commands would be executed:")
        for c in commands_list:
            print(c)
    else:
        print(f"Found {len(commands_list)} video(s) to download.")
        for i, c in enumerate(commands_list, 1):
            print(f"\n--- Starting download {i}/{len(commands_list)} ---")
            print(f"Command: {c}")
            try:
                subprocess.run(c, shell=True, check=True)
                print("Download completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error during download: {e}")

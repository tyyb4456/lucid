"""
LUCID Web & Network Tools - Browser control, downloads, network operations
"""

from langchain_core.tools import tool
import webbrowser
import urllib.parse
import requests
from pathlib import Path
import subprocess

@tool
def search_web(query: str, engine: str = "google") -> str:
    """
    Search the web and open results in default browser.
    
    Args:
        query: Search query
        engine: 'google', 'bing', 'duckduckgo', 'youtube'
    """
    try:
        engines = {
            "google": "https://www.google.com/search?q=",
            "bing": "https://www.bing.com/search?q=",
            "duckduckgo": "https://duckduckgo.com/?q=",
            "youtube": "https://www.youtube.com/results?search_query="
        }
        
        base_url = engines.get(engine.lower(), engines["google"])
        encoded_query = urllib.parse.quote(query)
        url = f"{base_url}{encoded_query}"
        
        webbrowser.open(url)
        return f"Searching {engine} for: {query}"
    
    except Exception as e:
        return f"Error searching web: {e}"


@tool
def open_url(url: str, new_tab: bool = True) -> str:
    """
    Open any URL in the default browser.
    
    Args:
        url: URL to open
        new_tab: Open in new tab (True) or new window (False)
    """
    try:
        # Add https:// if not present
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        if new_tab:
            webbrowser.open_new_tab(url)
        else:
            webbrowser.open_new(url)
        
        return f"Opened: {url}"
    
    except Exception as e:
        return f"Error opening URL: {e}"


@tool
def download_file(url: str, save_path: str = "") -> str:
    """
    Download a file from a URL.
    
    Args:
        url: URL to download from
        save_path: Where to save (default: Downloads folder)
    """
    try:
        if not save_path:
            downloads = Path.home() / "Downloads"
            filename = url.split('/')[-1] or "download"
            save_path = str(downloads / filename)
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        save_path_obj = Path(save_path)
        save_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size_mb = save_path_obj.stat().st_size / (1024 * 1024)
        return f"Downloaded {file_size_mb:.2f}MB to: {save_path}"
    
    except requests.exceptions.RequestException as e:
        return f"Download failed: {e}"
    except Exception as e:
        return f"Error downloading file: {e}"


@tool
def get_webpage_content(url: str) -> str:
    """
    Fetch and return the text content of a webpage.
    
    Args:
        url: URL to fetch
    """
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Simple text extraction (would need BeautifulSoup for better parsing)
        content = response.text
        
        if len(content) > 5000:
            return f"Webpage content (first 5000 chars):\n{content[:5000]}\n... [truncated]"
        
        return f"Webpage content:\n{content}"
    
    except Exception as e:
        return f"Error fetching webpage: {e}"


@tool
def check_internet_connection() -> str:
    """Check if internet connection is active."""
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            return "✅ Internet connection active"
        else:
            return f"⚠️ Connection issue - Status code: {response.status_code}"
    except Exception as e:
        return f"❌ No internet connection: {e}"


@tool
def get_public_ip() -> str:
    """Get the public IP address."""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        ip = response.json()['ip']
        return f"Public IP address: {ip}"
    except Exception as e:
        return f"Error getting IP: {e}"


@tool
def ping_host(host: str) -> str:
    """
    Ping a host to check connectivity.
    
    Args:
        host: Hostname or IP address
    """
    try:
        result = subprocess.run(
            ["ping", "-n", "4", host],
            capture_output=True,
            text=True,
            timeout=10
        )
        return f"Ping result:\n{result.stdout}"
    except subprocess.TimeoutExpired:
        return f"Ping timeout for {host}"
    except Exception as e:
        return f"Error pinging host: {e}"


@tool
def open_maps_location(location: str) -> str:
    """
    Open Google Maps for a specific location.
    
    Args:
        location: Address or place name
    """
    try:
        encoded = urllib.parse.quote(location)
        url = f"https://www.google.com/maps/search/{encoded}"
        webbrowser.open(url)
        return f"Opened Google Maps for: {location}"
    except Exception as e:
        return f"Error opening maps: {e}"
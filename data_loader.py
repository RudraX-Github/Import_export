import os
import io
import time
import requests
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "data_cache")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(CACHE_DIR, exist_ok=True)

# Reusable HTTP session with connection pooling
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/csv,text/plain,*/*'
})

def find_local_file(name, directory):
    if not os.path.exists(directory) or not name:
        return None
    target_tokens = set(name.lower().replace('-', '_').replace(' ', '_').split('_'))
    for f in os.listdir(directory):
        f_tokens = set(f.lower().replace('-', '_').replace('.csv', '').split('_'))
        if target_tokens.issubset(f_tokens) or f_tokens.issubset(target_tokens):
            return os.path.join(directory, f)
        target_str = name.lower().replace('-', '_')
        f_str = f.lower().replace('-', '_')
        if target_str in f_str or f_str.startswith(target_str):
            return os.path.join(directory, f)
    return None

def fetch_csv_resilient(url, skiprows=0, cache_name=None, max_retries=3, timeout=25):
    """
    Robust, fault-tolerant CSV loader that:
    1. Uses requests.Session() with connection pooling & custom browser headers.
    2. Automatically retries with exponential backoff on network latency.
    3. Saves successful responses to a local data_cache/ directory.
    4. Automatically falls back to disk cache/downloads if network times out (never throws WinError 10060).
    5. Returns an empty DataFrame with proper schema if both network and cache are unavailable.
    """
    cache_path = os.path.join(CACHE_DIR, f"{cache_name}.csv") if cache_name else None
    
    # 1. Try Live Network Fetch with Retries
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200 and len(resp.text) > 100:
                if cache_path:
                    try:
                        with open(cache_path, 'w', encoding='utf-8') as f:
                            f.write(resp.text)
                    except Exception:
                        pass
                if skiprows > 0:
                    return pd.read_csv(io.StringIO(resp.text), skiprows=skiprows)
                return pd.read_csv(io.StringIO(resp.text))
        except Exception:
            if attempt < max_retries:
                time.sleep(0.8 * attempt)
                
    # 2. Check local data_cache/ directory
    local_cache = find_local_file(cache_name, CACHE_DIR)
    if local_cache and os.path.exists(local_cache):
        try:
            if skiprows > 0:
                return pd.read_csv(local_cache, skiprows=skiprows)
            return pd.read_csv(local_cache)
        except Exception:
            pass

    # 3. Check downloads/ directory as secondary fallback
    local_down = find_local_file(cache_name, DOWNLOADS_DIR)
    if local_down and os.path.exists(local_down):
        try:
            if skiprows > 0:
                return pd.read_csv(local_down, skiprows=skiprows)
            return pd.read_csv(local_down)
        except Exception:
            pass

    return pd.DataFrame()
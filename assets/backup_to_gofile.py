#!/usr/bin/env python3
"""Backup videos to gofile.io"""
import os
import subprocess
import json

def upload_to_gofile(file_path, server=None):
    """Upload file to gofile.io"""
    if server is None:
        # Get available servers
        result = subprocess.run(
            ['curl', '-s', 'https://api.gofile.io/servers'],
            capture_output=True, text=True, timeout=30
        )
        servers = json.loads(result.stdout).get('data', {}).get('servers', [])
        server = servers[0]['name'] if servers else 'store-eu-par-4'
    
    print(f"Uploading to {server}...")
    cmd = f'curl -s --max-time 600 -F "file=@{file_path}" "https://{server}.gofile.io/contents/uploadfile"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    
    try:
        data = json.loads(result.stdout)
        return data.get('data', {}).get('downloadPage', '')
    except:
        return None

def main():
    assets_dir = "/workspaces/hermes-agent/assets"
    
    # Find final videos
    videos = []
    for f in os.listdir(assets_dir):
        if f.endswith('.mp4') and 'final' in f:
            videos.append(os.path.join(assets_dir, f))
    
    print(f"Found {len(videos)} videos to backup")
    print("="*60)
    
    for video_path in sorted(videos):
        file_name = os.path.basename(video_path)
        file_size = os.path.getsize(video_path) / 1024 / 1024
        print(f"\n[{file_name}] {file_size:.1f} MB")
        
        url = upload_to_gofile(video_path)
        if url:
            print(f"  ✓ https://gofile.io/d/{url.split('/')[-1]}")
        else:
            print("  ✗ Upload failed")
    
    print("\n" + "="*60)
    print("Backup complete!")

if __name__ == "__main__":
    main()

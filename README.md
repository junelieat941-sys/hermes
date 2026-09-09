# Triptych Video Pipeline

Automated pipeline for generating triptych (three-panel) videos with covers and uploading to Google Drive.

## Quick Start

### Generate a Video

```bash
cd /workspaces/hermes/hermes

python3 auto_triptych.py <video_file> \
    --cover-title 流光 \
    --cover-en RADIANCE \
    --cover-kicker "COOL · DARK VIBES" \
    --cover-tag "冷冽暗夜 · 光影流动" \
    --cover-foot "from the dark" \
    --theme cool \
    --upload
```

### Upload to Google Drive

```bash
python3 backup_to_gdrive.py
```

Or upload a single file:
```bash
python3 backup_to_gdrive.py --file <filename.mp4>
```

## Scripts Reference

### auto_triptych.py - Video Generator
Generates triptych videos with:
- 3-panel layout (640×1080 each → 1920×1080 total)
- Cover image generation
- BGM integration with fade-in/fade-out
- Automatic gofile.io upload

Options:
- `--cover-title` Chinese title (2 characters recommended)
- `--cover-en` English subtitle
- `--cover-kicker` Top badge text
- `--cover-tag` Tagline in Chinese
- `--cover-foot` Footer text in English
- `--theme` Theme: `cool` (default) or `warm`
- `--hero-at` Frame timestamp for cover (default: 0.0)
- `--intro` Title card duration (default: 3s)
- `--fade-in` / `--fade-out` Video fade durations
- `--afade-in` / `--afade-out` Audio fade durations
- `--upload` Upload to gofile after generation
- `--keep-temp` Keep intermediate files for debugging

### make_series_cover.py - Cover Generator
Generates stylish 1280×720 covers from video frames.

```bash
python3 make_series_cover.py \
    --hero <video_or_image> \
    --at 0.0 \
    --theme cool \
    --title 流光 \
    --en RADIANCE \
    --kicker "COOL · DARK VIBES" \
    --tag "冷冽暗夜 · 光影流动" \
    --foot "from the dark"
```

### backup_to_gdrive.py - Google Drive Backup
Uploads all `*_final.mp4` videos to Google Drive.

```bash
python3 backup_to_gdrive.py          # Upload all finals
python3 backup_to_gdrive.py --file v1_final.mp4  # Single file
python3 backup_to_gdrive.py --dry-run           # List without uploading
python3 backup_to_gdrive.py --auth              # Re-authorize Google
```

## Setup

### Google Drive OAuth (One-time)

1. Download client secret JSON from Google Cloud Console
2. Save to `~/.gdrive_client_secret.json`
3. Run authorization:
   ```bash
   python3 backup_to_gdrive.py --auth
   ```
4. Open the URL in browser, grant permission, paste the code

### Required Files

- Source videos: `/workspaces/hermes/hermes/*.mp4`
- BGM: `/workspaces/hermes/hermes/bgm/Runway-Dreams*.mp3`
- Fonts: NotoSansCJK-Bold, NotoSerifCJK-Bold (already installed)

## Output Locations

- Videos: `/workspaces/hermes/hermes/out/`
- Covers: `/workspaces/hermes/hermes/covers/`
- Google Drive: https://drive.google.com/drive/my-drive

## Video Index

All 28 videos are backed up to Google Drive:

| Video | Size | Drive Link |
|-------|------|------------|
| v1_final.mp4 | 226.7 MB | [Link](https://drive.google.com/file/d/1OMBXafLti5JB-ywJVaGF_hE3Cdbjr0AP/view) |
| v3_final.mp4 | 238.7 MB | [Link](https://drive.google.com/file/d/1Oi4bk8IpQHMUkvXEk8N6gHJJpMO7m7ll/view) |
| v4_final.mp4 | 132.2 MB | [Link](https://drive.google.com/file/d/1bWe2iQeMCjjq1dFDrDeDKOD0GcS3rKzN/view) |
| v5_final.mp4 | 88.6 MB | [Link](https://drive.google.com/file/d/12eyocci39Ixaf1zdiMj9WHRQVb0Drsn9/view) |
| v6_final.mp4 | 119.5 MB | [Link](https://drive.google.com/file/d/1wdGUwycsW06V23pfsQOPd6_BYoUKXTru/view) |
| v7_final.mp4 | 78.8 MB | [Link](https://drive.google.com/file/d/1o8SyE6UtjCLlwJ7U2pamRkQJuE_8Rxg_/view) |
| v8_final.mp4 | 118.6 MB | [Link](https://drive.google.com/file/d/17LOCEU1atWuGeHME_zZEumSu-vQ4hHHX/view) |
| v9_final.mp4 | 88.7 MB | [Link](https://drive.google.com/file/d/1ceu-ozoHcfLL5OwYrE99VYkndiyTYPEt/view) |
| v10_final.mp4 | 105.4 MB | [Link](https://drive.google.com/file/d/1cL1E32Bv3ScUWqvLtcmBcc5Ze2dEb5g6/view) |
| v11_final.mp4 | 224.8 MB | [Link](https://drive.google.com/file/d/1CvYGQ-poEsNDy5HGNjIyOtgruyjtQjHS/view) |
| v12_final.mp4 | 84.5 MB | [Link](https://drive.google.com/file/d/10cs3-y62fIne5zu4OiV29_enCnn_OYmW/view) |
| v13_final.mp4 | 119.3 MB | [Link](https://drive.google.com/file/d/1ciRP6m2YJdQlEu6bLxvVuHHAsG-iWohc/view) |
| v14_final.mp4 | 112.9 MB | [Link](https://drive.google.com/file/d/1lMQ1TF4H5e6dpjztTlh74ZAYQq5srWp3/view) |
| v15_final.mp4 | 84.6 MB | [Link](https://drive.google.com/file/d/16-UfZku0GiaTyoyPmczD8UW_9oNXs-EL/view) |
| v22_final.mp4 | 135.0 MB | [Link](https://drive.google.com/file/d/1DG9pTkEWnyATF2jnfGBnv35YTxOoE6F_/view) |
| v23_final.mp4 | 137.8 MB | [Link](https://drive.google.com/file/d/17Oqn2HUnNLZy6TpB2mGJ0H1mCbkOUkOv/view) |
| v24_final.mp4 | 58.0 MB | [Link](https://drive.google.com/file/d/1VYYXx8dYTbmjFfZHtxtm4tgiudET1jIe/view) |
| v25_final.mp4 | 36.1 MB | [Link](https://drive.google.com/file/d/12A4q0U3YCrP-DmRgWKmTs1jRmuSdG_Eh/view) |
| v26_final.mp4 | 135.6 MB | [Link](https://drive.google.com/file/d/1UN01LKZlShLA-UjeyTUpmwk8SRuRIpCf/view) |
| v27_final.mp4 | 59.1 MB | [Link](https://drive.google.com/file/d/1rrjGKD6sDA7rpOlJ5DkI13PYG5Swsh4K/view) |
| v28_final.mp4 | 139.3 MB | [Link](https://drive.google.com/file/d/17u-yjUQi3wfR9FZ1Q7C_vBueNC-almjU/view) |
| t3_final.mp4 | 145.2 MB | [Link](https://drive.google.com/file/d/1tNKdwhLlQ24mtxBUe0ayl0hRUne844uZ/view) |
| triptych_cover_final.mp4 | 136.2 MB | [Link](https://drive.google.com/file/d/10LDKYW077U3iGLihluuKUbFYJBkGXn0P/view) |
| triptych_loop_final.mp4 | 112.0 MB | [Link](https://drive.google.com/file/d/1ij4XrO4H3U_fZ6JlRfx_LVImfFEu8A1l/view) |
| triptych_loop2_final.mp4 | 86.9 MB | [Link](https://drive.google.com/file/d/1r9-VIwZ-CIkIU_3WaT293FG5mn8uIwsK/view) |
| triptych_loop3_final.mp4 | 105.3 MB | [Link](https://drive.google.com/file/d/19soLI-i-wVrpWRZiD-9A01rTITx_43gd/view) |
| video_new_final.mp4 | 139.3 MB | [Link](https://drive.google.com/file/d/1MtTjroZ8e2wDZq_yXT852ePZ6d4ivUdA/view) |
| 勾勒_final.mp4 | 150.7 MB | [Link](https://drive.google.com/file/d/1z6w7GqJpa9hHMDcce0R2zsi_FRtL5bhB/view) |

## Troubleshooting

### Google Drive API 403 Error
The Google Drive API must be enabled for your project:
1. Go to https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=818870591593
2. Click "Enable"

### App Not Verified Error
Add your email as a test user:
1. Go to https://console.cloud.google.com/auth/audience
2. Find "Hermes Backup"
3. Click "Add users"
4. Add: minsmithat941@gmail.com

### Token Refresh Failed
Re-authorize:
```bash
python3 backup_to_gdrive.py --auth
```

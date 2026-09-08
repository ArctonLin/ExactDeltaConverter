# Exact Delta Converter
 
<h2 align="center"><span style="color:red">⚠️ Notice: DO NOT LISTEN ExactDelta WHILE DRIVING. ⚠️</span></h2>

Please use stereo headphone and turn off any audio enhancment such like Dolby Atmos.
 
A desktop application that allows you to independently shift the frequency (Hz) of the left and right audio channels, with additional features for stereo downmixing. 

## Requirements
- Python 3.7+
- This application requires `ffmpeg` to process MP3 files.

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install FFmpeg (Required for MP3 Support on Windows):
   - Download the FFmpeg release build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or use `winget`:
     ```bash
     winget install "FFmpeg (Essentials Build)"
     ```
   - Make sure FFmpeg is added to your system PATH.

## Usage

Run the application:
```bash
python main.py
```

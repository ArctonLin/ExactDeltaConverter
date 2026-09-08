# Exact Delta Converter

<h2 align="center">⚠️ Notice: DO NOT LISTEN TO ExactDelta WHILE DRIVING. ⚠️</h2>

**Please use stereo headphones and turn off any audio enhancements such as Dolby Atmos.**

## Overview

Exact Delta Converter is a unique binaural beat generator that **does not add any artificial tones or background sounds** to your audio. Instead, it directly alters the frequency spectrum of the original audio file. 

By independently shifting the frequencies of the left and right channels by a specific target Hz, it creates a binaural beat using the music itself. This means you can listen to your favorite songs while experiencing the benefits of binaural beats, whether for deep sleep, relaxation, or peak focus.

## How it Works

The application achieves this pure frequency shift using the **Hilbert Transform**:
1. It computes the analytic signal of the audio using `scipy.signal.hilbert`.
2. It shifts the entire frequency spectrum uniformly without affecting the playback speed or tempo.
3. This creates a precise Hz difference (Delta) between the left and right ears, forming the binaural beat.

## Quick Start

### 1. Install Requirements
Ensure you have Python 3.7+ installed.

**Install Python packages:**
```bash
pip install -r requirements.txt
```

**Install FFmpeg (Windows):**
*(Required for MP3 support)*
```bash
conda install ffmpeg
```

### 2. Run the App
```bash
python main.py
```

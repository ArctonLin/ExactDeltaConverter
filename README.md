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

## Brainwave Frequencies & Effects

Binaural beats utilize a concept called **brainwave entrainment**. When you hear two slightly different frequencies in each ear, your brain perceives a third tone (the binaural beat) that equals the difference between the two. Your brainwaves naturally begin to synchronize with this difference frequency, allowing you to guide your mental state.

Based on the presets available in the application, here are the different brainwave spectrums and their associated effects:

- **Delta (0.5Hz - 4.0Hz)**
  - **Effects**: Deep Sleep, Healing, Loss of bodily awareness.
  - **App Presets**: `0.5Hz`, `2.0Hz`, `3.2Hz`

- **Theta (4.0Hz - 8.0Hz)**
  - **Effects**: Light Sleep, Deep Meditation, Creativity, REM sleep.
  - **App Presets**: `4.0Hz`

- **Alpha (8.0Hz - 12.0Hz)**
  - **Effects**: Relaxed, Awake, Light Meditation, Calm focus.
  - **App Presets**: `11.76Hz`

- **Beta (12.0Hz - 30.0Hz)**
  - **Effects**: Active, Awake, Thinking, Problem-solving, Concentration.
  - **App Presets**: `15.68Hz`

- **Gamma (30.0Hz - 100.0Hz)**
  - **Effects**: High/Peak Focus, Cognitive enhancement, Heightened perception.
  - **App Presets**: `40.0Hz`

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

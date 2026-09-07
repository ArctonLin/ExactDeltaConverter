import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import numpy as np
import scipy.signal
import os
import sys
from pathlib import Path

# Add conda environment Library/bin to PATH so pydub can find ffmpeg
env_path = Path(sys.executable).parent
library_bin = env_path / "Library" / "bin"
if library_bin.exists():
    os.environ["PATH"] += os.pathsep + str(library_bin)

from pydub import AudioSegment

class ExactDeltaConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exact Delta Converter")
        self.root.geometry("600x500")

        self.files_to_process = []
        
        self.create_widgets()

    def create_widgets(self):
        # Settings Frame
        settings_frame = tk.LabelFrame(self.root, text="Settings", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Target Hz
        tk.Label(settings_frame, text="Target Hz:").grid(row=0, column=0, sticky="w", pady=5)
        self.target_hz_var = tk.StringVar(value="4.0 (Theta)")
        self.target_hz_presets = [
            "0.5 (Delta)",
            "2.0 (Delta)",
            "3.2 (Delta)",
            "4.0 (Theta)", 
            "11.76 (Alpha)", 
            "15.68 (Beta)"
        ]
        self.target_hz_cb = ttk.Combobox(settings_frame, textvariable=self.target_hz_var, values=self.target_hz_presets, width=15)
        self.target_hz_cb.grid(row=0, column=1, sticky="w", pady=5)

        # Delta Mode
        tk.Label(settings_frame, text="Delta Mode:").grid(row=1, column=0, sticky="w", pady=5)
        self.delta_mode_var = tk.StringVar()
        self.delta_modes = [
            "left keep + right rising",
            "left keep + right decreasing",
            "left rising + right keep",
            "left decreasing + right keep",
            "left rising half + right decreasing half",
            "left decreasing half + right rising half"
        ]
        self.delta_mode_cb = ttk.Combobox(settings_frame, textvariable=self.delta_mode_var, values=self.delta_modes, state="readonly", width=40)
        self.delta_mode_cb.current(4) # default to left rising half + right decreasing half
        self.delta_mode_cb.grid(row=1, column=1, sticky="w", pady=5)

        # Stereo Percentage
        tk.Label(settings_frame, text="Stereo Percentage:").grid(row=2, column=0, sticky="w", pady=5)
        self.stereo_pct_var = tk.StringVar()
        self.stereo_pcts = ["100%", "75%", "50%", "25%", "0%"]
        self.stereo_pct_cb = ttk.Combobox(settings_frame, textvariable=self.stereo_pct_var, values=self.stereo_pcts, state="readonly", width=10)
        self.stereo_pct_cb.current(0) # default to 100%
        self.stereo_pct_cb.grid(row=2, column=1, sticky="w", pady=5)

        # File List Frame
        list_frame = tk.LabelFrame(self.root, text="Files", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.listbox = tk.Listbox(list_frame, selectmode="extended")
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(btn_frame, text="Add Folder", command=self.add_folder).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Convert All", command=self.convert_all, bg="#4CAF50", fg="white").pack(side="right", padx=5)
        tk.Button(btn_frame, text="Convert One", command=self.convert_one, bg="#2196F3", fg="white").pack(side="right", padx=5)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, anchor="w").pack(fill="x", padx=10, pady=5)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=(("Audio Files", "*.mp3 *.wav *.flac *.ogg"), ("All Files", "*.*"))
        )
        for f in files:
            if f not in self.files_to_process:
                self.files_to_process.append(f)
                self.listbox.insert(tk.END, f)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            valid_exts = ['.mp3', '.wav', '.flac', '.ogg']
            for root, _, files in os.walk(folder):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in valid_exts):
                        full_path = os.path.join(root, file)
                        # Replace backslashes for consistency
                        full_path = full_path.replace("\\", "/")
                        if full_path not in self.files_to_process:
                            self.files_to_process.append(full_path)
                            self.listbox.insert(tk.END, full_path)

    def remove_selected(self):
        selected_indices = list(self.listbox.curselection())
        selected_indices.reverse()
        for idx in selected_indices:
            self.listbox.delete(idx)
            del self.files_to_process[idx]

    def convert_one(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a file to convert.")
            return
        
        file_to_convert = self.files_to_process[selected_indices[0]]
        self.start_conversion([file_to_convert])

    def convert_all(self):
        if not self.files_to_process:
            messagebox.showwarning("Warning", "No files to convert.")
            return
        self.start_conversion(self.files_to_process)

    def start_conversion(self, file_list):
        # Disable buttons during processing
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(state="disabled")

        # Run in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self.process_files, args=(file_list,))
        thread.start()

    def process_files(self, file_list):
        target_hz = float(self.target_hz_var.get().split()[0])
        mode = self.delta_mode_var.get()
        stereo_pct_str = self.stereo_pct_var.get()
        stereo_pct = float(stereo_pct_str.replace('%', '')) / 100.0

        # Determine shifts and mode_code based on mode
        l_shift = 0.0
        r_shift = 0.0
        mode_code = "Unknown"
        if mode == "left keep + right rising":
            r_shift = target_hz
            mode_code = "LkRr"
        elif mode == "left keep + right decreasing":
            r_shift = -target_hz
            mode_code = "LkRd"
        elif mode == "left rising + right keep":
            l_shift = target_hz
            mode_code = "LrRk"
        elif mode == "left decreasing + right keep":
            l_shift = -target_hz
            mode_code = "LdRk"
        elif mode == "left rising half + right decreasing half":
            l_shift = target_hz / 2.0
            r_shift = -target_hz / 2.0
            mode_code = "LrRd"
        elif mode == "left decreasing half + right rising half":
            l_shift = -target_hz / 2.0
            r_shift = target_hz / 2.0
            mode_code = "LdRr"

        stereo_code = stereo_pct_str.replace('%', '')

        total = len(file_list)
        for i, file_path in enumerate(file_list):
            self.status_var.set(f"Processing ({i+1}/{total}): {os.path.basename(file_path)}")
            try:
                self.process_single_file(file_path, l_shift, r_shift, stereo_pct, mode_code, stereo_code, target_hz)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process {os.path.basename(file_path)}:\n{str(e)}\n\nMake sure ffmpeg is installed and added to PATH for MP3 support.")
                break

        self.status_var.set("Ready")
        
        # Re-enable buttons
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(state="normal")
        
        messagebox.showinfo("Done", "Conversion finished successfully!")

    def process_single_file(self, file_path, l_shift, r_shift, stereo_pct, mode_code, stereo_code, target_hz):
        # Load audio
        audio = AudioSegment.from_file(file_path)
        
        # Ensure stereo
        if audio.channels == 1:
            audio = AudioSegment.from_mono_audiosegments(audio, audio)
        elif audio.channels > 2:
            raise ValueError("Only mono and stereo files are supported.")

        sample_rate = audio.frame_rate
        
        # Convert to numpy float arrays
        samples = np.array(audio.get_array_of_samples())
        samples = samples.reshape((-1, 2))
        
        # Max value for 16-bit audio
        max_int_val = float(2**(audio.sample_width * 8 - 1))
        samples_float = samples.astype(np.float32) / max_int_val
        
        left = samples_float[:, 0]
        right = samples_float[:, 1]
        
        # Stereo percentage processing
        if stereo_pct < 1.0:
            mono_mix = (left + right) / 2.0
            left = left * stereo_pct + mono_mix * (1.0 - stereo_pct)
            right = right * stereo_pct + mono_mix * (1.0 - stereo_pct)
            
        # Frequency Shift (Hilbert Transform) using chunked processing to prevent memory limits
        import scipy.fft
        
        def shift_channel(channel_data, shift_hz, sr):
            if shift_hz == 0:
                return channel_data
            
            chunk_size = int(30.0 * sr) # 30 seconds
            pad_size = int(2.0 * sr) # 2 seconds padding for safety
            
            out_channel = np.zeros_like(channel_data)
            total_samples = len(channel_data)
            
            for start in range(0, total_samples, chunk_size):
                end = min(start + chunk_size, total_samples)
                
                pad_start = max(0, start - pad_size)
                pad_end = min(total_samples, end + pad_size)
                
                chunk_padded = channel_data[pad_start:pad_end]
                
                N = len(chunk_padded)
                fast_len = scipy.fft.next_fast_len(N)
                
                analytic = scipy.signal.hilbert(chunk_padded, N=fast_len)[:N]
                
                t = np.arange(pad_start, pad_end) / sr
                shifted = np.real(analytic * np.exp(2j * np.pi * shift_hz * t))
                
                valid_start = start - pad_start
                valid_end = valid_start + (end - start)
                
                out_channel[start:end] = shifted[valid_start:valid_end]
                
            return out_channel

        left = shift_channel(left, l_shift, sample_rate)
        right = shift_channel(right, r_shift, sample_rate)
            
        # Clipping protection: reduce overall volume if max amplitude > 1.0
        max_amp = max(np.max(np.abs(left)), np.max(np.abs(right)))
        if max_amp > 1.0:
            # Reduce volume so max amplitude becomes 0.99 to be safe
            scale = 0.99 / max_amp
            left = left * scale
            right = right * scale

        # Convert back to 16-bit PCM integer
        left_int = (left * (max_int_val - 1)).astype(np.int16)
        right_int = (right * (max_int_val - 1)).astype(np.int16)
        
        # Interleave channels
        out_samples = np.empty((len(left_int), 2), dtype=np.int16)
        out_samples[:, 0] = left_int
        out_samples[:, 1] = right_int
        
        out_audio = AudioSegment(
            out_samples.tobytes(),
            frame_rate=sample_rate,
            sample_width=2, # 16-bit
            channels=2
        )
        
        # Determine output path
        path_obj = Path(file_path)
        parent_dir = path_obj.parent
        new_dir_name = f"ExactDelta_{parent_dir.name}"
        
        # The output folder should be in the same parent directory as the original folder
        # So if original is MyMusic/file.flac, new is ExactDelta_MyMusic/ExactDelta_file.flac
        new_dir_path = parent_dir.parent / new_dir_name
        new_dir_path.mkdir(parents=True, exist_ok=True)
        
        hz_str = f"{target_hz}hz" if target_hz % 1 != 0 else f"{int(target_hz)}hz"
        new_filename = f"ExactDelta_{hz_str}_{mode_code}_{stereo_code}_{path_obj.name}"
        out_path = new_dir_path / new_filename
        
        # Export with same format
        ext = path_obj.suffix.lower().strip('.')
        if ext == '':
            ext = 'wav'
            
        # Pydub export
        if ext == 'mp3':
            out_audio.export(str(out_path), format=ext, bitrate="320k")
        else:
            out_audio.export(str(out_path), format=ext)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExactDeltaConverterApp(root)
    root.mainloop()

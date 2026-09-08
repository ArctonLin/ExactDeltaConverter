import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import numpy as np
import scipy.signal
import os
import sys
from pathlib import Path
from pydub import AudioSegment
import pydub

class ExactDeltaConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exact Delta Converter")
        self.root.geometry("800x650")
        self.root.minsize(800, 600)

        self.files_to_process = {}
        self.stop_requested = False
        
        self.create_widgets()

    def create_widgets(self):
        # Settings Frame
        settings_frame = tk.LabelFrame(self.root, text="Settings", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Target Hz
        tk.Label(settings_frame, text="Target Hz:").grid(row=0, column=0, sticky="w", pady=5)
        self.target_hz_var = tk.StringVar(value="4.0 (Theta 4hz-8hz - Light Sleep, Deep Meditation)")
        self.target_hz_presets = [
            "0.5 (Delta 0.5hz-4.0hz - Deep Sleep)",
            "2.0 (Delta 0.5hz-4.0hz - Deep Sleep)",
            "3.2 (Delta 0.5hz-4.0hz - Deep Sleep)",
            "4.0 (Theta 4hz-8hz - Light Sleep, Deep Meditation)", 
            "11.76 (Alpha 8hz-12hz - Relaxed, Awake, Light Meditation)", 
            "15.68 (Beta 12hz-30hz - Active, Awake, Thinking)",
            "40.0 (Gamma 30hz-100hz - High/Peak Focus)"
        ]
        self.target_hz_cb = ttk.Combobox(settings_frame, textvariable=self.target_hz_var, values=self.target_hz_presets, width=50)
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
        self.delta_mode_cb = ttk.Combobox(settings_frame, textvariable=self.delta_mode_var, values=self.delta_modes, state="readonly", width=50)
        self.delta_mode_cb.current(4) # default to left rising half + right decreasing half
        self.delta_mode_cb.grid(row=1, column=1, sticky="w", pady=5)

        # Stereo Percentage
        tk.Label(settings_frame, text="Stereo Percentage:").grid(row=2, column=0, sticky="w", pady=5)
        self.stereo_pct_var = tk.StringVar()
        self.stereo_pcts = ["100%", "75%", "50%", "25%", "0%"]
        self.stereo_pct_cb = ttk.Combobox(settings_frame, textvariable=self.stereo_pct_var, values=self.stereo_pcts, state="readonly", width=10)
        self.stereo_pct_cb.current(0) # default to 100%
        self.stereo_pct_cb.grid(row=2, column=1, sticky="w", pady=5)

        # Target Format
        tk.Label(settings_frame, text="Target Format:").grid(row=3, column=0, sticky="w", pady=5)
        self.target_format_var = tk.StringVar(value="Same")
        self.target_format_cb = ttk.Combobox(settings_frame, textvariable=self.target_format_var, values=["Same", "flac", "mp3", "wav"], state="readonly", width=10)
        self.target_format_cb.grid(row=3, column=1, sticky="w", pady=5)

        # Target Bitrate
        tk.Label(settings_frame, text="Target Bitrate:").grid(row=4, column=0, sticky="w", pady=5)
        self.target_bitrate_var = tk.StringVar(value="Same")
        self.target_bitrate_cb = ttk.Combobox(settings_frame, textvariable=self.target_bitrate_var, values=["Same", "64kbps", "128kbps", "256kbps", "320kbps"], state="readonly", width=10)
        self.target_bitrate_cb.grid(row=4, column=1, sticky="w", pady=5)

        # Max Threads
        tk.Label(settings_frame, text="Max Threads:").grid(row=5, column=0, sticky="w", pady=5)
        self.thread_count_var = tk.StringVar()
        cores = os.cpu_count()
        max_threads = cores if cores else 4
        self.thread_counts = [str(i) for i in range(1, max_threads + 1)]
        self.thread_count_cb = ttk.Combobox(settings_frame, textvariable=self.thread_count_var, values=self.thread_counts, state="readonly", width=10)
        default_threads = min(4, max_threads)
        self.thread_count_cb.set(str(default_threads))
        self.thread_count_cb.grid(row=5, column=1, sticky="w", pady=5)

        # File List Frame
        list_frame = tk.LabelFrame(self.root, text="Files", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ('status', 'filepath')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode="extended")
        self.tree.heading('status', text='Status')
        self.tree.column('status', width=100, anchor='w', stretch=tk.NO)
        self.tree.heading('filepath', text='File Path')
        self.tree.column('filepath', width=600, anchor='w', stretch=tk.YES)
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=scrollbar.set)

        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(btn_frame, text="Add Folder", command=self.add_folder).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Convert All", command=self.convert_all, bg="#4CAF50", fg="white").pack(side="right", padx=5)
        tk.Button(btn_frame, text="Convert One", command=self.convert_one, bg="#2196F3", fg="white").pack(side="right", padx=5)
        self.stop_button = tk.Button(btn_frame, text="Stop", command=self.stop_conversion, bg="#f44336", fg="white", state="disabled")
        self.stop_button.pack(side="right", padx=5)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, anchor="w").pack(fill="x", padx=10, pady=5)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=(("Audio Files", "*.m4a *.flac *.mp3 *.wav *.wma *.aac *.opus"), ("All Files", "*.*"))
        )
        for f in files:
            if f not in self.files_to_process.values():
                item_id = self.tree.insert('', tk.END, values=("Pending", f))
                self.files_to_process[item_id] = f

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            valid_exts = ['.m4a', '.flac', '.mp3', '.wav', '.wma', '.aac', '.opus']
            for root, _, files in os.walk(folder):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in valid_exts):
                        full_path = os.path.join(root, file)
                        # Replace backslashes for consistency
                        full_path = full_path.replace("\\", "/")
                        if full_path not in self.files_to_process.values():
                            item_id = self.tree.insert('', tk.END, values=("Pending", full_path))
                            self.files_to_process[item_id] = full_path

    def remove_selected(self):
        selected_items = self.tree.selection()
        for item_id in selected_items:
            self.tree.delete(item_id)
            if item_id in self.files_to_process:
                del self.files_to_process[item_id]

    def stop_conversion(self):
        self.stop_requested = True
        self.status_var.set("Stopping...")
        self.stop_button.config(state="disabled")

    def convert_one(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a file to convert.")
            return
        
        items_to_convert = {item_id: self.files_to_process[item_id] for item_id in selected_items}
        self.start_conversion(items_to_convert)

    def convert_all(self):
        if not self.files_to_process:
            messagebox.showwarning("Warning", "No files to convert.")
            return
        self.start_conversion(self.files_to_process)

    def start_conversion(self, file_list):
        self.stop_requested = False
        # Disable buttons during processing
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        if getattr(self, 'stop_button', None) and child == self.stop_button:
                            continue
                        child.config(state="disabled")
                        
        if hasattr(self, 'stop_button'):
            self.stop_button.config(state="normal")

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

        stereo_code = 'S'+stereo_pct_str.replace('%', '')

        items_to_convert = file_list
        total = len(items_to_convert)
        self.status_var.set(f"Processing 0/{total} files...")
        
        try:
            max_workers = int(self.thread_count_var.get())
        except ValueError:
            max_workers = 4

        last_out_dir = None
        completed_count = 0
        
        def update_status(item_id, file_path, status):
            self.root.after(0, lambda: self.tree.item(item_id, values=(status, file_path)))

        def task_runner(item_id, file_path):
            if self.stop_requested:
                update_status(item_id, file_path, "Cancelled")
                return None
                
            update_status(item_id, file_path, "Processing")
            try:
                status, out_dir = self.process_single_file(file_path, l_shift, r_shift, stereo_pct, mode_code, stereo_code, target_hz)
                if status == "SKIPPED":
                    update_status(item_id, file_path, "Skipped")
                else:
                    update_status(item_id, file_path, "Done")
                return out_dir
            except Exception as e:
                print(f"Error on {file_path}: {e}")
                update_status(item_id, file_path, "Error")
                return None

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for item_id, path in items_to_convert.items():
                futures[executor.submit(task_runner, item_id, path)] = (item_id, path)
                
            for future in concurrent.futures.as_completed(futures):
                completed_count += 1
                if self.stop_requested:
                    self.root.after(0, lambda c=completed_count: self.status_var.set(f"Stopping... {c}/{total} files processed/cancelled"))
                else:
                    self.root.after(0, lambda c=completed_count: self.status_var.set(f"Processing {c}/{total} files..."))
                res = future.result()
                if res:
                    last_out_dir = res

        self.root.after(0, lambda: self.status_var.set("Ready"))
        
        # Re-enable buttons safely
        def reenable():
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Button):
                            child.config(state="normal")
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state="disabled")
            
            if self.stop_requested:
                messagebox.showinfo("Stopped", "Conversion stopped by user.")
            else:
                messagebox.showinfo("Done", "Conversion finished successfully!")
            
            if last_out_dir and last_out_dir.exists():
                import sys
                import subprocess
                if os.name == 'nt':
                    os.startfile(str(last_out_dir))
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', str(last_out_dir)])
                else:
                    subprocess.Popen(['xdg-open', str(last_out_dir)])
                    
        self.root.after(0, reenable)

    def process_single_file(self, file_path, l_shift, r_shift, stereo_pct, mode_code, stereo_code, target_hz):
        # Determine output path first to allow skipping
        path_obj = Path(file_path)
        parent_dir = path_obj.parent
        
        hz_str = f"{target_hz}hz" if target_hz % 1 != 0 else f"{int(target_hz)}hz"
        new_dir_name = f"ExactDelta_{hz_str}_{mode_code}_{stereo_code}_{parent_dir.name}"
        new_dir_path = parent_dir.parent / new_dir_name
        
        ext = path_obj.suffix.lower().strip('.')
        if ext == '':
            ext = 'wav'
            
        target_format = self.target_format_var.get()
        if target_format == "Same":
            target_format = ext
            if ext in ["aac", "m4a", "wma", "opus"]:
                target_format = "mp3"
                
        new_filename = f"ExactDelta_{hz_str}_{mode_code}_{stereo_code}_{path_obj.stem}.{target_format}"
        out_path = new_dir_path / new_filename
        
        if out_path.exists():
            return "SKIPPED", new_dir_path

        new_dir_path.mkdir(parents=True, exist_ok=True)

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
        
        # Bitrate logic
        target_bitrate_str = getattr(self, 'target_bitrate_var', tk.StringVar(value="Same")).get()
        if target_bitrate_str == "Same":
            try:
                from pydub.utils import mediainfo
                info = mediainfo(str(path_obj))
                bit_rate = info.get('bit_rate')
                if bit_rate:
                    target_bitrate = str(int(int(bit_rate)/1000)) + "k"
                else:
                    target_bitrate = "320k"
            except Exception:
                target_bitrate = "320k"
        elif target_bitrate_str == "64kbps":
            target_bitrate = "64k"
        elif target_bitrate_str == "128kbps":
            target_bitrate = "128k"
        elif target_bitrate_str == "256kbps":
            target_bitrate = "256k"
        elif target_bitrate_str == "320kbps":
            target_bitrate = "320k"
        else:
            target_bitrate = "320k"

        # Pydub export
        if target_format in ['mp3', 'm4a', 'wma', 'aac', 'opus']:
            out_audio.export(str(out_path), format=target_format, bitrate=target_bitrate)
        else:
            out_audio.export(str(out_path), format=target_format)
            
        return "DONE", new_dir_path

import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = ExactDeltaConverterApp(root)
    root.mainloop()

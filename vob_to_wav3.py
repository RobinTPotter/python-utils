import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import re
import time
import sys

sys.stdout.flush()

# --- Configuration ---
MPLAYER_PATH = r"C:\Program Files\MPlayer-x86_64-r38188+g6e1903938b\mplayer.exe"
FFMPEG_PATH = r"C:\Program Files\ffmpeg-4.3.1-2020-09-21-full_build\bin\ffmpeg.exe"
DVD_DEVICE = "D:"

# --- Global Variable to Track Process ---
extract_proc = None  # Global variable to hold the extraction process

# --- Utilities ---
def format_seconds(sec):
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}"

def parse_mplayer_output(raw_output):
    decoded = raw_output.decode(errors='ignore')
    titles_match = re.search(r'ID_DVD_TITLES=(\d+)', decoded)
    num_titles = int(titles_match.group(1)) if titles_match else 0

    track_lengths = {}
    for line in decoded.splitlines():
        match = re.match(r'ID_DVD_TITLE_(\d+)_LENGTH=([\d\.]+)', line)
        if match:
            title_num = int(match.group(1))
            length_sec = float(match.group(2))
            track_lengths[title_num] = length_sec

    return num_titles, track_lengths

def get_dvd_info():
    try:
        proc = subprocess.Popen([
            MPLAYER_PATH, "-identify", "-dvd-device", DVD_DEVICE, "dvd://1"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(3)
        proc.kill()
        output, _ = proc.communicate(timeout=15)  # 15-second timeout
        return parse_mplayer_output(output)
    except subprocess.TimeoutExpired:
        proc.kill()
        return 0, {}
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read DVD info: {e}")
        return 0, {}

# --- GUI App ---
class DVDExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DVD Audio Extractor")
        self.track_vars = []
        self.track_labels = []
        self.track_lengths = []

        self.output_format = tk.StringVar(value="wav")
        self.output_folder = os.path.expanduser("~/Desktop")  # Default to Desktop

        self.extracting = False

        # Set minimum size for the window (minimum width = 200px, minimum height = 300px)
        self.root.minsize(200, 300)

        # UI elements
        self.scan_button = tk.Button(root, text="Scan DVD", command=self.scan_dvd)
        self.scan_button.pack(pady=5)

        self.track_frame = tk.Frame(root)
        self.track_frame.pack(padx=10, pady=5)

        self.select_all = tk.Button(root, text="Select All", command=self.select_all)
        self.select_all.pack(pady=5)

        self.select_none = tk.Button(root, text="Select None", command=self.select_none)
        self.select_none.pack(pady=5)

        format_frame = tk.Frame(root)
        format_frame.pack(pady=5)
        tk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT)
        tk.OptionMenu(format_frame, self.output_format, "wav", "mp3").pack(side=tk.LEFT)

        folder_button = tk.Button(root, text="Choose Output Folder", command=self.choose_output_folder)
        folder_button.pack(pady=5)

        self.extract_button = tk.Button(root, text="Extract Selected Tracks", command=self.extract_tracks, state=tk.DISABLED)
        self.extract_button.pack(pady=10)

        self.cancel_button = tk.Button(root, text="Cancel Extraction", command=self.cancel_extraction, state=tk.DISABLED)
        self.cancel_button.pack(pady=5)

        self.progress = tk.Label(root, text="")
        self.progress.pack(pady=5)

    def select_all(self):
        for v in self.track_vars:
            v.set(1)
        

    def select_none(self):
        for v in self.track_vars:
            v.set(0)
        


    def choose_output_folder(self):
        # Open file dialog with Desktop as default
        self.output_folder = filedialog.askdirectory(initialdir=self.output_folder, title="Select Output Folder")
        if self.output_folder:
            messagebox.showinfo("Folder Selected", f"Output will be saved to: {self.output_folder}")

    def scan_dvd(self):
        if self.extracting:
            messagebox.showinfo("Processing", "Extraction is already in progress.")
            return

        self.track_vars.clear()
        self.track_labels.clear()
        self.track_lengths.clear()
        for widget in self.track_frame.winfo_children():
            widget.destroy()

        self.scan_button.config(state=tk.DISABLED)  # Disable scan button during extraction
        self.extract_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

        num_titles, track_lengths = get_dvd_info()
        if num_titles == 0:
            messagebox.showinfo("No Titles", "No DVD titles found or scan timed out.")
            self.scan_button.config(state=tk.NORMAL)
            return

        for i in range(1, num_titles + 1):
            length = track_lengths.get(i, 0)
            label = f"Track {i} - {format_seconds(length)}"
            var = tk.IntVar(value=1)
            chk = tk.Checkbutton(self.track_frame, text=label, variable=var)
            chk.pack(anchor='w')
            self.track_vars.append(var)
            self.track_labels.append(label)
            self.track_lengths.append(length)

        self.scan_button.config(state=tk.NORMAL)  # Enable scan button after scan
        self.extract_button.config(state=tk.NORMAL)

    def extract_tracks(self):
        if not self.output_folder:
            messagebox.showinfo("No Output Folder", "Please select an output folder first.")
            return

        self.extracting = True
        self.scan_button.config(state=tk.DISABLED)  # Disable scan button during extraction
        self.extract_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        threading.Thread(target=self._extract_tracks).start()

    def cancel_extraction(self):
        global extract_proc  # Access the global extract_proc
        if extract_proc:
            extract_proc.kill()  # Kill the extraction process
            self.progress.config(text="Extraction cancelled.")
        else:
            self.progress.config(text="No extraction in progress.")
        
        self.extracting = False
        self.cancel_button.config(state=tk.DISABLED)
        self.extract_button.config(state=tk.NORMAL)
        self.scan_button.config(state=tk.NORMAL)

    def update_progress(self, message):
        # Update progress in the GUI thread
        self.progress.config(text=message)

    def _extract_tracks(self):
        global extract_proc  # Access the global extract_proc

        selected = [i+1 for i, var in enumerate(self.track_vars) if var.get() == 1]
        if not selected:
            messagebox.showinfo("No Selection", "Please select at least one track.")
            self.extracting = False
            self.cancel_button.config(state=tk.DISABLED)
            self.extract_button.config(state=tk.NORMAL)
            return

        for i in selected:
            length = self.track_lengths[i-1]

            if not self.extracting:
                break

            self.update_progress(f"Extracting Track {i}...")
            self.root.update()

            try:
                # Dump audio stream
                extract_proc = subprocess.Popen([
                    MPLAYER_PATH,
                    "-dumpaudio",
                    "-dvd-device", DVD_DEVICE,
                    f"dvd://{i}",
                    "aid", "128"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Read the output of the extract process in real-time
                decoded_line = ""
                while not extract_proc.poll():
                    #time.sleep(0.2)
                    data = extract_proc.stdout.read(1)
                    if len(data)==0: break
                    #print(data)
                    if not data in [b"\r", b"\n"]: decoded_line = decoded_line + str(data.decode(errors="ignore"))
                    else:
                        #print(decoded_line)
                        if "dump" in decoded_line:  # You can modify this based on the output you get from MPlayer
                            match = re.search(r"~([\d\.]+%)", decoded_line)
                            if match:
                                percent = match.group(1)
                                self.update_progress(f"Extracting: {percent}")

                        decoded_line=""
               

                # Wait for the extraction process to finish
                print("wait")
                extract_proc.wait()

                if not self.extracting:
                    break

                # Convert to desired format
                out_file = os.path.join(self.output_folder, f"track{i}.{self.output_format.get()}")
                conversion_proc = subprocess.Popen([
                    FFMPEG_PATH,
                    "-y",
                    "-i", "stream.dump",
                    out_file
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Read the output of the conversion process in real-time


                # Read the output of the extract process in real-time
                decoded_line = ""
                while not conversion_proc.poll():
                    #time.sleep(0.2)
                    data = conversion_proc.stderr.read(1)
                    if len(data)==0: break
                    #print(data)
                    if not data in [b"\r", b"\n"]: decoded_line = decoded_line + str(data.decode(errors="ignore"))
                    else:
                        print(">>>" + str(decoded_line))
                        if "time=" in decoded_line:  # You can modify this based on the output you get from MPlayer
                            match = re.search(r"time=([^ ]*) ", decoded_line)
                            if match:
                                sofar = match.group(1).split(":")
                                #print(sofar)
                                sofar = 60*60*int(sofar[0])+60*int(sofar[1])+float(sofar[2])
                                #print(sofar)
                                percent = 100 * sofar / length
                                #print(percent)
                                self.update_progress(f"Converting: {percent:.2f}%")
                        decoded_line=""

                conversion_proc.wait()  # Wait for the conversion to complete

                # Clean up the dumped audio file
                if os.path.exists("stream.dump"):
                    os.remove("stream.dump")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract track {i}: {e}")
                break

        if self.extracting:
            self.update_progress("Extraction complete!")
            messagebox.showinfo("Done", "Audio extraction completed.")
        else:
            self.update_progress("Extraction cancelled.")

        self.extracting = False
        self.cancel_button.config(state=tk.DISABLED)
        self.extract_button.config(state=tk.NORMAL)
        self.scan_button.config(state=tk.NORMAL)

# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DVDExtractorApp(root)
    root.mainloop()

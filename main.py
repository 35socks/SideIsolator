import tkinter as tk
from tkinter import filedialog, messagebox
import os
from scipy.io import wavfile
import numpy as np
from datetime import datetime


# This was coded by github.com/35socks. Please give credit if you use this code as a whole or part of it.
# This code is licensed under the MIT License. See the LICENSE file for more information.
# This code is provided as is, without any warranty. Use it at your own risk.

def select_audio_file():
    filetypes = (
        ('Audio files', '*.wav'),
        ('All files', '*.*')
    )
   
    filename = filedialog.askopenfilename(
        title='Open an audio file',
        initialdir='/',
        filetypes=filetypes)
   
    return filename

def create_subfolder(base_filename):
    base_name = os.path.splitext(os.path.basename(base_filename))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    subfolder_name = f"{base_name}_{timestamp}"
    
    if not os.path.exists('INVERSIONS'):
        os.makedirs('INVERSIONS')
    
    subfolder_path = os.path.join('INVERSIONS', subfolder_name)
    os.makedirs(subfolder_path)
    
    return subfolder_path

def process_audio_file():
    try:
        filename = select_audio_file()
        
        if filename:
            output_folder = create_subfolder(filename)
            
            sample_rate, audio_array = wavfile.read(filename)
            
            audio_array = audio_array.astype(np.float32)
            if audio_array.ndim < 2:
                messagebox.showerror("Error", "File must be stereo (2 channels)")
                return
            
            audio_array = audio_array / np.max(np.abs(audio_array))
            
            left_channel = audio_array[:, 0]
            right_channel = audio_array[:, 1]
            
            mono_channel = (left_channel + right_channel) / 2
            
            left_inverted = -left_channel
            right_inverted = -right_channel
            
            left_non_mono = left_channel - mono_channel
            right_non_mono = right_channel - mono_channel
            
            left_mono_remains = left_channel - left_non_mono  
            right_mono_remains = right_channel - right_non_mono  
            mono_remains = (left_mono_remains + right_mono_remains) / 2  
            
            output_files = {
                '00_left_channel.wav': left_channel,
                '00_right_channel.wav': right_channel,
                '00_mono.wav': mono_channel,
                '01_left_inverted.wav': left_inverted,
                '02_right_inverted.wav': right_inverted,
                '03_left_non_mono.wav': left_non_mono,
                '04_right_non_mono.wav': right_non_mono,
                '07_REMAINS.wav': mono_remains
            }
            
            info_file_path = os.path.join(output_folder, 'process_info.txt')
            with open(info_file_path, 'w') as f:
                f.write(f"Original file: {filename}\n")
                f.write(f"Processing date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Sample rate: {sample_rate} Hz\n")
            
            for output_filename, data in output_files.items():
                output_path = os.path.join(output_folder, output_filename)
                normalized_data = np.float32(data)
                normalized_data = normalized_data / np.max(np.abs(normalized_data))
                wavfile.write(output_path, sample_rate, normalized_data)
            
            messagebox.showinfo("Success", f"All files processed and saved in\n{output_folder}")
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

root = tk.Tk()
root.title('Audio Channel Processor')
root.geometry('400x200')

label = tk.Label(root, text="Audio Channel Separator & Polarity Inverter",
                 font=('Helvetica', 12, 'bold'))
label.pack(pady=20)

process_button = tk.Button(root, text='Process Audio File',
                          command=process_audio_file,
                          font=('Helvetica', 10),
                          padx=20, pady=10)
process_button.pack(expand=True)

status_label = tk.Label(root, text="Select a stereo WAV file to begin",
                       font=('Helvetica', 10))
status_label.pack(pady=20)

root.mainloop()
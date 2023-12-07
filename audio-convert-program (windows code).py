import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pydub import AudioSegment
import os
import sys
import shutil
import subprocess  # Import the subprocess module
import tkinter.simpledialog

# icon  
if getattr(sys, 'frozen', False):
    # Running as a bundled executable
    icon_path = sys._MEIPASS + "\\icon.ico"
else:
    # Running as a regular Python script
    icon_path = "icon.ico"

################################################################################################## MP4 + MOV + AVI video files ---------- files + folders
# Define the supported video file extensions
VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".flv", ".mkv", ".webm", ".wmv")

def browse_folder_command():
    global folder_path
    folder_path = filedialog.askdirectory()

    if folder_path:
        # Check if the selected folder contains any valid files
        folder_contains_valid_files = any(file.lower().endswith(VIDEO_EXTENSIONS) for file in os.listdir(folder_path))
        if folder_contains_valid_files:
            folder_path_label.config(text="Selected folder: " + folder_path)
        else:
            messagebox.showerror("Error", "The selected folder does not contain valid video files (mp4, mov, avi, flv, mkv, webm, wmv).")
            folder_path = ""
            folder_path_label.config(text="Select a folder or files to convert")
    else:
        return

def browse_files_command():
    global input_paths
    input_paths = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4 *.mov *.avi *.flv *.mkv *.webm *.wmv")])

    if not input_paths:
        folder_path_label.config(text="No files selected")
    else:
        input_paths = list(input_paths)
        if len(input_paths) == 1:
            folder_path_label.config(text="Selected file: " + input_paths[0])
        else:
            folder_path_label.config(text=f"Selected {len(input_paths)} files")

####################################################################################################### MP4 + MOV + AVI video files
### CONVERT
def convert_command():
    if not folder_path and not input_paths:
        messagebox.showerror("Error", "Please select a folder or files first.")
        return

    audio_converted_folder = os.path.join(os.path.dirname(input_paths[0]) if input_paths else folder_path, "audio_converted_files")

    # Check if the output folder "audio_converted_files" already exists
    folder_exists = os.path.exists(audio_converted_folder)

    if folder_exists:
        response = messagebox.askquestion("Folder Exists", "'audio_converted_files' folder already exists. Do you want to overwrite it?", icon='warning', parent=app)

        if response.lower() == "yes":
            shutil.rmtree(audio_converted_folder)  # If the user chooses to overwrite, delete the existing folder
        else:
            return  # User chose not to overwrite

    # Create the output folder + give label to user
    status_label.config(text="Converting files...")
    app.update_idletasks()  # Update the label immediately
    os.mkdir(audio_converted_folder)

    # Determine the path to the bundled FFmpeg binary
    if getattr(sys, 'frozen', False):
        # If the script is running as a compiled executable
        ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
    else:
        # If the script is running as a regular Python script
        ffmpeg_path = os.path.join('ffmpeg', 'ffmpeg.exe')

    # Create a progress bar
    progress_bar = ttk.Progressbar(app, length=400, mode="determinate")
    progress_bar.place(relx=0.5, rely=0.5, anchor="center")

    input_files = input_paths if input_paths else [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith(VIDEO_EXTENSIONS)]

    # Set the maximum value for the progress bar based on the number of input files
    progress_bar["maximum"] = len(input_files)
    progress_bar["value"] = 0

    for input_path in input_files:
        if os.path.isfile(input_path):
            video_file_path = input_path
        else:
            continue

        audio_file_name = os.path.splitext(os.path.basename(input_path))[0] + ".mp3"
        audio_file_path = os.path.join(audio_converted_folder, audio_file_name)

        # Check if the audio file already exists in the output folder
        file_counter = 1
        while os.path.exists(audio_file_path):
            # If the file already exists, append a number to the filename
            audio_file_name = os.path.splitext(os.path.basename(input_path))[0] + f"({file_counter}).mp3"
            audio_file_path = os.path.join(audio_converted_folder, audio_file_name)
            file_counter += 1

        # Use the bundled FFmpeg binary
        cmd = [ffmpeg_path, "-i", video_file_path, audio_file_path]
        subprocess.run(cmd, shell=True)

        # Update the progress bar
        progress_bar["value"] += 1
        app.update_idletasks()

    # Clear the status label after conversion is complete
    status_label.config(text="")
    progress_bar.destroy()

    messagebox.showinfo("Success", "File(s) converted to audio and saved in 'audio_converted_files' folder successfully")
    # Reset the program after converting
    reset_program()

###############################################################################################################################
################### THE PROGRAM - tkinter
def reset_program():
    global folder_path, input_paths
    folder_path = ""
    input_paths = []
    folder_path_label.config(text="Select a folder or files to convert")

def exit_program():
    app.quit()

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

app = tk.Tk()
app.iconbitmap(icon_path)
app.title("Audio Converter program")
center_window(app, 600, 310)
app.resizable(width=False, height=False)

app.configure(background="#3b4370")

title_label = tk.Label(app, background="#CCCCFF", foreground="#333333", font=("Arial", 20, "bold"), text="Audio Converter program")
title_label.place(x=0, y=0, width=600, height=50)

folder_path_label = tk.Label(app, font=("Arial", 16), text="Select a folder or files to convert", background="#3b4370", foreground="white")
folder_path_label.place(x=0, y=70, width=600, height=20)

browse_folder_button = tk.Button(app, command=browse_folder_command, font=("Arial", 14), text="Select Folder", highlightbackground="#3b4370", highlightcolor="#3b4370", foreground="black")
browse_folder_button.place(relx=0.3, rely=0.35, anchor="center")

browse_files_button = tk.Button(app, command=browse_files_command, font=("Arial", 14), text="Select Files", highlightbackground="#3b4370", highlightcolor="#3b4370", foreground="black")
browse_files_button.place(relx=0.7, rely=0.35, anchor="center")

convert_button = tk.Button(app, command=convert_command, font=("Arial", 14), text="Convert", highlightbackground="#3b4370", highlightcolor="#3b4370", foreground="black")
convert_button.place(relx=0.5, rely=0.75, anchor="center")

status_label = tk.Label(app, font=("Arial", 16), text="", background="#3b4370", foreground="white")
status_label.place(relx=0.5, rely=0.6, anchor="center")

exit_button = tk.Button(app, command=exit_program, font=("Arial", 14), text="Exit", highlightbackground="#3b4370", highlightcolor="#3b4370", foreground="black")
exit_button.place(relx=0.5, rely=0.95, anchor="center")

folder_path = ""
input_paths = []
app.mainloop()
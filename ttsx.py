import os
import tkinter as tk
from tkinter import filedialog, messagebox
from gtts import gTTS
from pydub import AudioSegment
import pygame
import tempfile

# Initialize pygame mixer
pygame.mixer.init()

# Available macOS system voices (deep male, female, robotic)
MACOS_VOICES = {
    "Male": "Daniel",
    "Female": "Karen",
    "Robot": "Fred"
}

# Function to speak text with speed and pitch adjustment
def speak_text():
    text = text_entry.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return

    selected_voice = voice_var.get()
    speed = speed_var.get()
    pitch = pitch_var.get()

    # macOS System Voice
    voice = MACOS_VOICES[selected_voice]

    # Create a temporary file for the speech
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp_file:
        tmp_filename = tmp_file.name

    # Generate speech using the `say` command at normal speed
    os.system(f'say -v {voice} "{text}" -o {tmp_filename}')

    # Load the generated audio file
    audio = AudioSegment.from_file(tmp_filename, format="aiff")

    # Adjust speed by modifying the frame rate
    speed_adjusted_audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * speed)
    }).set_frame_rate(audio.frame_rate)

    # Adjust pitch
    pitch_shift = (pitch - 50) / 50  # Normalize pitch to a multiplier (0.5x to 1.5x)
    new_sample_rate = int(speed_adjusted_audio.frame_rate * (2.0 ** pitch_shift))
    pitched_audio = speed_adjusted_audio._spawn(speed_adjusted_audio.raw_data, overrides={'frame_rate': new_sample_rate})
    pitched_audio = pitched_audio.set_frame_rate(44100)  # Reset to standard frame rate

    # Export the modified audio to a temporary file
    modified_filename = tmp_filename.replace(".aiff", "_modified.wav")
    pitched_audio.export(modified_filename, format="wav")

    # Play the modified audio using pygame
    pygame.mixer.music.load(modified_filename)
    pygame.mixer.music.play()

    # Clean up temporary files
    os.remove(tmp_filename)
    os.remove(modified_filename)

# Function to save text as MP3
def save_as_mp3():
    text = text_entry.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
    if not file_path:
        return

    tts = gTTS(text, lang="en", tld="co.uk")  # Use UK English for deeper male voices
    tts.save(file_path)

    # Lower pitch using pydub
    sound = AudioSegment.from_file(file_path)
    deep_voice = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * 0.8)})
    deep_voice = deep_voice.set_frame_rate(44100)
    deep_voice.export(file_path, format="mp3")

    messagebox.showinfo("Success", "MP3 saved successfully!")

# Function to play audio
def play_audio():
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if not file_path:
        return

    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Function to stop audio
def stop_audio():
    pygame.mixer.music.stop()

# Function to update speed label
def update_speed_label(value):
    speed_label.config(text=f"Speed: {value}x")

# GUI Setup
root = tk.Tk()
root.title("Text-to-Speech Converter")
root.geometry("600x500")
root.configure(bg="#2c003e")  # Futuristic purple background

# Custom font for a modern look
custom_font = ("Helvetica", 12)

# Frame for Text Input
text_frame = tk.Frame(root, bg="#2c003e")
text_frame.pack(pady=10, padx=20, fill="both", expand=True)

# Text Input
text_entry = tk.Text(text_frame, height=5, width=50, font=custom_font, bg="#1a0033", fg="cyan", wrap="word")
text_entry.pack(pady=10, fill="both", expand=True)

# Frame for Controls
control_frame = tk.Frame(root, bg="#2c003e")
control_frame.pack(pady=10, padx=20, fill="both")

# Voice Selection Dropdown
voice_var = tk.StringVar(value="Male")
voice_label = tk.Label(control_frame, text="Select Voice:", font=custom_font, bg="#2c003e", fg="cyan")
voice_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
voice_dropdown = tk.OptionMenu(control_frame, voice_var, *MACOS_VOICES.keys())
voice_dropdown.config(font=custom_font, bg="#1a0033", fg="cyan", highlightbackground="#2c003e")
voice_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Speed Slider
speed_var = tk.DoubleVar(value=1.0)  # Default speed is 1x
speed_label = tk.Label(control_frame, text="Speed: 1.0x", font=custom_font, bg="#2c003e", fg="cyan")
speed_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
speed_slider = tk.Scale(control_frame, variable=speed_var, from_=0.25, to=2.0, resolution=0.25, orient="horizontal", bg="#1a0033", fg="cyan", highlightbackground="#2c003e", command=update_speed_label)
speed_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Pitch Slider
pitch_var = tk.IntVar(value=50)
pitch_label = tk.Label(control_frame, text="Pitch:", font=custom_font, bg="#2c003e", fg="cyan")
pitch_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
pitch_slider = tk.Scale(control_frame, variable=pitch_var, from_=10, to=100, orient="horizontal", bg="#1a0033", fg="cyan", highlightbackground="#2c003e")
pitch_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Frame for Buttons
button_frame = tk.Frame(root, bg="#2c003e")
button_frame.pack(pady=10, padx=20, fill="both")

# Buttons
speak_button = tk.Button(button_frame, text="Speak", command=speak_text, bg="cyan", fg="black", font=custom_font)
speak_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

save_button = tk.Button(button_frame, text="Save as MP3", command=save_as_mp3, bg="gold", fg="black", font=custom_font)
save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

play_button = tk.Button(button_frame, text="Play MP3", command=play_audio, bg="lightblue", fg="black", font=custom_font)
play_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

stop_button = tk.Button(button_frame, text="Stop", command=stop_audio, bg="red", fg="white", font=custom_font)
stop_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

# Make columns in button_frame equally weighted
for i in range(4):
    button_frame.grid_columnconfigure(i, weight=1)

root.mainloop()

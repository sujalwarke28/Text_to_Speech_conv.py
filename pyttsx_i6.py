import os
import tkinter as tk
from tkinter import filedialog, messagebox
from gtts import gTTS
from pydub import AudioSegment
import pygame
import tempfile
import math
import threading

# Initialize pygame mixer
pygame.mixer.init()

# macOS system voices (deep male, female, robotic)
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
    speed_adjusted_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)}).set_frame_rate(audio.frame_rate) #needs work !!!!

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

    # Start waveform animation
    animate_waveform() #Doesnot work as expected

    # Clean up temporary files after playback
    def cleanup():
        os.remove(tmp_filename)
        os.remove(modified_filename)

    threading.Thread(target=lambda: (pygame.mixer.music.wait(), cleanup()), daemon=True).start()


# Function to update waveform animation based on audio playback
def animate_waveform():
    if pygame.mixer.music.get_busy():
        draw_waveform(waveform_canvas, 600, 100, dynamic=True)
        root.after(100, animate_waveform)
    else:
        draw_waveform(waveform_canvas, 600, 100, dynamic=False) #Doesnot work as expected; needs work


# Function to draw the waveform
def draw_waveform(canvas, width, height, dynamic=False):
    canvas.delete("wave")  # Clear previous waveform
    for i in range(0, width, 5):
        amplitude = math.sin(i / 20) * (height / 2 - 10)
        if dynamic:
            amplitude *= 1 + (math.sin(pygame.mixer.music.get_pos() / 100) / 2)
        canvas.create_line(i, height / 2 + amplitude, i + 5, height / 2 - amplitude, fill="#00FFFF", tags="wave")


# GUI Setup
root = tk.Tk()
root.title("Text-to-Speech Converter")
root.geometry("600x500")
root.configure(bg="#2c003e")  # Futuristic purple background

# Custom font for a modern look
custom_font = ("Helvetica", 12)

# Text Input
text_entry = tk.Text(root, height=5, width=50, font=custom_font, bg="#1a0033", fg="cyan", wrap="word")
text_entry.pack(pady=10, fill="both", expand=True)

# Controls
voice_var = tk.StringVar(value="Male")
speed_var = tk.DoubleVar(value=1.0)
pitch_var = tk.IntVar(value=50)

tk.Label(root, text="Select Voice:", font=custom_font, bg="#2c003e", fg="cyan").pack()
tk.OptionMenu(root, voice_var, *MACOS_VOICES.keys()).pack()
tk.Label(root, text="Speed:", font=custom_font, bg="#2c003e", fg="cyan").pack()
tk.Scale(root, variable=speed_var, from_=0.25, to=2.0, resolution=0.25, orient="horizontal").pack()
tk.Label(root, text="Pitch:", font=custom_font, bg="#2c003e", fg="cyan").pack()
tk.Scale(root, variable=pitch_var, from_=10, to=100, orient="horizontal").pack()

tk.Button(root, text="Speak", command=speak_text).pack()

# Waveform Animation
waveform_canvas = tk.Canvas(root, bg="#2c003e", height=100, highlightthickness=0)
waveform_canvas.pack(fill="both", expand=True)
draw_waveform(waveform_canvas, 600, 100)

root.mainloop()

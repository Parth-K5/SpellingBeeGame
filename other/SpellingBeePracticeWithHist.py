import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import random
#import pyttsx3
from os import system
import platform
import logging
from io import BytesIO
from gtts import gTTS
import pygame
from datetime import datetime
from time import sleep

class SpellingGame:
    def __init__(self, root, style):
        self.root = root
        self.root.title("Spelling Game")
        self.style = style
        self.words=[]

        with open("wordList.txt", 'r') as wordFile:
            wordlist = wordFile.readlines()

        for i in wordlist:
            self.words.append(i.rstrip())
        self.current_word = ""
        self.score = 0
        self.allow_hyphen = tk.BooleanVar()
        self.custom_words_var = tk.StringVar()
        self.debug_var = tk.BooleanVar()
        self.game_started = False

        # Game Screen Widgets
        self.game_frame = ttk.Frame(root)
        self.label_word = ttk.Label(self.game_frame, text="")
        self.entry_guess = ttk.Entry(self.game_frame)
        self.label_result = ttk.Label(self.game_frame, text="")
        self.label_score = ttk.Label(self.game_frame, text="Score: 0")

        # Options Screen Widgets
        self.options_frame = ttk.Frame(root)
        self.check_hyphen = ttk.Checkbutton(self.options_frame, text="Allow Hyphenated Words", variable=self.allow_hyphen, style="TCheckbutton")
        self.custom_words_entry = ttk.Entry(self.options_frame, textvariable=self.custom_words_var)
        self.debug_checkbox = ttk.Checkbutton(self.options_frame, text="Debug Mode", variable=self.debug_var, style="TCheckbutton", command=self.update_debug_label)
        ttk.Label(self.options_frame, text="Custom Words (comma-separated):").pack(pady=10)
        self.custom_words_entry.pack(pady=10)
        self.debug_checkbox.pack(pady=10)
        ttk.Button(self.options_frame, text="Add Custom Word", command=self.add_custom_word, style="TButton").pack(pady=10)
        ttk.Button(self.options_frame, text="Exit Options", command=self.hide_options, style="TButton").pack(pady=20)

        # Buttons
        self.start_button = ttk.Button(self.game_frame, text="Start Game", command=self.toggle_game, style="TButton")
        self.check_button = ttk.Button(self.game_frame, text="Check Answer", command=self.check_answer, style="TButton", state="disabled")
        self.speech_button = ttk.Button(self.game_frame, text="Say Word", command=lambda: self.sayWord(self.current_word), style="TButton")
        ttk.Button(self.game_frame, text="Options", command=self.toggle_options, style="TButton").pack(pady=20)

        # Debug label
        self.debug_label = ttk.Label(self.options_frame, text="")
        self.debug_label.pack(pady=10)

        # Configure font for specific elements
        style.configure("TLabel", font=("Helvetica", 36))
        style.configure("TEntry", font=("Helvetica", 36))
        style.configure("TButton", font=("Helvetica", 36))
        style.configure("TCheckbutton", font=("Helvetica", 36))

        # Initial Layout
        self.game_frame.pack(expand=True, fill="both")
        self.label_word.pack(pady=20)
        self.entry_guess.pack(pady=20)
        self.start_button.pack(pady=20)
        self.check_button.pack(pady=20)
        self.speech_button.pack(pady=20)
        self.label_result.pack(pady=20)
        self.label_score.pack(pady=20)
        self.entry_guess.bind("<Return>", self.check_answer)

    def toggle_game(self):
        if self.game_started:
            self.end_game()
        else:
            self.start_game()

    def start_game(self):
        self.game_started = True
        self.start_button.config(text="End Game")
        self.check_button.config(state="normal")
        self.label_word.config(text="")
        self.label_result.config(text="")
        self.entry_guess.delete(0, tk.END)
        self.score = 0  # Reset score
        self.present_next_word();

    def end_game(self):
        self.game_started = False
        self.start_button.config(text="Start Game")
        self.check_button.config(state="disabled")

    def check_answer(self):
        if self.game_started:
            user_guess = self.entry_guess.get().lower()
            print(f"Entered: '{user_guess}")

            #Checks:
            direct = user_guess == self.current_word
            match = user_guess in self.homophones

            #print(f"{user_guess} = {self.current_word} => {direct}")
            #print(f"{user_guess} in {self.homophones} => {match}")

            # Check options
            if not self.allow_hyphen.get():
                user_guess = user_guess.replace("-", "")
                self.current_word = self.current_word.replace("-", "")

            if user_guess.lower() == self.current_word.lower() or user_guess in self.homophones:
                self.label_result.config(text="Correct!")
                self.score += 1
                self.label_score.config(text=f"Score: {self.score}")
                
                # Clear the entry widget
                self.entry_guess.delete(0, tk.END)
                
                # Use after method to delay the next word presentation by 1000 milliseconds (1 second)
                self.root.after(1000, self.present_next_word)
            else:
                self.label_result.config(text="Incorrect. Try again.")

    def present_next_word(self):
        if self.game_started:
            self.homophones = None
            self.current_word = random.choice(self.words)
            #print(f"RNG Word: {self.current_word}")
            if self.current_word.startswith("*"):
                self.sayWord("Next word can be spelled in multiple ways")
                sleep(3)

                words=self.current_word[2:]

                print(f"All variations:")
                self.homophones=words.split()

                for word in self.homophones:
                    self.homophones[self.homophones.index(word)] = word.lower()

                for word in self.homophones:
                    print(f"--> '{word}'")

                wordVariation = random.choice(self.homophones)

                print(f"Selected Variation: {wordVariation}")
                self.sayWord(wordVariation)
                self.current_word = wordVariation

            else:
                self.sayWord(self.current_word)
            self.label_word.config(text="")
            self.label_result.config(text="")


    def toggle_options(self):
        if self.options_frame.winfo_ismapped():
            self.hide_options()
        else:
            self.show_options()

    def show_options(self):
        self.game_frame.pack_forget()
        self.options_frame.pack(expand=True, fill="both")

    def hide_options(self):
        self.options_frame.pack_forget()
        self.game_frame.pack(expand=True, fill="both")

    def add_custom_word(self, event=None):
        # Add custom word to the word list
        custom_word = self.custom_words_var.get().strip()
        if custom_word:
            self.words.append(custom_word)
            self.custom_words_var.set("")  # Clear the textbox after adding the word

            # Update debug label if debug mode is enabled
            self.update_debug_label()

    def update_debug_label(self):
        # Update debug label based on the debug mode checkbox
        if self.debug_var.get():
            words_str = "Words in Game List: " + ", ".join(self.words)
            self.debug_label.config(text=words_str)
        else:
            self.debug_label.config(text="")

    def sayWord(self, word):
        if SFX_STYLE == "gTTS":
            mp3bytes = BytesIO()
            tts = gTTS(word, lang="en", tld="com")
            tts.write_to_fp(mp3bytes)
            mp3bytes.seek(0)
            pygame.mixer.Sound(mp3bytes).play()
        elif SFX_STYLE == "native":
            system(f"say {word}")

if __name__ == "__main__":
    if platform.system() != "Darwin":
        logging.warning("Warning: This program only runs without an internet connection on MacOS")
        SFX_STYLE = "gTTS"
    else:
        SFX_STYLE = "native"
    
    SFX_STYLE = "gTTS"
    if (SFX_STYLE == "gTTS"):
        pygame.mixer.init()
    print(f"Using {SFX_STYLE} tts")


    style = Style(theme="superhero")
    root = style.master
    random.seed(datetime.now().timestamp())
    app = SpellingGame(root, style)
    print("After constructor\n")
    root.mainloop()

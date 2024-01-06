import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import random
#import pyttsx3
import os
import platform
import logging
from io import BytesIO
from gtts import gTTS
import pygame
from bs4 import BeautifulSoup
from PyDictionary import PyDictionary
import requests
import shutil
from time import ctime

class SpellingGame:
    def __init__(self, root, style):
        self.root = root
        self.root.title("Spelling Game")
        self.style = style
        self.words = ["apple", "banana", "cherry", "orange", "grape", "kiwi", "melon", "pear", "plum", "strawberry"]
        self.current_word = ""
        self.score = 0
        self.allow_hyphen = tk.BooleanVar()
        self.custom_words_var = tk.StringVar()
        self.debug_var = tk.BooleanVar()
        self.game_started = False
        self.internal_record = {'practiced': [], 'correct': [], 'incorrect': []}

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
        #self.root.bind("<Return>", self.check_answer)
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
        style.configure("TLabel", font=("Helvetica", 24))
        style.configure("TEntry", font=("Helvetica", 18))
        style.configure("TButton", font=("Helvetica", 14))
        style.configure("TCheckbutton", font=("Helvetica", 14))

        # Initial Layout
        self.game_frame.pack(expand=True, fill="both")
        self.label_word.pack(pady=20)
        self.entry_guess.pack(pady=20)
        self.start_button.pack(pady=20)
        self.check_button.pack(pady=20)
        self.speech_button.pack(pady=20)
        self.label_result.pack(pady=20)
        self.label_score.pack(pady=20)

    def toggle_game(self):
        if self.game_started:
            self.end_game()
        else:
            self.start_game()

    def start_game(self):
        self.game_started = True
        self.start_button.config(text="End Game")
        self.check_button.config(state="normal")
        self.current_word = random.choice(self.words)
        self.sayWord(self.current_word)
        self.label_word.config(text="")
        self.label_result.config(text="")
        self.entry_guess.delete(0, tk.END)
        self.score = 0  # Reset score

    def end_game(self):
        self.game_started = False
        self.start_button.config(text="Start Game")
        self.check_button.config(state="disabled")

    def check_answer(self):
        if self.game_started:
            user_guess = self.entry_guess.get().lower()

            # Check options
            if not self.allow_hyphen.get():
                user_guess = user_guess.replace("-", "")
                self.current_word = self.current_word.replace("-", "")

            if user_guess == self.current_word:
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
            self.current_word = random.choice(self.words)
            self.sayWord(self.current_word)
            self.label_word.config(text="")
            self.label_result.config(text="")
            self.get_definition(self.current_word)


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
            os.system(f"say {word}")

    def get_definition(self, word):
        dictURL = f'https://www.oxfordlearnersdictionaries.com/definition/english/{word}'
        
        headers = {"User-Agent": ""}
        definitions = []

        resp = requests.get(dictURL, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')

        meaningsFound = soup.find_all('li', class_='sense')

        for eachMeaning in meaningsFound:
            definitions.append(eachMeaning.find('span', class_='def').text)
            
        if len(definitions) == 0:
            definitions = list(PyDictionary().meaning(word).values())[0]
        
        return definitions

    def record(self, word, result):
        self.internal_record['practiced'].append(word)
        self.internal_record[result].append(word)

        return f"Updated accuracy of {word} to [{self.internal_record['correct'].count(word)}:{self.internal_record['incorrect'].count(word)}]"

    def quit(self):
        with open('history.txt', 'w') as file:
            for word in self.internal_record['practiced']:
                file.write(f"{word} {self.internal_record['correct'].count(word)} {self.internal_record['incorrect'].count(word)}")

'''
def play():
    if platform.system() != "Darwin":
            logging.warning("Warning: This program only runs without an internet connection on MacOS")
            SFX_STYLE = "gTTS"
            pygame.mixer.init()
    else:
        SFX_STYLE = "native"
        
    print(f"Using {SFX_STYLE} tts")

    style = Style(theme="superhero")
    root = style.master
    app = SpellingGame(root, style)
    root.mainloop()
'''

class Adaptation(Exception):
    pass

class AdaptationCurve:
    HERE = os.getcwd()
    
    def __init__(self):
        self.refresh()
        
        self.processingData = None
        self.learningBias = []

    def refresh(self, preservation):
        self.historyPath = f'{self.HERE}/'
        self.historyFile = f"{self.historyPath}/history.txt"
        
        if preservation == False:
            if os.path.exists(self.historyFile) == False:
                file = open(self.historyFile, 'w')
                file.close()

        with open(self.historyFile, 'a') as results:
            self.processingData = results.readlines()

        if not self.processingData:
            raise Adaptation('No Previous Data Found')

    def extrapolate(self):
        curve = {}
        for line in self.processingData:
            terms = line.split(" ")
            curve[terms[0]] = int(terms[1]) / (int(terms[1]) + int(terms[2]))

        return curve
    


if __name__ == "__main__":
    if platform.system() != "Darwin":
        logging.warning("Warning: This program only runs without an internet connection on MacOS")
        SFX_STYLE = "gTTS"
        pygame.mixer.init()
    else:
        SFX_STYLE = "native"
    
    print(f"Using {SFX_STYLE} tts")

    style = Style(theme="superhero")
    root = style.master
    app = SpellingGame(root, style)

    root.mainloop()

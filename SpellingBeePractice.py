import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import random
from os import system
import platform
import logging
from io import BytesIO
from gtts import gTTS
import pygame
from datetime import datetime
import time
from time import sleep
import os
from PyDictionary import PyDictionary
import requests
from bs4 import BeautifulSoup
from lxml import etree
import multiprocessing
import concurrent.futures
import shutil

class SpellingGame:
    def __init__(self, root, style, SFX_STYLE, learningCurve=None):
        self.root = root
        self.SFX_STYLE = SFX_STYLE

        self.root.attributes("-fullscreen", True)
        self.root.title("Spelling Game")
        self.style = style
        self.words=[]
        self.homophones = []
        self.LEARNING_CURVE = learningCurve

        if self.LEARNING_CURVE:
                print("Found the following scores to adapt to:")
                print(self.LEARNING_CURVE)

        self.internal_record = {'practiced': [], 'correct': [], 'incorrect': []}
        self.local_definitions = "cache/definitions/"

        if os.path.exists("cache") == False:
                os.mkdir("cache")
        if os.path.exists("cache/definitions") == False:
            os.mkdir("cache/definitions")

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
        self.entry_guess.focus_set()
        self.entry_guess.bind("<Return>", func=self.check_answer)

        self.label_result = ttk.Label(self.game_frame, text="")
        self.label_definition = ttk.Label(self.game_frame, text="")
        self.label_score = ttk.Label(self.game_frame, text="Score: 0")

        # Options Screen Widgets
        self.options_frame = ttk.Frame(root)
        self.check_hyphen = ttk.Checkbutton(self.options_frame, text="Allow Hyphenated Words", variable=self.allow_hyphen, style="TCheckbutton")
        self.rebuild_button = ttk.Button(self.options_frame, text="Rebuild Cache", command=self.rebuild_cache, style="TButton")
        self.rebuild_button.pack(pady=20)

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
        self.speech_button.config(state="disabled")

        self.skip_button = ttk.Button(self.game_frame, text="Skip", command= lambda: self.skip(), style="TButton", state='disabled')

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
        self.skip_button.pack(pady=20)
        self.label_result.pack(pady=20)
        self.label_score.pack(pady=20)
        self.label_definition.pack(padx=20, pady=20)

    def toggle_game(self):
        if self.game_started:
            self.end_game()
        else:
            self.start_game()

    def skip(self):
        if self.game_started:
            self.label_result.config(text=f"The correct word is {self.current_word}")
            self.skip_button.config(state='disabled')
            self.check_button.config(state="disabled")
            self.root.after(5000, self.present_next_word)
            self.record(self.current_word, 'incorrect')

    def start_game(self):
        self.game_started = True
        self.start_button.config(text="End Game")
        self.check_button.config(state="normal")
        self.speech_button.config(state="normal")
        self.label_word.config(text="")
        self.label_result.config(text="")
        self.label_definition.config(text="")
        self.skip_button.config(state="normal")
        self.entry_guess.delete(0, tk.END)
        self.score = 0  # Reset score
        self.present_next_word();

    def end_game(self):
        self.game_started = False
        self.start_button.config(text="Start Game")
        self.check_button.config(state="disabled")
        self.speech_button.config(state="disabled")
        self.skip_button.config(state="disabled")
        self.label_definition.config(text="")
        self.score = 0
        self.label_score.config(text=f"Score: {self.score}")

        print("\n\nGAME ENDED")

        with open('history.txt', 'w') as progress:
            for word in list(set(self.internal_record['practiced'])):
                progress.write(f"{word} {self.internal_record['correct'].count(word)} {self.internal_record['incorrect'].count(word)}\n")

        print("RESULTS SAVED")

    def check_answer(self, keyActivated=None):
        if self.game_started:

            self.label_definition.config(text="")

            user_guess = self.entry_guess.get().lower()
            print(f"Entered: '{user_guess}'")

            #Checks:
            direct = user_guess == self.current_word
            match = user_guess in self.homophones

            print(f"{user_guess} = {self.current_word} => {direct}")
            print(f"{user_guess} in {self.homophones} => {match}")

            # Check options
            if not self.allow_hyphen.get():
                user_guess = user_guess.replace("-", "")
                self.current_word = self.current_word.replace("-", "")

            if user_guess.lower() == self.current_word.lower() or user_guess in self.homophones:
                self.label_result.config(text="Correct!")
                self.score += 1
                self.record(self.current_word, 'correct')
                self.label_score.config(text=f"Score: {self.score}")
                
                # Clear the entry widget
                self.entry_guess.delete(0, tk.END)
                
                # Use after method to delay the next word presentation by 1000 milliseconds (1 second)
                self.root.after(1000, self.present_next_word)
            else:
                self.record(self.current_word, 'incorrect')
                self.label_result.config(text="Incorrect. Try again.")

    def present_next_word(self):
        if self.game_started:
            self.check_button.config(state="normal")
            self.skip_button.config(state="normal")

            self.homophones = []

            if self.LEARNING_CURVE:
                weights = [self.LEARNING_CURVE.get(wordOption, 1.0) for wordOption in self.words]
                self.current_word = random.choices(self.words, weights=weights, k=1)[0]
            else:
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

            found_def = self.get_definition(self.current_word)
            if len(found_def) > 1:
                definition = found_def[0]
            else:
                definition = "\n".join(found_def[:2])
                
            font_size = 24 if len(definition) < 100 else 18
            
            self.label_definition.config(text=definition, font=("Helvetica", font_size))

            self.entry_guess.focus_set()


    def toggle_options(self):
        if self.options_frame.winfo_ismapped():
            self.hide_options()
        else:
            self.show_options()

    def show_options(self):
        self.game_frame.pack_forget()
        self.options_frame.pack(expand=True, fill="both")

    def hide_options(self):
        self.rebuild_button.config(state='normal')
        self.rebuild_button.config(text="Rebuild Cache")
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
        if self.SFX_STYLE == "gTTS":
            mp3bytes = BytesIO()
            tts = gTTS(word, lang="en", tld="com")
            tts.write_to_fp(mp3bytes)
            mp3bytes.seek(0)
            pygame.mixer.Sound(mp3bytes).play()
        elif self.SFX_STYLE == "native":
            system(f"say {word} --rate 150")
        elif self.SFX_STYLE == "espeak":
            system(f"espeak '{word}'")


    def get_definition(self, word):
            
            definitions = []

            if self.read_definitions(word):
                definitions = self.read_definitions(word)
                print(f"Using local definitions storage for {word}")
                return definitions
            

            #print(f"Fetching {word}")

            dictURL = f'https://www.oxfordlearnersdictionaries.com/definition/english/{word}'
            
            headers = {"User-Agent": ""}

            resp = requests.get(dictURL, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')

            meaningsFound = soup.find_all('li', class_='sense')

            for eachMeaning in meaningsFound:
                try:
                    definitions.append(eachMeaning.find('span', class_='def').text)
                except:
                    continue
                
            if len(definitions) == 0:
                try:
                    #print("Attempting Protocol 2")
                    definitions = list(PyDictionary().meaning(word).values())[0]
                except:
                    #print("Fallback on Protocol 3")
                    dictURL = f"https://www.dictionary.com/browse/{word}"

                    headers = {"User-Agent": ""}
                    definitions = []

                    resp = requests.get(dictURL, headers=headers)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    dom = etree.HTML(str(soup))
                    res = dom.xpath('//*[@id="top-definitions"]/div[1]/section[1]/div/div/ol/li/div')
                    meaning = res[0].getchildren()[0].text

                    definitions.append(meaning)
            
            self.store_definition(self.current_word, definitions)
            print(f"Added {word} to storage")

            return definitions

    def store_definition(self, word, definitions):
     with open(f"cache/definitions/{word}.txt", 'w') as f:
          f.write("\n".join(definitions[:2])) if len(definitions) > 1 else f.write(definitions[0])

    def read_definitions(self, word):
        definitionLocation = f"cache/definitions/{word}.txt"
        if os.path.exists(definitionLocation):
            with open(definitionLocation, 'r') as stored:
                local_def = stored.readlines()
            return local_def
        return None

    def rebuild_cache(self):

        self.rebuild_button.config(text="Rebuilding...")

        self.formatted_words = []

        for word in self.words:
            if "*" in word:
                for variation in word.split(" ")[1:]:
                    self.formatted_words.append(variation)
            else:
                self.formatted_words.append(word)

        self.CURRDIR = os.getcwd()

        if os.path.exists("cache/definitions"):
            shutil.rmtree("cache/definitions")
        os.mkdir("cache/definitions")

        print("Purged Cache")

        self.rebuild_button.config(text="Rebuilding")
        self.rebuild_button.config(state="disabled")

        workers = []

        rebuild_start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.worker_definitions, self.formatted_words)
        
        if os.path.exists("cache/definitions/.txt"):
            os.remove("cache/definitions/.txt")


        print(f"********************* Cache rebuilt [{len(self.words)} words] in {round(time.perf_counter()-rebuild_start, 2)} seconds *********************")
        self.rebuild_button.config(text="Cache Rebuilt")

    def worker_definitions(self, word):
        self.store_definition(word, self.get_definition(word))



    def record(self, word, result):
        self.internal_record['practiced'].append(word)
        self.internal_record[result].append(word)
        print("\n\n")
        print(f"Updated accuracy of {word} to [{self.internal_record['correct'].count(word)}:{self.internal_record['incorrect'].count(word)}]\n\n")


class Adaptation(Exception):
    pass

class AdaptationCurve:
    HERE = os.getcwd()
    
    def __init__(self):
        self.processingData = None
        self.bias = None

        self.refresh_data()

    def refresh_data(self):
        self.historyPath = f'{self.HERE}'
        self.historyFile = f"{self.historyPath}/history.txt"
        
        if os.path.exists(self.historyFile) == False:
            self.bias = None
            init_hist = open(self.historyFile, 'w')
            init_hist.write("")
            init_hist.close()
        if len(open(self.historyFile, 'r').read()) != 0:
            print("Applying past metrics:")

        with open(self.historyFile, 'r') as results:
            self.processingData = results.readlines()

        if not self.processingData:
            logging.warning("No previous data found")
            self.bias = None
            #raise Adaptation('No Previous Data Found')
        
        if len(self.processingData) != 0:
            return "Metrics Loaded"

    def extrapolate(self):
        curve = {}
        try:
            if self.processingData:
                for line in self.processingData:
                    terms = line.split(" ")
                    assert len(terms) == 3
                    curve[terms[0]] = 1 - (int(terms[1]) / (int(terms[1]) + int(terms[2])))
                    if curve[terms[0]] == 0:
                        curve[terms[0]] = 0.1
                    elif curve[terms[0]] == 1:
                        curve[terms[0]] = 0.7

            self.bias = curve
            return curve
                        
        except:
            logging.warning("Error: History file corrupted.")
            logging.warning("Resolving...")
            os.remove(self.historyFile)
            return None


        return "No Data"
    
    def start(self):

        if platform.system() != "Darwin":
            logging.warning("Warning: This program only runs without an internet connection on MacOS")
            SFX_STYLE = "gTTS"
        else:
            SFX_STYLE = "native"
        
        SFX_STYLE = "native"
        if (SFX_STYLE == "gTTS"):
            pygame.mixer.init()
        print(f"Using {SFX_STYLE} tts")

        style = Style(theme="superhero")
        root = style.master
        random.seed(datetime.now().timestamp())
        
        if self.bias:
            print("Starting with learning curve")
            app = SpellingGame(root, style, SFX_STYLE=SFX_STYLE, learningCurve=self.bias)
            root.mainloop()
        else:
            print("Starting default words list")
            app = SpellingGame(root, style, SFX_STYLE=SFX_STYLE)
            root.mainloop()

    '''

    #os.chdir("/Users/anju/Documents/Projects/Python")

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

    #controller = AdaptationCurve()

    app = SpellingGame(root, style)
    root.mainloop()
    '''


'''
if __name__ == "__main__":
    controller = AdaptationCurve()
    analyze = controller.extrapolate()

    if analyze == None:
        controller.refresh_data()

    print(controller.extrapolate())
    controller.start()

'''

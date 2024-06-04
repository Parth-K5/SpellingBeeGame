import requests
from git import Repo
from platform import system
import os
import sys
import shutil
from time import sleep, perf_counter
from random import randint

class UpdaterErrors(Exception):
    pass

class Updater:
    def __init__(self):
        self.LAUNCH_PATH = os.getcwd()
        self.PACKAGED_PATH = None
        self.ID = self.report_version()

    def check_update(self):
        cachedBypass = randint(1, 999999999999)
        try:
            r = requests.get(f"https://raw.githubusercontent.com/parthk5/SpellingBeeGame/main/version.txt?{cachedBypass}")
        except:
            self.notify("Spelling Bee Game", "No Internet. Please reconnect and try again")
            raise UpdaterErrors("No Internet. Please reconnect to the internet and try again")
            exit(0)
        self.rawFutureID = r.text
        
        latest = int(r.text.replace(".", ""))

        self.futureID = latest


        with open("version.txt", 'r') as verFile:
            currVer = int(verFile.read().replace(".", ""))

        #print(f"Latest: {latest}")
        #print(f"Current: {currVer}")

        return self.ID != self.rawFutureID
        


    def download(self, versionID):
        if system() == "Darwin":
            download_dir = f"/Users/{os.environ['USER']}/Desktop/SBG-{versionID}"
            self.PACKAGED_PATH = download_dir
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        Repo.clone_from("https://github.com/parthk5/SpellingBeeGame", download_dir)


    def run_update(self):
        print(f"Update function launchPath: {self.LAUNCH_PATH}")
        print(f"Update function targetPath: {self.PACKAGED_PATH}")
        os.system(f"python3 {self.PACKAGED_PATH}/update.py '{self.PACKAGED_PATH}' '{self.LAUNCH_PATH}'")

    def report_version(self):
        with open("version.txt", 'r') as verFile:
            currVer = verFile.read()
        return currVer
    

    def notify(self, title, text):
        os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


if __name__ == "__main__":
    updater = Updater()

    if updater.check_update():
        print(f"New Update available. v{updater.ID} -> v{updater.rawFutureID}")
        #updater.download(updater.futureID)
        #updater.run_update()
        #exit("Quitting")
    else:
        print(f"No new update available. Latest: v{updater.report_version()}")

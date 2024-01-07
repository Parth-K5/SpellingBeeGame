import requests
from git import Repo
from platform import system
import os
import sys
import shutil
from time import sleep, perf_counter
class Updater:
    def __init__(self):
        self.LAUNCH_PATH = os.getcwd()
        self.PACKAGED_PATH = None
        self.ID = self.report_version()

    def check_update(self):
        r = requests.get("https://raw.githubusercontent.com/parthk5/SpellingBeeGame/main/version.txt")
        latest = int(r.text.replace(".", ""))

        self.futureID = latest

        with open("version.txt", 'r') as verFile:
            currVer = int(verFile.read().replace(".", ""))

        #print(f"Latest: {latest}")
        #print(f"Current: {currVer}")

        return latest > currVer


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
        os.system(f"python3 {self.PACKAGED_PATH}/update.py {self.PACKAGED_PATH} {self.LAUNCH_PATH}")

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
        startUpdate = perf_counter()

        updater.notify("Spelling Bee Game", f"Updating from {updater.ID} to {updater.futureID}")
        sleep(3)

        updater.download(updater.futureID)
        updater.run_update()

        elapsedTime = perf_counter - startUpdate

        updater.notify("Spelling Bee Game", f"Spelling Bee Game was updated to version {updater.report_version} (Elapsed: {elapsedTime}). Please reopen the application")
        sleep(2)

        exit("Quitting")
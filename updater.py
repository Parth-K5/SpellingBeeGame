import requests
from git import Repo
from platform import system
import os
import sys


class Updater:
    def __init__(self):
        self.LAUNCH_PATH = os.getcwd()
        self.PACKAGED_PATH = None
        self.newestID = self.report_version()

    def check_update(self):
        r = requests.get("https://raw.githubusercontent.com/parthk5/SpellingBeeGame/main/version.txt")
        latest = int(r.text.replace(".", ""))

        self.newestID = latest

        with open("version.txt", 'r') as verFile:
            currVer = int(verFile.read().replace(".", ""))

        #print(f"Latest: {latest}")
        #print(f"Current: {currVer}")

        return latest > currVer


    def download(self, versionID):
        if system() == "Darwin":
            download_dir = f"/Users/{os.environ['USER']}/Desktop/SBG-{versionID}"
            self.PACKAGED_PATH = download_dir
        Repo.clone_from("https://github.com/parthk5/SpellingBeeGame", download_dir)


    def run_update(self):
        os.system(f"python3 {self.PACKAGED_PATH}/update.py {self.LAUNCH_PATH}", shell=True)

    def report_version(self):
        with open("version.txt", 'r') as verFile:
            currVer = verFile.read()
        return currVer

if __name__ == "__main__":
    updater = Updater()

    if updater.check_update():
        updater.download(updater.newestID)
        updater.run_update()
        exit("Applying Update")
from setuptools import setup, find_packages
import shutil
import os

setup(
    name="SpellingBeePractice",
    description="GUI application to practice for the spelling bee",
    author="Parth Khanna",
    install_requires=['pygame', 'ttkbootstrap', 'gtts'],
    entry_points={
        "console_scripts": [
            "spellgame=SpellingBeePractice:play",],
    }
)

shutil.rmtree('build')
shutil.rmtree('dist')
shutil.rmtree('SpellingBeePractice.egg-info')

os.system("pyinstaller --hidden-import=gtts --hidden-import=ttkbootstrap --hidden-import=pygame --onefile SpellingBeePractice.py")

shutil.rmtree('build')
os.remove("SpellingBeePractice.spec")
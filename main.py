import SpellingBeePractice
import os
import shutil
import platform
import updater

PROJECT_PATH = os.getcwd()


if platform.system() == "Darwin":
    os.chdir(f"/Users/{os.environ['USER']}/Desktop")
    for file in os.listdir():
        if "SBG-" in file:
            print("Found previous update files")
            shutil.rmtree(file)
            print("Cleaned old update files")


os.chdir(PROJECT_PATH)


updater = updater.Updater()

if updater.check_update():
    print("New Update Found")
    updater.download(updater.futureID)
    updater.notify("Spelling Bee Game", f"Updating game from {updater.ID} to {updater.futureID}")
    updater.run_update()
    updater.notify("Spelling Bee Game", f"Spelling Bee updated to v{updater.report_version()}. Please reopen it")
else:
    print("No Update Available")


controller = SpellingBeePractice.AdaptationCurve()
analyze = controller.extrapolate()

if analyze == None:
    controller.refresh_data()

print(controller.extrapolate())
controller.start()
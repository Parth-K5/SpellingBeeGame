import SpellingBeePractice
import os
import shutil
import platform
import updater

TEMP_UPDATE_PATH = f"/Users/{os.environ['USER']}/Desktop/SGB-Update"

if platform.system() == "Darwin":
    if os.path.exists(TEMP_UPDATE_PATH):
        shutil.rmtree(TEMP_UPDATE_PATH)


updater = updater.Updater()

if updater.check_update():
    updater.download(updater.newestID)
    updater.run_update()
    exit("Applying Update")
else:
    print(f"Spelling Bee game is at the latest version: {updater.report_version()}")


controller = SpellingBeePractice.AdaptationCurve()
analyze = controller.extrapolate()

if analyze == None:
    controller.refresh_data()

print(controller.extrapolate())
controller.start()

import shutil
import os
import sys
import stat

def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)


def install(installPath):
    updatePATH = os.getcwd().split("/")[-1]
    os.system("cd ..")

    if os.path.exists(installPath):
        shutil.rmtree(installPath, onerror=remove_readonly)
    
    shutil.coptree(updatePATH, installPath)
    exit("Update Applied")

install(sys.argv[1])
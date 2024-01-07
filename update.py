import shutil
import os
import sys
import stat

def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)


def install(installPath):
    updatePATH = os.path.basename(os.getcwd())
    os.chdir("..")

    if os.path.exists(installPath):
        shutil.rmtree(installPath, onerror=remove_readonly)

    
    os.mkdir(installPath)
    shutil.copytree(updatePATH, installPath, symlinks=True, dirs_exist_ok=True)
    exit("Update Applied")

install(sys.argv[1])
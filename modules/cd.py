from os import chdir, getcwd

def cd(command):
    path = " ".join(command.args)
    command.progress = f"{OK} Changing working directory to {path}"
    chdir(path)
    return getcwd()

OK = "[+]"

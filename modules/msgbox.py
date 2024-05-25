import ctypes

def msgbox(command):
    msg = " ".join(command.args)
    return str(ctypes.windll.user32.MessageBoxW(0, msg, "Message", 0x40))

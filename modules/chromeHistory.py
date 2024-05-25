from subprocess import Popen
import sqlite3
from os import getcwd

def gethistory(command):
    command.progress = f"{OK} Terminating chrome"
    Popen("TASKKILL /IM chrome.exe", shell=True)

    command.progress = f"{OK} Opening chrome history database"
    con = sqlite3.connect('C:\\Users\\Sen\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History')
    cursor = con.cursor()
    cursor.execute("SELECT url FROM urls")
    urllist = cursor.fetchall()
    history = []

    command.progress = f"{OK} Retrieving chrome history"
    for urltuple in urllist:
        for url in urltuple:
            u = (url.replace("https://", "")).replace("www.","").split("/")[0]
            history.append(u)

    history_dict = {i:history.count(i) for i in history}
    sortedurls = sorted(history_dict.items(),key=lambda x:x[1])

    string = ""
    for key, value in sortedurls:
        string+=f"{key} {value}\n"

    command.progress = f"{OK} writing chrome history to file"
    with open("history.txt","w") as f:
        f.write(string)

    return f"Done retrieving chrome history : {getcwd()}\\history.txt"

OK = "[+]"

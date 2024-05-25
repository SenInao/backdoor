class Command:
    _next_id = 1
    def __init__(self, command:str, args:list, id=None) -> None:
        if id is None:
            self._id = Command._next_id
            Command._next_id += 1
        else:
            self._id = id

        self.output = command != "detatched" 
        if not self.output:
            self.command = args[0]
            self.args = args[1:]
        else:
            self.command = command
            self.args = args

        self.progress = None

        self.shouldRun = True
        self.running = False
        self.done = False
        self.success = True
        self.result = None
        self.file = None
   
def findById(id:int, commands:list):
    for command in commands:
        if id == command._id:
            return command

    return False

OK = "[+]"

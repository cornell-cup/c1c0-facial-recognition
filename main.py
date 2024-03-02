import time, os # Default Python Libraries

from client.client import * # Importing The Client/Task Manager

# Global Variables (Sleep Time For Ability To See Results, Is Not Needed)
SLEEP_TIME: float = 1

def create_client(load: bool = False, disp: bool = False, prnt: bool = False) -> Client:
    """
    Creates a client with the given parameters. Needed for this file to be used by
    `importlib` from scheduler.

    PARAMETERS
    ----------
    load - Whether the client should load from a given directory.
    disp - Whether the client should display the images & bounding boxes.
    prnt - Whether the client should print intermediate results.

    RETURNS
    -------
    Client - The created client.
    """

    return Client(load=load, disp=disp, prnt=prnt)

def execute_task(client: Client, command: str, args: List[str] = None) -> any:
    """
    Executes a task with the given command and arguments. Needed for this file to be
    used by `importlib` from scheduler.

    PARAMETERS
    ----------
    client - The client to execute the task with.
    command - The command to execute.
    args - The arguments to execute the command with.

    RETURNS
    -------
    any - The result of the task (depends on the function, but usually a List[str])
    """

    task = client.interpret_task(command);
    return task(args)

if __name__ == '__main__':
    client: Client = create_client(load=False, disp=True, prnt=True) # Creating The Client

    while True:
        # Clearing Terminal & Getting Inputs
        os.system('cls' if os.name == 'nt' else 'clear')
        inputs = input().split(' ')
        command, args = inputs[0].lower(), inputs[1:]

        # Parsing Commands, Running Tasks, & Sleeping For Ability To See Results
        if (command == 'exit' or command == 'e'): break
        if (command == 'quit' or command == 'q'): break
        execute_task(client, command, args)
        time.sleep(SLEEP_TIME)

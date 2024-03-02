import time, os

from client.client import *

# Global variables
SLEEP_TIME: float = 1

def execute_task(client: Client, command: str, args: List[str] = None) -> None:
    task = client.interpret_task(command);
    return task(args)

if __name__ == '__main__':
    client: Client = Client(load=False)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        inputs = input().split(' ')
        command, args = inputs[0].lower(), inputs[1:]

        if (command == 'exit' or command == 'e'): break
        if (command == 'quit' or command == 'q'): break
        execute_task(client, command, args)
        time.sleep(SLEEP_TIME)

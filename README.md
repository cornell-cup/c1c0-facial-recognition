# Facial Recognition

### Overview

This repository implements functionality for the recognition and learning of various faces. It provides a terminal interface in which commands can be read and executed repeatedly. Most of the command processing happens in the `client` folder, with some additional utilities found in `cache.py`. Recognition and learning commands compare against and add to a cache in order to improve efficiency. The makefile commands are specified below in the order they should be run:

`make venv`: Creates the virtual environment (different versions for different OS's).

`make install`: Installs all required python packages & image magick (for image processing).

`make cache`: Pulls images from the Cornell Cup Robotics website and adds them to the cache.

`make [all]`: Starts the facial recognition client and camera, ready to execute commands.

`make clean`: Removes the cached images and any python cache files.

### File Structure

```py
.cache/ # Folder Containing Cached & Processed Images

client/ # Folder Containing Various Utilities
|-- __init__.py # Making Client A Package
|-- camera.py   # Utilities For Opening & Reading From A Camera
|-- classify.py # Utilities For Recognition & Learning
|-- client.py   # Utilities For Command Parsing & Runtime Management
|-- config.py   # Configuration Variables

resources/ # Folder Containing Data Files
|-- examples/ # Folder Containing Example Classifications
|   |-- 70-3-2.jpg   # Image With 70% Scale, 3 Upsamples, 2 Jitters
|   |-- 80-2-2.jpg   # Image With 80% Scale, 2 Upsamples, 2 Jitters
|   |-- 80-4-2.jpg   # Image With 80% Scale, 4 Upsamples, 2 Jitters
|   |-- 100-4-2.jpg  # Image With 100% Scale, 4 Upsamples, 2 Jitters
|   |-- original.jpg # Original Image
|-- people/ # Folder Containing People Images To Load
|   |-- Christopher_De_Jesus.jpeg # Image Of Christopher De Jesus (Dev Of This Repo)
|   |-- Dave_Schneider.jpg        # Image Of Dave Schneider (Cornell Cup Robotics Advisor)
|   |-- Mohammad_Khan.jpg         # Image Of Mohammad Khan (Dev Of This Repo)
|   |-- Yashraj_Sinha.jpeg        # Image Of Yashraj Sinha (CS Lead At The Time)

.gitignore       # Git Ignore Specifications
cache.py         # Pre-Caching Program
main.py          # Command Parsing Program
makefile         # Build & Run Commands
README.md        # Information File
requirements.txt # Required Python Packages
```

### Miscellaneous

Other images (not from the website) can be cached as well, as long as the URL and filename parsing are relatively nice. Issues could arise when website is updated, but can be fixed by changing URL and filename parsing to match the website structure. Note that there might be the file `facial_comm.py` in this repository, and that is a file specifically for communicating with scheduler. It should be updated when massive updates to this repository are made. There are some bugs with the display that may occur, to fix them just rerun the program.

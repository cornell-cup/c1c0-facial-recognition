import subprocess, requests, shutil, sys, bs4, re, os # Default Python libraries

from client.client import * # Importing The Client/Task Manager
from client.config import * # Importing The Config File

from typing import List # Type Hinting

# Global Variables Not In Config (Specific For Caching Only)
SITE: str          = "https://cornellcuprobotics.com/"
OUTPUT_PATH: str   = "resources/cache/"
DOWNLOAD_PATH: str = "resources/download/"
SIZE: str          = "900x600!"
EXT: str           = ".JPG"

def convert(urlname: str) -> str:
    """
    Converts a given HTTP URL name to an acceptable file name, by stripping,
    removing certain words, and adding spaces.

    PARAMETERS
    ----------
    urlname - The URL name to convert.

    RETURNS
    -------
    str - The converted URL name.
    """

    rmwords: List[str] = ["C1C0CS", "BIZCOMM", "MINIBOTCS", "ECE", "_", "-"]
    for rmword in rmwords: urlname = urlname.replace(rmword, "")

    for i in range(1, len(urlname)):
        if urlname[i].isupper():
            urlname = urlname[:i] + " " + urlname[i:]
            break
    return urlname.strip()

def cache_website() -> None:
    """
    Pulls all files from the members page of the Cornell Cup Robotics website, filters
    for specific image types, downloads them to a temporary directory, converts them
    to a specific size using imagemagick, and then loads them onto the cache through
    the client. Removes the temporary directories after completion.
    """
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    response: requests.Response = requests.get(SITE + "members.html")
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, 'html.parser')
    tags: List[bs4.element.Tag] = soup.find_all('img')

    urls: List[str] = [img['src'] for img in tags]
    urls: List[str] = [img for img in urls if EXT in img]

    for i, url in enumerate(urls):
        urlname: str = re.search(r'/([\w_-]+[.]JPG)$', url).group(1)
        downloadname: str = DOWNLOAD_PATH + urlname[:-4] + ".jpg"

        filename: str = OUTPUT_PATH + convert(urlname[:-4]) + ".jpg"

        with open(downloadname, 'wb') as f:
            if 'http' not in url: url = '{}{}'.format(SITE, url)
            response = requests.get(url)
            f.write(response.content)

        cmdname = "magick" if MAC_MODE else "convert"
        subprocess.call([cmdname, downloadname, "-resize", SIZE, filename])
        print(f"Finished downloading image {i:02}: {url}")

    print("Started loading all images onto cache.")
    _ = Client(path=OUTPUT_PATH, open=False)
    print("Finished loading all images onto cache.")

    shutil.rmtree(DOWNLOAD_PATH)
    shutil.rmtree(OUTPUT_PATH)

def cache_images(filenames: str) -> None:
    """
    Extracts the file paths and makes sure they exists/are valid, then converts
    them to a specific size using imagemagick, and then loads them onto the cache.
    Removes the temporary directories after completion.
    """

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    for filename in filenames:
        if (not os.path.exists(filename)):
            print(f"File {filename} does not exist, exiting.")
            return

        a_index: int = filename.rfind("/")+1 if "/" in filename else 0
        b_index: int = filename.rfind(".") if "." in filename else len(filename)
        diffname: str = OUTPUT_PATH + convert(filename[a_index:b_index]) + ".jpg"

        cmdname = "magick" if MAC_MODE else "convert"
        subprocess.call([cmdname, filename, "-resize", SIZE, diffname])
        print(f"Converted {filename} to {diffname}")

    print("Started loading all images onto cache.")
    _ = Client(path=OUTPUT_PATH, open=False)
    print("Finished loading all images onto cache.")

    shutil.rmtree(OUTPUT_PATH)

if __name__ == '__main__':
    # If No Arguments, Cache The Cornell Cup Robotics Website
    if len(sys.argv) == 1: cache_website()
    # Else, Cache The Given Files From Arguments
    else: cache_images(sys.argv[1:])

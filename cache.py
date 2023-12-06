import subprocess, requests, shutil, sys, bs4, re, os

from client.client import *
from client.config import *

from typing import List

# Global variables
SITE: str          = "https://cornellcuprobotics.com/"
OUTPUT_PATH: str   = "resources/cache/"
DOWNLOAD_PATH: str = "resources/download/"
SIZE: str          = "900x600!"
EXT: str           = ".JPG"

def convert(urlname: str) -> str:
	rmwords: List[str] = ["C1C0CS", "BIZCOMM", "MINIBOTCS", "ECE", "_", "-"]
	for rmword in rmwords: urlname = urlname.replace(rmword, "")

	for i in range(1, len(urlname)):
		if urlname[i].isupper():
			urlname = urlname[:i] + " " + urlname[i:]
			break
	return urlname.strip()

def cache_website() -> None:
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

        subprocess.call(["convert", downloadname, "-resize", SIZE, filename])
        print(f"Finished downloading image {i:02}: {url}")

    print("Started loading all images onto cache.")
    _ = Client(path=OUTPUT_PATH, open=False)
    print("Finished loading all images onto cache.")

    shutil.rmtree(DOWNLOAD_PATH)
    shutil.rmtree(OUTPUT_PATH)

def cache_images(filenames: str) -> None:
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    for filename in filenames:
        if (not os.path.exists(filename)):
            print(f"File {filename} does not exist, exiting.")
            return

        a_index: int = filename.rfind("/")+1 if "/" in filename else 0
        b_index: int = filename.rfind(".") if "." in filename else len(filename)
        diffname: str = OUTPUT_PATH + convert(filename[a_index:b_index]) + ".jpg"

        subprocess.call(["convert", filename, "-resize", SIZE, diffname])
        print(f"Converted {filename} to {diffname}")

    print("Started loading all images onto cache.")
    _ = Client(path=OUTPUT_PATH, open=False)
    print("Finished loading all images onto cache.")

    shutil.rmtree(OUTPUT_PATH)

if __name__ == '__main__':
    if len(sys.argv) == 1: cache_website()
    else: cache_images(sys.argv[1:])

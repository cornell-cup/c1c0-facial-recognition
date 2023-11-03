import subprocess, requests, shutil, bs4, re, os
from typing import List

from client.client import *
from client.config import *

# Global Variables
SITE: str          = "https://cornellcuprobotics.com/"
OUTPUT_PATH: str   = "resources/cache/"
DOWNLOAD_PATH: str = "resources/download/"
SIZE: str          = "900x600!"
PORT: int          = 1233
EXT: str           = ".JPG"
IP: str            = "127.0.0.1"

if __name__ == '__main__':
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
		filename: str = OUTPUT_PATH + urlname[:-4] + ".jpg"

		with open(downloadname, 'wb') as f:
			if 'http' not in url: url = '{}{}'.format(SITE, url)
			response = requests.get(url)
			f.write(response.content)

		subprocess.call(["convert", downloadname, "-resize", SIZE, filename])
		print(f"Finished downloading image {i:02}: {url}")

	print("Started loading all images onto cache.")
	client: Client = Client(path=OUTPUT_PATH, ip=IP, load=DEFAULT_LOAD, port=PORT, cache_location=DEFAULT_CACHE_LOCATION, dev=None)
	print("Finished loading all images onto cache.")

	shutil.rmtree(DOWNLOAD_PATH)
	shutil.rmtree(OUTPUT_PATH)

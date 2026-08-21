from bs4 import BeautifulSoup
import requests
from pprint import pprint
import os
import subprocess

# 清除螢幕的魔法
_ = subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
import requests
from bs4 import BeautifulSoup

aaa = requests.get("http://hyogo-animalhospital.com/%e7%8a%ac%e3%81%ab%e9%96%a2%e3%81%99%e3%82%8b%e8%a8%98%e4%ba%8b/%e7%8a%ac%e4%bd%95%e7%a8%ae%e6%b7%b7%e5%90%88%e3%83%af%e3%82%af%e3%83%81%e3%83%b3/")
soup = BeautifulSoup(aaa.text)

print(soup.find("p"))

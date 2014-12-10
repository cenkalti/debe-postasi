#!/usr/bin/env python3
"""
Run with following command: PYTHONIOENCODING=utf-8 python3 debe.py > debe.html

"""
import asyncio

import requests
from bs4 import BeautifulSoup

URL_BASE = "https://eksisozluk.com"
PATH_DEBE = "/debe"


def generate_html():
    resp_debe = requests.get(URL_BASE + PATH_DEBE)
    soup_debe = BeautifulSoup(resp_debe.text)

    ol = soup_debe.find(id="content-body").find("ol")

    @asyncio.coroutine
    def fetch_entry(li):
        for a in li.find_all("a"):
            if a["href"].startswith("/"):
                a["href"] = URL_BASE + a["href"]

        a = li.find("a")
        resp_entry = requests.get(a["href"])
        soup_entry = BeautifulSoup(resp_entry.text)
        content = soup_entry\
            .find("ol", id="entry-list")\
            .find("li")\
            .find("article")\
            .find("div", class_="content")

        for a in content.find_all("a"):
            if a["href"].startswith("/"):
                a["href"] = URL_BASE + a["href"]

        li.append(soup_debe.new_tag("br"))
        li.append(content)
        li.append(soup_debe.new_tag("br"))

    loop = asyncio.get_event_loop()
    tasks = [asyncio.async(fetch_entry(li)) for li in ol.find_all("li")]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    return "<!DOCTYPE html>\n<html><head><meta charset=\"UTF-8\"></head>" \
           "<body><h1>dünün en beğenilen entry'leri</h1>" + \
           ol.encode().decode() + \
           "<hr><a href=\"%Link:Unsubscribe%\">bu e-postaları artık almak " \
           "istemiyorsaniz tıklayın</a></body></html>"


if __name__ == "__main__":
    print(generate_html())

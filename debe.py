#!/usr/bin/env python3
"""
Run with following command: PYTHONIOENCODING=utf-8 python3 debe.py > debe.html

"""
import os
from io import StringIO

from requests import Session
from requests.exceptions import RequestException
import backoff
from bs4 import BeautifulSoup

URL_BASE = "https://eksisozluk.com"
PATH_DEBE = "/debe"
RETRY_COUNT = 8

headers = {
    'User-Agent': 'curl/7.43.0',
}

proxies = {}
proxy = os.getenv('PROXY')
if proxy:
    proxies['https'] = proxy

session = Session()


class ParseError(Exception):
    pass


@backoff.on_exception(backoff.expo,
                      RequestException,
                      max_tries=RETRY_COUNT)
def get_url(url):
    return session.get(URL_BASE + url, headers=headers, proxies=proxies)


def generate_html():
    s = StringIO()
    s.write(
        '<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"></head>\n'
        "<body><h1>dünün en beğenilen entry'leri</h1>\n")

    titles = get_titles()
    for i, title in enumerate(titles, 1):
        content = get_content(title)
        s.write('<h2 style="text-transform: uppercase">')
        s.write(str(i))
        s.write('. <a href="')
        s.write(URL_BASE)
        s.write(title['href'])
        s.write('">')
        s.write(title['title'])
        s.write('</a></h2>\n')
        s.write(content['content'])
        s.write('\n')
        if not content['not_found']:
            s.write('<p>yazar: <a href="')
            s.write(URL_BASE)
            s.write(content['author_href'])
            s.write('">')
            s.write(content['author'])
            s.write('</a> tarih: ')
            s.write(content['date'])
            s.write('</p>\n')

    s.write("</body></html>")
    return s.getvalue()


def get_titles():
    resp = get_url(PATH_DEBE)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    ret = []
    ol = soup.find("nav", id="partial-index").find("ul", class_="topic-list")
    for li in ol.find_all("li"):
        a = li.find("a")
        href = a["href"]
        title = a.find("span", class_="caption").string
        ret.append({"title": title, "href": href})

    return ret


def get_content(title):
    author = None
    author_href = None
    date = None
    not_found = True
    resp = get_url(title["href"])
    # resp = get_url("/entry/948321421")
    soup = BeautifulSoup(resp.text, "html.parser")
    if resp.status_code == 404:
        topic = soup.find(id="topic")
        content = topic.find("p")
    elif resp.status_code == 200:
        ul = soup.find("ul", id="entry-item-list")
        li = ul.find("li")
        content = li.find("div", class_="content")
        add_base_url(content)
        content.name = "p"
        entry_author = ul.find(class_="entry-author")
        author = entry_author.string
        author_href = entry_author['href']
        date = ul.find(class_="entry-date").string
        not_found = False
    else:
        raise ParseError

    return {
            "not_found": not_found,
            "content": str(content),
            "author": author,
            "author_href": author_href,
            "date": date,
    }


def add_base_url(elem):
    for a in elem.find_all("a"):
        if a["href"].startswith("/"):
            a["href"] = URL_BASE + a["href"]


if __name__ == "__main__":
    print(generate_html())

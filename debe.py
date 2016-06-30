#!/usr/bin/env python3
"""
Run with following command: PYTHONIOENCODING=utf-8 python3 debe.py > debe.html

"""
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

URL_BASE = "https://eksisozluk.com"
PATH_DEBE = "/debe"
MAX_WORKERS = 10

headers = {
    'User-Agent': 'curl/7.43.0',
}


def generate_html():
    session = FuturesSession(max_workers=MAX_WORKERS)
    resp_debe = session.get(URL_BASE + PATH_DEBE, headers=headers).result()
    soup_debe = BeautifulSoup(resp_debe.text, "html.parser")
    ol = soup_debe.find(id="content-body").find("ol")
    add_base_url(ol)

    # fetch enries in parallel
    futures = []
    for li in ol.find_all("li"):
        a = li.find("a")
        f = session.get(a["href"], headers=headers)
        futures.append((li, f))

    # inject into the list
    for li, f in futures:
        resp_entry = f.result()
        soup_entry = BeautifulSoup(resp_entry.text, "html.parser")
        content_body = soup_entry.find(id="content-body")
        topic = content_body.find(id="topic")
        not_found = topic.attrs.get("data-not-found") == "true"
        if not_found:
            content = topic.find("p")
        else:
            content = soup_entry\
                .find(id="entry-list")\
                .find("div", class_="content")
            add_base_url(content)
            content.name = "p"

        li.append(content)

        # move author below the entry
        author = li.find("a").find("div", class_="detail").extract()
        author_href = "%s/biri/%s" % (URL_BASE, author.string)
        author_a = soup_entry.new_tag("a", href=author_href)
        author_a.string = author.string
        author_p = soup_entry.new_tag("p")
        author_p.string = "yazar: "
        author_p.append(author_a)
        li.append(author_p)

    return "<!DOCTYPE html>\n<html><head><meta charset=\"UTF-8\"></head>" \
           "<body><h1>dünün en beğenilen entry'leri</h1>" + \
           ol.encode().decode() + "<hr></body></html>"


def add_base_url(elem):
    for a in elem.find_all("a"):
        if a["href"].startswith("/"):
            a["href"] = URL_BASE + a["href"]


if __name__ == "__main__":
    print(generate_html())

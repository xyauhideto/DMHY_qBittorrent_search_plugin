
#VERSION: 1.00
#AUTHORS: xyau (xyauhideto@gmail.com)

# MIT License
#
# Copyright (c) 2018 xyau
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the right
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software i
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# qBT
if __name__ == "__main__":
    import os
    import sys
    root_path = os.path.abspath(__file__)
    root_path = "\\".join(root_path.split("\\")[:-2])
    sys.path.append(root_path)
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter

# parser
from html.parser import HTMLParser
from enum import Enum
from re import compile as re_compile
class dmhyorg(object):
    class InfoParser(HTMLParser):
        class ParseStep(Enum):
            nothingTodo = -1
            onFoundTable = 0
            onFoundSearch = 1
            onFoundTitle = 2
            onParseTitle = 21
            onParseLink = 3
            onFindingSize = 4
            onParseSize = 41
            onFindingSeeds = 5
            onParseSeeds = 51
            onParseDone = 6
        def __init__(self,url):
            HTMLParser.__init__(self)
            self.url = url
            self.step = self.ParseStep.nothingTodo
            self.empty()
        def empty(self):
            self.torrentInfo = {
                "link": "",
                "name": "",
                "size": "-1",
                "seeds": "-1",
                "leech": "-1",
                "engine_url": self.url,
                "desc_link": ""
            }
        def clipMagnetHref(self,url : str) -> str:
            pos = url.find("&")
            if pos != -1:
                return url[:pos]
            return url
        
        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            if tag == "div" and "clear" in params.get("class", "") and "table" in params.get("class", ""):
                self.step = self.ParseStep.onFoundTable

            if tag == "tbody" and self.step == self.ParseStep.onFoundTable:
                self.step = self.ParseStep.onFoundSearch

            if (self.step == self.ParseStep.onFoundSearch and "title" == params.get("class", "") and tag == "td"):
                self.step = self.ParseStep.onFoundTitle

            if self.step == self.ParseStep.onFoundTitle and tag == "a" and params.get("href", "").startswith("/topics/view/"):
                self.step =self.ParseStep.onParseTitle

            if self.step == self.ParseStep.onParseLink and "磁力下載" == params.get("title", "") and tag == "a":
                self.torrentInfo["link"] = self.clipMagnetHref(params.get("href", ""))
                self.step = self.ParseStep.onFindingSize

            if self.step == self.ParseStep.onFindingSize and tag == "td":
                self.step = self.ParseStep.onParseSize

            if self.step == self.ParseStep.onFindingSeeds and tag == "td":
                self.step = self.ParseStep.onParseSeeds

        def handle_endtag(self, tag):
            if self.step == self.ParseStep.onParseTitle and tag == "a":
                self.step = self.ParseStep.onParseLink
            if(self.step == self.ParseStep.onParseDone):
                self.torrentInfo["name"] = self.torrentInfo["name"].replace("\t","")
                self.torrentInfo["name"] = self.torrentInfo["name"].replace("\n","")
                prettyPrinter(self.torrentInfo)
                self.step = self.ParseStep.onFoundSearch
                self.empty()
            if self.step == self.ParseStep.onFoundTable and tag == "tbody":
                self.step = self.ParseStep.nothingTodo

        def handle_data(self, data):
            if self.step == self.ParseStep.onParseTitle:
                self.torrentInfo["name"] += data
            if self.step == self.ParseStep.onParseSize:
                self.torrentInfo["size"] = data
                self.step = self.ParseStep.onFindingSeeds
            if self.step == self.ParseStep.onParseSeeds:
                self.torrentInfo["seeds"] = data if data != "-" else "-1"
                self.step = self.ParseStep.onParseDone

            
    url = "https://share.dmhy.org"
    name = "DMHY"
    supported_categories = {"all":0,"anime":2,"pictures":3,"music":4,"tv":6,"games":9}

    def download_torrent(self, info):
        """ Downloader """
        print(download_file(info))

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat="all"):
        """ Performs search """

        def get_data(url):
            get_next = re_compile('(?s)"fl".+href="([^"]+)">下一')
            
            html = retrieve_url(url)
            next_page = get_next.search(html)
            parser = self.InfoParser(self.url)
            parser.feed(html)
            parser.close()
            return next_page and self.url + next_page.group(1)

        query = "%s/topics/list/?keyword=%s&sort_id=%d" % (
            self.url, what, self.supported_categories.get(cat, "0"))

        while query:
            query = get_data(query)

if __name__ == "__main__":
    engine = dmhyorg()
    engine.search("conan")

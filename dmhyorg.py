
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
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter

# parser
from html.parser import HTMLParser
from re import compile as re_compile

class dmhyorg(object):
    url = "https://share.dmhy.org"
    name = "DMHY"
    supported_categories = {"all":0,"anime":2,"pictures":3,"music":4,"tv":6,"games":9}

    def download_torrent(self, info):
        """ Downloader """
        print(download_file(info))

    class dmhy_list_parser(HTMLParser):
        """ Parser class """
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = None
            self.save_item_key = None

        def handle_starttag(self, tag, attrs):
            """ Parser"s start tag handler """
            if self.current_item:
                params = dict(attrs)
                if tag == "a":
                    link = params["href"]
                    if "/view/" in link and "target" in params:
                        # description link
                        self.current_item["desc_link"] = self.url+ link
                        self.save_item_key = "name"
                    elif link.startswith("magnet"):
                        self.current_item["link"] = link
                elif tag == "span" and "class" in params and params["class"].startswith("bt") and not "leech" in self.current_item:
                    self.save_item_key = "leech" if "seeds" in self.current_item else "seeds"
                elif tag == "td" and "link" in self.current_item and not "size" in self.current_item:
                    self.save_item_key = "size"
            elif tag == "tr":
                self.current_item = {}
                self.current_item["engine_url"] = self.url

        def handle_endtag(self, tag):
            """ Parser"s end tag handler """
            if self.current_item and tag == "tr":
                if all(key in self.current_item for key in ["name","link","size"]):
                    prettyPrinter(self.current_item)
                self.current_item = None

        def handle_data(self, data):
            """ Parser"s data handler """
            if self.save_item_key:
                save_item_value = data.strip()
                if "size" == self.save_item_key:
                    size = re_compile("([\d\.]+)(\w+)").search(save_item_value)
                    num = float(size.group(1))
                    unit = 2**(10*(1+'kmgtpezy'.find(size.group(2)[0].lower())))
                    save_item_value = str(int(num * unit))
                elif self.save_item_key in ["seeds", "leech"]:
                    save_item_value = 0 if "-" == save_item_value else int(save_item_value)
                self.current_item[self.save_item_key] = save_item_value
                self.save_item_key = None

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat="all"):
        """ Performs search """
        parser = self.dmhy_list_parser(self.url)

        def get_data(url):
            highlight = re_compile("<span class=\"keyword\">([^<]+)</span>")
            get_next = re_compile('(?s)"fl".+href="([^"]+)">下一')
            get_table = re_compile(
                "(?s)<table[^<]+topic_list.+<tbody>(.*)</tbody>.*</table>")
            html = retrieve_url(url)
            next_page = get_next.search(html)
            table = get_table.search(html)
            # clear highlighting
            return [table and highlight.sub(r"\1",table.group(1)),
                    next_page and self.url + next_page.group(1)]

        page_url = "%s/topics/list/?keyword=%s&sort_id=%d" % (
            self.url, what, self.supported_categories.get(cat, "0"))

        while page_url:
            [data,page_url] = get_data(page_url)
            parser.feed(data)

        parser.close()


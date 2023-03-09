
# VERSION: 2.00
# AUTHORS: xyau (xyauhideto@gmail.com)

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

try:
	from re import findall
except ModuleNotFoundError:
	pass

# import qBT modules
try:
    from novaprinter import prettyPrinter
    from helpers import retrieve_url
except ModuleNotFoundError:
    pass

class dmhyorg(object):
	url = "https://share.dmhy.org"
	name = "DMHY"
	supported_categories = {"all": 0, "anime": 2,
        "pictures": 3, "music": 4, "tv": 6, "games": 9}
	reg = '<tr\s+class="even"[\s\S]*?</td>\s+<td\s+class="title">\s+<a\s+href="([^"]+)"[^>]+>\s*([\s\S]+?)\s*<span\s+class="keyword">[\s\S]+?<td\s+nowrap="nowrap"\s+align="center">\s+<a\s+class="download-arrow arrow-magnet"\s+title="磁力下載"\s+href="([^"]+)">[^<]+</a>[\s\S]+?</td>\s+<td\s+nowrap="nowrap"\s+align="center">([^<]+)</td>[^<]+<td\s+nowrap="nowrap"\s+align="center"><span class="btl_1">(\d+)</span></td>[^<]+<td\s+nowrap="nowrap"\s+align="center"><span\s+class="bts_1">(\d+)</span></td>[^<]+<td\s+nowrap="nowrap"\s+align="center">(\d+)</td>'

	def get_data(self, url):
		html = retrieve_url(url)
		result = findall(self.reg, html)
		data, item = [], {}
		for v in result:
			item = {'link': v[2], 'name': v[1], 'desc_link': v[0], 'size': v[3],
                'seeds': v[4], 'leech': v[5], 'engine_url': self.url}
			data.append(item)
		return [data, len(data)]

	def search(self, what, cat="all"):
		page, cate = 1, self.supported_categories.get(cat, "0")

		while True:
			url = "{}/topics/list/page/{}?keyword={}&sort_id={}&team_id=0&order=date-desc".format(
			    self.url, page, what, cate)
			[data, len] = self.get_data(url)
			for item in data:
				prettyPrinter(item)
			if page >= 5 and len < 80:
				return
			++page

import datetime
import lxml.html
import xlrd

import scrapelib

from billy.scrape.bills import BillScraper, Bill
from billy.scrape.votes import Vote


def icols(page):
    headers = [x.value for x in page.row(0)]
    for row in range(1, page.nrows):
        yield dict(zip(headers, (x.value for x in page.row(row))))


class DCBillScraper(BillScraper):
    jurisdiction = 'dc'

    def lxmlize(self, url):
        page = self.urlopen(url)
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)
        return page

    def download_bill_index(self):
        CSV_URL = (
            "http://lims.dccouncil.us/_layouts/15/uploader/AdminProxy.aspx?"
            "keyword=&"
            "category=0&"
            "pageIndex=0&"
            "exportToCsv=true&"
            "chronological=false"
        )
        page = self.get(CSV_URL)
        return xlrd.open_workbook(file_contents=page.content)

    def scrape_history(self, page):
        pass

    def scrape_bills(self, page):
        for bill in icols(page):
            print(bill['Download URL'])

    def scrape(self, session, chambers):
        index = self.download_bill_index()
        methods = {"LegislativeSummary": self.scrape_history,
                   "BillHistory": self.scrape_bills}
        for sheet in index.sheets():
            methods[sheet.name](sheet)

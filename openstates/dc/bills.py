import datetime
import lxml.html
import xlrd
import json

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

    def get_legislation_public_data(self, bill_id):
        endpoint = "http://lims.dccouncil.us/_layouts/15/uploader/AdminProxy.aspx/GetPublicData"
        data = self.post(
            endpoint,
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/json; charset=UTF-8'
            },
            data='{"legislationId": "PR21-0006"}'
        )
        return json.loads(data.json()['d'])

    def scrape_history(self, page):
        pass

    def scrape_bills(self, page):
        map(self.scrape_bill, icols(page))

    def scrape_bill(self, bill):
        data = self.get_legislation_public_data(bill['Bill Number'])
        print(json.dumps(data, sort_keys=True, indent=4))

    def scrape(self, session, chambers):
        index = self.download_bill_index()
        methods = {"LegislativeSummary": self.scrape_history,
                   "BillHistory": self.scrape_bills}
        for sheet in index.sheets():
            methods[sheet.name](sheet)

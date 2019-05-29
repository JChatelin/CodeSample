from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
import time


class FillPriceTable(object):
    def __init__(self, event_url):
        self.event_url = event_url
        self.browser = webdriver.Chrome()

    def run(self):
        self.browser.get(self.event_url)
        try:
            if "Ticketmaster" not in self.browser.title:
                raise AssertionError
        except AssertionError:
            self.browser.implicitly_wait(10)
            self.browser.refresh()
        try:
            if "maintenance" in self.browser.page_source or \
                    "Maintenance" in self.browser.page_source:
                raise AssertionError
            prices_and_categories = self.collect_price()
            self.tear_down()
        except AssertionError:
            self.tear_down()
            prices_and_categories = self.run()
        return prices_and_categories

    def collect_price(self):
        """This function is there to make sure that the collect_price_by_category is execute
            properly whether there is a show price table link or not"""
        try:
            self.browser.implicitly_wait(5)
            show_table_price = self.browser.find_element_by_id('blocs-liens-tarifs')
            self.browser.execute_script("arguments[0].scrollIntoView(true)", show_table_price)
            show_table_price.click()
        except (TimeoutException, NoSuchElementException, ElementNotVisibleException):
            prices_and_categories = self.collect_price_by_category()
            # categories = self.get_category_names()
            return prices_and_categories
        else:
            prices_and_categories = self.collect_price_by_category()
            # categories = self.get_category_names()
            return prices_and_categories

    def get_category_names(self):
        """return the names of all ticket categories"""
        category_names = list()
        time.sleep(1)  # let the table load before proceed
        try:
            table = self.browser.find_element_by_xpath('//*[@id="price-table"]/tbody')
            self.browser.execute_script("arguments[0].scrollIntoView(true)", table)
            first_row = table.find_element_by_tag_name('tr')
            table_head = first_row.find_elements_by_tag_name('th')
            for header in table_head:
                category = header.text
                if len(category) > 0:
                    category_names.append(category)
        except NoSuchElementException:
            category_names = None
        return category_names

    def collect_price_by_category(self):
        """ associate each category with its price in a dictionary and return it"""
        price_by_category = dict()
        prices = None
        category_names = self.get_category_names()
        if category_names is not None:
            prices = [None for _ in range(0, len(category_names))]
        regular_rate_row = None
        self.browser.implicitly_wait(5)  # let the table load before proceed
        try:
            table = self.browser.find_element_by_xpath('//*[@id="price-table"]/tbody')
            self.browser.execute_script("arguments[0].scrollIntoView(true)", table)
            table_rows = table.find_elements_by_tag_name('tr')
            for row in table_rows:
                header = row.find_element_by_tag_name('th')
                if header.text == "TARIF NORMAL":  # get only the row with the regular rate
                    regular_rate_row = row
                    break
            table_data = None
            if regular_rate_row is not None:  # to avoid some error I got earlier
                table_data = regular_rate_row.find_elements_by_class_name('price')
            i = 0
            if table_data is not None:
                for data in table_data:
                    price = data.text
                    if len(price) > 0:
                        price = float(price.replace("€", "").strip())
                        prices[i] = price
                    i += 1
            for i in range(0, len(category_names)):
                price_by_category[category_names[i]] = prices[i]
        except NoSuchElementException:
            price_by_category = None
        return price_by_category

    def tear_down(self):
        self.browser.close()


if __name__ == '__main__':
    test = FillPriceTable("https://www.ticketmaster.fr/fr/manifestation/marvel-universe-live-billet/idmanif/452219")
    prices_by_cats = test.run()
    if prices_by_cats is not None:
        for cat in prices_by_cats:
            print(cat + ' : ' + str(prices_by_cats[cat]))

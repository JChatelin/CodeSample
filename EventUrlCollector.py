from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time


class EventUrlCollector(object):
    def __init__(self, event_location_url):
        self.event_location_url = event_location_url
        self.browser = webdriver.Chrome()

    def run(self):
        self.browser.get(self.event_location_url)
        try:
            if "Ticketmaster" not in self.browser.page_source:
                raise AssertionError
        except AssertionError:
            self.browser.implicitly_wait(10)
            self.browser.refresh()
        self.click_display_all_link()
        time.sleep(3)
        events_urls = self.get_url_by_event()
        self.tear_down()
        return events_urls

    def click_display_all_link(self):
        try:
            page_navigation = self.browser.find_element_by_class_name('results-pagination')
        except NoSuchElementException:
            page_navigation = None
        if page_navigation is not None:
            display_all_event = page_navigation.find_element_by_id('afficherTout')
            self.browser.execute_script("arguments[0].scrollIntoView(true)", display_all_event)
            time.sleep(1)
            display_all_event.click()

    def get_event_url(self):
        """this function returns a list of boolean. Each boolean match a event,
        if the eticket is active on an event then the boolean is true else false"""
        events_url = list()
        try:
            time.sleep(1)
            result_list = self.browser.find_element_by_id('resultsListZone')
        except NoSuchElementException:
            result_list = None
        if result_list is not None:
            time.sleep(1)
            articles = result_list.find_elements_by_tag_name('article')
            for article in articles:
                event_type = article.get_attribute('class')
                if "bloc-platinum-fr" not in event_type \
                        and "bloc-package-fr" not in event_type \
                        and "bloc-parking-fr" not in event_type:
                    link_tag = article.find_element_by_tag_name('a')
                    url = link_tag.get_attribute('href')
                    events_url.append(url)
        else:
            events_url = None
        return events_url

    def get_url_by_event(self):
        """this function associate each with his eticket presence in a dictionary and return it"""
        events = list()
        try:
            time.sleep(1)
            result_list = self.browser.find_element_by_id('resultsListZone')
        except NoSuchElementException:
            result_list = None
        if result_list is not None:
            events_urls = self.get_event_url()
            time.sleep(1)
            articles = result_list.find_elements_by_tag_name('article')
            counter = 0
            for article in articles:
                event_type = article.get_attribute('class')
                if "bloc-platinum-fr" not in event_type \
                        and "bloc-package-fr" not in event_type \
                        and "bloc-parking-fr" not in event_type:
                    title = article.find_element_by_class_name('bloc-result-title')
                    event_name = title.find_element_by_tag_name('span')
                    if "PARKING" in event_name.text or "PACK" in event_name.text:
                        counter += 1
                        continue
                    else:
                        ev_name_and_url = event_name.text, events_urls[counter]
                        events.append(ev_name_and_url)
                        counter += 1
        return events

    def tear_down(self):
        self.browser.close()


if __name__ == '__main__':
    test = EventUrlCollector('https://www.ticketmaster.fr/fr/salle/zenith-amiens/idsite/10064')
    events = test.run()
    if events is not None:
        for name in events:
            print(name[0] + " : " + str(name[1]))

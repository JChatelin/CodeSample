from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from datetime import datetime
from ConnectDatabase import *
from EventUrlCollector import *
from FillPriceTable import *


class FillEventAndPriceTable(ConnectDatabase):
    def __init__(self):
        super().__init__()

    def run(self, resume=0):
        tracker, no_error = self.fill_global_event_and_price_table(resume)
        if not no_error:
            self.run(tracker)
        else:
            self.run()

    def fill_global_event_and_price_table(self, resume=0):

        sql_select_salle = """SELECT id, url FROM Salle;"""
        sql_select_events = """SELECT url FROM Event_Global;"""
        str_format_insert = """INSERT INTO Event_Global(Salle_id, name, url, insert_date) 
                        VALUES ("{}", "{}", "{}", "{}");"""
        sql_select_last_event_added = """SELECT id FROM Event_Global ORDER BY id DESC LIMIT 1;"""
        self.cursor.execute(sql_select_salle)
        salle_urls = self.cursor.fetchall()
        self.cursor.execute(sql_select_events)
        database_url = self.cursor.fetchall()
        tracker = 0
        already_saved = False
        for i in range(resume, len(salle_urls)):
            salle_id = salle_urls[i][0]
            salle_url = salle_urls[i][1]
            url_collector = EventUrlCollector(salle_url)
            try:
                all_events_urls = url_collector.run()
            except(NoSuchElementException, TimeoutException,
                    StaleElementReferenceException, WebDriverException):
                tracker = i
                break
            if all_events_urls is not None:
                for event in all_events_urls:
                    event_name = event[0]
                    event_url = event[1]
                    if database_url is not None:
                        for url in database_url:
                            url = url[0]
                            if event_url == url:
                                already_saved = True
                                break
                    if not already_saved:
                        if '"' in event_name:
                            event_name = event_name.replace('"', "'")
                        sql_insert = str_format_insert.format(salle_id, event_name,
                                                              event_url, datetime.now().date())
                        self.cursor.execute(sql_insert)
                        self.con.commit()
                        self.cursor.execute(sql_select_last_event_added)
                        last_event_added_id = self.cursor.fetchone()
                        self.fill_price_table(last_event_added_id, event_url)
                    already_saved = False
        if tracker == len(salle_urls):
            no_error = True
        else:
            no_error = False
        return tracker, no_error

    def fill_price_table(self, event_id, event_url):
        str_format1 = """INSERT INTO Prix (Event_id, category, prix) VALUES ("{}", "{}", "{}");"""
        str_format2 = """INSERT INTO Prix (Event_id, category) VALUES ("{}", "{}");"""
        str_format3 = """INSERT INTO Prix (Event_id) VALUES ("{}");"""
        price_collector = FillPriceTable(event_url)
        prices_and_cats = price_collector.run()
        event_id = event_id[0]
        if prices_and_cats is not None:
            for cat in prices_and_cats:
                if prices_and_cats[cat] is None:
                    sql_insert = str_format2.format(event_id, cat)
                    self.cursor.execute(sql_insert)
                else:
                    sql_insert = str_format1.format(event_id, cat, prices_and_cats[cat])
                    self.cursor.execute(sql_insert)
        else:
            sql_insert = str_format3.format(event_id)
            self.cursor.execute(sql_insert)


if __name__ == '__main__':
    rob = FillEventAndPriceTable()
    rob.connect_to_database()
    rob.run()
    rob.close_connection_to_database()

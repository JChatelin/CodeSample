from ConnectDatabase import *


class TablesCreation(ConnectDatabase):
    def __init__(self):
        super().__init__()

    def run(self):
        self.connect_to_database()
        self.tables_creation()
        self.close_connection_to_database()

    def tables_creation(self):
        salle_table_creation = """CREATE TABLE IF NOT EXISTS Salle (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        ville VARCHAR(255),
        url TEXT NOT NULL,
        PRIMARY KEY(id));"""
        event_table_creation = """CREATE TABLE IF NOT EXISTS Event_Global (
        id INT NOT NULL AUTO_INCREMENT,
        Salle_id INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        url TEXT NOT NULL,
        insert_date DATE NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(Salle_id) REFERENCES Salle (id));"""
        price_table_table = """CREATE TABLE IF NOT EXISTS Prix (
        id INT NOT NULL AUTO_INCREMENT,
        Event_id INT NOT NULL,
        category VARCHAR(30) DEFAULT NULL,
        prix FLOAT DEFAULT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(Event_id) REFERENCES Event_Global(id));
        """
        self.cursor.execute(salle_table_creation)
        self.cursor.execute(event_table_creation)
        self.cursor.execute(price_table_table)


if __name__ == '__main__':
    TablesCreation().run()

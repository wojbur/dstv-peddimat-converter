import sqlite3
import os
from dstv_decoder import SteelPart


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file
    
    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class PartDatabase:
    def __init__(self, part, connection):
        self.part = part
        self.connection = connection.connect()

    def create_table(self):
        query = """CREATE TABLE IF NOT EXISTS part (
        id integer PRIMARY KEY,
        partmark text,
        profile text,
        profile_type text,
        quantity integer,
        profile_depth integer,
        web_thickness integer,
        flange_height integer,
        flange_thickness integer,
        length integer
        );"""
        cursor = self.connection.cursor()
        cursor.execute(query)
    
    def insert_data(self):
        query = """INSERT INTO part (
        partmark,
        profile
        )
        VALUES (?,?);"""
        cursor = self.connection.cursor()
        cursor.execute(query, (self.part.partmark, self.part.profile))
        self.connection.commit()
        cursor.close()
        self.connection.close()


def main():
    steel_part = SteelPart("1011B.nc1")
    database_connection = DatabaseConnection()
    part_database = PartDatabase(part=steel_part, connection=database_connection)
    part_database.create_table()
    part_database.insert_data()


if __name__ == "__main__":
    main()
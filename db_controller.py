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
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def create_table(self):
        connection = self.database_connection.connect()
        cursor = connection.cursor()

        query = """CREATE TABLE IF NOT EXISTS part (
        PartId integer PRIMARY KEY,
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

        cursor.execute(query)
        cursor.close()
        connection.close()
    
    def insert_data(self, part):
        connection = self.database_connection.connect()
        cursor = connection.cursor()

        query = """INSERT INTO part (
        partmark,
        profile,
        profile_type,
        quantity,
        profile_depth,
        web_thickness,
        flange_height,
        flange_thickness,
        length
        )
        VALUES (?,?,?,?,?,?,?,?,?);"""

        cursor.execute(query, (
            part.partmark,
            part.profile,
            part.profile_type,
            part.quantity,
            round(part.profile_depth),
            round(part.web_thickness),
            round(part.flange_height),
            round(part.flange_thickness),
            round(part.length)
            ))
        connection.commit()
        cursor.close()
        connection.close()

class HoleDatabase:
    def __init__(self, database_connection):
        self.database_connection = database_connection
    
    def get_part_id(self, hole):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT PartId FROM part WHERE partmark = ?", (hole.partmark,))
        part_id = list(result)[0][0]
        return part_id

    def create_table(self):
        connection = self.database_connection.connect()
        cursor = connection.cursor()

        query = """CREATE TABLE IF NOT EXISTS hole (
        HoleId integer PRIMARY KEY,
        PartId integer,
        surface text,
        slotted text,
        slot_x integer,
        slot_y integer,
        size text,
        x_distance integer,
        y_distance integer
        );"""

        cursor.execute(query)
        cursor.close()
        connection.close()
    
    def insert_data(self, hole):
        part_id = self.get_part_id(hole)


def main():
    steel_part1 = SteelPart("1009B.nc1")
    database_connection = DatabaseConnection()

    part_database = PartDatabase(database_connection)
    hole_database = HoleDatabase(database_connection)

    part_database.create_table()
    hole_database.create_table()

    part_database.insert_data(steel_part1)

    for hole in steel_part1.holes:
        hole_database.get_part_id(hole)

if __name__ == "__main__":
    main()
import sqlite3
import os
from dstv_decoder import SteelPart


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file
    
    def delete_old(self):
        if os.path.exists(self.database_file):
            os.remove(self.database_file)
    
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
    
    def remove_data(self, partmark):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM part WHERE partmark = ?", (partmark,))
        connection.commit()
        cursor.close()
        connection.close()
    
    def get_partmarks_list(self):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT partmark FROM part")
        return [item[0] for item in result]

    def get_part_geometry(self, partmark):
        connection = self.database_connection.connect()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = """SELECT
        profile_type,
        profile_depth,
        web_thickness,
        flange_height,
        flange_thickness,
        length
        FROM part WHERE partmark = ?"""

        cursor.execute(query, (partmark,))
        result = cursor.fetchone()
        return dict(result)


class HoleDatabase:
    def __init__(self, database_connection):
        self.database_connection = database_connection
    
    def get_part_id(self, hole=None, partmark=None):
        if not partmark:
            partmark = hole.partmark
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT PartId FROM part WHERE partmark = ?", (partmark,))
        part_id = cursor.fetchone()[0]
        return part_id

    def create_table(self):
        connection = self.database_connection.connect()
        cursor = connection.cursor()

        query = """CREATE TABLE IF NOT EXISTS hole (
        HoleId integer PRIMARY KEY,
        PartId integer,
        surface text,
        diameter integer,
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
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        part_id = self.get_part_id(hole=hole)

        query = """INSERT INTO hole (
        PartId,
        surface,
        diameter,
        slotted,
        slot_x,
        slot_y,
        size,
        x_distance,
        y_distance
        )
        VALUES (?,?,?,?,?,?,?,?,?);"""

        cursor.execute(query, (
            part_id,
            hole.surface,
            round(hole.diameter),
            hole.slotted,
            round(hole.slot_x),
            round(hole.slot_y),
            hole.size,
            round(hole.x_distance),
            round(hole.y_distance)
            ))
        connection.commit()
        cursor.close()
        connection.close()
    
    def remove_data(self, partmark):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        part_id = self.get_part_id(partmark=partmark)
        cursor.execute("DELETE FROM hole WHERE PartId = ?", (part_id,))
        connection.commit()
        cursor.close()
        connection.close()
    
    def get_hole_info_list(self, partmark):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        part_id = self.get_part_id(partmark=partmark)

        query = """SELECT
        surface,
        size,
        x_distance,
        y_distance
        FROM hole WHERE PartId = ?"""     
        cursor.execute(query, (part_id, ))
        return cursor.fetchall()
    
    def get_hole_geometry_list(self, partmark, surface):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        part_id = self.get_part_id(partmark=partmark)

        query = """SELECT
        diameter,
        slot_x,
        slot_y,
        x_distance,
        y_distance
        FROM hole WHERE PartId = ? AND surface = ?"""     
        cursor.execute(query, (part_id, surface))
        return cursor.fetchall()






def main():
    parts = ["1001B.nc1", "1002B.nc1", "1003B.nc1", "1004B.nc1", "1005B.nc1", "1006B.nc1", "1007B.nc1", "1008B.nc1", "1009B.nc1", "1010B.nc1", "1011B.nc1"]
    database_connection = DatabaseConnection()
    database_connection.delete_old()
    part_database = PartDatabase(database_connection)
    part_database.create_table()
    hole_database = HoleDatabase(database_connection)
    hole_database.create_table()

    for part in parts:
        steel_part = SteelPart(part)
        part_database.insert_data(steel_part)

        for hole in steel_part.holes:
            hole_database.insert_data(hole)

def test1():
    database_connection = DatabaseConnection()
    part_database = PartDatabase(database_connection)
    print(part_database.get_partmarks_list())

def test2():
    database_connection = DatabaseConnection()
    hole_database = HoleDatabase(database_connection)
    print(hole_database.get_hole_info_list("1002B"))

def test3():
    database_connection = DatabaseConnection()
    part_database = PartDatabase(database_connection)
    print(part_database.get_part_geometry("1002B"))


if __name__ == "__main__":
    test3()
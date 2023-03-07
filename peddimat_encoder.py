import sqlite3
from db_controller import DatabaseConnection


class PeddimatEncoder:
    def __init__(self, database_connection):
        self.database_connection = database_connection
    
    def get_part_id(self, partmark):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT PartId FROM part WHERE partmark = ?", (partmark,))
        part_id = cursor.fetchone()[0]
        return part_id
    
    def load_part_data(self, partmark):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        query = """SELECT
        profile,
        profile_type,
        quantity,
        profile_depth,
        web_thickness,
        flange_height,
        flange_thickness,
        length
        FROM part WHERE partmark = ?
        """
        cursor.execute(query, (partmark,))
        print(cursor.fetchone())
    
    def load_holes_data(self, partmark):
        connection = self.database_connection.connect()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        part_id = self.get_part_id(partmark)

        query = """SELECT
        surface,
        diameter,
        slotted,
        slot_x,
        slot_y,
        size,
        x_distance,
        y_distance
        FROM hole WHERE PartId = ?
        """
        cursor.execute(query, (part_id,))
        result = cursor.fetchall()
        for hole in result:
            print(dict(hole))
    
    def save_peddimat_file(self, partmark):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT profile FROM part WHERE partmark = ?", (partmark,))
        print(cursor.fetchone())


def main():
    database_connection = DatabaseConnection("database.db")
    peddimat_encoder = PeddimatEncoder(database_connection)
    peddimat_encoder.load_holes_data("1009B")


if __name__ == "__main__":
    main()
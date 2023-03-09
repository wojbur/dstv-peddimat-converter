import sqlite3
from db_controller import DatabaseConnection


class PeddimatEncoder:
    def __init__(self, database_connection):
        self.database_connection = database_connection
    
    def build_peddimat_string(self, partmark):
        part_data = self.load_part_data(partmark)
        rows = []
        rows.append(part_data["partmark"])
        rows.append(part_data["profile"])
        rows.append(part_data["profile_type"])

        

        rows.append(self.build_profile_info_row(partmark, part_data))
        print("\n".join(rows))
    
    def build_profile_info_row(self, partmark, part_data):
        row = []
        row.append(str(part_data["quantity"]))
        row.append(str(part_data["profile_depth"]))
        row.append(str(part_data["web_thickness"]))
        row.append(str(part_data["flange_height"]))
        row.append(str(part_data["flange_thickness"]))
        row.append(str(part_data["length"]))
        row_string = "  ".join(row)
        return " " + row_string
    
    def get_part_id(self, partmark):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT PartId FROM part WHERE partmark = ?", (partmark,))
        part_id = cursor.fetchone()[0]
        return part_id
    
    def load_part_data(self, partmark):
        connection = self.database_connection.connect()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """SELECT
        partmark,
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
        part_data = dict(cursor.fetchone())
        return part_data
    
    def load_tools(self, partmark, surface):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        part_id = self.get_part_id(partmark)
        cursor.execute("SELECT size FROM hole WHERE PartId = ? AND surface = ?", (part_id, surface))
        tools = []
        [tools.append(row[0]) for row in cursor.fetchall() if row[0] not in tools]
        return tools
    
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
    # peddimat_encoder.load_holes_data("1009B")
    # print(peddimat_encoder.load_tools("1002B", "top"))
    # print(peddimat_encoder.load_part_data("1003B"))
    peddimat_encoder.build_peddimat_string("1002B")


if __name__ == "__main__":
    main()
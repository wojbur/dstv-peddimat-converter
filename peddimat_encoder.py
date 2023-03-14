import sqlite3
from db_controller import DatabaseConnection
import os


class PeddimatEncoder:
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def save_peddimat_file(self, partmark, dir_path=""):
        peddimat_string = self.build_peddimat_string(partmark)
        path = os.path.join(dir_path, partmark)
        with open(path, "w") as file:
            file.write(peddimat_string)
    
    def build_peddimat_string(self, partmark):
        part_data = self.load_part_data(partmark)
        rows = []

        rows.append(part_data["partmark"])
        rows.append(part_data["profile"])
        rows.append(part_data["profile_type"])
        
        profile_info_row = self.build_profile_info_row(part_data)
        tool_info_row = self.build_tool_row(partmark)
        profile_and_tool_row = profile_info_row + tool_info_row

        rows.append(profile_and_tool_row)

        hole_quantity_row = self.build_hole_quantity_row(partmark)
        rows.append(hole_quantity_row)

        holes_data = self.load_holes_data(partmark)
        for hole in holes_data:
            hole_row = self.build_hole_row(hole, partmark)
            rows.append(hole_row)
        
        rows.append("")

        peddimat_string = "\n".join(rows)
        return peddimat_string
    
    def build_profile_info_row(self, part_data):
        row = []
        row.append(str(part_data["quantity"]))
        row.append(str(part_data["profile_depth"]))
        row.append(str(part_data["web_thickness"]))
        row.append(str(part_data["flange_height"]))
        row.append(str(part_data["flange_thickness"]))
        profile_info_string = "  ".join(row)
        row = f' {profile_info_string}  0  0  0  {part_data["length"]}'
        return row
    
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
    
    def get_tools(self, partmark):
        tools = zip(self.load_tools(partmark, "front"), self.load_tools(partmark, "bottom"), self.load_tools(partmark, "top"))
        return list(tools)

    def build_tool_row(self, partmark):
        tools = self.get_tools(partmark)
        tool_string = ""
        for tool in tools:
            for surface in tool:
                tool_string += f"  {surface}"
        return tool_string
    
    def load_tools(self, partmark, surface):
        connection = self.database_connection.connect()
        cursor = connection.cursor()
        part_id = self.get_part_id(partmark)
        cursor.execute("SELECT size FROM hole WHERE PartId = ? AND surface = ?", (part_id, surface))
        tools = []
        [tools.append(row[0]) for row in cursor.fetchall() if row[0] not in tools]
        while len(tools) < 9:
            tools.append("0")
        return tools
    
    def build_hole_quantity_row(self, partmark):
        holes_data = self.load_holes_data(partmark)
        quantity = len(holes_data)+1
        row = f" {quantity}"
        return row
    
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
        hole_data_list = [dict(hole_data) for hole_data in result]
        return hole_data_list
    
    def get_tool_number(self, partmark, size, surface):
        tool_row = self.get_tools(partmark)
        match surface:
            case "front":
                surface_index = 1
            case "bottom":
                surface_index = 2
            case "top":
                surface_index = 3
        for i in range(9):
            if tool_row[i][surface_index-1] == size:
                return f"{surface_index}0{i+1}0"
    
    def build_hole_row(self, hole_data, partmark):
        tool_number = self.get_tool_number(partmark, hole_data["size"], hole_data["surface"])
        row = f' {hole_data["x_distance"]}  {hole_data["y_distance"]}.{tool_number}'
        return row


def main():
    database_connection = DatabaseConnection("database.db")
    peddimat_encoder = PeddimatEncoder(database_connection)


    parts = ["1001B", "1002B", "1003B", "1004B", "1005B", "1006B", "1007B", "1008B", "1009B", "1010B", "1011B"]
    for part in parts:
        peddimat_encoder.save_peddimat_file(part, "output_test")


if __name__ == "__main__":
    main()
import re

class SteelPart:
    def __init__(self, path):
        self.dstv_content = self.get_dstv_content(path)

        self.partmark = self.get_partmatk()
        self.profile = self.get_profile()
        self.valid_profile_type = True
        self.profile_type = self.get_profile_type()
        self.quantity = self.get_quantity()
        self.profile_depth = self.get_profile_depth()
        self.web_thickness = self.get_web_thickness()
        self.flange_height = self.get_flange_height()
        self.flange_thickness = self.get_flange_thickness()
        self.length = self.get_length()
        self.holes = self.get_holes()
    
    def __repr__(self):
        return str({
            "partmark": self.partmark,
            "profile": self.profile,
            "profile type": self.profile_type,
            "quantity": self.quantity,
            "profile depth": round(self.profile_depth),
            "web thickness": round(self.web_thickness),
            "flange height": round(self.flange_height),
            "flange thickness": round(self.flange_thickness),
            "length": round(self.length),
            "holes": len(self.holes)
        })
    
    def get_dstv_content(self, path):
        with open(path, "r") as f:
            dstv_content = f.read()
        return dstv_content

    def get_partmatk(self) -> str:
        line = self.dstv_content.splitlines()[3]
        partmark = line.strip()
        return partmark

    def get_profile(self) -> str:
        line = self.dstv_content.splitlines()[8]
        profile = line.strip()
        return profile
    
    def get_profile_type(self) -> str:
        line = self.dstv_content.splitlines()[9]
        profile_type_dstv = line.strip()
        match profile_type_dstv:
            case "I":
                profile_type_peddimat = "B"
            case "U":
                profile_type_peddimat = "C"
            case "M":
                profile_type_peddimat = "T"       
            # B(Plate) and L(Angle) profile functionality to be added later
            # case "B":
            #     profile_type_peddimat = "P"
            # case "L":
            #     profile_type_peddimat = "L"
            case _:
                profile_type_peddimat = None
                self.valid_profile_type = False
        return profile_type_peddimat
    
    def get_quantity(self) -> int:
        line = self.dstv_content.splitlines()[7]
        quantity = int(line.strip())
        return quantity
    
    def get_profile_depth(self) -> int:
        line = self.dstv_content.splitlines()[11]
        depth = float(line)*10
        return depth
    
    def get_web_thickness(self) -> int:
        line = self.dstv_content.splitlines()[14]
        thickness = float(line)*10
        return thickness

    def get_flange_height(self) -> int:
        line = self.dstv_content.splitlines()[12]
        height = float(line)*10
        return height

    def get_flange_thickness(self) -> int:
        line = self.dstv_content.splitlines()[13]
        thickness = float(line)*10
        return thickness

    def get_length(self) -> int:
        line = self.dstv_content.splitlines()[10]
        # Depending on DSTV export settings the line can contain single value or two values separated by comma
        try:
            length = float(line)*10
        except ValueError:
            length=float(line.split(",")[0])*10
        return length
    
    def get_holes(self) -> list:
        holes_lines = self.get_holes_lines()
        holes = [Hole(self, line) for line in holes_lines]
        return holes

    def get_holes_lines(self) -> list:
        BO_block_content = re.findall(r"(?<=BO\n)(.*)(?=EN)", self.dstv_content, re.DOTALL)[0]
        holes_lines = re.findall(r"  [ovu].+", BO_block_content)
        return holes_lines

class Hole:
    def __init__(self, part, hole_line_text: str):
        self.part = part
        self.partmark = self.part.partmark

        self.hole_line = self.get_hole_line_list(hole_line_text)

        self.surface = self.get_surface()
        self.diameter = self.get_diameter()

        slot_info = self.get_slotted()
        self.slotted = slot_info["slotted"]
        self.slot_x = slot_info["slot_x"]
        self.slot_y = slot_info["slot_y"]
        self.size = slot_info["size"]

        self.x_distance = self.get_x_distance()
        self.y_distance = self.get_y_distance()
    
    def __repr__(self):
        return str({
            "surface": self.surface,
            "diameter": round(self.diameter),
            "slotted": self.slotted,
            "slot x": round(self.slot_x),
            "slot y": round(self.slot_y),
            "size": self.size,
            "x_distance": round(self.x_distance),
            "y_distance": round(self.y_distance)
        })
    
    def get_hole_line_list(self, line_text):
        hole_line = line_text.split()
        return hole_line
    
    def get_surface(self) -> str:
        match self.hole_line[0]:
            case "v":
                return "front"
            case "o":
                return "top"
            case "u":
                return "bottom"
            
    def get_diameter(self):
        diameter_string = self.hole_line[3]
        diameter = float(diameter_string)*10
        return diameter
    
    def get_slotted(self):
        if len(self.hole_line) == 4:
            slotted = False
            slot_x = 0
            slot_y = 0
            size = str(round(self.diameter))
        else:
            slotted = True
            slot_x = float(self.hole_line[5])*10
            slot_y = float(self.hole_line[6])*10
            size = f"{round(self.diameter+slot_x)}X{round(self.diameter+slot_y)}"
        return {
            "slotted": slotted,
            "slot_x": slot_x,
            "slot_y": slot_y,
            "size": size
        }
    
    def get_x_distance(self) -> int:
        distance_string = self.hole_line[1][:-1]
        x_distance = float(distance_string)*1000
        if self.slotted:
            x_distance = x_distance + (self.slot_x*50)
        x_distance = x_distance
        return x_distance
    
    def get_y_distance(self) -> int:
        distance_string = self.hole_line[2]

        if "g" in distance_string:
            self.type = "r_thrd"
            distance_string = distance_string[:-1]
        elif "l" in distance_string:
            self.type = "l_thrd"
            distance_string = distance_string[:-1]
        elif "m" in distance_string:
            self.type = "mark"
            distance_string = distance_string[:-1]
            self.diameter = 0
            self.size = "0"
        else:
            self.type = "std"
            
        if self.surface == "front":
            y_distance = self.part.profile_depth*100 - float(distance_string)*1000
        else:
            y_distance = float(distance_string)*1000
        return y_distance


def main():
    steel_part = SteelPart("1004B.nc1")
    for hole in steel_part.holes:
        print(hole)


if __name__ == "__main__":
    main()
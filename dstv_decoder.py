import re

class SteelPart:
    def __init__(self, path):
        self.dstv_content = self.get_dstv_content(path)

        self.get_partmatk()
        self.get_profile()
        self.get_profile_type()
        self.get_quantity()
        self.get_profile_depth()
        self.get_web_thickness()
        self.get_flange_height()
        self.get_flange_thickness()
        self.get_length()
        self.get_holes()
    
    def get_dstv_content(self, path):
        with open(path, "r") as f:
            dstv_content = f.read()
        return dstv_content

    def get_partmatk(self) -> str:
        line = self.dstv_content.splitlines()[3]
        self.partmark = line.strip()

    def get_profile(self) -> str:
        line = self.dstv_content.splitlines()[8]
        self.profile = line.strip()
    
    def get_profile_type(self) -> str:
        line = self.dstv_content.splitlines()[9]
        self.valid_profile_type = True

        profile_type_dstv = line.strip()
        match profile_type_dstv:
            case "I":
                self.profile_type = "B"
            case "U":
                self.profile_type = "C"
            case "M":
                self.profile_type = "T"
            case "T":
                self.profile_type = "t"
            # B(Plate) and L(Angle) profile functionality to be added later
            # case "B":
            # case "L":
            case _:
                self.profile_type = None
                self.valid_profile_type = False
    
    def get_quantity(self) -> int:
        line = self.dstv_content.splitlines()[7]
        self.quantity = int(line.strip())
    
    def get_profile_depth(self) -> int:
        if self.profile_type == "t":
            line = self.dstv_content.splitlines()[12]
        else:
            line = self.dstv_content.splitlines()[11]
        self.profile_depth = float(line)*10
    
    def get_web_thickness(self) -> int:
        line = self.dstv_content.splitlines()[14]
        self.web_thickness = float(line)*10

    def get_flange_height(self) -> int:
        if self.profile_type == "t":
            line = self.dstv_content.splitlines()[11]
        else:
            line = self.dstv_content.splitlines()[12]
        self.flange_height = float(line)*10

    def get_flange_thickness(self) -> int:
        line = self.dstv_content.splitlines()[13]
        self.flange_thickness = float(line)*10

    def get_length(self) -> int:
        line = self.dstv_content.splitlines()[10]
        # Depending on DSTV export settings the line can contain single value or two values separated by comma
        # The first value is profile net length
        try:
            self.length = float(line)*10
        except ValueError:
            self.length = float(line.split(",")[0])*10
    
    def get_holes(self) -> list:
        holes_lines = self.get_holes_lines()
        self.holes = [Hole(self, line) for line in holes_lines]

    def get_holes_lines(self) -> list:
        try:
            BO_block_content = re.findall(r"(?<=BO\n)(.*)(?=EN)", self.dstv_content, re.DOTALL)[0]
        except IndexError:
            return []
        holes_lines = re.findall(r"  [ovu].+", BO_block_content)
        return holes_lines

class Hole:
    def __init__(self, part, hole_line_text: str):
        self.part = part
        self.partmark = self.part.partmark

        self.get_hole_line_list(hole_line_text)
        self.get_surface()
        self.get_diameter()
        self.get_slotted_info()
        self.get_hole_type()
        self.get_x_distance()
        self.get_y_distance()
    
    def get_hole_line_list(self, line_text):
        self.hole_line = line_text.split()
    
    def get_surface(self) -> str:
        if self.part.profile_type == "t":
            match self.hole_line[0]:
                case "v":
                    self.surface = "top"
                case "o":
                    self.surface = "front"
        else:
            match self.hole_line[0]:
                case "v":
                    self.surface = "front"
                case "o":
                    self.surface = "top"
                case "u":
                    self.surface = "bottom"
            
    def get_diameter(self):
        diameter_string = self.hole_line[3]
        self.diameter = float(diameter_string)*10
    
    def get_slotted_info(self):
        if len(self.hole_line) == 4:
            self.slotted = False
            self.slot_x = 0
            self.slot_y = 0
            self.size = str(round(self.diameter))
        else:
            self.slotted = True
            self.slot_x = float(self.hole_line[5])*10
            self.slot_y = float(self.hole_line[6])*10
            self.size = f"{round(self.diameter+self.slot_x)}X{round(self.diameter+self.slot_y)}"

    def get_hole_type(self) -> int:
        type_string = self.hole_line[2]
        if "g" in type_string:
            self.hole_type = "r_thrd"
        elif "l" in type_string:
            self.hole_type = "l_thrd"
        elif "m" in type_string:
            self.hole_type = "mark"
            self.diameter = 0
            self.size = "0"
        else:
            self.hole_type = "std"
    
    def get_x_distance(self) -> int:
        distance_string = self.hole_line[1][:-1]
        self.x_distance = float(distance_string)*1000 + self.slot_x*50
    
    def get_y_distance(self) -> int:
        distance_string = self.hole_line[2]
        if self.hole_type != "std":
            distance_string = distance_string[:-1]

        if self.surface == "front" and self.part.profile_type == "t":
            self.y_distance = float(distance_string)*1000 - self.slot_y*50
        elif self.surface == "front":
            self.y_distance = self.part.profile_depth*100 - float(distance_string)*1000 + self.slot_y*50
        else:
            self.y_distance = float(distance_string)*1000 - self.slot_y*50

def main():
    pass

if __name__ == "__main__":
    main()
import re

class SteelPart:
    def __init__(self, dstv_content: str):
        self.part_mark = self.get_partmatk(dstv_content)
        self.profile = self.get_profile(dstv_content)
        self.profile_type = self.get_profile_type(dstv_content)
        self.quantity = self.get_quantity(dstv_content)
        self.holes = self.get_holes(dstv_content)
    
    def __repr__(self):
        return str({
            "part mark": self.part_mark,
            "profile": self.profile,
            "profile type": self.profile_type,
            "quantity": self.quantity,
            "holes": self.holes
        })


    def get_partmatk(self, dstv) -> str:
        line = dstv.splitlines()[3]
        partmark = line.strip()
        return partmark

    def get_profile(self, dstv: str) -> str:
        line = dstv.splitlines()[8]
        profile = line.strip()
        return profile
    
    def get_profile_type(self, dstv: str) -> str:
        line = dstv.splitlines()[9]
        profile_type_dstv = line.strip()
        match profile_type_dstv:
            case "I":
                profile_type_peddimat = "B"
            case "U":
                profile_type_peddimat = "C"
            case "M":
                profile_type_peddimat = "T"
            case "B":
                profile_type_peddimat = "P"
            case "L":
                profile_type_peddimat = "L"
            case _:
                profile_type_peddimat = profile_type_dstv
        return profile_type_peddimat
    
    def get_quantity(self, dstv: str) -> int:
        line = dstv.splitlines()[7]
        quantity = int(line.strip())
        return quantity
    
    def get_holes(self, dstv: str) -> list:
        holes_lines = self.get_holes_lines(dstv)
        holes = [Hole(line) for line in holes_lines]
        return holes

    def get_holes_lines(self, dstv: str) -> list:
        BO_block_content = re.findall(r"(?<=BO\n)(.*)(?=EN)", dstv, re.DOTALL)[0]
        holes_lines = re.findall(r"  [ovu].+", BO_block_content)
        return holes_lines

class Hole:
    def __init__(self, hole_line_text: str):
        self._hole_line = self.get_hole_line_list(hole_line_text)
        self.surface = self.get_surface(self._hole_line)
        self.diameter = self.get_diameter(self._hole_line)
        self.slotted = False
        self.slot_x = 0
        self.slot_y = 0
    
    def __repr__(self):
        return str({
            "surface": self.surface,
            "diameter": self.diameter
        })
    
    def get_hole_line_list(self, line_text: str):
        hole_line = line_text.split()
        return hole_line
    
    def get_surface(self, hole_line: list) -> str:
        match hole_line[0]:
            case "v":
                return "front"
            case "o":
                return "top"
            case "u":
                return "bottom"
            
    def get_diameter(self, hole_line: list):
        diameter_string = hole_line[3]
        diameter = round(float(diameter_string)*10)
        return diameter
            

    def get_holes_lines(self, dstv: str) -> list:
        BO_block_content = re.findall(r"(?<=BO\n)(.*)(?=EN)", dstv, re.DOTALL)[0]
        holes_text = re.findall(r"  [ovu].+", BO_block_content)
        holes_lines = [line.split() for line in holes_text]
        return holes_lines
    


with open("1002B.nc1", "r") as f:
    dstv_content = f.read()

steel_part = SteelPart(dstv_content)
print(steel_part)
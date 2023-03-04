import re

class SteelPart:
    def __init__(self, dstv_content):
        self.part_mark = self.get_partmatk(dstv_content)
        self.profile = self.get_profile(dstv_content)
        self.holes = self.get_holes(dstv_content)


    def get_partmatk(self, dstv) -> str:
        line = dstv.splitlines()[3]
        partmark = line.strip()
        return partmark

    def get_profile(self, dstv_content: str) -> str:
        line = dstv_content.splitlines()[7]
        profile = line.strip()
        return profile

    
    def get_holes(self, dstv_content: str) -> list:
        holes_lines = self.get_holes_lines(dstv_content)
        holes = [{
        "surface": self.get_surface(hole),
        "diameter": self.get_diameter(hole),
        "x_distance": self.get_x_distance(hole),
        "y_distance": float(hole[2]),
        "slotted": True if len(hole) > 4 else False
       } for hole in holes_lines]
        return holes

    def get_holes_lines(self, dstv_content: str) -> list:
        BO_block_content = re.findall(r"(?<=BO\n)(.*)(?=EN)", dstv_content, re.DOTALL)[0]
        holes_text = re.findall(r"  [ovu].+", BO_block_content)
        holes_lines = [line.split() for line in holes_text]
        return holes_lines
        
    def get_surface(self, hole: list) -> str:
        if hole[0] == "v":
            return "front"
        if hole[0] == "o":
            return "top"
        if hole[0] == "u":
            return "bottom"

    def get_diameter(self, hole: list):
        diameter_string = hole[3]
        diameter = round(float(diameter_string)*10)
        return diameter

    def get_x_distance(self, hole: list):
        x_distance_string = hole[1][:-1]
        return x_distance_string
    


with open("1002B.nc1", "r") as f:
    dstv_content = f.read()

part = SteelPart(dstv_content)
print(part.holes[0])
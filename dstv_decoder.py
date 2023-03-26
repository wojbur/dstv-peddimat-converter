import re
import os

class SteelPart:
    """A class to store information about steel part geometry"""
    def __init__(self, path):
        """
        Read all necessary infromation for the SteelPart object from DSTV file.
        Parameters:
        path : str
            path to .NC1 file
        """
        self.dstv_content = self.get_dstv_content(path)

        self.check_correct_dstv_format(path)

        if self.correct_dstv_format:
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
    
    def get_dstv_content(self, path) -> str:
        """Return text content of given DSTV file"""
        with open(path, "r") as f:
            dstv_content = f.read()
        return dstv_content
    
    def check_correct_dstv_format(self, path):
        """Check if the DSTV file has correct items order"""
        # Check if row 4 contain partmark
        partmark_filename = os.path.basename(path).split(".")[0]
        partmark_dstv = self.dstv_content.splitlines()[3].strip()
        if partmark_filename != partmark_dstv:
            self.correct_dstv_format = False
            return 
        # Check if row 8 contain quantity of parts
        try:
            int(self.dstv_content.splitlines()[7].strip())
        except ValueError:
            self.correct_dstv_format = False
            return
        # All checks are correct
        self.correct_dstv_format = True

    def get_partmatk(self) -> None:
        """Get part mark from DSTV file text content"""
        line = self.dstv_content.splitlines()[3]
        self.partmark = line.strip()

    def get_profile(self) -> None:
        """Get parts profile from DSTV file text content"""
        line = self.dstv_content.splitlines()[8]
        self.profile = line.strip()
    
    def get_profile_type(self) -> None:
        """Get part profile type symbol from DSTV file text content"""
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
    
    def get_quantity(self) -> None:
        """Get quantity of parts from DSTV file text content"""
        line = self.dstv_content.splitlines()[7]
        self.quantity = int(line.strip())
    
    def get_profile_depth(self) -> None:
        """Get profile depth in mm*10 from DSTV file text content"""
        if self.profile_type == "t":
            line = self.dstv_content.splitlines()[12]
        else:
            line = self.dstv_content.splitlines()[11]
        self.profile_depth = float(line)*10
    
    def get_web_thickness(self) -> None:
        """Get profile web thickness in mm*10 from DSTV file text content"""
        line = self.dstv_content.splitlines()[14]
        self.web_thickness = float(line)*10

    def get_flange_height(self) -> None:
        """Get profile flange height in mm*10 from DSTV file text content"""
        if self.profile_type == "t":
            line = self.dstv_content.splitlines()[11]
        else:
            line = self.dstv_content.splitlines()[12]
        self.flange_height = float(line)*10

    def get_flange_thickness(self) -> None:
        """Get profile flange thickness in mm*10 from DSTV file text content"""
        line = self.dstv_content.splitlines()[13]
        self.flange_thickness = float(line)*10

    def get_length(self) -> None:
        """Get part length in mm*10 from DSTV file text content"""
        line = self.dstv_content.splitlines()[10]
        # Depending on DSTV export settings the line can contain single value or two values separated by comma
        # The first value is profile net length
        try:
            self.length = float(line)*10
        except ValueError:
            self.length = float(line.split(",")[0])*10
    
    def get_holes(self) -> None:
        """Get list of part holes info"""
        holes_lines = self.get_holes_lines()
        self.holes = [Hole(self, line) for line in holes_lines]

    def get_holes_lines(self) -> list:
        """Return list of lines associated with hole info from DSTV file text content"""
        try:
            BO_block_content = re.findall(r"(?<=BO\n)(.*)(?=EN)", self.dstv_content, re.DOTALL)[0]
        except IndexError:
            return []
        holes_lines = re.findall(r"  [ovu].+", BO_block_content)
        return holes_lines

class Hole:
    """A class to store information about geometry and location of hole in SteelPart object"""
    def __init__(self, part, hole_line_text: str):
        """
        Read all necessary infromation for the SteelPart object from DSTV file.
        Parameters:
        part : SteelPart
            SteelPart object associated with the hole
        hole_line_test : str
            row from DSTV file containing info about the hole
        """
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
        """Get list of elements containg info about hole geometry"""
        self.hole_line = line_text.split()
    
    def get_surface(self) -> str:
        """Get surface of part on which the hole is located"""
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
        """Get hole diameter in mm*10 from list of hole info row"""
        diameter_string = self.hole_line[3]
        self.diameter = float(diameter_string)*10

    def get_slotted_info(self):
        """Get information about slotted holes from list of hole info row"""
        if len(self.hole_line) == 4:
            self.slotted = False
            self.slot_x = 0
            self.slot_y = 0
            self.size = str(round(self.diameter))
            self.size_mm = str(round(self.diameter/10, 1))
            self.size_inch = str(round(self.diameter/254, 3))
        else:
            self.slotted = True
            self.slot_x = float(self.hole_line[5])*10
            self.slot_y = float(self.hole_line[6])*10
            self.size = f"{round(self.diameter+self.slot_x)}X{round(self.diameter+self.slot_y)}"
            self.size_mm = f"{round((self.diameter+self.slot_x)/10, 1)}X{round((self.diameter+self.slot_y)/10, 1)}"
            self.size_inch = f"{round((self.diameter+self.slot_x)/254, 3)}X{round((self.diameter+self.slot_y)/254, 3)}"

    def get_hole_type(self) -> int:
        """Get type of hole from list of hole info row"""
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
        """Get x distance from left end of part to hole center in mm*1000 from list of hole info row"""
        distance_string = self.hole_line[1][:-1]
        self.x_distance = float(distance_string)*1000 + 100*self.slot_x/2
    
    def get_y_distance(self) -> int:
        """Get y distance to hole center in mm*1000 from list of hole info row"""
        distance_string = self.hole_line[2]
        if self.hole_type != "std":
            distance_string = distance_string[:-1]

        if self.surface == "front" and self.part.profile_type == "t":
            self.y_distance = float(distance_string)*1000 - 100*self.slot_y/2
        elif self.surface == "front":
            self.y_distance = self.part.profile_depth*100 - float(distance_string)*1000 + 100*self.slot_y/2
        else:
            self.y_distance = float(distance_string)*1000 - 100*self.slot_y*50/2

def main():
    pass

if __name__ == "__main__":
    main()
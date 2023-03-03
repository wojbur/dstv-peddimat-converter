import re

with open("1002B.nc1", "r") as f:
    dstv_content = f.read()


BO_block_content = re.findall(r"(?<=BO\n)(.*)(?=EN)", dstv_content, re.DOTALL)[0]

front_holes_raw = re.findall(r"  v.+", BO_block_content)
top_holes_raw = re.findall(r"  o.+", BO_block_content)
bottom_holes_raw = re.findall(r"  u.+", BO_block_content)

front_holes_lines = [hole.split() for hole in front_holes_raw]
front_holes = [{
    "surface": "front",
    "diameter": float(hole[3])*10,
    "x_dim": float(hole[1][:-1]),
    "y_dim": float(hole[2]),
    "slotted": True if len(hole) > 4 else False
} for hole in front_holes_lines]

print(front_holes[0])
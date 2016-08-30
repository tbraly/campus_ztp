import re

line = "  Compressed Pri Code size = 19632275, Version:08.0.40aT201 (SWS08040a.bin)"

version = re.compile('(.)+Pri(.)+Version(.)+')
if version.match(line):
	ver_str = version.match(line).group().split(':')[-1].split()[0]
	print(ver_str)
else:
	print("No Match")


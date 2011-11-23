import re

bar = open("WarList_NEW.txt", 'r')

PAT = re.compile(r"\d{4} +(?P<name>.*) +(?P<type>Intra|Extra|Non|Inter)-State War +#(?P<warnum>\d+)")

for line in bar:
    m = PAT.match(line)
    if m:
        print m.group('warnum'), m.group('name').strip(), m.group('type')
        
    



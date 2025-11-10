import re

with open("sample.txt") as f:
    obtwFlag = None
    for line in f:

        # OBTW TLDR comments check
        if obtwFlag != None:
            if re.search("TLDR", line):
                obtwFlag = None
            continue

        obtwFlag = re.search("OBTW", line)
        if obtwFlag != None:
            continue

        # BTW comments ignore
        toParse = line.split("BTW")[0]      #get the left half of the line split by "BTW"
        print(toParse)




# output tokens
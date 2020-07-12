


total = {}

with open("communicate.txt", "r") as f:
    for line in f:
        line = line.replace("\n", "")
        if line.startswith("0"):
            print(line)
            
        average = ' '.join(line.split(" ")[3:])
        value = float(line.split(" ")[2])

        if not average in list(total.keys()):
            total[average] = {"sum": 0, "items": 0}

        total[average]["sum"] += value
        total[average]["items"] += 1
        # if line.startswith("2"):
            # print(line.replace("\n", ""))
    print("Averages")

    for key in list(total.keys()):
        avg = total[key]
        print(key, avg["sum"]/avg["items"])
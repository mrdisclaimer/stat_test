import simplejson # sudo pip2 install simplejson

fname = "./log.txt"
output_fname = "out.txt"

responds = {}
stats = {}
p = 0.95 # 95% confidence probability
alpha = (1 - p) / 2
Za2 = 1.96

# We do not load all file in a memory, use iterator instead
with open(fname, "r") as file:

    for line in file:
        if (line != '\n'):
    
            respond = line[line.find(",") + 1:-3]

            if (respond not in responds.keys()):
                responds[respond] = {"freq_mobile" : 0,
                                     "count" : 0}

            responds[respond]["freq_mobile"] += int(line[-2:]) # binary value

            responds[respond]["count"] += 1

# Calculate frequency
for key in responds.keys():
    responds[key]["freq_mobile"] /= responds[key]["count"]

# Calculate mean and std
with open(fname, "r") as file:

    for line in file:
        if (line != '\n'): # Control missed lines
        
            respond = line[line.find(",") + 1:-3]
        
            if (respond not in stats.keys()):
                stats[respond] = {"error_square" : 0,
                                  "std" : 0}

            value = int(line[-2:])

            # Accumulate squared error for each respond's binary value
            stats[respond]["error_square"] += ((value - responds[respond]["freq_mobile"]) ** 2)

for respond in stats.keys():
    stats[respond]["std"] = (stats[respond]["error_square"] /
                             responds[respond]["count"]) ** (1/2)
    mean = responds[respond]["freq_mobile"]
    std = stats[respond]["std"]
    n = responds[respond]["count"]
    responds[respond]["confidence interval"] = [mean - Za2 * (std ** 2) / (n ** (1 / 2)),
                                                mean + Za2 * (std ** 2) / (n ** (1 / 2))]
    
print(simplejson.dumps(responds, indent=4 * ' '))

# Hypothesis testing

# Assume, that propotion of mobile requests in query /test = Pt, and in /index = Pi

# Because the propotion of telephone calls is numerically equal
# to the average for the population,
# we can test the hypothesis of the equality of the means.

# H0: Pt - Pi = 0
# H1: Pt - Pi != 0

def z_stat(x1mean, x2mean, var1, var2, n1, n2):
    return (x1mean - x2mean) / ((var1 / n1 - var2 / n2) ** (1 / 2))

def testH(z, confidence_level):
    if ((z > confidence_level) or (z < -confidence_level)):
        return "Accepted H1, averages are not equal"
    else:
        return "Accepted H0, averages are equal"

z = z_stat(responds["/index"]["freq_mobile"], responds["/test"]["freq_mobile"],
           stats["/index"]["std"] ** 2, stats["/test"]["std"] ** 2,
           responds["/index"]["count"], responds["/test"]["count"])

print("\nHypotesis testing result:\n", testH(z, Za2))

# Output responds
open(output_fname, "w").write(simplejson.dumps(responds, indent=4 * ' '))

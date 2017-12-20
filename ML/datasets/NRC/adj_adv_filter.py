adjFile = open("adj.txt",'r')
advFile = open("adv.txt", 'r')

adj = {}
adv = {}

for line in adjFile:
	adj[line.split(" ")[0]] = 1
for line in advFile:
	adv[line.split(" ")[0]] = 1

adjFile.close()
advFile.close()

lexFile = open("NRClexicon.txt", 'r')
outputFile = open("NRClexicon1.0.txt", 'a')

for line in lexFile:
	word = line.split(",")[0]
	if word in adj or word in adv:
		outputFile.write(line)


lexFile.close()
outputFile.close()

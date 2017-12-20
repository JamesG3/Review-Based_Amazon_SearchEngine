file = open("item_dedup.json",'r')
counter = 0
for line in file:
	print line

	if counter == 100:
		break
	counter += 1
	if counter%1000000 == 0:
		print counter/1000000

print counter
file.close()
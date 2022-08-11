if __name__ == ('__main__'):

	import matplotlib.pyplot as plt
	with open('pokemon_cards.csv','r') as file:
	        data = [element.strip() for element in file.readlines()]

	header = data[0].split(',')
	data = [element.split(',')for element in data[1:]]

	# CREATING A COMPACT DATA FRAME WITH THE GENERATION AND CARD NUMBER AS THE PRIMARY KEY
	concatData = []
	for element in data:
	    concatData.append([element[0],element[1],str(element[2]) + '_' + str(element[3]),element[4]])

	# FILTERING THE DATA INTO TWO LISTS OF STANDARD CARD TYPES AND REVERSE HOLO CARD TYPES
	standards = [element for element in concatData if element[1] == 'STANDARD']
	reverse_holos = [element for element in concatData if element[1] == 'REVERSE HOLO']

	# JOINING THE PRICES WITH THE NEWLY CREATED PRIMARY KEY
	for i in standards:
	    generation = i[2]
	    for j in reverse_holos:
	        if generation == j[2]:
	            i.append(j[3])

	# CREATING A STRUCTURE INCLUDING POKEMON, GENERATION, CARD NUMBER, STANDARD PRICE, REVERSE HOLO PRICE
	# THE PRIMARY KEY WILL BE SPLIT AGAIN INTO INDIVIDUAL ATTRIBUTES
	# IF A CARD DOES NOT HAVE A REVERSE HOLO VERSION IT WILL NOT BE APPENDED TO THE LIST
	comparativeList = []
	for element in standards:
	    try:
	        comparativeList.append([element[0],element[2].split('_')[0],element[2].split('_')[1],element[3],element[4]])
	    except:
	        pass

	# AVERAGE OF STANDARD CARD TYPE PRICES
	standard_avg = sum([float(element[3]) for element in comparativeList]) / len([element[3] for element in comparativeList])
	# AVERAGE OF REVERSE HOLO CARD TYPE PRICES
	reverse_holo_avg = sum([float(element[4]) for element in comparativeList]) / len([element[4] for element in comparativeList])
	print(standard_avg,reverse_holo_avg)
	# CREATING THE DATA VISUAL
	x = ['standard','reverse holo']
	y = [standard_avg,reverse_holo_avg]
	plt.bar(x,y,color=['grey','gold'])
	plt.xlabel(xlabel='Pokemon card type')
	plt.ylabel(ylabel='Average Price £')
	plt.savefig('Average_standard_against_reverse_holo_price.png')
if __name__ == ('__main__'):

    import time
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    import csv

    def get_driver():
        #set options for easier browsing
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument('start-maximized')
        options.add_argument('disable-dev-shm-usage')
        options.add_argument('no-sandbox')
        options.add_experimental_option('excludeSwitches',['enable-automation'])
        options.add_argument('disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get('https://www.chaoscards.co.uk/shop/pokemon/singles-pokemon/sort/price-high-to-low/show/64-products/oos/yes/page/1')
        return driver
    def pokeCards():
        driver = get_driver()
        cookies = driver.find_element(by='xpath',value='/html/body/div[1]/div[5]/div[1]/div/div/div[2]/span[2]')
        cookies.click()
        lastPage = driver.find_element(by='xpath',value='/html/body/div[1]/div[4]/div[2]/main/div/div[2]/div[3]/nav/ol/li[7]/a')
        lastPage = int(lastPage.text)
        print('Last Page ',lastPage)
        cardList = []
        for page in range(0,lastPage):
            print(page+1)
            elements = driver.find_elements(By.CLASS_NAME,"prod-el")
            for card in elements:
                cardList.append(card.text)
            time.sleep(1)
            if page + 1 <= 3:
                try:
                    nextButton = driver.find_element(by='xpath',value='/html/body/div[1]/div[4]/div[2]/main/div/div[2]/div[3]/nav/ol/li[8]')
                    nextButton.click()
                except:
                    print('End of list')
            if page + 1 > 3:
                try:
                    nextButton = driver.find_element(by='xpath',value='/html/body/div[1]/div[4]/div[2]/main/div/div[2]/div[3]/nav/ol/li[9]')
                    nextButton.click()
                except:
                    print('End of list')
            time.sleep(10)
        return cardList

    # RUNNING THE SCRAPER
    cards = pokeCards()

    # SAVED TO TXT SO AS NOT TO LOSE THE DATA
    strippedCards = ['__'.join(element.split('\n')) for element in cards]
    newLines = [str(element) + '\n' for element in strippedCards]
    with open('dirty_Pokemon_Cards.txt','w',encoding='utf-8') as file:
        file.writelines(newLines)

    # READING THE DATA
    with open('dirty_Pokemon_Cards.txt','r',encoding='utf-8') as file:
        data = [element.strip().split('__') for element in file.readlines()]
    cleanData = []

    # CUTTING OUT IRRELEVANT DATA
    for element in data:
        if element[0] == 'OUT OF STOCK':
            cleanData.append(element[1:3])
        else:
            cleanData.append(element[0:2])
            
    # CLEANING THE FROM STRINGS FROM PRICE FIELD
    for element in cleanData:
        index = cleanData.index(element)
        x = element[1].split(' ')
        if x[0] == 'FROM':
            cleanData[index][1] = x[1]
        if x[0] != 'FROM':
            if len(element[1].split(' ')) > 1:
                cleanData[index][1] = element[1].split(' ')[0]
                
    # REMOVING POUND SYMBOL
    for element in cleanData:
        index = cleanData.index(element)
        cleanData[index][1] = element[1].split('£')[-1]

    #REMOVING RECORDS WITH MISSING PRICES (LAST CHECKED ONLY ONE SET THAT HAS NO BUSINESS BEING IN THE SINGLE CARDS WEBPAGE)
    for element in cleanData:
        index = cleanData.index(element)
        if len(element[1]) == 0:
            cleanData.remove(element)  
        
    # SPLITTING POKEMON AND GENERATION
    splitList = []
    num = 1
    for element in cleanData:
        splitData = element[0].split(' : ')
        try:
            testSplitIndex = splitData[0].split(' ')[1]
        except:
            textSplitIndex = 'NA'
        if len(splitData) < 2:
            splitList.append([str(splitData[0].split(' - Pokemon Single Card')[0]).split(' - Pokemon Single Promotional Card')[0],'UNKNOWN',element[1]])
        if len(splitData) >= 2:
            if testSplitIndex == 'JAPANESE':
                splitList.append([str(splitData[1].split(' - Pokemon Single Card')[0]).split(' - Pokemon Single Promotional Card')[0],splitData[0].split(' - Pokemon Single Card')[0],element[1]])
            if testSplitIndex != 'JAPANESE':
                splitList.append([str(splitData[0].split(' - Pokemon Single Card')[0]).split(' - Pokemon Single Promotional Card')[0],splitData[1].split(' - Pokemon Single Card')[0],element[1]])     

    # REMOVING ONLINE CARDS
    physicalCards = []
    for element in splitList:
        if element[0] != 'Pokemon Code Card':
            physicalCards.append(element)

    # FIXING REMAINING REVERSED POKEMON AND GENERATION FIELDS
    for element in physicalCards:
        index = physicalCards.index(element)
        try:
            if int(element[0].split('/')[-1]) > 0:
                generation = element[0]
                card = element[1]
                price = element[2]
                physicalCards[index] = [card,generation,price]
        except:
            pass

    # REMOVING ALL UNKNOWN CARDS AND GENERATIONS
    noUnknowns = []
    for element in physicalCards:
        if element[0] != 'UNKNOWN':
            if element[1] != 'UNKNOWN':
                noUnknowns.append(element)

    # SPLITTING GENERATIONS AND CARD NUMBERS
    cardNumberList = []
    for element in noUnknowns:
        if len(element[1].split('/')) > 1:
             cardNumberList.append([element[0],' '.join(element[1].split(' ')[0:len(element[1].split(' '))-1]).strip(' -'),' of '.join(str(element[1].split(' ')[-1]).split('/')),element[2]])
        else:
            cardNumberList.append([element[0],element[1].strip(' -'),'UNKNOWN',element[2]])

    # STRUCTURING THE RECORDS TO ADD THE TYPE OF CARD IT IS E.G. REVERSE HOLLOW OR STANDARD
    finalList = []
    for element in cardNumberList:
        if len(element[0].split('(')) > 1:
            finalList.append([element[0].split(' (')[0].upper(),element[0].split(' (')[1].strip(')').upper(),element[1].upper(),element[2].upper(),element[3].upper()])
        else:
            finalList.append([element[0].upper(),'STANDARD',element[1].upper(),element[2].upper(),element[3].upper()])
        
    # REMOVING ROGUE BRACKETS
    for element in finalList:
        index = finalList.index(element)
        finalList[index][1] = ' '.join(element[1].split(')('))
        
    # WRITING TO A CSV
    header = ['Pokemon','Card Type','Generation','Card Number','Price £']
    with open('pokemon_cards.csv','w',newline='') as file:
        writer = csv.writer(file)
        # write the header
        writer.writerow(header)
        # write multiple rows
        writer.writerows(finalList)

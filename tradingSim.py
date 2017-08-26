from lxml import html
import requests
import csv
import _thread
import time

fileName = "data.csv"
cash = 0;
marginBalance = 0;
#each stock is in the format of (name, average price per stock, amount)
portfolio = []

def getPortfolioValue():
    global portfolio
    global cash
    totalValue = cash
    for i in range(0,len(portfolio)):
        tempList = list(portfolio[i])
        tempList[3] = getCurrentStockPrice(portfolio[i][0])
        portfolio[i] = tuple(tempList)
        
        #if current position is a short, then get the value by taking the profit
        if(portfolio[i][2] < 0):
            #(current price - average price) * amount of shares
            stockValue = (portfolio[i][3] - portfolio[i][1]) * portfolio[i][2]
        else:
            stockValue = portfolio[i][3] * portfolio[i][2]
        totalValue = totalValue + stockValue
    return totalValue


def addToPortfolio(tickerName, price, shares):
    global portfolio
    cost = (price * shares)
    portfolioIndex = getStockIndex(tickerName)
    if(portfolioIndex != -1):
        totalShares = portfolio[portfolioIndex][2] + shares
        #closing a position
        if(totalShares == 0):
            del portfolio[portfolioIndex]
        else:
            averagePrice = portfolio[portfolioIndex][2]
            #if increasing existing position then readjust the average cost
            #if decreasing or closing a position, then the average price doesn't get adjusted
            if(abs(totalShares) > abs(portfolio[portfolioIndex][2])):
                #account for change in average price per share
                averagePrice = (cost + (portfolio[portfolioIndex][1] * portfolio[portfolioIndex][2])) / totalShares
                
            #update the current entry
            portfolio[portfolioIndex] = (tickerName, averagePrice, totalShares, price)
    else:
        portfolio.append((tickerName, price, shares, price))
        
    savePortfolio()
    return
def priceToFloat(priceStr):
	priceFloat = ''
	for i in range(0, len(priceStr)):
		if((priceStr[i] <= '9' and priceStr[i] >= '0') or (priceStr[i] is '.')):
			priceFloat = priceFloat + priceStr[i]
			
	return float(priceFloat)
			

def getCurrentStockPrice(ticker):
    price = -1
    priceFloat = float(-1)

    while(priceFloat == -1):
        print("Getting price...\n")
        page = requests.get('https://www.google.com/finance?q=%3A' + ticker)
        pageContent = str(page.content)
        
        priceStartIdx = pageContent.find("meta itemprop=\"price\"")
        
        contentStartIdx = pageContent.find("content", priceStartIdx)
        if(priceStartIdx != -1 and contentStartIdx != -1):
            
            firstQuote = pageContent.find("\"", contentStartIdx)
            secondQuote = pageContent.find("\"", firstQuote + 1) 
            
            if(firstQuote != -1 and secondQuote != -1):
                price = pageContent[firstQuote + 1: secondQuote]
                price = price.replace(',', '')
                priceFloat = float(price)
	
    return priceFloat

def loadPortfolio():
	myCsv = open(fileName, 'r+')
	csvBuffer = myCsv.read()
	csvRows = csvBuffer.split('\n')
	rowsList  = []

	for rows in csvRows:
		line = rows.split(',')
		list_buffer = []
		for i in line:
			if(len(i)):
				list_buffer.append(str(i))
		rowsList.append(list_buffer)

		
	global cash
	cash = float(rowsList[0][0])

	for i in range(1,len(rowsList)):
		if(len(rowsList[i]) == 3):
			name = str(rowsList[i][0])
			cost = float(rowsList[i][1])
			shares = int(rowsList[i][2])
			#loadportfolio only initializes the data structures and doesn't update value from online
			currentPrice = -1.0
			portfolio.append((name, cost, shares, currentPrice))
	
	myCsv.close()
	return 
	

    
    
def savePortfolio():
	myCsv = open(fileName, 'w+')
	myCsv.write(str(cash))
	myCsv.write("\n")
	
	for i in range(0, len(portfolio)):
		myCsv.write(str(portfolio[i][0])) #name
		myCsv.write(",")
		myCsv.write(str(portfolio[i][1])) #average cost
		myCsv.write(",")
		myCsv.write(str(portfolio[i][2])) #count
		myCsv.write("\n")
	myCsv.close()
	return
	

def getPercentGain(tickerIndex):
    global portfolio
    percentGain = (portfolio[tickerIndex][3] - portfolio[tickerIndex][1]) * 100 / portfolio[tickerIndex][1];
    
    #if it's a short position reverse the sign
    if(portfolio[tickerIndex][2] < 0):
        percentGain = -percentGain;
        
    return percentGain
	
def printPortfolio():
	print("\nCash: $", cash, "\n")
	currentPortfolioValue = getPortfolioValue()
    #don't print portfolio value for now. it messes with the trading behavior
    # print("Portfolio Value: $", currentPortfolioValue, " (", (currentPortfolioValue - 25000) * 100/ 25000,  "%)\n")
	for i in range(0, len(portfolio)):
		print("Name: ", portfolio[i][0])
		print("Avg Price: $", portfolio[i][1])  
		print("Current Price: $", portfolio[i][3], "(", getPercentGain(i), "%)")
		print("Shares: ", portfolio[i][2], "\n")
	return
	
#start of program

def getStockIndex(name):
	global portfolio
	
	for i in range(0, len(portfolio)):
		if(portfolio[i][0] == name):
			return i
	return -1

def marketBuy(tickerName, shares):
    global cash;
    price = getCurrentStockPrice(tickerName)
    transactionFee = (0.005 * abs(shares))
    cost = (price * shares)
    if(cost + transactionFee > cash):
        print("You don't have enough cash to buy!\n")
    else:
        cash = cash - cost - transactionFee
        addToPortfolio(tickerName, price, shares)  
    return
	
def limitBuy(tickerName, limitPrice, shares):
    global cash;
    #block until price is less or equal
    price = getCurrentStockPrice(tickerName)
    while(price > limitPrice):
        price = getCurrentStockPrice(tickerName)
        
    transactionFee = (0.005 * abs(shares))
    cost = price * shares
    cash = cash - cost - transactionFee
    addToPortfolio(tickerName, price, shares)
	
    print("\n", tickerName, "has been bought.\n")
    return
	
def buyStock():
    global portfolio
    ticker = input('Enter stock ticker: ')
    price = getCurrentStockPrice(ticker)
    print(ticker, " is $" + str(price) + ".")

    if(price > 0):
        option = input("Order type: (1)Market or (2)Limit. (3)Buy to Cover. (0)Cancel.")	
        if(option == "1"):
            shares = int(input("How many " + ticker + " would you like to buy?"))
            marketBuy(ticker, shares)
        elif(option == "2"):
            shares = int(input("How many " + ticker + " would you like to buy?"))
            limitPrice = float(input("Enter your limit price: "))
            transactionFee = shares * 0.005
            minimumCost = limitPrice * shares
            if(minimumCost + transactionFee > cash):
                print("You don't have enough cash to buy!\n")
            else:
                _thread.start_new_thread(limitBuy, (ticker, limitPrice, shares))
                print("Your order for buying", ticker, "at limit price", limitPrice, "has been entered.")
        elif(option == "3"):
            shares = int(input("How many " + ticker + " would you like to buy?"))
            buyCover(ticker, shares)
    else:
        print("Please check your ticker and try again.")
	
    return

	
def sellStock():
    global portfolio
    ticker = input('Enter stock ticker: ')
    portfolioIndex = getStockIndex(ticker)

    price = getCurrentStockPrice(ticker)
    print(ticker, " is $" + str(price) + ".")

    if(price > 0):
        option = input("Order type: (1)Market, (2)Limit, (3)Sell Short. (0)Cancel.")
        if(option == "1"):
            if(portfolioIndex == -1):
                print("You don't have any", ticker, "stocks to sell!")
                return
            shares = int(input("How many " + ticker + " would you like to sell?"))
            if(shares > portfolio[portfolioIndex][2]):
                print("You don't have enough shares to sell!\n")
                return
            marketSell(ticker, shares)
        elif(option == "2"):
            if(portfolioIndex == -1):
                print("You don't have any", ticker, "stocks to sell!")
                return
            if(shares > portfolio[portfolioIndex][2]):
                print("You don't have enough shares to sell!\n")
                return
            shares = int(input("How many " + ticker + " would you like to sell?"))
            limitPrice = float(input("Enter your limit price: "))
            _thread.start_new_thread(limitSell, (ticker, limitPrice, shares))
            print("Your order for selling", ticker, "at limit price", limitPrice, "has been entered.")
        elif(option == "3"):
            shares = int(input("How many " + ticker + " would you like to short?"))
            #only supports market price shorting for now
            shortSell(ticker, shares)
    else:
        print("Please check your ticker and try again.")
    return
	
def marketSell(tickerName, shares):
    global cash
    price = getCurrentStockPrice(tickerName)
    transactionFee = abs(shares) * 0.005
    cost = shares * price;
    cash = cash + cost - transactionFee
    addToPortfolio(tickerName, price, -shares)
    return
	
def limitSell(tickerName, limitPrice, shares):
    #block until price is greater or equal
    price = getCurrentStockPrice(tickerName)
    while(price < limitPrice):
        price = getCurrentStockPrice(tickerName)
    transactionFee = shares * 0.005
    cost = price * abs(shares)
    cash = cash + cost - transactionFee
    addToPortfolio(tickerName, price, -shares)
    print("\n", tickerName, "has been sold.\n")
    return

   
def shortSell(tickerName, shares):
    global portfolio
    global cash
    transactionFee = shares * 0.005
    if(transactionFee > cash):
        print("You don't have enough cash for this transaction!\n");
    else:
        portfolioIndex = getStockIndex(tickerName)
        #if a position already exists
        if(portfolioIndex != -1):
            #if the existing position is a short
            if(portfolio[portfolioIndex][2] > 0):
                print("You can't short an existing long position!\n");
                return
            else:
                price = getCurrentStockPrice(tickerName)
                addToPortfolio(tickerName, price, -shares)
        #new position
        else:
            price = getCurrentStockPrice(tickerName)
            addToPortfolio(tickerName, price, -shares)
    return

def buyCover(tickerName, shares):
    global portfolio
    global cash
    
    portfolioIndex = getStockIndex(tickerName)
    #check if position exists
    if(portfolioIndex != -1):
        #check if the existing position is a short position
        if(portfolio[portfolioIndex][2] < 0):
            transactionFee = shares * 0.005
            if(transactionFee > cash):
                print("You don't have enough cash for this transaction!\n");
                
            price = getCurrentStockPrice(tickerName)
            #profit = shares * (currentPrice - averagePrice)
            profit = (-shares * price) - (portfolio[portfolioIndex][1] * -shares)
            cash = cash + profit
            addToPortfolio(tickerName, price, shares)
        else:
            print("You don't have any ", tickerName, " short positions to cover!\n")
    else:
        print("You don't have any ", tickerName, " short positions to cover!\n")

userInput = -1
loadPortfolio()
printPortfolio()
while(userInput != "0"):
	print("\n0. Exit\n")
	print("1. Buy\n")
	print("2. Sell\n")
	print("3. List Portfolio\n")
	print("5. Test Function")
	userInput = input('Enter your Selection: ')
	
	if(userInput == "1" or userInput == "buy"):
		buyStock()
		printPortfolio()
	elif(userInput == "2" or userInput == "sell"):
		sellStock()
		printPortfolio()
	elif(userInput == "3" or userInput == "list"):
		printPortfolio()
	elif(userInput == "5"):
        
    
    
		print(5)
	
	
	




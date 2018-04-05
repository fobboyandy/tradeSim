from lxml import html
import requests
import csv
import _thread
import time
import sys
import datetime


portfolio = [];
cash = 0;
saveFile = "";
logFile = "";
usernameIn = ""
actionIn = ""
tickerIn = ""
sharesIn = ""

def getTime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#this function parses the RESTful api into valid arguments
def parseCommands():
    global usernameIn
    global saveFile
    global logFile;
    #input has to come in the order of username action stockname and shares
    #username will always be provided in the first command
    usernameIn = sys.argv[1]
    saveFile = ".\\" + usernameIn + ".csv";
    logFile =  ".\\" + usernameIn + ".html";
    
    # for i in range(0, len(sys.argv)):
        # print(sys.argv[i])
    #if there are other commands parse them
    if(len(sys.argv) == 5):
        global actionIn
        global tickerIn
        global sharesIn
        try:
            actionIn = str(sys.argv[2])
        except:
            print("Please provide a valid action!<br></br>")
            exit()
            
        try:
            tickerIn = str(sys.argv[3])
        except:
            print("Please provide a valid stock ticker!<br></br>")
            exit()   
            
        try:
            sharesIn = int(sys.argv[4])
        except:
            print("Please provide an integer number of share!<br></br>")
            exit()
    return

def getStockIndex(name):
	global portfolio
	
	for i in range(0, len(portfolio)):
		if(portfolio[i][0] == name):
			return i
	return -1
    

def savePortfolio():
	myCsv = open(saveFile, 'w+')
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
	
def getCurrentStockPrice(ticker):
    price = -1
    priceFloat = float(-1)

    i = 0;
    #try to get the price 3 times
    while(priceFloat == -1 and i < 3):
        i = i + 1
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

def getPercentGain(tickerIndex):
    global portfolio
    percentGain = (portfolio[tickerIndex][3] - portfolio[tickerIndex][1]) * 100 / portfolio[tickerIndex][1];
    
    #if it's a short position reverse the sign
    if(portfolio[tickerIndex][2] < 0):
        percentGain = -percentGain;
        
    return percentGain
    
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


def printPortfolio():
    global portfolio;
    

    
    print("Cash: $", cash, "<br></br>")
    currentPortfolioValue = getPortfolioValue()
    #don't print portfolio value for now. it messes with the trading behavior
    print("Portfolio Value: $", currentPortfolioValue, " (", (currentPortfolioValue - 25000) * 100/ 25000,  "%)<br></br>")
    for i in range(0, len(portfolio)):
        print("Name: ", portfolio[i][0], "<br></br>")
        print("Avg Price: $", portfolio[i][1], "<br></br>")  
        print("Current Price: $", portfolio[i][3], "(", getPercentGain(i), "%)<br></br>")
        print("Shares: ", portfolio[i][2], "<br></br>")
    
    myLog = open(logFile, 'r');
    myLog.close();
    return


def loadPortfolio():
    global saveFile
    myCsv = open(saveFile, 'r+')
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
    

def addToPortfolio(tickerName, price, shares):
    myLog = open(logFile, 'a')
    myLog.write(getTime() + " " + tickerName + " " + str(price) + " " + str(shares) + "<br></br>");
    global portfolio
    cost = (price * shares)
    portfolioIndex = getStockIndex(tickerName)
    if(portfolioIndex != -1):
        totalShares = portfolio[portfolioIndex][2] + shares
        #closing a position
        if(totalShares == 0):
            del portfolio[portfolioIndex]
        else:
            averagePrice = portfolio[portfolioIndex][1]
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
    myLog.close()
    return

    
def marketBuy(tickerName, shares):
    global cash;
    price = getCurrentStockPrice(tickerName)
    transactionFee = 5 #(0.005 * abs(shares))
    cost = (price * shares)
    if(cost + transactionFee > cash):
        print("You don't have enough cash to buy!<br></br>")
    else:
        cash = cash - cost - transactionFee
        addToPortfolio(tickerName, price, shares)  
    return    


def buyCover(tickerName, shares):
    global portfolio
    global cash
    portfolioIndex = getStockIndex(tickerName)
    #check if position exists
    if(portfolioIndex != -1):
        #check if the existing position is a short position
        if(portfolio[portfolioIndex][2] < 0):
            if(abs(shares) <= abs(portfolio[portfolioIndex][2])):
                transactionFee = 5#shares * 0.005
                if(transactionFee > cash):
                    print("You don't have enough cash for this transaction!<br></br>");
                    
                price = getCurrentStockPrice(tickerName)
                #profit = shares * (currentPrice - averagePrice)
                profit = (-shares * price) - (portfolio[portfolioIndex][1] * -shares)
                cash = cash + profit
                addToPortfolio(tickerName, price, shares)
            else:
                print("You are covering more short shares than you own! <br></br>")
        else:
            print("You don't have any ", tickerName, " short positions to cover!<br></br>")
    else:
        print("You don't have any ", tickerName, " short positions to cover!<br></br>")
    
def buyStock():
    price = getCurrentStockPrice(tickerIn)
    myLog = open(logFile, 'a')
    if(price > 0):
        if(actionIn == "buy"):
            myLog.write("Entered long at ")
            myLog.close();
            marketBuy(tickerIn, sharesIn)
        elif(actionIn == "buyCover"):
            myLog.write("Covered existing short at")
            myLog.close();
            buyCover(tickerIn, sharesIn)
    else:
        print("Please check your ticker and try again.<br></br>")
	
    return    
    
def marketSell(tickerName, shares):
    global cash
    price = getCurrentStockPrice(tickerName)
    transactionFee = 5#abs(shares) * 0.005
    cost = shares * price;
    cash = cash + cost - transactionFee
    addToPortfolio(tickerName, price, -shares)
    return
	

def shortSell(tickerName, shares):
    global portfolio
    global cash
    transactionFee = 5#shares * 0.005
    if(transactionFee > cash):
        print("You don't have enough cash for this transaction!<br></br>");
    else:
        portfolioIndex = getStockIndex(tickerName)
        #if a position already exists
        if(portfolioIndex != -1):
            #if the existing position is a short
            if(portfolio[portfolioIndex][2] > 0):
                print("You can't short an existing long position!<br></br>");
                return
            else:
                price = getCurrentStockPrice(tickerName)
                addToPortfolio(tickerName, price, -shares)
        #new position
        else:
            price = getCurrentStockPrice(tickerName)
            addToPortfolio(tickerName, price, -shares)
    return
    
    
def sellStock():
    myLog = open(logFile, 'a')
    global portfolio
    portfolioIndex = getStockIndex(tickerIn)
    price = getCurrentStockPrice(tickerIn)
    if(price > 0):
        if(actionIn == "sell"):
            if(portfolioIndex == -1):
                print("You don't have any", tickerIn, "stocks to sell!")
                return
            if(sharesIn > portfolio[portfolioIndex][2]):
                print("You don't have enough shares to sell!\n")
                return
            myLog.write("Selling existing position at ");
            myLog.close()
            marketSell(tickerIn, sharesIn)
        elif(actionIn == "sellShort"):
            myLog.write("Entered short position at ");
            myLog.close()
            shortSell(tickerIn, sharesIn)
    else:
        print("Please check your ticker and try again.<br></br>")
    return
	 

def closePosition():
    global portfolio;
    portfolioIndex = getStockIndex(tickerIn)
    if(portfolioIndex != -1):
        #current position is a long
        if(portfolio[portfolioIndex][2] > 0):
            marketSell(tickerIn, portfolio[portfolioIndex][2])
        else:
            buyCover(tickerIn, abs(portfolio[portfolioIndex][2]))
    else:
        print("You don't have a(n)", tickerIn ,"position open!<br></br>");
    
    
    return
 
parseCommands();
try:
    myCsv = open(saveFile, 'r+');
except:
    #create a new save file
    myCsv = open(saveFile, 'w+')
    myCsv.write(str(25000))
    myCsv.write("\n")
    
try:
    myLog = open(logFile, 'r+')
except:
    myLog = open(logFile, 'a')
    
    
print("Welcome:", usernameIn, "<br></br>")
myCsv.close()  
myLog.close();
loadPortfolio()
#if user requires action
if(len(sys.argv) == 5):
    if(actionIn == "buy" or actionIn == "buyCover"):
        buyStock()
    elif(actionIn == "sell" or actionIn == "sellShort"):
        sellStock()
    elif(actionIn == "close"):
        closePosition()

printPortfolio()


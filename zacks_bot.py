import  urllib2
import re
import requests
import datetime
from iexfinance import Stock
from iexfinance import get_historical_data
#import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

class WebsiteScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.stocks_set = set() 

        self.current_date = datetime.date.today().strftime('%B %d, %Y')
    def open_url(self, url):
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'})
            c = response.content
            soup = BeautifulSoup(c, "html.parser")
            return soup        
        except Exception as e:
            print(e)
            print("Failed to open URL")
            try:
                print("Response Code: " +  str(response.status_code))
            except Exception as e:
                print(e)   
                print("No response code")
    
    def is_website_scraped(self, url):
        pass    

    def return_stocks(self):
        return frozenset(self.stocks_set)
    
    def print_stocks(self):
        print ("Zacks recommends these stocks: "+ str(self.stocks_set))
        print("----------------------------------------------------------------------------------------------------------")

class ZacksScraper(WebsiteScraper):
    def __init__(self, base_url):
        WebsiteScraper.__init__(self, base_url)
        
    def is_website_scraped(self):
        print("----------------------------------------------------------------------------------------------------------")
        is_base_url_verified = self.verify_url_0(self.base_url)
        print ("Base url verified: " + str(is_base_url_verified)) 
        print("------------------------------------")
        is_top_url_verified =  self.verify_url_1(self.top_url)
        print ("Top stocks verified: " + str(is_top_url_verified))                
        print("------------------------------------")
        verification_status = is_base_url_verified and is_top_url_verified 
        print("Zacks verification status: " + str(verification_status))  
        return verification_status

    def verify_url_0(self, url):
        try:
            print("Parsing Zacks Rank...")
            print("Finding appropriate link in main page...")
            soup = self.open_url(url)
            for element in soup.findAll("article", {"class": "bull_of_the_day"}):
                s = element.text.strip()    
                if "Bull of the Day" in element.text.strip():
                    bull = str((s[s.find("(")+1:s.find(")")])) 
                    print("Bull of the Day: " + bull)
                    self.stocks_set.add(bull)    
                    break

            for element in soup.findAll("p"):
                if "Zacks #1 Rank Additions" in element.text.strip():
                    self.top_url = "https://www.zacks.com" + str(element.find('a').get('href'))
                    print("Text Verification: " + str(element.text.strip()))
                    print("Link Verification: " + self.top_url)
                    return True
            return False
        except Exception as e:
            print(e)
            return False
               
    def verify_url_1(self, url):
        try:
            print("Parsing article page...")
            soup = self.open_url(url)    
            article_date = soup.find("time").text.strip()
            article_title = str(soup.title.string)
            is_title_valid = "strong" in article_title.lower() and "buy" in article_title.lower()
            is_date_valid = article_date == self.current_date 
            is_article_verified = is_date_valid and is_title_valid 
            {self.stocks_set.add(str(i.text.strip())) for i in soup.findAll("span", {"class": "hoverquote-symbol"})};
            
            print("System date: " + str(self.current_date))
            print("Article date: " + str(article_date))
            print("Dates match: " + str(is_article_verified))
            print("Article Title: " +str(soup.title.string))
            print("Stocks recommeded from article: " + str(self.stocks_set))
            return is_article_verified

        except Exception as e:
            print(e)
            return False
    

#Open url and parse stocks to buy
stocks_set = set() 
zacks_scraper = ZacksScraper("https://www.zacks.com/stocks/zacks-rank")

while True:
    if zacks_scraper.is_website_scraped():
        stocks_set.add(zacks_scraper.return_stocks())
        zacks_scraper.print_stocks()
        break

#init stock dict
bought_stocks = {}
cross_verified_stocks = {}
for i in stocks_set:
    for j in i:
        if j not in bought_stocks:
            bought_stocks[j] = Stock(j).get_price()
print("Bought these stocks: ")
print(bought_stocks)
print("----------------------------------------------------------------------------------------------------------")


stocks_remaining = True
#run for rest of day
while stocks_remaining:
    for stock in bought_stocks.keys():
        buy_price = bought_stocks[stock]
        current_price = Stock(stock).get_price()
        #print(stock + ": " + "Buy price: " + str(buy_price) + " Current price: " + str(current_price))
        if (current_price > (buy_price*1.01)):
            print("Selling " + stock + " Buy price: " + str(buy_price) + " Sell price: " +str(current_price))
            del bought_stocks[stock]
        elif (current_price < (buy_price*.98)):
            print("Selling " + stock + " Buy price: " + str(buy_price) + " Sell price: " +str(current_price))
            del bought_stocks[stock]
        elif (current_price == buy_price):
            pass
            #print("Selling " + stock + " Buy price: " + str(buy_price) + " Sell price: " +str(current_price))
            #del bought_stocks[stock]
    stocks_remaining = bool(bought_stocks) 


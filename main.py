import sys
import os
import pyotp
import robin_stocks
from robin_stocks import *
import csv
from datetime import datetime
import time



EMAIL = ''
PASSWD = ''

login = robinhood.login(EMAIL,PASSWD)

my_stocks =  robinhood.build_holdings(34476)
for key,value in my_stocks.items():
    print(key,value)

price_desired_to_invest = 800
invested = False
invested_at = 0
sold_at = 0
price_now = 0
price_list = [0.0,0.0,0.0,0.0,0.0]
price_slope = [0,0,0,0]
valley_found = False
earned = 0
percentage = 0
time_tics = 0
number_of_trades =0

####################
my_virtual_wallet = 1000
total_budget_began_with = my_virtual_wallet
on_bit = 0
####################

filename = 'crypto_log.csv'
row = ['Date', 'Time', 'Bought at', 'Sold at', 'Input', 'Output', 'Profit', 'Percentage']
with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(row)



def price_list_add(price):
    global price_now
    global price_list
    price_now = price
    price_list[0] = price_list[1]
    price_list[1] = price_list[2]
    price_list[2] = price_list[3]
    price_list[3] = price_list[4]
    price_list[4] = price

def calculator():
    global earned
    global percentage
    percentage = (price_now - invested_at)/invested_at
    earned = price_desired_to_invest * percentage
    
def slope_calculator():
    if(price_list[0] != 0):
        price_slope[0] = round(price_list[1] / price_list[0] -1, 10)
    if(price_list[1] != 0):
        price_slope[1] = round(price_list[2] / price_list[1] -1, 10)
    if(price_list[2] != 0):
        price_slope[2] = round(price_list[3] / price_list[2] -1, 10)
    if(price_list[3] != 0):
        price_slope[3] = round(price_list[4] / price_list[3] -1, 10)


def valley_detector():
    if (price_slope[2] < 0 and price_slope[3] > 0):
        global valley_found
        valley_found = True

def buy_crypto():
    global invested
    global invested_at
    global valley_found
    global time_tics


    invested = True
    invested_at = price_now
    valley_found = False
    time_tics = -1


    global my_virtual_wallet
    global on_bit
    my_virtual_wallet -= price_desired_to_invest
    on_bit += price_desired_to_invest

def sell_detector():
    if(percentage <= 0.25 and price_slope[3] < 0):
        sell_crypto()
        return
    if(time_tics == 0):
        return
    elif(time_tics == 1):
        if(price_slope[3] < 0):
            sell_crypto()
            return
    elif(time_tics == 2):
        if(price_slope[2] > 0 and price_slope[1] > 0):
            sell_crypto()
            return
        elif(price_slope[3] < 0):

            sell_crypto()
            return
        elif(price_slope[3]>0):
            if(price_slope[3]>price_slope[2]):
                return
            elif(price_slope[3]<price_slope[2]): 
                if(price_slope[3]>=0.07):
                    return
                else:
                    sell_crypto()
                    return
    elif(time_tics == 3):
        sell_crypto()
        return


def sell_crypto():
    global invested
    global invested_at
    global valley_found
    global sold_at
    global number_of_trades
    number_of_trades += 1
    invested = False
    sold_at = price_now
    valley_found = False
    write_log()

    global on_bit
    global my_virtual_wallet
    on_bit += ((sold_at - invested_at)/invested_at)*price_desired_to_invest 
    my_virtual_wallet += on_bit 
    on_bit = 0
    print(f"{((sold_at - invested_at)/invested_at * price_desired_to_invest):.10f}" +" made from "+ f"{(invested_at):.10f}")


def write_log():
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second
    weekday = now.isoweekday()

    row = ["Date", str(hour)+":"+str(minute), invested_at, sold_at, price_desired_to_invest, sold_at-invested_at+price_desired_to_invest, (sold_at-invested_at),str((sold_at - invested_at)/invested_at)+"%"]
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)



def main_brain():
    cur_pri = float(robinhood.crypto.get_crypto_quote('BTC', "mark_price"))
    price_list_add(cur_pri)
    slope_calculator()

    if (invested == False):
        valley_detector()
        if (valley_found):
            buy_crypto()
    elif (invested == True):
        global time_tics
        time_tics += 1
        calculator()
        sell_detector()


for i in range(24):
    print("\n\nCHAPTER #" + str(i))

    main_brain()
    if(i == 0):
        price_slope[3] = 0
    elif(i == 1):
        price_slope[2] = 0
    elif (i == 2):
        price_slope[1] = 0
    elif (i == 3):
        price_slope[0] = 0
    if(invested):
        print(str(invested_at)+"  ===>>>  " + str(price_now))
    print("BID:: " + str(on_bit))
    print("WALLET:: " + str(my_virtual_wallet))
    print("TOTAL:: "+ str((on_bit + my_virtual_wallet)))
    print("Prices::  " + str(price_list))

    print("SLOPE::  " + f"{price_slope[0]:.10f}% "+ f"{price_slope[1]:.10f}% "+ f"{price_slope[2]:.10f}% "+ f"{price_slope[3]:.10f}% ")


    if((on_bit + my_virtual_wallet) <= total_budget_began_with * 0.7):
        print("Lost 30% of money you invested. Automatically shutting down")
        break
        
    time.sleep(1800)

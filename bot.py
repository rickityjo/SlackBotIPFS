from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import os
from threading import Thread
from slack import WebClient
import slack_sdk
from flask_ngrok import run_with_ngrok
import sys
from dotenv import load_dotenv
import datetime
import yfinance as yf
import subprocess
from matplotlib import pyplot as plt
plt.style.use('ggplot')

load_dotenv()

SLACK_TOKEN=os.getenv('SLACK_TOKEN')
SIGNING_SECRET=os.getenv('SIGNING_SECRET')

slack_client = WebClient(SLACK_TOKEN)

def create_graph():
    
    symbol = 'GOOGL'
    ticker = yf.Ticker(symbol).info
    market_price = ticker['regularMarketPrice']
    previous_close_price = ticker['regularMarketPreviousClose']
    dt = datetime.datetime.now()

    # get weekday name
    day_name = 'Friday' #dt.strftime('%A')
    today = datetime.datetime.today().date()
    file_name = today - datetime.timedelta(days=today.weekday())
    file_name = str(file_name) + '.txt'

    change = ((market_price-previous_close_price)/previous_close_price)*100
    f=open(file_name, 'a')
    # f.write(str(day_name))
    # f.write('\n')
    # f.write(str(change))
    # f.write('\n\n')
    # f.close()
    
    output = subprocess.check_output(["ipfs", "add", file_name])
    output = output.decode('utf-8')
    output = output.split(' ')[1]
    f=open('hashes.txt', 'a')
    f.write(str(today))
    f.write(' : ')
    f.write(str(output))
    f.write('\n')
    f.close()

    # clear file to be ready for new week
    if day_name == 'Friday':
        f=open(file_name, 'r')
        lines = f.readlines()
        nums = []
        days = []
        for line in lines:
            if line.startswith('-') or line[0].isdigit():
                line = (float(line))*10
                nums.append(line)
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        x_pos = [i for i, _ in enumerate(days)]
        fig = plt.figure(figsize =(10, 7))

        # Horizontal Bar Plot
        plt.bar(days, nums, align='center')

        plt.xticks(x_pos, days)
        plt.savefig('foo.pdf')

        response = slack_client.files_upload(    
            file='foo.pdf',
            initial_comment='Image',
            channels='stockupdate'
        )
        f.close()
        f=open(file_name, 'w')
        f.write('')
        f.close()

        best_day = days[nums.index(max(nums))]

        message = 'The best day to buy ' + symbol + ' was: ' + best_day
        slack_client.chat_postMessage(channel='stockupdate', text=message)

if __name__ == "__main__":
    create_graph()





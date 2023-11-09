#!/usr/bin/env python
import pika
import sys
import requests
from bs4 import BeautifulSoup
import regex as re
import json
import threading

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    parse_page_links(url="https://999.md/ro/list/computers-and-office-equipment/processors", channel=channel)

    connection.close()

def parse_page_links(url, url_list=list(), max_page_num = None, page_num = 0, channel = None):
    if max_page_num is None or page_num < max_page_num:
        #get page content
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        
        #add links to list
        url_list = get_list_links(soup)

        #get next page
        next_page = go_next_page(soup)
        if next_page is not None:
            for link in url_list:
                message = link
                channel.basic_publish(
                    exchange='',
                    routing_key='task_queue',
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ))
                print(f" [x] Sent {message}")
            parse_page_links(url=next_page, url_list=url_list, max_page_num=max_page_num, page_num=page_num+1)
        else:
            print("No more pages to parse")

    return "Done"

def get_list_links(soup):
    list = []
    a = soup.find_all('div', class_='ads-list-photo-item-title')
    for b in a:
        for link in b.find_all('a'):
            final = link.get('href')
            # eliminate links that have booster in them, because they are not real ads.
            if final.find("booster") != -1:
                continue
            else:
                l = "https://999.md" + final
                list.append(str(l))
    
    print("Found " + str(len(list)) + " links")

    return list

def go_next_page(soup):
    current_page = soup.find('li', class_='current')
    next_page_li = current_page.find_next_sibling('li')
    if next_page_li is not None:
        next_page_href = next_page_li.find('a').get('href')
        print("Next page is: " + next_page_href)
        next_page = "https://999.md" + next_page_href
    else:
        next_page = None
    return next_page

if __name__ == '__main__':
    main()
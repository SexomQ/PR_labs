#!/usr/bin/env python
import pika
import time
import requests
from bs4 import BeautifulSoup
import regex as re
import json
from tinydb import TinyDB, Query

def main():

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')


    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    channel.start_consuming()


def callback(ch, method, properties, body):
    db = TinyDB('tinydb.json')
    Processors = Query()

    def get_data(url=None, db=None):
        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        title_header = soup.find('header', class_ = "adPage__header")
        title = title_header.find('h1').text
        if soup.find('div', class_ = "adPage__content__description grid_18") is None:
            description = "None"
        else:
            description = soup.find('div', class_ = "adPage__content__description grid_18").text
        # print(description)

        features = []
        features_div = soup.find('div', class_ = "adPage__content__features")
        features_ul = features_div.find_all("li", class_ = "m-value")

        for feature in features_ul:
            key = feature.find('span', class_ = "adPage__content__features__key").text
            value = feature.find('span', class_ = "adPage__content__features__value").text
            product_feature = {str(key): value}
            features.append(product_feature)

        # print(features)

        price_div = soup.find('div', class_ = "adPage__content__footer__wrapper")


        price_span = price_div.find('span', class_ = "adPage__content__price-feature__prices__price__value")
        if price_span.find_next_sibling('span') is not None:
            price = price_span.text + price_div.find('span', class_ = "adPage__content__price-feature__prices__price__currency").text
        else:
            price = price_span.text
        # print(price)

        region_elements_div = price_div.find('dl', class_ = "adPage__content__region grid_18")
        region_elements = region_elements_div.find_all('dd')
        region = ""
        for element in region_elements:
            region = region + element.text.strip()
        # print(region)

        phone_div = soup.find('dl', class_ = "js-phone-number adPage__content__phone is-hidden grid_18")

        if phone_div.find("a") is None:
            phone_no = "None"
        else:
            phone_no = phone_div.find('a').get('href').replace("tel:", "")
            # print(phone_no)

        # get owner and page stats
        stats_div = soup.find('div', class_ = "adPage__aside__stats")
        if stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment has-reviews") is not None:
            owner_url = "https://999.md" + stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment has-reviews").get('href')
            owner_name = stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment has-reviews").text
        elif stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment tooltip tooltipstered") is not None:
            owner_url = "https://999.md" + stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment tooltip tooltipstered").get('href')
            owner_name = stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment tooltip tooltipstered").text
        elif stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment") is not None:
            owner_url = "https://999.md" + stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment").get('href')
            owner_name = stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment").text
        else:
            owner_url = "None"
            owner_name = "None"

        updated = stats_div.find('div', class_ = "adPage__aside__stats__date").text
        type_ad = stats_div.find('div', class_ = "adPage__aside__stats__type").text
        views = stats_div.find('div', class_ = "adPage__aside__stats__views").text


        final_data = {"title": title, "description": description, "features": features, "price": price, "region": region, "phone_no": phone_no, "stats":{ "owner_url": owner_url, "owner_name": owner_name, "updated": updated, "type_ad": type_ad, "views": views} }
        print(final_data)

        try:
            db.insert(final_data)
        except:
            print("Error inserting into db")

    print(f" [x] Received {body.decode()}")
    get_data(url=body.decode(), db=db)
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


    

if __name__ == '__main__':
    main()

import requests
from bs4 import BeautifulSoup
import regex as re
import json

def get_data(urls):
    data = []
    for url in urls:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        title_header = soup.find('header', class_ = "adPage__header")
        title = title_header.find('h1').text
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
        phone_no = phone_div.find('a').get('href').replace("tel:", "")
        # print(phone_no)

        # get owner and page stats
        stats_div = soup.find('div', class_ = "adPage__aside__stats")
        owner_url = "https://999.md" + stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment").get('href')
        owner_name = stats_div.find('a', class_ = "adPage__aside__stats__owner__login buyer_experiment").text

        updated = stats_div.find('div', class_ = "adPage__aside__stats__date").text
        type_ad = stats_div.find('div', class_ = "adPage__aside__stats__type").text
        views = stats_div.find('div', class_ = "adPage__aside__stats__views").text


        final_data = {"title": title, "description": description, "features": features, "price": price, "region": region, "phone_no": phone_no, "stats":{ "owner_url": owner_url, "owner_name": owner_name, "updated": updated, "type_ad": type_ad, "views": views} }
        # print(final_data)

        data.append(final_data)

    return data

# open json file
with open('links.json', "r") as json_file:
    data = json.load(json_file)

urls_to_parse = data["links"][:3]
print(urls_to_parse)

info_items = {"items_info":get_data(urls_to_parse)}
print(info_items)

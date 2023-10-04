import requests
from bs4 import BeautifulSoup
import regex as re
import json

def main():  
    page_parsing_data = {"website_pages":[{"products":[]}, {"pages_content":[]}]}
    url_list = ["http://127.0.0.1:8080/"]
    total_links = ["http://127.0.0.1:8080/"]
    while len(url_list) > 0:
        url = url_list[0]
        del url_list[0]
        url_list, total_links, page_parsing_data = parse_page_links(url, url_list, total_links, page_parsing_data)

    print(page_parsing_data)

    with open("homework_products_export.json", "w") as file:
        json.dump(page_parsing_data["website_pages"][0], file)


def parse_page_links(url, url_list, total_links, page_parsing_data):
    #get page content
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    print(page.content[:20])
    
    #add links to list
    url_list.extend(get_list_links(soup, total_links))
    total_links.extend(get_list_links(soup, total_links))

    new_page_parsing_data = get_content(soup, url, page_parsing_data)

    return url_list, total_links, new_page_parsing_data

def get_content(soup, url, page_parsing_data):
    #get page content
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    if "products/" in url:
        content = soup.find_all("p")
        content_dict = {}
        for cont in content:
            content_dict[cont.get("id")] = cont.get_text()
            page_parsing_data["website_pages"][0]["products"].append(content_dict)
    else:
        content_dict = {}
        content = soup
        content_dict[url] = content
        page_parsing_data["website_pages"][1]["pages_content"].append(content_dict)
    
    return page_parsing_data


def get_list_links(soup, total_links):
    list = []

    links = soup.find_all('a')
    for link in links:
        if ("http://127.0.0.1:8080" + link.get('href')) not in total_links:
            list.append("http://127.0.0.1:8080" + link.get('href'))
    
    print("Found " + str(len(list)) + " links")

    return list

if __name__ == '__main__':
    main()
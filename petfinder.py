from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import random
import time
import pandas as pd
import os
import urllib
import shutil
from os import listdir
from os.path import isfile, join


def get_hrefs(urls):
    """
    The webpage scrapper for list of all dogs. Design for petfinder.com
    param:
        url: the list of links to webpage holding dog's infor
    return:
        hrefs: hrefs for all the dogs.
    """
    hrefs = []

    for url in urls:

        driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for link in soup.find_all("a", {"class": "petCard-link"}):
            href = link.get('href')
            hrefs.append(href)

        driver.close()

    return hrefs


def get_photo(hrefs):
    """
    Input: a list of hrefs for different dogs
    Output: list of titles and list of photo urls for those dogs
    """

    titles = []
    photo_urls = []

    for href in hrefs:

        page = requests.get(href, headers={'User-Agent': "Resistance is futile"})
        soup = BeautifulSoup(page.text, features="lxml")

        try:
            title = soup.title.text
            titles.append(title)
        except:
            titles.append(' ')

        try:
            photo_url = soup.find('meta', {"property": "og:image"})['content']
            photo_urls.append(photo_url)
        except:
            photo_urls.append(' ')

    return titles, photo_urls


def download_image(link, name, web_site, path):
    """
    This function is to build a file folder that contains the downloaded picture.
    param:
       link: the list of image url, for which should only be the url.
       name: the name of the sub-directory.
       web_site: the website’s name.
    return:
       Nothing.
    """
    path += name
    # build a folder
    if os.path.exists(path):
        shutil.rmtree(path)
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    # iterate through all url link
    for i, url in enumerate(link):
        # save the image
        if url == ' ':
            continue
        request = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'})
        img_name = web_site+"_"+str(i)+".jpg"
        with urllib.request.urlopen(request) as response, open(path+"/"+img_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    # return a notice.
    print("Store all images from link.")


if __name__ == "__main__":
    url = 'https://www.petfinder.com/search/dogs-for-adoption/us/ca/san-francisco/'
    urls = [url]
    for i in range(2, 5):
        urls.append(url + f'?page={i}')
    hrefs = get_hrefs(urls)
    titles, photo_urls = get_photo(hrefs)
    df = pd.DataFrame({'links': hrefs, 'titles': titles, 'photo_url': photo_urls})
    df.to_csv('petfinder.csv', index=False)
    photo_urls = df.photo_url.tolist()

    link = photo_urls
    name = 'petfinder_dogs'
    web_site = 'petfinder'
    path = '../dataset/'
    download_image(link, name, web_site, path)


# -*- coding: utf-8 -*-
"""
Created on Sun May  9 17:00:10 2021

@author: Nikko Prayudi
"""

from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
from tqdm import tqdm

class TweetAnalytics:
    def __init__(self, username_input, n_tweets):
        self.username_input = username_input
        self.n_tweets = n_tweets
        
    def get_tweet_data(self, card):
        username = card.find_element_by_xpath('.//span').text
        handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
        try:
            postdate = card.find_element_by_xpath('//time').get_attribute('datetime')
        except NoSuchElementException:
            return

        try:
            img_ = card.find_element_by_xpath('.//div[2]/div[2]/div[1]//img')
            if img_ != None:
                contain_img = True
                contain_vid = False
        except NoSuchElementException:
            contain_img = False
            try:
                vid_ = card.find_element_by_xpath('.//div[2]/div[2]/div[1]//video')
                if vid_ != None:
                    contain_vid = True
            except NoSuchElementException:
                contain_vid = False

        try:
            comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]//span').text
        except NoSuchElementException:
            comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
        responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
        text = f'{comment} {responding}'

        tweet = (username, handle, postdate, text, contain_img, contain_vid)
        return tweet

    def scrape_tweets(self):
        id_to_search = self.username_input
        tweets_to_get = self.n_tweets

        print('[INFO]: Getting things ready...')
        path = "D:\Projects\chromedriver.exe"
        driver = Chrome(path)
        driver.maximize_window()
        sleep(3)

        driver.get(f"https://www.twitter.com/{id_to_search}")
        sleep(5)
        driver.find_element_by_link_text('Tweets').click()
        sleep(5)
        cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')

        last_position = driver.execute_script("return window.pageYOffset;")
        tweet_data = list()
        scrolling = True

        print('[INFO]: Start scrapping tweets...')
        sleep(0.25)
        pbar = tqdm(total=tweets_to_get)
        while scrolling:
            page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
            for card in page_cards:
                tweet = self.get_tweet_data(card)
                tweet_data.append(tweet)
                pbar.update(1)
                if len(tweet_data) == tweets_to_get:
                    scrolling = False
                    pbar.close()
                    break

            scroll_attemp = 0
            while True:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(3)
                curr_position = driver.execute_script("return window.pageYOffset;")
                if last_position == curr_position:
                    scroll_attemp += 1

                    if scroll_attemp >= 3:
                        scrolling = False
                        break
                    else:
                        sleep(3)
                else:
                    last_position = curr_position
                    break

        tweet_df = pd.DataFrame(tweet_data, columns=['ProfileName',
                                     'Username',
                                     'DateTime',
                                     'Tweet',
                                     'ContainImg',
                                     'ContainVid'])
        print('[INFO]: Done.')
        return tweet_df

    def plot_graphs(self, tweet_df):
    #     %matplotlib qt5
        id_to_search = self.username_input
        tweets_to_get = self.n_tweets
        
        colors1 = ['#ff9999','#66b3ff']

        fig = plt.figure(figsize=(8,8))
        fig.suptitle(f"@{id_to_search}'s Simple Tweet Analytics",
                     fontweight='bold',
                     fontsize=13)

        ax1 = fig.add_subplot(2,2,1)
        tweeting_ = len(tweet_df[tweet_df['Username']==f'@{id_to_search}'])
        ax1.pie([tweeting_, tweets_to_get-tweeting_],
                colors=colors1,
                shadow=True, autopct='%1.1f%%')
        ax1.set_title('Tweet vs RT/QRT',
                      fontweight='bold',
                      fontsize=10)
        ax1.legend(labels=['Pure Tweets', 'RTs/QRTs'])

        ax2 = fig.add_subplot(2,2,2)
        rt_freq = tweet_df[tweet_df['Username']!=f'@{id_to_search}'].Username.value_counts()[:10].sort_values()
        ax2.barh(rt_freq.index,
                 width=rt_freq.values)
        ax2.set_title('10 Most Retweeted Accounts',
                      fontweight='bold',
                      fontsize=10)
        ax2.set_xlabel('Frequency')
        ax2.grid(axis='x')

        colors2 = ['cadetblue', 'slateblue']
        ax3 = fig.add_subplot(2,2,3)
        media = tweet_df[(tweet_df.ContainImg==True) | (tweet_df.ContainVid==True)]
        ax3.pie([len(media), tweets_to_get-len(media)],
                colors=colors2,
                shadow=True, autopct='%1.1f%%')
        ax3.set_title('Tweets Contain Media?',
                      fontweight='bold',
                      fontsize=10)
        ax3.legend(labels=['Yup', 'Nope'])

        colors3 = ['sienna', 'powderblue']
        ax4 = fig.add_subplot(2,2,4)
        contImg = media[media.ContainImg==True]
        ax4.pie([len(contImg), len(media)-len(contImg)],
                colors=colors3,
                shadow=True, autopct='%1.1f%%')
        ax4.set_title('What media?',
                      fontweight='bold',
                      fontsize=10)
        ax4.legend(labels=['Pics', 'Vids'])

        plt.tight_layout()
        plt.show()
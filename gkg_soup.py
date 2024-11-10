import os
import re
import pandas as pd
import numpy as np
import requests
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class GKGSoup():
    def __init__(self):
        self.set_gkg_soup()

    def set_gkg_soup(self):
        self.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        self.session = requests.Session()
        retry = Retry(connect=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    # get the soup object
    def get_gkg_soup(self, url, verbose=False):
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
            if verbose:
                print(f'Title: {self.soup.title.get_text()}') # test print of title
        except requests.exceptions.RequestException as e:
                print(f"Error: {e}")

    def get_headers(self, verbose=False):
        self.header_text = []
        for i in range(1,5):
            headers = self.soup.find_all(f'h{i}')
            for h in headers:
                self.header_text.append(h.get_text())
        if verbose:
            print(f'Length of Header List: {len(self.header_text)}'
                  f'\nFirst Header: {self.header_text[0]}'
                  f'\nLast Header: {self.header_text[-1]}')

    # Define start and end markers
    # If the source domain list becomes to long, create a json file to store the bounds and read from it
    def set_text_bounds(self):
        # Set default to None if no bounds match
        self.text_bounds = None
        
        # Define regex pattern for matching specific domains
        pattern = r"(screenrant\.com|gamerant\.com)"
        
        # Use regex to check if URL contains the desired domain
        if re.search(pattern, self.url):
            start_marker = "reached your account maximum for"
            end_marker = "Your changes have been saved"
            self.text_bounds = (start_marker, end_marker)
        else:
            print('No text bounds set for this URL')

    def get_paragraphs(self, verbose=False):
        paragraphs = self.soup.find_all('p')
        # if self.text_bounds is not empty, unpack the start and end markers
        if self.text_bounds:
            sm, em = self.text_bounds
            in_section = False
        else:
            # no bounds set, return all paragraphs
            in_section = True

        self.parsed_paragraphs = []
        # Iterate through each paragraph
        for idx, p in enumerate(paragraphs):
            text = p.get_text(strip=True)  # Extract and strip whitespace around text

            if self.text_bounds:
                # Start capturing paragraphs after the start_marker
                if sm in text:
                    in_section = True
                    continue  # Skip the marker paragraph itself

                # Stop capturing when we hit the end_marker
                if em in text:
                    if in_section:
                        break

            # Append paragraph if within the desired section
            if in_section and len(text) > 0:  # Example length filter
                self.parsed_paragraphs.append(text)

        if verbose:
            print(f'Length of Paragraph List: {len(self.parsed_paragraphs)}'
                  f'\nFirst Paragraph: {self.parsed_paragraphs[0]}'
                  f'\nLast Paragraph: {self.parsed_paragraphs[-1]}')

    def store_article_soup(self, verbose=False):
        url = self.url
        headers = self.header_text
        head_count = len(headers)
        paragraphs = self.parsed_paragraphs
        par_count = len(paragraphs)
        if self.text_bounds:
            text_bounds = True
        else:
            text_bounds = False
        # Create a dictionary to store the data
        data = {'URL': url, 'Headers': headers, 'Header Count': head_count, 'Paragraphs': paragraphs, 'Paragraph Count': par_count, 'Text Bounds': text_bounds}
        # Create a dataframe from the dictionary
        self.article_soup_df = pd.DataFrame([data])


    def parse_gkg_soup(self, url, verbose=False):
        self.url = url
        self.get_gkg_soup(url, verbose=verbose)
        self.set_text_bounds()
        self.get_headers(verbose=verbose)
        self.get_paragraphs(verbose=verbose)
        self.store_article_soup(verbose=verbose)
        print('\n')

if __name__ == '__main__':
    gkgsoup = GKGSoup()
    url = 'https://gamerant.com/one-piece-sun-god-loki-nika-luffy/'
    gkgsoup.parse_gkg_soup(url, verbose=True)
    print(gkgsoup.article_soup_df.T)
import os
import re
import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis
import requests
from datetime import date, datetime, timedelta
import gdelt # for gdelt searchs

from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# GDELT GKG Operator
class gkg_operator:
    def __init__(self):
        self.gdv2 = gdelt.gdelt(version=2) # Instantiate the GDELT object for searches
        self.current_date = date.today().strftime('%Y %b %d')
        self.search_date = [self.current_date]
        self.set_gkg_soup()


    def set_date(self, date):
        """
        date format: 'YYYY MM DD', ex. '2021 Jan 01'
        """
        if isinstance(date, str):
            self.search_date = [date]
        elif isinstance(date, list):
            self.search_date = date
        else:
            print('Invalid date input. Please input a string or list of strings in the format "YYYY MM DD"')


    def get_gkg(self, data=None, coverage=True):
        if data is None:
            self.gkg_query = self.gdv2.Search(date=self.search_date, table='gkg', normcols = True, coverage=coverage)
        else:
            self.gkg_query = data.copy()
        # reset index to avoid issues with indexing
        self.gkg_query.reset_index(drop=True, inplace=True)
        self.parse_urls()

    # takes a list of dates
    # technically could be made to take a list of dates and dateranges
    def get_gkg_dated_list(self, data=None, coverage=True):
        """Must be a list of dates and/or date ranges
        Ex. ['2021 Jan 01', '2021 Jan 02', ['2023 Jan 01', '2023 Jan 03']]
        """
        if isinstance(self.search_date, list):
            if data is None:
                self.gkg_query = pd.DataFrame()
                for date in self.search_date:
                    df = self.gdv2.Search(date=date, table='gkg', normcols = True, coverage=coverage)
                    # add filter options here
                    self.gkg_query = pd.concat([self.gkg_query, df], ignore_index=True)
            else:
                pass

    def gkg_filter(self, column = None, values = None):
        df = self.gkg_query.copy()
        if column is None or values is None:
            print('Please provide a column and values to filter by')
            return
        elif column is not None and isinstance(values, list):
            df.dropna(subset=[column], inplace=True)
            values = '|'.join(values)
            filtered_df = df[df[column].str.contains(values, case=False)]
            filtered_df.reset_index(drop=True, inplace=True)
            self.filtered_df = filtered_df
            return filtered_df
        else:
            print('Please provide a list of values to filter by')
            return

    def parse_urls(self):
        self.urls = self.gkg_query['documentidentifier'].tolist()
        self.parsed_urls = []
        for url in self.urls:
            url = url.replace('https://','').replace('http://','').replace('www.','').split('/')
            # if url is empty string, remove it
            if url[-1] == '':
                url.pop()
            article_title = url[-1]
            article_title = article_title.replace('-',' ')
            article_title = article_title.replace('_',' ')
            url[-1] = article_title
            # keep only first and last element of url
            url = [url[0],url[-1]]
            # print(url)
            self.parsed_urls.append(article_title)

    
    def parse_gkg_field(self, field='amounts'):
        self.parsed_field_name = field
        df = self.gkg_query.copy()
        parsed_rows = []  # Initialize a list to collect each new row
        for idx, row in df.iterrows():
            if pd.isna(row[field]):
                continue
            field_data = row[field].rstrip(';').split(';')
            for f in field_data:
                if field.__contains__('location'):
                    f = f.split('#')
                else:
                    f = f.split(',')
                parsed_rows.append([idx] + f)
        if field == 'v2tone':
            col_names = ['index','Tone','Positive Score', 'Negative Score', 'Polarity',
                          'Activity Reference Density', 'Self/Group Reference Density', 'Word Count']
        else:
            # Dynamically create column names based on length of `f`
            col_names = ['index'] + [f'{field}_{i}' for i in range(len(parsed_rows[0]) - 1)]
        self.parsed_fields_df = pd.DataFrame(parsed_rows, columns=col_names)
        return self.parsed_fields_df
    

    def tokenize_field(self, data=None, col_idx=None):
        if col_idx is None:
            print('Please provide a column index to tokenize')
            return
        if data is None:
            df = self.parsed_fields_df.copy()
        else:
            df = data.copy()
        # tokenize the field
        tokens = df.iloc[:,col_idx].unique()
        field_tokens = list(set(tokens))
        field_tokens.sort()
        self.field_tokens = field_tokens
        return self.field_tokens

    def vectorize_field(self, weight='boolean'):
        df = self.parsed_fields_df.copy()
        
        # Set the column index based on the field name
        col_idx = 2 if self.parsed_field_name == 'amounts' else 1
        
        # Change data type to float where possible and convert the selected column to lowercase
        df = df.apply(pd.to_numeric, errors='ignore')
        df.iloc[:, col_idx] = df.iloc[:, col_idx].astype(str).str.lower()
        
        # Remove non-alphanumeric characters except for whitespace
        df.iloc[:, col_idx] = df.iloc[:, col_idx].str.replace(r'[^a-z0-9\s]', '', regex=True)
        
        # Tokenize the field
        self.tokenize_field(data=df, col_idx=col_idx)
        
        # Initialize an empty DataFrame for the vectorized data
        rows = self.gkg_query.shape[0]
        vectorized_df = pd.DataFrame(np.zeros((rows, len(self.field_tokens))), columns=self.field_tokens)
        
        # Add tokens to a new 'token' column and group by index and token
        df['token'] = df.iloc[:, col_idx]
        counted_tokens = df.groupby(['index', 'token']).size().unstack(fill_value=0)
        
        # Align counted tokens with vectorized_df
        aligned_tokens = vectorized_df.reindex(counted_tokens.index).fillna(0) + counted_tokens.reindex_like(vectorized_df).fillna(0)
        
        if weight == 'weighted':
            # Apply weighted transformation (e.g., TF-IDF, normalization, or another weighting method)
            # For illustration, assume each token count is multiplied by a custom weight function `get_weight`
            def get_weight(token_count):
                # Define a weighting mechanism (this is a placeholder)
                return np.log1p(token_count)  # Example: log scaling as a simple weighting

            aligned_tokens = aligned_tokens.applymap(get_weight)  # Apply weighting function to each token count
        
        # Update or replace vectorized_df with aligned_tokens
        vectorized_df.update(aligned_tokens)
        self.vectorized_df = vectorized_df

    def get_fields_stats(self, weight='boolean'):
        # Ensure vectorized data exists
        if self.vectorized_df is None:
            self.vectorize_field(weight=weight)
        
        # Calculate non-zero float percentages
        non_zero = (self.vectorized_df.astype(bool).sum(axis=0) / self.vectorized_df.shape[0]) * 100
        non_zero = non_zero[non_zero > 0]
        non_zero.sort_values(ascending=False, inplace=True)
        non_zero_top_10 = non_zero[:10]
        
        # Initialize additional stats
        mean_weighted_top_10 = None
        mean_weighted_all_top_10 = None
        
        if weight == 'weighted':
            # Mean across non-zero values
            mean_weighted_values = self.vectorized_df[self.vectorized_df != 0].mean()
            mean_weighted_values = mean_weighted_values[mean_weighted_values > 0]
            mean_weighted_values.sort_values(ascending=False, inplace=True)
            mean_weighted_top_10 = mean_weighted_values[:10]

            # Mean across all values (including zeros)
            mean_weighted_all = self.vectorized_df.mean()
            mean_weighted_all = mean_weighted_all[mean_weighted_all > 0]
            mean_weighted_all.sort_values(ascending=False, inplace=True)
            mean_weighted_all_top_10 = mean_weighted_all[:10]
        
        # Print results
        print("    Top 10 Tokens by Non-Zero Percentage")
        print(non_zero_top_10.to_frame(name="Non-Zero Percentage"))
        
        if mean_weighted_top_10 is not None:
            print("\nTop 10 Tokens by Mean Weighted Value (Non-Zero Only)")
            print(mean_weighted_top_10.to_frame(name="Mean Weighted Value (Non-Zero)"))
        
        if mean_weighted_all_top_10 is not None:
            print("\nTop 10 Tokens by Mean Weighted Value (Including Zeros)")
            print(mean_weighted_all_top_10.to_frame(name="Mean Weighted Value (All)"))


    def calculate_token_stats(self, weight='boolean'):
        if self.vectorized_df is None:
            print('Please vectorize the field before calculating token statistics')
            return
        
        vectorized_df = self.vectorized_df.copy()
        
        # Token frequency (total count)
        token_frequency = vectorized_df.sum(axis=0)
        
        # Non-zero percentage (sparsity complement)
        token_non_zero_percentage = (vectorized_df.astype(bool).sum(axis=0) / vectorized_df.shape[0]) * 100
        
        # Variance and standard deviation
        token_variance = vectorized_df.var(axis=0)
        token_std_dev = vectorized_df.std(axis=0)
        
        # Maximum and minimum token weight
        token_max = vectorized_df.max(axis=0)
        token_min = vectorized_df.min(axis=0)
        
        # Inverse Document Frequency (IDF)
        N = vectorized_df.shape[0]
        document_frequency = vectorized_df.astype(bool).sum(axis=0)
        token_idf = np.log(N / (document_frequency + 1))
        
        # Skewness and Kurtosis
        token_skewness = vectorized_df.apply(skew, axis=0)
        token_kurtosis = vectorized_df.apply(kurtosis, axis=0)
        
        # Mean Weighted Value (Non-Zero Only)
        if weight == 'weighted':
            mean_weighted_values = vectorized_df[vectorized_df != 0].mean(axis=0)
            mean_weighted_all = vectorized_df.mean(axis=0)
        else:
            mean_weighted_values = pd.Series([np.nan] * vectorized_df.shape[1], index=vectorized_df.columns)
            mean_weighted_all = pd.Series([np.nan] * vectorized_df.shape[1], index=vectorized_df.columns)
        
        # Combine all stats into a single DataFrame
        token_stats_df = pd.DataFrame({
            'Frequency': token_frequency,
            'NonZeroPercentage': token_non_zero_percentage,
            'Variance': token_variance,
            'StdDev': token_std_dev,
            'MaxWeight': token_max,
            # 'MinWeight': token_min,
            'IDF': token_idf,
            # 'Skewness': token_skewness,
            # 'Kurtosis': token_kurtosis,
            'MeanWeightedNonZero': mean_weighted_values,
            'MeanWeightedAll': mean_weighted_all,
        })
        
        # Sort by frequency for convenience
        token_stats_df.sort_values(by='Frequency', ascending=False, inplace=True)
        self.token_stats = token_stats_df
        # return token_stats_df


    #####################################
    # Beautiful Soup Functions
    #####################################
    # initialized upon class instantiation
    def set_gkg_soup(self):
        self.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        self.session = requests.Session()
        retry = Retry(connect=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
                
    # get the soup object with a timeout
    def get_gkg_soup(self, url, verbose=False, timeout=10):
        try:
            response = self.session.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
            if verbose:
                print(f'Title: {self.soup.title.get_text()}')  # test print of title
        except requests.exceptions.Timeout:
            print("Request timed out.")
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
            print(f'No text bounds set for this URL: {self.url}')


    def get_paragraphs(self, verbose=False):
        paragraphs = self.soup.find_all('p')
        # if self.text_bounds is not empty, unpack the start and end markers
        if self.text_bounds:
            sm, em = self.text_bounds # start and end markers
            in_section = False
        else:
            # no bounds set, return all paragraphs
            in_section = True
        self.parsed_paragraphs = []
        # in_section = False
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
            

    def parse_gkg_soup(self, url, verbose=False):
        self.url = url
        self.get_gkg_soup(url, verbose=verbose)
        self.set_text_bounds()
        self.get_headers(verbose=verbose)
        self.get_paragraphs(verbose=verbose)
        if verbose:
            print('\n')

    def get_title(self, url, verbose=False):
        self.url = url
        self.get_gkg_soup(url, verbose=verbose)
        self.title = self.soup.title.get_text()
        if verbose:
            print(self.title)
        return self.title
        
    def get_all_soup(self, limit_output=5, verbose=False):
        """
        Note: This function will parse the soup for all urls in self.urls, which can be a large number.
            For testing purposes, limit_output can be set to a smaller number. For all urls, use limit_output='all'.
        limit_output: int, default 5, for all, use 'all' - limits the number of urls to parse
        verbose: bool, default False - prints the parsed data    
        """
        self.all_soup_data = pd.DataFrame()
        if limit_output == 'all':
            limit_output = len(self.urls)
        for url in self.urls[:limit_output]:
            if verbose:
                print(self.urls.index(url))
            self.parse_gkg_soup(url, verbose=verbose)
            # at this stage, all of the parsed data can be stored in a dataframe
            self.article_soup = {
                'URL': self.url,
                'Parsed URL': self.parsed_urls[self.urls.index(url)],
                'Titles': self.soup.title.get_text(),
                'Headers': self.header_text,
                'Paragraphs': self.parsed_paragraphs
            }
            # add dictionary as row to all_soup_data using concat
            self.all_soup_data = pd.concat([self.all_soup_data, pd.DataFrame([self.article_soup])], ignore_index=True)
        # We can merge the all_soup_data with the gkg_query data to have a complete dataset.
        # we can merge on url, or add the record id to the all_soup_data and merge on that.
        # Additionally, we can merge the vectorized_df with the all_soup_data to have a complete dataset.
        # We should expect the stored data to be quite large if we choose to store all parsed field data.


# run file
if __name__ == '__main__':
    print('Running gkg_tools.py')
    gkg = gkg_operator()
    # print all functions in the class
    print('All objects in class gkg_operator:\n ')
    print([f for f in dir(gkg) if not f.startswith('__')])
    OP = pd.read_csv('OP.csv') # We could alternatively use the subset of the queried data in the last section.
    gkg.get_gkg(data=OP) # stores in gkg.gkg_query as a dataframe
    gkg.parse_gkg_field(field='v2persons') # stores in gkg.parsed_fields_df as a dataframe
    gkg.tokenize_field(col_idx=1) # stores in gkg.field_tokens as a list
    print(f'Tokens as Parsed: {gkg.field_tokens[:5]}') # print the first 5 tokens as parsed
    gkg.vectorize_field() # stores in gkg.vectorized_df as a dataframe
    print(f'Tokens as Columns: {gkg.field_tokens[:5]}') # print the first 5 tokens as column names
    gkg.get_all_soup(limit_output=3, verbose=True) # stores in gkg.urls as a list of urls
    print(gkg.all_soup_data.info())
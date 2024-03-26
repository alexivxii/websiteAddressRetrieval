# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#pip install pyarrow for parquet file read, version
#Successfully installed numpy-1.26.4 pyarrow-15.0.2


import pyarrow.parquet as pq
import pandas
import requests
from bs4 import BeautifulSoup
import re

# Function to find and print all addresses in a string
def print_addresses(text):
    # Regular expression pattern to match addresses
    address_pattern = re.compile(r'\b\d{1,5}\s\w+\s\w+\b')
    addresses = address_pattern.findall(text)
    if addresses:
        print("Addresses found:")
        for address in addresses:
            print("-", address)

# Function to scrape a webpage and check for addresses
def check_website_for_address(url):
    # Fetch the webpage
    response = requests.get(url)
    if response.status_code == 200:
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from HTML
        text = soup.get_text()
        # Check if the text contains an address
        if contains_address(text):
            print("Address found on the webpage:", url)
            print_addresses(text)
        else:
            print("No address found on the webpage:", url)
    else:
        print("Failed to fetch webpage:", url)

# Function to check if a string contains an address pattern
def contains_address(text):
    # Regular expression pattern to match addresses
    address_pattern = re.compile(r'\b\d{1,5}\s\w+\s\w+\b')
    return bool(address_pattern.search(text))

def readParquetFile(file_path):
    # Open the Parquet file
    parquet_file = pq.ParquetFile(file_path)

    # Get the metadata of the Parquet file
    metadata = parquet_file.metadata

    # Get the number of rows from the metadata
    num_rows = metadata.num_rows

    # Get the number of columns from the metadata
    num_columns = len(metadata.schema.names)

    print("Number of rows:", num_rows)
    print("Number of columns:", num_columns)

    # Read the Parquet file into a pandas DataFrame
    #pip install pandas
    #not necesarrily needed to be imported
    df = parquet_file.read().to_pandas()

    # Now you can work with the DataFrame as usual
    print(df.head())

    print(df.at[0,"domain"])


if __name__ == '__main__':

    # Specify the path to your Parquet file
    file_path = "list of company websites.snappy.parquet"

    readParquetFile(file_path)

    check_website_for_address("https://www.umbrawindowtinting.com/")
    check_website_for_address("https://about.google/contact-google/")
    check_website_for_address("https://about.google/locations/?region=north-america")






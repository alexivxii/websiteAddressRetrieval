# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# pip install pyarrow for parquet file read, version
# Successfully installed numpy-1.26.4 pyarrow-15.0.2


import pyarrow.parquet as pq
import pandas
import requests
from bs4 import BeautifulSoup
import re

addressPatterns = [
    re.compile(r'\b\d{1,5}\s\w+\s\w+\b'),
    # for the google about pattern "https://about.google/contact-google/"
    re.compile(r'\b\d{1,5}\s\w+\s\w+\b.*\b[A-Za-z]{2}\s\d{5}(?:-\d{4})?\b'),

]

addressPatternMap = {
    "USA": re.compile(r'\b\d{1,5}\s\w+\s\w+\b.*\b[A-Za-z]{2}\s\d{5}(?:-\d{4})?\b'),

    "USA2": re.compile(r'\b(?:[A-Z][a-z]+\s*)+,\s*[A-Z][a-z]+\s*,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?,\s*[A-Z][a-z]+\b'),
    "France": re.compile(r'\b(?:[A-Z][a-z]+\s*)+,.*?,\s*\d{5}\s*[A-Z][a-z]+\b'),
    "UK": re.compile(r'\b(?:[A-Z][a-z]+\s*)+:.*?,\s*[A-Z][a-z]+\s*,\s*[A-Z][a-z]+\b'),
    # "Japan": re.compile(r'\b\d{1,5}\s\w+\s\w+\b.*\b[A-Za-z]{2}\s\d{5}(?:-\d{4})?\b'),
    "Columbia": re.compile(r'\b\d{1,5}\s\w+\s\w+\b.*\b[A-Za-z]{2}\s\d{5}(?:-\d{4})?\b'),
    "USAforum": re.compile(r'^(\d+) ?([A-Za-z](?= ))? (.*?) ([^ ]+?) ?((?<= )APT)? ?((?<= )\d*)?$'),
    # "Romania": re.compile(r'\bStr\.\s+[A-Z][a-z]+\s+\d+(?:[\s,-]+\w+)?(?:,\s+et\.\s*\d+)?(?:,\s+apt\.\s*\d+)?(?:,\s*[1-6])?,?\s+\d{6}\s+[A-Z]+(?:,\s+[A-Z][a-z]+)?\b'),


}


# Function to scrape a webpage and check for addresses
def check_website_for_address(url):
    # Fetch the webpage
    response = requests.get(url)
    if response.status_code == 200:
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from HTML and join lines into one
        text = " ".join(line.strip() for line in soup.stripped_strings)
        # Check for address patterns and print addresses if found
        print_addresses(text)
    else:
        print("Failed to fetch webpage:", url)


# Function to find and print all addresses in a string
def print_addresses(text):
    addresses_found = False
    for pattern in addressPatternMap:
        print(pattern) #key
        addresses = addressPatternMap[pattern].findall(text)
        if addresses:
            addresses_found = True
            print("Addresses found:")
            for address in addresses:
                print("-", address)
    if not addresses_found:
        print("No address found.")


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
    # pip install pandas
    # not necesarrily needed to be imported
    df = parquet_file.read().to_pandas()

    # Now you can work with the DataFrame as usual
    print(df.head())

    print(df.at[0, "domain"])


if __name__ == '__main__':
    # Specify the path to your Parquet file
    file_path = "list of company websites.snappy.parquet"

    readParquetFile(file_path)

    # check_website_for_address("https://www.umbrawindowtinting.com/")
    check_website_for_address("https://about.google/contact-google/")
    # check_website_for_address("https://about.google/locations/?region=north-america")
    # check_website_for_address("https://carrefour.ro/corporate/magazine?p=3")

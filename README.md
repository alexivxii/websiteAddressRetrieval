# Veridion Assignment Documentation

---
### Challenge #1

Write a program that extracts all the valid addresses that are found on a list of company websites. The format in which you will have to extract this data is the following: country, region, city, postcode, road, and road numbers. 

---

Questions I asked myself:

* How does the input look like?
* How do i extract text from website?
* How does the addresses look like? Are there differences?
* How do i test my code?
* What happens if there are no addresses/the website doesnt have text/the website is not valid?
* How do i know which address format pattern to use?

## My Approach

### 1. Analyze the input

Input consists of a parquet file with multiple rows and two columns, first column being the index and the second column being the website domains.

Example of the first 5 rows from the parquet file:

    domain
    0  umbrawindowtinting.com
    1          embcmonroe.org
    2         caffeygroup.com
    3          sk4designs.com
    4      draftingdesign.com

### 2. Research address formats

Next I looked online to find out address formats for different countries and special cases.
The following countries have unique address formats:

USA & CANADA
UK  
JAPAN  
COLOMBIA  
FRANCE  
REST OF THE WORLD  

France and Rest of the world have common address formats and can be treated as one.

To identify addresses inside text, i used regex patterns for each country stored in `addressPatternMap`. Key is country website domain and value is the regex pattern.

For every use case I found Websites & looked up on Google examples of addresses for testing.  
Inside the code can be found functions like the ones below, used for testing:

`testMyWebsites(testWebsite)` - called in main  
`printJapanAddress()`  
`printUKAddress()`  
`printColombiaAddress()`

### 3. App flow

Steps for how the app functions (after a lot of testing and trial & error):

1. Read and extract data from the parquet file stored in the environment


2. For every item in the pq file check if the domain is valid.  

First, some websites do not have the protocol and subdomain so we have to check and add them if needed.  
Use `checkValidDomain(domain)`. Inside this function I use whois package which checks if a website domain is valid.  

3. Check if the website has text and store it inside `websiteText` variable

Function `checkWebsiteForText(url)` is used and works like this:

* tries to connect to the website using `requests` package
* using `BeautifulSoup` package i extract the html inside the website. After that, i join all the lines together and remove endlines & replace them with whitespace. The reason is that the regex pattern need one long line of text to correctly identify address patterns.
* if an error occurs, the exception will be printed and return blank string
    
4. If current website has text, we need to apply regex patterns.

In order to use the correct pattern, I need to know the country of the website (for better narrowing of correct address pattern).  
I use function `getWebsiteDomainExtension(domain)` to extract the domain of the url using a regex pattern and return it.  
If the domain function is inside the special cases below, we use the corresponding regex.
`specialCases = ["COM", "JP", "UK", "CO", "GOOGLE", "CA", "NET", "IO"]` - where COM, CA, NET, IO have the same pattern for USA address format.  
Otherwise, we use address format for France.

Using `printAddresses(text,domainExtension)` I apply the pattern and print addresses in console. If no address can be found inside our text, a message is printed in console.

### 4. Python requirements

Modules installed in my environment and versions

    beautifulsoup4     4.12.3
    certifi            2024.2.2
    charset-normalizer 3.3.2
    idna               3.6
    numpy              1.26.4
    pandas             2.2.1
    pip                22.3.1
    pyarrow            15.0.2
    python-dateutil    2.9.0.post0
    python-whois       0.9.3
    pytz               2024.1
    requests           2.31.0
    setuptools         65.5.1
    six                1.16.0
    soupsieve          2.5
    tzdata             2024.1
    urllib3            2.2.1
    wheel              0.38.4

Modules imported

    import pyarrow.parquet as pq
    import pandas
    import requests
    from bs4 import BeautifulSoup
    import re
    import whois

### 5. Bibliography

https://about.google/contact-google/

https://www.geeksforgeeks.org/python-regex-re-search-vs-re-findall/

https://about.google/locations/?region=north-america

https://community.alteryx.com/t5/Alteryx-Designer-Desktop-Discussions/RegEx-Addresses-different-formats-and-headaches/td-p/360147

https://www.campussims.com/how-to-write-a-us-address/#:~:text=The%20recipient's%20first%20and%20last,state%2C%20but%20not%20zip%20code)

https://www.geopostcodes.com/blog/international-address-data/

https://www.geoapify.com/address-formats-by-country-json

https://stackoverflow.com/questions/37745801/how-can-i-extract-address-from-raw-text-using-nltk-in-python

https://pypi.org/project/pyap/

https://devnet.superoffice.com/en/company/learn/address-formats.html

https://www.linkedin.com/pulse/address-cleansing-fuzzy-matching-levenshtein-distance-akhil/

https://pypi.org/project/pycountry/

https://www.sljfaq.org/afaq/addresses.html#:~:text=Writing%20the%20address%20in%20Japanese&text=150%2D2345%20Tokyo%2Dto%2C,7%22%20is%20the%20building%20number.

https://www.kapital.jp/shop/search.html

https://www.starbucksreserve.com/locations/tokyo-roastery

https://pyshark.com/get-domain-name-information-using-python/

https://www.rexegg.com/regex-quickstart.html

https://londoninreallife.com/living-in-london/london-postcode/
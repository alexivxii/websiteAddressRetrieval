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
import whois

addressPatternMap = {

    #USA and rest of the world

    #example address: 2300 Traverwood Dr. Ann Arbor, MI 48105
    "RESTWORLD": re.compile(r'\b\d+\s+[a-zA-Z0-9\s.,]+?,\s+[a-zA-Z]{2}\s+\d{5,9}\b'),

    #/////////////////////////////////////////////////

    #FRANCE

    #Todo: still needs testing
    "FR": re.compile(r'\b(?:[A-Z][a-z]+\s*)+,.*?,\s*\d{5}\s*[A-Z][a-z]+\b'),

    #/////////////////////////////////////////////////

    #UK

    #Todo: still needs testing
    #https://londoninreallife.com/living-in-london/london-postcode/
    #https://www.visitnorthwest.com/liverpool/addresses-postcodes/

    "UK": re.compile(r'\b\d{1,3}\s+[a-zA-Z0-9/\-.]*\s+[a-zA-Z0-9]{1,4}\b\s*[a-zA-Z0-9,]{1,5}\s*\w+\b'),

    #/////////////////////////////////////////////////

    #JAPAN

    #has prefecture in front
    #\b for word
    #(?:東京都|大阪府|福岡県|札幌市|横浜市): This non-capturing group matches any of the specified prefecture names.
    #\s: Matches a whitespace character after the prefecture name.
    #\d+: Matches one or more digits.
    #[A-Z\d-]*: Matches zero or more uppercase letters, digits, or hyphens. This part allows matching apartment or floor numbers like "1F" or "5-6".
    #[\s,-]+: Matches one or more whitespace characters, commas, or hyphens. This allows handling variations in the address format where spaces, commas, or hyphens are used as separators.
    #(?:[A-Za-z]+[\s,-]+)+: Non-capturing group that matches one or more occurrences of a word (one or more alphabetic characters) followed by one or more whitespace characters, commas, or hyphens. This part matches street names or districts.
    #\d{3}-\d{4}: Matches a four-digit postal code separated by a hyphen.
    "JP": re.compile(r'\b(?:東京都|大阪府|福岡県|札幌市|横浜市)?\s*\d+[A-Z\d-]*[\s,-]+(?:[A-Za-z]+[\s,-]+)+\b(?:[A-Za-z]+\s)?\d{3}-\d{4}\b'),

    #for JP without the prefecture in front re.compile(r'\b\d+[A-Z\d-]*[\s,-]+(?:[A-Za-z]+[\s,-]+)+\d{3}-\d{4}\b'),

    #/////////////////////////////////////////////////

    #COLOMBIA

    #"CO": re.compile(r'\b(?:Carrera|Calle)\s+\d{1,3}[a-zA-Z]*\s+#?\d{1,3}\s*-\s*\d{1,3}\s*,*[a-zA-Z0-9\s#áéíóúÁÉÍÓÚ\-]+,[a-zA-Z0-9\s#áéíóúÁÉÍÓÚ\-]\b'),
    "CO": re.compile(r'\b\s*[a-zA-Z0-9áéíóúÁÉÍÓÚ.]*\s+\d{1,3}[a-zA-Z]*\s+#?\d{1,3}\s*-\s*\d{1,3}\s*,*[a-zA-Z0-9\s#áéíóúÁÉÍÓÚ\-]+,[a-zA-Z0-9\s#áéíóúÁÉÍÓÚ\-]\b'),

}


japanAddressList = [

#addresses of some stores in japan
"1-7-2 Minami Nijo Nishi, Chuo-ku, Sapporo 060-0062",
"1F Gaiya Ebisu Building, 2-20-2 Ebisu Minami, Shibuya-ku, 150-0022",
"352 Iseyamachi, Rokkaku-shita, Miyukimachi-dori, Nakagyo-ku, Kyoto 604-8066",
"5F Hankyu Men's Osaka 7-10 Kakuda-cho, Kita-ku, Osaka 530-0017",
"3672-10 Kojima Ogawacho, Kurashiki 711-0912",

"札幌市    7-10 Kakuda-cho, Kita-ku, Osaka 530-0017",

#List of japanese stations addresses of Tokyo, Kyoto and Osaka for testing japan regex
"4-chōme-2-8 Shibakōen, Minato City, Tokyo 105-0011, Japan",

"Higashishiokoji Kamadonocho, Shimogyo Ward, Kyoto, Japan",

"2-chōme-19-23 Aobadai Meguro City, Tokyo 153-0042, Japan",
]

colombiaAddressList = [
    #from some commercial centres in bogota
    "Av. Boyacá #12b-18, Bogotá, Colombia",
    "Av. Boyacá #80-94, Bogotá, Colombia",
    "Cl. 94 #11-65, Bogotá, Colombia",
    "Ac. 26 #62-47, Bogotá, Colombia",
    "Cra. 71d #6-94, Bogotá, Colombia",

    #from chatgpt
    "Carrera 7 #32-67, Bogotá, Cundinamarca",
    "Calle 93 #13-33, Medellín, Antioquia",
    "Carrera 5 #8-23, Barranquilla, Atlántico",
    "Calle 10 #12-45, Cali, Valle del Cauca",
    "Carrera 15 #20-10, Bucaramanga, Santander",
]

ukAddressList = [

    #five guys london addresses
    #https://restaurants.fiveguys.co.uk/greater-london

    "Baker Street. 194 Baker Street NW1 5RT London",
    "Bond Street. 92 Wigmore Steet W1U 3RE London",
    "Brent Cross Deliveroo Editions.Deliveroo Editions, Unit 2 NW2 7LN London",
    "Brixton. 2 Electric Lane SW9 8FA Brixton",
    "Camden. 32 Parkway NW1 7AH London",
    "Canary Wharf.Units 22 / 23 E14 5NY London",
]

# Function to scrape a webpage and check for addresses
#if response status code is 200 successful, we return the text inside the html
#else we return ""
def checkWebsiteForText(url):
    # Fetch the webpage
    response = requests.get(url)
    if response.status_code == 200:
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from HTML and join lines into one, separated by whitespace
        text = " ".join(line.strip() for line in soup.stripped_strings)

        #remove endlines and replace with whitespace
        text = re.sub(r'\n', ' ', text)

        print("Website has text")
        return text
    else:
        print("Failed to fetch webpage:", url)
        return ""


# Function to find and print all addresses in a string
def printAddresses(text,domainExtension):
    addressesFound = False

    pattern = addressPatternMap[domainExtension]

    addresses = pattern.findall(text)
    if addresses:
        addressesFound = True
        print("Addresses found:")
        for address in addresses:
            print("-", address)

    if addressesFound is False:
        print("No address found.")

def printJapanAddress():
    for address in japanAddressList:
        printAddresses(address, "JP")

def printColombiaAddress():
    for address in colombiaAddressList:
        printAddresses(address, "CO")

def printUKAddress():
    for address in ukAddressList:
        printAddresses(address, "UK")

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

    #print(df.at[0, "domain"])

    return df

def checkValidDomain(domain):
    try:
        domain_info = whois.whois(domain)
        print("Domain Valid")
        return True
    except:
        print("Domain Not Valid")
        return False

# if the website is valid and registered on the web, then the extension is also a valid one
def getWebsiteDomainExtension(domain):
    # Regular expression pattern to match the domain extension (. followed by at least two characters and followd by /|\?|$)
    #tested on
    # text1 = "www.website.com"
    # text2 = "www.website.ro?about.html"
    # text3 = "www.curs.pub.ro/about.html"
    # if website is https://about.google/contact-google/, the domain extension is google, but we can still continue
    domain_extension_pattern = r'\.([a-zA-Z]{2,})(?=/|\?|$)'
    match = re.search(domain_extension_pattern, domain)
    if match:
        return match.group(1)
    else:
        return None


if __name__ == '__main__':
    # Specify the path to your Parquet file
    file_path = "list of company websites.snappy.parquet"

    pqData = readParquetFile(file_path)

    #check if we have data in parquet file
    if pqData is not None:
        #Todo: replace testWebsite with for each website in pq file

        #testWebsite = pqData.at[0, "domain"]
        testWebsite = "https://restaurants.fiveguys.co.uk/greater-london"

        #check if the website domain is valid
        if checkValidDomain(testWebsite):

            #get text inside website
            websiteText = checkWebsiteForText(testWebsite)

            #check if the website has text inside
            if websiteText != "":

                #get website domain extension
                domainExtension = getWebsiteDomainExtension(testWebsite)
                print("Domain = " + domainExtension)

                domainExtension = domainExtension.upper()

                specialCases = ["FR", "JP", "UK", "CO"]

                if domainExtension not in specialCases:
                    domainExtension = "RESTWORLD"

                # io, net, com websites are usually used for USA websites
                # rest of the world usually uses same address format as USA, so we can cover most address formats
                # apply correct regex pattern for address matching

                print(websiteText)

                #printAddresses(websiteText, domainExtension)
                printAddresses(websiteText, "UK")

    #Test websites
    #"https://www.umbrawindowtinting.com/"
    #"https://about.google/contact-google/"
    #for this website for google locations, beautifulsoup gives a list of all locations and then the locations grouped, thats how the html is made for the website, so some addresses might appear twice
    #"https://about.google/locations/?region=north-america"
    #"https://carrefour.ro/corporate/magazine?p=3"
    #https://www.elespectador.com/
    #https: // restaurants.fiveguys.co.uk / greater - london

    #Test addresses
    #printJapanAddress()
    #printColombiaAddress()
    #printUKAddress()



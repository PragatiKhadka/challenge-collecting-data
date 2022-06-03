from bs4 import BeautifulSoup
from collections.abc import MutableMapping
from concurrent.futures import ThreadPoolExecutor 
from json import loads
import pandas as pd
import requests
import re
import time


def attr_from_table(table, attrs, attr_dict):
    """
    This function will extract only the attributes provided as input to it.
    It returns a dictionary with header and it's corresponding value.
    """
    for row in table:
        for attr in attrs:
            if row.find("th").contents[0].strip() == attr:
                header = "_".join(row.find("th").contents[0].split())
                value = row.find("td").contents[0].strip()
                attr_dict[f'{header}'] = value
                
    return attr_dict    

def get_attr_table(soup):
    """
    This function will specify some attributes to extract from the tabular data
    namely General and Interior tables.
    It will also call other function which will actually extract the data.
    """
    add_attr = {}
    tables = soup.find_all("tbody")
    general_table = tables[0].find_all("tr")
    gen_attr = ['Number of frontages']
    add_attr = attr_from_table(general_table, gen_attr, add_attr)
    
    interior_table = tables[1].find_all("tr")
    int_attr = ['Living area', 'Furnished']
    add_attr = attr_from_table(interior_table, int_attr, add_attr)
    
    return add_attr

def flatten_dict(d: MutableMapping, sep: str= '_') -> MutableMapping:
    """
    This function flatten the given json data which contains embedded dictionary into a single dictionary
    """
    [flat_dict] = pd.json_normalize(d, sep=sep).to_dict(orient='records')
    return flat_dict

def get_data_script(url):
    """
    Funtion to scrape the data from the given url using beautiful soup.
    Most of the attributes are extracted from the javascript in the page source.
    Some of the attributes are extracted from the tabular data.
    These two are later merged into one dictionary which is converted into a dataframe 
    and finally written to a csv file.
    
    """
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
     }

    response = requests.get(url, headers=headers)
  
    soup = BeautifulSoup(response.content, 'html.parser')
    
    script_text = soup.find("script", text=re.compile("window.dataLayer")).text.split("= ", 1)[1]
    
    #extract only the required text from the javascript and convert to json
    json_data = loads(script_text[:script_text.find(";")])[0]['classified'] 
    data = flatten_dict(json_data)
    data_frm_table = get_attr_table(soup) # get some attribute values from the tables in the page
    con_data = data | data_frm_table      # combine two dictionaries to get all info in one dictionary
    con_data['url'] = url                 # add url in the dictionary
    
    return con_data 

def read_file(filename, num):
    """
    Open the file with all the links and read only the given number of lines 
    """
    with open(filename) as file:
        urls = [next(file) for x in range(num)]    

    return urls

def scrape_data():
    info_dict = []
    file = 'all_links.txt'
    n = 100
    urls = read_file(file, n)

    for url in urls:
        info = get_data_script(url)       
        info_dict.append(info)

    return info_dict    


def main():
    data_dict = scrape_data() 
    # file = 'all_links.txt'
    # n = 100
    # with ThreadPoolExecutor() as pool: 
    #     urls = pool.map(read_file,)
    #     print(urls)

    df = pd.DataFrame(data_dict)  
    df.to_csv('housing_data_test1', index=False)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Program execution time was: %s seconds ---" % (time.time() - start_time))
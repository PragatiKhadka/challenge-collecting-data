from bs4 import BeautifulSoup
from collections.abc import MutableMapping
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
    print("attr_from_table")
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
    print("get_attr_table")
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
    print("get_data_script")
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
     }
    response = requests.get(url, headers=headers)
    print("test1")
    soup = BeautifulSoup(response.content, 'html.parser')
    print("test2")
    script_text = soup.find("script", text=re.compile("window.dataLayer")).text.split("= ", 1)[1]
    
    #extract only the required text from the javascript and convert to json
    json_data = loads(script_text[:script_text.find(";")])[0]['classified'] 
    data = flatten_dict(json_data)
    data_frm_table = get_attr_table(soup) # get some attribute values from the tables in the page
    con_data = data | data_frm_table      # combine two dictionaries to get all info in one dictionary
    con_data['url'] = url                 # add url in the dictionary
    print("end of scrape")

    return con_data 

def read_file(filename, num):
    """
    Open the file with all the links and read only the given number of lines 
    """
    with open(filename) as file:
        urls = [next(file) for _ in range(num)]    

    return urls

def scrape_data():
    info_dict = []
    file = 'all_links.txt'
    n = 10000
    urls = read_file(file, n)
    count = 0

    for url in urls:
        count += 1
        print("counter: ", count)
        info = get_data_script(url)       
        info_dict.append(info)

    return info_dict    

def data_cleaning():
    filepath = 'housing_data_100.csv'
    df = pd.read_csv(filepath, na_values=' ')

    df.drop(columns=['transactionType', 'visualisationOption', 'atticExists','energy_heatingType', 'certificates_primaryEnergyConsumptionLevel',
                  'specificities_SME_office_exists', 'parking_parkingSpaceCount_indoor', 'parking_parkingSpaceCount_outdoor',
                ], inplace=True)
                # renaming the columns
    df.rename(columns = {'basementExists':'has_basement',
                      'price': 'price(€)',
                     'building_constructionYear': 'construction_year',
                     'wellnessEquipment_hasSwimmingPool': 'has_swimmingpool',
                     'Furnished': 'is_furnished', 'outdoor_terrace_exists': 'has_terrace',
                     'Living_area': 'living_area(m²)',
                     'land_surface': 'land_surface(m²)',
                     'outdoor_garden_surface': 'outdoor_garden_surface(m²)',
                     'condition_isNewlyBuilt': 'is_newly_built',
                     'Number_of_frontages': 'number_of_facade'
                    }, inplace = True)

    # rearranging the columns
    df[['id', 'type', 'subtype', 'price(€)', 'zip','construction_year', 'building_condition',
       'is_newly_built', 'number_of_facade', 'living_area(m²)', 'is_furnished', 
       'kitchen_type','bedroom_count', 'land_surface(m²)', 'outdoor_garden_surface(m²)',
       'has_terrace', 'has_swimmingpool', 'has_basement', 'url']] 
                     
def main():
    """
    This function will call the function that does the scraping of the data.
    It will recieve a dictionary of data, then it will be converted to a dataframe.
    The final output will be a csv file with all the scraped data.

    """
    data_dict = scrape_data() 
    df = pd.DataFrame(data_dict)  
    df.to_csv('housing_data_th', index=False)
    
    #clean the data
    data_cleaning()

    
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Program execution time was: %s seconds ---" % (time.time() - start_time))
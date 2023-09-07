# Data Collection Project
The project is based on web scraping in Python. The final output of the project should be a dataset with atleast 10,000 rows.  

The webpage chosen for scraping is : https://www.immoweb.be  

The project consists of two main files:  
1. scraping.py: This file contains the functionality of scraping data from the immo webpage. The result of the program is the `housing_data_100_clean` file.  `housing_data_100.csv` file is the file after scraping without the cleaning.  
2. get_links.py: This file contains the functionality to get all the links inside the immo webpage. The result of this program is the `all_links.txt` file which contains all the links from the website.

Technical difficulties:
1. Extracting the address: Through the html tags, the address information was difficult to extract. So, it is extracted from the javascript tags.  
2. Collection of link: The links within tha main page was not found in the source page. The link was shown via the inspect but could not extract it using the `a` tag along with `class` tag. Therefore used sitemap of the site to parse the xml file and get all the required links.
3. Getting response from the website: While running for 100 urls, it took almost 71 mins to get the data. It would take day(s) to get the 10000 at this speed. The immo server is taking too long to respond to my requests. 



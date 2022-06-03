# get all the links using the sitemap and save it in a file

from bs4 import BeautifulSoup
import requests

def get_tags(url, text):
    """
    This function will extract the tags as specified by the text input and return it.
    """
    r = requests.get(url)
    xml = r.text
    soup = BeautifulSoup(xml, features="lxml")
    tags = soup.find_all(text)
    
    return tags

def get_classifieds_links(tags):    
    """
    This function will extract the classifieds links from the sitemap
    """
    classifieds_links = []
    for sitemap in tags:
        link = sitemap.findNext("loc").text
        if 'classifieds' in link:
            classifieds_links.append(link)

    return classifieds_links  

def get_all_links(c_links, fname):      
    """
    This function will open each xml file and extract the links for the house/apartment for sale.
    The result of this function will be a txt file with all the links.
    """    
    # the links with these keywords should not be included
    exclude = ['new-real-estate-project-houses', 'new-real-estate-project-apartments', 
               'house-to-build', 'office', 'land', 'other', 'garage', 'business']

    for i in range(0, len(c_links)):
        print(i)
        url = c_links[i]
        xhtml_tags = get_tags(url, "loc")
         
        for sitemap in xhtml_tags:
            link = sitemap.findNext("loc")
            if (link != None) and ('for-sale' in link.text): 
                if any(x in link.text for x in exclude):
                    pass
                else:
                    with open(fname, "a") as file:
                        file.write(link.text + "\n" )    

def main():
    url = 'https://www.immoweb.be/sitemap.xml'
    text = 'sitemap'
    filename = 'all_links.txt'

    classified_tags = get_tags(url, text)    
    classifieds_links = get_classifieds_links(classified_tags)
    get_all_links(classifieds_links, filename)



if __name__ == "__main__":
    main()    


                     
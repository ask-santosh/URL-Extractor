from bs4 import BeautifulSoup
import requests

# urls = ["https://www.thinktac.com/", "https://www.raspberrypi.com/", "https://www.bharatpetroleum.in/"]
# urls = ["arduino.cc"]
urls = ["winevibe.com"]
# urls = ["officetaxservices.com", "treeservicelincoln.com", "treeservicelittletonco.com", "treeservicelovelandoh.com",
#         "treeservicelowell.com", "treeservicemantecaca.com", "treeservicemarketer.com", "treeservicemason.com",
#         "treeservicemedfordoregon.com"]


def get_web_content(url: str):
    try:
        r = requests.get("https://www."+url)
        # print(r.content)
        if r.status_code != 200:
            print(f"Unable to connect ({r.status_code}):    https://www." + url)
            return
    except requests.exceptions.ConnectionError:
        print(f"Error Timeout:    https://www."+url)
        return


    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(r.content, 'html5lib')
    # print(soup.prettify())

    # Find all anchor tags (links) on the page
    links = soup.find_all('a')
    # print(links)

    # Iterate through the links to find Facebook page URLs
    facebook_pages = []
    for link in links:
        href = link.get('href')
        if href and "facebook.com" in href:
            facebook_pages.append(href)

    # Filter out unique URLs (optional)
    unique_facebook_pages = list(set(facebook_pages))

    # Print the Facebook page URLs
    print("")
    for page_url in unique_facebook_pages:
        print(page_url)


ctr = 0
for i in urls:
    ctr += 1
    print(ctr, end="\t")
    get_web_content(i)

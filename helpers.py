import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver

import settings

# urls = ["https://www.thinktac.com/", "https://www.raspberrypi.com/", "https://www.bharatpetroleum.in/", "arduino.cc"]
# urls = ["officetaxservices.com", "treeservicelincoln.com", "treeservicelittletonco.com", "treeservicelovelandoh.com",
#         "treeservicelowell.com", "treeservicemantecaca.com", "treeservicemarketer.com", "treeservicemason.com",
#         "treeservicemedfordoregon.com"]
# total_no_urls = len(urls)
# print(total_no_urls)


def preprocess_link(url: str) -> dict:
    """

    :param url:
    :return:
    """

    is_edited = False
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
        is_edited = True

    return {"url": url, "is_edited": is_edited}


def without_selenium(url: str) -> dict:
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return {"extracted_links": [], "status_code": res.status_code, "err_msg": f"Status Code: {res.status_code}"}

        soup = BeautifulSoup(res.content, 'html5lib')
        hyperlinks = soup.find_all('a')

        facebook_pages = []
        for link in hyperlinks:
            href = link.get('href')
            if href and "facebook.com" in href:
                facebook_pages.append(href)
        facebook_pages = list(set(facebook_pages))

        return {"extracted_links": facebook_pages, "status_code": res.status_code, "err_msg": None}

    except requests.exceptions.ConnectionError:
        print(f"Error Timeout: " + url)
        return {"extracted_links": [], "status_code": 0, "err_msg": f"Error Timeout: {url}"}

    except Exception:
        print("error handeled")
        return {"extracted_links": [], "status_code": 0, "err_msg": f"Unable to connect"}


def with_selenium(url: str) -> dict:
    try:
        browser = webdriver.Chrome(chrome_options=settings.options)
        browser.get(url)
        time.sleep(10)

        # print(dir(browser))

        html = browser.page_source
        soup = BeautifulSoup(html, features='html.parser')
        hyperlinks = soup.find_all('a')
        browser.quit()

        facebook_pages = []
        for link in hyperlinks:
            href = link.get('href')
            if href and "facebook.com" in href:
                facebook_pages.append(href)
        facebook_pages = list(set(facebook_pages))

        return {"extracted_links": facebook_pages, "status_code": 200, "err_msg": None}

    except requests.exceptions.ConnectionError:
        print(f"Error Timeout: " + url)
        return {"extracted_links": [], "status_code": 0, "err_msg": f"Error Timeout: {url}"}

    except Exception:
        print("error handeled")
        return {"extracted_links": [], "status_code": 0, "err_msg": f"Unable to connect"}


# def export_pdf(data):
#     df = pd.DataFrame(list(data.items()), columns=['URL', 'Facebook URL'])
#     df["URL"] = data.keys()
#     df["Facebook URL"] = data.values()
#     # print(df)
#     df.to_excel('fb_list.xlsx', index=False)
#     return

# ctr = 1
# for home_url in urls:
#     home_url = preprocess_link(home_url)["url"]
#     res = without_selenium(home_url)
#     extracted_links = res.get("extracted_links", None)
#     if res.get("err_msg", None) or not extracted_links:
#         res = with_selenium(home_url)
#
#     print(ctr, "-->", res)
#     ctr += 1

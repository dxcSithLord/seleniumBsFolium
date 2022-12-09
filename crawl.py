"""
Description: Updated burger wars code to pull list of NHS location addresses
             and extend them to add longitude and latitude
Updated by: A.J.Amabile
Date: 2022-12-01
"""

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expcond
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as BeSoup
import csv
import re  # regular expression
import os
import test_uri

nhs_site = 'https://www.nhs.uk/'
nhs_url = 'ServiceDirectories/Pages/NHSTrustListing.aspx'


def get_health_trusts(site=nhs_site, url=nhs_url):
    #  Create a Chrome driver and crawl the URL

    driver = webdriver.Chrome()
    if test_uri.uri_match(site):
        driver.get(site + url)
        timeout = 10
        try:
            element_present = expcond.presence_of_element_located((By.CLASS_NAME, 'trust-list'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("scanning web page")

        page = driver.page_source
        soup = BeSoup(page, "lxml")
        driver.close()

        # Find all List of NHS Trust websites

        trust_list = soup.find_all('ul', class_='trust-list')
        url_list = []
        url_ids = []
        url_title = []
        """
        Get a list of NHS Trusts and the URL for further details
        """
        for r in trust_list:
            for href in r.find_all('a'):
                if 'class' not in href.attrs.keys() and \
                        'href' in href.attrs.keys() and \
                        'title' in href.attrs.keys():
                    t_url = href.attrs['href']
                    t_title = href.attrs['title']
                    try:
                        a, b = re.search(r'View details for ', t_title).span()
                    except ValueError:
                        a, b = 0, 0

                    if t_url is not None:
                        #  print(t_url, href.attrs['title'])
                        url_list.append([t_url, t_title[b:]])  # lose the "View details for " from title
                        try:
                            url_ids.append(int(t_url.split('=')[-1]))  # extract URL ID
                        except ValueError:
                            print("Value error with %s", t_url)
                        url_title.append(href.attrs['title'])
                    else:
                        print(r.text + "is none")
        print(len(url_list))
        url_map = zip(url_ids, url_list)
        t_urld = dict(url_map)
    else:
        print("Site", site, "is not a valid URL")
        t_urld = {}
    return t_urld


def get_hospitals(site, t_urld):
    """
    Get the addresses of hospitals within the NHS Trusts
    return a dict of id, list of [title:string, url:string,
        address:list of [address components], trust_id]
    """
    if not test_uri.uri_match(site):
        print("site", site, "is not a value URI")
        return {}

    driver = webdriver.Chrome()
    h_dict = {}  # made up of h_ids linking list of h_urls, h_names and h_addrs
    # { t_urld.id = 0,  ::= this is the regional NHS trust
    # { hospital_dict.id = 1,  ::= the set of hospitals in the trust
    #  [[ hospital_address, lines, postcode ],
    #  "hospital name",
    #  "hospital URL" }
    for trust_key in list(t_urld.keys()):
        url = t_urld[trust_key][0]
        (a, b) = re.search('Overview', url).span()
        # As the NHS trust website give a list of the trusts, each trust
        # site first provides an overview, but the section we need is the
        # hospitals and clinics, hence
        # replace "Overview" with Hospitals and Clinics in url
        driver.get(site + url[:a] + 'HospitalsAndClinics' + url[b:])
        timeout = 10
        try:
            element_present = expcond.presence_of_element_located((By.CLASS_NAME, 'panel-content'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("scanning web page")

        page = driver.page_source
        soup = BeSoup(page, "lxml")

        hospitals = soup.find_all('div', class_=['box-list clear hospital-list',
                                                 'box-list clear clinic-list'])

        # Hospitals and clinics, not "others", as the format is different
        for H in hospitals[0:2]:
            # variables reset for each hospital
            for addrs in H.find_all('dd', class_='addrss'):
                # returns a list with alternate elements containing address
                # the "contents[1].a" accesses the contents of the
                # grandparent 'a' tag
                link = addrs.parent.parent.contents[1].a
                if link is not None:
                    h_dict[link.get('href').split('id=')[-1]] \
                        = [link.text, link.get('href'),
                           addrs.contents[::2], trust_key]
                else:
                    print("addrs does not have a linked parent:", addrs)
        print(len(h_dict.keys()))
    driver.close()
    return h_dict


def make_dataset(file_name, t_dict, h_dict):
    # Create dataset
    with open(file_name, mode='w', newline='', encoding='utf-8') as outputFile:
        hospitals_csv = csv.writer(outputFile, delimiter=',',
                                   quotechar='"', quoting=csv.QUOTE_MINIMAL)
        hospitals_csv.writerow(['id', 'Hospital', 'URL', 'Address',
                                'TrustID', 'TrustName', 'TrustURL'])
        for key in h_dict.keys():
            hospital_url = h_dict[key][1]
            if not test_uri.uri_match(hospital_url):
                hospital_url = nhs_site + hospital_url   # may have two "/" in url
            t_key = h_dict[key][3]
            hospitals_csv.writerow([key, h_dict[key][0], hospital_url,
                                    ",".join(h_dict[key][2]), t_key,
                                    t_dict[t_key][1], t_dict[t_key][0]])


if __name__ == '__main__':
    data_file_name = os.getenv('HOSPITALS_CSV', '')
    assert len(data_file_name) > 3, \
        f"Expected filename with more the three characters, got: {len(data_file_name)}"

    trust_dict = get_health_trusts(nhs_site, nhs_url)
    hospital_dict = get_hospitals(nhs_site, trust_dict)
    make_dataset(data_file_name, trust_dict, hospital_dict)
    """
        Direct run process.
    """
    '''
    assert num_sections > 2, \
        f"Expected more than one section from config file, got: {num_sections}"
    assert 'InFile1' in testing.sections(), "InFile1 section not found"
    assert 'InFile2' in testing.sections(), "InFile2 section not found"
    assert 'OutFile' in testing.sections(), "OutFile section not found"
    for secs in testing.sections():
        print(f"keys in {secs} {list(testing[secs].keys())}")
    '''

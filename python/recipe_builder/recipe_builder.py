import urllib.request
import re
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin
import time
import glob
import os


# fp = urllib.request.urlopen(url)
# mybytes = fp.read()
# html_str = mybytes.decode("utf8")
# fp.close()

# file_name = url.split("/")[-1]
# file_path = f"knowledge_base/{file_name}.html"
# print(f"Writing to {file_path}.")
# with open(file_path, "w", encoding="utf-8") as file:
#     file.write(html_str)


# recursively scrape recipes using bfs
def scrape_recipes(url):
    # grab list of existing files
    prev_parsed_files = glob.glob("./knowledge_base/*.html")
    prev_parsed_file = [os.path.basename(x) for x in prev_parsed_files]


    next_url = url
    parsed_urls = set()
    urls_to_parse = []
    urls_to_parse_set = set()
    max_recipes = 2500
    # starting at the given url, perform bfs to scrape the entire recipe
    while True:
        if next_url in parsed_urls:
            next_url = urls_to_parse.pop(0)
            continue
        if (len(parsed_urls) >= max_recipes):
            print("Max recipes reached. Exiting.")
            return
        print(f"Parsing {next_url}. {len(parsed_urls)} urls parsed. {len(urls_to_parse)} remaining urls.")
        html_str = extract_html_str(next_url)
        save_html(next_url, html_str)
        urls = extract_urls_from_html(next_url, html_str)
        
        parsed_urls.add(next_url)
        new_urls = set([n_url for n_url in urls if n_url not in parsed_urls and n_url not in urls_to_parse_set])
        urls_to_parse += new_urls
        urls_to_parse_set.update(new_urls)

        next_url = urls_to_parse.pop(0)
        if not next_url: 
            break
        time.sleep(2)


def extract_html_str(url):
    fp = None
    while (True):
        retries = 0
        try:
            fp = urllib.request.urlopen(url)
            break
        except Exception as e:
            if retries >= 2:
                raise e
            time.sleep(5)


    mybytes = fp.read()
    html_str = mybytes.decode("utf8")
    fp.close()
    return html_str

# save the url from the given html to a file
def save_html(url, html_str):
    file_name = url.split("/")[-1]
    file_path = f"knowledge_base/{file_name}.html"
    # print(f"Writing to {file_path}.")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_str)

# extract all spring recipe urls from the html article
def extract_urls_from_html(url, html_str):
    soup = BeautifulSoup(html_str, "html.parser")
    urls = []

    for undesired_div in soup.select('.theme-doc-sidebar-item-category theme-doc-sidebar-item-category-level-1 menu__list-item'):
        soup.decompose() # Removes the tag and its entire content

    article = soup.find('article')
    for link in article.find_all('a'):
        href = link.get('href')
        if href.startswith('#'):
            continue
        href_url = urljoin(url, href)
        # check if the link is to a recipe
        url_format = "^(.+docs\.openrewrite.+recipes(?:(?!(#.*)).)*)"
        url_extract = re.match(url_format, href_url)
        if not url_extract:
            # print(href_url)
            continue
        if re.match(".+docs\.openrewrite\.org\/recipes\/java\/spring\/boot[0-9]\/upgradespringboot_[0-9]_[0-9]$", href_url):
            continue
        if re.match("https://docs.openrewrite.org/reference/recipes-by-tag.+", href_url):
            continue
        if href_url in ["https://docs.openrewrite.org/recipes/yaml", "https://docs.openrewrite.org/recipes", "https://docs.openrewrite.org/recipes/java", "https://docs.openrewrite.org/recipes/java/spring", "https://docs.openrewrite.org/reference/recipes-by-tag"]:
            continue
        # if re.match("https://docs.openrewrite.org/recipes/java/spring/boot[0-9]$", href_url):
        #     continue

        # print(f"{href_url}")
        urls.append(url_extract.group())
    return urls


url = "https://docs.openrewrite.org/recipes/java/spring/boot3"
scrape_recipes(url)
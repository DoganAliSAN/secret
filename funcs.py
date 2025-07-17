import time
from curl_cffi import requests
from bs4 import BeautifulSoup
from ouo_bypass import ouo_bypass
# Step 1: Get the main page without proxy

def get_link(url):
    url_base = "https://ouo.io/"

    new_out = ""
    while new_out == "":
        try:
            out = ouo_bypass.ouo_bypass(url)
            bypass = out.get("bypassed_link")
            while "ouo" in bypass:

                new_code = bypass.split(".io/")[1]
                new_url = url_base+new_code
                new_out = ouo_bypass.ouo_bypass(new_url)
                bypass = new_out.get("bypassed_link")
                new_out = bypass
                print(bypass)
            new_out = bypass
        except :
            new_out = ""
    return new_out
def get_articles_by_page(page_number):
    url = f"https://turkifsaalemi.com/tia/page/{page_number}"
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    # Step 2: Find all <a> tags inside the target container
    container = soup.select_one("#main-content > div.content > div.post-listing.archive-box")
    post_links = []

    if container:
        a_tags = container.find_all("a", href=True)
        for a in a_tags:
            href = a["href"]
            if href not in post_links:
                post_links.append(href)

    print(f"Found {len(post_links)} article links.")

    # Step 3: Visit each article and extract links from p:nth-child(4) and (5)
    all_download_links = []
    return_list = []
    post_links = set(post_links)
    for post_url in post_links:
        try:
            print(f"Visiting: {post_url}")
            post_response = requests.get(post_url, timeout=15)
            post_soup = BeautifulSoup(post_response.text, "html.parser")
            title =  post_soup.select_one("#the-post > div > h1").text
            print(f"Title: {title}")
            # Get links from p:nth-child(4)
            p4 = post_soup.select_one("#the-post > div > div.entry > p:nth-child(4)")
            if p4:
                a_tags = p4.find_all("a", href=True)
                for a in a_tags:
                    all_download_links.append(a["href"])
                    print(get_link(a["href"]))
                    return_list.append(f"{title},{get_link(a['href'])}")
                    p_link = get_link(a["href"])
                    print("writing in file")
                    with open("templates/last-get.html","a+") as f:
                        f.write(f'<a href=\"{p_link}\"> {title}</a><br>\n')

            # Optionally get from p:nth-child(5)
            p5 = post_soup.select_one("#the-post > div > div.entry > p:nth-child(5)")
            if p5:
                a_tags = p5.find_all("a", href=True)
                for a in a_tags:
                    all_download_links.append(a["href"])
                    print(get_link(a["href"]))
                    return_list.append(f"{title},{get_link(a['href'])}")
                    p_link = get_link(a["href"])
                    print("writing in file")

                    with open("templates/last-get.html","a+") as f:
                        f.write(f'<a href=\"{p_link}\"> {title}</a><br>\n')

            time.sleep(0.5)  # polite delay

        except Exception as e:
            print(f"Error while processing {post_url}: {e}")
            continue
    return return_list
# Step 4: Print final results




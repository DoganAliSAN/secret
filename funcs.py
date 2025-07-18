import httpx
from bs4 import BeautifulSoup
from ouo_bypass import ouo_bypass
import time
from database import add_link

# Your proxy configuration
proxy_url = "http://fOKUYXAOqvb2X9rW:PCpUshlGu2LEiq27_session-Ppg6hvvb_lifetime-5m@geo.iproyal.com:12321"
proxies = {
    "http://": proxy_url,
    "https://": proxy_url,
}

def get_link(url, log_status):
    url_base = "https://ouo.io/"
    new_out = ""
    try_count = 0
    while new_out == "":
        try_count += 1
        try:
            log_status(f"Bypassing ouo: {url}")
            out = ouo_bypass(url)
            bypass = out.get("bypassed_link")

            while "ouo" in bypass:
                new_code = bypass.split(".io/")[1]
                new_url = url_base + new_code
                log_status(f"Recursing bypass: {new_url}")
                new_out = ouo_bypass(new_url)
                bypass = new_out.get("bypassed_link")
                new_out = bypass
            new_out = bypass
        except Exception as e:
            log_status(f"Retrying bypass ({try_count}) due to error: {e}")
            new_out = ""
    return new_out

def get_articles_by_page(page_number, log_status):
    url = f"https://turkifsaalemi.com/tia/page/{page_number}"
    log_status(f"Fetching page: {url}")

    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:            
            response = client.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            container = soup.select_one("#main-content > div.content > div.post-listing.archive-box")
            post_links = []

            if container:
                a_tags = container.find_all("a", href=True)
                for a in a_tags:
                    href = a["href"]
                    if href not in post_links:
                        post_links.append(href)

            log_status(f"Found {len(post_links)} post links")

            for post_url in post_links:
                try:
                    log_status(f"Scraping post: {post_url}")
                    post_response = client.get(post_url)
                    post_soup = BeautifulSoup(post_response.text, "html.parser")
                    title_element = post_soup.select_one("#the-post > div > h1")
                    title = title_element.text if title_element else "No title"

                    log_status("Checking p:nth-child(4)")
                    p4 = post_soup.select_one("#the-post > div > div.entry > p:nth-child(4)")
                    if p4:
                        a_tags = p4.find_all("a", href=True)
                        for a in a_tags:
                            p_link = get_link(a["href"], log_status)
                            log_status("Adding link (p4): " + p_link)
                            add_link(title, p_link)

                    log_status("Checking p:nth-child(5)")
                    p5 = post_soup.select_one("#the-post > div > div.entry > p:nth-child(5)")
                    if p5:
                        a_tags = p5.find_all("a", href=True)
                        for a in a_tags:
                            p_link = get_link(a["href"], log_status)
                            log_status("Adding link (p5): " + p_link)
                            add_link(title, p_link)

                    time.sleep(0.5)
                except Exception as e:
                    log_status(f"Error parsing post: {post_url} — {e}")
                    continue

            log_status("✅ Done.")
    except Exception as e:
        log_status(f"Error loading main page: {e}")
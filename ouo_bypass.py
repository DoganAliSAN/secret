import asyncio
import re
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from nodriver import start

# ----------------------------------------------------------
async def get_recaptcha_token(page):
    anchor_url = ('https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x'
                  '&co=aHR0cHM6Ly9vdW8ucHJlc3M6NDQz&hl=en&v=pCoGBhjs9s8EhFOHJFe8cqis&size=invisible&cb=ahgyd1gkfkhe')

    await page.goto(anchor_url)
    html = await page.content()
    token = re.search(r'recaptcha-token" value="(.*?)"', html).group(1)

    post_data = {
        "v": "pCoGBhjs9s8EhFOHJFe8cqis",
        "reason": "q",
        "c": token,
        "k": "6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x",
        "co": "aHR0cHM6Ly9vdW8ucHJlc3M6NDQz"
    }

    reload_url = "https://www.google.com/recaptcha/api2/reload?k=6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x"
    await page.goto(reload_url, method="POST", post_data=post_data)
    response_html = await page.content()
    answer = re.search(r'"rresp","(.*?)"', response_html).group(1)
    return answer

# ----------------------------------------------------------
async def ouo_bypass_nodriver(url):
    browser = await start(headless=True)
    page = await browser.page()

    tempurl = url.replace("ouo.press", "ouo.io")
    p = urlparse(tempurl)
    id = tempurl.split('/')[-1]

    await page.goto(tempurl)
    html = await page.content()
    next_url = f"{p.scheme}://{p.hostname}/go/{id}"

    for _ in range(2):
        if page.response and page.response.headers.get("Location"):
            break

        soup = BeautifulSoup(html, "html.parser")
        inputs = soup.form.find_all("input", {"name": re.compile(r"token$")})
        data = {el.get('name'): el.get('value') for el in inputs}
        data['x-token'] = await get_recaptcha_token(page)

        await page.goto(next_url, method="POST", post_data=data,
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
        html = await page.content()
        next_url = f"{p.scheme}://{p.hostname}/xreallcygo/{id}"

    headers = await page.response_headers()
    location = headers.get("Location") if headers else None
    return {
        'original_link': url,
        'bypassed_link': location
    }

# ----------------------------------------------------------
if __name__ == "__main__":
    url_base = "https://ouo.io/"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("URL code: ")

    url = url_base + url if not url.startswith("http") else url

    async def main():
        out = await ouo_bypass_nodriver(url)
        bypass = out.get("bypassed_link")

        while bypass and "ouo" in bypass:
            new_code = bypass.split(".io/")[1]
            new_url = url_base + new_code
            out = await ouo_bypass_nodriver(new_url)
            bypass = out.get("bypassed_link")
            print(out)

        print(out)

    asyncio.run(main())
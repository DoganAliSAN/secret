import re
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import httpx

# -------------------------------------------
def RecaptchaV3():
    ANCHOR_URL = 'https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x&co=aHR0cHM6Ly9vdW8ucHJlc3M6NDQz&hl=en&v=pCoGBhjs9s8EhFOHJFe8cqis&size=invisible&cb=ahgyd1gkfkhe'
    url_base = 'https://www.google.com/recaptcha/'
    post_data_template = "v={}&reason=q&c={}&k={}&co={}"
    
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    with httpx.Client(headers=headers) as client:
        matches = re.findall(r'([api2|enterprise]+)/anchor\?(.*)', ANCHOR_URL)[0]
        url_base += matches[0] + '/'
        params = matches[1]
        res = client.get(url_base + 'anchor', params=params)
        token = re.findall(r'"recaptcha-token" value="(.*?)"', res.text)[0]
        params_dict = dict(pair.split('=') for pair in params.split('&'))
        post_data = post_data_template.format(params_dict["v"], token, params_dict["k"], params_dict["co"])
        res = client.post(url_base + 'reload', params={'k': params_dict["k"]}, data=post_data)
        answer = re.findall(r'"rresp","(.*?)"', res.text)[0]
    return answer

# -------------------------------------------

HEADERS = {
    'authority': 'ouo.io',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    'referer': 'http://www.google.com/ig/adde?moduleurl=',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/110.0.0.0 Safari/537.36'
}

# -------------------------------------------
# OUO BYPASS

def ouo_bypass(url):
    tempurl = url.replace("ouo.press", "ouo.io")
    p = urlparse(tempurl)
    id = tempurl.split('/')[-1]
    
    with httpx.Client(headers=HEADERS, follow_redirects=False) as client:
        res = client.get(tempurl)
        next_url = f"{p.scheme}://{p.hostname}/go/{id}"

        for _ in range(2):
            if res.headers.get('location'):
                break

            bs4 = BeautifulSoup(res.content, 'lxml')

            form = bs4.find('form')
            if not form:
                with open("error.html", "w") as f:
                    f.write(res.text)
                raise Exception("No form found on the page")
            inputs = form.findAll("input", {"name": re.compile(r"token$")})
            data = {input.get('name'): input.get('value') for input in inputs}
            data['x-token'] = RecaptchaV3()

            headers_post = {
                'content-type': 'application/x-www-form-urlencoded',
                'user-agent': HEADERS['user-agent'],
                'referer': tempurl,
            }

            res = client.post(next_url, data=data, headers=headers_post, follow_redirects=False)
            next_url = f"{p.scheme}://{p.hostname}/xreallcygo/{id}"

        return {
            'original_link': url,
            'bypassed_link': res.headers.get('location')
        }

# -------------------------------------------


if __name__ == "__main__":
    url_base = "https://ouo.io/"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("URL code: ")
    url = url_base + url
    out = ouo_bypass(url)
    bypass = out.get("bypassed_link")
    while "ouo" in bypass:
        new_code = bypass.split(".io/")[1]
        new_url = url_base + new_code
        new_out = ouo_bypass(new_url)
        bypass = new_out.get("bypassed_link")
        print(new_out)
    print(out)
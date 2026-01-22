import bleach
from bleach.css_sanitizer import CSSSanitizer
from bs4 import BeautifulSoup



ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's',
    'h1', 'h2', 'h3', 'h4',
    'ul', 'ol', 'li','sub','sup',
    'blockquote', 'pre', 'code',
    'span', 'div',
    'a', 'img'
]

ALLOWED_ATTRIBUTES = {
    '*': ['style', 'class'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height']
}

ALLOWED_STYLES = [
    'color',
    'background-color',
    'text-align',
    'font-size',
    'font-weight',
    'font-style',
    'text-decoration',
    'border',
    'margin',
    'padding',
    'width',
    'height'
]
ALLOWED_PROTOCOLS = ["http", "https", "data"]

css_sanitizer = CSSSanitizer(
    allowed_css_properties=ALLOWED_STYLES
)

def sanitize_html(html):
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=css_sanitizer,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )

def sanitize_comment(comment):
    return bleach.clean(
        comment,
        tags=['p', 'br', 'strong', 'em', 'u', 's'],
        attributes={'a': ['href', 'title', 'target', 'rel'],},
        css_sanitizer=css_sanitizer,
        strip=True
    )

def normalize_links(html):
    soup = BeautifulSoup(html, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        if href.startswith("www."):
            a["href"] = "https://" + href

        elif not href.startswith(("http://", "https://", "/", "#")):
            a["href"] = "https://" + href

        a["rel"] = "noopener noreferrer"
        a["target"] = "_blank"
        a["style"] = "text-decoration: underline; color:blue;"

    return str(soup)
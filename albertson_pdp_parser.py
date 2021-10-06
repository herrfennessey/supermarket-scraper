import ast
import logging
import re

from bs4 import BeautifulSoup

PID_REGEX = re.compile(r"^.*product-details\.([0-9]*)\.html")
STORE_NAME = "albertsons"


def parse_pdp_response(pid, url, response):
    soup = BeautifulSoup(response.text, "lxml")

    script_blocks = soup.find_all("script", type="application/ld+json")
    title_reference = soup.find("title").string
    product_name = title_reference.split("-")[0]

    categories = []

    for script_block in script_blocks:
        try:
            block = ast.literal_eval(script_block.contents[0].strip())
        except Exception as e:
            logging.warn(f"Couldn't parse the html for this weird body {script_block} ", e)
            continue
        block_type = block.get("@type", "")
        if block_type == "BreadcrumbList":
            breadcrumbs = block.get("itemListElement")
            for breadcrumb in breadcrumbs:
                categories.append(breadcrumb.get("name"))
        elif block_type == "Product":
            product_name = block.get("name")
            if "offers" in block:
                url = block.get("offers").get("url")
        else:
            continue

    return {
        "pid": pid,
        "store_name": STORE_NAME,
        "url": url,
        "product_name": product_name,
        "product_category": categories
    }

import requests
import bs4
from collections import OrderedDict
import re
import datetime


def get_brick_seek():
    bs_url = "https://brickseek.com/deals?search=Lego"
    bs_req = requests.get(bs_url)
    bs_soup = bs4.BeautifulSoup(bs_req.text, 'lxml')
    bs_dict = {}

    for item in bs_soup.select(".item-list__item"):
        if "walmart" in str(item.select(".item-list__store")[0]):
            bs_store = "Walmart"
        elif "amazon" in str(item.select(".item-list__store")[0]):
            bs_store = "Amazon"
        elif "best-buy" in str(item.select(".item-list__store")[0]):
            bs_store = "Best Buy"
        else:
            bs_store = "Target"
        bs_title = item.select(".item-list__title")[0].text.split(";")[0]
        bs_price = "{:.2f}".format(float(item.select(".price-formatted__dollars")[0].text +
                                         "." + item.select(".price-formatted__cents")[0].text))
        bs_msrp = "{:.2f}".format(float(item.select(".price-formatted__dollars")[1].text +
                                        "." + item.select(".price-formatted__cents")[1].text))
        bs_discount = item.select(".item-list__discount-meter-bar-fill-text")[0].text.split(" ")[0]\
            .strip().replace("%", "")
        bs_date = item.select(".item-list__disclaimer-line")[0].text.strip().split(" ")[1]
        bs_date = datetime.datetime.strptime(bs_date, "%m/%d/%y").strftime("%m/%d/%Y")
        bs_location = item.select(".item-list__type-banner")[0].text.strip()
        bs_dict[bs_title] = {'Price': bs_price,
                             'MSRP': bs_msrp,
                             'Discount': int(bs_discount),
                             'Date': bs_date,
                             'Location': bs_location,
                             'Store': bs_store}

    bs_sorted = OrderedDict(sorted(bs_dict.items(), key=lambda i: i[1]['Discount'], reverse=True))

    return [f"{bs_sorted[key]['Discount']}% Off | "
            f"{key} | "
            f"Price: ${bs_sorted[key]['Price']} | "
            f"MSRP: ${bs_sorted[key]['MSRP']} | "
            f"Store: {bs_sorted[key]['Store']} ({bs_sorted[key]['Location']}) | "
            f"Added {bs_sorted[key]['Date']}"
            for key in bs_sorted]


def get_slick_deals():
    sd_url = "https://slickdeals.net/newsearch.php?q=lego&pp=20&sort=newest&forumid%5B%5D=30&forumid%5B%5D=9&" \
             "forumid%5B%5D=25&forumid%5B%5D=4&forumid%5B%5D=10&forumid%5B%5D=38&forumid%5B%5D=39&forumid%5B%5D=44&" \
             "forumid%5B%5D=53&forumid%5B%5D=54&forumchoice%5B%5D=4&forumchoice%5B%5D=9&forumchoice%5B%5D=10&" \
             "forumchoice%5B%5D=25&forumchoice%5B%5D=30&forumchoice%5B%5D=38&forumchoice%5B%5D=39&" \
             "forumchoice%5B%5D=44&forumchoice%5B%5D=53&forumchoice%5B%5D=54&%22+%5C+%22forumchoice%5B%5D=13&" \
             "%22+%5C+%22forumchoice%5B%5D=41&firstonly=1"
    sd_req = requests.get(sd_url)
    sd_soup = bs4.BeautifulSoup(sd_req.text, 'lxml')
    sd_dict = {}

    for item in sd_soup.select(".resultRow"):
        try:
            sd_store = item.select(".store")[0].text.strip()
        except IndexError:
            sd_store = "None"
        sd_title = item.select(".dealTitle")[0].text
        try:
            sd_price = "{:.2f}".format(float(item.select(".price")[0].text.strip().replace("$", "")))
        except ValueError:
            sd_price = "{:.2f}".format(float(0.00))
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        sd_info = item.select(".dealInfo")[0].text.strip()
        sd_date_string = re.search('\\d+/\\d+/\\d{4}', sd_info)
        if "yesterday" in sd_info.lower():
            sd_date = yesterday.strftime("%m/%d/%Y")
        elif "today" in sd_info.lower():
            sd_date = today.strftime("%m/%d/%Y")
        else:
            sd_date = datetime.datetime.strptime(sd_date_string.group(), "%m/%d/%Y")
            sd_date = sd_date.strftime("%m/%d/%Y")
        sd_dict[sd_title] = {'Price': sd_price,
                             'Date': sd_date,
                             'Store': sd_store}

    sd_sorted = OrderedDict(sorted(sd_dict.items(), key=lambda i: float(i[1]['Price'])))
    return [f"Price: ${sd_sorted[key]['Price']} | "
            f"{key} | "
            f"Store: {sd_sorted[key]['Store']} | "
            f"Added {sd_sorted[key]['Date']}"
            for key in sd_sorted]


def write_file(*argv):
    with open('lego_deals.txt', 'w', encoding="utf-8") as my_file:
        for arg in argv:
            for item in arg:
                my_file.write(item + "\n")


if __name__ == "__main__":
    write_file(get_brick_seek(), get_slick_deals())

from bs4 import BeautifulSoup
import requests
import csv
import re

out = open("output.csv", "w", newline="\n")
csv_writer = csv.writer(out, delimiter=",")
csv_writer.writerow(["First Name", "Last Name", "Address", "City", "Province", "Postal Code"])


def print_names(page: BeautifulSoup) -> None:
    """
    Prints each of the URLs that refer to a name
    """
    lists = page.find_all("ul")
    name_links = lists[1]
    names = name_links.find_all("li")

    for name in names:
        name_link = "https://411.ca" + name.a["href"]
        print(name_link)
        find_correct_names(name_link)


def find_correct_names(url: str) -> None:
    """
    For each name URL, finds the names that do not have last name "Markham" and
    appends them to "names.txt" file.
    """
    name_result = requests.get(url)
    name_page = BeautifulSoup(name_result.text, "html.parser")

    profiles = name_page.find_all("a", {"class": "listing-card-link"})

    for profile in profiles:
        if not re.search("Markham", profile.find("h4").text, re.IGNORECASE):
            profile_url = profile["href"]
            write_data("https://411.ca" + profile_url)


def write_data(profile_url: str) -> None:
    profile_result = requests.get(profile_url)
    profile_page = BeautifulSoup(profile_result.text, "html.parser")
    contact_info = profile_page.find("div", {"class": "contact-info"})

    first_name = contact_info.find("span", {"itemprop": "givenName"})
    last_name = contact_info.find("span", {"itemprop": "familyName"})
    address = contact_info.find("span", {"itemprop": "streetAddress"})
    city = contact_info.find("span", {"itemprop": "addressLocality"})
    province = contact_info.find("span", {"itemprop": "addressRegion"})
    postal_code = contact_info.find("span", {"itemprop": "postalCode"})

    items = [first_name, last_name, address, city, province, postal_code]

    for i in range(len(items)):
        try:
            items[i] = items[i].text.strip().replace(",", "")
        except AttributeError:
            items[i] = ""

    csv_writer.writerow(items)
    print(first_name, last_name, address, city, province, postal_code)

if __name__ == "__main__":
    main_url = "https://411.ca/white-pages/on/markham"
    main_result = requests.get(main_url)
    main_page = BeautifulSoup(main_result.text, "html.parser")

    # Operate on the main page
    print_names(main_page)

    # Find the second URL
    head = main_page.head
    links = head.find_all("link")

    while links[-1]["rel"][0] == "next":
        # Go to next page
        next_url = links[-1]["href"]
        print(next_url)
        next_result = requests.get(next_url)
        next_page = BeautifulSoup(next_result.text, "html.parser")

        # Operate on the next page
        print_names(next_page)

        # Find the next URL
        head = next_page.head
        links = head.find_all("link")

    out.close()

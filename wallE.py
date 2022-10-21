from collections import defaultdict
import json
import re
import unicodedata
from bs4 import BeautifulSoup
import requests


def findJobs(url: str = "https://boards.greenhouse.io/coursera") -> list[str]:
    """Find all job urls from Coursera site

    Args:
        url (str, optional): url to embedded GreenHouse jobs pages for Coursera. Defaults to "https://boards.greenhouse.io/coursera".

    Returns:
        list[str]: a list of job urls
    """

    # Make a http get request to the url
    req = requests.get(url)

    # Parse the html
    soup = BeautifulSoup(req.content, "lxml")

    # Find the root url
    url = url.removesuffix("/coursera")

    # Find and form job urls
    return [
        url + tag["href"]
        for tag in soup.find_all(href=re.compile(r"/coursera/jobs/\d*"))
    ]


def normalize(s: str) -> str:
    """Normalize a string including remove unicode and strip whitespaces

    Args:
        s (str): raw string

    Returns:
        str: normalized string
    """

    # Remove unicode characters
    s = (
        unicodedata.normalize("NFC", s)
        .encode("ascii", "ignore")
        .decode("utf-8", "ignore")
    )

    # Strip leading and tailing spaces
    s = s.strip()

    return s


def parseJob(url: str) -> dict:
    """Parse through job information

    Args:
        url (str): url to a job posting

    Returns:
        dict: extracted information
    """

    # Make a http get request to the url
    req = requests.get(url)

    # Parse through the html
    soup = BeautifulSoup(req.content, "lxml")

    # Intialize a dict to store job information
    job = defaultdict(str)

    # Extract title
    job["Title"] = normalize(soup.find(attrs={"class": "app-title"}).text)

    # Extract location
    job["Location"] = normalize(soup.find(attrs={"class": "location"}).text)

    # Extract description
    job["Description"] = soup.find(True, text=re.compile(r"Job Overview"))
    job["Description"] = (
        normalize(job["Description"].next_sibling.next_sibling.text)
        if job["Description"]
        else ""
    )

    # Extract responsibilities
    job["Responsibilities"] = soup.find(True, text=re.compile(r"Responsibilities"))
    job["Responsibilities"] = (
        [
            normalize(tag.text)
            for tag in job["Responsibilities"].findNextSibling("ul").find_all("li")
        ]
        if job["Responsibilities"]
        else []
    )

    # Extract basic qualifications
    job["Basic Qualifications"] = soup.find(
        True, text=re.compile(r"Basic Qualifications|Your Skills")
    )
    job["Basic Qualifications"] = (
        [
            normalize(tag.text)
            for tag in job["Basic Qualifications"].findNextSibling("ul").find_all("li")
        ]
        if job["Basic Qualifications"]
        else []
    )

    # Extract prefered qualifications
    job["Preferred Qualifications"] = soup.find(
        True, text=re.compile(r"Preferred Qualifications")
    )
    job["Preferred Qualifications"] = (
        [
            normalize(tag.text)
            for tag in job["Preferred Qualifications"]
            .findNextSibling("ul")
            .find_all("li")
        ]
        if job["Preferred Qualifications"]
        else []
    )

    return dict(job)


def main():
    """Starting point"""

    # Find all jobs
    jobs = findJobs()

    # Extract all jobs information
    jobs = [parseJob(job) for job in jobs]

    # Dump info into a jason
    with open("output.json", "w") as f:
        json.dump(jobs, f)


if __name__ == "__main__":
    main()

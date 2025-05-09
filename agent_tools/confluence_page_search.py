from dotenv import load_dotenv
import os
from typing import List
from dataclasses import dataclass, asdict
import json

from atlassian import Confluence
import html2text
from bs4 import BeautifulSoup
import re

@dataclass
class ConfluencePage:
    id: str
    title: str
    content: str

def make_hrefs_relative(text_content):
    re.findall('pattern', text_content)
    soup = BeautifulSoup(text_content, "html.parser")
    for a in soup.findAll('a'):
        if 'href' not in a.attrs:
            continue
        link = a['href']
        # Don't process external links
        if 'http' in link:
            continue
        linkname, extension = os.path.splitext(link)
        a['href'] = './%s' % linkname
    return str(soup)

def confluence_page_search_tool(search_phrase: str = None) -> List[ConfluencePage]:
    """
    Search for Confluence pages in a space containing a phrase to get more information about a particular project.

    Args:
        search_phrase (str): The phrase to search for.

    Returns:
        List[ConfluencePage]: A list of ConfluencePage dataclass objects, 
        each containing the following about the page 
        - id
        - title
        - content

    Raises:
        Exception: If no search phrase is provided.
    """
    load_dotenv()
    response = []

    if search_phrase is None or len(search_phrase) == 0:
        raise Exception("No search phrase provided")
    
    # For Confluence Cloud
    confluence = Confluence(
        url = os.getenv("JIRA_SERVER"),
        username = os.getenv("JIRA_USER"),
        password = os.getenv("JIRA_TOKEN"),
        cloud = True
    )

    # Search pages in a space
    pages = confluence.cql(f"space={os.getenv('JIRA_PROJECT_KEY')} and text ~ '{search_phrase}' and type=page")
    for result in pages['results']:
        page = result['content']
        content = confluence.get_page_by_id(page_id=page['id'], expand="body.storage")
        # print(f"Page ID: {page['id']}, Title: {page['title']}, url: {page['_links']['webui']}\n")
        # print(content["body"]["storage"]["value"])
        html_content = make_hrefs_relative(content["body"]["storage"]["value"])
        markdown_text = html2text.html2text(html_content)
        response.append(json.dumps(asdict(ConfluencePage(
            id = page['id'], 
            title = page['title'], 
            content = markdown_text
        ))))

    return response

def confluence_get_stakeholders_tool():
    load_dotenv()
    response = []

    # For Confluence Cloud
    confluence = Confluence(
        url = os.getenv("JIRA_SERVER"),
        username = os.getenv("JIRA_USER"),
        password = os.getenv("JIRA_TOKEN"),
        cloud = True
    )

    # Search pages in a space
    pages = confluence.cql(f"space={os.getenv('JIRA_PROJECT_KEY')} and title = 'Stakeholders' and type=database")
    for result in pages['results']:
        page = result['content']
        content = confluence.get_page_by_id(page_id=page['id'], expand="body.storage")
        # print(f"Page ID: {page['id']}, Title: {page['title']}, url: {page['_links']['webui']}\n")
        # print(content["body"]["storage"]["value"])
        html_content = make_hrefs_relative(content["body"]["storage"]["value"])
        markdown_text = html2text.html2text(html_content)
        response.append(json.dumps(asdict(ConfluencePage(
            id = page['id'], 
            title = page['title'], 
            content = markdown_text
        ))))

    return response

if __name__ == "__main__":    
    print(confluence_get_stakeholders_tool())

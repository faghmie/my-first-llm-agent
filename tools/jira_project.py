from jira import JIRA
from jira.exceptions import JIRAError
import os
from dotenv import load_dotenv

from dateutil import parser
import pytz

class JiraProject():
    def __init__(self, project_key: str = None):
        self.jira_connection = None
        load_dotenv()

        self.project_key = project_key or os.getenv("JIRA_PROJECT_KEY")
        self.connected = False

    def use(self, *args, **kwargs):
        self.connect()
        reponse = self.query()
        return reponse

    def parse_jira_date(self, date_str):
        """Parse Jira datetime string to timezone-aware datetime object"""
        if not date_str:
            return None
        try:
            return parser.isoparse(date_str).astimezone(pytz.timezone('UTC'))
        except (TypeError, ValueError) as e:
            print(f"Error parsing date {date_str}: {str(e)}")
            return None

    def query(self, jql_query: str = None) -> str:
        self.connect()
        
        if not jql_query is None and len(jql_query) > 0:
            jql_query = f'project = {self.project_key} AND {jql_query}'
        
        # Get all tickets matching the query
        tickets = self.jira_connection.search_issues(
            jql_query, 
            maxResults = 500,
        )
        
        return tickets
    
    def query_tickets(self, jql_query: str) -> str:
        # Get project information
        # project = self.jira_connection.project(self.project_key)
        # print(f"\nProject: {project.name} (Key: {project.key})")

        # JQL query to get Epics and Stories from the project
        jql_query = f'project = {self.project_key} AND (parent=SM-109 or parent = SM-55) ORDER BY component ASC'
        
        # Get all issues matching the query
        issues = self.jira_connection.search_issues(
            jql_query, 
            maxResults = 500,
            expand = 'changelog'
        )
        
        return self.process_issues(issues)
    
    def connect(self):
        if self.connected:
            return
        try:
            # Connect to Jira Cloud
            self.jira_connection = JIRA(
                server=os.getenv("JIRA_SERVER"),
                basic_auth=(
                    os.getenv("JIRA_USER"), 
                    os.getenv("JIRA_TOKEN")
                )
            )

            print("Successfully connected to Jira!")
            self.connected = True

        except JIRAError as e:
            print(f"Jira Error: {e.status_code} {e.text}")

        except Exception as e:
            print(f"Error: {str(e)}")

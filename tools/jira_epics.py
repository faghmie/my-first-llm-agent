if __name__ == "__main__":
    from jira_project import JiraProject
else:
    from tools.jira_project import JiraProject

from datetime import datetime
from typing import List
from dataclasses import dataclass, asdict
import json

@dataclass
class EpicTicket:
    key: str = None
    component: str = None
    summary: str = None
    description: str = None
    status: str = None
    created_date: str = None
    due_date: str = None
    update_date: str = None
    current_date: str = None


def jira_epic_list_tool() -> List[EpicTicket]:

    """
    Retrieve the list of Epics/Features from the Jira project.

    Returns:
        list: A list of EpicTicket dataclass objects. Each object contains:
            - key
            - component 
            - summary
            - description 
            - status
            - created_date
            - due_date
            - update_date
            - current_date
    """
    jira_conn = JiraProject()

    # JQL query to get Epics and Stories from the project
    jql_query = f'type=Epic'
    
    # Get all issues matching the query
    issues = jira_conn.query(jql_query)
    
    return process_issues(jira_conn,issues)

def process_issues(jira_conn, issues) -> List[EpicTicket]:
    try:
        print(f"Found {len(issues)} issues:\n")
        
        response = []

        for issue in issues:
            # Get basic fields
            key = issue.key
            component = issue.fields.components[0].name if len(issue.fields.components) > 0 else None
            summary = issue.fields.summary
            description = issue.fields.description
            status = issue.fields.status.name
            issue_type = issue.fields.issuetype.name
            created_date = jira_conn.parse_jira_date(issue.fields.created)
            due_date = jira_conn.parse_jira_date(issue.fields.duedate)
            update_date = jira_conn.parse_jira_date(issue.fields.updated)
            
            response.append(json.dumps(asdict(EpicTicket(
                key = key, 
                component = component, 
                summary = summary, 
                description = description,
                status = status,
                created_date = created_date.strftime('%d %b %Y') if created_date else 'N/A',
                due_date = due_date.strftime('%d %b %Y') if due_date else 'N/A',
                update_date = update_date.strftime('%d %b %Y') if update_date else 'N/A',
                current_date = datetime.now().strftime('%d %b %Y'),
            ))))

        return response

    except Exception as e:
        print(f"Error: {str(e)}")    


if __name__ == "__main__":
    print(jira_epic_list_tool())
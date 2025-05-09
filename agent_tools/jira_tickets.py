if __name__ == "__main__":
    from jira_project import JiraProject
else:
    from tools.jira_project import JiraProject

from datetime import datetime, timedelta

import numpy as np
from typing import List
from dataclasses import dataclass, asdict
import json

@dataclass
class TicketData:
    key: str = None
    product_stage: str = None
    summary: str = None
    description: str = None
    status: str = None
    created_date: str = None
    complete_date: str = None
    start_date: str = None
    update_date: str = None
    current_date: str = None
    duration: str = None

    def __str__(self):
        return f"""{{
            "Key": "{self.key}"
            "Product Stage": "{self.product_stage}"
            "Summary": "{self.summary}"
            "Description": "{self.description}"
            "Status": "{self.status}"
            "Created Date": "{self.created_date}"
            "Complete Date": "{self.complete_date}"
            "Start Date": "{self.start_date}"
            "Duration": "{self.duration}"
        }}
        """

def jira_ticket_list_tool(epic_key: [str]) -> List[TicketData]:
    """        
    Retrieve a list of tickets associated with specific epic keys from the Jira project.

    Args:
        epic_key (list of str): A list of epic keys for which to retrieve associated tickets.

    Returns:
        List[TicketData]: A list of TicketData objects representing the tickets associated 
        with the specified epic keys, sorted by component. Each object contains:
            - key
            - product_stage
            - summary
            - description
            - status
            - created_date
            - complete_date
            - start_date
            - update_date
            - current_date
            - duration
    """
    if not epic_key:
        epic_key = "[*]"
    
    if not isinstance(epic_key, list):
        epic_key = [epic_key]
    
    jira_conn = JiraProject()

    # JQL query to get Epics and Stories from the project
    jql_query = f"""parent IN ({", ".join(epic_key)}) ORDER BY component ASC"""
    
    # Get all issues matching the query
    issues = jira_conn.query(jql_query)
    
    return process_issues(jira_conn, issues) # process issues

def process_issues(jira_conn, issues) -> List[TicketData]:
    # Custom field IDs - Update these for your instance (see instructions below)
    START_DATE_FIELD = 'customfield_10426'  # Typically 'Start Date'
    COMPLETION_DATE_FIELD = 'resolutiondate'  # Typically 'Resolved Date'

    try:
        print(f"Found {len(issues)} issues:\n")
        
        response = []

        for issue in issues:
            # Get basic fields
            key = issue.key
            component = issue.fields.components[0].name if len(issue.fields.components) > 0 else None
            summary = issue.fields.summary
            description = getattr(issue.fields, 'description', 'No description')
            status = issue.fields.status.name
            issue_type = issue.fields.issuetype.name
            
            # Get dates - handle missing fields
            start_date = jira_conn.parse_jira_date(getattr(issue.fields, START_DATE_FIELD, None))
            completion_date = jira_conn.parse_jira_date(getattr(issue.fields, COMPLETION_DATE_FIELD, None))
            update_date = jira_conn.parse_jira_date(getattr(issue.fields, "updated", None))

            # Calculate duration
            duration_info = calculate_work_duration(start_date, completion_date) if start_date and completion_date else None

            work_days = None
            if duration_info:
                work_days = int(duration_info['business_days'])

            response.append(json.dumps(asdict(TicketData(
                key = key, 
                product_stage = component, 
                summary = summary, 
                description = description, 
                status = status,
                start_date = start_date.strftime('%d %b %Y') if start_date else 'N/A',
                complete_date = completion_date.strftime('%d %b %Y') if work_days else 'N/A',
                update_date = update_date.strftime('%d %b %Y') if update_date else 'N/A',
                current_date = datetime.now().strftime('%d %b %Y'),
                duration = work_days if work_days else ''
            ))))

        return response

    except Exception as e:
        print(f"Error: {str(e)}")    

def calculate_work_duration(start_dt, end_dt):
    """Calculate working duration between two datetime objects"""

    if not start_dt or not end_dt:
        return None
        
    if start_dt > end_dt:
        return None  # Invalid date range
    
    # Calculate total duration
    total_duration = end_dt - start_dt
    
    # Calculate business hours duration (9 AM to 5 PM)
    start_workday = start_dt.replace(hour=9, minute=0, second=0)
    end_workday = start_dt.replace(hour=17, minute=0, second=0)
    
    # Calculate business days considering weekends
    business_days = np.busday_count(
        start_dt.date(),
        end_dt.date() + timedelta(days=1),  # Inclusive end date
        weekmask='1111100'  # Monday-Friday
    )
    
    return {
        'total_days': round(total_duration.total_seconds() / 86400, 2),
        'business_days': business_days,
        'exact_duration': total_duration,
        'start_datetime': start_dt.strftime('%d %b %Y'),
        'end_datetime': end_dt.strftime('%d %b %Y')
    }


if __name__ == "__main__":
    # print(str(jira_ticket_list_tool(['SM-109', 'SM-55'])))
    print(str(jira_ticket_list_tool('sm-109')))
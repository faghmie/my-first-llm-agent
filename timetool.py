import datetime
from zoneinfo import ZoneInfo
from tool import Tool

class TimeTool(Tool):
    def name(self):
        return "Time Tool"

    def description(self):
        return ("""Gives the current time for a given city's
         	    timezone like Europe/Lisbon, America/New_York etc. If no timezone is provided, it returns the local time.""")

    def use(self, *args, **kwargs):
        format = "%Y-%m-%d %H:%M:%S %Z%z"
        current_time = datetime.datetime.now()
        input_timezone = args[0] if args else None
        if input_timezone:
            try:
                current_time = current_time.astimezone(ZoneInfo(input_timezone))
            except Exception:
                return f"Invalid timezone: {input_timezone}"
        return f"The current time is {current_time.strftime(format)}."
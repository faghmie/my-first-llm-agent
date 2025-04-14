import datetime
from zoneinfo import ZoneInfo
from tools.tool import Tool

class TimeTool(Tool):
    def name(self):
        return "Time Tool"

    def description(self):
        return ("""Provides the current time for a given city. 
                - **Important**: 
                    - Only use this tool to get the current time.
                    - Do not use this tool to determine the timezone.
                    - Do not use this tool to convert timezones.
                - **Argument**: 
                    - User must supply a valid timezone in string format, for example: "Asia/Tokyo"
                - **Result**: 
                    - The current time for a city in the format: "YYYY-MM-DD HH:MM:SS +0000"
                    - If no timezone is provided, it returns the local time.
                """)

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
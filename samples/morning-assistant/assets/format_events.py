"""Example code for an explicit external test adapter; importing does not run it."""
def format_event(event):
    return f'{event["time"]}: {event["title"]} ({event["status"]})'

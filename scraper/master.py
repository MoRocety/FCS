from datetime import datetime
from time import sleep

while True:
    import scrape
    import parse
    # Get current time
    current_time = datetime.now()

    # Format current time in 12-hour format
    current_time = current_time.strftime("%I:%M %p")
    sleep(15)





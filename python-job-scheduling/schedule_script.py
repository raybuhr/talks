import schedule
import time
from my_cool_script import run_job

schedule.every().hour().do(run_job)

while True:
    schedule.run_pending()
    time.sleep(3600)

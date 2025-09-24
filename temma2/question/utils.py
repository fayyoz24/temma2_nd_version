from decouple import config
from temma.settings import DEBUG

one_time_link=config('ONE_TIME_LINK_FOR_MENOTRS')
if DEBUG:
    one_time_link="http://127.0.0.1:8000/api/question/one-time-link?token="

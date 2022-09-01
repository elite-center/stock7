import os
import os.path
from datetime import datetime

import functions_framework
import pandas as pd
import requests
from finlab import data
from genericpath import isfile
from loguru import logger

FINLAB_TOKEN = os.environ["FINLAB_TOKEN"]
TG_TOKEN = os.environ["TG_TOKEN"]


def fetch_conference() -> pd.DataFrame:
    cache_path = "temp/investors_conference.csv"
    if os.path.isfile(cache_path):
        info = pd.read_csv(cache_path)
    else:
        data.login(FINLAB_TOKEN)
        info = data.get("investors_conference")
        info.to_csv(cache_path)
    return info


def fetch_shareholders_meeting() -> pd.DataFrame:
    cache_path = "temp/shareholders_meeting.csv"
    if os.path.isfile(cache_path):
        info = pd.read_csv(cache_path)
    else:
        data.login(FINLAB_TOKEN)
        info = data.get("shareholders_meeting")
        info.to_csv(cache_path)
    return info


def format_conference_msg(companies: list, today: str) -> str:
    if companies:
        companies_str = "\n\n".join(
            f"[{company['公司名稱']}](https://www.google.com/search?q={company['公司名稱']}&tbm=nws&tbs=qdr:d) `{company['召開法人說明會地點']}`\n{company['法人說明會擇要訊息']}"
            for company in companies
        )
    else:
        companies_str = "系統發生問題，請參照[其他網站](https://goodinfo.tw/tw/StockHolderMeetingList.asp?MARKET_CAT=全部&INDUSTRY_CAT=全部&YEAR=近期召開"
    return f"{today} 法說會\n\n" + companies_str


def format_shareholders_meeting_msg(companies: list, today: str) -> str:
    if companies:
        companies_str = "\n\n".join(
            f"[{company['公司名稱']}](https://www.google.com/search?q={company['公司名稱']}&tbm=nws&tbs=qdr:d) `"
            for company in companies
        )
    else:
        companies_str = "今日無股東會召開"
    return f"{today} 股東會\n\n" + companies_str


def send_tg(msg: str):
    channel_id = "-1001213944924"
    params: dict = {
        "chat_id": channel_id,
        "text": msg,
        "parse_mode": "markdown",
        "disable_web_page_preview": True,
    }
    res = requests.get(
        f"https://api.telegram.org/{TG_TOKEN}/sendMessage", params=params
    )
    if res.status_code != 200:
        logger.error(res.text)


def process_conference():
    info = fetch_conference()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    info_today = info[info.date == today][["公司名稱", "召開法人說明會地點", "法人說明會擇要訊息"]].to_dict(
        "records"
    )
    msg = format_conference_msg(info_today, today)
    logger.debug(msg)
    send_tg(msg)


def process_shareholders_meeting():
    info = fetch_shareholders_meeting()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    info_today = info[info.date == today][["公司名稱"]].to_dict("records")
    msg = format_shareholders_meeting_msg(info_today, today)
    logger.debug(msg)
    send_tg(msg)


@functions_framework.http
def main(request):
    process_conference()
    process_shareholders_meeting()
    return "OK"

import json
from pprint import pprint

import requests

id = "863071389 (12417)"


def get_all_packs():
    url = f"https://api.mobapay.com/api/app_shop?app_id=100000&user_id=330192529&server_id=9216&country=RU&language=en&network=&net=JMRU&coupon_id=&shop_id="

    referer = "https://www.mobapay.com/"

    data = requests.get(url, headers={"Referer": referer}).json()

    my_list = data["data"]["shop_info"]["good_list"]
    return my_list


def get_user_id(user: str):
    try:
        user_id = user.split(" ")[0]
        user_server = user.split(" ")[1].replace("(", "").replace(")", "")

        url = f"https://api.mobapay.com/api/app_shop?app_id=100000&user_id={user_id}&server_id={user_server}&country=RU&language=en&network=&net=JMRU&coupon_id=&shop_id="

        referer = "https://www.mobapay.com/"

        data = requests.get(url, headers={"Referer": referer}).json()

        user = data["data"]["user_info"]["user_name"]
        return user
    except:
        return False


def create_payment(user, price, mail):
    packs = get_all_packs()
    good = [
        i
        for i in packs
        if i["pay_channel_sub"][0]["price_local_sell_precision"] == price
    ][0]

    user_id = user.split(" ")[0]
    user_server = user.split(" ")[1].replace("(", "").replace(")", "")

    price = float(good["pay_channel_sub"][0]["price_local_sell_precision"])
    url = "https://api.mobapay.com/pay/order"
    payload = {
        "app_id": 100000,
        "user_id": int(user_id),
        "server_id": int(user_server),
        "email": mail,
        "shop_id": 1001,
        "amount_pay": int(price * 100),
        "currency_code": "RUB",
        "country_code": "RU",
        "goods_id": good["id"],
        "num": 1,
        "pay_channel_sub_id": 123471,
        "price_pay": int(price * 100),
        "lang": "en",
        "network": "",
        "net": "JMRU",
        "terminal_type": "WEB",
    }
    pprint(payload)
    referer = "https://www.mobapay.com/"
    data = requests.post(url, headers={"Referer": referer}, data=json.dumps(payload))
    print(data.status_code)
    return data.json(), good["id"]


def create_link(id: int):
    url = "https://api.mobapay.com/pay/order/payment"
    payload = {
        "net": "JMRU",
        "network": "",
        "order_id": f"{id}",
        "return_url": "https://www.mobapay.com/order?appid=100000&net=JMRU&order=1858129350722400256&r=RU",
        "terminal_type": "WEB",
    }
    referer = "https://www.mobapay.com/"
    data = requests.post(
        url, headers={"Referer": referer}, data=json.dumps(payload)
    ).json()
    return data

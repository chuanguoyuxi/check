# -*- coding: utf-8 -*-
"""
cron: 30 8 * * *
new Env('ikuuu');
"""
import json
import requests
from utils import check


class Ikuuu:
    name = "iKuuu"

    def __init__(self, check_item):
        self.check_item = check_item

    @staticmethod
    def login(baseUrl, name, email, passwd):
        try:
            url = baseUrl + "/auth/login"
            headers = {
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": "lang=zh-cn",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
            }
            session = requests.Session()
            response = session.post(
                url=url, data={"email": email, "passwd": passwd}, headers=headers
            )
            # content-type: text/html; charset=UTF-8
            print("response", response.json(), response.status_code)
            msg = name + json.loads(response.text)["msg"]

            cookies_dict = requests.utils.dict_from_cookiejar(session.cookies)
            cookie = "lang=zh-cn; " + "; ".join(
                [str(x) + "=" + str(y) for x, y in cookies_dict.items()]
            )

        except Exception as e:
            print("错误信息", str(e))
            msg = f"{name}登录失败，检查日志"
            cookie = ""
        msg = {"name": "帐号信息", "value": msg}
        return msg, cookie

    @staticmethod
    def checkin(baseUrl, cookie):
        try:
            url = baseUrl + "/user/checkin"
            headers = {
                "cookie": cookie,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
            }
            response = requests.post(url=url, headers=headers)
            print("response", cookie, response.json(), response.status_code)
            msg = json.loads(response.text)["msg"]

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "签到信息", "value": msg}
        return msg

    def main(self):
        baseUrl = self.check_item.get("baseUrl")
        name = self.check_item.get("name")
        email = self.check_item.get("email")
        passwd = self.check_item.get("passwd")
        login_msg, cookie = self.login(
            baseUrl=baseUrl, name=name, email=email, passwd=passwd
        )
        checkin_msg = self.checkin(baseUrl=baseUrl, cookie=cookie)
        msg = [login_msg, checkin_msg]
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


@check(run_script_name="iKuuu", run_script_expression="IKUUU")
def main(*args, **kwargs):
    return Ikuuu(check_item=kwargs.get("value")).main()


if __name__ == "__main__":
    main()

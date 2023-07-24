# -*- coding: utf-8 -*-
"""
cron: 30 8 * * *
new Env('阿里云盘');
"""

import requests
from utils import check


class Aliyundrive:
    name = "Aliyundrive"

    def __init__(self, check_item):
        self.check_item = check_item

    # 使用 refresh_token 更新 access_token
    @staticmethod
    def updateAccesssToken(self, refresh_token):
        try:
            url = "https://auth.aliyundrive.com/v2/account/token"
            headers = {"Content-Type": "application/json"}
            json = {"grant_type": "refresh_token", "refresh_token": refresh_token}
            response = requests.post(url=url, json=json, headers=headers)
            print("updateAccesssToken", response.json())

            code = response.json().get("code")
            message = response.json().get("message")
            if code:
                if code in ["RefreshTokenExpired", "InvalidParameter.RefreshToken"]:
                    msg = "refresh_token 已过期或无效"
                else:
                    msg = message
            else:
                access_token = response.json().get("access_token")
                new_refresh_token = response.json().get("refresh_token")
                nick_name = response.json().get("nick_name")
                msg = f"{nick_name}·欢迎登录"

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "更新用户token", "value": msg}
        return msg, access_token

    # 签到
    @staticmethod
    def signInList(access_token):
        try:
            url = "https://member.aliyundrive.com/v1/activity/sign_in_list"
            params = {"_rx-s": "mobile"}
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            json = {"isReward": False}
            response = requests.post(url=url, params=params, json=json, headers=headers)
            print("signInList", response.json())

            success = response.json().get("success")
            code = response.json().get("code")
            message = response.json().get("message")
            if success:
                signInCount = response.json().get("result").get("signInCount")
                signInLogs = response.json().get("result").get("signInLogs")
                msg = f"签到成功,本月累计签到 {signInCount} 天"
            else:
                msg = f"签到失败,{message}"

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "签到信息", "value": msg}
        return msg, signInCount

    # 领取奖励
    @staticmethod
    def signInReward(access_token, signInDay):
        try:
            url = "https://member.aliyundrive.com/v1/activity/sign_in_reward"
            params = {"_rx-s": "mobile"}
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            json = {"signInDay": signInDay}
            response = requests.post(url=url, params=params, json=json, headers=headers)
            print("getReward", response.json())

            if not response.json().get("result"):
                msg = "无奖励"
            else:
                name = response.json().get("result").get("name")
                description = response.json().get("result").get("description")
                msg = f"今日签到获得,{name}·{description}"

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "领取奖励", "value": msg}
        return msg

    def main(self):
        refresh_token = self.check_item.get("refresh_token")
        msg = []

        updateAccesssToken_msg, access_token = self.updateAccesssToken(
            self, refresh_token=refresh_token
        )  # 使用 refresh_token 更新 access_token
        msg.append(updateAccesssToken_msg)
        if access_token:
            signInList_msg, signInCount = self.signInList(
                access_token=access_token
            )  # 签到
            msg.append(signInList_msg)
            if signInCount:
                signInReward_msg = self.signInReward(
                    access_token=access_token, signInDay=signInCount
                )  # 获取奖励
                msg.append(signInReward_msg)

        print(msg)
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


@check(run_script_name="阿里云盘", run_script_expression="ALIYUNDRIVE")
def main(*args, **kwargs):
    return Aliyundrive(check_item=kwargs.get("value")).main()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
cron: 30 8 * * *
new Env('掘金');
"""

import requests
import random
from utils import check


class Juejin:
    name = "Juejin"

    def __init__(self, check_item):
        self.check_item = check_item

    # 获取用户信息
    @staticmethod
    def userGet(headers):
        try:
            url = "https://api.juejin.cn/user_api/v1/user/get"
            response = requests.get(url=url, headers=headers)
            # content-type: application/json; charset=utf-8
            print("userGet", response.json())

            data = response.json().get("data")
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            if err_no == 0:
                msg = f"掘友-{data.get('user_name')}"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "获取用户信息", "value": msg}
        return msg

    # 查询签到
    @staticmethod
    def getTodayStatus(headers):
        try:
            url = "https://api.juejin.cn/growth_api/v2/get_today_status"
            response = requests.get(url=url, headers=headers)

            print("getTodayStatus", response.json())

            data = response.json().get("data")
            # check_in_done 今天是否签到
            check_in_done = data.get("check_in_done")
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            if err_no == 0:
                if check_in_done:
                    msg = "今天已经签到"
                else:
                    msg = "今天还未签到，正在进行签到"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
            check_in_done = False
        msg = {"name": "查询今天是否签到", "value": msg}
        return msg, check_in_done

    # 签到
    @staticmethod
    def checkIn(headers):
        try:
            url = "https://api.juejin.cn/growth_api/v1/check_in"
            response = requests.post(url=url, headers=headers)

            print("checkIn", response.json())

            data = response.json().get("data")
            incr_point = data.get("incr_point")
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            # incr_point 签到获得矿石
            # sum_point 账户累计矿石
            if err_no == 0:
                # msg = f"签到成功，今日签到获得{data.get('incr_point')}矿石，当前累计{data.get('sum_point')}矿石"
                msg = f"签到成功 +{incr_point} 矿石"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "签到信息", "value": msg}
        return msg

    # 查询签到天数
    @staticmethod
    def getCounts(headers):
        try:
            url = "https://api.juejin.cn/growth_api/v1/get_counts"
            response = requests.get(url=url, headers=headers)

            print("getCounts", response.json())

            data = response.json().get("data")
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            # cont_count 连续签到天数
            # sum_count 总签到天数
            if err_no == 0:
                msg = f"连续签到{data.get('cont_count')}天，总签到{data.get('sum_count')}天"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "查询签到天数", "value": msg}
        return msg

    # 查询当前矿石
    @staticmethod
    def getCurPoint(headers):
        try:
            url = "https://api.juejin.cn/growth_api/v1/get_cur_point"
            response = requests.get(url=url, headers=headers)

            print("getCurPoint", response.json())

            data = response.json().get("data")
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            if err_no == 0:
                msg = f"当前累计{data}矿石"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "查询当前累计矿石", "value": msg}
        return msg

    # 查询抽奖
    @staticmethod
    def lotteryConfigGet(headers):
        try:
            url = "https://api.juejin.cn/growth_api/v1/lottery_config/get"
            response = requests.get(url=url, headers=headers)

            print("lotteryConfigGet", response.json())

            data = response.json().get("data")
            # free_count 免费次数
            free_count = data.get("free_count")
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            if err_no == 0:
                msg = f"免费抽奖次数{free_count}次"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
            free_count = 0
        msg = {"name": "查询抽奖", "value": msg}
        return msg, free_count

    # 抽奖
    @staticmethod
    def lotteryDraw(headers):
        try:
            url = "https://api.juejin.cn/growth_api/v1/lottery/draw"
            response = requests.post(url=url, headers=headers)

            print("lotteryDraw", response.json())

            data = response.json().get("data")
            lottery_name = data.get("lottery_name")
            draw_lucky_value = data.get("draw_lucky_value")
            total_lucky_value = data.get("total_lucky_value")
            # 奖品 lottery_name
            # 抽奖行为增加幸运值 draw_lucky_value
            # 幸运值 total_lucky_value
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            if err_no == 0:
                # msg = f"抽中奖品：{data.get('lottery_name')}，当前幸运值：{data.get('total_lucky_value')}"
                msg = f"恭喜抽中{lottery_name}，本次抽奖行为增加幸运值{draw_lucky_value}，当前幸运值为{total_lucky_value}"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
        msg = {"name": "抽奖信息", "value": msg}
        return msg

    # 获取沾喜气列表用户
    @staticmethod
    def lotteryHistoryGlobalBig(headers):
        try:
            url = "https://api.juejin.cn/growth_api/v1/lottery_history/global_big"
            response = requests.post(
                url=url, data={"page_no": 1, "page_size": 25}, headers=headers
            )

            print("lotteryHistoryGlobalBig", response.json())

            data = response.json().get("data")
            # lotteries 沾喜气列表用户
            lotteries = data.get("lotteries")
            # 随机获取一名幸运用户
            history_id = random.choice(lotteries).get("history_id")
            user_name = random.choice(lotteries).get("user_name")
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            if err_no == 0:
                msg = f"随机获取沾喜气用户-{user_name}"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
            history_id = ""
        msg = {"name": "获取沾喜气列表用户", "value": msg}
        return msg, history_id

    # 沾喜气
    @staticmethod
    def lotteryLuckyDipLucky(headers, history_id):
        try:
            url = "https://api.juejin.cn/growth_api/v1/lottery_lucky/dip_lucky"
            response = requests.post(
                url=url,
                data={"lottery_history_id": history_id},
                headers=headers,
            )

            print("lotteryLuckyDipLucky", response.json())

            data = response.json().get("data")
            dip_value = data.get("dip_value")
            has_dip = data.get("has_dip")
            total_value = data.get("total_value")
            # dip_value 粘的喜气
            # has_dip 是否已粘
            # total_value 当前幸运值
            err_msg = response.json().get("err_msg")
            err_no = response.json().get("err_no")
            if err_no == 0:
                if has_dip == False:
                    msg = f"沾得喜气{dip_value}点，当前幸运值{total_value}"
                else:
                    msg = "今天你已经沾过喜气，明天再来吧！"
            else:
                msg = err_msg

        except Exception as e:
            print("错误信息", str(e))
            msg = "未知错误，检查日志"
            dip_value = True
        msg = {"name": "沾喜气", "value": msg}
        return msg, dip_value

    def main(self):
        cookie = self.check_item.get("cookie")
        headers = {"cookie": cookie}
        msg = []

        userGet_msg = self.userGet(headers=headers)  # 获取用户信息
        msg.append(userGet_msg)
        getTodayStatus_msg, check_in_done = self.getTodayStatus(
            headers=headers
        )  # 查询今天是否签到
        msg.append(getTodayStatus_msg)
        if check_in_done == False:
            check_msg = self.checkIn(headers=headers)  # 签到
            msg.append(check_msg)
        getCounts_msg = self.getCounts(headers=headers)  # 查询签到天数
        msg.append(getCounts_msg)

        lotteryHistoryGlobalBig_msg, history_id = self.lotteryHistoryGlobalBig(
            headers=headers
        )  # 获取沾喜气列表用户
        msg.append(lotteryHistoryGlobalBig_msg)
        lotteryLuckyDipLucky_msg, dip_value = self.lotteryLuckyDipLucky(
            headers=headers, history_id=history_id
        )  # 沾喜气
        msg.append(lotteryLuckyDipLucky_msg)

        lotteryConfigGet_msg, free_count = self.lotteryConfigGet(
            headers=headers
        )  # 查询抽奖
        msg.append(lotteryConfigGet_msg)
        lotteryDraw_msg_list = []
        if free_count > 0:
            i = 0
            while i < free_count:
                lotteryDraw_msg = self.lotteryDraw(headers=headers)  # 抽奖
                lotteryDraw_msg_list.append(lotteryDraw_msg)
                i += 1
        msg = msg + lotteryDraw_msg_list

        getCurPoint_msg = self.getCurPoint(headers=headers)  # 查询当前矿石
        msg.append(getCurPoint_msg)

        # msg = (
        #     [
        #         userGet_msg,
        #         getTodayStatus_msg,
        #         getCounts_msg,
        #         getCurPoint_msg,
        #         lotteryConfigGet_msg,
        #     ]
        #     + lotteryDraw_msg_list
        #     + [lotteryHistoryGlobalBig_msg, lotteryLuckyDipLucky_msg]
        # )
        print(msg)
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


@check(run_script_name="掘金", run_script_expression="JUEJIN")
def main(*args, **kwargs):
    return Juejin(check_item=kwargs.get("value")).main()


if __name__ == "__main__":
    main()

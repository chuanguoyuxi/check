# -*- coding: utf-8 -*-
"""
cron: 30 8 * * *
new Env('掘金');
"""

import requests
import random
from utils import check

import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import cv2
import numpy as np


class Juejin:
    name = "Juejin"

    def __init__(self, check_item):
        self.check_item = check_item

    # 登录
    def login(self, username, password):
        try:
            login_button = self.driver.find_element(By.CLASS_NAME, "login-button")
            print("login_button", login_button)

            ActionChains(self.driver).move_to_element(login_button).click().perform()

            time.sleep(5)

            other_login_span = self.driver.find_element(By.CLASS_NAME, "clickable")
            print("other_login_span", other_login_span)

            ActionChains(self.driver).move_to_element(
                other_login_span
            ).click().perform()

            username_input = self.driver.find_element(
                By.XPATH, '//input[@name="loginPhoneOrEmail"]'
            )
            print("username_input", username_input)
            password_input = self.driver.find_element(
                By.XPATH, '//input[@name="loginPassword"]'
            )
            print("password_input", password_input)

            # 保护用户名密码
            self.driver.execute_script(
                "arguments[0].type = 'password';", username_input
            )
            username_input.send_keys(username)
            password_input.send_keys(password)

            login_button = self.driver.find_element(
                By.CSS_SELECTOR, ".panel>button.btn"
            )
            print("login_button", login_button)
            ActionChains(self.driver).move_to_element(login_button).click().perform()
            # print("self.retry", self.retry)

        except Exception as e:
            self.driver.save_screenshot("prepare_login.png")
            raise Exception("Prepare login is error" + str(e))

        flag = False
        for retry in range(self.retry):
            self.get_cookies()
            try:
                avatar = self.driver.find_element(
                    By.CSS_SELECTOR, ".avatar-wrapper>img"
                )
                print("avatar", avatar)
                if avatar:
                    flag = True
                    break
            except NoSuchElementException:
                pass

        if flag is False:
            raise Exception(f"Verify slide image error and retry {self.retry}! ")
        print("get_cookies", self.driver.get_cookies())
        return self.driver.get_cookies()

    def get_cookies(self):
        slider_url, background_url = self.get_verify_image_url()
        print("get_verify_image_url", slider_url, background_url)
        result = self.get_track(self, slider_url, background_url)
        print("result", result)
        self.click_and_move(result)

    def get_verify_image_url(self):
        # 获取验证图片
        verify_image1 = self.driver.find_element(
            By.CSS_SELECTOR, ".captcha_verify_img_slide"
        )
        print("verify_image1", verify_image1)
        verify_image2 = self.driver.find_element(By.ID, "captcha-verify-image")
        print("verify_image2", verify_image2)

        verify_image1_src = verify_image1.get_attribute("src")
        verify_image2_src = verify_image2.get_attribute("src")
        self.driver.save_screenshot("temp/verify_image.png")
        print("get_verify_image_url", verify_image1_src, verify_image2_src)
        return verify_image1_src, verify_image2_src

    @staticmethod
    def get_track(self, slider_url, background_url) -> list:
        print("get_track", slider_url, background_url)
        distance = self.get_slide_distance(slider_url, background_url)
        print("distance", distance)
        result = self.gen_normal_track(distance)
        print("result", result)
        return result

    def get_slide_distance(self, slider_url, background_url):
        print("get_slide_distance", slider_url, background_url)
        # 下载验证码背景图,滑动图片
        self.onload_save_img(slider_url, self.slider)
        self.onload_save_img(background_url, self.background)
        print("下载验证码背景图,滑动图片", self.slider, self.background)
        # 读取进行色度图片，转换为numpy中的数组类型数据，
        slider_pic = cv2.imread(self.slider, 0)
        print("读取进行色度图片，转换为numpy中的数组类型数据", slider_pic)
        background_pic = cv2.imread(self.background, 0)
        print("读取进行色度图片，转换为numpy中的数组类型数据", background_pic)
        # 获取缺口图数组的形状 -->缺口图的宽和高
        width, height = slider_pic.shape[::-1]

        cv2.imwrite("background_bak.png", background_pic)
        cv2.imwrite("slider_bak.png", slider_pic)
        # 读取另存的滑块图
        slider_pic = cv2.imread("slider_bak.png")
        print("读取另存的滑块图", slider_pic)
        # 进行色彩转换
        slider_pic = cv2.cvtColor(slider_pic, cv2.COLOR_BGR2GRAY)
        print("进行色彩转换", slider_pic)
        # 获取色差的绝对值
        slider_pic = abs(255 - slider_pic)
        print("获取色差的绝对值", slider_pic)
        # 保存图片
        cv2.imwrite("slider_bak.png", slider_pic)
        # 读取滑块
        slider_pic = cv2.imread("slider_bak.png")
        print("读取滑块", slider_pic)
        # 读取背景图
        background_pic = cv2.imread("background_bak.png")
        print("读取背景图", background_pic)
        # 比较两张图的重叠区域
        result = cv2.matchTemplate(slider_pic, background_pic, cv2.TM_CCOEFF_NORMED)
        print("比较两张图的重叠区域", result)
        # 获取图片的缺口位置
        top, left = np.unravel_index(result.argmax(), result.shape)
        print("获取图片的缺口位置", top, left)
        # 背景图中的图片缺口坐标位置
        print("当前滑块的缺口位置：", (left, top, left + width, top + height))
        return left * 340 / 552

    @staticmethod
    def onload_save_img(slider_url, slider):
        print("onload_save_img", slider_url, slider)
        response = requests.get(slider_url)
        with open(slider, "wb") as f:
            f.write(response.content)

    @staticmethod
    def gen_normal_track(distance):
        print("gen_normal_track", distance)

        def norm_fun(x, mu, sigma):
            pdf = np.exp(-((x - mu) ** 2) / (2 * sigma**2)) / (
                sigma * np.sqrt(2 * np.pi)
            )
            return pdf

        result = []
        for i in range(-10, 10, 1):
            result.append(norm_fun(i, 0, 1) * distance)
        result.append(sum(result) - distance)
        return result

    def click_and_move(self, slide_track):
        print("click_and_move", slide_track)
        verify_div = self.driver.find_element(
            By.XPATH, '//div[@class="sc-kkGfuU bujTgx"]'
        )
        print("verify_div", verify_div)

        # 按下鼠标左键
        ActionChains(self.driver).click_and_hold(verify_div).perform()
        # 遍历轨迹进行滑动
        for t in slide_track:
            ActionChains(self.driver).move_by_offset(xoffset=t, yoffset=0).perform()
        # 释放鼠标
        time.sleep(0.2)
        ActionChains(self.driver).release(on_element=verify_div).perform()
        time.sleep(random.randint(2, 5))

    # @staticmethod
    # def gen_track(distance):  # distance为传入的总距离
    #     # 移动轨迹
    #     result = []
    #     # 当前位移
    #     current = 0
    #     # 减速阈值
    #     mid = distance * 4 / 5
    #     # 计算间隔
    #     t = 0.2
    #     # 初速度
    #     v = 1

    #     while current < distance:
    #         if current < mid:
    #             # 加速度为2
    #             a = 4
    #         else:
    #             # 加速度为-2
    #             a = -3
    #         v0 = v
    #         # 当前速度
    #         v = v0 + a * t
    #         # 移动距离
    #         move = v0 * t + 1 / 2 * a * t * t
    #         # 当前位移
    #         current += move
    #         # 加入轨迹
    #         result.append(round(move))
    #     return result

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
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/google-chrome"
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            executable_path="/usr/bin/chromedriver", options=chrome_options
        )
        self.driver.implicitly_wait(10)
        self.driver.delete_all_cookies()
        self.driver.get("https://juejin.cn")

        self.retry = 10  # 重试
        self.slider = "slider.png"
        self.background = "background.jpeg"

        msg = []
        username = self.check_item.get("username")
        password = self.check_item.get("password")
        cookies = self.login(username=username, password=password)  # 登录
        print("login", cookies)

        print("========================================================")
        cookie_list = [item["name"] + "=" + item["value"] for item in cookies]
        print("cookie_list", cookie_list)
        cookie = ";".join(item for item in cookie_list)
        print("cookie", cookie)

        headers = {"cookie": cookie}
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

        print(msg)
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


@check(run_script_name="掘金账户密码", run_script_expression="JUEJIN")
def main(*args, **kwargs):
    return Juejin(check_item=kwargs.get("value")).main()


if __name__ == "__main__":
    main()

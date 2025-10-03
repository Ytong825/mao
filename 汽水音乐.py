#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汽水音乐 Cookie 直登版
author: 青龙社区
date  : 2025-08-10
"""

import sys, time, requests

try:
    from loguru import logger
except ImportError:
    import logging as logger
    logger.basicConfig(level="INFO", format="%(message)s")

# ======================
# 把下面整段 Cookie 换成你浏览器抓到的
COOKIE = (
    "uid=18888888888; "
    "token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx; "
    "session_id=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
)
# ======================

BASE = "https://music-api.douyin.com"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

s = requests.Session()
s.headers.update({
    "User-Agent": UA,
    "Cookie": COOKIE,
    "Referer": "https://music.douyin.com/"
})

def task(name: str, path: str, times: int = 1):
    for i in range(1, times + 1):
        try:
            r = s.post(f"{BASE}{path}", timeout=10).json()
            if str(r.get("code")) in {"0", "1000"}:
                logger.info(f"✅ {name} {i}/{times}")
            else:
                logger.warning(f"⚠️ {name} {i}/{times} 失败：{r}")
                break
        except Exception as e:
            logger.error(f"❌ {name} {i}/{times} 异常：{e}")
            break
        time.sleep(2)

if __name__ == "__main__":
    task("签到",     "/task/signIn")
    task("签到广告", "/task/watchAd")
    task("免费听",   "/ad/awardFreeListen", 2)
    task("福利广告", "/ad/watchBonusAd", 10)
    task("翻卡",     "/activity/flipCard", 3)
    task("红包雨",   "/activity/redPacketRain", 5)
    logger.info("全部完成")

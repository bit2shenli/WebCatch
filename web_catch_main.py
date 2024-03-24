# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  IDE         : PyCharm
  File Name   : main
  Description : 启动程序
  Author      : chenyushencc@gmail.com
  date        : 2024/3/13 10:31
-------------------------------------------------
"""
import asyncio
import logging

from my_logging import LoggerWriter
from web_catch import get_website_content, check_update, test_email


# TODO 链接和 class 配置
link_class = [
    # 国防科技大学 985
    # {
    #     "name": "国防科技大学官网-通知公告",
    #     "url": "http://yjszs.nudt.edu.cn/index/index.view",
    #     "class": "tzgg"
    # },
    # {
    #     "name": "国防科技大学官网-院所发文",
    #     "url": "http://yjszs.nudt.edu.cn/index/index.view",
    #     "class": "kswd zcfg fr"
    # },
    # {
    #     "name": "国防科技大学官网-首页模块",
    #     "url": "http://yjszs.nudt.edu.cn/index/index.view",
    #     "class": "zcfg fl"
    # },
    # {
    #     "name": "研招网-国防科技大学",
    #     "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368388.dhtml",
    #     "class": "left"
    # },

    # 广西大学 211
    {
        "name": "官网-广西大学",
        "url": "https://yjsc.gxu.edu.cn/tzgg.htm",
        "class": "pull-right list-right"
    },
    {
        "name": "官网-广西大学（机械工程学院）",
        "url": "https://me.gxu.edu.cn/index/tzgg.htm",
        "class": "winstyle208044"
    },
    {
        "name": "研招网-广西大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368436.dhtml",
        "class": "left"
    },


    # 新疆大学 211
    {
        "name": "新疆大学-官网",
        "url": "https://gs.xju.edu.cn/index/tzgg.htm",
        "class": "main"
    },
    {
        "name": "官网-新疆大学-计算机科学与技术学院（网络空间安全学院）",
        "url": "https://it.xju.edu.cn/xwtz/ggtz.htm",
        "class": "left"
    },
    {
        "name": "官网-新疆大学-智能科学与技术学院（未来技术学院）",
        "url": "https://wljs.xju.edu.cn/index/tzgg.htm",
        "class": "winstyle233985"
    },
    {
        "name": "研招网-新疆大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368613.dhtml",
        "class": "left"
    },

    # 云南大学 211
    {
        "name": "官网-云南大学",
        "url": "http://www.grs.ynu.edu.cn/zytz.htm",
        "class": ""     # 该网页监控元素没有用 class
    },
    {
        "name": "官网-云南大学-信息学院",
        "url": "http://www.ise.ynu.edu.cn/annunciations/?kw=",
        "class": "row inner"
    },
    {
        "name": "官网-云南大学-软件学院",
        "url": "http://www.sei.ynu.edu.cn/xwgg/tzgg.htm",
        "class": "class-col1"
    },


    # 河北工业大学 211
    {
        "name": "研招网-河北工业大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-367972.dhtml",
        "class": "left"
    },
    {
        "name": "河北工业大学-官网",        # TODO 无法获取
        "url": "https://yjs.hebut.edu.cn/zsgz/zsgztzgg/index.htm",
        "class": "t_list_main_2"
    },


    # 空军军医大学 211
    # {
    #     "name": "空军军医大学-官网-院系通知",
    #     "url": "https://www.fmmu.edu.cn/tongzhi/yxtz/yjsy1.htm",
    #     "class": "jgtz"
    # },
    # {
    #     "name": "研招网-空军军医大学",
    #     "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368546.dhtml",
    #     "class": "left"
    # },

    # 合肥工业大学 211
    {
        "name": "合肥工业大学-官网",
        "url": "https://yjszs.hfut.edu.cn/",
        "class": "list-box fl"
    },
    {
        "name": "研招网-合肥工业大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368238.dhtml",
        "class": "left"
    },

    # 西南大学 211 重庆
    {
        "name": "西南大学-官网-最新动态",
        "url": "http://yz.swu.edu.cn/s/yanzhao/",
        "class": "index-2-2 col-right"
    },
    {
        "name": "研招网-西南大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368457.dhtml",
        "class": "left"
    },

    # 中国矿业大学(北京) 211
    {
        "name": "中国矿业大学-官网-硕士招生",
        "url": "https://yz.cumt.edu.cn/index/sszs.htm",
        "class": "ny_right"
    },
    {
        "name": "研招网-中国矿业大学(北京)",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-367923.dhtml",
        "class": "left"
    },
    {
        "name": "研招网-中国矿业大学(苏州)",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368184.dhtml",
        "class": "left"
    },

    # 江南大学 211
    {
        "name": "江南大学-官网-最新通知",
        "url": "https://yz.jiangnan.edu.cn/zxtz2.htm",
        "class": "list_content"
    },
    {
        "name": "研招网-江南大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368189.dhtml",
        "class": "left"
    },


    # 南京农业大学 211
    {
        "name": "南京农业大学-官方",
        "url": "https://zsgz.njau.edu.cn/zsxx/sszs/sszxtz.htm",
        "class": "pull-right list-right"
    },
    {
        "name": "研招网-南京农业大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368198.dhtml",
        "class": "left"
    },

    # 湖南科技大学
    {
        "name": "研招网-湖南科技大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368379.dhtml",
        "class": "left"
    },
    {
        "name": "研招网-湖南科技大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368379.dhtml",
        "class": "left"
    },



    # 信息工程大学
    {
        "name": "研招网-信息工程大学(河南郑州)",
        "url": "https://yz.chsi.com.cn/sch/listBulletin--schId-368312,categoryId-462794,mindex-10.dhtml",
        "class": "container"           # 调剂 class
    },

    # 空军工程大学
    {
        "name": "空军工程大学-官网",
        "url": "https://www.afeu.cn:1001/notice-announcement/",
        "class": "article-list"           # 调剂 class
    },

    {
        "name": "研招网-空军工程大学",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368547.dhtml",
        "class": "yxk-column-con"           # 调剂 class
    },


    # 研究所，信息主要来源 = 研招网 + 微信公众号 + 官网
    # 武汉邮电科学研究院
    {
        "name": "研招网-武汉邮电科学研究院 + 关注公众号",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368331.dhtml",
        "class": "left"  # 调剂 class
    },

    # 中国兵器科学研究院(西南自动化研究所)
    {
        "name": "研招网-中国兵器科学研究院(西南自动化研究所) + 关注公众号",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368469.dhtml",
        "class": "left"  # 调剂 class
    },

    # 西安微电子技术研究所
    {
        "name": "研招网-西安微电子技术研究所",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368539.dhtml",
        "class": "left"  # 调剂 class
    },

    # 研究院-中国地震局地震研究所
    {
        "name": "研招网-中国地震局地震研究所",
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368329.dhtml",
        "class": "left"  # 调剂 class
    },
    {
        "name": "中国地震局地震研究所-官网",
        "url": "https://www.ief.ac.cn/zstext/index.html",
        "class": "secondarybox"  # 调剂 class
    },

    # 51考研网，调剂信息 B区 x10
    {
        "name": "工学-新疆B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616751_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-宁夏B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616752_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-青海B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616753_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-甘肃B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616754_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-西藏B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616755_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-云南B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616756_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-贵州B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616757_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-海南B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616758_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-广西B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616760_1.html",
        "class": "MoBody"
    },
    {
        "name": "工学-内蒙古B区",
        "url": "https://www.51kywang.com/51kaoyanwang/vip_doc/27040148_5615798_5616761_1.html",
        "class": "MoBody"
    },




    # test
    {
        "name": "CSDN-头条",
        "url": "https://www.csdn.net/",
        "class": "headlines-right"
    },
]


async def main():
    tasks = []
    # 创建一个定时发送官方邮件的 test 邮件
    task = asyncio.create_task(test_email())
    tasks.append(task)

    # 创建任务并启动多个协程
    for key, value in enumerate(link_class):
        # print(key, value, value["name"], value["url"], value["class"])
        name, url, catch_class = value["name"], value["url"], value["class"]
        content = get_website_content(url, catch_class)
        if content:
            task = asyncio.create_task(check_update(name, url, catch_class, content))
            tasks.append(task)

        else:
            print(f"{name} 无法获取网站内容 {url}")

    for task in tasks:
        await task


if __name__ == "__main__":
    # 将 sys.stdout 和 sys.stderr 重定向到日志记录器
    """ 将 print 打印成日志，需要本地打印时，注释掉 """
    import sys
    sys.stdout = LoggerWriter(logging.INFO)
    sys.stderr = LoggerWriter(logging.ERROR)
    """ 将 print 打印成日志，需要本地打印时，注释掉 """

    # 运行主协程
    asyncio.run(main())

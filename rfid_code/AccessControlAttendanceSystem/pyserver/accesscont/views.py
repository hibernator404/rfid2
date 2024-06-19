from accesscont import app
from flask import jsonify, request
from accesscont import db
from accesscont.models import userinfo, attendancetime
import time
import datetime
from sqlalchemy import func
import math
from datetime import date, timedelta
from datetime import datetime
import pyttsx3
from flask_cors import CORS

CORS(app)

@app.route('/')
def index():
    return 'hello!zyf'

# 定义键函数，返回字典中的 "name" 值
def get_name(item):
    return item["date"]

# 初始化 pyttsx3 引擎并定义函数
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    if engine._inLoop:
        engine.endLoop()
    engine.stop()

@app.route('/clockin', methods=["POST"])
def clockin():
    sth = request.json

    userid = sth['userid']
    print("用户id是" + str(userid))

    # 先判断是否是已录入用户
    res1 = userinfo.query.filter(userinfo.userid == userid).first()
    if not res1:
        errmsg = "无权进入！"
        # 调用语音函数
        speak(errmsg)
        return jsonify({"msg": errmsg, "tag": 0})
    else:
        res2 = attendancetime.query.filter(attendancetime.userid == userid, attendancetime.status == 0).first()
        # 找不到已上班打卡信息，则记录打卡
        if not res2:
            totime = int(time.time())
            current_timestamp = time.time()
            current_struct_time = time.localtime(current_timestamp)
            year = str(current_struct_time.tm_year)
            month = str(current_struct_time.tm_mon)
            day = str(current_struct_time.tm_mday)
            m1 = attendancetime(username=res1.username, userid=res1.userid, status=0, toworktimestamp=totime, createddate=year + '-' + month + '-' + day)
            db.session.add(m1)
            db.session.commit()
            toworkmsg =   "打卡人：" + res1.username + "上班打卡成功！"
            speak(toworkmsg)
            return jsonify({"msg": "上班打卡成功！", "tag": 1, "user": res1.username, "userid": res1.userid})
        # 存在上班打卡信息，则记录下班信息
        else:
            res2.status = 1
            res2.offworktimestamp = int(time.time())
            db.session.commit()
            # 统计本次出勤时间
            toworktime = int(res2.toworktimestamp)
            attendtime = res2.offworktimestamp - toworktime
            # 统计一个自然月出勤时间
            current_year = date.today().year
            current_month = date.today().month
            start_date = date(current_year, current_month, 1)
            end_date = start_date + timedelta(days=31)
            results = attendancetime.query.filter(
                func.extract('year', attendancetime.createddate) == current_year,
                func.extract('month', attendancetime.createddate) == current_month,
                attendancetime.createddate >= start_date,
                attendancetime.createddate < end_date,
            ).all()
            userres = []
            for x in results:
                if x.userid == userid:
                    userres.append(x)
            # 上面统计本人本月出勤记录
            daytotaltime = 0
            resultsnew = []
            analyres = []
            for x in userres:
                newdict = {"date": x.createddate, "clockintime": x.offworktimestamp - x.toworktimestamp}
                resultsnew.append(newdict)
            # 统计每次出勤时间
            attendtimetagarray = list({get_name(item): item for item in resultsnew}.values())
            # 去重，生成日期数组
            for x in attendtimetagarray:
                for y in resultsnew:
                    if x['date'] == y['date']:
                        daytotaltime += y["clockintime"]
                date_number = int(x['date'].strftime("%Y%m%d"))
                newdict = {date_number: daytotaltime}
                analyres.append(newdict)
                daytotaltime = 0
            # 统计每天出勤时间，生成日期对于时间的数组
            monthtotaltime = 0
            for x in analyres:
                values = x.values()
                for y in values:
                    monthtotaltime += y
            # 统计每个自然月总的出勤时间
            timelens = 1
            fakemonthtotaltime = monthtotaltime
            while fakemonthtotaltime > 9:
                fakemonthtotaltime = fakemonthtotaltime / 10
                timelens = timelens + 1
            actualvalue = int(timelens * math.pow(10, timelens) + monthtotaltime)
            # 设计第一位为总出勤时间的位数，第一位后为实际出勤时间
            hour = int(attendtime / 3600)
            minute = int((attendtime % 3600) / 60)
            second = int((attendtime % 3600) % 60)
            offworkmsg =  "打卡人：" + res1.username+"下班打卡成功！" + "本次出勤时间为：" + str(hour) + "小时，" + str(minute) + "分钟，" + str(second) + "秒。"
            print(offworkmsg)
            speak(offworkmsg)
            # 调用语音函数，进行播报
            return jsonify({"msg": "下班打卡成功！", "attendtime": attendtime, "tag": 2, "monthclockintime": actualvalue, "user": res1.username, "userid": res1.userid})

@app.route('/attendance-data')
def get_all_attendance_data():
    # 查询数据库，获取所有打卡数据
    attendance_records = attendancetime.query.all()

    # 将查询结果转换为字典列表
    attendance_data = []
    for record in attendance_records:
        # 确保toworktimestamp和offworktimestamp是有效的时间戳
        if record.toworktimestamp:
            towork_time = datetime.fromtimestamp(record.toworktimestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            towork_time = None

        if record.offworktimestamp:
            offwork_time = datetime.fromtimestamp(record.offworktimestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            offwork_time = None

        # 将日期字段转换为字符串格式
        created_date_str = record.createddate.strftime('%Y-%m-%d') if record.createddate else None

        # 构建每个记录的字典
        attendance_dict = {
            'aid': record.aid,
            'username': record.username,  # 假设username是attendancetime模型的一部分
            'userid': record.userid,
            'status': record.status,
            'toworktimestamp': towork_time,
            'offworktimestamp': offwork_time,
            'createddate': created_date_str
        }
        attendance_data.append(attendance_dict)

    # 返回JSON格式的打卡数据
    return jsonify(attendance_data)
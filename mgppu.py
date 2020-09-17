# -*- coding: utf-8 -*-
import requests
from Entity import Entity
from Lesson import Lesson
from Interval import Interval
from Papser import Parser
from bs4 import BeautifulSoup as Bs
import json
from datetime import date, timedelta
import datetime
from requests.auth import HTTPBasicAuth

#####################################################################

# any semester in range 2
SEMESTER = 1


#####################################################################

class Mgppu(Parser):
    def __init__(self):
        self.main_url = "https://mgppu.ru/students/timetable"
        self.fix_schedule = "https://mgppu.ru/students/educational_process/rings"
        self.API_server = "https://parser.helios.dewish.ru/"
        self.username = "6b17217c7c7548d165a39b669525f40b"
        self.university = 'МГППУ'
        self.password = "824073df3c0756ce8a3d04a787d8e776"
        self.monday = get_monday()

    def run(self):
        faculties = self.get_faculties()
        academic_year = self.get_academic_year_id()
        semester = self.get_semester()
        groups = get_groups(faculties, academic_year, semester)
        self.get_time_table(groups)

    def get_time_table(self, faculties):

        for faculty in range(len(faculties)):
            timetable = []
            soup = pars(self.main_url + "/view?y=" + self.get_academic_year_id() + "&s=" + self.get_semester() + "&g="
                        "" + faculties[faculty] + f"&f={self.monday}&t={self.monday + timedelta(days=12)}")
            if not self.check_date(soup):

                valid_table=additionally(soup, timetable, self.monday, self.get_semester(), self.get_academic_year_id(), faculties[faculty])

                continue

            try:
                table = soup.find("tbody").find_all("tr")
            except AttributeError:
                valid_table=additionally(soup, timetable, self.monday, self.get_semester(), self.get_academic_year_id(), faculties[faculty])

                continue
            for tr in table:
                try:
                    subject = word_check(tr.find_all("td")[1].text.split("(")[0].strip())
                except IndexError:
                    day = get_day(tr)
                    number_week = get_number_week(tr)
                    continue
                auditory = get_auditory(tr)
                extra = get_extra(tr)
                start_time = get_start_time(tr)
                number = get_number(tr, self.fix_schedule, start_time)
                end_time = get_end_time(tr, self.fix_schedule, start_time)
                interval=Interval(number,start_time,end_time)
                typ = get_type(tr)
                lesson=Lesson(number_week,day,interval,subject,auditory,extra,typ)

                self.addLessonToSchedule(timetable,lesson)


            valid_table=additionally(soup, timetable, self.monday, self.get_semester(), self.get_academic_year_id(), faculties[faculty])

            self.sendEntityToDatabase(valid_table,faculty,len(faculties))


    def get_semester(self):
        soup = pars(self.main_url)
        semesters = soup.find("select", id="semester").find_all("option")
        return semesters[SEMESTER].get("value")

    def check_date(self, soup):
        h2 = soup.find("h2").text.split(" ")[3].split("с")[-1].strip().split(".")
        days = str(self.monday).split("-")
        if h2[0] == days[2] and h2[1] == days[1] and h2[2] == days[0]:
            return True
        else:
            return False

    def get_faculties(self):
        groups = []
        soup = pars(self.main_url)
        table = soup.find("select", id="department").find_all("option")
        for group in table:
            groups.append(group.get("value"))
        del groups[0]
        return groups

    def get_academic_year_id(self):
        soup = pars(self.main_url)
        years = soup.find("select", id="academicYear").find_all("option")
        for year in years:
            if year.text.split("/")[-1] == str(date.today()).split("-")[0]:
                return year.get("value")

    def send_info(self, timetable):
        headers = {"Content-type": "Application/json"}
        timetable = json.dumps(timetable, ensure_ascii=False)
        response = requests.post(self.API_server, auth=HTTPBasicAuth(self.username, self.password),
                                 headers=headers, data=timetable.encode('utf-8')).text
        response = json.loads(response)
        print(response["entityStatus"] + " " * indent(response) + " | " + str(response["scheduleNotesCountOld"]) + " =>"
                      " " + str(response["scheduleNotesCountNew"]) + " | " + response["status"])


def get_auditory(tr):
    return word_check(tr.find_all("td")[-1].text)


def get_number_week(tr):
    return week(tr.find_all("td")[-1].text.split(" ")[0])


def get_day(tr):
    day = tr.find_all("td")[-1].text.split(" ")[-1]
    day = detect_day(day)
    return day


def get_type(tr):
    typ = tr.find_all("td")[1].text.split("(")[-1].split(")")[0]
    typ = translate_type(typ, tr)
    if typ is None:
        typ = word_check(tr.find_all("td")[0].text.split("(")[-1].split(")")[0])
    return typ


def get_number(tr, fix_schedule, start_time):
    try:
        number = word_check(tr.find_all("td")[0].text.split(" ")[0].strip())
        if len(number) > 3:
            return 1
        number = int(number)
    except ValueError:
        return get_fix_number(fix_schedule, start_time)
    return number


def get_fix_number(fix_schedule, start_time):
    soup = pars(fix_schedule)
    table = soup.find("tbody").find_all("tr")
    del table[0]
    del table[-3]
    for tr in table:
        times = tr.find_all("td")[1].text.strip().split(" - ")[0].split(".")
        if times[0] + ":" + times[1] == start_time:
            return int(tr.find_all("td")[0].text.strip())


def get_end_time(tr, fix_schedule, start_time):
    try:
        end_time = word_check(tr.find_all("td")[0].text.split("пара")[-1].split(" - ")[1])
    except IndexError:
        end_time = "00:00"
    return end_time


def get_fix_end_time(fix_schedule: object, start_time: object) -> object:
    soup = pars(fix_schedule)
    table = soup.find("tbody").find_all("tr")
    del table[0]
    del table[-3]
    for tr in table:
        times = tr.find_all("td")[1].text.strip().split(" - ")[0].split(".")
        if times[0] + ":" + times[1] == start_time:
            valid_end_time = tr.find_all("td")[1].text.strip().split(" - ")[1].split(".")
            return valid_end_time[0] + ":" + valid_end_time[1]
    start_time = start_time.split(":")

    return str(int(start_time[0]) + 1) + ":" + str(int(start_time[1]) + 30)


def get_start_time(tr: object) -> object:
    try:
        start_time = word_check(tr.find_all("td")[0].text.split("пара")[-1].split(" ")[0])
        start_time = start_time.split(" ")[0]
    except IndexError:
        start_time = "00:00"
    return start_time


def get_extra(tr):
    prefixies = ["доц.", "ст.", "проф.", "каф.", "асс", "преп."]
    try:
        full_extra = word_check(tr.find_all("td")[-2].text).split(" ")
    except AttributeError:
        return word_check(tr.find_all("td")[-2].text.strip())
    for prefix in prefixies:
        if full_extra[0] == prefix:
            return full_extra[-2] + " " + full_extra[-1]
    return word_check(tr.find_all("td")[-2].text.strip())


def get_monday():
    if datetime.datetime.weekday(datetime.datetime.today()) == 0:
        return date.today()

    elif datetime.datetime.weekday(datetime.datetime.today()) == 1:
        return date.today() - timedelta(days=1)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 2:
        return date.today() - timedelta(days=2)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 3:
        return date.today() - timedelta(days=3)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 4:
        return date.today() - timedelta(days=4)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 5:
        return date.today() - timedelta(days=5)

    elif datetime.datetime.weekday(datetime.datetime.today()) == 6:
        return date.today() - timedelta(days=6)


def additionally(soup, timetable, monday, semester, academic_year_id, faculty):
    name = soup.find('h1').text.split('группы')[-1].split('на')[0].strip()
    Type = 'group'
    url = f'https://mgppu.ru/students/timetable/view?y={academic_year_id}&s' \
                         f'={semester}&g={faculty}&f=' + str(monday) + '&t'\
                         f'={str(monday + timedelta(days=12))}'
    schedule = timetable
    entity=Entity(name, url, Type, schedule)
    return entity


def check_dublicate(day, number, weak, timetable, extra2):
    for lesson in timetable:
        if lesson["week"] == weak and lesson["day"] == day and \
                lesson["interval"]["number"] == number:
            extra1 = lesson["extra"]
            lesson["extra"] = extra1 + " | " + extra2
            return False
    return True


def get_groups(groups, academic_year, semester):
    faculties = []

    for group in groups:
        data = {"academicYearId": academic_year,
                "semesterId": semester,
                "departmentId": group}
        response = requests.post("https://mgppu.ru/timetable/get-student-groups", data=data)
        for faculty in json.loads(response.text):
            faculties.append(faculty)
    return faculties


def translate_type(typ, tr):
    if typ == "Пр.":
        return 'Практика'
    elif typ == 'Сем.':
        return 'Семинар'
    elif typ == 'Лек.':
        return 'Лекция'
    elif typ == "Лаб.":
        return "Лабораторная"
    else:
        return word_check(tr.find_all("td")[0].text.split("(")[-1].split(")")[0])


def word_check(word):
    if word != "":
        return word
    else:
        return None


def week(daties):
    try:
        day, month, year = tuple(daties.split(",")[0].split("."))
        number_week = datetime.date(int(year), int(month), int(day)).isocalendar()[1]
        if number_week % 2 == 0:
            return 2
        else:
            return 1
    except ValueError:
        pass


def detect_day(day):
    if day == "понедельник":
        return 1
    elif day == "вторник":
        return 2
    elif day == "среда":
        return 3
    elif day == "четверг":
        return 4
    elif day == "пятница":
        return 5
    elif day == "суббота":
        return 6


def indent(response):
    return 60 - len(response["entityStatus"])


def pars(link):
    response = requests.get(link)
    return Bs(response.text, "html.parser")



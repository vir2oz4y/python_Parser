import requests
import datetime
import calendar
import time
import urllib.parse
from bs4 import BeautifulSoup as BS
from Papser import Parser
from Interval import Interval
from Entity import Entity
from Lesson import Lesson
from WorkWithData import *

TimeLessonsBegin = ['08:20', '10:20', '12:05',
                    '13:55', '15:40', '17:25', '19:10', '20:55']


class TSUADParser(Parser):
    def __init__(self, university, username, password):
        super().__init__(university, username, password)

    def getTeachers(self):
        url = "https://tsuab.ru/schedule/api/teachers.php"
        arrayOfchar = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с',
                       'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'э', 'ю', 'я']

        nowWeek = getNowWeek()
        nextWeek = getNextWeek()
        teacherList = []
        for char in arrayOfchar:

            querystring = {"q": char}

            response = requests.request("GET", url, params=querystring)
            response.encoding = 'utf-8'
            for teacher in response.json()['items']:
                teacherList.append([teacher['value'], teacher['id']])

        filterTeachers = []
        for teacher in teacherList:
            if not teacher in filterTeachers:
                filterTeachers.append(teacher)

        filterTeachers.sort()
        teacherList = []
        for teacher in filterTeachers:
            urlnow = 'https://www.tsuab.ru/schedule/?q={}&type={}&dt={}&df={}&wid=11&text={}'.format(teacher[1],
                                                                                                     'teacher',
                                                                                                     nowWeek[1],
                                                                                                     nowWeek[0],
                                                                                                     teacher[0])

            url = urlnow
            name = teacher
            entity = Entity(name, url, 'teacher', None)
            teacherList.append(entity)

        return teacherList

    def getGroups(self):
        url = "https://www.tsuab.ru/schedule/api/groups.php"
        arrayOfchar = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с',
                       'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'э', 'ю', 'я', '0', '1', '2', '3', '4', '5', '6', '7',
                       '8', '9']

        filterGroups = []
        groupList = []
        for char in arrayOfchar:

            querystring = {"q": char}
            response = requests.request("GET", url, params=querystring)
            response.encoding = 'utf-8'
            for group in response.json()['items']:
                groupList.append([group['value'], group['id']])

        for group in groupList:
            if not group in filterGroups:
                filterGroups.append(group)

        filterGroups.sort()

        groupList = []
        nowWeek = getNowWeek()
        nextWeek = getNextWeek()

        for group in filterGroups:
            urlnow = 'https://www.tsuab.ru/schedule/?q={}&type={}&dt={}&df={}&wid=11&text={}'.format(group[1], 'group',
                                                                                                     nowWeek[1],
                                                                                                     nowWeek[0],
                                                                                                     group[0])

            url = urlnow
            name = group
            entity = Entity(name, url, 'group', None)
            groupList.append(entity)

        return groupList

    def getSchedule(self, group, typeP, entity):
        url = "https://www.tsuab.ru/schedule/api/timetable.php"
        schedule = []

        querystring = {"q": group[1], "type": typeP, "dt": getNowWeek()[1], "df": getNowWeek()[0], "wid": "11",
                       "text": group[0]}

        response = requests.request("GET", url, params=querystring)

        soup = BS(response.content, 'html.parser')

        lessons = soup.findAll('div', {'class': 'timetable-mobile__item'})
        fio = None
        for lesson in lessons:
            timetableRow = lesson.findAll('div', {'class': 'timetable__row'})
            if len(timetableRow) > 0:
                day = getNameOfTheDayOfTheWeek(lesson.find('div', {'class': 'timetable__day'}).get('data-date'))
                week = getNumberWeek(lesson.find('div', {'class': 'timetable__day'}).get('data-date'))
                numberLesson=0
                for el in timetableRow:
                    timeLesson = el.findAll('div', {'class': 'timetable-time__value'})
                    lessonBegin = timeLesson[0].text
                    lessonEnd = timeLesson[1].text
                    numberLesson = numberLesson+1
                    interval = Interval(numberLesson, lessonBegin, lessonEnd)

                    subject = el.find('div', {'class': 'timetable-lesson__title'}).text.replace('\n', '').strip()
                    if typeP == 'teacher':
                        extra = None
                    else:
                        extra = el.find('div', {'class': 'timetable-lesson__lecturer'}).text.replace('\n', '').strip()

                    if typeP == 'teacher':
                        fio = el.find('div', {'class': 'timetable-lesson__lecturer'}).text.replace('\n', '').strip()

                    auditory = el.find('div', {'class': 'timetable-lesson__lecture-room'}).text.replace('\n', '').strip()
                    Type = getNameType(
                        el.find('div', {'class': 'timetable-lesson__marker'}).get('class')[1].split('--')[1]) if len(
                        el.find('div', {'class': 'timetable-lesson__marker'}).get('class')) > 1 else None
                    lesson = Lesson(week, day, interval, subject, auditory, extra, Type)

                    self.addLessonToSchedule(schedule, lesson)

        querystring = {"q": group[1], "type": typeP, "dt": getNextWeek()[1], "df": getNextWeek()[0], "wid": "11",
                       "text": group[0]}

        response = requests.request("GET", url, params=querystring)

        soup = BS(response.content, 'html.parser')

        lessons = soup.findAll('div', {'class': 'timetable-mobile__item'})

        for lesson in lessons:
            timetableRow = lesson.findAll('div', {'class': 'timetable__row'})
            if len(timetableRow) > 0:
                day = getNameOfTheDayOfTheWeek(lesson.find('div', {'class': 'timetable__day'}).get('data-date'))
                week = getNumberWeek(lesson.find('div', {'class': 'timetable__day'}).get('data-date'))
                numberLesson = 0
                for el in timetableRow:
                    timeLesson = el.findAll('div', {'class': 'timetable-time__value'})
                    lessonBegin = timeLesson[0].text
                    lessonEnd = timeLesson[1].text
                    numberLesson = numberLesson+1
                    interval = Interval(numberLesson, lessonBegin, lessonEnd)

                    subject = el.find('div', {'class': 'timetable-lesson__title'}).text.replace('\n', '').replace(' ', '').strip()
                    if typeP == 'teacher':
                        extra = None
                    else:
                        extra = el.find('div', {'class': 'timetable-lesson__lecturer'}).text.replace('\n', '').strip()

                    if typeP == 'teacher':
                        fio = el.find('div', {'class': 'timetable-lesson__lecturer'}).text.replace('\n', '').strip()

                    auditory = el.find('div', {'class': 'timetable-lesson__lecture-room'}).text.replace('\n', '').strip()
                    Type = getNameType(
                        el.find('div', {'class': 'timetable-lesson__marker'}).get('class')[1].split('--')[1]) if len(
                        el.find('div', {'class': 'timetable-lesson__marker'}).get('class')) > 1 else None
                    lesson = Lesson(week, day, interval, subject, auditory, extra, Type)
                    self.addLessonToSchedule(schedule, lesson)
        if typeP == 'teacher':
            if fio == None:
                return []
            else:
                entity.name = fio.strip()
                return schedule
        else:
            return schedule


def getNowWeek():
    Monday = datetime.date.today()
    Monday = Monday - datetime.timedelta(days=Monday.weekday())
    Suturday = Monday + datetime.timedelta(6)

    last = str(Monday)
    now = str(Suturday)
    return [last, now]


def getNextWeek():
    lastMonday = datetime.date.today()
    lastMonday = lastMonday - datetime.timedelta(days=lastMonday.weekday())
    last = str(lastMonday)
    last = last.split('-')

    nextSaturday = datetime.date.today()
    nextSaturday = lastMonday + datetime.timedelta(days=-lastMonday.weekday(), weeks=1)
    Monday = nextSaturday
    Suturday = Monday + datetime.timedelta(6)
    return [str(Monday), str(Suturday)]


def getNameType(name):
    if name == 'lab':
        return 'Лабораторная'
    elif name == 'lecture':
        return 'Лекция'
    elif name == 'practice':
        return 'Практика'


def getNameOfTheDayOfTheWeek(date):
    date = date.split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    dayOfweek = calendar.weekday(year, month, day) + 1
    return dayOfweek


def getNumberWeek(date):
    date = date.split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    numberweek = 1 + datetime.date(year, month, day).isocalendar()[1] % 2
    return numberweek


def RUNTsuad():
    Parser = TSUADParser('ТГАСУ', '8bdc6af8d6e031201102ee81ca524d5f', '7ac2f03ea228e7d21e16e8736581a021')

    groupList = Parser.getGroups()

    for group in range(len(groupList)):
        if  group!=137:
            continue
        thisGroup = groupList[group]
        try:
            schedule = Parser.getSchedule(thisGroup.name, 'group', thisGroup)
            thisGroup.schedule = schedule
            thisGroup.name = thisGroup.name[0]
            Parser.sendEntityToDatabase(thisGroup, group, len(groupList))
        except Exception as e:
            e = "TSUAD "+str(e) + "\t" + " не удалось скачать расписание для группы " + thisGroup.name
            Parser.sendMessOnError(e)
            continue

    teacherList = Parser.getTeachers()
    for teacher in range(len(teacherList)):
        thisTeacher = teacherList[teacher]
        try:
            schedule = Parser.getSchedule(thisTeacher.name, 'teacher', thisTeacher)
            if len(schedule) > 0:
                thisTeacher.schedule = schedule
                Parser.sendEntityToDatabase(thisTeacher, teacher, len(teacherList))
        except Exception as e:
            e = "TSUAD "+str(e) + "\t" + " не удалось скачать расписание для преподавателя " + thisTeacher.name
            Parser.sendMessOnError(e)
            continue

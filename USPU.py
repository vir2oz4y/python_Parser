
from WorkWithData import *
from Papser import Parser
from Interval import Interval
from Entity import Entity
from Lesson import Lesson
from bs4 import BeautifulSoup as BS
import datetime
import requests


TimeLessonsBegin = ['08:30', '10:15', '12:00',
                    '14:00', '15:45', '17:30', '19:15', '20:10']
nameUniversity = "УрГПУ"
username = '069b79b349a143d303177be012ea001e'
password = 'fd610bfd0fb520833060ab50c198a700'

isTesting = False


class USPUParserGroups(Parser):
    def __init__(self, university, username, password):
        super().__init__(university, username, password)

    def getGroups(self):  # получаю все названия групп
        groupsite = "https://uspu.ru/education/eios/schedule"
        grouplist = requests.get(groupsite)
        soup = BS(grouplist.content, 'html.parser')

        groups = soup.find('select', {'name': 'group_name'}).findAll(
            'option', value=True)
        listGroups = []

        for group in groups:
            url = 'https://uspu.ru/education/eios/schedule/?group_name=%s' % (
                group.text)
            name = group.text
            entity = Entity(name, url, 'group', None)

            listGroups.append(entity)

        return listGroups

    def getTestingGroups(self):
        groups = []
        groups.append(Entity(
            'НОА-1701', '', 'group', None))
        return groups

    # получаю расписание на текущую и след неделю
    def getHTMLTimetableForGroup(self, groupname):
        url = "https://uspu.ru/ajax/rasp.php"
        timezone = getDatefor2Week()
        payload = 'group_name=%s&date=%s' % (groupname, timezone)
        headers = {
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        }

        response = requests.request(
            "POST", url, data=payload.encode('utf-8'), headers=headers)

        # print(response.text)
        return response

    # разбираю полученное расписание на элементы и отправляю его

    def getSchedule(self, HTML):
        soup = BS(HTML.content, 'html.parser')
        massSchedule = []

        for day in soup.select('.rasp-item'):

            # День и месяц дня рассписания
            today = day.find('span', {'class': 'rasp-day'}).text

            dayOfWeek = day.find('div', {'class': 'rasp-week'}).text
            dayOfWeek = GetDayOf(dayOfWeek, 'low')

            for TimeTableThisDay in day.select('.rasp-para'):

                schedule = TimeTableThisDay.find_all(text=True)

                LessonBegin = GetLesBegin(schedule[1])
                LessonEnd = GetLesEnd(schedule[1])
                NumberLessons = GetNumLessons(LessonBegin, TimeLessonsBegin)
                interval = Interval(NumberLessons, LessonBegin,
                                    LessonEnd)

                subject = getSubjectName(schedule[4])
                auditory = schedule[7]
                podgroop = getPodgroop(schedule[6])

                if int(podgroop) > 0:
                    typename = '%s  (%s п.)' % (
                        getTypeName(subject, schedule[4]), podgroop)
                elif getTypeName(subject, schedule[4]) == '':
                    typename = None
                else:
                    typename = getTypeName(subject, schedule[4])

                extra = getNameTeacher(schedule[8])

                lesson = Lesson(week(today), dayOfWeek, interval,
                                subject, auditory, extra, typename)

                self.addLessonToSchedule(massSchedule, lesson)

        return massSchedule


class USPUParserTeachers(Parser):
    def __init__(self, university, username, password):
        super().__init__(university, username, password)

    def getTeachers(self):
        teachersite = 'https://uspu.ru/education/eios/schedule/'
        teacherlist = requests.get(teachersite)
        soup = BS(teacherlist.content, 'html.parser')
        teacherList = []
        teachers = soup.find('select', {'name': 'teacher_search'}).find_all(
            'option', value=True)
        fio = soup.find(
            'select', {'name': 'teacher_search'}).find_all(text=True)

        porNumber = 3
        for teacher in teachers:

            url = 'https://uspu.ru/education/eios/schedule/?teacher_name=%s' % (
                teacher.text)

            name = fio[porNumber]
            entity = Entity(name, url, 'group', None)

            teacherList.append(entity)
            porNumber = porNumber+2
        return teacherList

    # получаю расписание на текущую и след неделю

    def getHTMLTimetableForTeacher(self, teacherName):
        url = 'https://uspu.ru/ajax/rasp_teacher.php'
        timezone = getDatefor2Week()
        payload = 'teacher_name=%s&date=%s' % (teacherName, timezone)
        headers = {
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        }

        response = requests.request(
            "POST", url, data=payload.encode('utf-8'), headers=headers)

        # print(response.text)
        return response

    # разбираю полученное расписание на элементы и отправляю его
    def getSchedule(self, HTML):
        soup = BS(HTML.content, 'html.parser')
        massSchedule = []

        for day in soup.select('.rasp-item'):

            # День и месяц дня рассписания
            today = day.find('span', {'class': 'rasp-day'}).text

            dayOfWeek = day.find('div', {'class': 'rasp-week'}).text
            dayOfWeek = GetDayOf(dayOfWeek, 'low')
            for TimeTableThisDay in day.select('.rasp-para'):

                schedule = TimeTableThisDay.find_all(text=True)
                LessonBegin = GetLesBegin(schedule[1])
                LessonEnd = GetLesEnd(schedule[1])
                NumberLessons = GetNumLessons(LessonBegin, TimeLessonsBegin)
                interval = Interval(NumberLessons, LessonBegin,
                                    LessonEnd)

                subject = getSubjectName(schedule[4])
                auditory = schedule[6].replace('( ', '(')
                podgroop = getPodgroop(schedule[9])
                if int(podgroop) > 0:
                    typename = '%s  (%s п.)' % (
                        getTypeName(subject, schedule[4]), podgroop)
                elif getTypeName(subject, schedule[4]) == '':
                    typename = None
                else:
                    typename = getTypeName(subject, schedule[4])

                extra = schedule[8].replace('Группа:','').replace('\n','')

                lesson = Lesson(week(today), dayOfWeek, interval,
                                subject, auditory, extra, typename)

                self.addLessonToSchedule(massSchedule, lesson)

        return massSchedule


def getSubjectName(sub):
    sub = sub.replace('(Лаб)', '')
    sub = sub.replace('(лаб)', '')
    sub = sub.replace('(Лек)', '')
    sub = sub.replace('(лек)', '')
    sub = sub.replace('(прак)', '')
    sub = sub.replace('(Пр)', '')
    sub = sub.replace('(Зач)', '')
    sub = sub.replace('(Экз)', '')
    return sub.rstrip()


def getTypeName(sub, typeN):
    Type='Экзамен'
    typeN = typeN.replace(sub, '')
    typeN = typeN.replace('(', '').replace(')', '')
    typeN = typeN.strip()
    if typeN == 'Лек' or typeN == 'лек' or typeN == 'Лек':
        Type = 'Лекция'
    elif typeN == 'Лаб' or typeN == 'лаб':
        Type = 'Лабораторная'
    elif typeN == 'Пр' or typeN == 'прак':
        Type = 'Практика'
    elif typeN == 'Зач' or typeN == 'зач':
        Type = 'Зачет'
    elif typeN == 'Экз' or typeN == 'экз':
        Type = 'Экзамен'
    return Type


def getNameTeacher(teac):
    teac = teac.split(': ')
    fam = teac[1]
    fam = fam.split(' ')
    if len(fam) == 2:
        fam = fam[0]+' '+fam[1][0]+'.'
    elif len(fam) == 3:
        fam = fam[0]+' '+fam[1][0]+'.'+fam[2][0]
    else:
        fam = fam[0]
    return fam


def getPodgroop(gr):
    gr = gr.split(':')
    return gr[1].replace(' ', '')


def getDatefor2Week():  # получаю дату предыдущего понедельника и след недели
    lastMonday = datetime.date.today()
    lastMonday = lastMonday - datetime.timedelta(days=lastMonday.weekday())
    last = str(lastMonday)
    last = last.split('-')

    nextSaturday = datetime.date.today()
    nextSaturday = lastMonday + \
        datetime.timedelta(days=-lastMonday.weekday()-1, weeks=2)
    next = str(nextSaturday)
    next = next.split('-')

    this2week = '%s.%s.%s%s-%s%s.%s.%s' % (
        last[2], last[1], last[0], ' ', ' ', next[2], next[1], next[0])
    return this2week


def week(date):
    date = date.split(' ')
    arrMonth = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
                'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря', ]
    arrMonthNum = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    for month in range(len(arrMonth)):
        if arrMonth[month] == date[1]:
            thismonth = arrMonthNum[month]
    year = datetime.date.today().year

    numberweek = datetime.date(year, thismonth, int(date[0])).isocalendar()[1]
    if numberweek % 2 == 0:
        return 1
    else:
        return 2


def RunUspuGroup():
    Parser = USPUParserGroups(nameUniversity, username, password)
    groupList = Parser.getTestingGroups() if isTesting else Parser.getGroups()

    for index in range(len(groupList)):
        thisgroup = groupList[index]
        timeTable = Parser.getHTMLTimetableForGroup(thisgroup.name)
        try:
            schedule = Parser.getSchedule(timeTable)
            thisgroup.schedule = schedule
            Parser.sendEntityToDatabase(thisgroup, index, len(groupList))
        except Exception as e:
            e ="USPU "+ str(e) + "\t"  + "не удалось скачать расписание для группы " + thisgroup.name
            Parser.sendMessOnError(e)



def RunUspuTeacher():
    Parser = USPUParserTeachers('USPU', username, password)
    TeacherList = Parser.getTeachers()

    for index in range(len(TeacherList)):
        thisTeacher = TeacherList[index]
        timeTable = Parser.getHTMLTimetableForTeacher(thisTeacher.name)
        try:
            schedule = Parser.getSchedule(timeTable)
            thisTeacher.schedule = schedule
            Parser.sendEntityToDatabase(thisTeacher, index, len(TeacherList))
        except Exception as e:
            e = "USPU "+ str(e) + "\t"  + "не удалось скачать расписание для преподавателя " + thisTeacher.name
            Parser.sendMessOnError(e)

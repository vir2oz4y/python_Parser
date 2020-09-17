import requests
import datetime
import calendar
import urllib.parse
from bs4 import BeautifulSoup as BS
from Papser import Parser
from Interval import Interval
from Entity import Entity
from Lesson import Lesson
from WorkWithData import *


nameUniversity = "СибАДИ"
username = '069b79b349a143d303177be012ea001e'
password = 'fd610bfd0fb520833060ab50c198a700'
TimeLessonsBegin = ['08:20', '10:00', '11:40',
                    '13:45', '15:25', '17:05', '18:40', '20:20']

isTesting = False


class SibADIParser(Parser):
    def __init__(self, university, username, password):
        super().__init__(university, username, password)

    def getGroups(self):
        groupList = []
        groupsite = 'http://umu.sibadi.org/Dek/Default.aspx?mode=group'

        response = requests.get(groupsite)
        soup = BS(response.content, 'html.parser')

        groups = soup.findAll('tr', {'class': 'TblText'})

        for group in groups:
            group = group.find('a')
            group = group.get('href')
            groupId = group.split('id=')[1]

            url = 'http://umu.sibadi.org/Rasp/Rasp.aspx?group={}&sem=2'.format(
                groupId)
            name = groupId
            entity = Entity(name, url, 'group', None)
            groupList.append(entity)


        groups = soup.findAll('tr', {'class': 'TblhiText'})

        for group in groups:
            group = group.find('a')
            group = group.get('href')
            groupId = group.split('id=')[1]

            url = 'http://umu.sibadi.org/Rasp/Rasp.aspx?group={}&sem=2'.format(
                groupId)
            name = groupId
            entity = Entity(name, url, 'group', None)
            groupList.append(entity)

        return groupList

    def getHTMLTimetableForGroup(self, groupname):
        url = "http://umu.sibadi.org/Rasp/Rasp.aspx?group={}&sem=2".format(
            groupname)
        headers = {
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        }
        response = requests.get(url,headers)
        response.encoding='utf-8'
        return response

    def getNameGroup(self, HTML):
        soup = BS(HTML.content, 'html.parser')
        groupName = soup.find('span', {'id': 'lblNameDoc'}).text.split(' ')[3]
        return groupName

    def getTestingGroups(self):
        groups = []
        groups.append(Entity(
            'Порхачева С.М.', 'http://umu.sibadi.org/Rasp/Rasp.aspx?&year=2019-2020&prep=%CF%EE%F0%F5%E0%F7%E5%E2%E0%20%D1.%CC.&sem=2', 'group', None))
        return groups


    def getTeachers(self, teachers):
        teachersList = []
        for teacher in teachers:
            teacherEncode = urllib.parse.quote(teacher.encode('cp1251'))
            url = 'http://umu.sibadi.org/Rasp/Rasp.aspx?&year=2019-2020&prep={}&sem=2'.format(
                teacherEncode)
            entity = Entity(teacher, url, 'teacher', None)
            teachersList.append(entity)

        return teachersList

    def getHTMLTimetableForTeacher(self, teachername):
        teachername = urllib.parse.quote(teachername.encode('cp1251'))
        url = "http://umu.sibadi.org/Rasp/Rasp.aspx?&year=2019-2020&prep={}&sem=2".format(
            teachername)
        headers = {
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        }

        response = requests.get(url,headers)
        response.encoding='cp1251'
        return response

    def getSchedule(self, HTML):

        soup = BS(HTML.content.decode('cp1251'), 'html.parser')
        select = soup.find(
            'select', {'name': 'cmbDayOfWeek'}).findAll('option')
        schedule = []
        date=[]
        day = -1
        interval = None
        weeks = []
        newDate=None
        itsFix=False
        for tableRow in soup.find('table', {'id': 'tblGr'}).findAll('tr', {'class': ''}):

            if (tableRow != soup.find('table', {'id': 'tblGr'}).findAll('tr', {'class': ''})[0]) and len(tableRow )>2:

                elementsTd = tableRow.findAll('td')

                if tableRow.text.replace('\n','')=='Расписание фиксированных занятий': 
                    itsFix=True

                if len(elementsTd)>3:

                    
                    if itsFix:

                        newDate = getDate(elementsTd[0])  # день недели фиксированных занятий
                        if newDate!=None:
                            date=newDate
                            week=date[0]
                            day=date[1]
                            del elementsTd[0]

                        newInterval = getInterval(elementsTd[0])
                        if newInterval != None:
                            interval = newInterval
                            del elementsTd[0]

                        subject = elementsTd[0].text
                        extra = elementsTd[1].text
                        auditory = elementsTd[2].text
                        typeL='%s (%s.%s)'.format(getTypeLes(subject.split(' ')[0]),date[2],date[3])
                        subject=clearSubject(subject)

                        lesson = Lesson(week, day, interval, subject, auditory, extra,typeL)
                        self.addLessonToSchedule(schedule, lesson)
                    else:

                        newDay = getDay(elementsTd[0].text)
                        if newDay != -1:
                            day = newDay
                            del elementsTd[0]

                        newInterval = getInterval(elementsTd[0])
                        if newInterval != None:
                            interval = newInterval
                            del elementsTd[0]

                        newWeeks = getWeeks(elementsTd[0])
                        weeks = newWeeks
                        if len(newWeeks) == 1:
                            del elementsTd[0]

                        subject = elementsTd[0].text
                        extra = elementsTd[1].text
                        auditory = elementsTd[2].text

                        typeL= getTypeLes(subject.split(' ')[0])
                        subject = clearSubject(subject)

                        for week in weeks:
                            lesson = Lesson(week, day, interval, subject, auditory, extra,typeL)
                            self.addLessonToSchedule(schedule, lesson)

        return schedule

def getInterval(firstTd):
    firstTd = firstTd.findAll(text=True)
    for time in range(len(TimeLessonsBegin)):
        if formatTime(firstTd[0]) == TimeLessonsBegin[time]:
            interval = Interval(time+1, formatTime(firstTd[0]), formatTime(firstTd[1]))
            return interval
    return None


def getDate(firstTd):
    date= firstTd.text.split('.')
    if len(date)>1:
        day=int(date[0])
        month=int(date[1])
        year=int(date[2])

        numberWeek = datetime.date(year, month, day).isocalendar()[1] %2+1

        dayOfweek=calendar.weekday(year, month, day)+1

    
        return [numberWeek,dayOfweek,month,day]
    else:
        return None

def getWeeks(firstTd):
    firstTd = firstTd.text
    if firstTd == '1':
        return [1]
    if firstTd == '2':
        return [2]
    else: return[1, 2]


def getDay(firstTd):
    arrayWeekDay = ['Понедельник', 'Вторник',
                    'Среда', 'Четверг', 'Пятница', 'Суббота']
    for weekDay in range(len(arrayWeekDay)):
        if firstTd == arrayWeekDay[weekDay]:
            return weekDay+1
    return -1



def getTypeLes(subject):
    if subject == 'лек':
        return 'Лекция'
    if subject == 'лек.':
        return 'Лекция'
    if subject == 'пр.':
        return 'Практика'
    if subject == 'Лаб':
        return 'Лабораторная'
    if subject == 'лаб.':
        return 'Лабораторная'
    if subject == 'экз.':
        return 'Экзамен'
    if subject == 'зач.':
        return 'Зачет'
    if subject == 'фак':
        return 'Факультатив'
    
def clearSubject(subject):
    subject=subject.replace('лек','')
    subject=subject.replace('лек.','')
    subject=subject.replace('пр.','')
    subject=subject.replace('Лаб','')
    subject=subject.replace('лаб.','')
    subject=subject.replace('экз.','')
    subject=subject.replace('зач.','')
    subject=subject.replace('фак','')
    subject=subject.lstrip()
    return subject



def formatTime(time):
    time= time.split('-')
    time= ':'.join(time)
    if len(time) == 4:
        time= '0'+time
    return time


def filterTeacher(teachers):
    filterTeachers= []

    for teacher in teachers:
        teacher= teacher.split(' | ')
        if len(teacher) > 1:
            filterTeachers.append(teacher[0].replace('(ауд)', ''))
            filterTeachers.append(teacher[1].replace('(ауд)', ''))
        else:
            filterTeachers.append(teacher[0].replace('(ауд)', ''))

    teachers= []
    for teacher in filterTeachers:
        if not teacher in teachers:
            if len(teacher.split('.каф.'))>1:
                pass
            else:
                teachers.append(teacher)
    
    return teachers

def RUNSibADI():
    Parser= SibADIParser(
        'СибАДИ', '6f035002491ec2e380ee8821859f3fbc', '030257d98a212512f732d10d036eea97')
    groupList= Parser.getGroups()
    teachersIngroup= []

    for group in range(len(groupList)):
        thisgroup = groupList[group]
        timeTable = Parser.getHTMLTimetableForGroup(thisgroup.name)
        try:
            schedule = Parser.getSchedule(timeTable)
            thisgroup.schedule = schedule
            thisgroup.name = Parser.getNameGroup(timeTable)
            Parser.sendEntityToDatabase(thisgroup, group, len(groupList))
        except Exception as e:
            e = "SibADI "+str(e) + "\t"+ "не удалось скачать расписание для группы " + thisgroup.name
            Parser.sendMessOnError(e)


        for teacher in thisgroup.schedule:
            teachersIngroup.append(teacher.extra)
    teachers = filterTeacher(teachersIngroup)
    teacherList=Parser.getTestingGroups()  if isTesting else Parser.getTeachers(teachers)
    
  
    for teacher in range(len(teacherList)):
        thisteacher= teacherList[teacher]
        timeTable= Parser.getHTMLTimetableForTeacher(
            teacherList[teacher].name)
        try:
            schedule= Parser.getSchedule(timeTable)
            thisteacher.schedule= schedule
            Parser.sendEntityToDatabase(thisteacher, teacher, len(teacherList))
        except Exception as e:
            e = "SibADI "+str(e) + "\t"+ " не удалось скачать расписание для преподавателя " + thisteacher.name
            Parser.sendMessOnError(e)




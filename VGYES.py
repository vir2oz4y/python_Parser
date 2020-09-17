import requests
import datetime
from Papser import Parser
from Interval import Interval
from Entity import Entity
from Lesson import Lesson
from WorkWithData import *

nameUniversity = 'ВГУЭС'
username = 'abdc056f76b1e6f757494506d3eecbe2'
password = '1a79f982620b634cd71fa12358ead1dd'
timeLessonsBegin = ['08:30', '10:10', '11:50', '12:35',
                    '13:30', '15:05', '15:10', '16:50', '18:30', '20:10','20:00','19:15','10:00','17:40','9:00','10:55']


isTesting = False


class VVSUParser(Parser):
    def __init__(self, university, username, password):
        super().__init__(university, username, password)

    def getGroups(self):  # получает списки групп
        listGroups = []
        groupsite = "http://kml.vvsu.ru/map/getTimeTableInst.php"

        jsonGroups = requests.get(groupsite).json()

        for jsonInstitute in jsonGroups:
            jsonGroupInInstitutes = jsonInstitute['group']

            for jsonGroup in jsonGroupInInstitutes:

                url = 'http://it.vvsu.ru/RTFReport/default.aspx?report=419210&Params=@pInstID=%d/;@pGroupID=%d' % (
                    int(jsonInstitute['id_inst']), int(jsonGroup['id']))

                name = jsonGroup['name_group']

                entity = Entity(name, url, 'group', None)
                listGroups.append(entity)

        return listGroups



    def getTestingGroups(self):
        groups = []
        groups.append(Entity(
            'ЗБЭМ-18', 'http://it.vvsu.ru/RTFReport/default.aspx?report=419210&Params=@pInstID=1008/;@pGroupID=60986', 'group', None))
        return groups




    def getSchedule(self, group):  # выполняет основную функцию

        # проходим по каждой группе
        schedule = []

        raspgroup = "http://kml.vvsu.ru/map/getTimeTable.php?group=%d" % int(
            group.url.split('GroupID=')[1])

        jsonSchedule = requests.get(raspgroup).json()

        for jsonWeek in jsonSchedule['data']:
            thisweek = jsonWeek['week']

            if(getWeekForLessons(thisweek)):

                weekforlesson = getWeekForLessons(thisweek)
                weektable = jsonWeek['weektable']

                for dayofweek in weektable:

                    dayOfweek = GetDayOf(
                        dayofweek['dayofweek'], 'full')

                    dayTable = dayofweek['daytable']
                    numberles = 0
                    for numberLesson in range(len(dayTable)):

                        lessonbegin = GetLesBegin(
                            dayTable[numberLesson]['TimePeriod'])  # начало урока
                        lessonend = GetLesEnd(
                            dayTable[numberLesson]['TimePeriod'])  # конец урока
                        numberles = numberles+1  # номер урока
                        inteval = Interval(
                            numberles, lessonbegin, lessonend)		 #

                        typeL = getNametype(
                            dayTable[numberLesson]['subject'])  # тип предмета
                        sybject = getNameLes(
                            dayTable[numberLesson]['subject'])  # предмет
                        extra = dayTable[numberLesson]['teacher']  # учитель
                        auditory = dayTable[numberLesson]['room']  # кабинет

                        # Формируем рассписание на день
                        lesson = Lesson(weekforlesson, dayOfweek, inteval,
                                        sybject, auditory, extra, typeL)



                        self.addLessonToSchedule(schedule, lesson)

        return schedule






def getNameLes(predm):  # получает название предмета

    # replagroupe   удаляет эту строку из исходной строки
    predm = predm.replace('Занятие Лекционное', '')
    predm = predm.replace('Занятие Лабораторное', '')
    predm = predm.replace('Занятие Практическое', '')
    predm = predm.replace('Мероприятие', '')
    predm = predm.replace('()', '')

    return predm






def getNametype(sybject):  # получает тип предмета

    word = ''

    jsonGroup = len(sybject)-2

    while sybject[jsonGroup] != '(':
        word = word+sybject[jsonGroup]
        jsonGroup = jsonGroup-1

    predm = word[::-1]

    if predm == 'Занятие Лекционное':
        predm = 'Лекция'
    elif predm == 'Занятие Лабораторное':
        predm = 'Лабораторная'
    elif predm == 'Занятие Практическое':
        predm = 'Практика'

    return predm





def getWeekForLessons(week):

    thisMonday = datetime.date.today()  # this week
    thisMonday = thisMonday - datetime.timedelta(days=thisMonday.weekday())
    thisMonday = str(thisMonday)
    date = thisMonday.split('-')
    thisMonday = '.'.join((date[2], date[1]))


    nextMonday = datetime.date.today()  # next week
    nextMonday = nextMonday + datetime.timedelta(days=-nextMonday.weekday(), weeks=1)
    nextMonday = str(nextMonday)
    date = nextMonday.split('-')
    nextMonday = '.'.join((date[2], date[1]))

    week = week.split(' - ')

    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    currentWeek = 2-datetime.date(year, month, day).isocalendar()[1] % 2

    if week[0] == thisMonday:
        return 2-currentWeek+1
    elif week[0] == nextMonday:
        return currentWeek
    else:
        return 0





def RUNVVSU():

    Parser = VVSUParser(nameUniversity,username, password)
    listgroup = Parser.getTestingGroups() if isTesting else Parser.getGroups()

    for index in range(len(listgroup)):
        group = listgroup[index]
        try:
            schedule = Parser.getSchedule(group)
            group.schedule = schedule
            Parser.sendEntityToDatabase(group, index, len(listgroup))
        except Exception as e:
            e ="VGYES "+ str(e) + "\t" + listgroup[index].name + "не удалось скачать расписание для группы " + group.name
            Parser.sendMessOnError(e)







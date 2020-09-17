import requests
import json
import random
import time

class Parser(object):
    def __init__(self,university, username, password):
        self.university=university
        self.username = username
        self.password = password

    def sendEntityToDatabase(self, entity,currentIndex, stopIndex):
        headers = {"content-type": "Application/json"}
        jsonEntity = json.dumps(entity.toJsonEntity())

        serverResponse = requests.post('https://parser.helios.dewish.ru/', auth=(
            self.username, self.password), headers=headers, data=jsonEntity)
        self.showInfo(entity,currentIndex,stopIndex,serverResponse.status_code,serverResponse.json())
        


    def showInfo(self,entity,currentIndex,stopIndex,code,serverResponse):
        if code==200:
            scheduleNotesCountOld=serverResponse['scheduleNotesCountOld']
            scheduleNotesCountNew=serverResponse['scheduleNotesCountNew']
            scheduleNotesComparison=serverResponse['scheduleNotesComparison']

            if scheduleNotesComparison=='Расписания отличались':
                scheduleNotesComparison='Обновлено'
            else:
                scheduleNotesComparison=''

            indexof= str(currentIndex+1)+'/'+str(stopIndex)
            line_new = '|{:^10}| {:^30} |{:^10} | {:^100} | {:^12} | Было: {:4} | Стало: {:4} |' .format(self.university,entity.name,indexof, entity.url,scheduleNotesComparison,scheduleNotesCountOld,scheduleNotesCountNew)
            print(line_new)
        else:
            print(serverResponse)
            error=serverResponse['error']
            try:
                info=serverResponse['info']
                print(error,info,entity)
                self.sendMessOnError(str(error, info, entity))
            except KeyError:
                print(error, entity)
                self.sendMessOnError(str(error, info, entity))

    def addLessonToSchedule(self, schedule, newLesson):
        findLesson = self.findLesson(newLesson, schedule)

        if findLesson == None:
            schedule.append(newLesson)

        else:
            findLesson.subject=self.getStringAfterFindLesson(findLesson.subject,newLesson.subject)
            findLesson.auditory=self.getStringAfterFindLesson(findLesson.auditory,newLesson.auditory)
            findLesson.extra=self.getStringAfterFindLesson(findLesson.extra,newLesson.extra)
            findLesson.typeL=self.getStringAfterFindLesson(findLesson.typeL,newLesson.typeL)




    def findLesson(self, newLesson, schedule):
        for exist in schedule:
            if newLesson.week == exist.week and newLesson.day == exist.day and newLesson.interval.NumLes == exist.interval.NumLes:
                return exist

        return None




    def getStringAfterFindLesson(self, laststring, nowstring):
        if laststring == nowstring:
            return laststring
        elif laststring==None:
            return nowstring
        elif nowstring==None:
            return laststring
        else:
            return ' | '.join([laststring, nowstring])


    def sendMessOnError(self, e):
        url = "https://api.vk.com/method/messages.send?peer_id=2000000001&message=message&v=5.101&random_id=124&access_token=2d552811d20aecb776cacad7245ce05bda56ceb56c8495683e4a171ccb0227287126e7afae532d00b8665"
        id_slava = 33262047
        id_kolya = 197547980

        headers = {
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'peer_id': id_slava,
            'message':  str(e),
            'v': 5.101,
            'random_id': random.randint(1, 100000),
            'access_token': 'a73613fa18243570b115d56169cc32bdb6d15bc63c8ad211514846c7fb60b5859621e9ca02e03ecd3e1a6'
        }
        requests.post(url, headers)
        time.sleep(10)

        headers = {
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'peer_id': id_kolya,
            'message': str(e),
            'v': 5.101,
            'random_id': random.randint(1, 100000),
            'access_token': 'a73613fa18243570b115d56169cc32bdb6d15bc63c8ad211514846c7fb60b5859621e9ca02e03ecd3e1a6'
        }
        requests.post(url, headers)
        time.sleep(10)






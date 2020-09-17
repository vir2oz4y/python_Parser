import json
from Lesson import *


class Entity(object):
    def __init__(self, name, url, typeS, schedule):
        self.name = name
        self.url = url
        self.typeS = typeS
        self.schedule = schedule

    def __str__(self):
        lenSchedule = 'ОШИБКА' if self.schedule == None else 'Занятий: ' + str(len(self.schedule))
        return self.name + ' ' + self.url + ' ' + self.typeS+' '+lenSchedule




    def toJsonEntity(self):

        JsonObject = ({"name": self.name,
                       "url": self.url,
                       "type": self.typeS,
                       "schedule": self.getJsonLessons(self.schedule)
                       })

        return JsonObject

    def getJsonLessons(self, schedule):
        jsonLessons = []
        if schedule == None:
            pass
            #print('ОШИБКА при получении предметов для ' + schedule)

        else:
            for lesson in schedule:
                jsonLessons.append(lesson.toJson())

        return jsonLessons

from Entity import *
# import json


class Lesson(object):
    def __init__(self, week, day, interval, subject, auditory, extra, typeL):
        self.week = week
        self.day = day
        self.interval = interval
        self.subject = subject
        self.auditory = auditory
        self.extra = extra
        self.typeL = typeL

    def toJson(self):
        if self.extra == "":
            self.extra = None
        if self.auditory == "":
            self.auditory = None
        if self.typeL == "":
            self.typeL = None

        lesson = {
            "week": self.week,
            "day": self.day,
            "interval": self.interval.toJson(),
            "subject": self.subject,
            "auditory": self.auditory,
            "extra": self.extra,
            "type": self.typeL
        }
        return lesson

import json
class Interval(object):
    def __init__(self,NumberLesson, TimeBegin, TimeEnd):
        self.NumLes=NumberLesson
        self.TimeBegin=TimeBegin
        self.TimeEnd=TimeEnd

    def toJson(self):
        structInterval={"number":self.NumLes,
                        "startTime":self.TimeBegin,
                        "endTime":self.TimeEnd
                        }
        
        return structInterval
        

        
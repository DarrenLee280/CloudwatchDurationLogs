import boto3
from csv import writer
import datetime

client = boto3.client('logs')

def findDurationIndex(response):
    '''
    Find the index in the event logs where the duration is being stored
    INPUT: Dict
    RETURNS: int
    '''
    durationIndex = -1
    index = 0
    for line in response.get('events'):
        line = str(line)
        if line.find("Duration: ") >= 0:
            durationIndex = index
        index += 1
    return durationIndex

def getDuration(line):
    '''
    Finds the duration from a given line
    INPUT: Str
    RETURNS: Str (Duration: ### ms)
    '''
    lineSplit = line.split("\\t")
    for i in lineSplit:
        if i.find("Duration: ") >= 0:
            break
    print(i)
    return i

def enterDataToCSV(data):
    '''
    Enters the data to a csv file with the format
    [Log Group Name][Log Stream Name][Duration]
    INPUT: List
    '''
    with open("test.csv", 'a', newline='') as excelFile:
        writer_object = writer(excelFile)
        writer_object.writerow(data)
        excelFile.close()

def mostRecent(LogGroupName):
    logName = "/aws/lambda/" + LogGroupName
    streamNames = client.describe_log_streams(logGroupName=logName, orderBy ='LastEventTime', descending = True)

    for name in streamNames.get("logStreams"):
        print(name)
    #FOR NOW JUST GET THE MOST RECENT LOG STREAM NAME
    streamName = streamNames.get("logStreams")[0].get("logStreamName")

    #Get Log events in response as a dictionary object
    response = client.get_log_events(logGroupName=logName, logStreamName = streamName)

    # for i in response.get('events'):
    #     print(i)

    #find where The duration is stored in the log events
    durationIndex = findDurationIndex(response)

    #Find the the function Duration at the index found above
    line = str(response.get('events')[durationIndex])
    duration = getDuration(line)

    #save it to a spreadsheet
    data = [logName, streamName, duration]
    enterDataToCSV(data)

def timeRange(LogGroupName):
    #find time range
    startTime = 0
    endTime = 0
    while(startTime >= endTime):
        startMonth = int(input("Enter Start Month: "))
        startDay = int(input("Enter Start Day: "))
        startYear = int(input("Enter Start Year: "))
        startHour = int(input("Enter Start Hour(0-23): "))
        startMin = int(input("Enter Start Minute(0-59): "))
        startSec = int(input("Enter Start Seconds(0-59): "))
        startTime = datetime.datetime(startYear,startMonth,startDay,startHour,startMin,startSec).timestamp()*1000
        print(startTime)

        endMonth = int(input("Enter End Month: "))
        endDay = int(input("Enter End Day: "))
        endYear = int(input("Enter End Year: "))
        endHour = int(input("Enter End Hour(0-23): "))
        endMin = int(input("Enter End Minute(0-59): "))
        endSec = int(input("Enter End Seconds(0-59): "))
        endTime = datetime.datetime(endYear,endMonth,endDay,endHour,endMin,endSec).timestamp()*1000
        print(endTime)
        if startTime >= endTime:
            print("Invalid Time Range")

    logName = "/aws/lambda/" + LogGroupName
    streamNames = client.describe_log_streams(logGroupName=logName, orderBy ='LastEventTime', descending = True)
    namesByCreationTime = []
    #find all stream names in the given durations and put it in the list
    for log in streamNames.get("logStreams"):
        if log.get("creationTime") >= startTime and log.get("creationTime") <= endTime:
            print(log.get("creationTime"))
            namesByCreationTime.append(log.get("logStreamName"))

    print(namesByCreationTime)
    for name in namesByCreationTime:
        #Get Log events in response as a dictionary object
        response = client.get_log_events(logGroupName=logName, logStreamName = name)
        #find where The duration is stored in the log events
        durationIndex = findDurationIndex(response)
        #Find the the function Duration at the index found above
        line = str(response.get('events')[durationIndex])
        duration = getDuration(line)
        #save it to a spreadsheet
        data = [logName, name, duration]
        enterDataToCSV(data)

def main(LogGroupName, timeQuery):
    if timeQuery == "N" or timeQuery =="n":
        mostRecent(LogGroupName)
    elif timeQuery == "Y" or timeQuery == "y":
        timeRange(LogGroupName)

if __name__ == "__main__":
    LogGroupName = input("Enter a Log Group Name(Q to quit): ")
    while LogGroupName != "Q":
        timeQuery = input("Want to input a time range?(Y or N): ")
        try:
            main(LogGroupName, timeQuery)
        except:
            print("Log Group Name does not exist")
        LogGroupName = input("Enter a Log Group Name(Q to quit): ")
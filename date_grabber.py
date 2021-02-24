import datetime

def getDate(string):
    days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    try:
        if string.isalpha():
            if string.lower() in days:
                for day in range(1,8):
                    checking_date = datetime.datetime.today() - datetime.timedelta(days=day)
                    if checking_date.strftime("%A").lower() == string.lower():
                        return [True, checking_date]
            elif string.lower() == "yesterday":
                todays_date = datetime.datetime.today()
                return [True, todays_date - datetime.timedelta(days=1)]
            elif string.lower() == "today":
                todays_date = datetime.datetime.today()
                return [True, todays_date]
            else:
                return [False,]
        else:
            deliminator = "-" if string.count("-") > 0 else "/"
            numbers = string.split(deliminator)
            if len(numbers) == 2:
                year = int(datetime.datetime.today().strftime("%Y"))
                month = int(numbers[0])
                day = int(numbers[1])
            elif len(numbers) == 3:
                year = int(numbers[2]) if len(numbers[2]) == 4 else int(numbers[2])+2000
                month = int(numbers[0])
                day = int(numbers[1])
            else:
                return [False,]

            return [True, datetime.datetime.combine(datetime.date(month=month, day=day, year=year), datetime.datetime.min.time())]
    except ValueError:
        return [False,]

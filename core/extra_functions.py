import datetime

def getStartDateAndEndDateOfWeek(end_date_time):

	end_date = end_date_time.split()[0]
	year = int(end_date.split('-')[0])
	month = int(end_date.split('-')[1])
	day = int(end_date.split('-')[2])

	current_date = datetime.date(year,month,day)

	Year,WeekNum,DOW = current_date.isocalendar()

	# d = current_date - datetime.timedelta(days=22)

	start_date_dict = {
		6: 0,
		7: 1,
		1: 2,
		2: 3,
		3: 4,
		4: 5,
		5: 6
	}

	start_date = current_date - datetime.timedelta(days=start_date_dict[DOW])

	end_date_dict = {
		6: 6,
		7: 5,
		1: 4,
		2: 3,
		3: 2,
		4: 1,
		5: 0
	}

	end_date = current_date + datetime.timedelta(days=end_date_dict[DOW])

	return_date = str(start_date) + "/" + str(end_date)

	return(return_date)

def displayErrors(error):
	# Errors -> Dictionary of Errors
	message = ""
	dict_keys = error.keys()
	for i, key in enumerate(dict_keys):
		if i == 0:
			message = message + "Error: " + key  + " - " + error[key][0]
		else:
			message = message + ", " + key + " - " + error[key][0]

	return message

def convertDateStringToDate(dateVal):
	# Assume datevale is of the following format YEAR-MONTH-DATE'T'HOUR:MIN:SEC.MS'Z' (ex. 2020-12-24T22:38:00.000Z)
	dateVal = dateVal[:-1]
	dateVal = dateVal + "+0800"
	dateVal = datetime.datetime.strptime(dateVal, "%Y-%m-%dT%H:%M:%S.%f%z")

	return dateVal

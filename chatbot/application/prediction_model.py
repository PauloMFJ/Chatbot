import requests, json, psycopg2, math, numpy

def read_password(file):
    reader = open(file, 'r')
    txt = reader.read();
    reader.close()
    return txt

def get_conn():
    return psycopg2.connect(dbname='postgres', host='localhost', user='postgres', password=read_password('..\..\..\password.txt'))

def create_db_table():
    try:
        conn = None
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS history (from_Loc TEXT, to_Loc TEXT, est_Depart float, actual_Depart float, est_Arrival float, actual_Arrival float, delay float)')
        conn.commit()
    except Exception as exception:
        print("Error:", exception)
    finally:
        if conn:
            conn.close()

def insert_into_db(origin, destination, estDepart, actDepart, estArrival, actArrival, delay):
    try:
        conn = None
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history(from_Loc, to_Loc, est_Depart, actual_Depart, est_Arrival, actual_Arrival, delay) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (origin, destination, estDepart, actDepart, estArrival, actArrival, delay))
        conn.commit()
    except Exception as exception:
        print("Error:", exception)
    finally:
        if conn:
            conn.close()

api_urlM = "https://hsp-prod.rockshore.net/api/v1/serviceMetrics"
api_urlD = "https://hsp-prod.rockshore.net/api/v1/serviceDetails"
headers = { "Content-Type": "application/json" }
auths = ("qke16pwu@uea.ac.uk", "AICoursework1@")

#Returns the JSON with CRS code of a station
def get_crs(locName):
    URL = "http://transportapi.com/v3/uk/places.json?query=%s&type=train_station&app_id=a6a49dd6&app_key=4e5744ed4cbc17940103827c1b3abb3d" % locName
    CRS = requests.get(URL, auth=('a6a49dd6', '4e5744ed4cbc17940103827c1b3abb3d'))
    
    data = CRS.json().get('member') #Gets a list of dictionaries
        
    if not data:
        stationCode = ["None"]
        return stationCode
        
    elif data:
        stationCode = data[0].get('station_code')
        return stationCode

# Get train history - returns a list of RIDs
def get_metricsRIDs(fromLoc, toLoc, fromTime, toTime, fromDate, toDate):
    data = {
                "from_loc": fromLoc,
                "to_loc": toLoc,
                "from_time": fromTime,
                "to_time": toTime,
                "from_date": fromDate,
                "to_date": toDate,
                "days": "WEEKDAY"
                }
    
    metrics = requests.post(api_urlM, headers=headers, auth=auths, json=data)
    metrics = metrics.json().get("Services")
    
    if not metrics:
        aList = ["None"]
        return aList
    
    elif metrics:
        aList = []
        
        for i in metrics:
            ridList = i.get("serviceAttributesMetrics").get("rids")
            for j in ridList:
                aList.append(j)
        
    return aList
    
#Get train info
def get_details(RIDnum):
    RID = {
            "rid": RIDnum
            }
    
    details = requests.post(api_urlD, headers=headers, auth=auths, json=RID)
    return details.json()

def get_from_crs(fromLocName):
    fromLoc = get_crs(fromLocName)
    if(fromLoc[0] is "None"):
        print("Sorry, current location not found. Please try again.")
    else:
        return fromLoc
    
def get_dest_crs(destLocName):
    destLoc = get_crs(destLocName)
    if(destLoc[0] is "None"):
        print("Sorry, destination location not found. Please try again.")
    else:
        return destLoc
    
def get_all_details(metricsRIDs):
    if(metricsRIDs[0] is "None"):
        print("Sorry, route history not found. Please try again.")
    elif(metricsRIDs[0] is not "None"):
        details = []
        for d in metricsRIDs:
            details.append(get_details(d))
        
        return details

def get_history(fromLocName, destLocName, fromTime, toTime, fromDate, toDate):
    #Get CRS codes
    fromLoc = get_from_crs(fromLocName)
    destLoc = get_dest_crs(destLocName)
    
    # Get Metrics
    metricsRIDs = get_metricsRIDs(fromLoc, destLoc, fromTime, toTime, fromDate, toDate)
    #print(metricsRIDs)
    
    # Get Details
    details = get_all_details(metricsRIDs)
    return details

def fill_table(details):
    for d in details:
        try:
            origin = d['serviceAttributesDetails']['locations'][0]['location']
            destination = d['serviceAttributesDetails']['locations'][-1]['location']
            estDepart = int(d['serviceAttributesDetails']['locations'][0]['gbtt_ptd'])
            actDepart = int(d['serviceAttributesDetails']['locations'][0]['actual_td'])
            estArrival = int(d['serviceAttributesDetails']['locations'][-1]['gbtt_pta'])
            actArrival = int(d['serviceAttributesDetails']['locations'][-1]['actual_ta'])
            delay = (actArrival - actDepart) - (estArrival - estDepart)
    
            insert_into_db(origin, destination, estDepart, actDepart, estArrival, actArrival, delay)
        except Exception as exception:
            print("Error:", exception)

def predict_delay(origin, destination, estDepart, estArrival, delaytime):
    origin = get_from_crs(origin)
    destination = get_from_crs(destination)

    try:
        conn = None
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history WHERE from_loc = %s AND to_loc = %s",\
                       [origin, destination])
        rows = cursor.fetchall()
        
    except Exception as exception:
        print("Error:", exception)
    finally:
        if conn:
            conn.close()
    if rows:
        result = []
        for r in rows:
            distance = math.sqrt(((int(estDepart) - int(r[2]))**2) + ((int(estArrival) - int(r[4]))**2) + ((int(delaytime) - int(r[6]))**2))
            aRow = list(r)
            aRow.append(distance)
            result.append(aRow)

        # Referencing https://stackoverflow.com/questions/17555218/python-how-to-sort-a-list-of-lists-by-the-fourth-element-in-each-list
        result.sort(key=lambda x:x[7])

        estArr = []
        for i in range(10):
            length = len(str(result[i][4]))
            time = str(result[i][5])
            
            if length is 5:
                hours = int(time[0]) * 60
                minutes = int(time[1] + time[2])
                estArr.append(hours + minutes)
            elif length is 6:
                hours = int(time[0] + time[1]) * 60
                minutes = int(time[2] + time[3])
                estArr.append(hours + minutes)
                
        predictedTime = int(numpy.mean(estArr))
        
        # Referencing https://stackoverflow.com/questions/17555218/python-how-to-sort-a-list-of-lists-by-the-fourth-element-in-each-list
        predictedTime = '{:02d}:{:02d}'.format(*divmod(predictedTime, 60))
        
        Message.emit_feedback('display received message', 'prediction', predictedTime)
    else:
        Message.emit_feedback('display received message', 'prediction_error')

# Executed when getting train history and building database
#details = get_history("Norwich", "London Liverpool street", "0700", "0900", "2017-01-01", "2018-12-31")
#create_db_table()
#fill_table(details)
#predict_delay("NRW", "LST", "700", "900", "20")

# --- TESTING ---
def get_metric():
    data = { "from_loc": "NRW",
             "to_loc": "LST",
             "from_time": "0700",
             "to_time": "0800",
             "from_date": "2016-07-01",
             "to_date": "2016-08-01",
             "days": "SATURDAY"}

    m = requests.post(api_urlM, headers=headers, auth=auths, json=data)
    print(json.dumps(json.loads(m.text), sort_keys=True, indent=2, separators=(',',': ')))
    
def get_detail():
    RID = {"rid":"201607294212242"}
    
    d = requests.post(api_urlD, headers=headers, auth=auths, json=RID)
    print(json.dumps(json.loads(d.text), sort_keys=True, indent=2, separators=(',',': ')))

#get_metric()
#get_detail()
# -------

from __main__ import Message
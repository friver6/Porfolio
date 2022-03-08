import json, sqlite3
from urllib.request import urlopen
from bottle import get, post, request, template, run

#Function to make API requests
def apiRequest(uAddress):
    with urlopen(uAddress) as apiResp:
        rawInfo = apiResp.read()

    rData = json.loads(rawInfo)
    return rData

# Function to make the list of works.
def getWorks(writerName):
    workList = []
    # Cleans user input and concatenates it to API url.
    authInfo = "https://openlibrary.org/search.json?author=" + writerName.replace(" ", "+")

    # Obtains information from the API in the form of a json object.
    req1 = apiRequest(authInfo)

    # Creates a list of tuples from the raw data.
    # If it can't find first publication year, it inputs 0.
    for number in range(len((req1["docs"]))):
        workList.append((req1["docs"][number]["title_suggest"].lower(), req1["docs"][number].get("first_publish_year", 0)))
    
    # Sorts the list by the second item of the tuples.
    workList.sort(key=lambda x:x[1])

    # Gets rid of duplicates (even ones with different case)
    check_val = set()
    retList = []
    for i in workList:
        if i[0] not in check_val:
            retList.append(i)
            check_val.add(i[0])

    return retList

#Creates database and table.
def dbTransfer(sampList):
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS aBooks 
        (booktitle text, year integer)
        ''')

    for a, b in sampList:
        c.execute("INSERT INTO abooks (booktitle, year) VALUES (?, ?)", (a, b))

    c.execute("DELETE FROM abooks WHERE year = 0")

    conn.commit()

    c.execute("SELECT * FROM abooks")

    result = c.fetchall()

    c.close()
    
    return result

# Functions below uses the Bottle web framework as user interface.
@get('/')
def nameGet():
    return '''
        <p>Displays list of works by author.</p>
        <form action="/" method="post">
            Enter author's name: <input name="authName" type="text" />
            <input value="Lookup" type="submit" />
        </form>
    '''

@post('/')
def do_nameGet():
    authName = request.forms.get("authName")
    bookList = getWorks(authName)
    aWorks = dbTransfer(bookList)
        
    return template('aWorks.html', rows=aWorks)

run(host='localhost', port=8080)

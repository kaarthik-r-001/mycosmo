from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user data for demonstration purposes
users = [
    {'username': 'user1', 'password': 'password'},
    {'username': 'user2', 'password': generate_password_hash('password2')}
]
mydb = mysql.connector.connect(
        host="localhost",
        password="password",
        user="root",
        database="hackathon"
    )
mycursor = mydb.cursor()
def registerUser(username,password,skills,userType):
    if userType == "EMPLOYEE":
        query = "INSERT INTO employee values(%s,%s,%s,%s)"
        data = (username,'name','email',password)
        mycursor.execute(query,data)
        mydb.commit()
        for skill in skills:
            query = "INSERT INTO empskills values(%s,%s)"
            data = (username,skill)
            mycursor.execute(query,data)
            mydb.commit()
    elif userType == "EMPLOYER":
        query = "INSERT INTO employer values(%s,%s,%s,%s)"
        data = (username,'name','email',password)
        mycursor.execute(query,data)
        mydb.commit()

def getUsers(type):
    if type == "EMPLOYEE":
        query = "SELECT empID FROM employee"
        mycursor.execute(query)
        result = mycursor.fetchall()
        return result
    elif type == "EMPLOYER":
        query = "SELECT emplrID FROM employer"
        mycursor.execute(query)
        result = mycursor.fetchall()
        return result
#fn to validate the user using given userid pass and usertype
def validateUser(username,password,userType):
    users = [i[0] for i in getUsers(userType)]
    if username not in users:
        return False
    if userType == "EMPLOYEE":
        query = "SELECT * FROM employee WHERE empID = %s"
        data = (username,)
        mycursor.execute(query,data)
        result = mycursor.fetchall()
        if result[0][3] == password:
            return True
        else:
            return False
    elif userType == "EMPLOYER":
        query = "SELECT * FROM employer WHERE emplrID = %s"
        data = (username,)
        mycursor.execute(query,data)
        result = mycursor.fetchall()
        if result[0][3] == password:
            return True
        else:
            return False
        
def getJobsofEmployer(username):
    query = "SELECT * FROM jobs WHERE emplrID = %s"
    data = (username,)
    mycursor.execute(query,data)
    result = mycursor.fetchall()
    return result


def getJobskillsofEmployer(username):
    query = "SELECT * FROM jobskills WHERE jid IN (SELECT jid FROM jobs WHERE emplrID = %s)"
    data = (username,)
    mycursor.execute(query,data)
    result = mycursor.fetchall()
    return result

def EmployeeCompatableJobs(username):
    query = "SELECT * FROM jobs WHERE jid IN (SELECT jid FROM jobskills WHERE skill IN (SELECT skill FROM empskills WHERE empID = %s))"
    data = (username,)
    mycursor.execute(query,data)
    result = mycursor.fetchall()
    return result
def getSkillsofJobs(jobs):
    skills = []
    for job in jobs:
        query = "SELECT * FROM jobskills WHERE jid = %s"
        data = (job[0],)
        mycursor.execute(query,data)
        result = mycursor.fetchall()
        skills+=result
    return skills
def getEmployeeSkills(username):
    query = "SELECT skill FROM empskills WHERE empID = %s"
    data = (username,)
    mycursor.execute(query,data)
    result = mycursor.fetchall()
    return result
def getEmployeeDetails(username):
    query = "SELECT * FROM employee WHERE empID = %s"
    data = (username,)
    mycursor.execute(query,data)
    result = mycursor.fetchall()
    return result




@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        if session['userType'] == "EMPLOYEE":
            return render_template('employeeHome.html',msg="Welcome, "+session['username']+"!",data = EmployeeCompatableJobs(session['username']),skills = getSkillsofJobs(EmployeeCompatableJobs(session['username'])))
        elif session['userType'] == "EMPLOYER":
            return render_template('employerHome.html',msg="Welcome, "+session['username']+"!",data = getJobsofEmployer(session['username']),skills = getJobskillsofEmployer(session['username']) )
        return f'Welcome, {session["username"]}!'
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        userType = data['userType']
        if validateUser(username,password,userType):
            session['username'] = username
            session['userType'] = userType
            if session['userType'] == "EMPLOYEE":
                return render_template('employeeHome.html',msg="Welcome, "+session['username']+"!",data = EmployeeCompatableJobs(session['username']),skills = getSkillsofJobs(EmployeeCompatableJobs(session['username'])) )
            elif session['userType'] == "EMPLOYER":
                return render_template('employerHome.html',msg="Welcome, "+session['username']+"!",data = getJobsofEmployer(session['username']),skills = getJobskillsofEmployer(session['username']) )
            return f'Welcome, {session["username"]}!'
        else:
            return "Invalid username or password"
        
        
        #     return f'Welcome, {session["username"]}!'
        # else:
        #     return 'Invalid username or password'
    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request)
        
        users =[i[0] for i in getUsers("EMPLOYEE")] 
        print(users)
        try:
        # xhr.send(JSON.stringify({username:username,password:password,li:li})) code to get the data from the front end
            data = request.get_json()
            
            username = data['username']
            password = data['password']
            if username in users:
                return 'User already exists'
            skills = data['li']
            userType = data['userType']
            registerUser(username,password,skills,userType)
        except Exception as e:
            print(e.args)
            return 'error: '+str(e.args)
            

        
        
      
        #users.append({'username': username, 'password': generate_password_hash(password)})
        return render_template('login.html')
    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        if session['userType'] == "EMPLOYEE":
            return render_template('profile.html',data = getEmployeeDetails(session['username'])[0],skills = getEmployeeSkills(session['username']))
        else:
            redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'username' in session:
        if session['userType'] == "EMPLOYEE":
            return render_template('employeeHome.html',msg="Welcome, "+session['username']+"!",data = EmployeeCompatableJobs(session['username']),skills = getSkillsofJobs(EmployeeCompatableJobs(session['username'])))
        elif session['userType'] == "EMPLOYER":
            return render_template('employerHome.html',msg="Welcome, "+session['username']+"!",data = getJobsofEmployer(session['username']),skills = getJobskillsofEmployer(session['username']) )
        return f'Welcome, {session["username"]}!'
    return render_template('login.html')


#logout
@app.route('/logout',methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/addjob',methods=['GET','POST'])
def addjob():
    if 'username' in session:
        if session['userType'] == 'EMPLOYER':
            if request.method == 'POST':
                data = request.get_json()
                jobTitle = data['jobTitle']
                jobDesc = data['description']
                skills = data['skills']
                query = "INSERT INTO jobs(emplrID,title,description) values(%s,%s,%s)"
                data = (session['username'],jobTitle,jobDesc)
                mycursor.execute(query,data)
                mydb.commit()
                fetch = "SELECT jid FROM jobs WHERE title = %s and description = %s"
                data = (jobTitle,jobDesc)
                mycursor.execute(fetch,data)
                result = mycursor.fetchall()
                jid = result[0][0]

                query = "Insert into jobskills values(%s,%s)"
                
                for skill in skills:
                    data = (jid,skill)
                    mycursor.execute(query,data)
                    mydb.commit()
                
                data = (jobTitle,skills)
                return "Job added successfully"
            else:
                return render_template('addjob.html')
        else:
            return "You are not authorized to access this page"
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True,port=4000)
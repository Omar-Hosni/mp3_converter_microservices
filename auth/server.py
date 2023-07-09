import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

app = Flask(__name__)
mysql = MySQL(app)

# Configure MySQL connection
db = mysql.connect(
    host=os.environ.get("MYSQL_HOST"),
    user=os.environ.get("MYSQL_USERNAME"),
    password=os.environ.get("MYSQL_PASS"),
    database='my_db'
)

@app.route('/', methods=['GET'])
def hello():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user")
    result = cursor.fetchall()
    return str(result)

def createJWT(username, secret, authz):
    return jwt.decode(
        {
            "username":username,
            "exp":datetime.datetime.now(tz=datetime.timezon.est) + datetime.timedelta(days=1),
            "iat":datetime.datetime.utcnow(),
            "admin":authz
        },
        secret,
        algorithm="HS256"
    )

@app.route('/login',methods=['POST'])
def login():
    auth = request.authorization
    if not auth:
        return "missing credemtials",401

    #check db for username and password
    cur = db.cursor()
    res = cur.execute("select email, password from user where email=%s", (auth.username))
    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

    if email == auth.username and password == auth.password:
        return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials",401

@app.route('/validate',methods=['POST'])
def validate():
    encoded_jwt = request.headers['Authorization']

    if not encoded_jwt:
        return "missing credentials", 401


    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt,
            os.environ.get("JWT_SECRET"),
            algorithm=["HS256"]
        )
    except:
        return "unauthorized", 401

    return decoded, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

import os
import pathlib
import asyncio
import sqlite3
import requests
import openai
from flask import Flask, session, abort, redirect, request, render_template, jsonify, make_response
import jwt
import datetime
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask("Google Login App")
openai.api_key = "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"
app.config['SECRET_KEY'] = 'ccf07ef2cb3c4233ae412249e4c13baa'
app.secret_key = "CodeSpecialist.com"
# only one account accept at 1 time
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.system('pip install flask[async]')
GOOGLE_CLIENT_ID = "67060647569-9p4hm9vosbq96d7endki97ielvp2ck94.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


async def rows_value(id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('select * from paraphrasing where user_id = ? ORDER by id DESC;', [id])
    result = cur.fetchall()
    con.commit()
    con.close()
    return result


async def rows_value_grammar(id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('select * from grammar_check where user_id = ? ORDER by id DESC;', [id])
    result = cur.fetchall()
    con.commit()
    con.close()
    return result


async def rows_value_pla(id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('select * from plagiarism_checker where user_id = ? ORDER by id DESC;', [id])
    result = cur.fetchall()
    con.commit()
    con.close()
    return result


async def insert_value_grammar(input, output, id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO grammar_check(input,output,user_id) VALUES (?,?,?)', (input, output, id))
    con.commit()
    con.close()


async def rows_value_completion(id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('select * from text_completion where user_id = ? ORDER by text_completion_id DESC;', [id])
    result = cur.fetchall()
    con.commit()
    con.close()
    return result


async def insert_value_para(input, output, id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO paraphrasing(input,output,user_id) VALUES (?,?,?)', (input, output, id))
    con.commit()
    con.close()

async def insert_value_pla(input, output, id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO plagiarism_checker(input,output,user_id) VALUES (?,?,?)', (input, output, id))
    con.commit()
    con.close()


async def insert_value_completion(input, output, id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO text_completion(input,output,user_id) VALUES (?,?,?)', (input, output, id))
    con.commit()
    con.close()



def check_user(id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT * from user where id = ?;', [id])
    result = cur.fetchall()
    con.commit()
    con.close()
    if result:
        return True
    else:
        return False


def register_user_to_db(id, name, email, profile_pic):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO user(id,name,email,profile_pic) values (?,?,?,?)', (id, name, email, profile_pic))
    con.commit()
    con.close()


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session["a"] = id_info
    session["id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["profile_pic"] = id_info.get("picture")
    # check user to insert db
    if not check_user(session["id"]):
        register_user_to_db(session["id"], session["name"], session["email"], session["profile_pic"])
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# home page
@app.route("/")
def index():
    # redirect /login
    html = "Hello World <a href='/login'><button>Login</button></a>"
    return render_template('index.html')


# main page
@app.route("/protected_area")
@login_is_required
def protected_area():
    # return f"Hello  {session['name']}! <a> {session['email']} </a> <br/> <a> {session['id']} </a> <img src='{session['profile_pic']}' " \
    #        f"alt='Google profile pic'></img> <br/> <a>'{session['a']}'</a> <br/> <a " \
    #        f"href='/logout'><button>Logout</button></a>"
    token = jwt.encode(
        payload={'id': session["id"], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, key='secret',
        algorithm="HS256")
    token_id = jwt.decode(jwt=token, key='secret', algorithms=["HS256"])
    pic = session["profile_pic"].replace("/","_")
    return render_template("main.html", token_id=token_id.get('id'), name=session["name"],pic = pic)


@app.route("/paraphrasing/<id>/<pic>/<name>", methods=['POST', 'GET'])
async def paraphare(id,pic,name):
    pic = str(pic)
    name = str(name)
    if request.method == 'GET':
        id = id.strip("#")
        rows_para = await rows_value(id)
        return render_template("paraphrase.html",rows_para=rows_para,pic=pic,name=name)
    else:
        para_input = request.form["para_input"].strip()
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "user", "content": f"paraphrase \"{para_input}\""}])
        output_para = completion.choices[0].message.content

        input = para_input
        output = output_para
        id = id.strip("#")
        await insert_value_para(input, output, id)
        rows_para = await rows_value(id)
        return render_template("paraphrase.html", output_para=output_para, rows_para=rows_para,pic=pic,name=name)


@app.route("/plagiarism/<id>/<pic>/<name>", methods=['POST', 'GET'])
async def plagiarism(id,pic,name):
    pic = str(pic)
    name = str(name)
    if request.method == 'GET':
        id = id.strip("#")
        rows_pla = await rows_value_pla(id)
        return render_template("plagiarism.html", rows_pla=rows_pla,pic=pic,name=name)
    else:
        pla_input = request.form["pla_input"].strip()
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "user", "content": f"Find Plagiarism \"{pla_input}\""}])
        output_pla = completion.choices[0].message.content

        input = pla_input
        output = output_pla
        id = id.strip("#")
        await insert_value_pla(input, output, id)
        rows_pla = await rows_value_pla(id)
        return render_template("plagiarism.html", output_pla=output_pla, rows_pla=rows_pla,pic=pic,name=name)


@app.route("/completion/<id>/<pic>/<name>", methods=['POST', 'GET'])
async def completion(id,pic,name):
    pic = str(pic)
    name = str(name)
    if request.method == 'GET':
        id = id.strip("#")
        rows_completion = await rows_value_completion(id)
        return render_template("completion.html",rows_completion=rows_completion,pic=pic,name=name)
    else:
        completion_input = request.form["completion_input"].strip()
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "user", "content": f"Complete the following passage  \"{completion_input}\""}])
        output_completion = completion.choices[0].message.content

        input = completion_input
        output = output_completion
        id = id.strip("#")
        await insert_value_completion(input, output, id)
        rows_completion = await rows_value_completion(id)
        return render_template("completion.html", output_completion=output_completion, rows_completion=rows_completion,pic=pic,name=name)


@app.route("/grammar/<id>/<pic>/<name>", methods=['POST', 'GET'])
async def grammar(id,pic,name):
    pic = str(pic)
    name = str(name)
    if request.method == 'GET':
        id = id.strip("#")
        rows_grammar = await rows_value_grammar(id)
        return render_template("grammar.html",rows_grammar=rows_grammar,pic=pic,name=name)
    else:
        grammar_input = request.form["grammar_input"].strip()
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "user", "content": f"Check error grammar and spelling error  \"{grammar_input}\""}])
        output_grammar = completion.choices[0].message.content
        input = grammar_input
        output = output_grammar
        id = id.strip("#")
        await insert_value_grammar(input, output, id)
        rows_grammar = await rows_value_grammar(id)
        return render_template("grammar.html", output_grammar=output_grammar, rows_grammar=rows_grammar,pic=pic,name=name)

if __name__ == '__main__':
    app.run(debug=True)

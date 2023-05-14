# paraphrasing: line 259
# plagiarism: line 294
# completion: 350
# grammar: 388
from gingerit.gingerit import GingerIt
from flask import Flask, session, abort, redirect, request, render_template, jsonify, make_response
import openai
import os
import datetime
import jwt
import sqlite3
import requests
import pathlib
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask(__name__, template_folder='templates', static_folder='static')

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
  scopes=[
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email", "openid"
  ],
  redirect_uri="http://127.0.0.1:5000/callback")


async def rows_value(id):
  con = sqlite3.connect('database.db')
  cur = con.cursor()
  cur.execute('select * from paraphrasing where user_id = ? ORDER by id DESC;',
              [id])
  result = cur.fetchall()
  con.commit()
  con.close()
  return result


async def rows_value_grammar(id):
  con = sqlite3.connect('database.db')
  cur = con.cursor()
  cur.execute(
    'select * from grammar_check where user_id = ? ORDER by id DESC;', [id])
  result = cur.fetchall()
  con.commit()
  con.close()
  return result


async def rows_value_pla(id):
  con = sqlite3.connect('database.db')
  cur = con.cursor()
  cur.execute(
    'select * from plagiarism_checker where user_id = ? ORDER by id DESC;',
    [id])
  result = cur.fetchall()
  con.commit()
  con.close()
  return result


async def insert_value_grammar(input, output, id):
  con = sqlite3.connect('database.db')
  cur = con.cursor()
  cur.execute('INSERT INTO grammar_check(input,output,user_id) VALUES (?,?,?)',
              (input, output, id))
  con.commit()
  con.close()


async def rows_value_completion(id):
  con = sqlite3.connect('database.db')
  cur = con.cursor()
  cur.execute(
    'select * from text_completion where user_id = ? ORDER by text_completion_id DESC;',
    [id])
  result = cur.fetchall()
  con.commit()
  con.close()
  return result


async def insert_value_para(input, output, id):
  con = sqlite3.connect('database.db')
  cur = con.cursor()
  cur.execute('INSERT INTO paraphrasing(input,output,user_id) VALUES (?,?,?)',
              (input, output, id))
  con.commit()
  con.close()


async def insert_value_pla(input, output, id):
  con = sqlite3.connect('database.db')
  cur = con.cursor()
  cur.execute(
    'INSERT INTO plagiarism_checker(input,output,user_id) VALUES (?,?,?)',
    (input, output, id))
  con.commit()
  con.close()


async def insert_value_completion(input, output, id):
  con = sqlite3.connect('database.db')
  cur = con.cursor()
  cur.execute(
    'INSERT INTO text_completion(input,output,user_id) VALUES (?,?,?)',
    (input, output, id))
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
  cur.execute('INSERT INTO user(id,name,email,profile_pic) values (?,?,?,?)',
              (id, name, email, profile_pic))
  con.commit()
  con.close()


def get_bigrams(string):
  """
    Take a string and return a list of bigrams.
    """
  if string is None:
    return ""

  s = string.lower()
  return [s[i:i + 2] for i in list(range(len(s) - 1))]


def simon_similarity(str1, str2):
  """
    Perform bigram comparison between two strings
    and return a percentage match in decimal form.
    """
  pairs1 = get_bigrams(str1)
  pairs2 = get_bigrams(str2)
  union = len(pairs1) + len(pairs2)

  if union == 0 or union is None:
    return 0

  hit_count = 0
  for x in pairs1:
    for y in pairs2:
      if x == y:
        hit_count += 1
        break
  return (2.0 * hit_count) / union


def login_is_required(function):

  def wrapper(*args, **kwargs):
    if "id" not in session:
      return abort(401)  # Authorization required
    else:
      return function()

  return wrapper


@app.route("/")
def index():
  # redirect /login
  return render_template('loginPage.html')


@app.route("/login")
def login():
  authorization_url, state = flow.authorization_url()
  session["state"] = state
  return redirect(authorization_url)


@app.route("/logout")
def logout():
  session.clear()
  return render_template('loginPage.html')


@app.route("/callback")
def callback():
  flow.fetch_token(authorization_response=request.url)
  if not session["state"] == request.args["state"]:
    abort(500)  # State does not match!
  credentials = flow.credentials
  request_session = requests.session()
  cached_session = cachecontrol.CacheControl(request_session)
  token_request = google.auth.transport.requests.Request(
    session=cached_session)

  id_info = id_token.verify_oauth2_token(id_token=credentials._id_token,
                                         request=token_request,
                                         audience=GOOGLE_CLIENT_ID)
  session["a"] = id_info
  session["id"] = id_info.get("sub")
  session["name"] = id_info.get("name")
  session["email"] = id_info.get("email")
  session["profile_pic"] = id_info.get("picture")
  # check user to insert db
  if not check_user(session["id"]):
    register_user_to_db(session["id"], session["name"], session["email"],
                        session["profile_pic"])
  return redirect("/protected_area")


@app.route("/protected_area")
@login_is_required
def protected_area():
  # return f"Hello  {session['name']}! <a> {session['email']} </a> <br/> <a> {session['id']} </a> <img src='{session['profile_pic']}' " \
  #        f"alt='Google profile pic'></img> <br/> <a>'{session['a']}'</a> <br/> <a " \
  #        f"href='/logout'><button>Logout</button></a>"
  token = jwt.encode(payload={
    'id':
    session["id"],
    'exp':
    datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
  },
                     key='secret',
                     algorithm="HS256")
  token_id = jwt.decode(jwt=token, key='secret', algorithms=["HS256"])
  pic = session["profile_pic"].replace("/", "_")
  return render_template("main.html",
                         token_id=token_id.get('id'),
                         name=session["name"],
                         pic=pic)


@app.route("/paraphrasing/<id>/<pic>/<name>", methods=['POST', 'GET'])
async def paraphare(id, pic, name):
  pic = str(pic)
  name = str(name)
  if request.method == 'GET':
    id = id.strip("#")
    rows_para = await rows_value(id)
    return render_template("paraphrase.html",
                           rows_para=rows_para,
                           id=id,
                           pic=pic,
                           name=name)
  else:
    para_input = request.form["para_input"].strip()ádfasd
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                              messages=[{
                                                "role":
                                                "user",
                                                "content":
                                                f"paraphrase \'{para_input}\'"
                                              }])
    output_para = completion.choices[0].message.content

    input = para_input
    output = output_para
    id = id.strip("#")
    await insert_value_para(input, output, id)
    rows_para = await rows_value(id)
    return render_template("paraphrase.html",
                           output_para=output_para,
                           id=id,
                           rows_para=rows_para,
                           pic=pic,
                           name=name)


@app.route("/plagiarism/<id>/<pic>/<name>", methods=['POST', 'GET'])
async def plagiarism(id, pic, name):
  pic = str(pic)
  name = str(name)
  if request.method == 'GET':
    id = id.strip("#")
    rows_pla = await rows_value_pla(id)
    return render_template("plagiarism.html",
                           rows_pla=rows_pla,
                           id=id,
                           pic=pic,
                           name=name)
  else:
    pla_input = request.form["pla_input"].strip()
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{
        "role":
        "user",
        "content":
        f"get links of websites went i search the content \'{pla_input}\'"
      }])
    output = completion.choices[0].message.content
    outputArray = output.split(" ")
    print(outputArray)
    input = pla_input
    linkArrays = []
    output_pla = ""
    percent = 0
    x = 0
    for element in outputArray:
      if element.__contains__("http"):
        link = element.split('\n')[0]
        output_pla += link + "\n"
        f = requests.get(link)
        x += 1
        percent += float(simon_similarity(input, f.text))
    if (x != 0):
      percent = int(percent * 100 / x)
      output_pla += "\n" + "The percentage of plagiarism of the above paragraph is: " + str(
        percent)
    else:
      output_pla = "Sorry I cannot check plagiarism of your text!"
    id = id.strip("#")
    await insert_value_pla(input, output_pla, id)
    rows_pla = await rows_value_pla(id)
    return render_template("plagiarism.html",
                           output_pla=output_pla,
                           id=id,
                           rows_pla=rows_pla,
                           pic=x,
                           name=name)


@app.route("/completion/<id>/<pic>/<name>", methods=['POST', 'GET'])
async def completion(id, pic, name):
  pic = str(pic)
  name = str(name)
  if request.method == 'GET':
    id = id.strip("#")
    rows_completion = await rows_value_completion(id)
    return render_template("completion.html",
                           rows_completion=rows_completion,
                           id=id,
                           pic=pic,
                           name=name)
  else:
    completion_input = request.form["completion_input"].strip()
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{
        "role":
        "user",
        "content":
        f"Complete the following passage  \'{completion_input}\'"
      }])
    output_completion = completion.choices[0].message.content

    input = completion_input
    output = output_completion
    id = id.strip("#")
    await insert_value_completion(input, output, id)
    rows_completion = await rows_value_completion(id)
    return render_template("completion.html",
                           output_completion=output_completion,
                           rows_completion=rows_completion,
                           id=id,
                           pic=pic,
                           name=name)


@app.route("/grammar/<id>/<pic>/<name>", methods=['POST', 'GET'])
async def grammar(id, pic, name):
  pic = str(pic)
  name = str(name)
  if request.method == 'GET':
    id = id.strip("#")
    rows_grammar = await rows_value_grammar(id)
    return render_template("grammar.html",
                           rows_grammar=rows_grammar,
                           id=id,
                           pic=pic,
                           name=name)
  else:
    grammar_input = request.form["grammar_input"].strip()
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{
        "role":
        "user",
        "content":
        f"Highlight the errors and suggest some correction of \'{grammar_input}\'"
      }])
    output_grammar = completion.choices[0].message.content
    input = grammar_input
    output = output_grammar
    listWrongKey = []
    id = id.strip("#")
    correct = GingerIt().parse(input)
    await insert_value_grammar(input, output, id)
    rows_grammar = await rows_value_grammar(id)
    for key, value in correct.items():
      if key == "corrections":
        listCorrect = value
    for dictCorrect in listCorrect:
      for key, value in dictCorrect.items():
        if key == "text":
          listWrongKey.append(dictCorrect[key])

    # x = []
    # for key, value in correct.items():
    #   if key == "text":
    #     inputText = value

    # for wrongText in listWrongKey:
    #   inputText = inputText.replace(wrongText, '-' + wrongText + '+')
    # x.append(inputText)
    # x.append(output_grammar)
    # print(x)
    return render_template("grammar.html",
                           output_grammar=output_grammar,
                           rows_grammar=rows_grammar,
                           id=id,
                           pic=pic,
                           name=name)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)

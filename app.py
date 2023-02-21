from flask import Flask, render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import dateutil.parser as dparser
from datetime import datetime

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///todo.sqlite'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db=SQLAlchemy(app)
app.app_context().push()

class Todo(db.Model):
    __tablename__="toDo"

    id=db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Text)
    due_date = db.Column(db.Date, default=datetime.now)
    complete = db.Column(db.Boolean,default=False)

    def __init__(self, task, due_date,complete):
        self.task = task
        self.due_date = due_date
        self.complete = complete

    def __repr__(self):
        return "{} - {} - {}".format(self.task,self.due_date, self.complete)

db.create_all()


@app.route('/')
@app.route('/<sorted>')
def index(sorted=None):
    # todos=Todo.query.all()

    if sorted == "Asc":
        incomplete = Todo.query.order_by(Todo.due_date).filter_by(complete=False).all()
    elif sorted == "Desc":
        incomplete = Todo.query.order_by(Todo.due_date.desc()).filter_by(complete=False).all()
    elif not sorted:
        incomplete = Todo.query.filter_by(complete=False).all()
    else:
        return render_template("404.html")

    complete = Todo.query.filter_by(complete=True).all()

    return render_template('index.html',incomplete=incomplete,complete=complete)


@app.route('/add',methods=['POST'])
def add():
    todo=Todo(task=request.form['todoitem'],due_date=dparser.parse(request.form['due_date']).date(),complete=False)
    db.session.add(todo)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/<action>/<id>')
@app.route('/<action>',methods=['POST'])
def edit(action,id=None):
    if request.method == "POST":
        id=request.form.get('id')

    if not id or not id.isnumeric():
        return render_template("404.html")

    todo=Todo.query.filter_by(id=id).first()

    if not todo:
        return render_template("404.html")

    if action in ('complete','move'):
        todo.complete = action=='complete'

    elif action == 'update':
        todo.task = request.form['update-task']
        todo.due_date = dparser.parse(request.form['due-date']).date()

    elif action == 'delete':
        db.session.delete(todo)

    else:
        return render_template("404.html")

    db.session.commit()
    return redirect(url_for('index'))


@app.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        search = request.form['searchtask']
        tasks_complete = Todo.query.filter(Todo.task.like('%'+search+'%')).filter(Todo.complete==True)
        tasks_incomplete = Todo.query.filter(Todo.task.like('%' + search + '%')).filter(Todo.complete == False)

        return render_template('search_results.html', tasks_incomplete=tasks_incomplete,tasks_complete=tasks_complete)


@app.route("/tasks_on_date", methods=["POST"])
def tasks_on_date():
    if request.method == "POST":
        date = dparser.parse(request.form['due_date'], fuzzy=True).date()
        tasks_date_complete = Todo.query.filter(Todo.due_date == date).filter(Todo.complete==True)
        tasks_date_incomplete = Todo.query.filter(Todo.due_date == date).filter(Todo.complete == False)
        return render_template("tasks_on_date.html",tasks_date_complete=tasks_date_complete,tasks_date_incomplete=tasks_date_incomplete)


app.run(debug=True)

from bottle import Bottle, run, debug, template, route, view, request, redirect, post, error
import sqlite3

DEBUG = False
DBFILE = '/tmp/slides.db'

from local import *

debug(DEBUG)

@route('/setup')
def setup():
    conn = sqlite3.connect( DBFILE )
    db = conn.cursor()
    db.execute('CREATE TABLE IF NOT EXISTS slides (name, slide, text, PRIMARY KEY(name, slide))')
    conn.close()

@post('/')
def do_login():
    name = request.forms.get('name')
    redirect('/' + name + '/1')
    return

@route('/')
@view('login.html')
def login():
    return

@route('/<name>')
@route('/<name>/<slide:int>')
@view('index.html')
def home(name=None, slide=1):
    if name:
        conn = sqlite3.connect( DBFILE )
        db = conn.cursor()
        row = db.execute('SELECT text FROM slides WHERE name=? AND slide=?', (name, slide) ).fetchone()
        rows = db.execute('SELECT slide,text FROM slides WHERE name=?', (name,) ).fetchall()
        if row:
            return dict(name=name, slide=slide, text=row[0], rows=rows)
        else:
            #return error404(404)
            text = 'Hello Monkey!'
        conn.close()
    else:
        text = 'Go login or something!'
    
    return dict(name=name, slide=slide, text=text, rows=rows)

@post('/<name>/<slide:int>')
@view('index.html')
def save_slide(name, slide):
    text = request.forms.get('text')
    conn = sqlite3.connect('/tmp/slides.db')
    db = conn.cursor()
    row = db.execute('SELECT text FROM slides WHERE name=? AND slide=?', (name, slide) ).fetchone()
    if row:
        db.execute('UPDATE slides SET text=? WHERE name=? AND slide=?', (text, name, slide) )
    else:
        db.execute('INSERT INTO slides (name,slide,text) VALUES (?, ?, ?)', (name, slide, text) )
    conn.commit()
    conn.close()
    next_slide = str( int(slide) + 1 )
    redirect('/' + name + '/' + next_slide)
    #return dict(name=name, slide=slide, text=text)
    return


@route('/<name>/go')
@view('slides.html')
def generate(name):
    conn = sqlite3.connect( DBFILE )
    db = conn.cursor()
    rows = db.execute('SELECT slide,text FROM slides WHERE name=?', (name,) ).fetchall()
    return dict(name=name, rows=rows)

@error(404)
def error404(error):
    return 'Nothing here, sorry'

run(host='localhost', port=8080)

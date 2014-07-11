from bottle import Bottle, run, debug, template, route, view, request, redirect, post, error, response
from tex import latex2pdf
import sqlite3

DEBUG = False
DBFILE = '/tmp/slides.db'

from local import *

debug(DEBUG)

@route('/setup')
def setup():
    conn = sqlite3.connect( DBFILE )
    db = conn.cursor()
    db.execute('CREATE TABLE IF NOT EXISTS slides (name, slide, title, text, PRIMARY KEY(name, slide))')
    db.execute('CREATE TABLE IF NOT EXISTS presentations (name PRIMARY KEY, title, text)')
    conn.close()

@post('/')
def do_login():
    name = request.forms.get('name').decode('utf-8')
    title = request.forms.get('title').decode('utf-8')
    conn = sqlite3.connect( DBFILE )
    db = conn.cursor()
    db.execute('INSERT INTO presentations (name,title) VALUES (?, ?)', (name, title, ) )
    conn.commit()
    conn.close()
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
        presentation = db.execute('SELECT title,text FROM presentations WHERE name=?', (name,) ).fetchone()
        p_title = presentation[0]
        p_text = presentation[1]
        row = db.execute('SELECT title,text FROM slides WHERE name=? AND slide=?', (name, slide) ).fetchone()
        rows = db.execute('SELECT slide,title,text FROM slides WHERE name=?', (name,) ).fetchall()
        if row:
            return dict(name=name, slide=slide, title=row[0], text=row[1], rows=rows, p_title=p_title)
        else:
            #return error404(404)
            title = 'Hello Monkey!'
            text = 'This is the winter of our discontent.'
        conn.close()
    else:
        text = 'Go login or something!'
    
    return dict(name=name, slide=slide, text=text, title=title, rows=rows, p_title=p_title)

@post('/<name>')
@view('index.html')
def save_presentation(name):
    title = request.forms.get('title').decode('utf-8')
    conn = sqlite3.connect( DBFILE )
    db = conn.cursor()
    db.execute('UPDATE presentations SET title=? WHERE name=?', (title, name, ) )
    conn.commit()
    conn.close()
    next_slide = str(1)
    redirect('/' + name + '/' + next_slide)
    return


@post('/<name>/<slide:int>')
@view('index.html')
def save_slide(name, slide):
    title = request.forms.get('title').decode('utf-8')
    text = request.forms.get('text').decode('utf-8')
    conn = sqlite3.connect( DBFILE )
    db = conn.cursor()
    row = db.execute('SELECT title,text FROM slides WHERE name=? AND slide=?', (name, slide) ).fetchone()
    if row:
        db.execute('UPDATE slides SET title=?, text=? WHERE name=? AND slide=?', (title, text, name, slide) )
    else:
        db.execute('INSERT INTO slides (name,slide,title,text) VALUES (?, ?, ?, ?)', (name, slide, title, text) )
    conn.commit()
    conn.close()
    next_slide = str( int(slide) + 1 )
    redirect('/' + name + '/' + next_slide)
    return

@route('/<name>/print/<format>')
def generate(name, format):
    conn = sqlite3.connect( DBFILE )
    db = conn.cursor()
    presentation = db.execute('SELECT title,text FROM presentations WHERE name=?', (name,) ).fetchone()
    p_title = presentation[0]
    p_text = presentation[1]
    rows = db.execute('SELECT slide,title,text FROM slides WHERE name=?', (name,) ).fetchall()
    tpl = 'slides.' + format
    result = template(tpl, name=name, rows=rows, p_title=p_title)
    if format == 'html':
        return result
    elif format == 'pdf':
        result = latex2pdf(result)
        response.content_type = 'application/pdf'
        return result
    elif format == 'tex':
        response.content_type = 'text/plain; charset=utf-8'
        return result

@error(404)
def error404(error):
    return 'Nothing here, sorry'

run(host='localhost', port=8080)

from bottle import Bottle, run, debug, template, route, view, install, request, redirect, post, error
import sqlite3

debug(True)
#run(reloader=True)

@route('/setup')
def setup():
    conn = sqlite3.connect('/tmp/slides.db')
    db = conn.cursor()
    db.execute('CREATE TABLE IF NOT EXISTS slides (name PRIMARY KEY, slide, text)')

@post('/')
def login():
    name = request.forms.get('name')
    redirect('/' + name)
    return

@route('/')
@route('/<name>')
@route('/<name>/<slide:int>')
@view('index.html')
def home(name=None, slide=1):
    if name:
        conn = sqlite3.connect('/tmp/slides.db')
        db = conn.cursor()
        row = db.execute('SELECT * FROM slides WHERE name=? AND slide=?', (name, slide) ).fetchone()
        conn.close()
        print row
        if row:
            return dict(name=name, slide=slide, text=row[2])
        return error404(404)
    else:
        text = 'Hello!'
    
    return dict(name=name, slide=slide, text=text)

@post('/<name>/<slide:int>')
@view('index.html')
def save_slide(name, slide):
    text = request.forms.get('text')
    conn = sqlite3.connect('/tmp/slides.db')
    db = conn.cursor()
    db.execute('INSERT INTO slides (name,slide,text) VALUES (?, ?, ?)', (name, slide, text) )
    conn.commit()
    conn.close()
    print "hello!!!"
    return dict(name=name, slide=slide, text=text)




@error(404)
def error404(error):
    return 'Nothing here, sorry'

run(host='localhost', port=8080)

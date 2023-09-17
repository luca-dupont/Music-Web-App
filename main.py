from pytube import YouTube
import os
from flask import Flask, render_template, request, redirect, send_from_directory
import validators
import shutil

app = Flask(__name__,)
message = ''
def download_vid(url) :
    global message
    message = ''
    if validators.url(url) :
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path="./downloads/")
        base, ext = os.path.splitext(out_file)
        new_file = ''.join(base) + '.mp3'
        os.rename(out_file, new_file)
        
    else :
        message = '<p style="color:red;">Please enter a valid URL</p>'

@app.route('/')
def main_red() :
    return redirect('/main')

@app.route('/main', methods=['GET', 'POST'])
def main() :
    global message
    if request.method == "POST":
        download_vid(request.form.get('url'))
    return render_template('main.html', message=message)

@app.route('/downloads/<song>')
def download(song) :
    return send_from_directory('./downloads', song)

@app.route('/library', methods=['GET', 'POST'])
def library():
    html = ''
    html2 = ''
    for i,song in enumerate(os.listdir("./downloads")):
        if song != ".DS_Store" and song != "playlists": 
            html += f'<h4>{i-1}. {song.replace(".mp3", "")}</h4><audio controls id="song" style="width: 300px; height: 50px;"><source src="/downloads/{song}" type="audio/mpeg"></audio>'
    if request.method == "POST" and request.form.get('new_playlist') != '' :
        os.mkdir(f"./downloads/playlists/{request.form.get('new_playlist')}")
    for playlist in os.listdir("./downloads/playlists"):
        if playlist != ".DS_Store": 
            html2 += f'<form action="http://127.0.0.1:5000/playlists/{playlist}"><button type="submit" style="margin-bottom:10px;">{playlist}</button></form>'
    return render_template('library.html', html=html, html2=html2)

@app.route('/playlists/<name>', methods = ['GET', 'POST'])
def playlist(name) :
    html = ''
    library_songs_html = ''
    for i,song in enumerate(os.listdir(f"./downloads/playlists/{name}")):
        if song != ".DS_Store": 
            html += f'''<h4>{i+1}. {song.replace(".mp3", "")}</h4>
                        <audio controls style="width: 300px; height: 50px; display: inline-flex;" id="audio{i+1}">
                            <source src="/downloads/{song}" type="audio/mpeg">
                        </audio>
                        <a href="/remove-song/{name}/{song}" style="padding-left: 20px; margin-bottom:50px;">
                            <button type="submit" name="submit" value="Remove" style="display: inline-flex; justify-content: middle;">Remove</button>
                        </a>'''
    for i,song in enumerate(os.listdir("./downloads")):
        if song != ".DS_Store" and song != "playlists": 
            library_songs_html += f'<div><h4 style="display: inline-block;margin-right: 10px">{song.replace(".mp3", "")}</h4><a href="/add-song/{name}/{song}"><button type="submit" name="submit" value="Submit" style="display: inline-block;">Add</button></a></div>'
    if request.method == 'POST' and request.form.get('list_name') != '':
        os.rename(f"./downloads/playlists/{name}",f"./downloads/playlists/{request.form.get('list_name')}")
        return redirect(f'/playlists/{request.form.get("list_name")}')
    return render_template('playlist.html', html=html,name=name, library_songs_html = library_songs_html)

@app.route('/add-song/<playlist>/<song>')
def add_song(playlist,song):
    shutil.copy(f"./downloads/{song}",f"./downloads/playlists/{playlist}")
    return redirect(f'/playlists/{playlist}')

@app.route('/remove-song/<playlist>/<song>')
def remove_song(playlist,song):
    os.remove(f"./downloads/playlists/{playlist}/{song}")
    return redirect(f'/playlists/{playlist}')

if __name__ == "__main__":
    app.run()

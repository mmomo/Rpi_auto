#  views.py
#  
#  Copyright 2016 Cesar Venzor <foxhound15c@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

from flask import render_template, session, redirect, url_for, flash, request
from app import app
from rasp import focos
from telegram import bot
import RPi.GPIO as GPIO
import time

@app.route('/')
def main():

    for foco in focos:
        focos[foco]['state'] = GPIO.input(foco)

        templateData = {
            'focos':focos
            }

    return render_template('main.html', **templateData)

@app.route('/<changePin>/<action>')
def action(changePin, action):
    changePin = int(changePin)
    deviceName = focos[changePin]['name']
    error = None

    if session.get('logged_in'):
        if action == 'on':
            message = "Turned " + deviceName + " on."
            GPIO.output(changePin, GPIO.HIGH)
        if action == 'off':
            message = "Turned " + deviceName +  " off."
            GPIO.output(changePin, GPIO.LOW)
    else:
        error = "You must log in."

    for foco in focos:
        focos[foco]['state'] = GPIO.input(foco)

    templateData = {
        'focos':focos,
        'error':error
        }
    return render_template('main.html', **templateData)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')

            localtime = time.asctime(time.localtime(time.time()))
            bot.sendMessage(app.config['CHAT_ID'], 'You were logged in - ' + localtime)
            return redirect(url_for('main'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    
    localtime = time.asctime(time.localtime(time.time()))
    bot.sendMessage(app.config['CHAT_ID'], 'You were logged out - ' + localtime)
    
    return redirect(url_for('main'))

@app.route('/about')
def about():
    return render_template('about.html')

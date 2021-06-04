from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

import os
import subprocess
import shutil
import datetime
import json
import signal
import requests

from django.db import models
from users.models import User

# *****custom Def******

def updStat(botID,userID, count):
    cUser = User.objects.get(id = userID)
    cBot = cUser.bot_set.get(id = botID)

    now = datetime.datetime.now()
    cDate = now.strftime("%d-%m-%Y")

    if ((cBot.messages_set.filter(date = cDate)).exists()):
        cBot.messages_set.filter(date =cDate).update(count = count)
        print('UPD')
    else:
        cBot.messages_set.create(date =cDate, count = count)
        print('create')

    return cBot.messages_set.filter(bot_name_id = botID)

def check_auth(request):
    sessionUserId=request.session.get('sUserId')
    if sessionUserId == None:
        return redirect('/')

    sUserId = sessionUserId
    uData = User.objects.filter(id = sUserId)
    url = ((request.path).split('/'))[1]
    # print(url)
    return {'sUserId':request.session.get('sUserId'), 'uData':uData[0], 'url': url}


# *****custom Def******


def removebot(request):
    try:
        deactivatebot(request)
    except Exception as e:
        pass

    cUser = User.objects.get(id = request.session.get('sUserId'))
    cBotId =request.session.get('botID')
    cBot = cUser.bot_set.get(id = cBotId)

    cBot.delete();
    path = os.getcwd() + '/tgstart2/bots/' + str( request.session.get('sUserId')) + "/"+cBotId
    shutil.rmtree(path)
    print("*******del bot*******")
    return redirect('/mybots')



def removeuser(request, botID, userID):
    cUser = User.objects.get(id = request.session.get('sUserId'))
    cBot = cUser.bot_set.get(id = botID)
    cUser = cBot.botuser_set.get(id = userID)
    cUser.delete()

def reloadbot(request):
    deactivatebot(request);
    activatebot(request)

def activatebot(request):
    cUser = User.objects.get(id = request.session.get('sUserId'))
    cBotId =request.session.get('botID')
    cBot = cUser.bot_set.get(id = cBotId)

    cDir = os.getcwd() + '/tgstart2/bots/' + str( request.session.get('sUserId')) + "/"+str(cBotId)
    pr = subprocess.Popen(['python', cDir +'/main.py'])
    # pr = subprocess.Popen(['python3', cDir +'/main.py'])
    cUser.bot_set.filter(id=cBotId).update(pID = pr.pid, status = 1)
    print("*******Activateded bot*******")
    return redirect('/mybots')

def deactivatebot(request):
    cUser = User.objects.get(id = request.session.get('sUserId'))
    cBotId =request.session.get('botID')
    cBot = cUser.bot_set.get(id = cBotId)
    print(cBot.pID)
    try:
        os.kill(cBot.pID, signal.SIGTERM)
    except Exception as e:
        print(e)

    cUser.bot_set.filter(id = cBotId).update(pID = 0, status = 0)
    print("*******Deactivated bot*******")
    return redirect('/mybots')

def BotIdProc(request):
    if 'botID' in request.POST:
        request.session['botID'] = request.POST.get('botID')
        print(request.session['botID'] + ' added!')
    if 'idCommand' in request.POST:
        request.session['idCommand'] = request.POST.get('idCommand')
        print(request.session['idCommand'] + ' added!')
    return redirect(request.path)

def dashboard(request):
    if 'botID' in request.POST:
        request.session['botID'] = request.POST.get('botID')
        print(request.session['botID'] + ' added!')
        return redirect('/dashboard/')

    cUser = User.objects.get(id = request.session.get('sUserId'))
    tgBots= cUser.bot_set.all()
    if((cUser.bot_set.all()).count() > 0):
        # print(tgBots[0].bot_name)
        if(request.session.get('botID') == None):
            request.session['botID'] = (cUser.bot_set.all())[1].id
        cBotId =str(request.session.get('botID'))
        cBot = cUser.bot_set.get(id = cBotId)
        usersCount = (cBot.botuser_set.all()).count()
        commandsCount = (cBot.customcommand_set.all()).count()
        dataChart = cBot.messages_set.filter(bot_name_id = cBotId)
        now = datetime.datetime.now()
        cDate = now.strftime("%d-%m-%Y")

        if ((cBot.messages_set.filter(date = cDate)).exists()):
            cCount = (cBot.messages_set.filter(date =cDate))[0].count
        else:
            cCount =0
    else:
        dataChart = '0'

    return render(request, 'volt/dashboard.html', {'dataChart': dataChart, 'cCount':cCount, 'usersCount':usersCount, 'commandsCount':commandsCount, 'cBot':cBot, 'tgBots': tgBots, 'auth':check_auth(request)})

def edit(request):
    cUser = User.objects.get(id = request.session.get('sUserId'))
    tgBots= cUser.bot_set.all()
    cBotCustomCommands = 0;

    cBotId =str(request.session.get('botID'))
    cBot = cUser.bot_set.get(id = cBotId)
    if((cBot.customcommand_set.all()).count() > 0):
        cBotCustomCommands = cBot.customcommand_set.all()

    if request.method == "POST":
        print("POST")
        if 'idCommand' in request.POST:
            cBotId =str(request.POST.get('botID'))
            cBot = cUser.bot_set.get(id = cBotId)
            (cBot.customcommand_set.get(id = request.POST.get('idCommand'))).delete()
            reloadbot(request)
            # return redirect('/mybots/edit')
        elif 'botCommand' in request.POST:
            cBot.customcommand_set.create(command = request.POST.get('botCommand'),response = request.POST.get('botResponse'))
            # cBot.CustomCommand_set.create(command = request.POST.get('botCommand'),response = request.POST.get('botResponse'))
            print('command added!')
            reloadbot(request)
            return redirect('/mybots/edit')


    return render(request, 'volt/edit.html', {'cBot':cBot,'cBotCustomCommands': cBotCustomCommands, 'auth': check_auth(request)})

def mybots(request):
    if 'botID' in request.POST:
        request.session['botID']= request.POST.get('botID');
        print("ADDED!")
        return redirect(request.path + 'edit');

    if request.method == "POST":

#assigning a option(template) to a bot
        cUser = User.objects.get(id = request.session.get('sUserId'))
        if not (cUser.bot_set.filter(token=request.POST.get('tgToken')).exists()):

            requestAPI = requests.get('https://api.telegram.org/bot'+request.POST.get('tgToken')+'/getMe')
            parsed_string = json.loads(requestAPI.content)
            if (parsed_string['ok']):
                cBotFirstName = parsed_string['result']['first_name']
                cBotGlobalId = parsed_string['result']['id']
                cBotUsername = parsed_string['result']['username']
            else:
                cBotFirstName= 'none'
                cBotGlobalId= 'none'
                cBotUsername= 'none'
            print(cBotFirstName)

            cUser.bot_set.create(option = request.POST.get('exampleRadios'), token = request.POST.get('tgToken'), bot_name = cBotFirstName, global_id= cBotGlobalId, bot_username =cBotUsername )
            cBotId =str((cUser.bot_set.all())[(cUser.bot_set.all()).count()-1].id)
            cBot = cUser.bot_set.get(id = cBotId)
            now = datetime.datetime.now()
            startDate = now.strftime("%d-%m-%Y")


            cBot.messages_set.create(count = 0, date =startDate)



#Creating a directory for a user's bot
            sUserId = str(request.session.get('sUserId'))
            cDir = os.getcwd() + '/tgstart2/bots/'
            if not os.path.isdir(cDir +sUserId):
                os.mkdir(cDir + sUserId)
            if not os.path.isdir(cDir +  sUserId + "/" + cBotId):
                os.mkdir(cDir + sUserId + "/" + cBotId)

            text_config = open(cDir + sUserId + "/" + cBotId +"/config.py", "w")
            text_config.write("token = '" + request.POST.get('tgToken')+ "'\n")
            text_config.write("user_id = '" + sUserId+ "'\n")
            text_config.write("bot_id = '" + cBotId+ "'\n")
            shutil.copyfile(cDir + "main.py", cDir + sUserId + "/" + cBotId +"/main.py")


            pr = subprocess.Popen(['python', cDir + sUserId + "/" + cBotId +'/main.py'])
            # pr = subprocess.Popen(['python3', cDir + sUserId + "/" + cBotId +'/main.py'])

            cUser.bot_set.filter(id=cBotId).update(pID = pr.pid)


    cUser = User.objects.get(id = request.session.get('sUserId'))


    return render(request, 'volt/mybots.html', {'bots':cUser.bot_set.all().order_by('-id'), 'auth': check_auth(request)})

def sendMessage(request):

    requests.get('https://api.telegram.org/bot'+token+'/sendMessage?chat_id='+id+'&text='+text)
def pay(request):
    return render(request, 'volt/pay.html', {'auth': check_auth(request)})

def sidebar(request):
    return render(request, 'volt/sidebar.html')

def senders(request):
    return render(request, 'volt/senders.html', {'auth': check_auth(request)})

def users(request):
    if 'botID' in request.POST:
        request.session['botID'] = request.POST.get('botID')
        print(request.session['botID'] + ' added!')
        return redirect('/users/')

    cUser = User.objects.get(id = request.session.get('sUserId'))
    tgBots= cUser.bot_set.all()



    if 'botId' and 'userID' in request.GET:
        removeuser(request, request.GET.get('botID'), request.GET.get('userID'))
    print(request.POST.get('messageText'))
    # if 'botID' and 'userID' and 'messageText' in request.POST:
    if request.POST:
        cBot = cUser.bot_set.get(id = request.POST.get('botID'))
        cBotToken = cBot.token
        tgid=cBot.botuser_set.get(id= request.POST.get('userID'))
        requests.get('https://api.telegram.org/bot'+cBotToken+'/sendMessage?chat_id='+tgid.tg_id+'&text='+request.POST.get('messageText'))
        print(cBotToken)
        print(tgid.tg_id)
        print('успешно')

    if 'botID' in request.session:
        if((cUser.bot_set.all()).count() > 0):
            # print(tgBots[0].bot_name)
            cBotId =str(request.session.get('botID'))
            cBot = cUser.bot_set.get(id = cBotId)
            cBotToken = cBot

            usersData = cBot.botuser_set.all()
            if((cBot.botuser_set.all()).count() == 0):
                usersData = 0;
        else:
            usersData = 0;
            cBotToken = 0;
    else:
        return render(request, 'volt/users.html', {'tgBots':tgBots, 'auth': check_auth(request)})

    return render(request, 'volt/users.html', {'usersData':usersData, 'tgBots':tgBots, 'cBot':cBot, 'auth': check_auth(request)})
def profile(request):

    if request.method == "POST":
        cUser = User.objects.get(id=request.session.get('sUserId'))
        cUser.user_lastname = request.POST.get('last_name')
        cUser.user_email = request.POST.get('user_email')
        cUser.save()

    return render(request, 'volt/profile.html', {'auth': check_auth(request)})

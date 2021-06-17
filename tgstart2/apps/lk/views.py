from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse


import os
import subprocess
import datetime
import shutil
import json
import signal
import requests


from django.db import models
from users.models import User


def check_auth(request):
    mainUserId=request.session.get('mainUserId')
    if mainUserId == None:
        print(mainUserId)
        return redirect('/')
    userData = User.objects.filter(id = mainUserId) #getting user data (firstname, lastname...)
    url = ((request.path).split('/'))[1] #getting page url

    return {'mainUserId':request.session.get('mainUserId'), 'userData':userData[0], 'url': url}

def getMainUser(request):
    return User.objects.get(id = request.session.get('mainUserId')) #get mainUser object with mainUserId

def changeMainBot(request):
    request.session['mainBotId'] = request.POST.get('botID') #change MainBotId for request.POST
    return HttpResponse("Мэйн Бот изменён") #sending answer

def reloadbot(request):
    deactivatebot(request);
    activatebot(request)

def activatebot(request):
    cDir = os.getcwd() + '/tgstart2/bots/' + str( request.session.get('mainUserId')) + "/"+str(request.session.get('mainBotId'))
    pr = subprocess.Popen(['python', cDir +'/main.py']) #starting subprocess with bot
    # pr = subprocess.Popen(['python3', cDir +'/main.py'])
    mainUser = getMainUser(request)
    mainUser.bot_set.filter(id=request.session.get('mainBotId')).update(pID = pr.pid, status = 1) #updating status on 1 and set pID process
    print("*******Activateded bot*******")
    return redirect('/')

def deactivatebot(request):
    mainUser = getMainUser(request)
    cBotId =request.session.get('mainBotId')
    cBot = mainUser.bot_set.get(id = cBotId)
    try:
        os.kill(cBot.pID, signal.SIGTERM)
    except Exception as e:
        print(e)

    mainUser.bot_set.filter(id = cBotId).update(pID = 0, status = 0)
    print("*******Deactivated bot*******")
    return redirect('/')

def removebot(request):
    try:
        deactivatebot(request) #try deactivate current bot if it works
    except Exception as e:
        pass
    mainUser = getMainUser(request)
    cBot = mainUser.bot_set.get(id = request.session.get('mainBotId'))
    cBot.delete();
    path = os.getcwd() + '/tgstart2/bots/' + str( request.session.get('mainUserId')) + "/"+request.session.get('mainBotId')
    shutil.rmtree(path)


    # request.session['mainBotId'] = (mainUser.bot_set.all())[0].id #get first user's bot for MAIN
    print("*******del bot*******")
    return redirect('/mybots')

def dashboard(request):
    if request.method == "POST":#if changed bot
        if 'botID' in request.POST:
            return changeMainBot(request);

    mainUser = getMainUser(request)
    mainBotId = request.session.get('mainBotId')
    allBots = '0';
    if((mainUser.bot_set.all()).count() > 0):
        if(mainBotId == None): #if there is no mainBotId in the session
            mainBotId = (mainUser.bot_set.all())[0].id #getting first user's bot id
        allBots = mainUser.bot_set.all()
        cBot = mainUser.bot_set.get(id = mainBotId) #getting current bot
        botData = {
            'bot' : cBot,
            'usersCount': (cBot.botuser_set.all()).count(),
            'commandsCount': (cBot.customcommand_set.all()).count(),
            'dataChart': cBot.messages_set.filter(bot_name_id = mainBotId)
        }
        todayDate = datetime.datetime.now().strftime("%d-%m-%Y") #getting date today
        if ((cBot.messages_set.filter(date = todayDate)).exists()): #if there are messages today
            botData['msgTodayCount'] = (cBot.messages_set.filter(date =todayDate))[0].count #adding key in botData
        else:
            botData['msgTodayCount'] = 0
    else:
        botData = ''
    return render(request, 'volt/dashboard.html', {'botData':botData, 'allBots':allBots, 'auth':check_auth(request)})

def edit(request):
    mainUser = getMainUser(request) #get mainUser object
    cBot = mainUser.bot_set.get(id = request.session.get('mainBotId'))
    cBotCustomCommands = 0;
    if((cBot.customcommand_set.all()).count() > 0):
        cBotCustomCommands = cBot.customcommand_set.all()

    if request.method == "POST":
        print("POST")
        if 'idCommand' in request.POST: #deletion currnet bot's command
            (cBot.customcommand_set.get(id = request.POST.get('idCommand'))).delete()
            return HttpResponse("Команда удалена!")
            reloadbot(request)
            # return redirect('/mybots/edit')
        elif 'botCommand' in request.POST: #adding currnet bot's command
            cBot.customcommand_set.create(command = request.POST.get('botCommand'), response = request.POST.get('botResponse'))
            return HttpResponse("Команда добавлена!")
            reloadbot(request)

    return render(request, 'volt/edit.html', {'cBot':cBot,'cBotCustomCommands':cBotCustomCommands, 'auth': check_auth(request)})

def mybots(request):
    mainUser = getMainUser(request)
    if request.method == "POST":
        if 'botID' in request.POST:
            return changeMainBot(request);
        if not (mainUser.bot_set.filter(token=request.POST.get('tgToken')).exists()): #if there is no bot with the current token
            responseAPI = requests.get('https://api.telegram.org/bot'+request.POST.get('tgToken')+'/getMe')
            parsed_string = json.loads(responseAPI.content)

            if (parsed_string['ok']): # geting current bot data...
                cBotFirstName = parsed_string['result']['first_name']
                cBotGlobalId = parsed_string['result']['id']
                cBotUsername = parsed_string['result']['username']
            else:
                # cBotFirstName= 'none'
                # cBotGlobalId= 'none'
                # cBotUsername= 'none'
                return HttpResponse("Инвалид Токен!")#sending response
            mainUser.bot_set.create( #creating bot in db
                option = request.POST.get('option'),
                token = request.POST.get('tgToken'),
                bot_name = cBotFirstName,
                global_id= cBotGlobalId,
                bot_username =cBotUsername
            )
            request.session['mainBotId'] = str((mainUser.bot_set.all())[(mainUser.bot_set.all()).count()-1].id) #getting last bot's id
            mainBotId = request.session.get('mainBotId')
            #Creating a directory for a user's bot
            mainUserId = str(request.session.get('mainUserId'))
            # mainUserId = s
            # cBotId =str((cUser.bot_set.all())[(cUser.bot_set.all()).count()-1].id)

            cDir = os.getcwd() + '/tgstart2/bots/' #getting current directory, for example C:\Users\fdsfd\github\tgstart\tgstart + /tgstart2/bots/
            if not os.path.isdir(cDir + mainUserId ): #if not directory for the user
                os.mkdir(cDir + mainUserId) #creating bots/mainUserId
            if not os.path.isdir(cDir +  mainUserId + "/" + mainBotId): #if not directory for the user's bot
                os.mkdir(cDir + mainUserId + "/" + mainBotId) #creating bots/mainUserId/mainBotId

            text_config = open(cDir + mainUserId + "/" + mainBotId +"/config.py", "w") #creating config.py bots/mainUserId/mainBotId/config.py
            text_config.write("token = '" + request.POST.get('tgToken')+ "'\n") #add row roken
            text_config.write("user_id = '" + mainUserId+ "'\n") #add row user_id
            text_config.write("bot_id = '" + mainBotId+ "'\n") #add row bot_id
            shutil.copyfile(cDir + "main.py", cDir + mainUserId + "/" + mainBotId +"/main.py") #copy pattern file with bot's code

            pr = subprocess.Popen(['python', cDir + mainUserId + "/" + mainBotId +'/main.py']) #starting subprocess with bot's script
            # pr = subprocess.Popen(['python3', cDir + sUserId + "/" + cBotId +'/main.py']) #starting (server) subprocess with bot's script

            mainUser.bot_set.filter(id=mainBotId).update(pID = pr.pid) #updating bot db and writting process pid
            return HttpResponse("Бот успешно создан!") #sending response
        else:
            return HttpResponse("Такой токен уже существует...") #sending response



    return render(request, 'volt/mybots.html', {'bots':mainUser.bot_set.all().order_by('-id'), 'auth':check_auth(request)})

def users(request):
    mainUser = User.objects.get(id = request.session.get('mainUserId'))
    if((mainUser.bot_set.all()).count() > 0):
        if 'botID' in request.POST:
            return changeMainBot(request);

        mainUser = User.objects.get(id = request.session.get('mainUserId'))
        cBot = mainUser.bot_set.get(id = request.session.get('mainBotId'))


        if 'sendMessage' in request.POST:
            tgUserID=(cBot.botuser_set.get(id= request.POST.get('userID'))).tg_id
            requests.get('https://api.telegram.org/bot'+cBot.token+'/sendMessage?chat_id='+tgUserID+'&text='+request.POST.get('messageText')) #sending a message to the user
        if 'delUser' in request.POST:
            botsUser = cBot.botuser_set.get(id = request.POST.get('userID'))
            botsUser.delete()
            return HttpResponse("Пользователь удален!") #sending response
        tgBots= mainUser.bot_set.all()

        if((mainUser.bot_set.all()).count() > 0):
            # print(tgBots[0].bot_name)
            cBot = mainUser.bot_set.get(id = request.session.get('mainBotId'))

            usersData = cBot.botuser_set.all()
            if((cBot.botuser_set.all()).count() == 0):
                usersData = 0;
        else:
            usersData = 0;
    else:
        usersData = 0;
        return render(request, 'volt/users.html', {'usersData':usersData, 'auth': check_auth(request)})


    return render(request, 'volt/users.html', {'usersData':usersData, 'tgBots':tgBots, 'cBot':cBot, 'auth': check_auth(request)})

def instruction(request):
    return render(request,'volt/instruction.html',{'auth': check_auth(request)})

def profile(request):
    if request.method == "POST":
        cUser = User.objects.get(id=request.session.get('mainUserId'))
        cUser.user_lastname = request.POST.get('last_name')
        cUser.user_email = request.POST.get('user_email')
        cUser.save()
    return render(request, 'volt/profile.html', {'auth': check_auth(request)})

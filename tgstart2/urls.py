from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('lk.urls')),
    path('', include('users.urls')),
    path('admin/', admin.site.urls),
    path('grappelli/', include('grappelli.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# START SUBPROCESSES
# from django.db import models
# from users.models import User
# import os, subprocess
#
# cUsers = User.objects.all()
# for u in cUsers:
#     cUserId = u.id
#     print('user: ' + str(u))
#     cBots = u.bot_set.all()
#     print('bot count: ' + str(cBots.count()))
#     if(cBots.count()>0):
#         print('*****')
#         for b in cBots:
#             cBotId = b.id
#             print('bot id: ' + str(b.id))
#             cBotStatus = b.status
#             print('bot status: ' + str(b.status))
#
#             if(cBotStatus == 1):
#                 cDir = os.getcwd() + '/tgstart2/bots/' + str( cUserId) + "/"+str(cBotId)
#                 print (cDir +'/main.py')
#                 pr = subprocess.Popen(['python', cDir +'/main.py'])
#                 print('pID ' + str(pr.pid))
#
#                 u.bot_set.filter(id=cBotId).update(pID = pr.pid, status = 1)
#         print('*****')

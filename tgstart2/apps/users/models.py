from django.db import models


class User(models.Model):
	user_name = models.CharField('Логин', max_length = 30)
	user_firstname = models.TextField('Имя', max_length = 30)
	user_lastname = models.TextField('Фамилия', max_length = 30)
	tg_id = models.CharField('tg_id', max_length = 10)


	def __str__(self):
		return self.user_name

	class Meta:
		verbose_name = "Пользователь"
		verbose_name_plural = "Пользователи"

class Bot(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	option = models.CharField('Option', max_length = 30)
	global_id = models.CharField('Global id', max_length = 30)
	bot_name = models.CharField('Bot Name', max_length = 30)
	bot_username = models.CharField('Bot Username', max_length = 30)
	token = models.CharField('Token', max_length = 100)
	status = models.IntegerField('Status', default=1)
	pID = models.IntegerField('pID', default=0)

	def __str__(self):
		return (str(self.id) + "_" + str(self.user))

	class Meta:
		verbose_name = "Бот"
		verbose_name_plural = "Боты"

class BotUser(models.Model):
	bot_name = models.ForeignKey(Bot, on_delete = models.CASCADE)
	username = models.CharField('Username', max_length = 30)
	first_name = models.TextField('Имя', max_length = 30)
	last_name = models.TextField('Фамилия', max_length = 30)
	tg_id = models.CharField('Id telegram', max_length = 10)
	pathAvatar = models.CharField('Avatar Path ', max_length = 200)
	dateReg = models.CharField('Дата регистрации', max_length = 200)

	def __str__(self):
		return (str(self.bot_name))

	class Meta:
		verbose_name = "Пользователь Бота"
		verbose_name_plural = "Пользователи Бота"

class Messages(models.Model):
	bot_name = models.ForeignKey(Bot, on_delete = models.CASCADE)
	count = models.IntegerField('Count', default=0)
	date = models.CharField('Date', max_length = 30)

	def __str__(self):
		return (str(self.bot_name))

	class Meta:
		verbose_name = "Сообщение"
		verbose_name_plural = "Сообщения"

class CustomCommand(models.Model):
	bot_name = models.ForeignKey(Bot, on_delete = models.CASCADE)
	command = models.CharField('Команда', max_length = 100, default=0)
	response = models.CharField('Ответ', max_length = 500, default=0)

	def __str__(self):
		return (str(self.bot_name))

	class Meta:
		verbose_name = "Пользовательские команды"
		verbose_name_plural = "Пользовательская команда"

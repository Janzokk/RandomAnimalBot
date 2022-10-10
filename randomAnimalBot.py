# -*- coding: utf-8 -*-

from genericpath import exists
from telegram.ext import *
from telegram import *
import requests
import json
import random
import googletrans

#Global variables: A translator, Language selection buttons, The language of the text, All the texts and The last animal we searched
translator = googletrans.Translator()

Button1 = KeyboardButton(
    text='/en'
)
Button2 = KeyboardButton(
	text='/ca'
)
Button3 = KeyboardButton(
	text='/es'
)
Button4 = KeyboardButton(
	text='/help'
)

lang = 'ca'
texts = ["Bon dia", 'Selecciona idioma', "Escriu /search + l'animal que vulguis buscar per veure fotos d'aquest animal\nL'animal que vols no funciona? Potser encara no el tenim a la plantilla, Revisa amb /available tots els animals disponibles", 
"Aquí tens una foto de: ", "Vols més fotos d'aquest animal? --> /more", "Si vols compartir l'imatge --> /share + el nom d'usuari", "No existeix o de moment no el tenim incorporat", "L'usuari no existeix o no a usat el bot"]
currAnimal = ""

#Method to translate all the texts to english
def en(update, context):
	global lang
	#Checks if the language is not english already
	if(lang != 'en'):
		n = 0
		#Translate every string and replaces de old one
		for x in texts:
			newTxt = translator.translate(x, src=lang, dest='en')
			texts[n] = newTxt.text
			n += 1
		lang = 'en'
	context.bot.send_message(update.message.chat_id, f'Language updated')

#Method to translate all the texts to catalan
def ca(update, context):
	global lang
	#Checks if the language is not catalan already
	if(lang != 'ca'):
		n = 0
		#Translate every string and replaces de old one
		for x in texts:
			newTxt = translator.translate(x, src=lang, dest='ca')
			texts[n] = newTxt.text
			n += 1
		lang = 'ca'
	context.bot.send_message(update.message.chat_id, f'Idioma actualitzat')

#Method to translate all the texts to spanish
def es(update, context):
	global lang
	#Checks if the language is not spanish already
	if(lang != 'es'):
		n = 0
		#Translate every string and replaces de old one
		for x in texts:
			newTxt = translator.translate(x, src=lang, dest='es')
			texts[n] = newTxt.text
			n += 1
		lang = 'es'
	context.bot.send_message(update.message.chat_id, f'Idioma actualizado')

#Start method, greets the user and lets him select a language
def start(update, context):
	''' START '''
	context.bot.send_message(update.message.chat_id, texts[0]+" "+(str)(update.message.chat.username))
	sendMovements(update.message.chat_id, context)
	writeUserData(update.message.from_user.id, update.message.from_user.username,
                  update.message.from_user.first_name, update.message.from_user.last_name)
#Writes down the user data on a json
def writeUserData(userId, userName, firstName, lastName):	
	userData = {'userId': userId, 'userName': userName, 'firstName': firstName, 'lastName': lastName}
	exists = False
	try:
		with open("users.json", "r+") as file:
			fileData = json.load(file)
			for x in fileData['users']:
				if(x["userName"] == userName):
					exists = True
			if(not exists):
				fileData["users"].append(userData)
				file.seek(0)
				json.dump(fileData, file, indent=4)
	except Exception as e:
		print(e)

#Method to invoke the language buttons
def sendMovements(userID, context):
    context.bot.send_message(userID,
                             text=texts[1],
                             reply_markup=ReplyKeyboardMarkup([
                                 [Button1, Button2, Button3, Button4],
                             ], one_time_keyboard=True))

#Explains the basic commands that the user can use in the bot
def help(update, context):
	'''Help'''

	context.bot.send_message(update.message.chat_id, texts[2])

#Method to search and show a photo from the desired animal
def search(update, context):
	'''Search animals'''
	global lang
	global currAnimal
	chat_ide = update.message.chat.id
	
	with open('animals.json', 'r') as json_file:
		json_load = json.load(json_file)

	data = json_load['animals']
	exists = False
	
	if(currAnimal == "" or len(context.args) > 0):
		newParam = translator.translate(context.args[0], src=lang, dest='en')
		param = newParam.text
		currAnimal = newParam.text
	else:
		param = currAnimal
	for x in data:
		if(x["name"] == param):

			context.bot.send_message(update.message.chat_id, texts[3]+" "+currAnimal+"\n"+texts[4]+"\n"+texts[5])

			exists = True
			animal = x["photos"]
			random_number = random.randint(1, len(animal))
			for y in animal:
				if(y["id"] == random_number):
					downloadimages(y["photo"])
			context.bot.send_photo(chat_id=chat_ide, photo=open("local_file.jpg", "rb"))
	
	if(not exists):
		context.bot.send_message(update.message.chat_id, texts[6])

#Method to download images from a url
def downloadimages(myUrl):
    local_file = open('local_file.jpg','wb')
    image_url = myUrl
    resp = requests.get(image_url, stream=True)

    local_file.write(resp.content)
    
    local_file.close()

#Uses the search method again with the same animal
def more(update, context):
	search(update, context)
	
#Sends last image to another user (has to use the bot at least once)
def shareImage(update, context):
	exists = False
	with open("users.json") as file:
		json_load = json.load(file)
	data = json_load['users']
	for x in data:
		if (x['userName'] == context.args[0]):
			chat_id = x['userId']
			context.bot.send_message(update.message.chat_id, "Check this photo")
			context.bot.send_photo(chat_id=x['userId'], photo=open("local_file.jpg", "rb"))
			exists = True

	if(not exists):
		context.bot.send_message(update.message.chat_id, texts[7])

#Shows which animals are available
def available(update, context):
	global lang
	aviableAnimals = ""
	with open('animals.json', 'r') as json_file:
		json_load = json.load(json_file)

	data = json_load['animals']
	for x in data:
		translated = translator.translate(x["name"], src='en', dest=lang)
		aviableAnimals += translated.text+"\n"
	context.bot.send_message(update.message.chat_id, aviableAnimals)
#Main method
def main():
	TOKEN="5357388010:AAGVRs_kyKa2wBjvsR4HqG-azdKzHCXC3wA"
	updater=Updater(TOKEN, use_context=True)
	dp=updater.dispatcher

	# Eventos que activarán nuestro bot.
	dp.add_handler(CommandHandler('start',	start))
	dp.add_handler(CommandHandler('help', help))
	dp.add_handler(CommandHandler('search', search))
	dp.add_handler(CommandHandler('more', more))
	dp.add_handler(CommandHandler('available', available))
	dp.add_handler(CommandHandler('share', shareImage))
	dp.add_handler(CommandHandler('en', en))
	dp.add_handler(CommandHandler('ca', ca))
	dp.add_handler(CommandHandler('es', es))



	# Comienza el bot
	updater.start_polling()
	# Lo deja a la escucha. Evita que se detenga.
	updater.idle()


if __name__ == '__main__':
	main()
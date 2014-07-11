#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import httplib
import cPickle
import os.path
from ConfigParser import ConfigParser
from bs4 import BeautifulSoup as bs
from time import sleep



class Flat:
	def __init__(self, title, description, price, surface, rooms, city, date, link):
		self.title = title
		self.description = description
		self.price = price
		self.surface = surface
		self.rooms = rooms
		self.city = city
		self.date = date
		self.link = link

	def __eq__(self, other):
		return isinstance(other, Flat) and self.title == other.title and self.price == other.price and self.city == other.city

	def __str__(self):
		return self.city + '|' + self.rooms + '|' + self.surface + '|' + self.price + ' [' + self.title + ']'

	def __add__(self, other):
		return str(self) + other

	def __radd__(self, other):
		return other + str(self)



def pushover(userKey, apiToken, title, message, link, link_title) :
	try:
		cx = httplib.HTTPSConnection("api.pushover.net:443")
		cx.request(
			"POST",
			"/1/messages",
			urllib.urlencode({
				"token": apiToken,
				"user": userKey,
				"title": title,
				"message": message,
				"url": link,
				"url_title": link_title
				}),
			{"Content-type": "application/x-www-form-urlencoded"}
		)
	except Exception:
		pass



def searchAnibis(flat_canton, flat_price_min, flat_price_max, flat_surface_min, flat_surface_max, flat_rooms_min, flat_rooms_max):
	# Generate URL
	urls = []
	domain = 'http://www.anibis.ch'
	url = domain + '/fr/immobilier-locations-vaud--434/advertlist.aspx?sf=dpo&so=d&ps=60&'
	if flat_canton:
		url += 'sct=' + flat_canton + '&'
	if flat_price_min or flat_price_max or flat_surface_min or flat_surface_max or flat_rooms_min or flat_rooms_max:
		url += 'aral='
		if flat_price_min or flat_price_max:
			url += '834_'
			if flat_price_min:
				url += flat_price_min
			url += '_'
			if flat_price_max:
				url += flat_price_max
			url += ','
		if flat_surface_min or flat_surface_max:
			url += '851_'
			if flat_surface_min:
				url += flat_surface_min
			url += '_'
			if flat_surface_max:
				url += flat_surface_max
			url += ','
		if flat_rooms_min or flat_rooms_max:
			url += '865_'
			if flat_rooms_min:
				url += flat_rooms_min
			url += '_'
			if flat_rooms_max:
				url += flat_rooms_max
		if url[-1] == ',':
			url = url[:-1]
	urls.append(url)

	# Generate page URLs
	for i in [1,2,3]:
		urls.append(url + '&p=' + str(i))

	# Web scrapping
	flats = []
	for url in urls:
		page = urllib2.urlopen(url)
		soup = bs(page.read())
		results = soup.find('table', {'class':'items'}).findAll('tr')

		for result in results:
			for linebreak in result.findAll('br'):
				linebreak.extract()

			link = domain + result.td.a['href'].encode('utf-8')
			title = result.td.a.h2.string.encode('utf-8')

			description = ' '.join(results[1].find('span',{'class':'desc'}).stripped_strings).encode('utf-8')

			price = result.find('td', {'class':'price'}).string.encode('utf-8').strip()

			attrs = result.find('span', {'class':'attr'}).string.encode('utf-8').strip()
			attrs = dict( (a.strip(),b.strip()) for a,b in (attr.split(':') for attr in attrs.split('|')) )

			infos = result.find('span', {'class':'info'}).string.encode('utf-8').split('|')

			if 'Pi\xc3\xa8ces' in attrs:
				rooms = attrs['Pièces'].strip() + 'pièces'
			else:
				rooms = '?pièces'

			if 'Surface' in attrs:
				surface = attrs['Surface'].strip()
			else:
				surface = '??m2'

			date = infos[0].strip()
			city = infos[1].strip()

			flats.append(Flat(title, description, price, surface, rooms, city, date, link))
	return flats



def searchHomegate():
	flats = []
	return flats



def searchImmoscout24():
	flats = []
	return flats



def main():
	# Get configuration
	#######################################################
	config = ConfigParser()
	os.path.join(os.path.abspath(os.path.dirname(__file__)), 'conf', 'config.cfg')
	config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'flatFinder.cfg'))

	dataFile = config.get('main', 'dataFile')

	flat_canton = config.get('flat', 'canton')
	flat_price_min = config.get('flat', 'price_min')
	if flat_price_min == 'None':
		flat_price_min = None
	flat_price_max = config.get('flat', 'price_max')
	if flat_price_max == 'None':
		flat_price_max = None
	flat_surface_min = config.get('flat', 'surface_min')
	if flat_surface_min == 'None':
		flat_surface_min = None
	flat_surface_max = config.get('flat', 'surface_max')
	if flat_surface_max == 'None':
		flat_surface_max = None
	flat_rooms_min = config.get('flat', 'rooms_min')
	if flat_rooms_min == 'None':
		flat_rooms_min = None
	flat_rooms_max = config.get('flat', 'rooms_max')
	if flat_rooms_max == 'None':
		flat_rooms_max = None

	pushoverClients	= config.items('pushover')
	temp = []
	for pushoverClient in pushoverClients:
		user_key = pushoverClient[1].split(',')[0]
		api_token = pushoverClient[1].split(',')[1]
		temp.append({'user_key':user_key,'api_token':api_token})
	pushoverClients = temp


	# Load data
	#######################################################
	if os.path.isfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), dataFile)):
		with open(dataFile, "rb") as input:
			flats = cPickle.load(input)
	else:
		flats = []


	# Web scraping
	#######################################################
	anibisFlats = searchAnibis(flat_canton, flat_price_min, flat_price_max, flat_surface_min, flat_surface_max, flat_rooms_min, flat_rooms_max)
	homegateFlats = searchHomegate()
	immoscout24Flats = searchImmoscout24()

	newFlats = anibisFlats + homegateFlats + immoscout24Flats

	newFound = False
	for newFlat in newFlats:
		if not newFlat in flats:
			flats.append(newFlat)
			print "new >> " + newFlat
			for pushoverClient in pushoverClients:
				pushover(pushoverClient['user_key'], pushoverClient['api_token'], newFlat, newFlat.description, newFlat.link, 'Link')
			newFound = True
	if not newFound:
		print "No new flats"


	# Save data
	#######################################################
	with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), dataFile), "wb") as output:
		cPickle.dump(flats, output, cPickle.HIGHEST_PROTOCOL)

	# Done
	#######################################################
	print "--- " + str(len(flats)) + " in DB -----------------------------------------------------"



if __name__ == '__main__':
	main()
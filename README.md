# flatFinder
Python script to find flats in Switzerland and push new results to smarphone via Pushover.
It looks to flats corresponding to your search criteria and stores them. Each time a new flat is found, it is added to the database and a notification is sent to your smartphone via Pushover.

## Requirements
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/): Beautiful Soup is a Python library designed for quick turnaround projects like screen-scraping.
* [Pushover](http://pushover.net/) account

## Usage
* Configure your search by setting price, surface, etc.. in flatFinder.cfg or if you don't want to, just set them to "None"
* Set your Pushover API Token and your user key in flatFinder.cfg
* Add the script to your crontab and enjoy.

## Websites used
* [anibis](http://www.anibis.ch)
* [homegate](http://www.homegate.ch) (soon)
* [immoscout24](http://www.immoscout24.ch) (soon)
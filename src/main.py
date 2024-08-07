#!/usr/bin/env python3

import requests
import time
import optparse
import datetime
import json
import os
from dotenv import load_dotenv
import getpass

load_dotenv()

#################
version = '1.2.0'
#################

# set environment variable
os.environ['RESAWOD_NUBAPP_VERSION'] = version

# Text formating colors
red_color = '\033[1;31m'
green_color = '\033[1;32m'
reset_color = '\033[0m'

# Custom Exceptions
class SkipUser(Exception):
	pass
class NoSlotAvailable(Exception):
	pass

data_file_prefix: str = "/data" if not os.getenv('RESAWOD_DEV_MODE') else "src/personal_data"

with open(f'{data_file_prefix}/data.json') as json_file:
	user_data = json.load(json_file)

# Variables
application_id = user_data['app_data']['application_id'] # Replace by your id_application in data.json
category_activity_id = user_data['app_data']['category_activity_id'] # Replace by your id_category_activity in data.json


def get_session_id(session, id_application):
	headers = {
		'authority': 'sport.nubapp.com',
		'pragma': 'no-cache',
		'cache-control': 'no-cache',
		'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
		'sec-ch-ua-mobile': '?0',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-dest': 'document',
		'referer': f'https://sport.nubapp.com/web/setApplication.php?id_application={id_application}',
		'accept-language': 'fr-FR,fr;q=0.9',
		'cookie': f'applicationId={id_application}',
	}

	params = (
		('id_application', id_application),
		('isIframe', 'false'),
	)
	return session.get('https://sport.nubapp.com/web/cookieChecker.php', headers=headers, params=params)


def login(session, account, password):

	headers = {
		'authority': 'sport.nubapp.com',
		'pragma': 'no-cache',
		'cache-control': 'no-cache',
		'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
		'accept': 'application/json, text/plain, */*',
		'sec-ch-ua-mobile': '?0',
		'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
		'content-type': 'application/x-www-form-urlencoded',
		'origin': 'https://sport.nubapp.com',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-mode': 'cors',
		'sec-fetch-dest': 'empty',
		'referer': 'https://sport.nubapp.com/web/index.php',
		'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
	}

	data = {
		'username': account,
		'password': password
	}

	return session.post('https://sport.nubapp.com/web/ajax/users/checkUser.php', headers=headers, data=data)


def next_weekday(d, weekday):
	days_ahead = weekday - d.weekday()
	if days_ahead <= 0:  # Target day already happened this week
		days_ahead += 7
	return d + datetime.timedelta(days_ahead)


def get_slots(session, start_timestamp, end_timestamp, now_timestamp, id_application):
	headers = {
		'authority': 'sport.nubapp.com',
		'accept': 'application/json, text/javascript, */*; q=0.01',
		'x-requested-with': 'XMLHttpRequest',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-mode': 'cors',
		'sec-fetch-dest': 'empty',
		'referer': 'https://sport.nubapp.com/web/index.php',
		'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
	}

	params = (
		('id_category_activity', category_activity_id),
		('offset', '-120'),
		('start', start_timestamp),
		('end', end_timestamp),
		('_', now_timestamp),
	)
	return session.get('https://sport.nubapp.com/web/ajax/activities/getActivitiesCalendar.php', headers=headers, params=params).json()


def book(session, id_activity_calendar):
	headers = {
		'authority': 'sport.nubapp.com',
		'accept': 'application/json, text/plain, */*',
		'content-type': 'application/x-www-form-urlencoded',
		'origin': 'https://sport.nubapp.com',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-mode': 'cors',
		'sec-fetch-dest': 'empty',
		'x-kl-ajax-request': 'Ajax_Request',
		'referer': 'https://sport.nubapp.com/web/index.php',
		'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
	}

	data = {
		'items[activities][0][id_activity_calendar]': id_activity_calendar,
		'items[activities][0][unit_price]': '0',
		'items[activities][0][n_guests]': '0',
		'items[activities][0][id_resource]': 'false',
		'discount_code': 'false',
		'form': '',
		'formIntoNotes': ''
	}
	ret = session.post(
		'https://sport.nubapp.com/web/ajax/bookings/bookBookings.php', headers=headers, data=data)

	return ret


def main(user):
	print("=" * 100)
	print(f"[{user['name']}] Running script on {str(datetime.datetime.now())}")

	d = datetime.datetime.today()

	session = requests.Session()

	# Login
	get_session_id(session, application_id)
	res_login = login(session, user['login'], user['password']).json()

	if res_login.get('success'):
		print(f"[{user['name']}] {green_color}Login success{reset_color}")
	else:
		print(f"[{user['name']}] {red_color}Login failed, skipping user{reset_color}")
		raise SkipUser


	if options.verbose:
		print(f"Response from login: \n {res_login}")

	id_application = user_data['app_data']['application_id'] or res_login.get('user').get('id_application')

	if options.first_connexion:
		print("First connexion mode : WIP")
		raise SkipUser


	# Build slots
	start_h, start_min, end_h, end_min = 00, 00, 22, 00

	calendar = dict()
	days = dict([('monday', 0), ('tuesday', 1), ('wednesday', 2), ('thursday', 3), ('friday', 4), ('saturday', 5), ('sunday', 6)])
	for res_slot in user['slots']:
		if options.verbose:
			print(f'Jour en cours : {res_slot}')
			print(f'horaire du jour en cours : {str(user_data["slots"][res_slot])}')
		weekday = next_weekday(d, days[res_slot])
		search_start = datetime.datetime(
			weekday.year, weekday.month, weekday.day, start_h, start_min)
		search_end = datetime.datetime(
			weekday.year, weekday.month, weekday.day, end_h, end_min)

		slots = get_slots(session, search_start.timestamp(), search_end.timestamp(
		), datetime.datetime.now().timestamp(), id_application)
		eligible_slots = [s for s in slots if str(user_data["slots"][res_slot]) in s['start']]

		if len(eligible_slots) == 1:
			assert len(eligible_slots) == 1
			slot = eligible_slots[0]

			calendar[res_slot[0]] = {
				'start': slot['start_time'],
				'end': slot['end_time'],
				'slot_id': slot['id_activity_calendar'],
				'activity': slot['name_activity']
			}
			if options.dry_run:
				print("Dry run mode : no booking - just printing the slot")
			else:
				print(f"Booking for {slot['name_activity']}, {res_slot.capitalize()} from {slot['start_time']} to {slot['end_time']}")
				book_res = book(session, slot['id_activity_calendar'])
				book_res = json.loads(book_res.content)
		else:
			print(f'No slot available for {res_slot.capitalize()} at {str(user_data["slots"][res_slot])}')


if __name__ == "__main__":
	# Print version & user
	message: str = 'Resawod Nubapp Reservator version : '
	print('#' * (len(message + version) + 4))
	print(f'# {message}{version} #')
	print('#' * (len(message + version) + 4))
	print(f'Launched by : {getpass.getuser()}')

	# Parse options
	parser = optparse.OptionParser()

	parser.add_option('-f', '--first-connexion', action="store_true", dest="first_connexion", default=False,
                   help="[WIP] If it's the first connexion of the user, the script will show your id_application & id_category_activity.")
	parser.add_option('-v', '--verbose', action="store_true", dest="verbose", default=False, help="Verbose mode")
	parser.add_option('-d', '--dry-run', action="store_true", dest="dry_run", default=False, help="Dry-run mode to test connexion settings")

	options, _ = parser.parse_args()

	everything_OK: bool = False

	while not everything_OK:
		for user in user_data['users']:
			user_nb_slots = len(user['slots'])
			res_errors: int = 0
			everything_OK = True
			try:
				main(user)
			except SkipUser:
				continue
			except NoSlotAvailable:
				res_errors += 1
				if res_errors == user_nb_slots:
					everything_OK = False
					print(f"Slots for next week not yet available for {user['name']}")
					print("Waiting for 5 min")
					time.sleep(300)
					break
				else:
					continue
    
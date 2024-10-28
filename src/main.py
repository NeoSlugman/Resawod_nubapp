#!/usr/bin/env python3

import requests
from time import sleep 
import optparse
import datetime
import json
import os
from dotenv import load_dotenv
import getpass

load_dotenv()

#################
version = '1.3.5'
#################

# set environment variable
os.environ['RESAWOD_NUBAPP_VERSION'] = version

# Text formating colors
red_color = '\033[1;31m'
orange_color = '\033[1;33m'
green_color = '\033[1;32m'
reset_color = '\033[0m'

# Custom Exceptions
class SkipUser(Exception):
	pass
class NoSlotAvailable(Exception):
	pass

dev_mode: bool = True if os.getenv('RESAWOD_DEV_MODE') else False
data_file_prefix: str = "/data" if not dev_mode else "src/personal_data"
data_file: str = f"{data_file_prefix}/data.json" if not dev_mode else f"{data_file_prefix}/data-dev.json"


def get_session_id(session, id_application):
	headers = {
		'cookie': f'applicationId={id_application}',
	}

	params = (
		('id_application', id_application),
		('isIframe', 'false'),
	)
	return session.get('https://sport.nubapp.com/web/cookieChecker.php', headers=headers, params=params)


def login(session, account, password):

	data = {
		'username': account,
		'password': password
	}

	return session.post('https://sport.nubapp.com/web/ajax/users/checkUser.php', data=data)


def next_weekday(d, weekday):
	days_ahead = weekday - d.weekday()
	if days_ahead <= 0:  # Target day already happened this week
		days_ahead += 7
	return d + datetime.timedelta(days_ahead)


def get_slots(session, start_timestamp, end_timestamp, now_timestamp, id_application):

	params = (
		('id_category_activity', category_activity_id),
		('offset', '-120'),
		('start', start_timestamp),
		('end', end_timestamp),
		('_', now_timestamp),
	)
	return session.get('https://sport.nubapp.com/web/ajax/activities/getActivitiesCalendar.php', params=params).json()


def book(session, id_activity_calendar):

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
		'https://sport.nubapp.com/web/ajax/bookings/bookBookings.php', data=data)

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
			print(f'Jour en cours : {res_slot["day"]}')
			print(f'Horaire du jour en cours : {res_slot["time"]}')
			print(f'Activité : {res_slot["activity"]}')

		weekday = next_weekday(d, days[res_slot["day"]])
		search_start = datetime.datetime(
			weekday.year, weekday.month, weekday.day, start_h, start_min)
		search_end = datetime.datetime(
			weekday.year, weekday.month, weekday.day, end_h, end_min)

		slots = get_slots(session, search_start.timestamp(), search_end.timestamp(
		), datetime.datetime.now().timestamp(), id_application)
		eligible_slots = [s for s in slots if (res_slot["time"] in s['start_time'] 
							and res_slot["activity"] in s['name_activity'])]
		# print(f'{len(eligible_slots)} slot found for {res_slot["activity"]} on {res_slot["day"].capitalize()} at {str(res_slot["time"])}')
		with open("src/test/eligible_slots_test.json", "w") as f:
			json.dump(slots, f)

		if len(eligible_slots) == 0:
			global res_errors
			res_errors += 1
			print(f'{red_color}Error : no slot available for {res_slot["activity"]} on {res_slot["day"].capitalize()} at {str(res_slot["time"])}{reset_color}')
			# If every reservations failed, maybe the slots are not yet available for the next week -> raise an error
			if res_errors == len(user['slots']) and res_errors > 1:
				# print(f'No slot available for {res_slot["activity"]} on {res_slot["day"].capitalize()} at {str(res_slot["time"])}')
				print("It's seems that slots are not yet available for the next week")
				raise NoSlotAvailable
			else:
				continue
					
		else:
			slot = eligible_slots[0]

			calendar[res_slot["day"]] = {
				'start': slot['start_time'],
				'end': slot['end_time'],
				'slot_id': slot['id_activity_calendar'],
				'activity': slot['name_activity']
			}
			if options.dry_run:
				print(f"{orange_color}Dry run mode : no booking - just printing the slot{reset_color}")
			else:
				book_res = book(session, slot['id_activity_calendar'])
				book_res = json.loads(book_res.content)
				match int(book_res['error']):
					case 0:
						print(f"{green_color}Booked for {slot['name_activity']} on {res_slot['day'].capitalize()} from {slot['start_time']} to {slot['end_time']}{reset_color}")
					case 5:
						print(f"{orange_color}Already booked for {slot['name_activity']} on {res_slot['day'].capitalize()} from {slot['start_time']} to {slot['end_time']}{reset_color}")


if __name__ == "__main__":
	# Print version & user
	message: str = 'Resawod Nubapp Reservator version : '
	print('#' * (len(message + version) + 4))
	print(f'# {message}{version} #')
	print('#' * (len(message + version) + 4))
	print(f'Launched by : {getpass.getuser()}')
	print(f'at {datetime.datetime.now()}')

	# Parse options
	parser = optparse.OptionParser()

	parser.add_option('-f', '--first-connexion', action="store_true", dest="first_connexion", default=False,
                   help="[WIP] If it's the first connexion of the user, the script will show your id_application & id_category_activity.")
	parser.add_option('-v', '--verbose', action="store_true", dest="verbose", default=False, help="Verbose mode")
	parser.add_option('-d', '--dry-run', action="store_true", dest="dry_run", default=False, help="Dry-run mode to test connexion settings")

	options, _ = parser.parse_args()

	# Main program

	# Setup
	Everything_OK: bool = False

	# If every reservation failed, wait for 5 min and retry
	while not Everything_OK:			
		with open(data_file, 'r') as json_file:
			user_data = json.load(json_file)

		# Variables
		application_id: int = user_data['app_data']['application_id'] # Replace by your id_application in data.json
		category_activity_id: int = user_data['app_data']['category_activity_id'] # Replace by your id_category_activity in data.json

		# Loop over users
		for user in user_data['users']:
			res_errors: int = 0
			try:
				main(user)
				Everything_OK = True
			except SkipUser:
				continue
			except NoSlotAvailable:
				if dev_mode:
					print('Dev Mode, Waiting 3s')
					sleep(3)
				else:
					print("Waiting for 3 min")
					sleep(180)
				Everything_OK = False
				break
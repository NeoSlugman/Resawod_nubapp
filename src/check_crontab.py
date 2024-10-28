#!/usr/bin/env python3

from crontab import CronTab
from dotenv import load_dotenv
import json
import os

load_dotenv()

crondays: dict[str,int] = {
	"monday": 1,
	"tuesday": 2,
	"wednesday": 3,
	"thursday": 4,
	"friday": 5,
	"saturday": 6,
	"sunday": 7,
}

dev_mode: bool = True if os.getenv('RESAWOD_DEV_MODE') else False
data_file_prefix: str = "/data" if not dev_mode else "src/personal_data"
data_file: str = f"{data_file_prefix}/data.json" if not dev_mode else f"{data_file_prefix}/data-dev.json"

cron = CronTab(user="neoslugman")
slots_to_book: list[list[str]] = []

with open(data_file, "r") as file:
	data = json.load(file)

for user in data["users"]:
	for slot in user["slots"]:
		day, time = slot["day"], slot["endtime"]
		hour, minute = time.split(":")
		# print(day, hour, minute)
		if [day, hour, minute] not in slots_to_book:
			slots_to_book.append([day, hour, minute])

# print(slots_to_book)

# TODO : add slots to cron

for event in slots_to_book:
    day, hour, minute = event
    # print(hour+":"+minute)
    job = cron.new(command="echo POUET", comment="Resawod")
    # print(crondays[day])
    job.minute.on(int(minute))
    job.hour.also.on(int(hour))
    job.day.also.on(crondays[day])
    cron.write()
    # cron.add(minute=minute, hour=hour, day=day)
import asyncio
import base64
import json
import logging
import os
import random
import re
from datetime import date, datetime, timedelta

import pytz
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from database.users_chats_db import db
from info import ADMINS
   

@Client.on_message(filters.command("report") & filters.user(ADMINS))
async def get_report(client, message):
    keyboard = [
        [
            InlineKeyboardButton("Yesterday", callback_data="yesterday"),
            InlineKeyboardButton("Last 7 Days", callback_data="last_7_days"),
        ],
        [
            InlineKeyboardButton("Last 30 Days", callback_data="last_30_days"),
            InlineKeyboardButton("This Year", callback_data="this_year"),
        ],
        [
            InlineKeyboardButton("Weekly", callback_data="every_7_days_total_count"),
            InlineKeyboardButton("Monthly", callback_data="every_30_days_total_count"),
        ],
        [
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    today = date.today()
    report_date = today.strftime('%d %B, %Y')
    report = f"Report for {report_date}:\n\n"

    total_users = await db.daily_users_count(today)
    total_chats = await db.daily_chats_count(today)
    report += f"{today.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    await message.reply_text(report, reply_markup=reply_markup, quote=True)


@Client.on_callback_query(filters.regex("yesterday"))
async def report_yesterday(client, callback_query):
    # Calculate the start and end dates for yesterday
    yesterday = date.today() - timedelta(days=1)
    start_date = yesterday
    end_date = yesterday

    current_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    total_users = await db.daily_users_count(current_datetime)
    total_chats = await db.daily_chats_count(current_datetime)

    report = f"Yesterday's Report:\n{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"Users: {total_users}, Chats: {total_chats}\n"
    keyboard = InlineKeyboardMarkup(
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_yesterday")
        ]
    )

    await callback_query.edit_message_text(report, reply_markup=keyboard, quote=True)
        
@Client.on_callback_query(filters.regex("last_7_days"))
async def report_last_7_days(client, callback_query):
    today = date.today()
    past_days = 7
    start_date = today - timedelta(days=6)
    end_date = today

    report = "Last 7 Days' Report:\n\n"

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
    
    keyboard = InlineKeyboardMarkup(
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_last_7_days")
        ]
    )

    await callback_query.edit_message_text(report, reply_markup=keyboard, quote=True)


@Client.on_callback_query(filters.regex("last_30_days"))
async def report_last_30_days(client, callback_query):
    today = date.today()
    past_days = 30
    start_date = today - timedelta(days=past_days - 1)
    end_date = today

    report = "Last 30 Days' Report:\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    for i in range(start_index, end_index):
        if i >= past_days:
            break
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    keyboard_buttons = [
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_last_30_days")
        ]
    ]

    if page > 1:  # If it's not the first page
        keyboard_buttons.append([
            InlineKeyboardButton("<< Prev", callback_data="last_30_days_{}".format(page - 1))
        ])

    if end_index < past_days:  # If there is a next page
        keyboard_buttons.append([
            InlineKeyboardButton("Next >>", callback_data="last_30_days_{}".format(page + 1))
        ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await callback_query.edit_message_text(report, reply_markup=keyboard, quote=True)

@Client.on_callback_query(filters.regex("this_year"))
async def report_this_year(client, callback_query):
    # Calculate the start and end dates for this year
    today = date.today()
    start_date = date(today.year, 1, 1)
    end_date = today

    report = "This Year's Report:\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date
    count = 0

    while current_date <= end_date:
        if count >= start_index:
            current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
            total_users = await db.daily_users_count(current_datetime)
            total_chats = await db.daily_chats_count(current_datetime)
            report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=1)
        count += 1

    keyboard_buttons = [
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_this_year")
        ]
    ]

    if count > end_index:  # If there is a next page
        keyboard_buttons.append([
            InlineKeyboardButton("Next >>", callback_data="this_year_{}".format(page + 1))
        ])

    if page > 1:  # If it's not the first page
        keyboard_buttons.append([
            InlineKeyboardButton("<< Prev", callback_data="this_year_{}".format(page - 1))
        ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await callback_query.edit_message_text(report, reply_markup=keyboard, quote=True)

@Client.on_callback_query(filters.regex("every_7_days_total_count"))
async def report_every_7_days_total_count(client, callback_query):
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today

    report = "Weekly Report (Last 12 Months):\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date + timedelta(days=start_index * 7)
    for i in range(start_index, end_index):
        if current_date > end_date:
            break
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=7)

    keyboard_buttons = [
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_every_7_days_total_count")
        ]
    ]

    if current_date <= end_date:  # If there is a next page
        keyboard_buttons.append([
            InlineKeyboardButton("Next >>", callback_data="every_7_days_total_count_{}".format(page + 1))
        ])

    if page > 1:  # If it's not the first page
        keyboard_buttons.append([
            InlineKeyboardButton("<< Prev", callback_data="every_7_days_total_count_{}".format(page - 1))
        ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await callback_query.edit_message_text(report, reply_markup=keyboard, quote=True)


@Client.on_callback_query(filters.regex("every_30_days_total_count"))
async def report_every_30_days_total_count(client, callback_query):
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today

    report = "Monthly Report: (Last 12 Months):\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date + timedelta(days=start_index * 30)
    for i in range(start_index, end_index):
        if current_date > end_date:
            break
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=30)

    keyboard_buttons = [
        [
            InlineKeyboardButton("Home", callback_data="report"),
            InlineKeyboardButton("Cancel", callback_data="report_cancel")
        ],
        [
            InlineKeyboardButton("Download", callback_data="download_every_30_days_total_count")
        ]
    ]

    if current_date <= end_date:  # If there is a next page
        keyboard_buttons.append([
            InlineKeyboardButton("Next >>", callback_data="every_30_days_total_count_{}".format(page + 1))
        ])

    if page > 1:  # If it's not the first page
        keyboard_buttons.append([
            InlineKeyboardButton("<< Prev", callback_data="every_30_days_total_count_{}".format(page - 1))
        ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await callback_query.edit_message_text(report, reply_markup=keyboard, quote=True)

@Client.on_callback_query(filters.regex("cancel"))
async def cancel_report(client, callback_query):
    # Handle cancel button action
    await callback_query.edit_message_text("Report canceled.", quote=True)


@Client.on_callback_query(filters.regex("download_yesterday"))
async def download_report_yesterday(client, callback_query):
    # Calculate the start and end dates for yesterday
    yesterday = date.today() - timedelta(days=1)
    start_date = yesterday
    end_date = yesterday

    current_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    total_users = await db.daily_users_count(current_datetime)
    total_chats = await db.daily_chats_count(current_datetime)

    report = f"Yesterday's Report:\n{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"Users: {total_users}, Chats: {total_chats}\n"

    file_name = "report_yesterday.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_last_7_days"))
async def download_report_last_7_days(client, callback_query):
    today = date.today()
    past_days = 7
    start_date = today - timedelta(days=6)
    end_date = today

    report = "Last 7 Days' Report:\n\n"

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    file_name = "report_last_7_days.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_last_30_days"))
async def download_report_last_30_days(client, callback_query):
    today = date.today()
    past_days = 30
    start_date = today - timedelta(days=past_days - 1)
    end_date = today

    report = "Last 30 Days' Report:\n\n"

    for i in range(past_days):
        current_date = start_date + timedelta(days=i)
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        current_date_str = current_datetime.strftime('%d %B, %Y')
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"

    file_name = "report_last_30_days.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_this_year"))
async def download_report_this_year(client, callback_query):
    today = date.today()
    start_date = date(today.year, 1, 1)
    end_date = today

    report = "This Year's Report:\n\n"

    current_date = start_date
    while current_date <= end_date:
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=1)

    file_name = "report_this_year.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_every_7_days_total_count"))
async def download_report_every_7_days_total_count(client, callback_query):
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today

    report = "Weekly Report (Last 12 Months):\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date + timedelta(days=start_index * 7)
    for i in range(start_index, end_index):
        if current_date > end_date:
            break
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=7)

    file_name = "weekly_report.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)

@Client.on_callback_query(filters.regex("download_every_30_days_total_count"))
async def download_report_every_30_days_total_count(client, callback_query):
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today

    report = "Monthly Report (Last 12 Months):\n\n"

    page = int(callback_query.data.split("_")[-1])
    results_per_page = 7
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    current_date = start_date + timedelta(days=start_index * 30)
    for i in range(start_index, end_index):
        if current_date > end_date:
            break
        current_datetime = datetime.datetime.combine(current_date, datetime.time.min)
        total_users = await db.daily_users_count(current_datetime)
        total_chats = await db.daily_chats_count(current_datetime)
        report += f"{current_datetime.strftime('%Y-%m-%d')}: Users: {total_users}, Chats: {total_chats}\n"
        current_date += timedelta(days=30)

    file_name = "monthly_report.txt"
    file_content = report.encode("utf-8")

    await client.send_document(callback_query.from_user.id, file_content, caption=file_name)
    

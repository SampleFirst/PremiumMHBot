# skymovies.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
from info import ADMINS, LOG_CHANNEL 
from urllib.parse import urlparse

movie_links = {}
group_links = {}


@Client.on_message(filters.command("skymovies"))
async def skymovieshd(client, message):
    query = message.text.split(maxsplit=1)
    if len(query) == 1:
        await message.reply_text("Please provide a movie name to search.")
        return
    query = query[1]
    search_results = await message.reply_text("Processing...")
    try:
        movies_list = search_movies(query)
        if movies_list:
            keyboards = []
            for movie in movies_list:
                keyboard = [InlineKeyboardButton(movie["title"], callback_data=movie["id"])]
                keyboards.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboards)
            await search_results.edit_text('Search Results...', reply_markup=reply_markup)
        else:
            await search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")


@Client.on_callback_query(filters.regex('^app\d+$'))
async def movie_result(client, callback_query):
    try:
        query = callback_query
        movie_id = query.data
        group_list = get_movie(movie_links[movie_id])
        if group_list:
            keyboards = []
            for group in group_list:
                keyboard = [InlineKeyboardButton(group["title"], callback_data=group["id"])]
                keyboards.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboards)
            await query.answer("Sent group finals..")
            await query.message.reply_text("Choose Download Link:", reply_markup=reply_markup)
        else:
            await query.message.reply_text("No group finals available for this movie.")
    except Exception as e:
        await query.message.reply_text(f"An error occurred: {str(e)}")
 

@Client.on_callback_query(filters.regex('^pay\d+$'))
async def final_movies_result(client, callback_query):
    try:
        query = callback_query
        group_id = query.data
        finale_list = final_page(group_links[group_id])
        if finale_list:
            keyboard = [
                [
                    InlineKeyboardButton(final["title"], url=final["id"]
                    ),
                ]
                for final in finale_list
            ]
            keyboard.insert(0, 
                [
                    InlineKeyboardButton('info', callback_data='info')
                ]
            )
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.answer("Sent finale download links..")
            await query.message.reply_text("Extracted Links:", reply_markup=reply_markup)
        else:
            await query.message.reply_text("No download links available for this movie.")
    except Exception as e:
        await query.message.reply_text(f"An error occurred: {str(e)}")
 

def search_movies(query):
    movies_list = []
    try:
        website = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
        if website.status_code == 200:
            website = website.text
            website = BeautifulSoup(website, "html.parser")
            movies = website.find_all("div", {'class': 'L'})
            for movie in movies:
                movie_details = {}
                movie_link = movie.find("a", href=True)
                if movie_link:
                    movie_details["id"] = f"app{movies.index(movie)}"
                    movie_details["title"] = movie_link.text.strip()
                    movie_links[movie_details["id"]] = movie_link['href']
                    movies_list.append(movie_details)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return movies_list


def get_movie(movie_page_url):
    group_list = []
    try:
        movie_page = "https://skymovieshd.ngo" + movie_page_url
        webpage = requests.get(movie_page)
        if webpage.status_code == 200:
            webpage = webpage.text
            webpage = BeautifulSoup(webpage, "html.parser")
            groups = webpage.find("div", {'class': 'Bolly'})
            if groups:
                groups = groups.find_all("a", href=True)
                for group in groups:
                    group_details = {}
                    group_details["id"] = f"pay{groups.index(group)}"
                    group_details["title"] = group.text.strip()
                    group_links[group_details["id"]] = group['href']
                    group_list.append(group_details)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return group_list


def final_page(final_page_url):
    finale_list = []
    try:
        final_page = final_page_url
        webpage = requests.get(final_page)
        if webpage.status_code == 200:
            webpage = webpage.text
            webpage = BeautifulSoup(webpage, "html.parser")
            finals = webpage.find_all("a", href=True, rel="external", target="_blank")
            for final in finals:
                finale_details = {}
                finale_details["id"] = final['href']
                parsed_url = urlparse(final['href'])
                finale_details["title"] = parsed_url.netloc
                finale_list.append(finale_details)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return finale_list


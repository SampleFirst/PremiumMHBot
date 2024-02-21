# skymovies.py 
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
import re

url_list = {}
group_links = {}


@Client.on_message(filters.command("skymovies"))
async def skymovies(client, message):
    query = message.text.split(maxsplit=1)
    if len(query) == 1:
        await message.reply_text("Please provide a movie name to search.")
        return
    query = query[1]
    search_results = await message.reply_text("Processing...")
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = [InlineKeyboardButton(movie["title"], callback_data=f"movie_{movie['id']}")]
            keyboards.append(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboards)
        await search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        await search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


@Client.on_callback_query(filters.regex('^movie_'))
async def movie_result(client, callback_query):
    query = callback_query
    movie_id = query.data.split("_")[1]
    group_links[movie_id] = get_group_links(url_list[movie_id])
    group_buttons = []
    for group_id, group_name in group_links[movie_id].items():
        button = InlineKeyboardButton(group_name, callback_data=f"group_{movie_id}_{group_id}")
        group_buttons.append([button])
    reply_markup = InlineKeyboardMarkup(group_buttons)
    await query.message.reply_text("Choose a download group:", reply_markup=reply_markup)


@Client.on_callback_query(filters.regex('^group_'))
async def group_result(client, callback_query):
    query = callback_query
    _, movie_id, group_id = query.data.split("_")
    final_links = get_final_links(group_links[movie_id][group_id])
    link_buttons = []
    for link_name, link_url in final_links.items():
        button = InlineKeyboardButton(link_name, url=link_url)
        link_buttons.append([button])
    reply_markup = InlineKeyboardMarkup(link_buttons)
    await query.message.reply_text("Choose a download link:", reply_markup=reply_markup)


def search_movies(query):
    movies_list = []
    website = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
    if website.status_code == 200:
        website = website.text
        website = BeautifulSoup(website, "html.parser")
        movies = website.find_all("div", class_="L")
        for movie in movies:
            link = movie.find("a")
            if link:
                movie_details = {}
                movie_details["id"] = f"len{movies.index(movie)}"
                movie_details["title"] = link.text.strip()
                url_list[movie_details["id"]] = link['href']
                movies_list.append(movie_details)
    return movies_list


def get_group_links(movie_page_url):
    group_details = {}
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        links = movie_page_link.find_all("a", {'href': re.compile(r'https://howblogs.xyz/*')})
        for i in links:
            group_details[f"{i.text}"] = i['href']
    return group_details


def get_final_links(group_page_url):
    final_details = {}
    movie_page_link = requests.get(group_page_url)
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        links = movie_page_link.find_all("a", {'rel': 'external', 'target': '_blank'})
        for i in links:
            final_details[i.text.strip()] = i['href']
    return final_details

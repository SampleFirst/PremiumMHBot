# mkvcinemas.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
from io import BytesIO

url_list = {}
movie_links = {}
group_links = {}


@Client.on_message(filters.command("mkvcinemas"))
async def mkvcinemas(client, message):
    query = message.text.split(maxsplit=1)
    if len(query) == 1:
        await message.reply_text("Please provide a movie name to search.")
        return
    query = query[1]
    search_results = await message.reply_text("Processing...")
    movies_list = search_movies_mkvcinemas(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = [InlineKeyboardButton(movie["title"], callback_data=movie["id"])]
            keyboards.append(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboards)
        await search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        await search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


@Client.on_callback_query(filters.regex('^link'))
async def movie_result(client, callback_query):
    query = callback_query
    movie_id = query.data
    s = get_movie_mkvcinemas(url_list[movie_id])
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    await query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link_buttons = []
    links = s["links"]
    for name, link in links.items():
        button = InlineKeyboardButton(name, url=link)
        link_buttons.append([button])

    caption = f"🎥 {s['title']}\n\n⚡ Download Links:"
    reply_markup = InlineKeyboardMarkup(link_buttons)
    
    await query.message.reply_text(caption, reply_markup=reply_markup)
    await query.answer("Sent movie links")


@Client.on_message(filters.command("skymovies"))
async def skymovieshd(client, message):
    query = message.text.split(maxsplit=1)
    if len(query) == 1:
        await message.reply_text("Please provide a movie name to search.")
        return
    query = query[1]
    search_results = await message.reply_text("Processing...")
    try:
        movies_list = search_movies_skymovies(query)
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
        group_list = get_movie_skymovies(movie_links[movie_id])
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
        finale_list = final_page_skymovies(group_links[group_id])
        if finale_list:
            links = finale_list["links"]
            buttons = []
            for name, link in links.items():
                button = InlineKeyboardButton(text=name, url=link)
                buttons.append([button])
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.reply_text("Click on the below buttons to download:", reply_markup=reply_markup)
            await query.answer("Sent movie links")
        else:
            await query.message.reply_text("No download links available for this movie.")
    except Exception as e:
        await query.message.reply_text(f"An error occurred: {str(e)}")


def search_movies_mkvcinemas(query):
    movies_list = []
    movies_details = {}
    website = requests.get(f"https://mkvcinemas.dev/?s={query.replace(' ', '+')}")
    if website.status_code == 200:
        website = website.text
        website = BeautifulSoup(website, "html.parser")
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        for movie in movies:
            if movie:
                movies_details["id"] = f"link{movies.index(movie)}"
                movies_details["title"] = movie.find("span", {'class': 'mli-info'}).text
                url_list[movies_details["id"]] = movie['href']
                movies_list.append(movies_details)
                movies_details = {}
    return movies_list


def get_movie_mkvcinemas(movie_page_url):
    movie_details = {}
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
        movie_details["title"] = title
        img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
        movie_details["img"] = img
        links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
        final_links = {}
        for i in links:
            final_links[f"{i.text}"] = i['href']
        movie_details["links"] = final_links
    return movie_details


def search_movies_skymovies(query):
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


def get_movie_skymovies(movie_page_url):
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


def final_page_skymovies(final_page_url):
    finale_list = {}
    try:
        final_page = final_page_url
        webpage = requests.get(final_page)
        if webpage.status_code == 200:
            webpage = webpage.text
            webpage = BeautifulSoup(webpage, 'html.parser')
            links = webpage.find_all("a", {'rel': 'external', 'target': '_blank'})
            final_links = {}
            for link in links:
                final_links[link.text.strip()] = link['href']
            finale_list["links"] = final_links
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return finale_list



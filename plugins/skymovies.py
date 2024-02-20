from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup

url_list = {}
sky_list = {}


# Search Movies results in Skymovieshd
def search_movies(query):
    movies_list = []
    website = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
    if website.status_code == 200:
        soup = BeautifulSoup(website.text, "html.parser")
        movies = soup.find_all("div", class_="L")
        for movie in movies:
            link = movie.find("a")
            if link:
                movie_details = {}
                movie_details["id"] = f"link{movies.index(movie)}"
                movie_details["title"] = link.text.strip()
                url_list[movie_details["id"]] = link['href']
                movies_list.append(movie_details)
    return movies_list

# Select Movies list if user select movie and get Download Group list (Google Drive links)
def get_sky_link(movie_page_url):
    sky_link_list = []
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        soup = BeautifulSoup(movie_page_link.text, "html.parser")
        skylinks = soup.find_all("div", class_="Bolly")
        for skylink in skylinks:
            sky = skylink.find("a")
            if sky:
                sky_details = {}
                sky_details["id"] = f"sky{skylinks.index(skylink)}"
                sky_details["title"] = sky.text.strip()
                sky_list[sky_details["id"]] = sky['href']
                sky_link_list.append(sky_details)
    return sky_link_list


# Get final download links if user selects Download Group link (gdtot, gdflix, filepress)
def get_movie(sky_page_url):
    final_links = []
    sky_page_link = requests.get(sky_page_url)
    if sky_page_link.status_code == 200:
        soup = BeautifulSoup(sky_page_link.text, "html.parser")
        tags = soup.find_all("a", rel="external")
        for tag in tags:
            final_links.append(tag['href'])
    return final_links



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
            keyboard = [InlineKeyboardButton(movie["title"], callback_data=movie["id"])]
            keyboards.append(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboards)
        await search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        await search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


@Client.on_callback_query(filters.regex('^link'))
async def sky_results(client, callback_query):
    query = callback_query
    movie_id = query.data
    sky_link_list = get_sky_link(url_list[movie_id])
    if sky_link_list:
        keyboards = []
        for sky_link in sky_link_list:
            keyboard = [InlineKeyboardButton(sky_link["title"], callback_data=sky_link["id"])]
            keyboards.append(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboards)
        await query.message.edit_text('Select a Download Group...', reply_markup=reply_markup)
    else:
        await query.message.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


@Client.on_callback_query(filters.regex('^sky'))
async def movie_result(client, callback_query):
    query = callback_query
    sky_id = query.data
    final_links = get_movie(sky_list[sky_id])
    if final_links:
        text = "Final Download Links:\n"
        for link in final_links:
            text += f"- [{link}]({link})\n"
        await query.message.edit_text(text, disable_web_page_preview=True)
    else:
        await query.message.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')



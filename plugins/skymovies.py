from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
from io import BytesIO

url_list = {}


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

@Client.on_callback_query()
async def callback_handlers(client, callback_query):
    if callback_query.data.startswith("link"):
        movie_id = callback_query.data
        movie_page_url = url_list.get(movie_id)
        if movie_page_url:
            download_groups = get_movie(movie_page_url)
            if download_groups:
                keyboards = []
                for group in download_groups:
                    keyboard = []
                    for link in group["links"]:
                        keyboard.append(InlineKeyboardButton(link["title"], callback_data=f"download_{link['url']}"))
                    keyboards.append(keyboard)
                reply_markup = InlineKeyboardMarkup(keyboards)
                await callback_query.message.edit_text(group["title"], reply_markup=reply_markup)
    elif callback_query.data.startswith("download"):
        download_url = callback_query.data.split("_", 1)[1]
        # Fetch the final download URL or handle as needed
        await callback_query.answer(text="Processing download...")
        # Handle the download process here


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


def get_movie(movie_page_url):
    downloads_list = []
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        soup = BeautifulSoup(movie_page_link.text, "html.parser")
        download_groups = soup.find_all("div", class_="Bolly")  # Assuming download groups are in divs with class "Bolly"
        for group in download_groups:
            group_details = {}
            links = group.find_all("a")
            if links:
                group_details["title"] = group.find("b").text.strip()
                group_details["links"] = []
                for link in links:
                    group_details["links"].append({"title": link.text.strip(), "url": link['href']})
                downloads_list.append(group_details)
    return downloads_list

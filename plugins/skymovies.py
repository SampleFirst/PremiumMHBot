from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup
from io import BytesIO

url_list = {}
grp_list = {}


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
        await message.reply_text('Search Results...', reply_markup=reply_markup)
    else:
        await message.reply_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')

@Client.on_callback_query()
async def callback_handlers(client, callback_query):
    try:
        if callback_query.data.startswith("link"):        
            movie_id = callback_query.data
            if movie_page_url:
                groups_list = get_movie(url_list[movie_id])
                if groups_list:
                    keyboards = []
                    for group in groups_list:
                        keyboard = [InlineKeyboardButton(group["title"], callback_data=group["id"])]
                        keyboards.append(keyboard)
                    reply_markup = InlineKeyboardMarkup(keyboards)
                    
                    await query.message.edit_text('Download Groups Results...', reply_markup=reply_markup)
                else:
                    await query.message.edit_text('Sorry 🙏, No Result Found!')
    
        elif callback_query.data.startswith("grp"):
            download_url = callback_query.data.split("_", 1)[1]
            # Fetch the final download URL or handle as needed
            await callback_query.answer(text="Processing download...")
            # Handle the download process here
    except Exception as e:
        await callback_query.message.edit_text(text=f"An error occurred: {str(e)}")


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
    groups_list = []
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        soup = BeautifulSoup(movie_page_link.text, "html.parser")
        groups = soup.find_all("div", class_="Bolly")  # Assuming download groups are in divs with class "Bolly"
        for group in groups:
            link = group.find_all("a")
            if link:
                group_details = {}                
                group_details["id"] = f"grp{groups.index(group)}"
                group_details["title"] = link.text.strip()
                grp_list[movie_details["id"]] = link['href']
                groups_list.append(group_details)
    return groups_list
    

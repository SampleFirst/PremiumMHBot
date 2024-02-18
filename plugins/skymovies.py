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

@Client.on_callback_query(filters.regex('^link'))
async def skymovie_result(client, callback_query):
    query = callback_query
    movie_id = query.data
    s = get_movie(url_list[movie_id])
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    await query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Download Links :-\n\n{link}"
    await query.message.reply_text(text=caption)
    await query.answer("Sent movie links")

def search_movies(query):
    movies_list = []
    movies_details = {}
    
    # Updated to use the provided website for searching movies
    website = requests.get(f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All")
    
    if website.status_code == 200:
        website = website.text
        soup = BeautifulSoup(website, "html.parser")
        
        # Finding all movie names before 'file folder' icon 
        movies = soup.find_all("div", class_="main")
        
        for movie in movies:
            title_text = movie.find("a").text
            
            if title_text:  # Checking if the text is not empty or None
                
                # Creating a dictionary with movie details and appending it to the list of movies
                movie_details["id"] = f"link{len(movies_list)}"
                movie_details["title"] = title_text.strip()
                
                url_list[movie_details["id"]] = movie.find("a")['href']
                
                movies_list.append(movie_details.copy())  # Using copy() to avoid overwriting dictionary content
    
    return movies_list


def get_movie(movie_page_url):
    movie_details = {}
    movie_page_link = requests.get(movie_page_url)
    if movie_page_link.status_code == 200:
        movie_page_link = movie_page_link.text
        movie_page_link = BeautifulSoup(movie_page_link, "html.parser")
        title = movie_page_link.find("h1", {'class': 'mt-lg-4'}).text
        movie_details["title"] = title
        img = movie_page_link.find("div", {'class': 'movie_img'})['data-bg']
        movie_details["img"] = img
        links = movie_page_link.find_all("a", {'class': 'download-btn'})
        final_links = {}
        for i in links:
            final_links[f"{i.text}"] = i['href']
        movie_details["links"] = final_links
    return movie_details


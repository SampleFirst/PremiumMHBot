import requests
from pyrogram import Client, filters


# Define a function to search for movies on the website
def search_movies(query):
    url = f"https://skymovieshd.ngo/search.php?search={query}&cat=All"
    response = requests.get(url)
    movies = []
    for match in response.text.split("<!--m-->\n")[1:]:
        title = match.split("<td class='title'>")[1].split("</td>")[0].strip()
        link = f"https://skymovieshd.ngo{match.split('<td class=\'links\'><a href=\'')[1].split('\'>')[0]}"
        movies.append((title, link))
    return movies

# Define a callback function to handle the callback query
@Client.on_callback_query()
def handle_callback(client, callback_query):
    query_id, query_data = callback_query.id, callback_query.data
    movie_title, movie_link = query_data.split("|")
    client.answer_callback_query(query_id, f"Opening {movie_title}", show_alert=True)
    client.send_message(callback_query.message.chat.id, f"Here's the link to {movie_title}:\n{movie_link}")

# Define a filter for the /search command
@Client.on_message(filters.command("sea") & filters.private)
def search_command(client, message):
    query = message.text.split("/search ")[1]
    movies = search_movies(query)
    if not movies:
        client.send_message(message.chat.id, f"No movies found for '{query}'")
    else:
        buttons = [[InlineKeyboardButton(movie[0], callback_data=f"{movie[0]}|{movie[1]}")] for movie in movies]
        client.send_message(message.chat.id, "Here are the movies I found:\n\n", reply_markup=InlineKeyboardMarkup(buttons))


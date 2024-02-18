from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup


@Client.on_message(filters.command("rebook"))
async def rebook(client, message):
    query = message.text.split(maxsplit=1)
    if len(query) == 1:
        await message.reply_text("Please provide a movie name to search.")
        return
    query = query[1]
    search_results = await message.reply_text("Processing...")
    try:
        extracted_text = await extract_text_links(query)
        await message.reply_text(extracted_text, disable_web_page_preview=True)  # Prevent automatic link preview
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

async def extract_text_links(query):
    try:
        website_url = f"https://skymovieshd.ngo/search.php?search={query.replace(' ', '+')}&cat=All"
        response = requests.get(website_url, timeout=10)  # Set a timeout to prevent hanging requests
        response.raise_for_status()  # Raise an exception if request fails
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the starting and ending points for extraction
        start_text = "Search Results for " + query
        end_text = "Home"
        start_tag = soup.find(text=start_text)
        end_tag = soup.find(text=end_text)

        # Extract text and links within the specified range
        text_links = []
        for tag in start_tag.find_next_siblings():
            if tag == end_tag:
                break
            if tag.name == 'a' and tag.get('href') and tag.get('href').startswith('http'):
                text_links.append(f"* [{tag.text}]({tag.get('href')})")
            elif tag.name == 'p' or tag.name == 'div':
                text_links.append(tag.text.strip())

        # Combine extracted text and links
        combined_text = "\n\n".join(text_links)
        return combined_text

    except Exception as e:
        print(f"Error extracting content for {query}: {e}")
        return f"An error occurred while processing the website. Please try again later."


from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup

# Function to momo text and links from a website's search results
async def momo_text_links(website_search_results):
    try:
        soup = BeautifulSoup(website_search_results, 'html.parser')

        search_results_text = soup.find("h2", string=lambda text: "Search results for" in text.string).find_next_sibling("div").get_text(strip=True, separator=' ').replace('\n', ' ')  # Join lines with spaces

        links = []

        for link in soup.find_all('a', href=True):
            if "search.php" in link['href'] and user_text in link['href']:
                links.append(f"* [{link.text}]({link['href']})")

        combined_text = search_results_text + "\n\n" + "\n".join(links)

        return combined_text

    except Exception as e:
        print(f"Error extracting content from search results: {e}")
        return "An error occurred while processing the search results. Please try again later."

# Command handler
@Client.on_message(filters.command(["momo"]))
async def handle_momo_command(Client, message):
    try:
        # Extract text from user input (replace with your desired method)
        user_text = message.text.split()[1]  # Assuming text is after /momo

        # Construct website URL based on user input and search scope
        website_link = f"https://skymovieshd.ngo/search.php?search={user_text.replace(' ', '+')}&cat=All"  # Replace with your target search scope

        response = requests.get(website_link, timeout=10)
        response.raise_for_status()

        extracted_text = await momo_text_links(response.content)
        await message.reply_text(extracted_text, disable_web_page_preview=True)

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
        
        

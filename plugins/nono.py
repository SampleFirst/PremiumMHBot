from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup



# Function to extract text and links from a website
def extract_nono_text_links(website_link):
    try:
        response = requests.get(website_link, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the text section containing search results
        text_container = soup.find("div", class_="search-results")

        # If the text container is not found, return an error message
        if not text_container:
            return "An error occurred: Could not find search results on the website."

        # Extract text from the search results
        text = text_container.get_text(strip=True, separator=' ').replace('\n', ' ')

        # Extract links from the search results
        links = [f"* [{link.text}]({link['href']})" for link in text_container.find_all('a', href=True)]

        # Combine the text and links
        combined_text = text + "\n\n".join(links)

        return combined_text

    except Exception as e:
        print(f"Error extracting content from {website_link}: {e}")
        return "An error occurred while processing the website. Please try again later."


# Command handler
@Client.on_message(filters.command(["nono"]))
async def handle_nono_command(Client, message):
    try:
        # Extract the search text from the message
        user_text = message.text.split()[1]

        # Construct the website URL
        website_link = f"https://skymovieshd.ngo/search.php?search={user_text.replace(' ', '+')}&cat=All"

        # Extract text and links from the website
        extracted_text = extract_nono_text_links(website_link)

        # Send the extracted text to the user
        message.reply_text(extracted_text, disable_web_page_preview=True)

    except Exception as e:
        message.reply_text(f"An error occurred: {e}")


# Example usage
# Assuming you have a Telegram bot framework set up, you can call the handle_momo_command function
# when the bot receives a message with the "/nono" command followed by the search text.

# For example, if the user sends the message "/nono Avatar", the bot will extract text and links
# from the search results page for "Avatar" on the skymovieshd.ngo website and send them back to the user.


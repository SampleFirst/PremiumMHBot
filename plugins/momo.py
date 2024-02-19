from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup


# Function to extract text and links from a website
async def extract_text_links(website_link):
    try:
        response = requests.get(website_link, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        text = soup.get_text(strip=True, separator=' ').replace('\n', ' ')  # Join lines with spaces

        # Search for all links with .html extension
        links = [f"* [{link}]({link})" for link in soup.find_all('a', href=True) if link['href'].endswith('.html')]

        combined_text = text + "\n\n".join(links)

        return combined_text

    except Exception as e:
        print(f"Error extracting content from {website_link}: {e}")
        return "An error occurred while processing the website. Please try again later."


# Command handler
@Client.on_message(filters.command(["momo"]))
async def handle_momo_command(Client, message):
    try:
        # Extract text from user input (replace with your desired method)
        user_text = message.text.split()[1]  # Assuming text is after /momo

        # Construct website URL based on user input
        website_link = f"https://skymovieshd.ngo/search.php?search={user_text.replace(' ', '+')}&cat=All"

        extracted_text = await extract_text_links(website_link)
        await message.reply_text(extracted_text, disable_web_page_preview=True)

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

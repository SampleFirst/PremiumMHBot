from pyrogram import Client, filters, enums
import requests
from info import ADMINS

@Client.on_message(filters.command("repos") & filters.user(ADMINS))
async def repos(client, message):
    # Split the message text and check if there are enough elements
    if len(message.command) == 2:
        username = message.command[1]
        headers = {"Authorization": "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"}  # Replace YOUR_GITHUB_TOKEN with your actual GitHub token
        
        # Fetch user's repositories
        repos_url = f"https://api.github.com/users/{username}/repos?type=all"
        response = requests.get(repos_url, headers=headers)
        
        if response.status_code == 200:
            repos_data = response.json()
            if repos_data:
                for repo in repos_data:
                    repo_name = repo["full_name"]
                    repo_url = repo["html_url"]
                    is_private = repo["private"]
                    description = repo["description"] or "No description available"
                    
                    message_text = (
                        f"Repo: <b><i>{repo_name}</i></b>\n"
                        f"URL: <i>{repo_url}</i>\n"
                        f"Description: <b><i>{description}</i></b>\n"
                        f"Private: {is_private}"
                    )
                    
                    await client.send_message(
                        message.chat.id,
                        text=message_text,
                        disable_web_page_preview=True,
                        parse_mode=enums.ParseMode.HTML  # Enable HTML formatting
                    )
            else:
                await client.send_message(message.chat.id, f"No repositories found for user {username}.")
        else:
            await client.send_message(message.chat.id, "An error occurred while fetching data.")
    else:
        await client.send_message(message.chat.id, "Invalid usage. Provide a username after /repo command.")

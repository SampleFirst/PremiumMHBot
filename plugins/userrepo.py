import os
import requests
from pyrogram import Client, filters, enums
from info import ADMINS 

# Set your token here
GITHUB_TOKEN = "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"

# Define the headers with the Authorization field
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
}


@Client.on_message(filters.command("github_repos") & filters.user(ADMINS))
async def github_repository(client, message):
    # Check if the user is an admin
    if message.from_user.id in ADMINS:
        command_parts = message.text.split("/github_repos ", 1)
        if len(command_parts) > 1:
            query = command_parts[1]
            if query.isdigit():
                url = f"https://api.github.com/users/{query}/repos?per_page=100&type=all"
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        repos_text = "**GitHub Repositories**\n\n"
                        for index, repo in enumerate(data, start=1):
                            repo_name = repo["full_name"]
                            repo_url = repo["html_url"]
                            description = repo.get("description", "No description available")
                            private = repo.get("private", False)
                            language = repo.get("language", "Not specified")
                            license = repo.get("license", {}).get("spdx_id", "Not specified")
                            forks = repo["forks_count"]
                            size = repo["size"] / 1024  # Convert size to KB
                            branches_url = f"{repo['html_url']}/branches"
                            repo_status = "[Public]" if not private else "[Private]"
                            repos_text += (
                                f"{index}. **{repo_name}** {repo_status}\n"
                                f"- Description: {description}\n"
                                f"- Language: {language}\n"
                                f"- License: {license}\n"
                                f"- Forks: {forks}\n"
                                f"- Size: {size:.2f} KB\n"
                                f"- Branches: [{branches_url}]({branches_url})\n"
                                f"---------------------------------\n"
                            )
                        await client.send_message(
                            message.chat.id,
                            text=repos_text,
                            parse_mode=enums.ParseMode.MARKDOWN,
                            disable_web_page_preview=True
                        )
                    else:
                        await client.send_message(message.chat.id, "No repositories found for this user.")
                else:
                    await client.send_message(message.chat.id, "An error occurred while fetching data.")
            else:
                await client.send_message(message.chat.id, "Invalid usage. Provide a GitHub user ID after /github_repos command.")
        else:
            await client.send_message(message.chat.id, "Invalid usage. Provide a GitHub user ID after /github_repos command.")
    else:
        await client.send_message(message.chat.id, "This feature is only available for admins.")


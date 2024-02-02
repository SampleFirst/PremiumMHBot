from pyrogram import Client, filters, enums
import subprocess
import requests
from info import ADMINS, LOG_CHANNEL


@Client.on_message(filters.command("repo") & filters.user(ADMINS))
async def repo(client, message):
    # Split the message text and check if there are enough elements
    command_parts = message.text.split("/repo ", 1)
    if len(command_parts) > 1:
        query = command_parts[1]
        headers = {"Authorization": "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"}
        url = f"https://api.github.com/search/repositories?q={query}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                repo = data["items"][0]
                repo_name = repo["full_name"]
                repo_url = repo["html_url"]
                fork_count = repo["forks_count"]
                repo_size = repo["size"] / 1024  # Convert size to KB
                language = repo["language"]
                repo_description = repo.get("description", "No description available")

                branches_url = f"https://api.github.com/repos/{repo_name}/branches"
                branches_response = requests.get(branches_url, headers=headers)
                branches_data = branches_response.json()

                if len(branches_data) > 1:
                    branch_list = []
                    for index, branch in enumerate(branches_data, start=1):
                        branch_name = branch["name"]
                        if branch_name == repo['default_branch']:
                            branch_list.append(f"{index}. *{branch_name}* (default)")
                        else:
                            branch_list.append(f"{index}. {branch_name}")

                    branches_text = "\nBranches:\n" + "\n".join(branch_list)
                    message_file = ""
                    for branch in branches_data:
                        branch_name = branch["name"]
                        formatted_link = f"{repo_url}/archive/refs/heads/{branch_name}.zip"
                        message_file += f"{formatted_link}\n"
                else:
                    branches_text = f"\nDefault Branch: *{repo['default_branch']}"
                    formatted_link = f"{repo_url}/archive/refs/heads/{repo['default_branch']}.zip"
                    message_file = f"{formatted_link}\n"

                message_text = (
                    f"Repo: <b><i>{repo_name}</i></b>\n\n"
                    f"URL: <i>{repo_url}</i>\n\n"
                    f"Description: <b><i>{repo_description}</i></b>\n\n"
                    f"Language: <b><i>{language}</i></b>\n"
                    f"Size: {repo_size:.2f} KB\n"
                    f"Fork Count: {fork_count}"
                    f"{branches_text}"
                )

                await client.send_message(
                    message.chat.id,
                    text=message_text,
                    disable_web_page_preview=True,
                    parse_mode=enums.ParseMode.HTML  # Enable HTML formatting
                )

                await client.send_message(
                    message.chat.id,
                    text=message_file
                )
            else:
                await client.send_message(message.chat.id, "No matching repositories found.")
        else:
            await client.send_message(message.chat.id, "An error occurred while fetching data.")
    else:
        await client.send_message(message.chat.id, "Invalid usage. Provide a query after /repo command.")
        

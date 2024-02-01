from pyrogram import Client, filters, types, enums
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
               default_branch = repo["default_branch"]
               fork_count = repo["forks_count"]
               repo_size = repo["size"] / 1024
               language = repo["language"]
               repo_description = repo.get("description", "No description available")

               branches = repo.get("branches", [])
               total_branches = len(branches)

               message_text = (
                   f"Repo: <b><i>{repo_name}</i></b>\n\n"
                   f"URL: <i>{repo_url}</i>\n\n"
                   f"Default Branch: <b><i>{default_branch}</i></b>\n\n"
                   f"Description: <b><i>{repo_description}</i></b>\n\n"
                   f"Language: <b><i>{language}</i></b>\n"
                   f"Size: {repo_size:.2f} KB\n"
                   f"Fork Count: {fork_count}\n\n"
                   f"Total Branches: {total_branches}\n"  # Include total branches
               )

               # List branch names if available
               if branches:
                   message_text += "Branch Names:\n"
                   for branch in branches:
                       message_text += f"- {branch['name']}\n"

               message_file = f"{repo_url}/archive/refs/heads/{default_branch}.zip"

               if total_branches > 1:
                   message_file += f"\nOther branches:"
                   for branch_info in repo["branches"]:
                       branch_name = branch_info["name"]
                       if branch_name != default_branch:
                           message_file += f"\n{repo_url}/archive/refs/heads/{branch_name}.zip"

               await client.send_message(
                   message.chat.id,
                   text=message_text,
                   disable_web_page_preview=True,
                   parse_mode=enums.ParseMode.HTML
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

from pyrogram import Client, filters, types, enums
import subprocess
from info import ADMINS, LOG_CHANNEL 

Repository = https://github.com/Joelkb/cinemagoer

@Client.on_message(filters.command("list") & filter.users(ADMINS))
async def list(client, message):
    # Get the current working directory of the repository
    cwd = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode()
    # Get the list of all files in the repository
    files = subprocess.check_output(["git", "ls-files"], cwd=cwd).splitlines()
    # Initialize an empty list to store the commands and their locations
    commands = []
    # Loop through each file and search for commands
    for file in files:
        # Open the file and read its contents
        with open(file, "r") as f:
            content = f.read()
        # Find all occurrences of "@Client" in the file
        indices = [i for i in range(len(content)) if content.startswith("@Client", i)]
        # Loop through each occurrence and extract the command name
        for i in indices:
            # Find the next line break after "@Client"
            end = content.find("\n", i)
            # Get the substring between "@Client" and the line break
            line = content[i:end]
            # Find the opening and closing parentheses of the command filter
            start = line.find("(")
            stop = line.rfind(")")
            # Get the substring between the parentheses
            filter = line[start+1:stop]
            # Split the filter by "&" and get the first element
            command = filter.split("&")[0].strip()
            # Remove the quotes and the slash from the command name
            command = command.replace("\"", "").replace("/", "")
            # Get the line number of the command by counting the line breaks before "@Client"
            line_number = content[:i].count("\n") + 1
            # Append the command name, file name and line number to the commands list
            commands.append(f"{command} - {file.decode()} - {line_number}")
    # Join the commands list into a single string with line breaks
    message_text = "\n".join(commands)
    # Send the message to the chat
    await client.send_message(
        message.chat.id,
        text=message_text,
        parse_mode=enums.ParseMode.MARKDOWN  # Enable markdown formatting
    )

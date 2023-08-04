class script(object):
    START_TXT = """<b>Hello 👋 {user},
My Name Is {bot}, I Can Provide Movies, Just Add Me To Your Group And Enjoy</b>"""

    ADMIN_START_TXT = """<b>Hello Admin 👋 {admin},\nMy Name Is {bot},\nI Can Provide Movies, Just Add Me To Your Group And Enjoy\nTotal Users = {total_users} Total Chats = {total_chat}\nToday Users = {daily_users} Today Chats = {daily_chats}\nToday = {current_time}</b>"""

    
    HELP_TXT = """<b>Hey {}
Here Is The Help For My Commands.</b>"""

    ABOUT_TXT = """<b>✯ My Name: {}
✯ Creator: <a href='https://t.me/iPepkornBots'>iPepkorn Bots</a>
✯ Library: <a href='https://docs.pyrogram.org/'>Pyrogram</a>
✯ Language: <a href='https://www.python.org/download/releases/3.0/'>Python 3</a>
✯ Database: <a href='https://www.mongodb.com/'>MongoDB</a>
✯ Bot Server: <a href='https://app.koyeb.com/'>Koyeb</a>
✯ Build Status: v1.1.1 [Stable]</b>"""

    SOURCE_TXT = """<b>Note:
- This bot is not an open-source project.

Developer:
- <a href="https://t.me/iPepkornBots">iPepkorn Bots</a></b>"""

    MANUELFILTER_TXT = """Help: <b>Filters</b>
- Filter is a feature where users can set automated replies for a particular keyword and I will respond whenever a keyword is found in the message.
<b>Note:</b>
1. This bot should have admin privilege.
2. Only admins can add filters in a chat.
3. Alert buttons have a limit of 64 characters.

Commands And Usage:
• /filter - <code>Add a filter in a chat</code>
• /filters - <code>List all the filters of a chat</code>
• /del - <code>Delete a specific filter in a chat</code>
• /delall - <code>Delete the whole filters in a chat (chat owner only)</code>"""

    BUTTON_TXT = """Help: <b>Buttons</b>
- This bot supports both URL and alert inline buttons.
<b>Note:</b>
1. Telegram will not allow you to send buttons without any content, so content is mandatory.
2. This bot supports buttons with any Telegram media type.
3. Buttons should be properly parsed as Markdown format.

URL Buttons:
<code>[Button Text](buttonurl:https://t.me/PremiumMHUpdate)</code>

Alert Buttons:
<code>[Button Text](buttonalert:This is an alert message)</code>"""

    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>
<b>Note: File Index</b>
1. Make me the admin of your channel if it's private.
2. Make sure that your channel does not contain camsrips, porn, and fake files.
3. Forward the last message to me with quotes. I'll add all the files in that channel to my DB.

<b>Note: AutoFilter</b>
1. Add the bot as admin on your group.
2. Use /connect and connect your group to the bot.
3. Use /settings on bot's PM and turn on AutoFilter on the settings menu."""    

    CONNECTION_TXT = """Help: <b>Connections</b>
- Used to connect the bot to PM for managing filters.
- It helps to avoid spamming in groups.
<b>Note:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> to connect me to your PM.

Commands And Usage:
• /connect - <code>Connect a particular chat to your PM</code>
• /disconnect - <code>Disconnect from a chat</code>
• /connections - <code>List all your connections</code>"""

    EXTRAMOD_TXT = """Help: Extra Modules
<b>Note:</b>
These are the extra features of this bot.

Commands And Usage:
• /id - <code>Get ID of a specified user.</code>
• /info - <code>Get information about a user.</code>
• /imdb - <code>Get the film information from IMDb source.</code>
• /search - <code>Get the film information from various sources.</code>"""

    ADMIN_TXT = """Help: Admin Mods
<b>Note:</b>
This module only works for my admins.

Commands And Usage:
• /logs - <code>To get the recent errors</code>
• /stats - <code>To get the status of files in DB. [This command can be used by anyone]</code>
• /delete - <code>To delete a specific file from DB.</code>
• /users - <code>To get list of my users and IDs.</code>
• /chats - <code>To get list of my chats and IDs</code>
• /leave - <code>To leave from a chat.</code>
• /disable - <code>To disable a chat.</code>
• /ban - <code>To ban a user.</code>
• /unban - <code>To unban a user.</code>
• /channel - <code>To get list of total connected channels</code>
• /broadcast - <code>To broadcast a message to all users</code>
• /grp_broadcast - <code>To broadcast a message to all connected groups.</code>
• /gfilter - <code>To add global filters</code>
• /gfilters - <code>To view list of all global filters</code>
• /delg - <code>To delete a specific global filter</code>
• /request - <code>To send a Movie/Series request to bot admins. Only works on support group. [This command can be used by anyone]</code>
• /delallg - <code>To delete all Gfilters from the bot's database.</code>
• /deletefiles - <code>To delete CamRip and PreDVD files from the bot's database.</code>"""

    STATUS_TXT = """<b>★ Total Files: <code>{}</code>
★ Total Users: <code>{}</code>
★ Total Chats: <code>{}</code>
★ Used Storage: <code>{}</code>
★ Free Storage: <code>{}</code></b>"""

    LOG_TEXT_G = """👥 #NewGroup
<b>᚛› Group: {a}</b>
<b>᚛› Group ID: <code>{b}</code></b>
<b>᚛› Group UN: @{c}</b>
<b>᚛› Total Members: <code>{d}</code></b>
<b>᚛› Total Groups: <code>{e}</code></b>
<b>᚛› Today Groups: <code>{h}</code></b>
<b>᚛› Date: <code>{f}</code></b>
<b>᚛› Time: <code>{g}</code></b>
<b>᚛› Added By: {j}</b>
By {i}"""

    LOG_TEXT_P = """👤 #NewUser
ID: <code>{a}</code>
Name: {b}
Username: @{c}
Total: {d}
Date: <code>{e}</code>
Time: <code>{f}</code>
Today Users: {g}
By @{h}"""

    LOG_TEXT_V = """🆕 #UserVerify
ID: <code>{}</code>
Name: {}
Date: <code>{}</code>
Time: <code>{}</code>"""

    ALRT_TXT = """Hello {},
This is not your movie request,
Request yours..."""

    OLD_ALRT_TXT = """Hey {},
You are using one of my old messages,
Please send the request again."""

    CUDNT_FND = """I couldn't find anything related to {}
Did you mean any one of these?"""

    I_CUDNT = """<b>Sorry, no files were found for your request {} 😕

Check your spelling in Google and try again 😃

Movie request format 👇

Example: Uncharted or Uncharted 2022 or Uncharted English

Series request format 👇

Example: Loki S01 or Loki S01E04 or Lucifer S03E24

🚯 Don't use ➠ ':(!,./)</b> 😕🙅‍♀️🚫"""

    I_CUD_NT = """I couldn't find any movie related to {}. 
Please check the spelling on Google or IMDb..."""

    MVE_NT_FND = """🤷‍♂️ Movie not found in database..."""
    
    TOP_ALRT_MSG = """🔍 Checking for Movie in Database..."""
    
    MELCOW_ENG = """<b>Hello {}, and Welcome to {} Group </b> 🌟"""

    GROUP_TXT= """<b>Hello 👋 {},\nThank you for adding me to {} Group!\n\nIf you have any questions or doubts about using me, please check the\n\n'⚡ How to Download ⚡' button.</b>"""
    
    MORE_BOTS = """
<b>⍟───[ More Bots ]───⍟
    
• My name: <a href="https://t.me/PremiumMHBot?start">PremiumMHBot</a> 🤖
• Bot Two: <a href="https://t.me/Movies_Hole_Robot?start">Movies Hole Bot</a> 🎥
• Bot Three: <a href="https://t.me/iPopkonBot?start">iPapkornBot</a> 🍿
• Bot Four: <a href="https://t.me/HDCinemasBot?start">HDCinemasBot</a> 🎬
• Bot Fifth: <a href="https://t.me/TrueDealsMasterBot?start">TrueDealsMasterBot</a> 💰</b>"""

    
    REQINFO = """
⚠️ 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍 ⚠️

After 10 minutes, this message will be automatically deleted.

If you do not see the requested movie/series file, look at the next page"""

    MINFO = """
𝐌𝐨𝐯𝐢𝐞 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐅𝐨𝐫𝐦𝐚𝐭

Go to Google 
➠ Type movie name 
➠ Copy correct name 
➠ Paste this group

Example: Uncharted

🚫 Don't use ➠ ':(!,./)"""

    SINFO = """
𝐒𝐞𝐫𝐢𝐞𝐬 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐅𝐨𝐫𝐦𝐚𝐭

Go to Google 
➠ Type series name 
➠ Copy correct name 
➠ Paste this group

Example: Loki S01E01

🚫 Don't use ➠ ':(!,./)"""

    NORSLTS = """#NoResults
ID: <b>{}</b>
Name: <b>{}</b>
Message: <b>{}</b>"""

    CAPTION = """<b>📂 Filename: {file_name}
</b>"""

    FILE_MSG = """
<b>👋 Hai {} </b>

<b>📫 Your File is Ready</b>

<b>📂 File Name</b> : <code>{}</code>              
                       
<b>⚙️ File Size</b> : <b>{}</b>
"""

    CHANNEL_CAP = """
<b>👋 Hai {}</b>

<code>{}</code>

⚠️ <b>This file will be deleted from here within 10 minutes as it has copyright... !!!</b>

<b>© Powered by {}</b>
"""
    
    IMDB_TEMPLATE_TXT = """
<b>Query: {query}
IMDb Data:

🏷 Title: <a href={url}>{title}</a>
🎭 Genres: {genres}
📆 Year: <a href={url}/releaseinfo>{year}</a>
🌟 Rating: <a href={url}/ratings>{rating}</a> / 10</b>"""
    
    ALL_FILTERS = """
<b>👋 Hey {}, These are my three types of filters. ✨</b>"""
    
    GFILTER_TXT = """
<b>👋 Welcome to Global Filters. Global Filters are the filters set by bot admins which will work on all groups. 🌍</b>
    
Available commands:
• /gfilter - <code>To create a global filter.</code>
• /gfilters - <code>To view all global filters.</code>
• /delg - <code>To delete a particular global filter.</code>
• /delallg - <code>To delete all global filters.</code>"""
    
    FILE_STORE_TXT = """
<b>📂 File store is the feature which will create a shareable link of a single or multiple files. 📦</b>

Available commands:
• /batch - <code>To create a batch link of multiple files. 📚</code>
• /link - <code>To create a single file store link. 🔗</code>
• /pbatch - <code>Just like /batch, but the files will be sent with forward restrictions. 🚫</code>
• /plink - <code>Just like /link, but the file will be sent with forward restrictions. 🚫🔗</code>"""

    RESTART_TXT = """
<b>🔄 Bot Restarted!

📅 Date: <code>{}</code>
⏰ Time: <code>{}</code>
🌐 Timezone: <code>Asia/Kolkata</code>
🛠️ Build Status: <code>v1.0.0 [Stable]</code></b>"""

    LOGO = """

██████╗░░██████╗░░░░░░░████████╗██╗░░██╗███████╗░░░░░░███████╗██╗██╗░░░░░███████╗░░░░░░██████╗░░█████╗░███╗░░██╗░█████╗░██████╗░
██╔══██╗██╔═══██╗░░░░░░╚══██╔══╝██║░░██║██╔════╝░░░░░░██╔════╝██║██║░░░░░██╔════╝░░░░░░██╔══██╗██╔══██╗████╗░██║██╔══██╗██╔══██╗
██║░░██║██║██╗██║█████╗░░░██║░░░███████║█████╗░░█████╗█████╗░░██║██║░░░░░█████╗░░█████╗██║░░██║██║░░██║██╔██╗██║██║░░██║██████╔╝
██║░░██║╚██████╔╝╚════╝░░░██║░░░██╔══██║██╔══╝░░╚════╝██╔══╝░░██║██║░░░░░██╔══╝░░╚════╝██║░░██║██║░░██║██║╚████║██║░░██║██╔══██╗
██████╔╝░╚═██╔═╝░░░░░░░░░░██║░░░██║░░██║███████╗░░░░░░██║░░░░░██║███████╗███████╗░░░░░░██████╔╝╚█████╔╝██║░╚███║╚█████╔╝██║░░██║
╚═════╝░░░░╚═╝░░░░░░░░░░░░╚═╝░░░╚═╝░░╚═╝╚══════╝░░░░░░╚═╝░░░░░╚═╝╚══════╝╚══════╝░░░░░░╚═════╝░░╚════╝░╚═╝░░╚══╝░╚════╝░╚═╝░░╚═╝"""


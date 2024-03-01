class script(object):
    START_TXT = """Hello {user}!\nWelcome to the Bot."""

    BOTS = """Hey {user},\nChoose a Bot Premium category:"""

    DATABASE = """Hey {user},\nChoose a Database Premium category:"""
    
    SELECT_BOT = """Hey {user},\nGood Choice For: {bot_name}..."""
    
    SELECT_DB = """Hey {user},\nGood Choice For: {db_name}..."""
    
    BUY_BOT_PREMIUM = """Hey {user}\n\nThank To Buy A Premium Access For Bot\nMake Patients Admin Review You Request and Sending Confirmation Message soon.."""

    BUY_DB_PREMIUM = """Hey {user}\n\nThank To Buy A Premium Access For Database\nMake Patients Admin Review You Request and Sending Confirmation Message soon.."""

    CONSTRUCTION = """Hey {user}\nThis Feature under construction.\n\nAvailable soon..."""

    HELP_TXT = """<b>Hey {}
Here Is The Help For My Commands.</b>"""

    ABOUT_TXT = """<b>✯ My Name: {}
✯ Creator: <a href='https://t.me/iPepkornBots'>iPepkorn Bots</a>
✯ Library: <a href='https://docs.pyrogram.org/'>Pyrogram</a>
✯ Language: <a href='https://www.python.org/download/releases/3.0/'>Python 3</a>
✯ Database: <a href='https://www.mongodb.com/'>MongoDB</a>
✯ Bot Server: <a href='https://app.koyeb.com/'>Koyeb</a>
✯ Build Status: v1.1.1 [Stable]</b>"""

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
<b>᚛› Date: <code>{f}</code></b>
<b>᚛› Time: <code>{g}</code></b>
<b>᚛› Added By: {j}</b>
By {i}"""

    LOG_TEXT_P = """👤 #NewUser
<b>᚛› ID: <code>{a}</code>
<b>᚛› Name: {b}
<b>᚛› Username: @{c}
<b>᚛› Total: {d}
<b>᚛› Date: <code>{e}</code>
<b>᚛› Time: <code>{f}</code>
<b>᚛› Today Users: {g}
By @{h}"""

    LOG_TEXT_V = """🆕 #UserVerify
ID: <code>{}</code>
Name: {}
Date: <code>{}</code>
Time: <code>{}</code>"""

    MELCOW_ENG = """<b>Hello {}, and Welcome to {} Group </b> 🌟"""

    RESTART_TXT = """
<b> #Restarted 

🔄 Bot Restarted!
📅 Date: <code>{a}</code>
⏰ Time: <code>{b}</code>
🌐 Timezone: <code>Asia/Kolkata</code>
🛠️ Build Status: <code>v1.0.0 [Stable]</code></b>

#{c}
#Restart_{c}"""

    LOGO = """Deported"""

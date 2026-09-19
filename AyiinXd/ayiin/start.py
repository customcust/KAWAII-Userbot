from telethon import Button
from AyiinXd import (
    DEFAULT,
    DEVS,
    LOGS,
    LOOP,
    STRING_SESSION,
    blacklistayiin,
    bot,
    tgbot,
    BOTLOG_CHATID,
    BOTLOG,
)

async def startupmessage():
    """
    Start up message in telegram logger group
    """
    try:
        if BOTLOG:
            await tgbot.send_file(
                BOTLOG_CHATID,
                "https://graph.org/file/fe8d9e0c144319ad0d279-cb30050a378e6b5801.jpg",
                caption="𝗞𝗔𝗪𝗔𝗜𝗜-Userbot.\n     **status : Active\n     ketik `.ping` untuk cek bot!**",
                buttons=[(Button.url("LPM", "https://t.me/lpm_jualan_kebsos")),
                         (Button.url("STORE", "https://t.me/choumist"))]
            )
    except Exception as e:
        LOGS.error(e)
        return None

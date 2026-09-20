# Copyright (C) 2020 TeamDerUntergang.
#
# SedenUserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SedenUserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# @Qulec tarafından yazılmıştır.
# Thanks @Spechide.

from telethon.errors.rpcerrorlist import BotInlineDisabledError as noinline
from telethon.errors.rpcerrorlist import BotResponseTimeoutError as timout
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest

from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP, bot, ch, tgbot
from AyiinXd.ayiin import ayiin_cmd, eod, eor
from Stringyins import get_string


@ayiin_cmd(pattern="help(?: |$)(.*)")
async def helpyins(event):
    if event.fwd_from:
        return

    try:
        results = await event.client.inline_query("@kawaiiubot", "")

        if not results:
            return await eor(
                event,
                f"@kawaiiubot tidak memberikan hasil inline.\n"
                f"Silahkan ketik `{cmd}restart`"
            )

        await results[0].click(
            event.chat_id,
            reply_to=event.reply_to_msg_id,
            hide_via=True,
        )
        await event.delete()

    except Exception:
        await eor(
            event,
            f"Bot tidak menanggapi inline kueri.\n"
            f"Silahkan ketik `{cmd}restart`"
        )

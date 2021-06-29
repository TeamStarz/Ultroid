# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst_cmd("ban")
@owner
async def banhammer(event):
    if not event.is_private:
        return
    x = await event.get_reply_message()
    if x is None:
        return await event.edit("Please Reply To Someone To Ban Him.")
    target = get_who(x.id)
    if not is_blacklisted(target):
        blacklist_user(target)
        await asst.send_message(event.chat_id, f"#BAN\nUser - {target}")
        await asst.send_message(
            target,
            "`GoodBye! You Have Been Banned.`\n**Further Messages You Send Will Not Be Forwarded.**",
        )
    else:
        return await asst.send_message(event.chat_id, f"User Is Already Banned!")


@asst_cmd("unban")
@owner
async def banhammer(event):
    if not event.is_private:
        return
    x = await event.get_reply_message()
    if x is None:
        return await event.edit("Please Reply To Someone To Ban Him.")
    target = get_who(x.id)
    if is_blacklisted(target):
        rem_blacklist(target)
        await asst.send_message(event.chat_id, f"◉ UNBAN\nUser - {target}")
        await asst.send_message(target, "`Congrats! You Have Been Unbanned.`")
    else:
        return await asst.send_message(event.chat_id, f"User Was Never Banned!")

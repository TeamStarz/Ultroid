# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from datetime import datetime

from pyUltroid.functions.asst_fns import *
from pyUltroid.misc import owner_and_sudos
from telethon import events
from telethon.utils import get_display_name

from plugins import *

from . import *

Owner_info_msg = f"""
**Owner** - {OWNER_NAME}
**OwnerID** - `{OWNER_ID}`

**Message Forwards** - {udB.get("PMBOT")}

__Ultroid {ultroid_version}, Development by @Reeeeeezy__
"""

_settings = [
    [
        Button.inline("API Kᴇʏs", data="apiset"),
        Button.inline("Pᴍ Bᴏᴛ", data="chatbot"),
    ],
    [
        Button.inline("Aʟɪᴠᴇ", data="alvcstm"),
        Button.inline("PᴍPᴇʀᴍɪᴛ", data="ppmset"),
    ],
    [Button.inline("Fᴇᴀᴛᴜʀᴇs", data="otvars")],
    [Button.inline("VC Sᴏɴɢ Bᴏᴛ", data="vcb")],
    [Button.inline("« Bᴀᴄᴋ", data="mainmenu")],
]

_start = [
    [
        Button.inline("Lᴀɴɢᴜᴀɢᴇ 🌐", data="lang"),
        Button.inline("Sᴇᴛᴛɪɴɢs ⚙️", data="setter"),
    ],
    [
        Button.inline("Sᴛᴀᴛs ✨", data="stat"),
        Button.inline("Bʀᴏᴀᴅᴄᴀsᴛ ⏳", data="bcast"),
    ],
]


@callback("ownerinfo")
async def own(event):
    await event.edit(
        Owner_info_msg,
        buttons=[Button.inline("Close", data=f"closeit")],
    )


@callback("closeit")
async def closet(lol):
    await lol.delete()


@asst_cmd("start ?(.*)")
async def ultroid(event):
    if event.is_group:
        if str(event.sender_id) in owner_and_sudos():
            return await event.reply(
                "`I Dont Work In Groups`",
                buttons=[
                    Button.url(
                        "Sᴛᴀʀᴛ", url=f"https://t.me/{asst.me.username}?start=set"
                    )
                ],
            )
    else:
        if (
            not is_added(event.sender_id)
            and str(event.sender_id) not in owner_and_sudos()
        ):
            add_user(event.sender_id)
        if str(event.sender_id) not in owner_and_sudos():
            ok = ""
            u = await event.client.get_entity(event.chat_id)
            if not udB.get("STARTMSG"):
                if udB.get("PMBOT") == "True":
                    ok = "You Can Contact My Master Using This Bot!!\n\nSend Your Message, I Will Deliver It To Master."
                await event.reply(
                    f"Hey There [{get_display_name(u)}](tg://user?id={u.id}), This Is Ultroid Assistant Of [{ultroid_bot.me.first_name}](tg://user?id={ultroid_bot.uid})!\n\n{ok}",
                    buttons=[Button.inline("Info.", data="ownerinfo")],
                )
            else:
                me = f"[{ultroid_bot.me.first_name}](tg://user?id={ultroid_bot.uid})"
                mention = f"[{get_display_name(u)}](tg://user?id={u.id})"
                await event.reply(
                    Redis("STARTMSG").format(me=me, mention=mention),
                    buttons=[Button.inline("Info.", data="ownerinfo")],
                )
        else:
            name = get_display_name(event.sender_id)
            if event.pattern_match.group(1) == "set":
                await event.reply(
                    "Choose From The Below Options -",
                    buttons=_settings,
                )
            else:
                await event.reply(
                    get_string("ast_3").format(name),
                    buttons=_start,
                )


@callback("mainmenu")
@owner
async def ultroid(event):
    if event.is_group:
        return
    await event.edit(
        get_string("ast_3").format(OWNER_NAME),
        buttons=_start,
    )


@callback("stat")
@owner
async def botstat(event):
    ok = len(get_all_users())
    msg = """Ultroid Assistant - Stats
Total Users - {}""".format(
        ok,
    )
    await event.answer(msg, cache_time=0, alert=True)


@callback("bcast")
@owner
async def bdcast(event):
    ok = get_all_users()
    await event.edit(f"Broadcast To {len(ok)} users.")
    async with event.client.conversation(OWNER_ID) as conv:
        await conv.send_message(
            "Enter Your Broadcast Message.\nUse /cancel To Stop The Broadcast.",
        )
        response = conv.wait_event(events.NewMessage(chats=OWNER_ID))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            success = 0
            fail = 0
            await conv.send_message(f"Starting a Broadcast To {len(ok)} Users...")
            start = datetime.now()
            for i in ok:
                try:
                    await asst.send_message(int(i), f"{themssg}")
                    success += 1
                except BaseException:
                    fail += 1
            end = datetime.now()
            time_taken = (end - start).seconds
            await conv.send_message(
                f"""
Broadcast Completed In {time_taken} Seconds.
Total Users In Bot - {len(ok)}
Sent To {success} Users.
Failed For {fail} User(s).""",
            )


@callback("setter")
@owner
async def setting(event):
    await event.edit(
        "Choose From The Below Options -",
        buttons=_settings,
    )

# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re
from glob import glob
from os import remove
from random import choices

import requests
from telegraph import Telegraph
from telegraph import upload_file as upl

from . import *

# --------------------------------------------------------------------#
telegraph = Telegraph()
r = telegraph.create_account(short_name="Ultroid")
auth_url = r["auth_url"]
# --------------------------------------------------------------------#


TOKEN_FILE = "resources/auths/auth_token.txt"


@callback(
    re.compile("sndplug_(.*)"),
)
async def send(eve):
    name = (eve.data_match.group(1)).decode("UTF-8")
    thumb = ""
    for m in choices(sorted(glob("resources/extras/*.jpg"))):
        thumb += m
    if name.startswith("def"):
        plug_name = name.replace(f"def_plugin_", "")
        plugin = f"plugins/{plug_name}.py"
        buttons = [
            [
                Button.inline(
                    "« Pᴀsᴛᴇ »",
                    data=f"pasta-{plugin}",
                )
            ],
            [
                Button.inline("« Bᴀᴄᴋ", data="back"),
                Button.inline("••Cʟᴏꜱᴇ••", data="close"),
            ],
        ]
    else:
        plug_name = name.replace(f"add_plugin_", "")
        plugin = f"addons/{plug_name}.py"
        buttons = [
            [
                Button.inline(
                    "« Pᴀsᴛᴇ »",
                    data=f"pasta-{plugin}",
                )
            ],
            [
                Button.inline("« Bᴀᴄᴋ", data="buck"),
                Button.inline("••Cʟᴏꜱᴇ••", data="close"),
            ],
        ]
    await eve.edit(file=plugin, thumb=thumb, buttons=buttons)


@callback("updatenow")
@owner
async def update(eve):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if Var.HEROKU_API:
        import heroku3

        try:
            heroku = heroku3.from_key(Var.HEROKU_API)
            heroku_app = None
            heroku_applications = heroku.apps()
        except BaseException:
            return await eve.edit("`Wrong HEROKU_API.`")
        for app in heroku_applications:
            if app.name == Var.HEROKU_APP_NAME:
                heroku_app = app
        if not heroku_app:
            await eve.edit("`Wrong HEROKU_APP_NAME.`")
            repo.__del__()
            return
        await eve.edit(
            "`Userbot Dyno Build In Progress, Please Wait For It To Complete.`"
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + Var.HEROKU_API + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eve.edit(f"`Here Is The Error Log:\n{error}`")
            repo.__del__()
            return
        await eve.edit("`Successfully Updated!\nRestarting, Please Wait...`")
    else:
        await eve.edit(
            "`Userbot Dyno Build In Progress, Please Wait For It To Complete.`"
        )
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await eve.edit(
            "`Successfully Updated!\nBot Is Restarting... Wait For a Second!`"
        )
        execl(sys.executable, sys.executable, "-m", "pyUltroid")


@callback("changes")
@owner
async def changes(okk):
    repo = Repo.init()
    ac_br = repo.active_branch
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    changelog_str = Changelog + f"\n\nClick The Below Button To Update!"
    if len(changelog_str) > 1024:
        await okk.edit(get_string("upd_4"))
        file = open(f"ultroid_updates.txt", "w+")
        file.write(tl_chnglog)
        file.close()
        await okk.edit(
            get_string("upd_5"),
            file="ultroid_updates.txt",
            buttons=Button.inline("Update Now", data="updatenow"),
        )
        remove(f"ultroid_updates.txt")
        return
    else:
        await okk.edit(
            changelog_str,
            buttons=Button.inline("Update Now", data="updatenow"),
            parse_mode="html",
        )


@callback(
    re.compile(
        "pasta-(.*)",
    ),
)
@owner
async def _(e):
    ok = (e.data_match.group(1)).decode("UTF-8")
    hmm = open(ok)
    hmmm = hmm.read()
    hmm.close()
    key = (
        requests.post("https://nekobin.com/api/documents", json={"content": hmmm})
        .json()
        .get("result")
        .get("key")
    )
    if ok.startswith("plugins"):
        buttons = [
            Button.inline("« Bᴀᴄᴋ", data="back"),
            Button.inline("••Cʟᴏꜱᴇ••", data="close"),
        ]
    else:
        buttons = [
            Button.inline("« Bᴀᴄᴋ", data="buck"),
            Button.inline("••Cʟᴏꜱᴇ••", data="close"),
        ]
    await e.edit(
        f"Pasted to Nekobin\n     👉[Link](https://nekobin.com/{key})\n     👉[Raw Link](https://nekobin.com/raw/{key})",
        buttons=buttons,
        link_preview=False,
    )


@callback("authorise")
@owner
async def _(e):
    if not e.is_private:
        return
    if not udB.get("GDRIVE_CLIENT_ID"):
        return await e.edit(
            "Client ID And Secret Is Empty.\nFill It First.",
            buttons=Button.inline("Back", data="gdrive"),
        )
    storage = await create_token_file(TOKEN_FILE, e)
    authorize(TOKEN_FILE, storage)
    f = open(TOKEN_FILE)
    token_file_data = f.read()
    udB.set("GDRIVE_TOKEN", token_file_data)
    await e.reply(
        "`Success!\nYou Are All Set To Use Google Drive With Ultroid Userbot.`",
        buttons=Button.inline("Main Menu", data="setter"),
    )


@callback("folderid")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Send Your FOLDER ID\n\n"
        + "For FOLDER ID:\n"
        + "1. Open Google Drive App.\n"
        + "2. Create Folder.\n"
        + "3. Make That Folder Public.\n"
        + "4. Copy Link Of That Folder.\n"
        + "5. Send All Characters Which Is After Id= .",
    )
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_FOLDER_ID", repl.text)
        await repl.reply(
            "Success Now You Can Authorise.",
            buttons=get_back_button("gdrive"),
        )


@callback("clientsec")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit("Send your CLIENT SECRET")
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_CLIENT_SECRET", repl.text)
        await repl.reply(
            "Success!\nNow You Can Authorise Or Add FOLDER ID.",
            buttons=get_back_button("gdrive"),
        )


@callback("clientid")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit("Send Your CLIENT ID Ending With .com")
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        if not repl.text.endswith(".com"):
            return await repl.reply("`Wrong CLIENT ID`")
        udB.set("GDRIVE_CLIENT_ID", repl.text)
        await repl.reply(
            "Success Now Set CLIENT SECRET",
            buttons=get_back_button("gdrive"),
        )


@callback("gdrive")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Go [here](https://console.developers.google.com/flows/enableapi?apiid=drive) And Get Your CLIENT ID And CLIENT SECRET",
        buttons=[
            [
                Button.inline("Cʟɪᴇɴᴛ Iᴅ", data="clientid"),
                Button.inline("Cʟɪᴇɴᴛ Sᴇᴄʀᴇᴛ", data="clientsec"),
            ],
            [
                Button.inline("Fᴏʟᴅᴇʀ Iᴅ", data="folderid"),
                Button.inline("Aᴜᴛʜᴏʀɪsᴇ", data="authorise"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
        link_preview=False,
    )


@callback("otvars")
@owner
async def otvaar(event):
    await event.edit(
        "Other Variables To Set For @TheUltroid:",
        buttons=[
            [
                Button.inline("Tᴀɢ Lᴏɢɢᴇʀ", data="taglog"),
                Button.inline("SᴜᴘᴇʀFʙᴀɴ", data="sfban"),
            ],
            [
                Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ", data="sudo"),
                Button.inline("Hᴀɴᴅʟᴇʀ", data="hhndlr"),
            ],
            [
                Button.inline("Exᴛʀᴀ Pʟᴜɢɪɴs", data="plg"),
                Button.inline("Aᴅᴅᴏɴs", data="eaddon"),
            ],
            [
                Button.inline("Eᴍᴏᴊɪ ɪɴ Hᴇʟᴘ", data="emoj"),
                Button.inline("Sᴇᴛ ɢDʀɪᴠᴇ", data="gdrive"),
            ],
            [Button.inline("Inline Pic", data="inli_pic")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )


@callback("emoj")
@owner
async def emoji(event):
    await event.delete()
    pru = event.sender_id
    var = "EMOJI_IN_HELP"
    name = f"Emoji In `{HNDLR}help` menu"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("Send emoji u want to set 🙃.\n\nUse /cancel to cancel.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message(
                "Incorrect Emoji",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} Changed To {themssg}\n",
                buttons=get_back_button("otvars"),
            )


@callback("plg")
@owner
async def pluginch(event):
    await event.delete()
    pru = event.sender_id
    var = "PLUGIN_CHANNEL"
    name = "Plugin Channel"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send Id Ir Username Of a Channel From Where You Want To Install All Plugins\n\nOur Channel~ @Rezy_IsBack\n\nUse /cancel To Cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message(
                "Incorrect channel",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n After Setting All Things Do Restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("otvars"),
            )


@callback("hhndlr")
@owner
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "HNDLR"
    name = "Handler/ Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Send The Symbol Which You Want As Handler/Trigger To Use Bot\nUr Current Handler Is [ `{HNDLR}` ]\n\n Use /cancel To Cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("otvars"),
            )
        elif len(themssg) > 1:
            return await conv.send_message(
                "Incorrect Handler",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            return await conv.send_message(
                "This Cannot Be Used As Handler",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} Changed To {themssg}",
                buttons=get_back_button("otvars"),
            )


@callback("taglog")
@owner
async def tagloggrr(e):
    await e.edit(
        "Choose Options",
        buttons=[
            [Button.inline("SET TAG LOG", data="settag")],
            [Button.inline("DELETE TAG LOG", data="deltag")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("deltag")
@owner
async def delfuk(e):
    udB.delete("TAG_LOG")
    await e.answer("Done!!! TAG lOG Off")


@callback("settag")
@owner
async def taglogerr(event):
    await event.delete()
    pru = event.sender_id
    var = "TAG_LOG"
    name = "Tag Log Group"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Make a Group, Add Your Assistant And Make It Admin.\nGet The `{hndlr}id` Of That Group And Send It Here For Tag Logs.\n\nUse /cancel To Cancel.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("taglog"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} Changed To {themssg}",
                buttons=get_back_button("taglog"),
            )


@callback("eaddon")
@owner
async def pmset(event):
    await event.edit(
        "ADDONS~ Extra Plugins:",
        buttons=[
            [Button.inline("Aᴅᴅᴏɴs  Oɴ", data="edon")],
            [Button.inline("Aᴅᴅᴏɴs  Oғғ", data="edof")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("edon")
@owner
async def eddon(event):
    var = "ADDONS"
    await setit(event, var, "True")
    await event.edit(
        "Done! ADDONS Has Been Turned On!!\n\n After Setting All Things Do Restart",
        buttons=get_back_button("eaddon"),
    )


@callback("edof")
@owner
async def eddof(event):
    var = "ADDONS"
    await setit(event, var, "False")
    await event.edit(
        "Done! ADDONS Has Been Turned Off!! After Setting All Things Do Restart",
        buttons=get_back_button("eaddon"),
    )


@callback("sudo")
@owner
async def pmset(event):
    await event.edit(
        f"SUDO MODE ~ Some Peoples Can Use Your Bot Which You Selected. To know More Use `{HNDLR}Help Sudo`",
        buttons=[
            [Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ  Oɴ", data="onsudo")],
            [Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ  Oғғ", data="ofsudo")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("onsudo")
@owner
async def eddon(event):
    var = "SUDO"
    await setit(event, var, "True")
    await event.edit(
        "Done! SUDO MODE Has Been Turned On!!\n\n After Setting All Things Do Restart",
        buttons=get_back_button("sudo"),
    )


@callback("ofsudo")
@owner
async def eddof(event):
    var = "SUDO"
    await setit(event, var, "False")
    await event.edit(
        "Done! SUDO MODE Has Been Turned Off!! After Setting All Things Do Restart",
        buttons=get_back_button("sudo"),
    )


@callback("sfban")
@owner
async def sfban(event):
    await event.edit(
        "SuperFban Settings:",
        buttons=[
            [Button.inline("FBᴀɴ Gʀᴏᴜᴘ", data="sfgrp")],
            [Button.inline("Exᴄʟᴜᴅᴇ Fᴇᴅs", data="sfexf")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("sfgrp")
@owner
async def sfgrp(event):
    await event.delete()
    name = "FBan Group ID"
    var = "FBAN_GROUP_ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Make a Group, Add @MissRose_Bot, Send `{hndlr}Id`, Copy That And Send It Here.\nUse /cancel To Go Back.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("sfban"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} Changed To {themssg}",
                buttons=get_back_button("sfban"),
            )


@callback("sfexf")
@owner
async def sfexf(event):
    await event.delete()
    name = "Excluded Feds"
    var = "EXCLUDE_FED"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Send The Fed IDs You Want To Exclude In The Ban. Split By a Space.\neg`id1 id2 id3`\nSet Is As `None` If You Dont Want Any.\nUse /cancel To Go Back.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("sfban"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} Changed To {themssg}",
                buttons=get_back_button("sfban"),
            )


@callback("alvcstm")
@owner
async def alvcs(event):
    await event.edit(
        f"Customise Your {HNDLR}Alive. Choose From The Below Options -",
        buttons=[
            [Button.inline("Aʟɪᴠᴇ Tᴇxᴛ", data="alvtx")],
            [Button.inline("Aʟɪᴠᴇ ᴍᴇᴅɪᴀ", data="alvmed")],
            [Button.inline("Dᴇʟᴇᴛᴇ Aʟɪᴠᴇ Mᴇᴅɪᴀ", data="delmed")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )


@callback("alvtx")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_TEXT"
    name = "Alive Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Text**\nEnter The New Alive text.\n\nUse /cancel To Terminate The Operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("alvcstm"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} Changed To {}\n\nAfter Setting All Things Do restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("alvcstm"),
            )


@callback("alvmed")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_PIC"
    name = "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Media**\nSend Me a Pic/Gif/Bot Api Id Of Sticker To Set As Alive Media.\n\nUse /cancel To Terminate The Operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation Cancelled!!",
                    buttons=get_back_button("alvcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "alvpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("alvcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} Has Been Set.",
            buttons=get_back_button("alvcstm"),
        )


@callback("delmed")
@owner
async def dell(event):
    try:
        udB.delete("ALIVE_PIC")
        return await event.edit("Done!", buttons=get_back_button("alvcstm"))
    except BaseException:
        return await event.edit(
            "Something Went Wrong...",
            buttons=get_back_button("alvcstm"),
        )


@callback("pmcstm")
@owner
async def alvcs(event):
    await event.edit(
        "Customise Your PMPERMIT Settings -",
        buttons=[
            [
                Button.inline("Pᴍ Tᴇxᴛ", data="pmtxt"),
                Button.inline("Pᴍ Mᴇᴅɪᴀ", data="pmmed"),
            ],
            [
                Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ", data="apauto"),
                Button.inline("PMLOGGER", data="pml"),
            ],
            [
                Button.inline("Sᴇᴛ Wᴀʀɴs", data="swarn"),
                Button.inline("Dᴇʟᴇᴛᴇ Pᴍ Mᴇᴅɪᴀ", data="delpmmed"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="ppmset")],
        ],
    )


@callback("pmtxt")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "PM_TEXT"
    name = "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Text**\nEnter The New Pmpermit Text.\n\nu Can Use `{name}` `{fullname}` `{count}` `{mention}` `{username}` To Get This From User Too\n\nUse /cancel To Terminate The Operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("pmcstm"),
            )
        else:
            if len(themssg) > 4090:
                return await conv.send_message(
                    "Message Too Long!\nGive a Shorter Message Please!!",
                    buttons=get_back_button("pmcstm"),
                )
            await setit(event, var, themssg)
            await conv.send_message(
                "{} Changed To {}\n\nAfter Setting All Things Do restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("pmcstm"),
            )


@callback("swarn")
@owner
async def name(event):
    m = range(1, 10)
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in m]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« Bᴀᴄᴋ", data="pmcstm")])
    await event.edit(
        "Select The Number Of Warnings For a User Before Getting Blocked In PMs.",
        buttons=lst,
    )


@callback(re.compile(b"wrns_(.*)"))
@owner
async def set_wrns(event):
    value = int(event.data_match.group(1).decode("UTF-8"))
    dn = udB.set("PMWARNS", value)
    if dn:
        await event.edit(
            f"PM Warns Set to {value}.\nNew Users Will Have {value} Chances In PMs Before Getting Banned.",
            buttons=get_back_button("pmcstm"),
        )
    else:
        await event.edit(
            f"Something Went Wrong, Please Check Your {hndlr}Logs!",
            buttons=get_back_button("pmcstm"),
        )


@callback("pmmed")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "PMPIC"
    name = "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Media**\nSend Me a Pic/Gif/ Or Link  To Set As Pmpermit Media.\n\nUse /cancel To Terminate The Operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation Cancelled!!",
                    buttons=get_back_button("pmcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "pmpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("pmcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} Has Been Set.",
            buttons=get_back_button("pmcstm"),
        )


@callback("delpmmed")
@owner
async def dell(event):
    try:
        udB.delete("PMPIC")
        return await event.edit("Done!", buttons=get_back_button("pmcstm"))
    except BaseException:
        return await event.edit(
            "Something Went Wrong...",
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("apauto")
@owner
async def apauto(event):
    await event.edit(
        "This'll Auto Approve On Outgoing Messages",
        buttons=[
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ ON", data="apon")],
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ OFF", data="apof")],
            [Button.inline("« Bᴀᴄᴋ", data="pmcstm")],
        ],
    )


@callback("apon")
@owner
async def apon(event):
    var = "AUTOAPPROVE"
    await setit(event, var, "True")
    await event.edit(
        f"Done!! AUTOAPPROVE  Started!!",
        buttons=[[Button.inline("« Bᴀᴄᴋ", data="apauto")]],
    )


@callback("apof")
@owner
async def apof(event):
    try:
        udB.delete("AUTOAPPROVE")
        return await event.edit(
            "Done! AUTOAPPROVE Stopped!!",
            buttons=[[Button.inline("« Bᴀᴄᴋ", data="apauto")]],
        )
    except BaseException:
        return await event.edit(
            "Something Went Wrong...",
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("pml")
@owner
async def alvcs(event):
    await event.edit(
        "PMLOGGER This Will Forward Ur Pm to Ur Private Group -",
        buttons=[
            [Button.inline("PMLOGGER ON", data="pmlog")],
            [Button.inline("PMLOGGER OFF", data="pmlogof")],
            [Button.inline("« Bᴀᴄᴋ", data="pmcstm")],
        ],
    )


@callback("pmlog")
@owner
async def pmlog(event):
    var = "PMLOG"
    await setit(event, var, "True")
    await event.edit(
        f"Done!! PMLOGGER  Started!!",
        buttons=[[Button.inline("« Bᴀᴄᴋ", data="pml")]],
    )


@callback("pmlogof")
@owner
async def pmlogof(event):
    try:
        udB.delete("PMLOG")
        return await event.edit(
            "Done! PMLOGGER Stopped!!",
            buttons=[[Button.inline("« Bᴀᴄᴋ", data="pml")]],
        )
    except BaseException:
        return await event.edit(
            "Something Went Wrong...",
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("ppmset")
@owner
async def pmset(event):
    await event.edit(
        "PMPermit Settings:",
        buttons=[
            [Button.inline("Tᴜʀɴ PMPᴇʀᴍɪᴛ Oɴ", data="pmon")],
            [Button.inline("Tᴜʀɴ PMPᴇʀᴍɪᴛ Oғғ", data="pmoff")],
            [Button.inline("Cᴜsᴛᴏᴍɪᴢᴇ PMPᴇʀᴍɪᴛ", data="pmcstm")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )


@callback("pmon")
@owner
async def pmonn(event):
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(
        f"Done! PMPermit Has Been Turned On!!",
        buttons=[[Button.inline("« Bᴀᴄᴋ", data="ppmset")]],
    )


@callback("pmoff")
@owner
async def pmofff(event):
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(
        f"Done! PMPermit Has Been Turned Off!!",
        buttons=[[Button.inline("« Bᴀᴄᴋ", data="ppmset")]],
    )


@callback("chatbot")
@owner
async def chbot(event):
    await event.edit(
        f"From This Feature You Can Chat With Ppls Via Your Assistant Bot.\n[More Info](https://t.me/UltroidUpdates/2)",
        buttons=[
            [Button.inline("Cʜᴀᴛ Bᴏᴛ  Oɴ", data="onchbot")],
            [Button.inline("Cʜᴀᴛ Bᴏᴛ  Oғғ", data="ofchbot")],
            [Button.inline("Bᴏᴛ Wᴇʟᴄᴏᴍᴇ", data="bwel")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
        link_preview=False,
    )


@callback("bwel")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "STARTMSG"
    name = "Bot Welcome Message:"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**BOT WELCOME MSG**\nEnter The Msg Which You Want To Show When Someone Start Your Assistant Bot.\n\nUse /cancel To Terminate The Operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("chatbot"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} Changed To {}".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("chatbot"),
            )


@callback("onchbot")
@owner
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "True")
    await event.edit(
        "Done! Now You Can Chat With People Via This Bot",
        buttons=[Button.inline("« Bᴀᴄᴋ", data="chatbot")],
    )


@callback("ofchbot")
@owner
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "False")
    await event.edit(
        "Done! Chat People Via This Bot Stopped.",
        buttons=[Button.inline("« Bᴀᴄᴋ", data="chatbot")],
    )


@callback("vcb")
@owner
async def vcb(event):
    await event.edit(
        f"From This Feature You Can Play Songs In Group Voice Chat\n\n[More Info](https://t.me/UltroidUpdates/4)",
        buttons=[
            [Button.inline("VC Sᴇssɪᴏɴ", data="vcs")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
        link_preview=False,
    )


@callback("vcs")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "VC_SESSION"
    name = "VC SESSION"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Vc session**\nEnter The New Session You Generated For Vc Bot.\n\nUse /cancel To Terminate The Operation.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("vcb"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} Changed To {}\n\nAfter Setting All Things Do restart".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("vcb"),
            )


@callback("inli_pic")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "INLINE_PIC"
    name = "Inline Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Inline Media**\nSend Me a Pic/Gif/ Or Link  To Set As Inline Media.\n\nUse /cancel To Terminate The Operation.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Operation Cancelled!!",
                    buttons=get_back_button("setter"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "inlpic")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("setter"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} Has Been Set.",
            buttons=get_back_button("setter"),
        )

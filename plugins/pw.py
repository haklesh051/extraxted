#  MIT License...
#  Code edited By Cryptostark + Fixed by ChatGPT for Haklesh

import requests
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from subprocess import getstatusoutput

@Client.on_message(filters.command(["pw"]))
async def account_login(bot, m: Message):
    editable = await m.reply_text(
        "Send **Auth code** in this manner otherwise bot will not respond.\n\nSend like this:-  **AUTH CODE**"
    )  
    input1: Message = await bot.listen(editable.chat.id)
    raw_text1 = input1.text

    headers = {
        'Host': 'api.penpencil.xyz',
        'authorization': f"Bearer {raw_text1}",
        'client-id': '5eb393ee95fab7468a79d189',
        'client-version': '12.84',
        'user-agent': 'Android',
        'randomid': 'e4307177362e86f1',
        'client-type': 'MOBILE',
        'device-meta': '{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswalb}',
        'content-type': 'application/json; charset=UTF-8',
    }

    params = {
       'mode': '1',
       'filter': 'false',
       'exam': '',
       'amount': '',
       'organisationId': '5eb393ee95fab7468a79d189',
       'classes': '',
       'limit': '20',
       'page': '1',
       'programId': '',
       'ut': '1652675230446', 
    }

    await editable.edit("**You have these Batches :-\n\nBatch ID : Batch Name**")
    response = requests.get(
        'https://api.penpencil.xyz/v3/batches/my-batches',
        params=params,
        headers=headers
    ).json()["data"]

    for data in response:
        batch_name = data["name"]
        batch_id = data["_id"]
        await m.reply_text(f"```{batch_id}```  :  **{batch_name}**")

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input3 = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    response2 = requests.get(
        f'https://api.penpencil.xyz/v3/batches/{raw_text3}/details',
        headers=headers
    ).json()["data"]["subjects"]

    await editable1.edit("subject : subjectId")
    vj = ""
    for data in response2:
        bb = f"{data['_id']}&"
        await m.reply_text(bb)

    vj = ""
    for data in response2:
        tids = data['_id']
        idid = f"{tids}&"
        if len(f"{vj}{idid}") > 4096:
            await m.reply_text(vj)
            vj = ""
        vj += idid

    await m.reply_text(f"**Enter this to download full batch :-**\n```{vj}```")
    input4 = await bot.listen(editable.chat.id)
    raw_text4 = input4.text

    await m.reply_text("**Enter resolution**")
    input5 = await bot.listen(editable.chat.id)
    raw_text5 = input5.text

    editable4 = await m.reply_text(
        "Now send the **Thumb url** Eg : ```https://telegra.ph/file/d9e24878bd4aba05049a1.jpg```\n\nor Send **no**"
    )
    input6 = await bot.listen(editable.chat.id)
    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    try:
        xv = raw_text4.split('&')
        for y in range(0, len(xv)):
            t = xv[y]
            for page in range(1, 5):
                paramsX = {'page': str(page), 'tag': '', 'contentType': 'exercises-notes-videos', 'ut': ''}
                responseX = requests.get(
                    f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{t}/contents',
                    params=paramsX,
                    headers=headers
                ).json()["data"]

                for data in responseX:
                    class_title = data["topic"]
                    class_url = data["url"].replace("d1d34p8vz63oiq", "d3nzo6itypaz07").replace("mpd", "m3u8").strip()
                    with open(f"{raw_text3}.txt", 'a') as f:
                        f.write(f"{class_title}:{class_url}\n")
        await m.reply_document(f"{raw_text3}.txt")

    except Exception as e:
        await m.reply_text(f"❌ Error:\n`{str(e)}`")

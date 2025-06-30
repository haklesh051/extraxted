#  MIT License
#  Code edited By Cryptostark

import requests
import json
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from subprocess import getstatusoutput
import os

@Client.on_message(filters.command(["pw"]))
async def account_login(bot: Client, m: Message):
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

    await editable.edit("**You have these Batches :-\n\nBatch Name : Batch ID**")
    response = requests.get('https://api.penpencil.xyz/v3/batches/my-batches', params=params, headers=headers).json()["data"]

    for data in response:
        batch_name = data.get("name", "No Name")
        batch_id = data.get("_id")
        if isinstance(batch_id, dict):
            batch_id = batch_id.get("$oid", "UnknownID")
        aa = f"```{batch_name}```  :  ```{batch_id}```"
        await m.reply_text(aa)

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input3 = await bot.listen(editable.chat.id)
    raw_text3 = input3.text

    response2 = requests.get(f'https://api.penpencil.xyz/v3/batches/{raw_text3}/details', headers=headers).json()["data"]["subjects"]
    await editable1.edit("subject : subjectId")

    vj = ""
    for data in response2:
        bb = f"{data['_id']}&"
        await m.reply_text(bb)

    vj = ""
    for data in response2:
        tids = data['_id']
        idid = f"{tids}&"
        if len(vj + idid) > 4096:
            await m.reply_text(vj)
            vj = ""
        vj += idid

    editable2 = await m.reply_text(f"**Enter this to download full batch :-**\n```{vj}```")
    input4 = await bot.listen(editable.chat.id)
    raw_text4 = input4.text

    await m.reply_text("**Enter resolution**")
    input5: Message = await bot.listen(editable.chat.id)
    raw_text5 = input5.text

    editable4 = await m.reply_text("Now send the **Thumb url** Eg : ```https://telegra.ph/file/d9e24878bd4aba05049a1.jpg```\n\nor Send **no**")
    input6 = await bot.listen(editable.chat.id)
    thumb = input6.text

    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    try:
        xv = raw_text4.split('&')
        for t in xv:
            if not t.strip():
                continue

            for page in range(1, 5):
                params = {'page': str(page), 'tag': '', 'contentType': 'exercises-notes-videos', 'ut': ''}
                response_data = requests.get(
                    f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{t}/contents',
                    params=params, headers=headers
                ).json().get("data", [])

                for item in response_data:
                    class_title = item.get("topic", "No Title")
                    class_url = item.get("url", "").replace("d1d34p8vz63oiq", "d3nzo6itypaz07").replace("mpd", "m3u8").strip()
                    with open(f"{batch_name}.txt", 'a') as f:
                        f.write(f"{class_title}:{class_url}\n")

        await m.reply_document(f"{batch_name}.txt")

    except Exception as e:
        await m.reply_text(str(e))

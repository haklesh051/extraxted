#  MIT License
#  Code edited By Cryptostark & Haklesh Bot Team

import requests
import json
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from subprocess import getstatusoutput

@Client.on_message(filters.command(["pw"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text(
        "**Send your PW Auth Token like this:**\n\n`eyJhbGciOiJIUzI1NiIsIn...`"
    )

    input1: Message = await bot.listen(editable.chat.id)
    auth_token = input1.text.strip()

    headers = {
        'authorization': f"Bearer {auth_token}",
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
        'organisationId': '5eb393ee95fab7468a79d189',
        'limit': '20',
        'page': '1',
    }

    try:
        response = requests.get(
            'https://api.penpencil.xyz/v3/batches/my-batches',
            headers=headers, params=params
        ).json()["data"]

        if not response:
            return await editable.edit("❌ No purchased batches found.")

        await editable.edit("✅ **Your Purchased Batches:**")

        for data in response:
            batch_name = data["name"]
            batch_id = data["_id"]
            await m.reply_text(f"📦 **{batch_name}**\n🆔 Batch ID: `{batch_id}`")

        msg = await m.reply_text("Now send the **Batch ID** to download:")
        input2: Message = await bot.listen(m.chat.id)
        batch_id = input2.text.strip()

        subjects = requests.get(
            f'https://api.penpencil.xyz/v3/batches/{batch_id}/details',
            headers=headers
        ).json()["data"]["subjects"]

        await msg.edit("📚 **Subject IDs:**\n(You can select one or all)")

        vj = ""
        for sub in subjects:
            sub_id = sub["_id"]
            line = f"{sub_id}&"
            if len(vj + line) > 4000:
                await m.reply_text(vj)
                vj = ""
            vj += line
        await m.reply_text(f"📥 **Use this to download full batch:**\n```{vj}```")

        input3: Message = await bot.listen(m.chat.id)
        subject_ids_raw = input3.text.strip()

        await m.reply_text("🖼️ Now send the **video resolution** (e.g., 360, 480, 720):")
        input4: Message = await bot.listen(m.chat.id)
        resolution = input4.text.strip()

        thumb_msg = await m.reply_text("📷 Send **thumbnail URL** or type `no`:")
        input5: Message = await bot.listen(m.chat.id)
        thumb_url = input5.text.strip()

        thumb = ""
        if thumb_url.startswith("http"):
            getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
            thumb = "thumb.jpg"

        all_ids = subject_ids_raw.split('&')
        output_filename = f"{batch_id}.txt"

        for sub_id in all_ids:
            if not sub_id.strip():
                continue

            for page in range(1, 5):
                params_page = {
                    'page': str(page),
                    'tag': '',
                    'contentType': 'exercises-notes-videos',
                    'ut': ''
                }

                try:
                    content_data = requests.get(
                        f'https://api.penpencil.xyz/v2/batches/{batch_id}/subject/{sub_id}/contents',
                        headers=headers, params=params_page
                    ).json()["data"]

                    for item in content_data:
                        topic = item.get("topic")
                        url = item.get("url", "").replace("d1d34p8vz63oiq", "d3nzo6itypaz07").replace("mpd", "m3u8").strip()

                        if topic and url:
                            with open(output_filename, "a", encoding="utf-8") as f:
                                f.write(f"{topic}:{url}\n")

                except Exception as e:
                    await m.reply_text(f"⚠️ Error: {str(e)}")

        await m.reply_document(output_filename)

    except Exception as e:
        await m.reply_text(f"❌ Error: `{str(e)}`")

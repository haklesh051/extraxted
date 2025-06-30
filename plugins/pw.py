from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from pyromod import listen
from subprocess import getstatusoutput

@Client.on_message(filters.command(["pw"]))
async def account_login(bot: Client, m: Message):
    # Step 1: Get auth token
    editable = await m.reply_text("Send **Auth code** like this:\n\n`AUTH_CODE`")
    input1: Message = await bot.listen(editable.chat.id)
    auth_code = input1.text.strip()

    # Step 2: Headers for PenPencil API
    headers = {
        'Host': 'api.penpencil.xyz',
        'authorization': f"Bearer {auth_code}",
        'client-id': '5eb393ee95fab7468a79d189',
        'client-version': '12.84',
        'user-agent': 'Android',
        'randomid': 'e4307177362e86f1',
        'client-type': 'MOBILE',
        'device-meta': '{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswallah}',
        'content-type': 'application/json; charset=UTF-8',
    }

    # Step 3: Get list of batches
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

    await editable.edit("**Fetching your batches...**")
    res = requests.get('https://api.penpencil.xyz/v3/batches/my-batches', headers=headers, params=params).json()
    batch_data = res.get("data", [])

    if not batch_data:
        return await m.reply_text("No batches found.")

    batch_list = "**📦 Your Batches:**\n\n"
    for data in batch_data:
        batch_name = data.get("name", "Unknown")
        batch_id = data.get("_id", "Unknown")
        batch_list += f"`{batch_name}` ➤ `{batch_id}`\n"

    await m.reply_text(batch_list)

    # Step 4: Ask user for Batch ID
    editable2 = await m.reply_text("Now send the **Batch ID** you want to explore:")
    input2 = await bot.listen(editable2.chat.id)
    batch_id = input2.text.strip()

    # Step 5: Fetch Subjects from Batch
    res2 = requests.get(f'https://api.penpencil.xyz/v3/batches/{batch_id}/details', headers=headers).json()
    subjects = res2["data"].get("subjects", [])

    subject_ids = ""
    subject_list = "**📚 Subjects Found:**\n\n"
    for sub in subjects:
        subject_list += f"`{sub['subject']}` ➤ `{sub['_id']}`\n"
        subject_ids += f"{sub['_id']}&"

    await m.reply_text(subject_list)
    await m.reply_text(f"**👉 Use this ID string to continue:**\n```{subject_ids}```")

    # Step 6: Get subject IDs to download
    editable3 = await m.reply_text("Send the subject ID list (joined with `&`) to download:")
    input3 = await bot.listen(editable3.chat.id)
    input_subjects = input3.text.strip().split("&")

    # Step 7: Ask for resolution
    await m.reply_text("Enter desired resolution (e.g. 360, 480, 720):")
    input4 = await bot.listen(editable3.chat.id)
    resolution = input4.text.strip()

    # Step 8: Optional thumbnail
    editable4 = await m.reply_text("Send **thumbnail URL** or type `no`:")
    input5 = await bot.listen(editable4.chat.id)
    thumb = input5.text.strip()
    if thumb.startswith("http"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = None

    # Step 9: Download content from each subject
    file_name = f"{batch_id}.txt"
    open(file_name, "w").close()  # clear file if already exists

    for subject in input_subjects:
        if not subject.strip():
            continue
        for page in range(1, 5):
            content_url = f'https://api.penpencil.xyz/v2/batches/{batch_id}/subject/{subject}/contents'
            params = {'page': str(page), 'tag': '', 'contentType': 'exercises-notes-videos', 'ut': ''}
            try:
                content = requests.get(content_url, params=params, headers=headers).json().get("data", [])
                for item in content:
                    title = item.get("topic", "No title")
                    url = item.get("url", "").replace("d1d34p8vz63oiq", "d3nzo6itypaz07").replace("mpd", "m3u8")
                    if url:
                        with open(file_name, "a") as f:
                            f.write(f"{title}:{url}\n")
            except Exception as e:
                await m.reply_text(f"Error: {str(e)}")

    await m.reply_document(file_name, caption="✅ Done!")

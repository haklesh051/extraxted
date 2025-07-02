import os, time, requests, re, subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from helper import pull_run, duration
from p_bar import progress_bar
from subprocess import getstatusoutput

API_ID = 123456  # your api_id
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

app = Client("pw_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def extract_key_url(m3u8_url):
    try:
        res = requests.get(m3u8_url)
        if "#EXT-X-KEY" in res.text:
            match = re.search(r'URI="(.*?)"', res.text)
            if match:
                return match.group(1)
        return None
    except:
        return None

@app.on_message(filters.command("down"))
async def download_command(bot: Client, m: Message):
    await m.reply_text("📄 Send text file (`Name:URL` per line)")
    input = await bot.listen(m.chat.id)
    x = await input.download()
    await input.delete(True)

    try:
        with open(x, "r") as f:
            content = f.read().splitlines()
        links = [line.split(":", 1) for line in content if ":" in line]
        os.remove(x)
    except:
        await m.reply_text("❌ Invalid file format.")
        os.remove(x)
        return

    await m.reply_text(f"✅ Total links: {len(links)}\n\nSend resolution (e.g. 360):")
    res = (await bot.listen(m.chat.id)).text.strip()

    await m.reply_text("📦 Enter Batch Name:")
    batch = (await bot.listen(m.chat.id)).text.strip()

    await m.reply_text("👤 Enter Downloaded By:")
    who = (await bot.listen(m.chat.id)).text.strip()

    await m.reply_text("⚙️ Threads (default 1):")
    try:
        thread = int((await bot.listen(m.chat.id)).text.strip())
    except:
        thread = 1

    count = 1
    cmds = []

    for name_raw, url in links:
        name = name_raw.translate(str.maketrans("", "", ":/|@*+?<>\\\"")).strip()
        base_cmd = ['yt-dlp', '--no-part', '--no-check-certificate', '-N', '100']
        if ".pdf" in url:
            base_cmd += ['-o', f'{name}.pdf', url]
        elif ".m3u8" in url:
            key = extract_key_url(url)
            if key:
                base_cmd += ['-o', f'{name}.mp4', url]
            else:
                await m.reply_text(f"🔒 DRM or key missing. Skipped: `{name}`")
                continue
        else:
            base_cmd += ['-S', f'height:{res},ext:mp4', '-o', f'{name}.mp4', url]
        cmds.append(base_cmd)

    for i in range(0, len(cmds), thread):
        batch_cmds = cmds[i:i+thread]
        await m.reply_text(f"⬇️ Downloading batch {i+1}")
        pull_run(thread, batch_cmds)

        for cmd in batch_cmds:
            try:
                filename = cmd[-2]
                caption = f"{str(count).zfill(2)}. {filename}\n\n**Batch »** {batch}\n**By »** {who}"
                if filename.endswith(".pdf"):
                    await m.reply_document(filename, caption=caption)
                    os.remove(filename)
                else:
                    reply = await m.reply_text("📤 Uploading...")
                    thumbnail = f"{filename}.jpg"
                    subprocess.run(f'ffmpeg -y -i "{filename}" -ss 00:00:03 -vframes 1 "{thumbnail}"', shell=True)
                    duration_sec = int(duration(filename))
                    start_time = time.time()

                    await m.reply_video(
                        filename,
                        caption=caption,
                        thumb=thumbnail,
                        height=720,
                        width=1280,
                        duration=duration_sec,
                        supports_streaming=True,
                        progress=progress_bar,
                        progress_args=(reply, start_time)
                    )
                    await reply.delete()
                    os.remove(filename)
                    if os.path.exists(thumbnail): os.remove(thumbnail)
                count += 1
            except Exception as e:
                await m.reply_text(f"❌ Upload error: {str(e)}")
                continue

    await m.reply_text("✅ Done!")

app.run()

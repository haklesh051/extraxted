from pyrogram import Client, filters
from pyrogram.types import Message
import os, time, requests
from subprocess import getstatusoutput
from helper import pull_run, duration  # Use your existing helper functions
from p_bar import progress_bar

# Function to check if AES encryption key is available in m3u8
def extract_key_url(m3u8_url):
    try:
        res = requests.get(m3u8_url)
        content = res.text
        if "#EXT-X-KEY" in content:
            import re
            match = re.search(r'URI="(.*?)"', content)
            if match:
                return match.group(1)
        return None
    except:
        return None

@Client.on_message(filters.command(["down"]))
async def account_login(bot: Client, m: Message):
    await m.reply_text("**Send Text file containing URLs (Name:URL format)**")
    input: Message = await bot.listen(m.chat.id)
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

    await m.reply_text(f"✅ Total links found: {len(links)}\n\nSend start index (default 0):")
    input1 = await bot.listen(m.chat.id)
    try:
        start_index = int(input1.text.strip())
    except:
        start_index = 0

    await m.reply_text("📦 Enter Batch Name:")
    batch = (await bot.listen(m.chat.id)).text

    await m.reply_text("👤 Enter Downloaded By (name):")
    who = (await bot.listen(m.chat.id)).text

    await m.reply_text("🎞️ Enter resolution (360 / 480 / etc.):")
    resolution = (await bot.listen(m.chat.id)).text

    await m.reply_text("🖼️ Enter Thumbnail URL or 'no':")
    thumb_msg = await bot.listen(m.chat.id)
    thumb_input = thumb_msg.text.strip()
    thumb = "thumb.jpg" if thumb_input.startswith("http") else "no"
    if thumb != "no":
        getstatusoutput(f"wget '{thumb_input}' -O 'thumb.jpg'")

    await m.reply_text("⚙️ Enter number of threads:")
    thread_msg = await bot.listen(m.chat.id)
    try:
        thread = int(thread_msg.text.strip())
    except:
        thread = 1

    count = 1
    clist = []

    for i in range(start_index, len(links)):
        try:
            name_raw, url = links[i]
            name = name_raw.replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("\t", "").strip()
        except:
            continue

        base_cmd = ['yt-dlp', '--ignore-errors', '--no-part', '--no-check-certificate', '-N', '100']

        if ".pdf" in url:
            base_cmd += ['-o', f'{name}.pdf', url]
        elif ".m3u8" in url:
            key = extract_key_url(url)
            if key:
                base_cmd += ['-o', f'{name}.mp4', url]
            else:
                await m.reply_text(f"🔒 DRM or no key found. Skipping: `{name}`")
                continue
        else:
            base_cmd += ['-S', f'height:{resolution},ext:mp4', '-o', f'{name}.mp4', url]

        clist.append(base_cmd)

    try:
        for i in range(0, len(clist), thread):
            batch_cmds = clist[i:i + thread]
            status_msg = await m.reply_text("⬇️ Downloading...")

            try:
                pull_run(thread, batch_cmds)

                for cmd in batch_cmds:
                    try:
                        filename = cmd[-2]
                    except:
                        continue

                    caption = f"{str(count).zfill(2)}. {filename}\n\n**Batch »** {batch}\n**Downloaded By »** {who}"

                    if filename.endswith(".pdf"):
                        await m.reply_document(filename, caption=caption)
                        os.remove(filename)
                        count += 1
                        continue

                    # Video flow
                    reply = await m.reply_text("📤 Uploading video...")
                    try:
                        if thumb == "no":
                            subprocess.run(f'ffmpeg -i "{filename}" -ss 00:00:30 -vframes 1 "{filename}.jpg"', shell=True)
                            thumbnail = f"{filename}.jpg"
                        else:
                            thumbnail = "thumb.jpg"
                    except Exception as e:
                        await m.reply_text(f"🖼️ Thumbnail Error: {str(e)}")
                        continue

                    duration_in_sec = int(duration(filename))
                    start_time = time.time()
                    caption = f"{str(count).zfill(2)}. {filename} - {resolution}p\n\n**Batch »** {batch}\n**Downloaded By »** {who}"

                    await m.reply_video(
                        filename,
                        caption=caption,
                        thumb=thumbnail,
                        height=720,
                        width=1280,
                        duration=duration_in_sec,
                        supports_streaming=True,
                        progress=progress_bar,
                        progress_args=(reply, start_time)
                    )

                    await reply.delete()
                    os.remove(filename)
                    if os.path.exists(f"{filename}.jpg"):
                        os.remove(f"{filename}.jpg")
                    count += 1

            except Exception as e:
                await m.reply_text(f"❌ Error in batch: {str(e)}")
                continue

    except Exception as e:
        await m.reply_text(f"❌ Final Error: {str(e)}")

    await m.reply_text("✅ All done!")

import asyncio
import re

from AyiinXd import CMD_HANDLER as cmd,CMD_HELP,BOTLOG_CHATID,bot,LOOP
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd.modules.sql_helper import spam_sql

from telethon.errors import FloodWaitError

active_spams={}
MIN_DELAY=5


async def send_log(client,text):
    if BOTLOG_CHATID:
        try: await client.send_message(BOTLOG_CHATID,text)
        except Exception as e: print(f"[LOG] {e}")


async def safe_send(client,g,text=None,media=None):
    try:
        if media: await client.send_file(g,media,caption=text or "",parse_mode="html")
        else: await client.send_message(g,text,parse_mode="html")
        return True,None
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds);return False,f"FloodWait {e.seconds}s"
    except Exception as e:return False,str(e)


def task_alive(nama):
    task=active_spams.get(nama)
    if not task:return False
    if task.done():active_spams.pop(nama,None);return False
    return True


@ayiin_cmd(pattern=r"setgrup (\S+)\s+([\s\S]+)")
async def setgrup(event):
    nama=event.pattern_match.group(1).strip()
    grups=[]
    for g in event.pattern_match.group(2).split():
        g=g.replace("https://t.me/","").strip("/")
        if not g.startswith("@"):g=f"@{g}"
        grups.append(g)
    if not grups:return await event.edit("✘ Grup tidak ditemukan.")
    spam_sql.add_list(nama,"spam","",MIN_DELAY)
    spam_sql.add_groups_to_list(nama,grups)
    await event.edit(f"✓ Berhasil menambahkan `{len(grups)}` grup ke `{nama}`.")


@ayiin_cmd(pattern=r"onspam (\d+)\s+(\S+)\s+([\s\S]+)")
async def onspam(event):
    delay=int(event.pattern_match.group(1))
    nama=event.pattern_match.group(2).strip()
    teks=event.pattern_match.group(3).strip()

    if delay<MIN_DELAY:return await event.edit(f"✘ Delay minimal {MIN_DELAY} detik.")
    if task_alive(nama):return await event.edit(f"∅ Spam `{nama}` sudah berjalan.")

    if not spam_sql.get_list(nama):return await event.edit(f"✘ List `{nama}` tidak ditemukan.")
    if not spam_sql.get_groups(nama):return await event.edit(f"✘ List `{nama}` kosong.")

    reply=await event.get_reply_message()
    media=reply.media if reply else None
    if reply and media:
        spam_sql.update_media(
            nama,
            event.chat_id,
            reply.id,
            type(media).__name__
        )

    spam_sql.update_list(nama,"spam",delay,teks)
    spam_sql.set_active(nama,True)

    await event.edit(f"⎋ Spam `{nama}` dimulai.")

    async def loop():
        try:
            while True:
                for g in spam_sql.get_groups(nama):
                    await safe_send(event.client,g,teks,media)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[SPAM ERROR] {e}")
        finally:
            spam_sql.set_active(nama,False)
            active_spams.pop(nama,None)

    active_spams[nama]=asyncio.create_task(loop())

@ayiin_cmd(pattern=r"onfw (\d+)\s+(\S+)\s+(https?://t\.me/[^\s]+)")
async def onfw(event):
    delay=int(event.pattern_match.group(1))
    nama=event.pattern_match.group(2).strip()
    link=event.pattern_match.group(3).strip()

    if delay<MIN_DELAY:return await event.edit(f"✘ Delay minimal {MIN_DELAY} detik.")
    if task_alive(nama):return await event.edit(f"∅ Forward `{nama}` sudah berjalan.")
    if not spam_sql.get_list(nama):return await event.edit(f"✘ List `{nama}` tidak ditemukan.")
    if not spam_sql.get_groups(nama):return await event.edit(f"✘ List `{nama}` kosong.")

    try:
        m=re.match(r"https://t.me/(c/)?(-?\d+|\w+)/(\d+)",link)
        if not m:raise Exception("Link tidak valid")
        chat=m.group(2);msg_id=int(m.group(3))
        chat_id=int("-100"+chat) if m.group(1)=="c/" else (int(chat) if chat.isdigit() else chat)
        msg=await event.client.get_messages(chat_id,ids=msg_id)
    except Exception as e:
        return await event.edit(f"✘ Gagal mengambil pesan: {e}")

    spam_sql.update_list(nama,"forward",delay,link)
    spam_sql.set_active(nama,True)

    await event.edit(f"⎋ Forward `{nama}` dimulai.")

    async def loop():
        try:
            while True:
                for g in spam_sql.get_groups(nama):
                    try:await event.client.forward_messages(g,msg)
                    except FloodWaitError as e:await asyncio.sleep(e.seconds)
                    except Exception as e:print(f"[FW] {e}")
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[FW ERROR] {e}")
        finally:
            spam_sql.set_active(nama,False)
            active_spams.pop(nama,None)

    active_spams[nama]=asyncio.create_task(loop())


@ayiin_cmd(pattern=r"stopspam (.+)")
async def stopspam(event):
    nama=event.pattern_match.group(1).strip()
    task=active_spams.get(nama)
    spam_sql.set_active(nama,False)

    if not task:return await event.edit(f"✘ Spam `{nama}` tidak berjalan.")

    task.cancel()
    active_spams.pop(nama,None)

    await event.edit(f"∅ Spam `{nama}` berhasil dihentikan.")


@ayiin_cmd(pattern="listspam$")
async def listspam(event):
    lists=spam_sql.get_all_lists()
    if not lists:return await event.edit("✘ Tidak ada list spam.")

    teks="**⎉ Daftar Spam:**\n\n"

    for l in lists:
        teks+=f"• `{l.name}` [{l.type}] | Grup: `{len(spam_sql.get_groups(l.name))}` | Delay: `{l.delay}s` | {'Aktif ✓' if l.is_active else 'Nonaktif ❌'}\n"

    await event.edit(teks)


@ayiin_cmd(pattern=r"listsave (.+)")
async def listsave(event):
    nama=event.pattern_match.group(1).strip()
    data=spam_sql.get_list(nama)

    if not data:return await event.edit(f"✘ List `{nama}` tidak ditemukan.")

    grup=spam_sql.get_groups(nama)
    me=await event.client.get_me()
    akun=f"@{me.username}" if me.username else me.first_name

    teks=f"⎉ **List:** `{nama}`\n• Jenis: `{data.type}`\n• Delay: `{data.delay}s`\n• Status: `{data.is_active}`\n• Akun: `{akun}`\n• Isi:\n{data.content}\n\n⎋ **Grup:**\n"

    teks+="\n".join(f"• `{x}`" for x in grup)

    await event.edit(teks)


@ayiin_cmd(pattern=r"delgrup (.+?) (.+)")
async def delgrup(event):
    nama=event.pattern_match.group(1).strip()
    grup=event.pattern_match.group(2).strip()

    spam_sql.delete_group(nama,grup)

    await event.edit(f"✓ `{grup}` dihapus dari `{nama}`.")


@ayiin_cmd(pattern=r"dellist (.+)")
async def dellist(event):
    nama=event.pattern_match.group(1).strip()

    spam_sql.delete_list(nama)

    await event.edit(f"♺ List `{nama}` dihapus.")


@ayiin_cmd(pattern="slist$")
async def slist(event):
    lists=spam_sql.get_all_lists()

    if not lists:return await event.edit("✘ Belum ada list.")

    teks="♺ **Nama List Spam:**\n\n"

    for l in lists:
        grup=spam_sql.get_groups(l.name)
        if grup:teks+=f"• `{l.name}` ({len(grup)} grup)\n"

    await event.edit(teks)

async def auto_resume_spam_startup():
    await asyncio.sleep(10)
    resumed=[]

    for l in spam_sql.get_all_lists():
        if not l.is_active:continue
        if not spam_sql.get_groups(l.name):continue

        media=None

        if getattr(l,"media_msg",0):
            try:
                m=await bot.get_messages(int(l.media_chat),ids=l.media_msg)
                media=m.media
            except Exception as e:
                print(f"[MEDIA RESUME] {e}")

        if l.type=="spam":

            async def resume_spam(nama=l.name,teks=l.content,delay=l.delay,media=media):
                try:
                    while True:
                        for g in spam_sql.get_groups(nama):
                            try:
                                if media:
                                    await bot.send_file(g,media,caption=teks or "",parse_mode="html")
                                else:
                                    await bot.send_message(g,teks,parse_mode="html")
                            except FloodWaitError as e:
                                await asyncio.sleep(e.seconds)
                            except Exception as e:
                                print(f"[SPAM RESUME] {e}")
                        await asyncio.sleep(delay)

                except asyncio.CancelledError:raise
                finally:
                    spam_sql.set_active(nama,False)
                    active_spams.pop(nama,None)

            active_spams[l.name]=asyncio.create_task(resume_spam())
            resumed.append(l.name)


        elif l.type=="forward":

            try:
                m=re.match(r"https://t.me/(c/)?(-?\d+|\w+)/(\d+)",l.content)
                if not m:continue

                chat=m.group(2)
                mid=int(m.group(3))
                cid=int("-100"+chat) if m.group(1)=="c/" else (int(chat) if chat.isdigit() else chat)
                msg=await bot.get_messages(cid,ids=mid)

                async def resume_fw(nama=l.name,msg=msg,delay=l.delay):
                    try:
                        while True:
                            for g in spam_sql.get_groups(nama):
                                try:await bot.forward_messages(g,msg)
                                except FloodWaitError as e:await asyncio.sleep(e.seconds)
                                except Exception as e:print(f"[FW RESUME] {e}")
                            await asyncio.sleep(delay)
                    except asyncio.CancelledError:raise
                    finally:
                        spam_sql.set_active(nama,False)
                        active_spams.pop(nama,None)

                active_spams[l.name]=asyncio.create_task(resume_fw())
                resumed.append(l.name)

            except Exception as e:
                print(f"[AUTO FW] {e}")

    if resumed and BOTLOG_CHATID:
        try:
            await bot.send_message(BOTLOG_CHATID,"♻️ **Spam Resume:**\n"+"\n".join(f"• `{x}`" for x in resumed))
        except:pass

LOOP.create_task(auto_resume_spam_startup())


CMD_HELP.update(
    {
        "spamloop": f"**Plugin : **`spamloop`\
        \n\n  »  **Perintah :** `{cmd}onspam <delay> <namalist> <teks sebar>`\
        \n  »  **Kegunaan :** Mengirim spam teks otomatis ke semua grup yang ada di dalam list. Bisa mengirim media dengan cara reply pesan terlebih dahulu.\
        \n\n  »  **Perintah :** `{cmd}onfw <delay> <namalist> <link pesan channel>`\
        \n  »  **Kegunaan :** Mengirim forward pesan dari channel Telegram ke semua grup yang ada di dalam list secara otomatis.\
        \n\n  »  **Perintah :** `{cmd}stopspam <namalist>`\
        \n  »  **Kegunaan :** Menghentikan spam yang sedang berjalan pada list tertentu dan menonaktifkan auto resume.\
        \n\n  »  **Perintah :** `{cmd}setgrup <namalist> <@grup1> <@grup2>`\
        \n  »  **Kegunaan :** Menambahkan beberapa grup ke dalam satu list spam. Mendukung banyak grup sekaligus.\
        \n\n  »  **Perintah :** `{cmd}listspam`\
        \n  »  **Kegunaan :** Menampilkan semua list spam yang tersimpan beserta jumlah grup, delay, dan status aktif/nonaktif.\
        \n\n  »  **Perintah :** `{cmd}listsave <namalist>`\
        \n  »  **Kegunaan :** Menampilkan detail list seperti jenis spam, delay, jumlah grup, akun pengirim, dan isi pesan/link yang digunakan.\
        \n\n  »  **Perintah :** `{cmd}slist`\
        \n  »  **Kegunaan :** Menampilkan semua nama list spam yang memiliki grup tersimpan.\
        \n\n  »  **Perintah :** `{cmd}delgrup <namalist> <@grup>`\
        \n  »  **Kegunaan :** Menghapus grup tertentu dari list spam.\
        \n\n  »  **Perintah :** `{cmd}dellist <namalist>`\
        \n  »  **Kegunaan :** Menghapus seluruh list spam beserta semua grup yang tersimpan di dalamnya.\
        \n\n  •  **NOTE :**\
        \n    - Delay menggunakan hitungan detik.\
        \n    - Bisa mengirim media dengan cara reply pesan media terlebih dahulu sebelum menjalankan `{cmd}onspam`.\
        \n    - Link forward harus berupa link pesan Telegram (contoh: `https://t.me/channel/123`).\
        \n    - Grup harus dimasukkan terlebih dahulu menggunakan `{cmd}setgrup`.\
        \n    - Data list tersimpan di database.\
        \n    - Sistem mendukung auto resume setelah restart jika status list masih aktif.\
        \n    - Gunakan dengan bijak, spam berlebihan dapat menyebabkan pembatasan akun Telegram!"
    }
)

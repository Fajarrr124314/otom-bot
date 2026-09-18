import asyncio
import datetime
import time

async def wait_until_target(target_time_str: str):
    """
    Menunggu sampai waktu target (format HH:MM:SS).
    Menampilkan countdown setiap detik, lalu beralih ke micro-polling ketika mendekati waktu target.
    """
    if not target_time_str or not target_time_str.strip():
        print("[Scheduler] Target time kosong. Memulai eksekusi sekarang...")
        return

    parts = list(map(int, target_time_str.strip().split(":")))
    target_hour, target_minute, target_second = parts[0], parts[1], parts[2]
    
    print(f"[*] Menunggu waktu target: {target_time_str} ...")

    last_logged_sec = -1
    while True:
        now = datetime.datetime.now()
        current_time = (now.hour, now.minute, now.second)
        target_tuple = (target_hour, target_minute, target_second)

        # Jika sudah sampai atau melewati target
        if current_time >= target_tuple:
            print(f"\n[+] WAKTU TERCAPAI! Waktu sistem: {now.strftime('%H:%M:%S.%f')[:-3]}")
            break

        # Log countdown setiap detik
        if now.second != last_logged_sec:
            remaining_seconds = (
                (target_hour - now.hour) * 3600 +
                (target_minute - now.minute) * 60 +
                (target_second - now.second)
            )
            if remaining_seconds > 0:
                print(f"\r[*] Menunggu... Sisa waktu: {remaining_seconds} detik", end="", flush=True)
            last_logged_sec = now.second

        # Jika mendekati 2 detik terakhir, gunakan sleep yang sangat singkat (high precision)
        await asyncio.sleep(0.01)

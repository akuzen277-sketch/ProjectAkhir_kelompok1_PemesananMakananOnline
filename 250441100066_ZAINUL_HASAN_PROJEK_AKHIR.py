import time
import os
import random
import json
from datetime import datetime

DATA_FILE = "data.json"

DEFAULT = {
    "USERS": {"user@gmail.com": "123"},
    "ADMINS": {"zen_&_vina@gmail.com": "admin071025"},
    "MENU": {
        "nasi goreng": 15000,
        "ayam geprek": 18000,
        "mie ayam": 12000,
        "es teh": 5000,
        "jus alpukat": 12000,
        "kopi": 8000
    },

    "KUPON": {
        "FREEONGKIR": {"type": "ongkir", "val": 100, "uses": None},
        "FIVEDISK": {"type": "pct", "val": 5, "uses": None}
    },
    "DRIVERS": {
        "driver a": {"ongkir": 8000, "eta_menit": 10, "status": "online", "busy": False, "ratings": [], "total_orders": 0, "bonus": 0, "pos": (0,0)},
        "driver b": {"ongkir": 10000, "eta_menit": 12, "status": "online", "busy": False, "ratings": [], "total_orders": 0, "bonus": 0, "pos": (0,0)},
        "driver c": {"ongkir": 12000, "eta_menit": 8, "status": "offline", "busy": False, "ratings": [], "total_orders": 0, "bonus": 0, "pos": (0,0)}
    },
    "RIWAYAT": {},
    "ORDER_COUNTER": 1
}

USERS = {}
ADMINS = {}
MENU = {}
KUPON = {}
DRIVERS = {}
RIWAYAT = {}
ORDER_COUNTER = 1
CART = []
ACTIVE_ORDER = None
CHATS = {}

def load_data():
    global USERS, ADMINS, MENU, KUPON, DRIVERS, RIWAYAT, ORDER_COUNTER
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_users = data.get("USERS", DEFAULT["USERS"])
            USERS = {}
            for k, v in raw_users.items():
                if isinstance(v, dict):
                    userdict = v.copy()
                    userdict.setdefault("password", userdict.get("password", ""))
                    userdict.setdefault("used_coupons", userdict.get("used_coupons", []))
                    userdict.setdefault("new_user_bonus", userdict.get("new_user_bonus", False))
                    USERS[k] = userdict
                else:
                    USERS[k] = {"password": v, "used_coupons": [], "new_user_bonus": False}
            ADMINS = data.get("ADMINS", DEFAULT["ADMINS"])
            MENU = data.get("MENU", DEFAULT["MENU"])
            KUPON = data.get("KUPON", DEFAULT["KUPON"])
            DRIVERS = data.get("DRIVERS", DEFAULT["DRIVERS"])
            RIWAYAT = data.get("RIWAYAT", DEFAULT["RIWAYAT"])
            ORDER_COUNTER = data.get("ORDER_COUNTER", DEFAULT["ORDER_COUNTER"])
            print("[Data loaded from data.json]")
        except Exception as e:
            print("[Gagal load data, pakai default]", e)
            set_defaults()
    else:
        set_defaults()

def save_data():
    try:
        data_users = {}
        for k, v in USERS.items():
            data_users[k] = v
        data = {
            "USERS": data_users,
            "ADMINS": ADMINS,
            "MENU": MENU,
            "KUPON": KUPON,
            "DRIVERS": DRIVERS,
            "RIWAYAT": RIWAYAT,
            "ORDER_COUNTER": ORDER_COUNTER
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Gagal menyimpan data:", e)

def set_defaults():
    global USERS, ADMINS, MENU, KUPON, DRIVERS, RIWAYAT, ORDER_COUNTER
    USERS = {}
    for k, v in DEFAULT["USERS"].items():
        if isinstance(v, dict):
            USERS[k] = v.copy()
        else:
            USERS[k] = {"password": v, "used_coupons": [], "new_user_bonus": False}
    ADMINS = DEFAULT["ADMINS"].copy()
    MENU = DEFAULT["MENU"].copy()
    KUPON = DEFAULT["KUPON"].copy()
    DRIVERS = DEFAULT["DRIVERS"].copy()
    RIWAYAT = DEFAULT["RIWAYAT"].copy()
    ORDER_COUNTER = DEFAULT["ORDER_COUNTER"]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header(title):
    print("="*60)
    print(title.center(60))
    print("="*60)

def pause():
    try:
        input("\nTekan ENTER untuk melanjutkan...")
    except KeyboardInterrupt:
        print()

def safe_input(prompt="> "):
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print()
        return ""

def to_key(s):
    return s.strip().lower() if isinstance(s, str) else s

def currency(x):
    try:
        if isinstance(x, float):
            x = int(round(x))
        return f"Rp{int(x):,}".replace(",", ".")
    except:
        return f"Rp{x}"

def sign_up():
    header("DAFTAR USER BARU")
    email = to_key(safe_input("Masukkan email: "))
    if not email:
        print("Email tidak boleh kosong.")
        return None
    if email in USERS:
        print("Email sudah terdaftar.")
        return None
    pw = safe_input("Buat password: ")
    USERS[email] = {"password": pw, "used_coupons": [], "new_user_bonus": False}
    give_new_user_coupons(email)
    save_data()
    print("Pendaftaran berhasil. Silakan login.")
    return email

def login_user():
    header("LOGIN USER")
    email = to_key(safe_input("Email: "))
    pw = safe_input("Password: ")
    user = USERS.get(email)
    if user and isinstance(user, dict) and user.get("password") == pw:
        print(f"Login berhasil. Hi {email}!")
        return email
    if USERS.get(email) == pw:
        print(f"Login berhasil. Hi {email}!")
        return email
    print("Email atau password salah.")
    return None

def login_admin():
    header("LOGIN ADMIN")
    email = to_key(safe_input("Email Admin: "))
    pw = safe_input("Password: ")
    if ADMINS.get(email) == pw:
        print("Login admin berhasil.")
        return email
    print("Credential admin salah.")
    return None

def tampilkan_menu():
    header("MENU TOKO")
    for name, price in MENU.items():
        print(f"- {name.title():30} {currency(price)}")
    print("-"*60)

def tambah_menu_admin():
    header("TAMBAH MENU (ADMIN)")
    name = to_key(safe_input("Nama menu: "))
    if not name:
        print("Nama kosong.")
        return
    if name in MENU:
        print("Menu sudah ada.")
        return
    try:
        price = int(safe_input("Harga (angka): "))
    except:
        print("Harga harus angka.")
        return
    MENU[name] = price
    save_data()
    print("Menu ditambahkan.")

def hapus_menu_admin():
    header("HAPUS MENU (ADMIN)")
    lihat = list(MENU.keys())
    for i, k in enumerate(lihat, start=1):
        print(f"{i}. {k.title()} - {currency(MENU[k])}")
    idx = safe_input("Pilih nomor menu untuk hapus: ")
    try:
        idx = int(idx)-1
        key = lihat[idx]
        del MENU[key]
        save_data()
        print("Menu dihapus.")
    except:
        print("Pilihan tidak valid.")

def update_menu_admin():
    header("UPDATE MENU (ADMIN)")
    if not MENU:
        print("Menu masih kosong.")
        pause()
        return

    # tampilkan list menu
    daftar = list(MENU.items())
    for i, (nama, harga) in enumerate(daftar, start=1):
        print(f"{i}. {nama.title()} - {currency(harga)}")

    try:
        idx = int(safe_input("\nPilih nomor menu yang ingin diupdate: ")) - 1
        if idx < 0 or idx >= len(daftar):
            print("Pilihan tidak valid.")
            pause()
            return
    except:
        print("Input harus angka.")
        pause()
        return

    old_name, old_price = daftar[idx]
    print(f"\nMenu dipilih: {old_name.title()} - {currency(old_price)}")
    print("Apa yang ingin diupdate?")
    print("1. Ubah Nama Menu")
    print("2. Ubah Harga Menu")
    print("3. Ubah Nama & Harga")

    pilihan = safe_input("Pilihan: ")
    if pilihan == "1" or pilihan == "3":
        new_name = to_key(safe_input("Nama baru: "))
        if not new_name:
            print("Nama tidak boleh kosong.")
            pause()
            return
        if new_name in MENU and new_name != old_name:
            print("Nama menu sudah ada.")
            pause()
            return
        MENU[new_name] = MENU.pop(old_name)
        old_name = new_name

    if pilihan == "2" or pilihan == "3":
        try:
            new_price = int(safe_input("Harga baru: "))
            MENU[old_name] = new_price
        except:
            print("Harga harus angka.")
            pause()
            return

    save_data()
    print("Menu berhasil diperbarui!")
    pause()

def tampilkan_driver():
    header("DAFTAR DRIVER")
    for nama, info in DRIVERS.items():
        avg = sum(info.get("ratings", []))/len(info.get("ratings", [])) if info.get("ratings") else 0
        busy = "BUSY" if info.get("busy") else "FREE"
        print(f"- {nama.title():12} | Ongkir {currency(info['ongkir']):12} | ETA {info['eta_menit']}m | {info['status'].upper()} | {busy} | Avg {avg:.1f} | Bonus {currency(info.get('bonus',0))}")
    print("-"*60)

def tambah_driver():
    header("TAMBAH DRIVER")
    nama = to_key(safe_input("Nama driver: "))
    if not nama:
        print("Nama kosong.")
        return
    if nama in DRIVERS:
        print("Driver sudah ada.")
        return
    try:
        ongkir = int(safe_input("Ongkir: "))
        eta = int(safe_input("ETA (menit): "))
    except:
        print("Input harus angka.")
        return
    status = to_key(safe_input("Status (online/offline): "))
    if status not in ("online", "offline"):
        status = "offline"
    DRIVERS[nama] = {"ongkir": ongkir, "eta_menit": eta, "status": status, "busy": False, "ratings": [], "total_orders": 0, "bonus": 0, "pos": (0,0)}
    save_data()
    print("Driver ditambahkan.")

def update_driver_status():
    tampilkan_driver()
    nama = to_key(safe_input("Driver (nama): "))
    if nama not in DRIVERS:
        print("Driver tidak ada.")
        return
    st = to_key(safe_input("Status baru (online/offline): "))
    if st in ("online", "offline"):
        DRIVERS[nama]["status"] = st
        save_data()
        print("Status driver diperbarui.")
    else:
        print("Status tidak valid.")

def tambah_ke_keranjang(user_email):
    header("TAMBAH PESANAN")
    tampilkan_menu()
    nama = to_key(safe_input("Masukkan nama menu: "))
    if nama not in MENU:
        print("Menu tidak ditemukan.")
        return
    try:
        qty = int(safe_input("Jumlah: "))
        if qty <= 0:
            print("Jumlah harus > 0")
            return
    except:
        print("Jumlah harus angka.")
        return
    CART.append((nama, qty, MENU[nama]*qty))
    print(f"{nama.title()} x{qty} ditambahkan ke keranjang.")

def tampilkan_keranjang():
    header("KERANJANG")
    if not CART:
        print("Keranjang kosong.")
        return 0
    total = 0
    for i, (item, qty, price) in enumerate(CART, start=1):
        print(f"{i}. {item.title()} x{qty} = {currency(price)}")
        total += price
    print("-"*40)
    print(f"Total sementara: {currency(total)}")
    return total

def edit_keranjang():
    if not CART:
        print("Keranjang kosong.")
        return
    tampilkan_keranjang()
    try:
        idx = int(safe_input("Pilih nomor item untuk edit: ")) - 1
        if idx < 0 or idx >= len(CART):
            print("Index tidak valid.")
            return
    except:
        print("Input harus angka.")
        return
    print("1. Ubah menu\n2. Ubah jumlah\n3. Hapus item")
    pilih = safe_input("Pilihan: ")
    if pilih == "1":
        tampilkan_menu()
        new = to_key(safe_input("Nama menu baru: "))
        if new not in MENU:
            print("Menu tidak ada.")
            return
        qty = CART[idx][1]
        CART[idx] = (new, qty, MENU[new]*qty)
        print("Menu diperbarui.")
    elif pilih == "2":
        try:
            new_qty = int(safe_input("Jumlah baru: "))
            if new_qty <= 0:
                print("Jumlah harus >0.")
                return
            item = CART[idx][0]
            CART[idx] = (item, new_qty, MENU[item]*new_qty)
            print("Jumlah diperbarui.")
        except:
            print("Jumlah harus angka.")
    elif pilih == "3":
        CART.pop(idx)
        print("Item dihapus.")
    else:
        print("Pilihan tidak valid.")

def hapus_semua_keranjang():
    CART.clear()
    print("Semua item dihapus dari keranjang.")

def pilih_metode_pembayaran():
    print("Metode pembayaran: 1.DANA 2.GOPAY 3.BRI 4.COD")
    pilih = safe_input("Pilih (1-4): ")
    mapping = {"1":"DANA","2":"GOPAY","3":"BRI","4":"COD"}
    return mapping.get(pilih, "COD")

def auto_assign_driver():
    candidates = [(n,i) for n,i in DRIVERS.items() if i.get("status")=="online" and not i.get("busy")]
    if not candidates:
        return None, 0
    candidates.sort(key=lambda x: (x[1]["ongkir"], x[1]["eta_menit"]))
    return candidates[0][0], candidates[0][1]["ongkir"]

def estimasi_waktu(driver_name, total_qty):
    if driver_name not in DRIVERS:
        return 10
    base = DRIVERS[driver_name]["eta_menit"]
    extra = int(round(total_qty * 1.5))
    if "a" in driver_name: extra -= 1
    if "b" in driver_name: extra += 2
    return max(3, base + extra)

def checkout(user_email, user_name):
    global ORDER_COUNTER, ACTIVE_ORDER
    if not CART:
        print("Keranjang kosong. Tambahkan pesanan dulu.")
        return
    subtotal = tampilkan_keranjang()
    if subtotal == 0:
        return
    print("\nPilih driver: ketik 'auto' untuk auto-assign atau masukkan nama driver.")
    tampilkan_driver()
    pick = to_key(safe_input("Driver (nama/auto): "))
    if pick == "auto":
        driver_name, ongkir = auto_assign_driver()
        if not driver_name:
            print("Tidak ada driver tersedia.")
            return
    else:
        driver_name = pick
        if driver_name not in DRIVERS:
            print("Driver tidak ada.")
            return
        if DRIVERS[driver_name]["status"] != "online" or DRIVERS[driver_name]["busy"]:
            print("Driver tidak tersedia.")
            return
        ongkir = DRIVERS[driver_name]["ongkir"]
    metode = pilih_metode_pembayaran()
    dibayar = (metode != "COD")
    total_before = subtotal + ongkir
    print(f"\nSubtotal: {currency(subtotal)} | Ongkir {currency(ongkir)} | Total sebelum kupon: {currency(total_before)}")

    if user_email not in USERS or not isinstance(USERS[user_email], dict):
        USERS[user_email] = {"password": "", "used_coupons": [], "new_user_bonus": False}
    USERS[user_email].setdefault("used_coupons", [])
    USERS[user_email].setdefault("new_user_bonus", False)

    used_coupon = None
    total = total_before

    if total_before > 50000:
        yn = to_key(safe_input("Punya kupon? (y/n): "))
        if yn == "y":
            kode = safe_input("Masukkan kode kupon: ").upper()

            if kode in USERS[user_email]["used_coupons"]:
                print("Kupon ini sudah pernah kamu gunakan. Tidak bisa dipakai lagi.")
                total = total_before
            else:
                info = KUPON.get(kode)
                if info:
                    if info.get("type") == "ongkir":
                        ongkir = 0
                        total = subtotal + ongkir

                    elif info.get("type") == "pct":
                        pot = subtotal * info.get("val", 0) // 100
                        total = subtotal + ongkir - pot

                    used_coupon = kode
                    
                    USERS[user_email]["used_coupons"].append(kode)

                    if info.get("uses") is not None:
                        info["uses"] = max(0, info["uses"] - 1)
                        if info["uses"] == 0:
                            del KUPON[kode]

                    print(f"Kupon {kode} diterapkan.")
                    save_data()

                else:
                    print("Kupon tidak valid.")
                    total = total_before
    else:
        total = total_before
    print(f"Total yang harus dibayar: {currency(total)}")

    confirm_checkout = safe_input("Konfirmasi checkout? (y = lanjut / ketik 'cancel' untuk batal): ")
    if to_key(confirm_checkout) == "cancel" or to_key(confirm_checkout) != "y":
        print("Checkout dibatalkan. Kembali ke menu.")
        return

    if dibayar:
        while True:
            try:
                bayar_raw = safe_input("Masukkan nominal pembayaran (ketik 'cancel' untuk batal): ")
                if to_key(bayar_raw) == "cancel":
                    print("Pembayaran dibatalkan. Kembali ke menu.")
                    return
                bayar = int(bayar_raw)
                if bayar < total:
                    print(f"Uang kurang {currency(total-bayar)}.")
                    return
                change = bayar - total
                print(f"Pembayaran sukses. Kembali: {currency(change)}")
                break
            except:
                print("Nominal harus angka.")
    else:
        print("Pilihan COD: bayar di tempat pada saat penerimaan.")

    DRIVERS[driver_name]["busy"] = True
    DRIVERS[driver_name]["total_orders"] += 1
    items_copy = list(CART)
    order = {
        "order_id": ORDER_COUNTER,
        "pelanggan_email": user_email,
        "pelanggan_nama": user_name,
        "items": items_copy,
        "subtotal": subtotal,
        "ongkir": ongkir,
        "total": total,
        "driver": driver_name,
        "status": "Dalam Pengantaran",
        "kupon": used_coupon,
        "metode": metode,
        "dibayar": dibayar,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estimasi": estimasi_waktu(driver_name, sum(q for (_, q, _) in items_copy))
    }
    ORDER_COUNTER += 1
    RIWAYAT.setdefault(user_email, []).append(order)
    ACTIVE_ORDER = {"pelanggan_email": user_email, "order_id": order["order_id"]}
    CHATS[order["order_id"]] = []
    save_data()
    print(f"\nOrder #{order['order_id']} dibuat. Driver: {driver_name.title()}. Estimasi: {order['estimasi']} menit.")
    print("Memulai proses pengantaran (simulasi)...")
    time.sleep(0.3)
    print("Driver mengambil pesanan...")
    time.sleep(0.3)
    print("Dalam perjalanan...")
    time.sleep(0.3)
    print("Pesanan sampai (simulasi).")

    while True:
        try:
            rating_raw = safe_input(f"Berikan rating untuk {driver_name.title()} (1-5): ")
            rating = int(rating_raw)
            if 1 <= rating <= 5:
                DRIVERS[driver_name]["ratings"].append(rating)
                break
            else:
                print("Rating 1-5.")
        except:
            print("Masukkan angka.")
    DRIVERS[driver_name]["busy"] = False
    avg = sum(DRIVERS[driver_name]["ratings"]) / len(DRIVERS[driver_name]["ratings"]) if DRIVERS[driver_name]["ratings"] else 0
    if avg >= 4 and DRIVERS[driver_name]["total_orders"] >= 1:
        DRIVERS[driver_name]["bonus"] += 3000
        print(f"Driver {driver_name.title()} mendapat bonus Rp3000 (avg {avg:.1f}).")
        
    for o in RIWAYAT.get(user_email, []):
        if o["order_id"] == order["order_id"]:
            o["status"] = "Selesai"
            break
    CART.clear()
    ACTIVE_ORDER = None
    save_data()
    print("Pesanan selesai dan sudah tersimpan di riwayat.")
    pause()

def batalkan_pesanan(username=None):
    global ACTIVE_ORDER
    if username is None:
        header("PEMBATALAN (ADMIN)")
        if not ACTIVE_ORDER:
            print("Tidak ada pesanan aktif.")
            pause()
            return
        email = ACTIVE_ORDER["pelanggan_email"]
        order_id = ACTIVE_ORDER["order_id"]
        target = None
        for o in RIWAYAT.get(email, []):
            if o["order_id"] == order_id:
                target = o; break
        if not target:
            print("Order tidak ditemukan.")
            pause(); return
        confirm = to_key(safe_input(f"Batalkan order #{order_id} milik {email}? (y/n): "))
        if confirm != "y":
            print("Dibatalkan.")
            pause(); return
        d = target.get("driver")
        if d in DRIVERS:
            DRIVERS[d]["busy"] = False
            if DRIVERS[d]["total_orders"] > 0:
                DRIVERS[d]["total_orders"] -= 1
        target["status"] = "Dibatalkan"
        ACTIVE_ORDER = None
        save_data()
        print("Order dibatalkan oleh admin.")
        pause(); return
    header("PEMBATALAN (USER)")
    if username not in RIWAYAT or len(RIWAYAT[username]) == 0:
        print("Tidak ada riwayat/pesanan untuk dibatalkan.")
        pause(); return
    latest = RIWAYAT[username][-1]
    cancellable_states = ("Dalam Pengantaran","checkout","pending pembayaran","diproses","dimasak")
    if latest["status"] in ("Selesai","Dibatalkan"):
        print(f"Pesanan sudah {latest['status']}. Tidak bisa dibatalkan.")
        pause(); return
    if latest.get("status") not in cancellable_states:
        print(f"Status saat ini '{latest.get('status')}' tidak dapat dibatalkan.")
        pause(); return
    if latest.get("metode","").upper() != "COD" and latest.get("dibayar") is True:
        print("Pesanan sudah dibayar via non-COD, hubungi admin untuk pengembalian.")
        pause(); return
    confirm = to_key(safe_input(f"Batalkan order #{latest['order_id']}? (y/n): "))
    if confirm != "y":
        print("Pembatalan dibatalkan.")
        pause(); return
    d = latest.get("driver")
    if d in DRIVERS:
        DRIVERS[d]["busy"] = False
        if DRIVERS[d]["total_orders"] > 0:
            DRIVERS[d]["total_orders"] -= 1
    latest["status"] = "Dibatalkan"
    if ACTIVE_ORDER and ACTIVE_ORDER.get("pelanggan_email")==username and ACTIVE_ORDER.get("order_id")==latest.get("order_id"):
        ACTIVE_ORDER = None
    save_data()
    print("Pesanan berhasil dibatalkan.")
    pause()

def tracking_order(user_email):
    if user_email not in RIWAYAT or len(RIWAYAT[user_email])==0:
        print("Tidak ada riwayat pesanan.")
        pause(); return
    order = RIWAYAT[user_email][-1]
    print(f"Tracking Order #{order['order_id']} Status: {order.get('status')}")
    driver = order.get("driver")
    if not driver:
        print("Driver belum ditugaskan.")
        pause(); return
    eta = order.get("estimasi", 10)
    steps = 5
    for step in range(1, steps+1):
        pct = (step/steps)*100
        remaining = max(0, int(eta*(1 - step/steps)))
        print(f"[{driver.title()}] Progress: {int(pct)}% - Est. sisa {remaining} menit")
        time.sleep(0.2)
    print("Tracking selesai (simulasi).")
    pause()

def chat_with_driver(user_email):
    if user_email not in RIWAYAT or len(RIWAYAT[user_email])==0:
        print("Belum ada order untuk chat.")
        pause(); return
    order = RIWAYAT[user_email][-1]
    oid = order["order_id"]
    driver = order.get("driver")
    if not driver:
        print("Driver belum ditugaskan.")
        pause(); return
    header(f"CHAT - Order #{oid} dengan {driver.title()}")
    msgs = CHATS.get(oid, [])
    if msgs:
        print("--- Riwayat Chat ---")
        for sender, msg, ts in msgs:
            print(f"[{ts}] {sender}: {msg}")
    else:
        print("Belum ada pesan.")
    print("---------------------")
    while True:
        txt = safe_input("Ketik pesan (atau 'exit' untuk keluar): ")
        if to_key(txt) == "exit":
            break
        if txt:
            ts = datetime.now().strftime("%H:%M:%S")
            CHATS.setdefault(oid, []).append(("User", txt, ts))
            reply = random.choice([
                "Baik, saya segera mengambil pesanan.",
                "On my way!",
                "Permisi, saya sudah sampai di lokasi restoran.",
                "Mohon tunggu sebentar."
            ])
            time.sleep(0.2)
            CHATS[oid].append((driver.title(), reply, datetime.now().strftime("%H:%M:%S")))
            print(f"{driver.title()}: {reply}")
    pause()

def print_struk(user_email):
    if user_email not in RIWAYAT or len(RIWAYAT[user_email]) == 0:
        print("Belum ada riwayat.")
        pause(); return
    order = RIWAYAT[user_email][-1]
    lines = []
    lines.append("==== STRUK PESANAN ====")
    lines.append(f"Order ID : {order['order_id']}")
    lines.append(f"Tanggal  : {order.get('created_at')}")
    lines.append(f"Pelanggan: {order.get('pelanggan_nama')} ({user_email})")
    lines.append("-"*30)
    for item, qty, price in order['items']:
        lines.append(f"{item.title()} x{qty} = {currency(price)}")
    lines.append("-"*30)
    lines.append(f"Subtotal: {currency(order['subtotal'])}")
    lines.append(f"Ongkir  : {currency(order['ongkir'])}")
    lines.append(f"Total   : {currency(order['total'])}")
    lines.append(f"Driver  : {order.get('driver').title()}")
    lines.append(f"Metode  : {order.get('metode')}")
    lines.append(f"Status  : {order.get('status')}")
    lines.append("="*30)
    header("STRUK PESANAN")
    print("\n".join(lines))
    simpan = to_key(safe_input("Simpan struk ke file? (y/n): "))
    if simpan == "y":
        fname = f"struk_order_{order['order_id']}.txt"
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"Struk disimpan sebagai {fname}")
        except Exception as e:
            print("Gagal menyimpan struk:", e)
    pause()

def give_new_user_coupons(user):
    '''Berikan kupon otomatis saat user pertama kali daftar'''
    if user not in USERS:
        USERS[user] = {"password": "", "used_coupons": [], "new_user_bonus": False}
    if "used_coupons" not in USERS[user]:
        USERS[user]["used_coupons"] = []

    bonus = ["FREEONGKIR", "FIVEDISK"]

    if not USERS[user].get("new_user_bonus", False):
        USERS[user]["new_user_bonus"] = True
        print("\n Kamu mendapatkan kupon spesial untuk pengguna baru!")
        for k in bonus:
            if k in KUPON:
                print(f"- {k}")
        save_data()

def show_coupon_history(user):
    header("RIWAYAT KUPON YANG PERNAH DIPAKAI")

    if user not in USERS or "used_coupons" not in USERS[user] or len(USERS[user]["used_coupons"]) == 0:
        print("Belum ada kupon yang pernah dipakai.")
        pause()
        return

    print("Kupon yang sudah pernah kamu gunakan:")
    for idx, k in enumerate(USERS[user]["used_coupons"], 1):
        print(f"{idx}. {k}")

    print()
    pause()

def user_menu(user_email):
    user_name = user_email.split("@")[0]
    while True:
        header(f"USER MENU - {user_email}")
        print("1. Lihat Menu")
        print("2. Tambah Pesanan ke Keranjang")
        print("3. Lihat Keranjang")
        print("4. Edit Keranjang")
        print("5. Hapus Semua Keranjang")
        print("6. Checkout")
        print("7. Riwayat Pesanan")
        print("8. Tracking Pesanan (last order)")
        print("9. Chat dengan Driver (last order)")
        print("10. Print Struk (last order)")
        print("11. Batalkan Pesanan (COD saja, belum dibayar)")
        print("12. Riwayat Kupon")
        print("0. Logout")
        pilih = to_key(safe_input("Pilih: "))
        if pilih in ("1","lihat","menu","lihat menu"):
            tampilkan_menu(); pause()
        elif pilih in ("2","tambah","tambah pesanan","tambah keranjang"):
            tambah_ke_keranjang(user_email); pause()
        elif pilih in ("3","keranjang","lihat keranjang"):
            tampilkan_keranjang(); pause()
        elif pilih in ("4","edit","edit keranjang"):
            edit_keranjang(); pause()
        elif pilih in ("5","hapus semua","hapus semua keranjang"):
            hapus_semua_keranjang(); pause()
        elif pilih in ("6","checkout"):
            checkout(user_email, user_name)
        elif pilih in ("7","riwayat","riwayat pesanan"):
            header("RIWAYAT ANDA")
            for o in RIWAYAT.get(user_email, []):
                print(f"Order #{o['order_id']} - {o['status']} - {currency(o['total'])}")
            pause()
        elif pilih in ("8","tracking"):
            tracking_order(user_email)
        elif pilih in ("9","chat","chat driver"):
            chat_with_driver(user_email)
        elif pilih in ("10","struk","print struk"):
            print_struk(user_email)
        elif pilih in ("11","batalkan","batalkan pesanan"):
            batalkan_pesanan(username=user_email)
        elif pilih in ("12","kupon","riwayat kupon"):
            show_coupon_history(user_email)
        elif pilih in ("0","logout","keluar"):
            print("Logout..."); break
        else:
            print("Pilihan tidak valid."); pause()

def admin_menu(admin_email):
    while True:
        header("ADMIN MENU")
        print("1. Lihat Menu")
        print("2. Tambah Menu")
        print("3. Hapus Menu")
        print("4. Update Menu")
        print("5. Lihat Driver")
        print("6. Tambah Driver")
        print("7. Ubah Status Driver")
        print("8. Lihat Semua Pesanan (semua user)")
        print("9. Batalkan Active Order")
        print("0. Logout")
        pilih = to_key(safe_input("Pilih: "))
        if pilih in ("1","lihat menu"):
            tampilkan_menu(); pause()
        elif pilih in ("2","tambah menu"):
            tambah_menu_admin(); pause()
        elif pilih in ("3","hapus menu"):
            hapus_menu_admin(); pause()
        elif pilih == "4":
            update_menu_admin(); pause()
        elif pilih in ("5","lihat driver"):
            tampilkan_driver(); pause()
        elif pilih in ("6","tambah driver"):
            tambah_driver(); pause()
        elif pilih in ("7","ubah status"):
            update_driver_status(); pause()
        elif pilih in ("8","lihat pesanan"):
            header("SEMUA PESANAN")
            for email, orders in RIWAYAT.items():
                for o in orders:
                    print(f"User: {email} | Order #{o['order_id']} | Status: {o['status']} | Total: {currency(o['total'])}")
            pause()
        elif pilih in ("9","batalkan active"):
            batalkan_pesanan(None)
        elif pilih in ("0","logout"):
            print("Logout admin..."); break
        else:
            print("Pilihan tidak valid."); pause()

def main():
    load_data()
    while True:
        clear()
        header("SISTEM PEMESANAN - MAKANAN ONLINE")
        print("1. Login User")
        print("2. Daftar User")
        print("3. Login Admin")
        print("0. Keluar")
        pilih = safe_input("Pilih: ")
        if pilih == "1":
            user = login_user()
            if user:
                user_menu(user)
        elif pilih == "2":
            sign_up(); pause()
        elif pilih == "3":
            adm = login_admin()
            if adm:
                admin_menu(adm)
        elif pilih == "0":
            print("Terima Kasih telah menggunakan sistem!")
            save_data()
            break
        else:
            print("Pilihan tidak valid."); pause()

if __name__ == "__main__":

    main()

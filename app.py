import requests
import csv
import time
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import threading
import random
import re
import hashlib
import html
import math
import pyotp
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone 
from urllib.parse import urljoin, quote, unquote
from flask import Flask

# Bangladesh local time used for all profile daily/7-day statistics.
BD_TZ = timezone(timedelta(hours=6))

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = "9263597360:AAGFZRZzbtUerRrr1rd6295NxPY9BSYcleM"  # Add the new Telegram bot token here.
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 6800119501  # Add the new owner Telegram user ID here.
BOT_USERNAME = "IX NUMBER BOT"  # Filled automatically by getMe at startup.
DEVELOPER_LINK = "https://t.me/psycho_coder_PXN"  # Developer contact button in Support.
DB_FILE = "bot_data.json"

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id=\"5352694861990501856\">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id=\"5420130255174145507\">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id=\"5336944168944047463\">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id=\"5353032893096567467\">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id=\"5352861489541714456\">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id=\"5352721946054268944\">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id=\"5352597830089347330\">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id=\"5352877703043258544\">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id=\"5348469219761626211\">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id=\"5420396762189831222\">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id=\"6314258015734211084\">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id=\"5420155432272438703\">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id=\"5420517437885943844\">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id=\"5422557736330106570\">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id=\"5353001161878182134\">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id=\"5336972142066047577\">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id=\"5353022963132174959\">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id=\"5337132498965010628\">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id=\"5352862640592949843\">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id=\"5352922460897452503\">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id=\"5352552689983067014\">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id=\"5353027129250453493\">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5336972142066047577", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "6338935574967098253", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607",
    # Profile UI custom-emoji mappings. These IDs are stored in code, so restarts do not change them.
    "📩": "5337302974806922068",
    "💵": "6312344027983257537",
    "🏆": "5420396762189831222",
    "⏰": "5336983442125001376",
    "📆": "5352585194295564660"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "╔═══════════╗\n       📊 NUMBER BOT\n╚═══════════╝\n🚀 Welcome to Number & OTP Service\n━━━━━━━━━━━━\n✅ Choose an option below\nto continue using the bot.\n━━━━━━━━━━━━\n💎 Premium OTP Service", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 😒 WITHDRAWAL 》\n➖➖➖➖➖➖➖\n👋 Total Otp: {total_otp}\n➖➖➖➖➖➖➖\n🫂 Total Reffer :{total_ref}\n➖➖➖➖➖➖➖\n📅 BALANCE: {bal}৳\n➖➖➖➖➖➖➖\n🔐 MINIMUM: {min_w} ৳\n➖➖➖➖➖➖➖\nSELECT METHOD:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# Firebase Setup
# ==========================================
firebase_credentials_json = r"""
{
  "type": "service_account",
  "project_id": "stv-update",
  "private_key_id": "f389ad26944ec918fea51a1ff52bc04960d82940",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDGbHnZ6AJXpeDd\nF0Ki6gnMZmOfSGH8EyEIZXSngeRfBSefBk9VsfHFIX/zKost4ZGnzcs/1/CPxSCc\n8dhyrSQPmh2FfP6h9TbzMk2vOnyIGrRpbkpMbo6WUcWI2sqWdoKYPLJVj3FgL52Q\nrEVn9qAmsmC9PfDmJtrYe6rJjoIJ6FRuzxjKRPGyjfgjZ2PvZYCKBxULuZVX/HmX\npQnyb0bO+p++v6q3UvtIJgbKkb36TQoCzIbZTqNpRYKOrQKQnQQ9d9Zk/dRVrjzA\nW2y4fI8RRD8lTKYmWfsqDLoEL2n3+YUtmf9yzh13KuAdxo42Vh+q9Ok6rYe4AsY7\nTTYYINB9AgMBAAECggEAAYayNYSj9R1Wk38LO4WxcuLOb37W9PO+JF8IinK29L2R\n6M1t1hGvhd3ZBikiZQ5yT0gsJYgQKPd/rsnq1zQabh24II1boyn6ByZnirOPPu6/\nXTPyUaKbMpSkkqpl2u6NtCmgfmAeteflkJFfNdy19w9fdPdzo9BkjKna1zdQ4uB3\nMN/JcJoKepUZ3sRVd+4PWxbjnzp+eY9fExoSZoFTWbauCNzKr3Av7PS6nxq2R6BZ\nWCTmE2fBXfEiVkgDx2BYEomKoJhTnztfr+kc6xewUG2i94y1UReaDMfc07GZEXzw\nhWBSlERDqO3E8Ib4IJ4X9iCMhSFOr7tG0OfcQc5wAQKBgQDmSRfhzLQ0yeltvKDy\n9i7G4OFtpg3BZ3199jzSg4X03hV7c4Tr/a+u+DyP9gKfV4AkDREudpy2fB9OKV2w\nelsGxAj3+wfK2bekpvvKUIGMFCfua48Cso/UsXn+xK1SPXKli50WpezNEamn9cue\ngoX6b/LvKQa2zX2yUnTH+304fQKBgQDclJYnKH1cpF3vbLrJNTx081ou3VwGssvI\nkUMtdFjMEAEqecBAuwIxW+CJhkmQlqexp0CMSYhcKEdT/7QQoLKCFld1sC24KO33\nG1M+COtQtILP4ybMSqhgrmDxPAcOb0AFmTdM1zCBc9Vfw51NSWl6+9iMIlqMValm\n9i2PVB14AQKBgGxOfkv1gd++AupYp/39KPzicUOnsJqAuPXQJMUBlLQY61OXfjGb\nq9AH8jvnAU690YejGayXnpb5A6Q4Mlc5BKzG8EzpJL4T7Zoj6xI5EOS36hvpPGaR\nYrIvEmhvSfD+83fGlQg824WLRBa5tJ2FV8v0cPZofj7loLOIsmIH9tnlAoGABGHX\nUdPWGb8SNq18UH8EQnaLNh8jsuZecg+gvAhxsywmOcfNb/vHIV/n6BOI5px3nGns\nOF1Fnj8Wm66azzHCGh+DgU0Mu3nksGIUl0jqE+JiLuseXDSnf7Q3LNO6eCjxpqrS\nlG46AnhgptRmDaEFvXG/bZlJHzycbvU5Fn3fUAECgYBw7sQFDwxzR3KugPJsMO1O\ngUix7NdEooQ7Wln1gMbeKJrQI6GG0GIaJWUixFMTm4D7qZfXLWMhrRbS5LA6s4aN\njqZ4/vDeDmgh23Ks2BFSoOOhY6+tl7Op/nQTm/m7ebT53s7Y8RdKVqMdWVVj5MlU\nAjljMBxKZYrC5btuW3f7AA==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@stv-update.iam.gserviceaccount.com",
  "client_id": "109855355253980065263",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40stv-update.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}




"""

try:
    cred_dict = json.loads(firebase_credentials_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase Connected! (Full Sync Enabled)")
except Exception as e:
    print(f"❌ Firebase Error: {e}")
    db = None

local_users = {}
# Persist active Get Number sessions so Prefix toggle state survives bot restarts.
user_active_sessions = {}

bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "",  # Add the new OTP group/channel link here.
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    # Per-service/per-country OTP price overrides configured from DXA Control -> SET PRICE.
    # Structure: {"FACEBOOK": {"Togo": 0.5, "Benin": 0.4}}
    "service_country_prices": {},
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "",  # Add the new support link here.
    "sell_id_link": "",  # SELL ID link configured from Admin Panel.
    "sell_id_text": "💼 <b>SELL ID</b>\n\nTap the button below to sell your ID:",
    "shop_link": "",     # iX Shop link configured from Admin Panel.
    "shop_text": "🛒 <b>iX SHOP</b>\n\nTap the button below to open iX Shop:",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "", 
    "payout_group": "",
    
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "zenex_keys": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "zenex_services": {},
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    # OTP Group fixed custom-emoji slots. IDs are saved in bot_data.json.
    # Country already has a known Premium Emoji ID; the other four can be
    # filled once from the admin Premium Emoji setup without changing code.
    "otp_group_emojis": {
        "title": None,
        "number": None,
        "service": None,
        "country": "5336972142066047577",
        "sms": None
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}

FS_KEYS = [
    "admins", "panels", "fw_groups", "otp_link", "withdraw_on", 
    "min_withdraw", "otp_reward", "service_country_prices", "refer_reward", "cooldown", 
    "num_req", "num_share", "support_link", "sell_id_link", "sell_id_text", "shop_link", "shop_text", "w_methods", "w_group", "payout_group", "stex_keys", "voltx_keys", "search_countries", "stex_services", "voltx_services",
    "fj_on", "fj_channels", "voltx_auto", "stex_auto", "zenex_auto", "zenex_keys", "zenex_services", "zenex_search_countries",
    "otp_group_emojis", "premium_apps", "premium_flags"
]

number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
zenex_assigned_numbers = {}
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
ZENEX_BASE_URL = "https://api.zenexnetwork.com"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
# Panel-only event state: each distinct Number + Full SMS is tracked independently.
panel_processed_events = set()
# Stable per-event fingerprint so distinct SMS events for the same number can never collide.
panel_event_fingerprints = set()
# Panel OTP delivery state: keeps separate retry status for OTP Group and User Inbox.
panel_otp_group_delivered = set()
# Track historical pagination per panel so one API panel cannot block live OTP polling
# while sequentially scanning up to 20 pages on every cycle.
panel_pagination_cursors = {}
panel_otp_inbox_delivered = set()
recent_traffic = []
user_banned_cache = {}

# Active HTTP sessions for Auto Captcha Panels
panel_sessions = {}

# 🌟 sAjaxSource (AJAX/DataTable) এবং Fallback HTML Parser Helper Function
def fetch_cpt_panel_cdrs(p, session, check_url):
    res = session.get(check_url, timeout=15)
    html_text = res.text
    
    # সেশন শেষ হয়েছে বা লগইন পেজে রিডাইরেক্ট করেছে কি না তা চেক করা
    if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
        raise Exception("Session expired")
        
    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break
            
    results = []
    
    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2

    # ৫.১ যদি sAjaxSource AJAX লিংক পাওয়া যায়
    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl
            
        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"

        # Fetch the complete DataTables result set instead of relying on a single
        # server-side page. Some Auto Captcha panels ignore iDisplayLength=10000
        # and return only the currently paged rows; that can make a second OTP for
        # the same number invisible to the bot even though it is visible in the panel.
        ajax_headers = {
            "Referer": check_url,
            "X-Requested-With": "XMLHttpRequest"
        }

        def _ajax_page_url(start, length=1000):
            url = re.sub(r'([?&])iDisplayStart=\d+', r'\1iDisplayStart=' + str(start), full_ajax_url)
            url = re.sub(r'([?&])iDisplayLength=\d+', r'\1iDisplayLength=' + str(length), url)
            if "iDisplayStart=" not in url:
                url += ("&" if "?" in url else "?") + f"iDisplayStart={start}"
            if "iDisplayLength=" not in url:
                url += "&iDisplayLength=" + str(length)
            return url

        # Auto-Captcha/DataTables panels can serve CDR rows through GET or POST,
        # and different panel versions use legacy (iDisplayStart/iDisplayLength)
        # or modern (start/length) pagination.  Reproduce both request styles.
        seen_page_rows = set()
        total_records = None
        max_pages = 100
        page_length = 1000

        def _add_ajax_param(url, name, value):
            pattern = rf'([?&]){re.escape(name)}=[^&]*'
            if re.search(pattern, url, flags=re.I):
                return re.sub(pattern, rf'\1{name}={value}', url, flags=re.I)
            sep = '&' if '?' in url else '?'
            return f"{url}{sep}{name}={value}"

        def _request_datatable(url, start, length):
            """Return JSON rows from common DataTables GET/POST variants."""
            query_variants = []
            # Legacy DataTables GET.
            u1 = _ajax_page_url(start, length)
            query_variants.append(("GET", u1, None))
            # Modern DataTables GET.
            u2 = _add_ajax_param(full_ajax_url, 'start', start)
            u2 = _add_ajax_param(u2, 'length', length)
            query_variants.append(("GET", u2, None))
            # Modern/legacy POST.  A number of Auto Captcha panels configure
            # DataTables with sServerMethod='POST'; GET may otherwise return
            # only one/default record even though the browser table shows more.
            payload_legacy = {
                "sEcho": str(int(time.time() * 1000) % 100000000),
                "iDisplayStart": start,
                "iDisplayLength": length,
            }
            payload_modern = {
                "draw": 1,
                "start": start,
                "length": length,
            }
            query_variants.append(("POST", url, payload_legacy))
            query_variants.append(("POST", url, payload_modern))

            for method, request_url, payload in query_variants:
                try:
                    if method == "POST":
                        resp = session.post(
                            request_url,
                            data=payload,
                            headers=ajax_headers,
                            timeout=15,
                        )
                    else:
                        resp = session.get(
                            request_url,
                            headers=ajax_headers,
                            timeout=15,
                        )
                    data = resp.json()
                    rows = data.get("aaData", data.get("data", []))
                    if isinstance(rows, list) and rows:
                        total_value = data.get(
                            "iTotalDisplayRecords",
                            data.get("iTotalRecords", data.get("recordsTotal")),
                        )
                        return rows, total_value
                except Exception:
                    continue
            return [], None

        page_start = 0
        last_batch_signatures = set()
        for _page_no in range(max_pages):
            rows, total_value = _request_datatable(full_ajax_url, page_start, page_length)
            if not rows:
                break

            try:
                if total_value is not None:
                    total_records = int(total_value)
            except (TypeError, ValueError):
                pass

            new_rows = 0
            current_batch_signatures = set()
            for row_val in rows:
                # DataTables may return rows as arrays or dictionaries depending
                # on the panel version.  Keep the configured column indexes for
                # array rows and support named fields for object rows as well.
                if isinstance(row_val, dict):
                    lower_map = {str(k).strip().lower(): v for k, v in row_val.items()}
                    num_val = lower_map.get(n_col_name) or lower_map.get("number") or lower_map.get("phone") or lower_map.get("msisdn")
                    msg_val = lower_map.get(m_col_name) or lower_map.get("message") or lower_map.get("sms") or lower_map.get("content")
                    row_signature = repr(row_val)
                elif isinstance(row_val, list):
                    row_signature = repr(row_val)
                    if len(row_val) < max(n_idx, m_idx) + 1:
                        continue
                    num_val = row_val[n_idx] if 0 <= n_idx < len(row_val) else None
                    msg_val = row_val[m_idx] if 0 <= m_idx < len(row_val) else None
                else:
                    continue

                current_batch_signatures.add(row_signature)
                if row_signature not in seen_page_rows:
                    seen_page_rows.add(row_signature)
                    new_rows += 1

                clean_num = re.sub(r'\D', '', str(num_val or ''))
                clean_msg = str(msg_val or '').strip()
                if clean_num and 5 <= len(clean_num) <= 18 and clean_msg:
                    otp = extract_otp_code(clean_msg) or "NA"
                    item = {
                        "number": clean_num,
                        "message": clean_msg,
                        "otp": str(otp).strip(),
                    }
                    if item not in results:
                        results.append(item)

            if total_records is not None and page_start + len(rows) >= total_records:
                break
            if not new_rows or current_batch_signatures == last_batch_signatures:
                break
            last_batch_signatures = current_batch_signatures
            page_start += len(rows)

    else:
        # ৫.২ ডাইরেক্ট HTML টেবিল থেকে রিড করার ব্যাকআপ লজিক
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            
            final_n_idx = n_idx
            final_m_idx = m_idx
            
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text: final_n_idx = i
                if m_col_name in c_text: final_m_idx = i

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols): continue
                
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    
                    clean_num = re.sub(r'\D', '', num_text)
                    msg_text = str(msg_text or '').strip()
                    if clean_num and 5 <= len(clean_num) <= 18 and msg_text:
                        otp = extract_otp_code(msg_text) or "NA"
                        results.append({"number": clean_num, "message": msg_text, "otp": otp})
                            
    # Some Auto Captcha/DataTables panels visibly contain multiple SMS rows in the
    # HTML table even when the AJAX endpoint returns only the currently selected row/page.
    # Always merge those visible rows as an additional source. Exact duplicate events are
    # removed, while different OTP/SMS events for the same number are preserved.
    if s_ajax_source:
        try:
            soup_html = BeautifulSoup(html_text, 'html.parser')
            for table in soup_html.find_all('table'):
                rows = table.find_all('tr')
                if not rows:
                    continue
                final_n_idx = n_idx
                final_m_idx = m_idx
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text:
                        final_n_idx = i
                    if m_col_name in c_text:
                        final_m_idx = i

                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if all(c.name == 'th' for c in cols):
                        continue
                    if len(cols) > max(final_n_idx, final_m_idx):
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        clean_num = re.sub(r'\D', '', num_text)
                        msg_text = str(msg_text or '').strip()
                        if clean_num and 5 <= len(clean_num) <= 18 and msg_text:
                            otp = extract_otp_code(msg_text) or "NA"
                            results.append({"number": clean_num, "message": msg_text, "otp": str(otp).strip()})
        except Exception:
            pass

    # Final event-level de-duplication for Auto Captcha + HTML/AJAX merge.
    # The full SMS is part of the identity, so multiple OTPs on one number remain separate.
    if results:
        merged_results = []
        seen_events = set()
        for item in results:
            event_key = (
                str(item.get("number", "")).replace("+", "").replace(" ", "").replace("-", "").strip(),
                str(item.get("otp", "")).strip(),
                str(item.get("message", "")).strip(),
            )
            if event_key not in seen_events:
                seen_events.add(event_key)
                merged_results.append({
                    "number": event_key[0],
                    "message": event_key[2],
                    "otp": event_key[1],
                })
        results = merged_results

    return results, html_text

# Track active number sessions to expire them automatically
assigned_number_rates = {}
# Exact service selected by the user when a number is assigned.
assigned_number_services = {}
# Exact country label selected/uploaded for a number. Keeps custom labels
# such as "SYRIA 5" instead of canonical phone-prefix country names.
assigned_number_countries = {}
user_number_mode = {}  # chat_id -> "stock" (uploaded files) | "api" (Stex/Voltx/Zenex ranges)
api_country_hint = {}  # chat_id -> {"query": range, "country": selected country} for API (Stex/Voltx/Zenex) numbers
# Persistent owner mapping for numbers assigned through the generic number flow.
assigned_number_owners = {}

def _clean_assigned_number(value):
    return str(value or "").replace("+", "").replace(" ", "").replace("-", "").strip()

def _numbers_match(a, b):
    a = _clean_assigned_number(a)
    b = _clean_assigned_number(b)
    if not a or not b:
        return False
    return a == b or (len(a) >= 8 and len(b) >= 8 and (a.endswith(b[-8:]) or b.endswith(a[-8:])))

def get_assigned_service_for_number(number):
    """Get the exact Get Number service selected for this number."""
    for session_data in user_active_sessions.values():
        selected_service = session_data.get("service")
        if not selected_service:
            continue
        for active_num in session_data.get("nums", []):
            if _numbers_match(active_num, number):
                return str(selected_service).strip()
    for assigned_num, selected_service in assigned_number_services.items():
        if selected_service and _numbers_match(assigned_num, number):
            return str(selected_service).strip()
    return None

def get_assigned_country_for_number(number):
    """Get the exact country label selected/uploaded for this number."""
    for assigned_num, selected_country in assigned_number_countries.items():
        if selected_country and _numbers_match(assigned_num, number):
            return str(selected_country).strip()
    return None

def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, stex_assigned_numbers, voltx_assigned_numbers, zenex_assigned_numbers, processed_otps, assigned_number_rates, assigned_number_services, assigned_number_countries, assigned_number_owners, local_users, user_active_sessions
    
    loaded_from_local = False
    
    # ১. প্রথমে Local DB লোড করবে (এটি সবচেয়ে আপডেট থাকে, তাই Key হারাবে না)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key == "custom_messages":
                        for m_key, m_val in val.items():
                            bot_settings["custom_messages"][m_key] = m_val
                    else:
                        bot_settings[key] = val
                        
                for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                    if m_key not in bot_settings["custom_messages"]:
                        bot_settings["custom_messages"][m_key] = m_val
                        
                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", {})
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
                zenex_assigned_numbers = data.get("zenex_assigned_numbers", {})
                processed_otps = set(data.get("processed_otps", []))
                assigned_number_rates = data.get("assigned_number_rates", {})
                assigned_number_services = data.get("assigned_number_services", {})
                assigned_number_countries = data.get("assigned_number_countries", {})
                assigned_number_owners = data.get("assigned_number_owners", {})
                local_users = data.get("local_users", {}) or {}
                user_active_sessions = data.get("user_active_sessions", {}) or {}
                # JSON object keys are strings; normalize chat IDs back to their usual form.
                user_active_sessions = {int(k) if str(k).lstrip("-").isdigit() else k: v for k, v in user_active_sessions.items()}
                loaded_from_local = True
            print("✅ Local Stock/UI DB Loaded Successfully!")
        except Exception as e:
            print(f"❌ Error loading local DB: {e}")

    # ২. এরপর Firestore থেকে শুধু মিসিং ডেটা লোড করবে (Local ডেটা ওভাররাইট করবে না)
    if db:
        try:
            doc = db.collection('settings').document('bot_config').get()
            if doc.exists:
                fs_data = doc.to_dict()
                for k in FS_KEYS:
                    # যদি Local-এ ডেটা না থাকে (ফাঁকা থাকে), তবেই শুধুমাত্র Firestore থেকে আনবে
                    if k in fs_data and (not loaded_from_local or bot_settings.get(k) in [None, [], ""]):
                        bot_settings[k] = fs_data[k]
                print("✅ Config Synced with Firestore!")
            else:
                fs_data = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
                db.collection('settings').document('bot_config').set(fs_data)
                print("✅ Firestore Config Initialized!")
        except Exception as e:
            print(f"❌ Error loading from Firestore: {e}")

import atexit

_db_write_lock = threading.Lock()
_db_dirty_event = threading.Event()
_db_writer_guard = threading.Lock()
_db_writer_started = False

try:
    import orjson as _orjson   # optional: pip install orjson
except Exception:
    _orjson = None

def _write_local_db_now():
    """Write bot_data.json now: compact JSON (fast) + atomic replace (no corrupt file)."""
    with _db_write_lock:
        for _attempt in range(10):
            try:
                local_data = {
                    "bot_settings": dict(bot_settings),
                    "number_batches": dict(number_batches),
                    "used_numbers_list": list(used_numbers_list),
                    "total_uploaded_stats": total_uploaded_stats,
                    "total_assigned_stats": total_assigned_stats,
                    "recent_traffic": list(recent_traffic),
                    "stex_assigned_numbers": dict(stex_assigned_numbers),
                    "voltx_assigned_numbers": dict(voltx_assigned_numbers),
                    "zenex_assigned_numbers": dict(zenex_assigned_numbers),
                    "processed_otps": list(processed_otps),
                    "assigned_number_rates": dict(assigned_number_rates),
                    "assigned_number_services": dict(assigned_number_services),
                    "assigned_number_countries": dict(assigned_number_countries),
                    "assigned_number_owners": dict(assigned_number_owners),
                    "local_users": dict(local_users),
                    "user_active_sessions": dict(user_active_sessions)
                }
                tmp_file = DB_FILE + ".tmp"
                payload = None
                if _orjson is not None:
                    # orjson is ~5-10x faster than json, so the GIL is held far less.
                    try:
                        payload = _orjson.dumps(local_data, option=_orjson.OPT_NON_STR_KEYS)
                    except Exception:
                        payload = None
                if payload is not None:
                    with open(tmp_file, "wb") as f:
                        f.write(payload)
                else:
                    payload = json.dumps(local_data, separators=(",", ":"))
                    with open(tmp_file, "w", encoding='utf-8') as f:
                        f.write(payload)
                os.replace(tmp_file, DB_FILE)
                return
            except RuntimeError:
                # Another thread changed a dict while it was being read; retry.
                time.sleep(0.05)
            except Exception as e:
                print(f"❌ Local DB save error: {e}")
                return

def _db_writer_loop():
    while True:
        _db_dirty_event.wait()
        time.sleep(0.5)  # merge many quick save requests into one write
        _db_dirty_event.clear()
        _t0 = time.perf_counter()
        _write_local_db_now()
        _dur = time.perf_counter() - _t0
        if _dur > 0.3:
            print(f"[DB WRITE] bot_data.json save took {_dur:.2f}s")
        # json.dumps holds Python's GIL, so every button handler stalls while it runs.
        # Rest ~4x as long as the write took (max 10s): small DBs are unaffected,
        # big DBs stop being rewritten non-stop.
        time.sleep(min(15.0, max(1.0, _dur * 8)))

def _flush_local_db_on_exit():
    if _db_dirty_event.is_set():
        _db_dirty_event.clear()
        _write_local_db_now()

atexit.register(_flush_local_db_on_exit)

def save_local_db():
    """Request a save. The real write happens in a background thread (max ~0.5s later)
    so button clicks and OTP processing are never blocked by the big JSON write."""
    global _db_writer_started
    if not _db_writer_started:
        with _db_writer_guard:
            if not _db_writer_started:
                threading.Thread(target=_db_writer_loop, daemon=True).start()
                _db_writer_started = True
    _db_dirty_event.set()

def _sync_fs():
    if not db: return
    fs_data = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
    try:
        db.collection('settings').document('bot_config').set(fs_data)
    except: pass

_fs_sync_guard = threading.Lock()
_fs_sync_running = False
_fs_sync_pending = False

def _fs_sync_worker():
    """Single Firestore sync worker: many save_db() calls in a row become one write of the latest settings."""
    global _fs_sync_running, _fs_sync_pending
    while True:
        _sync_fs()
        with _fs_sync_guard:
            if _fs_sync_pending:
                _fs_sync_pending = False
                continue
            _fs_sync_running = False
            return

def save_db():
    global _fs_sync_running, _fs_sync_pending
    save_local_db()
    # Firestore sync runs in one background worker (not daemon, so a restart still lets it finish).
    with _fs_sync_guard:
        if _fs_sync_running:
            _fs_sync_pending = True
            return
        _fs_sync_running = True
    threading.Thread(target=_fs_sync_worker).start()

load_db()

# Keep OTP Group emoji slots available even when loading an older bot_data.json.
bot_settings.setdefault("otp_group_emojis", {})
for _slot in ("title", "number", "service", "country", "sms", "otp_code", "sms_rate"):
    bot_settings["otp_group_emojis"].setdefault(_slot, None)

_OLD_COUNTRY_EMOJI_ID = "5334590977837403844"
_NEW_COUNTRY_EMOJI_ID = "5336972142066047577"
_REQUESTED_OTP_TITLE_EMOJI_ID = "6053061091456457277"
_REQUESTED_OTP_NUMBER_EMOJI_ID = "6246967624941442448"
_REQUESTED_OTP_SERVICE_EMOJI_ID = "6053063247530039664"
_REQUESTED_INBOX_OTP_TITLE_EMOJI_ID = "5452162237231804831"

# Only populate defaults if a slot is empty — never overwrite admin customizations on restart.
_otp_defaults_changed = False
if not bot_settings["otp_group_emojis"].get("country") or bot_settings["otp_group_emojis"].get("country") == _OLD_COUNTRY_EMOJI_ID:
    bot_settings["otp_group_emojis"]["country"] = _NEW_COUNTRY_EMOJI_ID
    _otp_defaults_changed = True
if not bot_settings["otp_group_emojis"].get("title"):
    bot_settings["otp_group_emojis"]["title"] = _REQUESTED_OTP_TITLE_EMOJI_ID
    _otp_defaults_changed = True
if not bot_settings["otp_group_emojis"].get("number"):
    bot_settings["otp_group_emojis"]["number"] = _REQUESTED_OTP_NUMBER_EMOJI_ID
    _otp_defaults_changed = True
if not bot_settings["otp_group_emojis"].get("service"):
    bot_settings["otp_group_emojis"]["service"] = _REQUESTED_OTP_SERVICE_EMOJI_ID
    _otp_defaults_changed = True
if _otp_defaults_changed:
    save_db()

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session() # Reuse Telegram HTTPS connections for lower latency.
# Keep a pool of reusable connections so concurrent OTP forwards do not queue
# behind a single connection. Retries stay disabled to avoid duplicate messages.
_tg_adapter = requests.adapters.HTTPAdapter(
    pool_connections=20,
    pool_maxsize=50,
    max_retries=0,
    pool_block=False,
)
tg_session.mount("https://", _tg_adapter)

def _timed_api_get(url, headers=None, timeout=10, label="API"):
    """Diagnostic wrapper: log API latency without printing URLs, tokens, or OTP text."""
    started = time.perf_counter()
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        elapsed = time.perf_counter() - started
        if elapsed > 1.0 or response.status_code != 200:
            print(f"[OTP TIMING][API] source={label} elapsed={elapsed:.3f}s status={response.status_code}")
        return response
    except Exception as exc:
        elapsed = time.perf_counter() - started
        print(f"[OTP TIMING][API ERROR] source={label} elapsed={elapsed:.3f}s error={type(exc).__name__}")
        raise

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    started = time.perf_counter()
    is_polling = method.split("?", 1)[0] == "getUpdates"
    try:
        # Telegram long polling can wait 50 seconds; the HTTP timeout must be longer.
        res = tg_session.post(url, json=payload, timeout=65 if is_polling else 15)
        elapsed = time.perf_counter() - started
        if is_polling:
            if res.status_code != 200:
                print(f"[TELEGRAM POLLING] elapsed={elapsed:.3f}s status={res.status_code}")
        elif method == "sendMessage":
            if elapsed > 1.0 or res.status_code != 200:
                chat_id = (payload or {}).get("chat_id", "unknown")
                print(f"[OTP TIMING][TELEGRAM] method=sendMessage chat={chat_id} elapsed={elapsed:.3f}s status={res.status_code}")
        try:
            data = res.json()
        except ValueError:
            print(f"[TELEGRAM API ERROR] method={method.split('?', 1)[0]} invalid_json status={res.status_code}")
            return {}
        if not data.get("ok"):
            # Avoid logging the full URL because it contains the bot token.
            print(f"[TELEGRAM API ERROR] method={method.split('?', 1)[0]} status={res.status_code} description={data.get('description', 'Unknown error')}")
        return data
    except Exception as e:
        elapsed = time.perf_counter() - started
        method_name = method.split("?", 1)[0]
        print(f"[TELEGRAM REQUEST ERROR] method={method_name} elapsed={elapsed:.3f}s error={type(e).__name__}")
        return {}

def normalize_withdrawal_group_target(value):
    """Convert public Telegram group links to Bot API targets.

    Private invite links cannot be used as sendMessage chat_id; those require
    the group's numeric chat ID (usually -100...).
    """
    target = str(value or "").strip()
    if not target:
        return ""
    target = target.rstrip("/")
    if target.startswith(("https://t.me/", "http://t.me/")):
        path = target.split("t.me/", 1)[1].split("?", 1)[0].strip("/")
        if path.startswith(("+", "joinchat/")):
            return ""
        # Public group/channel URL: t.me/groupname -> @groupname
        if path and "/" not in path and path not in {"", "c"}:
            return "@" + path.lstrip("@")
        return ""
    if target.startswith("t.me/"):
        return normalize_withdrawal_group_target("https://" + target)
    if target.startswith("@"):
        return target
    if target.lstrip("-").isdigit():
        try:
            return int(target)
        except (TypeError, ValueError):
            return ""
    return ""

def download_telegram_file(file_id, retries=3):
    """Download a Telegram file with a dedicated session, timeouts + retries.
    Returns (content_text, error_message)."""
    last_err = None
    with requests.Session() as dl_session:
        for attempt in range(1, retries + 1):
            try:
                r = dl_session.get(f"{BASE_URL}/getFile", params={"file_id": file_id}, timeout=(10, 20))
                info = r.json()
                if not info.get("ok"):
                    desc = str(info.get("description", "getFile failed"))
                    if "too big" in desc.lower():
                        return None, "File is too large (Telegram Bot API limit is 20 MB)."
                    raise RuntimeError(desc)
                file_path = info["result"]["file_path"]
                fr = dl_session.get(f"{FILE_URL}{file_path}", timeout=(10, 90))
                fr.raise_for_status()
                return fr.content.decode("utf-8-sig", errors="replace"), None
            except Exception as e:
                last_err = e
                print(f"[FILE DOWNLOAD] attempt {attempt}/{retries} failed: {type(e).__name__}: {e}")
                time.sleep(0.5 * attempt)
    print(f"[FILE DOWNLOAD] gave up: {last_err}")
    return None, str(last_err or "Unknown download error")

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    if parse_mode == "HTML" and text:
        text = apply_bot_fonts(text)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup:
        payload["reply_markup"] = style_reply_markup(reply_markup)
    result = api_call("sendMessage", payload)

    # If generated HTML contains an invalid Telegram entity, retry this same
    # message as plain text so a formatting issue cannot block OTP delivery.
    if (not result.get("ok", False)
            and parse_mode == "HTML"
            and "ENTITY_TEXT_INVALID" in str(result.get("description", ""))):
        plain_text = re.sub(r"<[^>]*>", "", str(text or ""))
        plain_text = html.unescape(plain_text)
        retry_payload = dict(payload)
        retry_payload["text"] = plain_text
        retry_payload.pop("parse_mode", None)
        result = api_call("sendMessage", retry_payload)
        if result.get("ok", False):
            print(f"[Telegram sendMessage] HTML entity fallback succeeded for chat={chat_id}")

    # Keep Telegram errors visible instead of silently losing OTP messages.
    if not result.get("ok", False):
        print(f"[Telegram sendMessage ERROR] chat={chat_id}: {result.get('description', result)}")
    return result

def send_otp_to_groups(message_text, otp):
    """Send one OTP to all configured groups concurrently; return each result."""
    groups = list(bot_settings.get("fw_groups", []) or [])
    if not groups:
        return []

    def _send_one(fw):
        try:
            result = send_message(
                fw["chat_id"], message_text,
                reply_markup=build_fw_otp_keyboard(otp, fw),
            )
            return fw, result
        except Exception as exc:
            print(f"[Telegram OTP forward ERROR] chat={fw.get('chat_id')}: {exc}")
            return fw, {}

    if len(groups) == 1:
        return [_send_one(groups[0])]
    with ThreadPoolExecutor(max_workers=min(8, len(groups))) as executor:
        return list(executor.map(_send_one, groups))

# Post-send bookkeeping (Firestore balance / total OTP / stats) runs here, in order,
# on ONE worker so it can never delay the user's inbox message.
_otp_accounting_executor = ThreadPoolExecutor(max_workers=1)

def send_otp_to_groups_async(message_text, otp):
    """Fire-and-forget OTP Group send, so group delivery never delays the user's inbox."""
    def _run():
        try:
            send_otp_to_groups(message_text, otp)
        except Exception as exc:
            print(f"[Telegram OTP forward ERROR] {exc}")
    threading.Thread(target=_run, daemon=True).start()

def _account_otp_in_background(owner_id, reward):
    def _run(_uid=owner_id, _rw=reward):
        try:
            if _rw > 0:
                update_balance(_uid, _rw)
            increment_total_otps(_uid)
            record_otp_stats(_uid, _rw)
        except Exception as exc:
            print(f"[OTP accounting ERROR] user={_uid}: {exc}")
    _otp_accounting_executor.submit(_run)

def deliver_inbox_otp_fast(owner_id, otp, num, display_num, app_full_name, iso, prem_app_html):
    """Send the OTP to the user's inbox FIRST; do balance/stat writes afterwards in background."""
    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
    reward = float(_get_assigned_number_reward(num))
    # Built BEFORE update_balance(): _format_inbox_otp_message already adds this OTP's reward.
    inbox_msg = _format_inbox_otp_message(display_num, app_full_name, iso, owner_id, prem_app_html)
    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
    _account_otp_in_background(owner_id, reward)

def build_fw_otp_keyboard(otp, fw):
    """Build only the configured custom URL buttons for the OTP group.

    A malformed custom URL must not prevent the OTP message itself from
    reaching the forward group. Invalid legacy button URLs are skipped.
    """
    # The OTP is displayed in the message body; do not create a Copy button.
    kb = []

    temp_row = []
    styles = ["danger", "success", "primary"]
    for i, btn in enumerate(fw.get("buttons", []) or []):
        btn_text = str(btn.get("text", "")).strip()
        btn_url = str(btn.get("url", "")).strip()

        # Telegram inline URL buttons require a valid URL.
        if not btn_text or not (btn_url.startswith("https://") or
                                 btn_url.startswith("http://") or
                                 btn_url.startswith("tg://")):
            print(f"[OTP BUTTON SKIPPED] Invalid URL for '{btn_text}': {btn_url}")
            continue

        b_obj = {"text": btn_text, "url": btn_url, "style": styles[i % 3]}

        # Requested Premium icons for these OTP Group buttons.
        # URL/callback behavior is preserved exactly; only the icon changes.
        requested_button_icons = {
            "GET NUMBER": "5217824874487101321",
            "CHANNEL": "5278256077954105203",
        }
        # Match the configured button by its label even if the saved label
        # contains an ordinary emoji (e.g. "🚀 GET NUMBER ↗"). Replace that
        # ordinary leading icon with Telegram's premium button icon while
        # preserving the original URL and all button behavior.
        btn_upper = btn_text.upper()
        matched_label = None
        if "GET NUMBER" in btn_upper:
            matched_label = "GET NUMBER"
        elif "CHANNEL" in btn_upper:
            matched_label = "CHANNEL"
        icon_id = requested_button_icons.get(matched_label) or btn.get("icon_custom_emoji_id")
        if matched_label:
            b_obj["text"] = matched_label
        if icon_id:
            b_obj["icon_custom_emoji_id"] = str(icon_id)
        temp_row.append(b_obj)
        if len(temp_row) == 2:
            kb.append(temp_row)
            temp_row = []

    if temp_row:
        kb.append(temp_row)
    return {"inline_keyboard": kb}

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = style_reply_markup(reply_markup)
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    if parse_mode == "HTML" and text:
        text = apply_bot_fonts(text)
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = style_reply_markup(reply_markup)
    return api_call("editMessageText", payload)

def edit_message_reply_markup(chat_id, message_id, reply_markup):
    """Edit only the inline keyboard without changing the message text."""
    return api_call("editMessageReplyMarkup", {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": style_reply_markup(reply_markup)
    })

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass

# 🌟 Local User List to completely remove Firebase Read Costs!
all_known_users = set()

def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users = set(json.load(f))
        if not all_known_users and db:
            for doc in db.collection('users').select([]).stream():
                all_known_users.add(doc.id)
            with open("users_list.json", "w") as f:
                json.dump(list(all_known_users), f)
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        # 🌟 Non-blocking background save (Prevents lag)
        threading.Thread(target=_save_users_list, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id):
    success = 0
    failed = 0
    users = list(all_known_users)
    
    # 🌟 Dedicated Connection Pool for Broadcast (Fixes Port Exhaustion & Network Lag)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except:
            failed += 1
        time.sleep(0.035) # Safe speed (28 msgs/sec) to prevent Telegram Ban
        
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}"))

_BOLD_SERIF_TRANS = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "".join(chr(0x1D400 + i) for i in range(26)) + "".join(chr(0x1D41A + i) for i in range(26))
)
_SANS_BOLD_ITALIC_TRANS = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "".join(chr(0x1D63C + i) for i in range(26)) + "".join(chr(0x1D656 + i) for i in range(26))
)
_FONT_SKIP_RE = re.compile(
    r'(<tg-emoji\b[^>]*>.*?</tg-emoji>|<code>.*?</code>|<pre>.*?</pre>|<[^>]+>|https?://\S+|tg://\S+|@[A-Za-z0-9_]+|\{[A-Za-z0-9_]+\}|&[A-Za-z0-9#]+;)',
    re.DOTALL | re.IGNORECASE
)
_REVERSE_BOT_FONT_TRANS = str.maketrans(
    "".join(chr(0x1D400 + i) for i in range(26))
    + "".join(chr(0x1D41A + i) for i in range(26))
    + "".join(chr(0x1D63C + i) for i in range(26))
    + "".join(chr(0x1D656 + i) for i in range(26)),
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" * 2
)

def normalize_bot_font(text):
    """Convert styled button/command text back to plain ASCII for command matching."""
    if not text:
        return str(text)
    return str(text).translate(_REVERSE_BOT_FONT_TRANS)

def style_reply_markup(reply_markup):
    """Apply Bold Serif font to all ReplyKeyboard and InlineKeyboard button labels."""
    if not isinstance(reply_markup, dict):
        return reply_markup
    styled = dict(reply_markup)
    for key in ("inline_keyboard", "keyboard"):
        rows = reply_markup.get(key)
        if not isinstance(rows, list):
            continue
        new_rows = []
        for row in rows:
            if not isinstance(row, list):
                new_rows.append(row)
                continue
            new_row = []
            for btn in row:
                if isinstance(btn, dict):
                    b = dict(btn)
                    if "text" in b and b["text"]:
                        b["text"] = str(b["text"]).translate(_BOLD_SERIF_TRANS)
                    new_row.append(b)
                else:
                    new_row.append(btn)
            new_rows.append(new_row)
        styled[key] = new_rows
    return styled

def apply_bot_fonts(text):
    """Apply Bold Serif (𝐄𝐗𝐀𝐌𝐏𝐋𝐄 𝐅𝐎𝐍𝐓) to <b> headings and Sans Bold Italic (𝙀𝙓𝘼𝙈𝙋𝙇𝙀 𝙁𝙊𝙉𝙏) to body text."""
    if not text:
        return str(text)
    parts = _FONT_SKIP_RE.split(str(text))
    in_bold = False
    out = []
    for part in parts:
        if not part:
            continue
        low = part.lower()
        if low in ("<b>", "<strong>"):
            in_bold = True
            out.append(part)
        elif low in ("</b>", "</strong>"):
            in_bold = False
            out.append(part)
        elif _FONT_SKIP_RE.fullmatch(part):
            out.append(part)
        else:
            out.append(part.translate(_BOLD_SERIF_TRANS if in_bold else _SANS_BOLD_ITALIC_TRANS))
    return "".join(out)

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id=\"{prem_id}\">{normal_emj}</tg-emoji>')
    return apply_bot_fonts("".join(parts))

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id=\"{eid}\">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

# Fallback country calling-code database.
# The bot first uses premium_flags (so existing custom Telegram emojis are preserved),
# then falls back to this map when a code is missing from the database/settings.
FALLBACK_COUNTRY_CODES = {
    "20": ("EG", "Egypt"), "27": ("ZA", "South Africa"),
    "30": ("GR", "Greece"), "31": ("NL", "Netherlands"), "32": ("BE", "Belgium"),
    "33": ("FR", "France"), "34": ("ES", "Spain"), "36": ("HU", "Hungary"),
    "39": ("IT", "Italy"), "40": ("RO", "Romania"), "41": ("CH", "Switzerland"),
    "43": ("AT", "Austria"), "44": ("GB", "United Kingdom"), "45": ("DK", "Denmark"),
    "46": ("SE", "Sweden"), "47": ("NO", "Norway"), "48": ("PL", "Poland"),
    "49": ("DE", "Germany"), "51": ("PE", "Peru"), "52": ("MX", "Mexico"),
    "53": ("CU", "Cuba"), "54": ("AR", "Argentina"), "55": ("BR", "Brazil"),
    "56": ("CL", "Chile"), "57": ("CO", "Colombia"), "58": ("VE", "Venezuela"),
    "60": ("MY", "Malaysia"), "61": ("AU", "Australia"), "62": ("ID", "Indonesia"),
    "63": ("PH", "Philippines"), "64": ("NZ", "New Zealand"), "65": ("SG", "Singapore"),
    "66": ("TH", "Thailand"), "81": ("JP", "Japan"), "82": ("KR", "South Korea"),
    "84": ("VN", "Vietnam"), "86": ("CN", "China"), "90": ("TR", "Turkey"),
    "91": ("IN", "India"), "92": ("PK", "Pakistan"), "93": ("AF", "Afghanistan"),
    "94": ("LK", "Sri Lanka"), "95": ("MM", "Myanmar"), "98": ("IR", "Iran"),
    "211": ("SS", "South Sudan"), "212": ("MA", "Morocco"), "213": ("DZ", "Algeria"),
    "216": ("TN", "Tunisia"), "218": ("LY", "Libya"), "220": ("GM", "Gambia"),
    "221": ("SN", "Senegal"), "222": ("MR", "Mauritania"), "223": ("ML", "Mali"),
    "224": ("GN", "Guinea"), "225": ("CI", "Cote d'Ivoire"), "226": ("BF", "Burkina Faso"),
    "227": ("NE", "Niger"), "228": ("TG", "Togo"), "229": ("BJ", "Benin"),
    "230": ("MU", "Mauritius"), "231": ("LR", "Liberia"), "232": ("SL", "Sierra Leone"),
    "233": ("GH", "Ghana"), "234": ("NG", "Nigeria"), "235": ("TD", "Chad"),
    "236": ("CF", "Central African Republic"), "237": ("CM", "Cameroon"),
    "238": ("CV", "Cape Verde"), "239": ("ST", "Sao Tome and Principe"),
    "240": ("GQ", "Equatorial Guinea"), "241": ("GA", "Gabon"), "242": ("CG", "Republic of the Congo"),
    "243": ("CD", "Democratic Republic of the Congo"), "244": ("AO", "Angola"),
    "245": ("GW", "Guinea-Bissau"), "246": ("IO", "British Indian Ocean Territory"),
    "248": ("SC", "Seychelles"), "249": ("SD", "Sudan"), "250": ("RW", "Rwanda"),
    "251": ("ET", "Ethiopia"), "252": ("SO", "Somalia"), "253": ("DJ", "Djibouti"),
    "254": ("KE", "Kenya"), "255": ("TZ", "Tanzania"), "256": ("UG", "Uganda"),
    "257": ("BI", "Burundi"), "258": ("MZ", "Mozambique"), "260": ("ZM", "Zambia"),
    "261": ("MG", "Madagascar"), "262": ("RE", "Reunion"), "263": ("ZW", "Zimbabwe"),
    "264": ("NA", "Namibia"), "265": ("MW", "Malawi"), "266": ("LS", "Lesotho"),
    "267": ("BW", "Botswana"), "268": ("SZ", "Eswatini"), "269": ("KM", "Comoros"),
    "290": ("SH", "Saint Helena"), "291": ("ER", "Eritrea"), "297": ("AW", "Aruba"),
    "298": ("FO", "Faroe Islands"), "299": ("GL", "Greenland"), "350": ("GI", "Gibraltar"),
    "351": ("PT", "Portugal"), "352": ("LU", "Luxembourg"), "353": ("IE", "Ireland"),
    "354": ("IS", "Iceland"), "355": ("AL", "Albania"), "356": ("MT", "Malta"),
    "357": ("CY", "Cyprus"), "358": ("FI", "Finland"), "359": ("BG", "Bulgaria"),
    "370": ("LT", "Lithuania"), "371": ("LV", "Latvia"), "372": ("EE", "Estonia"),
    "373": ("MD", "Moldova"), "374": ("AM", "Armenia"), "375": ("BY", "Belarus"),
    "376": ("AD", "Andorra"), "377": ("MC", "Monaco"), "378": ("SM", "San Marino"),
    "380": ("UA", "Ukraine"), "381": ("RS", "Serbia"), "382": ("ME", "Montenegro"),
    "383": ("XK", "Kosovo"), "385": ("HR", "Croatia"), "386": ("SI", "Slovenia"),
    "387": ("BA", "Bosnia and Herzegovina"), "389": ("MK", "North Macedonia"),
    "420": ("CZ", "Czech Republic"), "421": ("SK", "Slovakia"), "423": ("LI", "Liechtenstein"),
    "500": ("FK", "Falkland Islands"), "501": ("BZ", "Belize"), "502": ("GT", "Guatemala"),
    "503": ("SV", "El Salvador"), "504": ("HN", "Honduras"), "505": ("NI", "Nicaragua"),
    "506": ("CR", "Costa Rica"), "507": ("PA", "Panama"), "509": ("HT", "Haiti"),
    "590": ("GP", "Guadeloupe"), "591": ("BO", "Bolivia"), "592": ("GY", "Guyana"),
    "593": ("EC", "Ecuador"), "594": ("GF", "French Guiana"), "595": ("PY", "Paraguay"),
    "596": ("MQ", "Martinique"), "597": ("SR", "Suriname"), "598": ("UY", "Uruguay"),
    "599": ("CW", "Curacao"), "670": ("TL", "Timor-Leste"), "673": ("BN", "Brunei"),
    "674": ("NR", "Nauru"), "675": ("PG", "Papua New Guinea"), "676": ("TO", "Tonga"),
    "677": ("SB", "Solomon Islands"), "678": ("VU", "Vanuatu"), "679": ("FJ", "Fiji"),
    "680": ("PW", "Palau"), "681": ("WF", "Wallis and Futuna"), "682": ("CK", "Cook Islands"),
    "683": ("NU", "Niue"), "685": ("WS", "Samoa"), "686": ("KI", "Kiribati"),
    "687": ("NC", "New Caledonia"), "688": ("TV", "Tuvalu"), "689": ("PF", "French Polynesia"),
    "690": ("TK", "Tokelau"), "691": ("FM", "Micronesia"), "692": ("MH", "Marshall Islands"),
    "850": ("KP", "North Korea"), "852": ("HK", "Hong Kong"), "853": ("MO", "Macau"),
    "855": ("KH", "Cambodia"), "856": ("LA", "Laos"), "880": ("BD", "Bangladesh"),
    "886": ("TW", "Taiwan"), "960": ("MV", "Maldives"), "961": ("LB", "Lebanon"),
    "962": ("JO", "Jordan"), "963": ("SY", "Syria"), "964": ("IQ", "Iraq"),
    "965": ("KW", "Kuwait"), "966": ("SA", "Saudi Arabia"), "967": ("YE", "Yemen"),
    "968": ("OM", "Oman"), "970": ("PS", "Palestine"), "971": ("AE", "United Arab Emirates"),
    "972": ("IL", "Israel"), "973": ("BH", "Bahrain"), "974": ("QA", "Qatar"),
    "975": ("BT", "Bhutan"), "976": ("MN", "Mongolia"), "977": ("NP", "Nepal"),
    "992": ("TJ", "Tajikistan"), "993": ("TM", "Turkmenistan"), "994": ("AZ", "Azerbaijan"),
    "995": ("GE", "Georgia"), "996": ("KG", "Kyrgyzstan"), "998": ("UZ", "Uzbekistan")
}

def _iso_to_flag(iso):
    iso = str(iso or "").upper()
    if len(iso) != 2 or not iso.isalpha():
        return "🌍"
    return "".join(chr(127397 + ord(c)) for c in iso)

def _fallback_country_for_number(num):
    clean = re.sub(r"\D", "", str(num or ""))
    for code in sorted(FALLBACK_COUNTRY_CODES, key=len, reverse=True):
        if clean.startswith(code):
            iso, name = FALLBACK_COUNTRY_CODES[code]
            return _iso_to_flag(iso), iso, None, name
    return "🌍", "XX", None, "Unknown"

def get_flag_info_from_num(num):
    clean = re.sub(r"\D", "", str(num or ""))
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data.get("char", "🌍"), data.get("iso", "XX"), data.get("id")
    return _fallback_country_for_number(clean)[:3]

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_premium_flag_for_number(num):
    """Return the configured premium flag data for a number, or None if no premium flag is configured."""
    clean = re.sub(r"\D", "", str(num or ""))
    for code in sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True):
        code = str(code)
        if clean.startswith(code):
            data = bot_settings["premium_flags"].get(code) or {}
            # A premium flag is considered active only when its custom emoji ID exists.
            if data.get("id"):
                return data
            return None
    return None

def get_flag_info_html(num_or_iso, return_full_name=False):
    value = str(num_or_iso or "").strip()
    if len(value) == 2 and value.isalpha():
        iso = value.upper()
        for code, data in bot_settings.get("premium_flags", {}).items():
            if str(data.get("iso", "")).upper() == iso:
                char = data.get("char") or _iso_to_flag(iso)
                name = data.get("name", iso)
                if return_full_name: return name
                return _premium_emoji_html(data, char)
        for _, (f_iso, name) in FALLBACK_COUNTRY_CODES.items():
            if f_iso == iso:
                if return_full_name: return name
                return _iso_to_flag(iso)
        if return_full_name: return iso
        return "🌍"

    char, iso, eid = get_flag_info_from_num(value)
    if return_full_name:
        for code, data in bot_settings.get("premium_flags", {}).items():
            clean = re.sub(r"\D", "", value)
            if clean.startswith(code):
                return data.get("name", iso)
        return _fallback_country_for_number(value)[3]

    clean_value = re.sub(r"\D", "", value)
    for code, data in bot_settings.get("premium_flags", {}).items():
        if clean_value.startswith(str(code)) and data.get("id") == eid:
            return _premium_emoji_html(data, char)
    if eid:
        return f'<tg-emoji emoji-id=\"{eid}\">{char}</tg-emoji>'
    return char

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    if len(clean) > 6: return f"{clean[:3]}DXA{clean[-3:]}"
    elif len(clean) > 2: return f"{clean[:1]}DXA{clean[-1:]}"
    return clean


OTP_GROUP_SLOTS = {
    "title": {
        "label": "Title Header",
        "btn": "🏷 Title Header",
        "fallback": "✉️",
        "where": "কার্ডের একদম উপরে দুই পাশে ([emoji] 🆂🅼🆂 🆁🅲🆅 [emoji])"
    },
    "number": {
        "label": "Number Row",
        "btn": "📱 Number Row",
        "fallback": "📱",
        "where": "NUMBER লাইনের বাম পাশে ([emoji] NUMBER 880✪ᴀʀ✪1234)"
    },
    "sms": {
        "label": "SMS Row",
        "btn": "💬 SMS Row",
        "fallback": "💬",
        "where": "SMS লাইনের বাম পাশে ([emoji] 𝗦𝗠𝗦 · #English)"
    },
    "service": {
        "label": "Service (Default)",
        "btn": "⚙️ Service (Default)",
        "fallback": "⚙️",
        "where": "কোনো সার্ভিস ডিটেক্ট না হলে সার্ভিস নামের পাশে বসবে"
    },
    "otp_code": {
        "label": "OTP Code Row",
        "btn": "🔐 OTP Code Row",
        "fallback": "🔐",
        "where": "OTP CODE লাইনের বাম পাশে ([emoji] OTP CODE: 123456)"
    },
    "sms_rate": {
        "label": "SMS Rate Row",
        "btn": "💰 SMS Rate Row",
        "fallback": "💰",
        "where": "SMS RATE লাইনের বাম পাশে ([emoji] SMS RATE: ৳1 / OTP)"
    },
    "country": {
        "label": "Country (Default)",
        "btn": "🌍 Country (Default)",
        "fallback": "🌍",
        "where": "দেশের পতাকা না পাওয়া গেলে ডিফল্ট কান্ট্রি আইকন হিসেবে বসবে"
    }
}


def _otp_group_emoji(slot, fallback=None):
    """Return the configured Premium/Custom Emoji HTML for an OTP Group slot.
    Supports both {"id": ..., "char": ...} and legacy string IDs.
    """
    if fallback is None:
        fallback = OTP_GROUP_SLOTS.get(slot, {}).get("fallback", "✨")
    val = bot_settings.get("otp_group_emojis", {}).get(slot)
    if isinstance(val, dict):
        eid = str(val.get("id") or "").strip()
        ch = str(val.get("char") or fallback).strip() or fallback
        if eid:
            return f'<tg-emoji emoji-id="{html.escape(eid)}">{html.escape(ch)}</tg-emoji>'
        return html.escape(ch)
    eid = str(val or "").strip()
    if not eid:
        eid = GLOBAL_BODY_EMOJIS.get(fallback)
    if eid:
        return f'<tg-emoji emoji-id="{html.escape(str(eid))}">{html.escape(fallback)}</tg-emoji>'
    return html.escape(fallback)


def build_otp_group_emoji_manager_ui(notice=""):
    """Build the interactive OTP Group Emoji Manager with live visual map."""
    t_e = _otp_group_emoji("title", "✉️")
    c_e = _otp_group_emoji("country", "🌍")
    s_e = _otp_group_emoji("service", "⚙️")
    n_e = _otp_group_emoji("number", "📱")
    m_e = _otp_group_emoji("sms", "💬")
    o_e = _otp_group_emoji("otp_code", "🔐")
    r_e = _otp_group_emoji("sms_rate", "💰")

    header_notice = f"{notice}\n\n" if notice else ""
    txt = (
        f"{header_notice}"
        "✨ <b>OTP GROUP EMOJI MANAGER</b> ✨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "নিচের প্রিভিউতে দেখুন কোন জায়গায় কোন ইমোজি বসবে। যেটি পরিবর্তন করতে চান নিচের সেই বাটনে ক্লিক করুন:\n\n"
        "<blockquote>"
        f"{t_e} <b>🆂🅼🆂 🆁🅲🆅</b> {t_e}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{c_e} <b>Country</b> │ {s_e} <b>Service</b>\n"
        f"{n_e} <b>NUMBER</b>  <code>880✪ᴀʀ✪1234</code>\n"
        f"{m_e} <b>𝗦𝗠𝗦</b> · <i>#English</i>\n"
        f"{o_e} <b>OTP CODE:</b> <code>123456</code>\n"
        f"{r_e} <b>SMS RATE:</b> <b>৳1 / OTP</b>"
        "</blockquote>"
    )
    kb = [
        [
            {"text": OTP_GROUP_SLOTS["title"]["btn"], "callback_data": "otp_slot_title", "style": "primary"},
            {"text": OTP_GROUP_SLOTS["number"]["btn"], "callback_data": "otp_slot_number", "style": "primary"}
        ],
        [
            {"text": OTP_GROUP_SLOTS["sms"]["btn"], "callback_data": "otp_slot_sms", "style": "primary"},
            {"text": OTP_GROUP_SLOTS["service"]["btn"], "callback_data": "otp_slot_service", "style": "primary"}
        ],
        [
            {"text": OTP_GROUP_SLOTS["otp_code"]["btn"], "callback_data": "otp_slot_otp_code", "style": "primary"},
            {"text": OTP_GROUP_SLOTS["sms_rate"]["btn"], "callback_data": "otp_slot_sms_rate", "style": "primary"}
        ],
        [
            {"text": OTP_GROUP_SLOTS["country"]["btn"], "callback_data": "otp_slot_country", "style": "primary"},
            {"text": "🧪 Test Preview", "callback_data": "otp_emoji_preview", "style": "success"}
        ],
        [
            {"text": "🔄 Reset All Defaults", "callback_data": "otp_emoji_reset_all", "style": "danger"}
        ],
        [
            {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}
        ]
    ]
    return txt, {"inline_keyboard": kb}


def _format_otp_group_message(number, service_name, iso, full_sms, country_name_override=None, otp_code=None):
    """Format only the OTP Forward Group message in the Premium card style."""
    clean_num = re.sub(r"\D", "", str(number or ""))
    # Stylish text marker for the masked portion of the number.
    mask_emoji = "<b>✪ᴀʀ✪</b>"
    if len(clean_num) > 7:
        masked_num_html = f"<code>{html.escape(clean_num[:3])}</code>{mask_emoji}<code>{html.escape(clean_num[-4:])}</code>"
    elif len(clean_num) > 2:
        masked_num_html = f"<code>{html.escape(clean_num[:1])}</code>{mask_emoji}<code>{html.escape(clean_num[-1:])}</code>"
    else:
        masked_num_html = f"<code>{html.escape(clean_num or 'Unknown')}</code>"

    try:
        country_name = str(
            country_name_override or get_assigned_country_for_number(clean_num) or ""
        ).strip()
        if not country_name:
            country_name = get_flag_info_html(str(iso or "XX"), return_full_name=True)
            country_name = re.sub(r"<[^>]+>", "", str(country_name or "")).strip()
        # Resolve the flag using the full phone number so configured Telegram
        # Premium country-flag emoji IDs can be matched by number prefix.
        # Looking up only the ISO code can fall back to a normal Unicode flag.
        country_flag = str(
            get_flag_info_html(clean_num, return_full_name=False) or ""
        ).strip()
    except Exception:
        country_name = str(iso or "XX").strip() or "Unknown"
        country_flag = "🌍"

    if not country_name or country_name.upper() == "XX":
        country_name = "Unknown"
    if not country_flag or country_flag == "🌍":
        country_flag = _otp_group_emoji('country', '🌍')
    elif "<tg-emoji" not in country_flag:
        country_flag = html.escape(country_flag)

    service = re.sub(r"<[^>]+>", "", str(service_name or "OTP Service")).strip() or "OTP Service"
    sms = str(full_sms or "").strip() or "—"
    # OTP Group only: always show the service the user selected in GET NUMBER
    # for this number (the SMS text is NOT used to detect the service).
    # If the selected service is unknown, show the explicit fallback label.
    try:
        assigned_service = get_assigned_service_for_number(clean_num)
        if assigned_service:
            service_label, service_logo_html = get_service_info_html(assigned_service, "")
            if service_label and service_label != "Service Not Detected":
                service = service_label
            else:
                service = "Service Not Detected"
        else:
            service = "Service Not Detected"
            service_logo_html = _otp_group_emoji('service', '⚙️')
        if not service_logo_html:
            service_logo_html = _otp_group_emoji('service', '⚙️')
    except Exception:
        service = "Service Not Detected"
        service_logo_html = _otp_group_emoji('service', '⚙️')

    try:
        lang_code = detect_language(sms)
        lang_name = LANG_MAP.get(lang_code, "English") if "LANG_MAP" in globals() else str(lang_code).replace("#", "")
    except Exception:
        lang_name = "English"

    # Show the same per-number reward that is credited when this OTP is received.
    try:
        sms_rate = float(_get_assigned_number_reward(clean_num))
    except Exception:
        sms_rate = 0.0
    rate_text = f"৳{sms_rate:g}" if sms_rate.is_integer() else f"৳{sms_rate:.2f}"

    # Premium-style Telegram text layout; only the OTP group card footer is changed.
    return render_body_text(
        f"{_otp_group_emoji('title', '✉️')} <b>🆂🅼🆂 🆁🅲🆅</b> {_otp_group_emoji('title', '✉️')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{country_flag} <b>{html.escape(country_name.title())}</b>"
        f"│{service_logo_html} <b>{html.escape(service)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{_otp_group_emoji('number', '📱')}  <b>𝐍𝐔𝐌𝐁𝐄𝐑</b>  {masked_num_html}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{_otp_group_emoji('sms', '💬')}  <b>𝗦𝗠𝗦</b> · <i>#{html.escape(lang_name)}</i>\n"
        f"<blockquote>{html.escape(sms)}</blockquote>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{_otp_group_emoji('otp_code', '🔐')} <b>OTP CODE:</b> <code>{html.escape(str(otp_code or 'NA').strip())}</code>\n"
        f"{_otp_group_emoji('sms_rate', '💰')} <b>SMS RATE:</b> <b>{rate_text} / OTP</b>"
    )


def _format_inbox_otp_message(number, service_name, iso, owner_id, service_emoji_html=None):
    """Format only the Inbox OTP message body; keyboard/buttons remain unchanged."""
    clean_num = re.sub(r"\D", "", str(number or ""))
    display_num = clean_num or "Unknown"

    # Keep the full current user balance in the Inbox OTP card.
    try:
        balance = float(get_user(owner_id).get("balance", 0.0) or 0.0)
    except Exception:
        balance = 0.0

    # Show the same per-number SMS reward used by the OTP reward flow.
    try:
        sms_rate = float(_get_assigned_number_reward(clean_num) or 0.0)
    except Exception:
        sms_rate = 0.0

    # Inbox text is sent before update_balance() runs, so display the post-OTP
    # balance here: current cached balance plus the reward for this OTP.
    balance += sms_rate
    rate_text = f"৳{sms_rate:g}" if sms_rate.is_integer() else f"৳{sms_rate:.2f}"

    # Premium-style title emoji; this changes message text only, not the OTP Group button.
    title_emoji = f'<tg-emoji emoji-id="{_REQUESTED_INBOX_OTP_TITLE_EMOJI_ID}">⚡️</tg-emoji>'

    return render_body_text(
        f"{title_emoji} <b>𝐍𝐄𝐖 𝐎𝐓𝐏 𝐑𝐄𝐂𝐄𝐈𝐕𝐄</b> {title_emoji}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 <b>𝐍𝐔𝐌𝐁𝐄𝐑:</b> <code>{html.escape(display_num)}</code>\n"
        f"💸 <b>𝐑𝐄𝐖𝐀𝐑𝐃:</b> <b>{rate_text} / OTP</b>\n"
        f"💰 <b>𝐁𝐀𝐋𝐀𝐍𝐂𝐄:</b> <b>৳{balance:.2f} BDT</b>"
    )

LANG_MAP = {
    "#EN": "English", "#BN": "Bengali", "#AR": "Arabic", "#HI": "Hindi", 
    "#PA": "Punjabi", "#GU": "Gujarati", "#OR": "Odia", "#TA": "Tamil", 
    "#TE": "Telugu", "#KN": "Kannada", "#ML": "Malayalam", "#SI": "Sinhala", 
    "#TH": "Thai", "#LO": "Lao", "#BO": "Tibetan", "#MY": "Burmese", 
    "#AM": "Amharic", "#KM": "Khmer", "#KA": "Georgian", "#HY": "Armenian", 
    "#HE": "Hebrew", "#EL": "Greek", "#RU": "Russian", "#ZH": "Chinese", 
    "#JA": "Japanese", "#KO": "Korean", "#ID": "Indonesian", "#MS": "Malay", 
    "#VN": "Vietnamese", "#TL": "Filipino", "#ES": "Spanish", "#PT": "Portuguese", 
    "#FR": "French", "#DE": "German", "#IT": "Italian", "#PL": "Polish", 
    "#TR": "Turkish", "#NL": "Dutch", "#SV": "Swedish", "#DA": "Danish", 
    "#NO": "Norwegian", "#FI": "Finnish", "#CS": "Czech", "#SK": "Slovak", 
    "#HU": "Hungarian", "#RO": "Romanian", "#HR": "Croatian", "#BG": "Bulgarian", 
    "#UK": "Ukrainian", "#SW": "Swahili", "#AF": "Afrikaans"
}

# ==========================================
# 🌟 ADVANCED SERVICE & LANGUAGE DETECTION
# ==========================================

SERVICE_SMS_KEYWORDS = {
    # 🟢 Social Media & Chat (Added Arabic Keywords)
    "whatsapp": ["whatsapp", "whatsa", "whatsap", "whats", "whatsapp business", "whatsapp me", "whatsapp code", "whatsap", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსאფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],

    # 🔵 Tech & Mail
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    
    # 💰 Crypto & Trading
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],

    # 💳 Finance & Wallets
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "alipay": ["alipay", "ali pay", "alipay verification", "支付宝"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],

    # 🛒 E-commerce & Delivery
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],

    # 🎮 Gaming & Entertainment
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],

    # 🎲 Betting & Casino
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],

    # ❤️ Dating
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def detect_service(text):
    """Detect a service only from clear service-name matches in the SMS text."""
    text_lower = str(text or "").lower()
    if not text_lower.strip():
        return None

    # Prefer the most specific/longest alias first, preventing short aliases such
    # as "ig", "fb", or "line" from winning on unrelated parts of an SMS.
    candidates = []
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for keyword in keywords:
            kw = str(keyword or "").strip().lower()
            if kw:
                candidates.append((len(kw), service_key, kw))
    candidates.sort(key=lambda item: item[0], reverse=True)

    for _, service_key, keyword in candidates:
        if re.fullmatch(r"[a-z0-9]+(?:[._-][a-z0-9]+)*", keyword):
            # Latin aliases must match whole tokens, not substrings inside words.
            pattern = r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])"
            if re.search(pattern, text_lower):
                return service_key.upper()
        elif keyword in text_lower:
            return service_key.upper()
    return None


def _get_effective_otp_service(number, message_text, fallback_service=None):
    """Use the service explicitly identifiable in the SMS, never the requested number label."""
    detected_service = detect_service(message_text)
    if not detected_service:
        return "Service Not Detected", _otp_group_emoji('service', '⚙️') if '_otp_group_emoji' in globals() else "⚙️"
    return get_service_info_html(detected_service, "")

def _premium_emoji_html(data, fallback="📱"):
    """Return one or multiple configured Premium/Custom Emojis as HTML."""
    data = data or {}
    ids = data.get("ids")
    chars = data.get("chars")
    if not isinstance(ids, list):
        ids = [data.get("id")] if data.get("id") else []
    if not isinstance(chars, list):
        chars = [data.get("char")] if data.get("char") else []

    parts = []
    for idx, eid in enumerate(ids[:2]):
        if not eid:
            continue
        char = chars[idx] if idx < len(chars) and chars[idx] else (chars[0] if chars else fallback)
        parts.append(f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>')
    if parts:
        return " ".join(parts)
    return chars[0] if chars else fallback


def get_service_info_html(service_text, msg_text=""):
    """Map a detected service key to its configured display name and emoji."""
    s = str(service_text or "").strip().upper()
    if not s or s in {"UNKNOWN", "NONE", "MESSAGE", "SERVICE NOT DETECTED"}:
        return "Service Not Detected", _otp_group_emoji('service', '⚙️') if '_otp_group_emoji' in globals() else "⚙️"

    apps = bot_settings.get("premium_apps", {})
    clean_s = re.sub(r"[^\w\s]", "", s).strip()
    for app_name, data in apps.items():
        app_key = str(app_name).strip().upper()
        if app_key == s or app_key == clean_s:
            full_name = data.get("name", str(app_name).title())
            return full_name, _premium_emoji_html(data, "📱")

    # Keep the detected service label even when no custom Premium Emoji is configured.
    return s.title(), "📱"

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)

    # ১. Unicode Block দিয়ে নিখুঁত বর্ণমালা শনাক্তকরণ (100% Accurate for scripts)
    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR" # Arabic / Persian / Urdu
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN" # Bengali
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI" # Hindi / Marathi / Nepali
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA" # Punjabi (Gurmukhi)
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU" # Gujarati
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR" # Odia
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA" # Tamil
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE" # Telugu
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN" # Kannada
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML" # Malayalam
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI" # Sinhala
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH" # Thai
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO" # Lao
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO" # Tibetan
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY" # Burmese (Myanmar)
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM" # Amharic (Ethiopic)
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM" # Khmer
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA" # Georgian
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY" # Armenian
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE" # Hebrew
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL" # Greek
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU" # Russian / Ukrainian (Cyrillic)
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH" # Chinese
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA" # Japanese
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO" # Korean

    # ২. OTP Keyword দিয়ে ভাষা শনাক্তকরণ (Latin script languages)
    text_lower = text_str.lower()
    
    # Asian / Pacific
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID" # Indonesian
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS" # Malay
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN" # Vietnamese
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL" # Tagalog / Filipino
    
    # European / Americas
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES" # Spanish
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT" # Portuguese
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR" # French
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE" # German
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT" # Italian
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL" # Polish
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR" # Turkish
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL" # Dutch
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV" # Swedish
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA" # Danish
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO" # Norwegian
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI" # Finnish
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS" # Czech
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK" # Slovak
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU" # Hungarian
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO" # Romanian
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR" # Croatian/Serbian
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG" # Bulgarian
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK" # Ukrainian
    
    # African
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW" # Swahili
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF" # Afrikaans
    
    # ৩. উপরের কোনোটি না মিললে ডিফল্ট
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

# Remember "already joined" results for 60 seconds so every message/button click
# does not call Telegram once per channel. Only successful checks are cached, so a
# user who has not joined is always re-checked live (Check Joined works instantly).
_fj_joined_cache = {}
FJ_CACHE_SECONDS = 60
FJ_STALE_OK_SECONDS = 900   # a user who was verified as joined stays instant for 15 min
_fj_refreshing = set()
_fj_pool = ThreadPoolExecutor(max_workers=16)

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    _fj_key = (user_id, tuple(bot_settings["fj_channels"]))
    _fj_hit = _fj_joined_cache.get(_fj_key)
    if _fj_hit:
        _age = time.time() - _fj_hit
        if _age < FJ_CACHE_SECONDS:
            return True
        if _age < FJ_STALE_OK_SECONDS:
            # Verified before: answer instantly, re-verify in the background.
            # If the user has left a channel, the cache is dropped and the next click is blocked.
            if _fj_key not in _fj_refreshing:
                _fj_refreshing.add(_fj_key)
                def _bg(_k=_fj_key, _uid=user_id):
                    try:
                        if _fj_check_all_channels(_uid):
                            _fj_joined_cache[_k] = time.time()
                        else:
                            _fj_joined_cache.pop(_k, None)
                    except Exception:
                        pass
                    finally:
                        _fj_refreshing.discard(_k)
                threading.Thread(target=_bg, daemon=True).start()
            return True
    if _fj_check_all_channels(user_id):
        _fj_joined_cache[_fj_key] = time.time()
        if len(_fj_joined_cache) > 20000:
            _fj_joined_cache.clear()
        return True
    _fj_joined_cache.pop(_fj_key, None)
    return False

def _fj_check_one_channel(ch, user_id):
    res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
    if not res.get("ok") or not isinstance(res.get("result"), dict):
        # Do not silently bypass Force Join when Telegram cannot verify membership.
        print(f"[FORCE JOIN] Membership check failed for channel={ch}: {res.get('description', 'Telegram API error')}")
        return False
    member = res["result"]
    status = str(member.get("status", "")).lower()
    # Telegram's restricted status can still mean the user is a channel member.
    is_member = member.get("is_member", False)
    return status in ("creator", "administrator", "member") or (status == "restricted" and is_member)

def _fj_check_all_channels(user_id):
    channels = list(bot_settings["fj_channels"])
    if len(channels) <= 1:
        return all(_fj_check_one_channel(ch, user_id) for ch in channels)
    # Several channels: check them in parallel instead of one after another.
    return all(_fj_pool.map(lambda ch: _fj_check_one_channel(ch, user_id), channels))

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if ch.startswith("@") else ch
        kb.append([{"text": f"Join Channel", "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

_ban_refreshing = set()

def _refresh_ban_status(user_id):
    prev = user_banned_cache.get(user_id)
    banned = False
    ok = False
    if db:
        try:
            doc = db.collection('users').document(str(user_id)).get()
            banned = bool(doc.exists and doc.to_dict().get("banned", False))
            ok = True
        except: pass
    if not ok and prev:
        banned = prev['banned']  # Firestore failed: keep the last known answer
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

def is_user_banned(user_id):
    if is_admin(user_id): return False
    entry = user_banned_cache.get(user_id)
    if entry:
        if time.time() - entry['time'] >= 60 and user_id not in _ban_refreshing:
            # Stale: answer instantly from cache and refresh in the background so a
            # button click never waits for a Firestore read. (Admin ban/unban already
            # updates this cache directly, so those take effect immediately.)
            _ban_refreshing.add(user_id)
            def _bg(_uid=user_id):
                try: _refresh_ban_status(_uid)
                finally: _ban_refreshing.discard(_uid)
            threading.Thread(target=_bg, daemon=True).start()
        return entry['banned']
    return _refresh_ban_status(user_id)  # first time we see this user

# ==========================================
# Captcha Auto Login & Parsing Core
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))

    # 1. Multi-part OTPs (e.g. 123-456 or 809-761)
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        # হাইফেন (-) থাকলে সেটা রেখে দিবে, কিন্তু স্পেস থাকলে মুছে একসাথে করে দিবে
        return multi_part.group(0).replace(" ", "")

    # 2. Keyword-based extraction
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match:
        candidate = keyword_match.group(1)
        # Accept alphanumeric OTPs when they are explicitly attached to an OTP/code
        # keyword. This does not treat standalone usernames/passwords as OTPs.
        if any(ch.isdigit() for ch in candidate):
            return candidate
        
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev:
        candidate = keyword_match_rev.group(1)
        if any(ch.isdigit() for ch in candidate):
            return candidate

    # 3. Google OTP
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)

    # 4. Digit sequences fallback
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]

    return None

def parse_panel_response(response_text, p_config=None):
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"

    n_col_name = str(p_config.get("num_col_name", "number")).strip().lower() if p_config else "number"
    m_col_name = str(p_config.get("msg_col_name", "message")).strip().lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    def normalize_number(value):
        clean = re.sub(r'\D', '', str(value or ''))
        return clean if 5 <= len(clean) <= 18 else None

    def append_record(number_value, message_value):
        num = normalize_number(number_value)
        msg = str(message_value or '').strip()
        # Keep every real Number + Message event. Short messages can be legitimate SMS/OTP.
        if not num or not msg:
            return
        otp = extract_otp_code(msg)
        # A message without a detectable OTP is still a valid event; display it as NA.
        otp = str(otp).strip() if otp else "NA"
        results.append({"number": num, "message": msg, "otp": otp})

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if not rows:
                    continue
                final_n_idx = n_idx
                final_m_idx = m_idx
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text:
                        final_n_idx = i
                    if m_col_name in c_text:
                        final_m_idx = i
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if all(c.name == 'th' for c in cols):
                        continue
                    if len(cols) > max(final_n_idx, final_m_idx):
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        append_record(num_text, msg_text)
        except Exception:
            pass
    else:
        try:
            data = json.loads(response_text)
            temp_results = []

            # API providers can wrap the actual records in several nested layers.
            # The old blind scan could combine a number from one field with a
            # message from another field in the same wrapper, causing one of
            # several SMS records for the same number to disappear.  Only treat
            # an object as a record when it contains an actual number+message pair.
            number_keys = [n_col_name, "number", "num", "phone", "msisdn", "mobile", "phone_number"]
            message_keys = [m_col_name, "message", "msg", "sms", "content", "text", "body"]
            number_keys = list(dict.fromkeys(k for k in number_keys if k))
            message_keys = list(dict.fromkeys(k for k in message_keys if k))

            def find_key_value(item, candidates):
                if not isinstance(item, dict):
                    return None
                lower_map = {str(k).strip().lower(): v for k, v in item.items()}
                for key in candidates:
                    if key in lower_map:
                        value = lower_map[key]
                        if isinstance(value, (str, int, float)) and str(value).strip():
                            return value
                return None

            def process_record(item):
                # Explicit object record: number + message must come from this
                # same object. This prevents wrapper-level cross-matching.
                if isinstance(item, dict):
                    number_value = find_key_value(item, number_keys)
                    message_value = find_key_value(item, message_keys)
                    if number_value is not None and message_value is not None:
                        append_record(number_value, message_value)
                        return True

                # Flat array record, e.g. [id, number, message, ...].
                if isinstance(item, list) and item and all(not isinstance(x, (dict, list)) for x in item):
                    if 0 <= n_idx < len(item) and 0 <= m_idx < len(item):
                        before = len(results)
                        append_record(item[n_idx], item[m_idx])
                        return len(results) > before
                    return False
                return False

            def traverse_json(node):
                if isinstance(node, dict):
                    # A New Provider response can contain the newest SMS as
                    # number/message fields on a wrapper object while older SMS
                    # rows are stored inside a nested data/list object.  The old
                    # code returned immediately after finding number+message on
                    # the wrapper, which silently dropped those nested rows.
                    # Keep the current object as a record when it is one, BUT
                    # always continue walking nested containers so every SMS
                    # event in the response is collected.
                    process_record(node)
                    for value in node.values():
                        if isinstance(value, (dict, list)):
                            traverse_json(value)
                elif isinstance(node, list):
                    # A list of record objects should produce one event per item.
                    if node and all(isinstance(x, dict) for x in node):
                        for child in node:
                            traverse_json(child)
                    elif node and all(not isinstance(x, (dict, list)) for x in node):
                        process_record(node)
                    else:
                        for child in node:
                            if isinstance(child, (dict, list)):
                                traverse_json(child)

            traverse_json(data)

            # Final de-duplication: only an exact Number + OTP + Full SMS match
            # is a duplicate. Same number with a different SMS remains separate.
            seen = set()
            for r in results:
                uid = (
                    str(r.get("number", "")).replace("+", "").replace(" ", "").replace("-", "").strip(),
                    str(r.get("otp", "")).strip(),
                    str(r.get("message", "")).strip(),
                )
                if uid not in seen:
                    seen.add(uid)
                    temp_results.append({
                        "number": uid[0],
                        "message": uid[2],
                        "otp": uid[1]
                    })
            results = temp_results
        except Exception:
            pass

    return results

# 🌟 Advanced Automated Background Captcha Solver 🌟
def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
        
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        
        # 1. SOLVE CAPTCHA (Exact bot 3.py logic)
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m
                        break
                        
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+': answer = str(a + b)
            elif op == '-': answer = str(a - b)
            elif op == '*': answer = str(a * b)

        # 2. FIND FORM
        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
            
        action = form.get("action")
        from urllib.parse import urljoin, quote, unquote
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name: form_data[name] = hidden.get("value") or ""
        
        user_input = form.find("input", {"name": re.compile(r"user|email|id", re.I)}) or \
                     form.find("input", {"type": "text", "placeholder": re.compile(r"user|email", re.I)}) or \
                     form.find("input", {"type": "text"})
                     
        pass_input = form.find("input", {"name": re.compile(r"pass", re.I)}) or \
                     form.find("input", {"type": "password"})
                     
        captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha", re.I)}) or \
                        form.find("input", {"name": re.compile(r"ans|captcha|ver|code", re.I)})
        
        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_field:
            form_data[captcha_field] = answer

        # 3. SUBMIT
        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)
        
        # 4. VERIFY (Exact bot 3.py check logic)
        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
            
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        
        check_res = session.get(check_url, timeout=10)
        
        if 'logout' in login_req.text.lower() or 'logout' in check_res.text.lower() or 'sms reports' in check_res.text.lower() or 'dashboard' in check_res.text.lower() or 'cdrs' in check_res.text.lower():
            panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:
            # এখানে ফেইল হলে অংক কী পেয়েছিল তা দেখা যাবে
            p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
            return False
            
    except Exception as e:
        p["login_status"] = f"❌ Error: {str(e)[:20]}"
        
    return False

def panel_supervisor_thread():
    """Runs one independent monitor thread per panel, so a slow/broken panel
    can no longer delay OTP polling of the other panels."""
    workers = {}
    while True:
        try:
            for panel in list(bot_settings.get("panels", [])):
                key = id(panel)
                entry = workers.get(key)
                if entry is None or not entry[0].is_alive():
                    worker = threading.Thread(target=panel_monitor_thread, args=(panel,), daemon=True)
                    worker.start()
                    workers[key] = (worker, panel)  # keep reference so id() stays unique
            for key in [k for k, (w, _p) in workers.items() if not w.is_alive()]:
                del workers[key]
        except Exception as e:
            print(f"[PANEL SUPERVISOR ERROR] {type(e).__name__}: {e}")
        time.sleep(3)

def panel_monitor_thread(target_panel=None):
    global processed_otps, recent_traffic, panel_sessions, panel_processed_events, panel_event_fingerprints, assigned_number_owners
    while True:
        try:
            # Prioritize Hadi so slow polling of unrelated panels cannot hold up its OTPs.
            panel_items = list(enumerate(bot_settings.get("panels", [])))
            if target_panel is not None:
                # Per-panel worker: only watch its own panel; stop if the panel was deleted.
                panel_items = [(i, pp) for i, pp in panel_items if pp is target_panel]
                if not panel_items:
                    return
            panel_items.sort(key=lambda item: 0 if "hadi" in str(item[1].get("name", "")).lower() else 1)
            for idx, p in panel_items:
                panel_cycle_started = time.perf_counter()
                if p.get("status") == "ON":
                    
                    if p.get("type") == "Auto Captcha Panel":
                        sess = panel_sessions.get(idx)
                        
                        if not sess:
                            now = time.time()
                            if now - p.get("last_login_attempt", 0) < 30: 
                                continue 
                            p["last_login_attempt"] = now
                            
                            success = attempt_auto_login(p, idx)
                            save_db() # Save login status text to show in settings
                            if not success:
                                continue 
                            sess = panel_sessions.get(idx)
                            
                        try:
                            # 🌟 auto sessions with sAjaxSource and Fallback HTML Parser
                            parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                            p["login_status"] = "✅ Active & Fetching"
                        except Exception as e:
                            p["login_status"] = "❌ Session Expired (Retrying...)"
                            del panel_sessions[idx]
                            save_db()
                            continue

                    elif p.get("api_url") or p.get("full_api_url"): 
                        api_scan_started = time.perf_counter()
                        full_url = p.get("full_api_url", "").strip()
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        if not full_url and not url: continue
                        
                        is_hadi_panel = "hadi" in str(p.get("name", "")).lower()
                        urls_to_try = []
                        if full_url:
                            urls_to_try.append(full_url)
                        else:
                            if "{token}" in url or "{key}" in url:
                                urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                            elif "token=" in url or "key=" in url:
                                urls_to_try.append(url)
                            else:
                                sep = '&' if '?' in url else '?'
                                urls_to_try.append(f"{url}{sep}token={token}")
                                urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                urls_to_try.append(f"{url}{sep}key={token}")
                            
                        parsed_data = []
                        # 🌟 Browser Bypass (403 Forbidden Fix)
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                        successful_api_url = None
                        successful_urls = []
                        has_fresh_unseen_events = False
                        # Prefer fast delivery of a newly received OTP. Once a URL
                        # variant returns an event not yet processed, avoid waiting for
                        # other fallback variants in this polling cycle.
                        for try_url in urls_to_try:
                            try:
                                res = _timed_api_get(try_url, headers=headers, timeout=5 if is_hadi_panel else 10, label=f"PANEL:{p.get('name', 'unknown')}:url_variant")
                                page_data = parse_panel_response(res.text, p)
                                if page_data:
                                    parsed_data.extend(page_data)
                                    successful_urls.append(try_url)
                                    if successful_api_url is None:
                                        successful_api_url = try_url
                                    if not full_url and try_url != url and token and not p.get("api_url"):
                                        p["api_url"] = try_url.replace(token, "{token}")
                                        save_db()
                                    for api_item in page_data:
                                        event_num = str(api_item.get("number", "")).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        event_otp = str(api_item.get("otp", "NA") or "NA").strip() or "NA"
                                        event_msg = str(api_item.get("message", "") or "").strip()
                                        if not event_msg:
                                            continue
                                        event_source = f"{event_num}\x1f{event_otp}\x1f{event_msg}"
                                        event_hash = hashlib.sha256(event_source.encode("utf-8", "replace")).hexdigest()
                                        if f"PANEL_{event_hash}" not in panel_event_fingerprints:
                                            has_fresh_unseen_events = True
                                            break
                                    # Use the first API URL variant that returns parseable records
                                    # for every API panel, matching the fast HADI behavior. These URL
                                    # variants are authentication fallbacks, not separate data sources.
                                    if page_data:
                                        break
                            except Exception:
                                continue

                        # Do not scan historical API pages synchronously before forwarding.
                        # File B processes the current API response directly; fetching older
                        # pages here can block this panel (and all panels after it) for several
                        # request timeouts. Keep the current response as the live OTP source.
                        if parsed_data:
                            print(f"[PANEL DEBUG] API parsed before merge: {len(parsed_data)} record(s)")
                            merged = []
                            seen_api_events = set()
                            for api_item in parsed_data:
                                event_key = (
                                    str(api_item.get("number", "")).replace("+", "").replace(" ", "").replace("-", "").strip(),
                                    str(api_item.get("otp", "")).strip(),
                                    str(api_item.get("message", "")).strip(),
                                )
                                if event_key not in seen_api_events:
                                    seen_api_events.add(event_key)
                                    merged.append(api_item)
                            parsed_data = merged
                            print(f"[PANEL DEBUG] API parsed after exact-event merge: {len(parsed_data)} record(s)")
                        print(f"[OTP TIMING][PANEL SCAN] panel={p.get('name', 'unknown')} api_scan_elapsed={time.perf_counter() - api_scan_started:.3f}s records={len(parsed_data)}")
                        if not parsed_data: continue
                    else:
                        continue
                    
                    if p.get("type") != "Auto Captcha Panel":
                        # The configured records value controls pagination above; it must
                        # not become a final delivery limit, otherwise later SMS events
                        # for the same number can be discarded before processing.
                        pass
                        
                    print(f"[PANEL DEBUG] Entering event processor with {len(parsed_data)} record(s)")
                    for item in parsed_data:
                        try:
                            num = item["number"]
                            otp = str(item.get("otp") or "NA").strip() or "NA"
                            msg_text = str(item.get("message") or "").strip()
                            if not msg_text:
                                continue
                            # Create a collision-resistant identity from Number + OTP + exact Full SMS.
                            # This is panel-local and does not use the shared provider processed_otps set.
                            normalized_event_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            normalized_event_msg = str(msg_text).strip()
                            event_source = f"{normalized_event_num}\x1f{str(otp).strip()}\x1f{normalized_event_msg}"
                            event_hash = hashlib.sha256(event_source.encode("utf-8", "replace")).hexdigest()
                            unique_id = f"PANEL_{event_hash}"
                            print(f"[PANEL DEBUG] Event candidate: number=*{normalized_event_num[-4:]}, otp_len={len(str(otp).strip())}, fingerprint={event_hash[:12]}")
                            print(f"[OTP TIMING][PANEL EVENT] panel={p.get('name', 'unknown')} fingerprint={event_hash[:12]} elapsed_since_panel_iteration_start={time.perf_counter() - panel_cycle_started:.3f}s")
                        
                            if unique_id not in panel_event_fingerprints:
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = _get_effective_otp_service(num, msg_text, p.get("name", "Panel"))
                                current_time = time.time()
                            
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({
                                    "traffic_service": get_assigned_service_for_number(num), "service": app_full_name,
                                    "iso": iso,
                                    "flag": char,
                                    "number": num,
                                    "time": current_time,
                                    "traffic_source": "otp_group"
                                })
                                # 🌟 শুধু লোকাল ফাইলে সেভ করবে, Firestore এ অহেতুক Write করবে না!
                                save_local_db()
                                 
                                display_num = str(num).replace("+", "").replace(" ", "").replace("-", "")
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                            
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = _format_otp_group_message(display_num, app_full_name, iso, msg_text, otp_code=otp)
                            
                                # Send this exact OTP event to every configured OTP Group,
                                # but remember successful delivery so a temporary Telegram
                                # error can be retried without duplicating successful sends.
                                # Group send runs in parallel with the owner lookup + inbox send
                                # (it used to block them). It is joined below before completion check.
                                group_thread = None
                                group_results = []
                                if unique_id not in panel_otp_group_delivered:
                                    def _panel_group_send(_msg=display_msg, _otp=otp, _out=group_results):
                                        try:
                                            _out.extend(send_otp_to_groups(_msg, _otp))
                                        except Exception as _exc:
                                            print(f"[PANEL DEBUG] Group send crashed: {_exc}")
                                    group_thread = threading.Thread(target=_panel_group_send, daemon=True)
                                    group_thread.start()
                            
                                owners = []
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            
                                # 🌟 ALGORITHM FIX: সরাসরি Active Sessions থেকে মালিক খোঁজা 
                                # (কারণ Local Stock থেকে নাম্বার Assign হওয়ার সাথে সাথে ডিলিট হয়ে যায়)
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owners.append(uid)
                                            break
                                        
                                # Persistent generic owner fallback for New Provider / Auto Captcha.
                                # This survives active-session replacement and local-stock removal.
                                remembered_owner = assigned_number_owners.get(clean_api_num)
                                if remembered_owner is not None:
                                    owners.append(remembered_owner)
                                else:
                                    # Match formatting/country-code variants in the persistent
                                    # owner map too, so API panels use the same owner recovery.
                                    for assigned_num, mapped_owner in assigned_number_owners.items():
                                        if _numbers_match(assigned_num, clean_api_num):
                                            owners.append(mapped_owner)
                                            break

                                # Provider/local-stock fallback: an assigned number may no longer
                                # exist in the active provider map after the stock assignment.
                                # Keep the current owner lookup limited to this exact number/event
                                # flow so multiple OTPs for the same number can all reach its owner.
                                if not owners:
                                    for assigned_map in (stex_assigned_numbers, voltx_assigned_numbers, zenex_assigned_numbers):
                                        for assigned_num, n_owner in assigned_map.items():
                                            clean_assigned = str(assigned_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                            if clean_assigned == clean_api_num or (len(clean_assigned) >= 8 and clean_assigned.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_assigned[-8:])):
                                                owners.append(n_owner)

                                # Local uploaded numbers keep their owner in used_by.
                                # This is needed when the number has already been removed
                                # from the provider-assignment maps.
                                if not owners:
                                    for batch_data in number_batches.values():
                                        for number_obj in batch_data.get("numbers", []):
                                            local_num = str(number_obj.get("num", "")).replace("+", "").replace(" ", "").replace("-", "").strip()
                                            if local_num == clean_api_num or (len(local_num) >= 8 and local_num.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(local_num[-8:])):
                                                owners.extend(number_obj.get("used_by", []) or [])
                                                break
                                        if owners:
                                            break

                                owners = list(dict.fromkeys(owners))
                                print(f"[PANEL DEBUG] Owner lookup: fingerprint={event_hash[:12]}, owners={len(owners)}")
                                inbox_delivery_ok = True
                                for owner_id in owners:
                                    inbox_key = f"{unique_id}_{owner_id}"
                                    if inbox_key in panel_otp_inbox_delivered:
                                        continue
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    reward = float(_get_assigned_number_reward(clean_api_num))
                                    inbox_msg = _format_inbox_otp_message(display_num, app_full_name, iso, owner_id, prem_app_html)
                                    result = send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    print(f"[PANEL DEBUG] Inbox send: fingerprint={event_hash[:12]}, ok={isinstance(result, dict) and result.get('ok', False)}")
                                    if isinstance(result, dict) and result.get("ok", False):
                                        panel_otp_inbox_delivered.add(inbox_key)
                                        # One valid processed OTP = one profile OTP event, even when the same number receives multiple OTPs.
                                        _account_otp_in_background(owner_id, reward)
                                    else:
                                        inbox_delivery_ok = False

                                if group_thread is not None:
                                    group_thread.join(timeout=30)
                                    group_delivery_ok = bool(group_results)
                                    for fw, result in list(group_results):
                                        print(f"[PANEL DEBUG] Group send: fingerprint={event_hash[:12]}, ok={isinstance(result, dict) and result.get('ok', False)}")
                                        if not isinstance(result, dict) or not result.get("ok", False):
                                            group_delivery_ok = False
                                    if group_delivery_ok:
                                        panel_otp_group_delivered.add(unique_id)

                                # Mark the event processed only after its required deliveries
                                # have succeeded. This prevents one failed delivery from
                                # permanently suppressing a later OTP with a different SMS.
                                group_required_ok = (unique_id in panel_otp_group_delivered) or not bot_settings.get("fw_groups", [])
                                # If no user owns this number (nobody to deliver to), the event is
                                # complete once the OTP Group got it. Otherwise it was re-processed
                                # every cycle forever (repeated saves + full stock scans = delay).
                                all_owner_inbox_ok = all(f"{unique_id}_{owner_id}" in panel_otp_inbox_delivered for owner_id in owners) if owners else True
                                print(f"[PANEL DEBUG] Event completion: fingerprint={event_hash[:12]}, group_ok={group_required_ok}, inbox_ok={all_owner_inbox_ok}")
                                if group_required_ok and all_owner_inbox_ok:
                                    panel_event_fingerprints.add(unique_id)
                                    panel_processed_events.add(unique_id)
                                    if len(panel_event_fingerprints) > 200000: panel_event_fingerprints.clear()
                                    if len(panel_processed_events) > 10000: panel_processed_events.clear()
                                    panel_otp_group_delivered.discard(unique_id)
                                    for owner_id in owners:
                                        panel_otp_inbox_delivered.discard(f"{unique_id}_{owner_id}")
                        except Exception as event_error:
                            # Isolate one Panel OTP event so an error in one SMS can never stop later SMS events.
                            print(f"[PANEL EVENT ERROR] {type(event_error).__name__}: {event_error}")
                            continue
        except Exception as e:
            print(f"[PANEL MONITOR ERROR] {type(e).__name__}: {e}")
        # Poll API providers more frequently so newly arrived OTPs are picked up sooner.
        time.sleep(2)

# ==========================================
# Firebase User Management
# ==========================================
# 🌟 Local User Cache: বারবার Firestore থেকে Read করা বন্ধ করবে!
user_cache = {}
# Values changed locally while Firebase is unavailable/failed. They are retried later.
pending_balance_sync = {}
pending_total_otp_sync = {}
# Per-user lock prevents concurrent OTP listener threads from overwriting profile stats.
otp_stats_locks = {}
otp_stats_locks_guard = threading.Lock()

def _get_otp_stats_lock(user_id):
    with otp_stats_locks_guard:
        if user_id not in otp_stats_locks:
            otp_stats_locks[user_id] = threading.Lock()
        return otp_stats_locks[user_id]

def get_user(user_id):
    # Always keep a local cache entry, even when Firebase is temporarily unavailable.
    # This prevents OTP rewards / Total OTP from appearing as 0 immediately after receipt.
    if user_id in user_cache:
        return user_cache[user_id]

    if not db:
        saved_user = local_users.get(str(user_id)) if isinstance(local_users, dict) else None
        if isinstance(saved_user, dict):
            new_user = dict(saved_user)
            new_user["user_id"] = user_id
            new_user.setdefault("balance", 0.0)
            new_user.setdefault("total_refers", 0)
            new_user.setdefault("total_otps", 0)
            new_user.setdefault("banned", False)
            new_user.setdefault("verified", False)
            new_user.setdefault("profile_name", "User")
            new_user.setdefault("otp_daily_stats", {})
            new_user.setdefault("total_otp_earnings", 0.0)
        else:
            new_user = {
                "user_id": user_id,
                "balance": 0.0,
                "total_refers": 0,
                "total_otps": 0,
                "banned": False,
                "verified": False,
                "profile_name": "User",
                "otp_daily_stats": {},
                "total_otp_earnings": 0.0
            }
        user_cache[user_id] = new_user
        return new_user

    try:
        doc_ref = db.collection('users').document(str(user_id))
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict() or {}
            if "user_id" not in data: data["user_id"] = user_id
            if "balance" not in data: data["balance"] = 0.0
            if "total_refers" not in data: data["total_refers"] = 0
            if "total_otps" not in data: data["total_otps"] = 0
            if "banned" not in data: data["banned"] = False
            if "verified" not in data: data["verified"] = False
            if "profile_name" not in data: data["profile_name"] = "User"
            if "otp_daily_stats" not in data: data["otp_daily_stats"] = {}
            if "total_otp_earnings" not in data: data["total_otp_earnings"] = 0.0
            user_cache[user_id] = data
            local_users[str(user_id)] = dict(data)
            return data

        new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "banned": False, "verified": False, "profile_name": "User", "otp_daily_stats": {}, "total_otp_earnings": 0.0}
        doc_ref.set(new_user)
        user_cache[user_id] = new_user
        local_users[str(user_id)] = dict(new_user)
        return new_user
    except Exception as e:
        # Firebase read can fail temporarily; preserve the last locally saved user data.
        print(f"⚠️ User read error for {user_id}: {e}")
        saved_user = local_users.get(str(user_id)) if isinstance(local_users, dict) else None
        if isinstance(saved_user, dict):
            new_user = dict(saved_user)
            new_user["user_id"] = user_id
            new_user.setdefault("balance", 0.0)
            new_user.setdefault("total_refers", 0)
            new_user.setdefault("total_otps", 0)
            new_user.setdefault("banned", False)
            new_user.setdefault("verified", False)
            new_user.setdefault("profile_name", "User")
            new_user.setdefault("otp_daily_stats", {})
            new_user.setdefault("total_otp_earnings", 0.0)
        else:
            new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "banned": False, "verified": False, "profile_name": "User", "otp_daily_stats": {}, "total_otp_earnings": 0.0}
        user_cache[user_id] = new_user
        local_users[str(user_id)] = dict(new_user)
        return new_user

def _bd_today_key():
    return datetime.now(BD_TZ).date().isoformat()


def _normalise_profile_name(first_name="", last_name="", fallback="User"):
    full_name = f"{first_name or ''} {last_name or ''}".strip()
    return full_name or fallback or "User"


def sync_user_identity(user_id, msg_or_user):
    """Persist the latest Telegram display name without changing existing user/account logic."""
    try:
        user_obj = msg_or_user.get("from", msg_or_user) if isinstance(msg_or_user, dict) else {}
        first_name = user_obj.get("first_name", "")
        last_name = user_obj.get("last_name", "")
        current_name = _normalise_profile_name(first_name, last_name)
        user = user_cache.get(user_id) or get_user(user_id)
        current_username = str(user_obj.get("username") or "").strip().lstrip("@")
        if user.get("profile_name") == current_name and user.get("username") == current_username:
            return
        user["profile_name"] = current_name
        user["username"] = current_username
        user_cache[user_id] = user
        local_users[str(user_id)] = dict(user)
        if db:
            try:
                db.collection("users").document(str(user_id)).set(
                    {"user_id": user_id, "profile_name": current_name, "username": current_username}, merge=True
                )
            except Exception as e:
                print(f"⚠️ Profile name sync error for {user_id}: {e}")
        save_local_db()
    except Exception as e:
        print(f"⚠️ Profile identity error for {user_id}: {e}")


def record_otp_stats(user_id, reward=0.0):
    """Persist OTP daily/7-day/lifetime reward stats. Each valid processed OTP is one event."""
    try:
        reward = float(reward or 0.0)
    except Exception:
        reward = 0.0
    if reward < 0:
        reward = 0.0

    lock = _get_otp_stats_lock(user_id)
    with lock:
        user = user_cache.get(user_id) or get_user(user_id)
        today = _bd_today_key()
        daily = user.get("otp_daily_stats") or {}
        if not isinstance(daily, dict):
            daily = {}

        entry = daily.get(today) or {"count": 0, "earnings": 0.0}
        entry["count"] = int(entry.get("count", 0) or 0) + 1
        entry["earnings"] = round(float(entry.get("earnings", 0.0) or 0.0) + reward, 6)
        daily[today] = entry

        # Keep only today + previous 6 days locally. Lifetime totals are separate.
        valid_keys = sorted(daily.keys())[-7:]
        daily = {k: daily[k] for k in valid_keys}
        user["otp_daily_stats"] = daily
        user["total_otp_earnings"] = round(float(user.get("total_otp_earnings", 0.0) or 0.0) + reward, 6)
        user_cache[user_id] = user
        local_users[str(user_id)] = dict(user)
        save_local_db()

        if db:
            try:
                db.collection("users").document(str(user_id)).set(
                    {
                        "user_id": user_id,
                        "otp_daily_stats": daily,
                        "total_otp_earnings": firestore.Increment(reward)
                    }, merge=True
                )
            except Exception as e:
                # Local DB remains authoritative fallback until the next restart/retry.
                print(f"⚠️ OTP stats Firebase sync error for {user_id}: {e}")


def get_profile_stats(user_id):
    user = user_cache.get(user_id) or get_user(user_id)
    today = _bd_today_key()
    daily = user.get("otp_daily_stats") or {}
    if not isinstance(daily, dict):
        daily = {}

    today_data = daily.get(today) or {}
    today_count = int(today_data.get("count", 0) or 0)
    today_earnings = float(today_data.get("earnings", 0.0) or 0.0)

    last7_count = 0
    last7_earnings = 0.0
    today_date = datetime.now(BD_TZ).date()
    for i in range(7):
        key = (today_date - timedelta(days=i)).isoformat()
        data = daily.get(key) or {}
        last7_count += int(data.get("count", 0) or 0)
        last7_earnings += float(data.get("earnings", 0.0) or 0.0)

    return {
        "name": user.get("profile_name", "User"),
        "uid": user_id,
        "balance": get_fresh_balance(user_id),
        "today_count": today_count,
        "today_earnings": today_earnings,
        "last7_count": last7_count,
        "last7_earnings": last7_earnings,
        "lifetime_count": int(user.get("total_otps", 0) or 0),
        "lifetime_earnings": float(user.get("total_otp_earnings", 0.0) or 0.0)
    }


def build_my_profile_text(user_id, page=1):
    stats = get_profile_stats(user_id)
    line = "━━━━━━━━━━━━━━━━━━━━"
    name = html.escape(str(stats.get("name") or "User")[:25])
    updated = datetime.now(BD_TZ).strftime("%I:%M:%S %p")
    # render_body_text() turns each emoji below into its Telegram Premium custom emoji.
    if page == 2:
        return render_body_text(
            "💎 <b>𝐌𝐘 𝐏𝐑𝐎𝐅𝐈𝐋𝐄</b> 💎\n"
            f"{line}\n"
            "📆 <b>𝐋𝐀𝐒𝐓 𝟕 𝐃𝐀𝐘𝐒</b>\n"
            f"📩 <b>OTP Received:</b> <code>{stats['last7_count']}</code>\n"
            f"💵 <b>Earnings:</b> <code>{stats['last7_earnings']:.2f} TK</code>\n"
            f"{line}\n"
            "🏆 <b>𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄</b>\n"
            f"📈 <b>Total OTP:</b> <code>{stats['lifetime_count']}</code>\n"
            f"💰 <b>Total Earnings:</b> <code>{stats['lifetime_earnings']:.2f} TK</code>\n"
            f"{line}\n"
            f"🕓 <i>Updated: {updated}</i>"
        )
    return render_body_text(
        "💎 <b>𝐌𝐘 𝐏𝐑𝐎𝐅𝐈𝐋𝐄</b> 💎\n"
        f"{line}\n"
        f"👤 <b>Name:</b> {name}\n"
        f"🆔 <b>ID:</b> <code>{stats['uid']}</code>\n"
        f"{line}\n"
        f"💰 <b>Balance:</b> <code>৳ {stats['balance']:.2f}</code>\n"
        f"📩 <b>Today OTP:</b> <code>{stats['today_count']}</code>\n"
        f"💵 <b>Today Earnings:</b> <code>{stats['today_earnings']:.2f} TK</code>\n"
        f"{line}\n"
        f"🕓 <i>Updated: {updated}</i>"
    )


def my_profile_keyboard(page=1):
    close_btn = {"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}
    withdrawal_btn = {"text": "WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "open_withdrawal", "style": "danger"}
    if page == 2:
        return {"inline_keyboard": [
            [
                {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "my_profile_back", "style": "primary"},
                withdrawal_btn
            ],
            [
                {"text": "REFRESH", "icon_custom_emoji_id": "6053323501073341449", "callback_data": "my_profile_next", "style": "success"},
                close_btn
            ]
        ]}
    return {"inline_keyboard": [
        [
            {"text": "MORE STATS", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "my_profile_next", "style": "primary"},
            withdrawal_btn
        ],
        [
            {"text": "REFRESH", "icon_custom_emoji_id": "6053323501073341449", "callback_data": "my_profile", "style": "success"},
            close_btn
        ]
    ]}


def increment_total_otps(user_id, amount=1):
    """Increment Total OTP in Firebase when available and ALWAYS sync the local cache."""
    try:
        amount = int(amount)
    except Exception:
        amount = 1
    if amount <= 0:
        return

    user = user_cache.get(user_id) or get_user(user_id)
    try:
        current = int(user.get("total_otps", 0) or 0)
    except Exception:
        current = 0
    user["total_otps"] = current + amount
    user_cache[user_id] = user
    local_users[str(user_id)] = dict(user)

    if db:
        try:
            db.collection('users').document(str(user_id)).set(
                {"user_id": user_id, "total_otps": firestore.Increment(amount)},
                merge=True
            )
            pending_total_otp_sync.pop(user_id, None)
        except Exception as e:
            pending_total_otp_sync[user_id] = user["total_otps"]
            save_local_db()
            print(f"⚠️ Total OTP update error for {user_id}: {e}")
    else:
        pending_total_otp_sync[user_id] = user["total_otps"]
        save_local_db()

def update_balance(user_id, amount):
    """Add OTP reward to balance and keep the displayed balance in sync even if Firebase fails."""
    try:
        amount = float(amount)
    except Exception:
        return
    if amount == 0:
        return

    user = user_cache.get(user_id) or get_user(user_id)
    try:
        current = float(user.get("balance", 0.0) or 0.0)
    except Exception:
        current = 0.0

    # Update local cache FIRST so Inbox and Withdraw immediately show the added reward.
    user["balance"] = current + amount
    user_cache[user_id] = user
    local_users[str(user_id)] = dict(user)

    if db:
        try:
            doc_ref = db.collection("users").document(str(user_id))
            doc_ref.set(
                {"user_id": user_id, "balance": firestore.Increment(amount)},
                merge=True
            )
            pending_balance_sync.pop(user_id, None)
        except Exception as e:
            pending_balance_sync[user_id] = user["balance"]
            save_local_db()
            print(f"⚠️ Balance update error for {user_id}: {e}")
    else:
        pending_balance_sync[user_id] = user["balance"]
        save_local_db()

FRESH_READ_TTL = 15  # seconds a Firestore balance/total-OTP read is reused for repeat clicks
_fresh_balance_ts = {}
_fresh_total_otp_ts = {}

def get_fresh_balance(user_id):
    """Read the latest balance, but never discard a locally-added reward that still needs syncing."""
    cached_user = user_cache.get(user_id) or get_user(user_id)
    # update_balance() already writes the local cache first, so a recent read is still correct.
    if (user_id not in pending_balance_sync
            and time.time() - _fresh_balance_ts.get(user_id, 0) < FRESH_READ_TTL):
        return float(cached_user.get("balance", 0.0) or 0.0)

    # If the previous Firebase write failed, retry the exact local balance first.
    if user_id in pending_balance_sync:
        local_balance = float(cached_user.get("balance", pending_balance_sync[user_id]) or 0.0)
        if db:
            try:
                db.collection("users").document(str(user_id)).set(
                    {"user_id": user_id, "balance": local_balance},
                    merge=True
                )
                pending_balance_sync.pop(user_id, None)
            except Exception as e:
                print(f"⚠️ Balance retry error for {user_id}: {e}")
        return local_balance

    try:
        if db:
            doc = db.collection("users").document(str(user_id)).get()
            if doc.exists:
                data = doc.to_dict() or {}
                balance = float(data.get("balance", 0.0) or 0.0)
                if user_id in user_cache:
                    user_cache[user_id]["balance"] = balance
                _fresh_balance_ts[user_id] = time.time()
                return balance
    except Exception as e:
        print(f"⚠️ Balance refresh error for {user_id}: {e}")
    return float(cached_user.get("balance", 0.0) or 0.0)

def add_referral(inviter_id, new_user_id):
    if not db.collection('users').document(str(new_user_id)).get().exists:
        get_user(new_user_id) 
        reward = bot_settings.get("refer_reward", 0.2)
        update_balance(inviter_id, reward)
        db.collection('users').document(str(inviter_id)).update({"total_refers": firestore.Increment(1)})
        if inviter_id in user_cache:
            user_cache[inviter_id]["total_refers"] = user_cache[inviter_id].get("total_refers", 0) + 1
        
        # আপনার দেওয়া নতুন ডিজাইন
        ref_msg = (
            f"{PEM['gift']} <b>New Referral !</b>\n"
            f"------------------\n"
            f"🔥 <b>You Received {reward} TK</b>\n"
            f"------------------\n"
            f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
        )
        send_message(inviter_id, render_body_text(ref_msg))

# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def _services_for_mode(mode):
    """Service names to show for GET NUMBER STOCK / GET NUMBER API (None = old combined list)."""
    local_srvs = set(b["service"] for b in number_batches.values() if b.get("numbers"))
    api_srvs = (set(bot_settings.get("stex_services", {}).keys())
                | set(bot_settings.get("voltx_services", {}).keys())
                | set(bot_settings.get("zenex_services", {}).keys()))
    if mode == "stock":
        return local_srvs
    if mode == "api":
        return api_srvs
    return local_srvs | api_srvs

def _recent_hit_index(traffic, current_time, source=None, window=120):
    """One pass over recent_traffic for the auto add/delete logic.
    Replaces the old per-service/per-country/per-range loops that rescanned the whole
    list (and ran get_flag_info_html on every record) and froze the bot for seconds.
    Returns (service_hits, (service, country)_hits, (service, range)_hits)."""
    srv_hits, country_hits, range_hits = {}, {}, {}
    name_cache = {}
    for t in traffic:
        if current_time - t.get("time", 0) > window:
            continue
        if source is not None and t.get("source") != source:
            continue
        srv = str(t.get("service", "")).upper()
        has_rr = "real_range" in t
        if has_rr:
            srv_hits[srv] = srv_hits.get(srv, 0) + 1
            iso = t.get("iso")
            try:
                name = name_cache.get(iso)
                if name is None:
                    name = get_flag_info_html(iso, return_full_name=True).title()
                    name_cache[iso] = name
                ck = (srv, name)
                country_hits[ck] = country_hits.get(ck, 0) + 1
            except Exception:
                pass
        rr = t.get("real_range")
        if rr is not None:
            rk = (srv, rr)
            range_hits[rk] = range_hits.get(rk, 0) + 1
    return srv_hits, country_hits, range_hits

def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [
            {"text": "Get Number (V1)", "icon_custom_emoji_id": "5337132498965010628", "style": "primary"},
            {"text": "Get Number (V2)", "icon_custom_emoji_id": "5336972142066047577", "style": "success"}
        ],
        [
            {"text": "MY PROFILE", "icon_custom_emoji_id": "5352838545826420397", "style": "primary"},
            {"text": "LEADERBOARD", "icon_custom_emoji_id": "5353032893096567467", "style": "success"}
        ],
        [
            {"text": "iX Shop", "icon_custom_emoji_id": "5190576863226933563", "style": "danger"},
            {"text": "SELL ID", "icon_custom_emoji_id": "5190576863226933563", "style": "success"}
        ],
        [
            {"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "primary"},
            {"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success"}
        ]
    ]
    if is_admin(user_id): 
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    users_count = len(all_known_users) # 🌟 Zero Cost User Count!
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "SELL ID", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "admin_sell_id_menu", "style": "primary"},
         {"text": "iX Shop", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "admin_shop_menu", "style": "success"}],
        [{"text": "Withdrawal Management", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "withdrawal_management", "style": "primary"}],
        [{"text": "Manage Service & Country", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_service_country", "style": "primary"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def admin_sell_id_keyboard():
    return {"inline_keyboard": [
        [{"text": "🔗 Set SELL ID Link", "callback_data": "set_sell_id_link", "style": "primary"}],
        [{"text": "📝 Edit SELL ID Text", "callback_data": "set_sell_id_text", "style": "success"}],
        [{"text": "🔄 Reset Default Text", "callback_data": "reset_sell_id_text", "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def admin_shop_keyboard():
    return {"inline_keyboard": [
        [{"text": "🔗 Set Shop Link", "callback_data": "set_shop_link", "style": "primary"}],
        [{"text": "📝 Edit Shop Text", "callback_data": "set_shop_text", "style": "success"}],
        [{"text": "🔄 Reset Default Text", "callback_data": "reset_shop_text", "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
         {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
        [{"text": "Zenex Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_control", "style": "success"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}], 
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"}],
        [{"text": "PXN Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "dxa_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    # 🌟 Fast & Free User Management Stats!
    total = len(all_known_users)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def build_all_user_balance_report():
    """Read all accounts once and use the same snapshot for total and CSV."""
    import io
    from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

    # Read Firebase first. A failed/partial read must never look like a full total.
    users = {}
    if db:
        for doc in db.collection("users").stream():
            users[str(doc.id)] = dict(doc.to_dict() or {})
    local_snapshot = {}
    for uid, user in list(local_users.items()):
        if isinstance(user, dict):
            local_snapshot[str(uid)] = dict(user)
    for uid, user in list(user_cache.items()):
        if isinstance(user, dict):
            local_snapshot[str(uid)] = dict(user)
    for uid, user in local_snapshot.items():
        if uid not in users:
            users[uid] = user
        else:
            # Identity can be newer locally, but remote balances remain authoritative.
            for key in ("username", "profile_name"):
                if key in user:
                    users[uid][key] = user[key]
    for uid, balance in list(pending_balance_sync.items()):
        key = str(uid)
        users.setdefault(key, dict(local_snapshot.get(key, {})))["balance"] = balance
    missing = {str(uid) for uid in list(all_known_users)} - set(users)
    if missing:
        raise ValueError(f"Balance records unavailable for {len(missing)} known users")

    rows = []
    total = Decimal("0.00")
    for uid, user in users.items():
        try:
            balance = Decimal(str(user.get("balance", 0) or 0))
            if not balance.is_finite():
                raise ValueError("Non-finite balance")
            balance = balance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError(f"Invalid balance for user {uid}")
        username = str(user.get("username") or "").strip().lstrip("@")
        name = str(user.get("profile_name") or "User")
        # Keep spreadsheet applications from interpreting a display name as a formula.
        if name.lstrip().startswith(("=", "+", "-", "@")):
            name = "'" + name
        rows.append((uid, "@" + username if username else "N/A", name, balance))
        total += balance
    rows.sort(key=lambda row: (-row[3], row[0]))
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["User ID", "Username", "Name", "Balance (BDT)"])
    for uid, username, name, balance in rows:
        writer.writerow([uid, username, name, f"{balance:.2f}"])
    return len(rows), total, output.getvalue().encode("utf-8-sig")


def send_all_user_balance_report(chat_id):
    """Generate an admin-only report without blocking the callback handler."""
    try:
        count, total, content = build_all_user_balance_report()
    except Exception as error:
        print(f"[ALL USER BALANCE] Report failed: {error}")
        send_message(chat_id, render_body_text("❌ Could not load every user's balance. Please try again. No incomplete total was shown."))
        return
    stamp = datetime.now(BD_TZ).strftime("%Y-%m-%d %H:%M:%S")
    source = "Database + pending local updates" if db else "Saved local records (database offline)"
    caption = (f"💰 <b>ALL USER BALANCE</b>\n\n"
               f"👥 Total users: <b>{count}</b>\n"
               f"💵 Total balance: <b>৳{total:.2f}</b>\n"
               f"🕒 {stamp} (Bangladesh)\n"
               f"Source: {source}\n\n"
               "CSV: User ID, Username, Name, Balance (BDT).\n"
               "N/A = username not available yet.")
    try:
        response = requests.post(
            f"{BASE_URL}/sendDocument",
            data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
            files={"document": ("all_user_balances.csv", content, "text/csv")},
            timeout=60,
        )
        response.raise_for_status()
        if not response.json().get("ok"):
            raise ValueError("Telegram rejected the CSV")
    except Exception:
        send_message(chat_id, render_body_text("❌ Balance report delivery failed. Please try again."))


def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "SHOW ALL USER", "callback_data": "um_all_page_0", "style": "primary"},
         {"text": "SHOW BANED USER", "callback_data": "um_banned_page_0", "style": "danger"}],
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "All User Balance", "callback_data": "um_all_user_balance", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}


def _get_user_management_listing(banned_only=False):
    """Return a best-effort user snapshot for the admin user listing."""
    users = {}
    if db:
        try:
            for doc in db.collection("users").stream():
                info = dict(doc.to_dict() or {})
                info.setdefault("user_id", doc.id)
                users[str(doc.id)] = info
        except Exception as exc:
            print(f"[USER MANAGEMENT LIST ERROR] {type(exc).__name__}: {exc}")
    # Local sources fill gaps when Firebase is unavailable or incomplete.
    for source in (local_users, user_cache):
        if isinstance(source, dict):
            for uid, info in source.items():
                if isinstance(info, dict):
                    users.setdefault(str(uid), dict(info))
    for uid in all_known_users:
        users.setdefault(str(uid), {"user_id": str(uid), "profile_name": "User", "banned": False})
    if banned_only:
        users = {uid: info for uid, info in users.items() if bool(info.get("banned", False)) or (uid.isdigit() and user_banned_cache.get(int(uid), {}).get("banned", False))}
    return sorted(users.items(), key=lambda item: (not bool(item[1].get("banned", False)), str(item[0])))


def user_management_listing_keyboard(listing_type, page, total_pages):
    prefix = "um_banned_page_" if listing_type == "banned" else "um_all_page_"
    kb = []
    nav = []
    if page > 0:
        nav.append({"text": "◀️ Previous", "callback_data": f"{prefix}{page - 1}", "style": "primary"})
    if page + 1 < total_pages:
        nav.append({"text": "Next ▶️", "callback_data": f"{prefix}{page + 1}", "style": "primary"})
    if nav:
        kb.append(nav)
    kb.append([{"text": "Back to User Management", "callback_data": "user_management", "style": "danger"}])
    return {"inline_keyboard": kb}


def render_user_management_listing(listing_type, page):
    banned_only = listing_type == "banned"
    users = _get_user_management_listing(banned_only=banned_only)
    page_size = 10
    total_pages = max(1, (len(users) + page_size - 1) // page_size)
    page = max(0, min(int(page), total_pages - 1))
    start = page * page_size
    visible = users[start:start + page_size]
    title = "🚫 <b>BANNED USERS</b>" if banned_only else "👥 <b>ALL USERS</b>"
    lines = [title, f"Total: <b>{len(users)}</b>", f"Page {page + 1}/{total_pages}", ""]
    if not visible:
        lines.append("No users found.")
    else:
        for index, (uid, info) in enumerate(visible, start=start + 1):
            name = html.escape(str(info.get("profile_name") or info.get("name") or "User"))
            status = " 🚫" if bool(info.get("banned", False)) else ""
            if not banned_only:
                username_value = str(info.get("username") or "").strip()
                username = html.escape("@" + username_value.lstrip("@")) if username_value else "N/A"
                try:
                    balance = float(info.get("balance", 0) or 0)
                except (TypeError, ValueError):
                    balance = 0.0
                lines.append(f"{index}. {name}{status} — <code>{html.escape(str(uid))}</code>\n   Username: <b>{username}</b> | Balance: <b>৳{balance:.2f}</b>")
            else:
                lines.append(f"{index}. {name}{status} — <code>{html.escape(str(uid))}</code>")
    return render_body_text("\n".join(lines)), user_management_listing_keyboard(listing_type, page, total_pages)

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit Search Number", "icon_custom_emoji_id": "5190645917711114179", "callback_data": "md_edit_search_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "md_edit_withdrawal", "style": "danger"},
         {"text": "Edit SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "md_edit_support", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Set OTP Group Emojis", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "setup_otp_group_emojis", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def _emoji_management_services():
    services = set()
    local_srvs = {
        str(b.get("service", "")).strip()
        for b in number_batches.values()
        if isinstance(b, dict) and b.get("numbers") and str(b.get("service", "")).strip()
    }
    services.update(local_srvs)
    for key in ("stex_services", "voltx_services", "zenex_services"):
        services.update(str(s) for s in (bot_settings.get(key, {}) or {}).keys() if str(s).strip())
    return sorted(services, key=str.casefold)


def _emoji_management_countries():
    countries = set()
    for key in ("stex_services", "voltx_services", "zenex_services"):
        for service_data in (bot_settings.get(key, {}) or {}).values():
            if isinstance(service_data, dict):
                countries.update(str(c) for c in service_data.keys() if str(c).strip())
    for batch in number_batches.values():
        if isinstance(batch, dict) and str(batch.get("country", "")).strip():
            countries.add(str(batch.get("country")).strip())
    return sorted(countries, key=str.casefold)


def _emoji_management_target_keyboard():
    return {"inline_keyboard": [
        [{"text": "SERVICE", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "emoji_target_service", "style": "primary"},
         {"text": "COUNTRY", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "emoji_target_country", "style": "primary"}],
        [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]
    ]}


def _emoji_management_services_keyboard():
    kb = []
    apps_db = bot_settings.get("premium_apps", {}) or {}
    for service in _emoji_management_services():
        emoji_id = "5257969839313526622"
        for app_key, app_data in apps_db.items():
            app_name = str((app_data or {}).get("name", app_key)).upper()
            if service.upper() == app_name or service.upper() in app_name or app_name in service.upper():
                emoji_id = (app_data or {}).get("id") or emoji_id
                break
        kb.append([{"text": service, "icon_custom_emoji_id": emoji_id, "callback_data": f"emoji_set_srv_{quote(service, safe='')}", "style": "primary"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "add_single_emoji", "style": "danger"}])
    return {"inline_keyboard": kb}


def _emoji_management_countries_keyboard():
    kb = []
    flags_db = bot_settings.get("premium_flags", {}) or {}
    for country in _emoji_management_countries():
        emoji_id = "5780471598922337683"
        label_upper = str(country).upper()
        flag_items = sorted(flags_db.items(), key=lambda item: len(str((item[1] or {}).get("name", "") or "")), reverse=True)
        for code, data in flag_items:
            data = data or {}
            name = str(data.get("name", "") or "").strip()
            iso = str(data.get("iso", "") or "").strip().upper()
            if (label_upper == name.upper() or name.upper() in label_upper or label_upper == iso or label_upper == str(code).upper()) and data.get("id"):
                emoji_id = data["id"]
                break
        kb.append([{"text": country, "icon_custom_emoji_id": emoji_id, "callback_data": f"emoji_set_cnt_{quote(country, safe='')}", "style": "primary"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "add_single_emoji", "style": "danger"}])
    return {"inline_keyboard": kb}


def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}




def stex_control_keyboard():
    auto_status = "ON" if bot_settings.get("stex_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_stex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def zenex_control_keyboard():
    auto_status = "ON" if bot_settings.get("zenex_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Zenex Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_zenex_keys", "style": "danger"}],
        [{"text": "Manage Zenex Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_zenex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_zenex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def voltx_control_keyboard():
    auto_status = "ON" if bot_settings.get("voltx_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_voltx_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def _price_service_key(service):
    """Stable service key used by the persistent price mapping."""
    return str(service or "").strip()


def _country_display_info(country):
    """Return (display_name, flag_char, premium_emoji_id) for a configured country."""
    value = str(country or "").strip()
    flags_db = bot_settings.get("premium_flags", {}) or {}
    value_upper = value.upper()

    for code, data in flags_db.items():
        data = data or {}
        name = str(data.get("name", "")).strip()
        iso = str(data.get("iso", "")).strip().upper()
        if value_upper == name.upper() or value_upper == iso or value == str(code):
            return name or value, data.get("char", _iso_to_flag(iso)), data.get("id")

    # If the service stores a numeric calling code, use the existing fallback DB.
    if value.isdigit():
        info = _fallback_country_for_number(value)
        return info[3], info[0], None

    # Existing service data normally stores the country name, so preserve it if
    # there is no Premium Flag configured yet.
    return value or "Unknown", "🌍", None


def _get_service_country_price(service, country, fallback=None):
    """Get the configured service+country price, otherwise return fallback/global reward."""
    service_key = _price_service_key(service)
    country_key = str(country or "").strip()
    prices = bot_settings.get("service_country_prices", {}) or {}
    service_prices = prices.get(service_key, {}) or {}

    # Exact country-name match first.
    if country_key in service_prices:
        try:
            return float(service_prices[country_key])
        except (TypeError, ValueError):
            pass

    # Be tolerant of legacy/case differences in country names.
    for saved_country, saved_price in service_prices.items():
        if str(saved_country).strip().lower() == country_key.lower():
            try:
                return float(saved_price)
            except (TypeError, ValueError):
                break

    if fallback is not None:
        try:
            return float(fallback)
        except (TypeError, ValueError):
            pass
    return float(bot_settings.get("otp_reward", 0.0) or 0.0)


def _get_price_for_number(service, number, fallback=None):
    """Resolve a service-country override for a real assigned number."""
    try:
        country_name = get_flag_info_html(str(number or ""), return_full_name=True)
    except Exception:
        country_name = ""
    return _get_service_country_price(service, country_name, fallback=fallback)


def _normalize_assigned_number(number):
    """Normalize a phone number so reward lookups survive +/space/- formatting differences."""
    return str(number or "").replace("+", "").replace(" ", "").replace("-", "").strip()


def _set_assigned_number_rate(number, rate):
    """Store the reward under a normalized key for reliable OTP matching."""
    key = _normalize_assigned_number(number)
    if not key:
        return
    try:
        assigned_number_rates[key] = float(rate)
    except (TypeError, ValueError):
        assigned_number_rates[key] = float(bot_settings.get("otp_reward", 0.0) or 0.0)


def _get_assigned_number_reward(number, default=None):
    """Return the exact reward assigned to this number; never replace a local batch rate with a service price."""
    key = _normalize_assigned_number(number)
    if key:
        # First try the normalized key.
        if key in assigned_number_rates:
            try:
                return float(assigned_number_rates[key])
            except (TypeError, ValueError):
                pass
        # Backward compatibility for old saved databases that used formatted keys.
        for saved_num, saved_rate in assigned_number_rates.items():
            if _normalize_assigned_number(saved_num) == key:
                try:
                    return float(saved_rate)
                except (TypeError, ValueError):
                    break
    if default is None:
        default = bot_settings.get("otp_reward", 0.0)
    try:
        return float(default or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _price_services():
    """Return services from locally uploaded number batches."""
    return sorted({str(batch.get("service", "")).strip() for batch in number_batches.values()
                   if isinstance(batch, dict) and str(batch.get("service", "")).strip()}, key=str.casefold)


def _price_countries_for_service(service):
    countries = set()
    for batch in number_batches.values():
        if isinstance(batch, dict) and str(batch.get("service", "")).strip() == str(service).strip():
            country = str(batch.get("country", "")).strip()
            if country:
                countries.add(country)
    return sorted(countries, key=str.casefold)


def _managed_services():
    """Dynamically collect service names from locally uploaded batches."""
    services = set()
    for batch in number_batches.values():
        if isinstance(batch, dict) and str(batch.get("service", "")).strip():
            services.add(str(batch.get("service")).strip())
    return sorted(services, key=str.casefold)


def _managed_local_services():
    """Services that have at least one locally uploaded number-file batch."""
    return sorted({str(batch.get("service", "")).strip() for batch in number_batches.values()
                   if isinstance(batch, dict) and str(batch.get("service", "")).strip()}, key=str.casefold)


def _managed_countries(service, local_only=False):
    """Return dynamic country labels for one service; optionally limit to uploaded files."""
    countries = set()
    for batch in number_batches.values():
        if not isinstance(batch, dict) or str(batch.get("service", "")).strip() != str(service).strip():
            continue
        country = str(batch.get("country", "")).strip()
        if country:
            countries.add(country)
    return sorted(countries, key=str.casefold)


def _msc_key(text):
    """Short fixed-size token for callback_data.
    Telegram rejects callback_data over 64 BYTES. Service/country names with flags/emoji/long text
    become huge after quote() (one emoji = 12 chars), so the button (or the whole keyboard) was
    silently refused and tapping a country did nothing. A 12-char hash is always safe."""
    return hashlib.md5(str(text).strip().encode("utf-8")).hexdigest()[:12]


def _msc_find_service(key, local_only=False):
    services = _managed_local_services() if local_only else _managed_services()
    for service in services:
        if _msc_key(service) == key:
            return service
    return None


def _msc_find_country(service, key, local_only=False):
    for country in _managed_countries(service, local_only=local_only):
        if _msc_key(country) == key:
            return country
    return None


def _msc_refresh(chat_id, msg_id, text, reply_markup):
    """edit_message, but never fail silently (old behaviour: user saw nothing happen)."""
    res = edit_message(chat_id, msg_id, text, reply_markup=reply_markup)
    if not (res or {}).get("ok"):
        desc = str((res or {}).get("description", "")).lower()
        if "not modified" not in desc:
            send_message(chat_id, text, reply_markup=reply_markup)
    return res


def _manage_service_country_keyboard():
    return {"inline_keyboard": [
        [{"text": "Rename Service", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "msc_rename", "style": "primary"}],
        [{"text": "Delete Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "msc_delete", "style": "danger"}],
        [{"text": "Set OTP Rate", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "msc_rate", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}],
    ]}


def _managed_services_keyboard(action, local_only=False):
    kb = []
    services = _managed_local_services() if local_only else _managed_services()
    for service in services:
        kb.append([{"text": service, "callback_data": f"msc_srv_{action}_{_msc_key(service)}", "style": "primary"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_service_country", "style": "danger"}])
    return {"inline_keyboard": kb}


def _managed_countries_keyboard(action, service, local_only=False):
    kb = []
    for country in _managed_countries(service, local_only=local_only):
        label = country
        if action == "rate":
            fallback = bot_settings.get("otp_reward", 0.0)
            for batch in number_batches.values():
                if str(batch.get("service", "")).strip() == service and str(batch.get("country", "")).strip() == country:
                    fallback = batch.get("rate", fallback)
                    break
            price = _get_service_country_price(service, country, fallback=fallback)
            label = f"{country} | {price:g} TK"
        kb.append([{"text": label, "callback_data": f"msc_cnt_{action}_{_msc_key(service)}__{_msc_key(country)}", "style": "success" if action == "rate" else "danger"}])
    back_action = "msc_rename" if action == "rename" else "msc_delete" if action == "delete" else "msc_rate"
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_action, "style": "danger"}])
    return {"inline_keyboard": kb}


def set_price_services_keyboard():
    kb = []
    for service in _price_services():
        apps_db = bot_settings.get("premium_apps", {}) or {}
        emoji_id = "5352694861990501856"
        for app_key, app_data in apps_db.items():
            if service.upper() == str(app_key).upper() or service.upper() in str(app_key).upper() or str(app_key).upper() in service.upper():
                if app_data.get("id"):
                    emoji_id = app_data["id"]
                break
        kb.append([{"text": service, "icon_custom_emoji_id": emoji_id, "callback_data": f"sp_srv_{quote(str(service), safe='')}", "style": "primary"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "danger"}])
    return {"inline_keyboard": kb}


def set_price_countries_keyboard(service):
    kb = []
    for country in _price_countries_for_service(service):
        name, flag_char, emoji_id = _country_display_info(country)
        price = _get_service_country_price(service, country, fallback=bot_settings.get("otp_reward", 0.0))
        text = f"{name} | {price:g} TK"
        btn = {"text": text, "callback_data": f"sp_cnt_{quote(str(service), safe='')}__{quote(str(country), safe='')}", "style": "success"}
        if emoji_id:
            btn["icon_custom_emoji_id"] = emoji_id
        kb.append([btn])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "set_price", "style": "danger"}])
    return {"inline_keyboard": kb}


def set_price_country_prompt_keyboard(service):
    return {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"sp_srv_{quote(str(service), safe='')}", "style": "danger"}]]}


def dxa_control_keyboard():
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "dxa_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "dxa_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "dxa_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "dxa_sup_link", "style": "success"},
         {"text": "SET PRICE", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "set_price", "style": "primary"}],
        [{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def withdrawal_management_keyboard():
    w_status = "ON" if bot_settings.get("withdraw_on", True) else "OFF"
    payout_group = str(bot_settings.get("payout_group", "") or "").strip()
    payout_label = "Payout Group: SET" if payout_group else "Payout Group: NOT SET"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    kb = [
        [{"text": f"Withdrawal Request: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "dxa_toggle_w", "style": "success" if bot_settings.get("withdraw_on", True) else "danger"}],
        [{"text": f"Withdrawal Group: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "dxa_w_group", "style": "success" if bot_settings.get("w_group") else "danger"}],
        [{"text": "Withdraw Method", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": "Withdrawal Requests", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "withdrawal_requests", "style": "primary"}],
        [{"text": payout_label, "icon_custom_emoji_id": "5420517437885943844", "callback_data": "set_payout_group", "style": "success"}],
    ]
    # For a public @username or t.me link, provide a direct group-opening button.
    if payout_group.startswith("https://t.me/") or payout_group.startswith("http://t.me/"):
        kb.append([{"text": "Open Payout Group", "icon_custom_emoji_id": "5420517437885943844", "url": payout_group, "style": "primary"}])
    elif payout_group.startswith("@"):
        kb.append([{"text": "Open Payout Group", "icon_custom_emoji_id": "5420517437885943844", "url": "https://t.me/" + payout_group[1:], "style": "primary"}])
    kb.append([{"text": "⬅️ Back to Admin Panel", "callback_data": "back_to_admin", "style": "danger"}])
    return {"inline_keyboard": kb}

def pending_withdrawals_keyboard():
    kb = []
    items = list(pending_withdrawals.items())
    if not items:
        kb.append([{"text": "🔄 Refresh", "callback_data": "withdrawal_requests", "style": "success"}])
    else:
        for req_id, req in items[:30]:
            label = f"{req.get('full_name', req.get('user_id', 'User'))} · {req.get('amount', 0)} TK"
            kb.append([{"text": label[:60], "callback_data": f"wview_{req_id}", "style": "primary"}])
        kb.append([{"text": "🔄 Refresh", "callback_data": "withdrawal_requests", "style": "success"}])
    kb.append([{"text": "⬅️ Back", "callback_data": "withdrawal_management", "style": "danger"}])
    return {"inline_keyboard": kb}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703" 
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "🌐 Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
        
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    """Show each configured Get Number service's share of received OTPs."""
    current_time = time.time()
    services = {str(b["service"]).strip() for b in number_batches.values()
                if b.get("numbers") and b.get("service")}
    for key in ("stex_services", "voltx_services", "zenex_services"):
        services.update(str(name).strip() for name in bot_settings.get(key, {}))
    labels = {name.casefold(): name for name in sorted(services) if name}
    counts = {name: 0 for name in labels.values()}
    for event in list(recent_traffic):
        if event.get("traffic_source") != "otp_group":
            continue
        try:
            age = current_time - float(event.get("time", 0))
        except (TypeError, ValueError):
            continue
        if not 0 <= age <= 1800:
            continue
        # New events retain the selected service even after assignment changes.
        # Legacy events only count when their stored label matches exactly;
        # never guess which Facebook variant an old generic event belongs to.
        service = str(event.get("traffic_service") or event.get("service") or "").strip()
        label = labels.get(service.casefold())
        if label:
            counts[label] += 1

    total = sum(counts.values())
    txt = "📊 <b>SERVICE TRAFFIC (LAST 30 MINUTES)</b>\n\n"
    if not counts:
        txt += "<i>No services available.</i>\n"
    elif not total:
        txt += "<i>No OTPs received for these services in the last 30 minutes.</i>\n\n"
        for label in sorted(counts, key=str.casefold):
            txt += f"{html.escape(label)} 0%\n"
    else:
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold())):
            percentage = count * 100 / total
            percent_text = f"{percentage:.1f}".rstrip("0").rstrip(".")
            txt += f"{html.escape(label)} <b>{percent_text}%</b>\n"
    txt += f"\nTotal OTPs: <b>{total}</b>\n<i>Share of received OTPs, not success rate.</i>"
    kb = [
        [{"text": "Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "refresh_traffic", "style": "primary"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}],
    ]
    return render_body_text(txt), {"inline_keyboard": kb}

def build_daily_leaderboard_ui():
    """Build the user-facing daily OTP leaderboard in a premium UI using Bangladesh time."""
    today = _bd_today_key()
    today_label = datetime.now(BD_TZ).strftime("%d %b %Y")
    updated_str = datetime.now(BD_TZ).strftime("%I:%M:%S %p")

    # Merge the persisted local users with the in-memory cache so a restart
    # cannot lose the daily mapping/statistics.
    users_by_id = {}
    for uid, user in (local_users or {}).items():
        if isinstance(user, dict):
            users_by_id[str(uid)] = user
    for uid, user in (user_cache or {}).items():
        if isinstance(user, dict):
            users_by_id[str(uid)] = user

    all_ranked = []
    total_today_otps = 0
    total_today_earnings = 0.0
    for uid, user in users_by_id.items():
        daily = user.get("otp_daily_stats") or {}
        if not isinstance(daily, dict):
            continue
        entry = daily.get(today) or {}
        try:
            count = int(entry.get("count", 0) or 0)
        except Exception:
            count = 0
        if count <= 0:
            continue
        try:
            earnings = float(entry.get("earnings", 0.0) or 0.0)
        except Exception:
            earnings = 0.0
        total_today_otps += count
        total_today_earnings += earnings
        name = str(user.get("profile_name") or "User").strip() or "User"
        all_ranked.append((count, earnings, name, uid))

    # OTP count is the ranking criterion; earnings are only displayed.
    all_ranked.sort(key=lambda item: (-item[0], -item[1], item[2].lower(), str(item[3])))
    ranking = all_ranked[:5]

    txt = (
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "     🏆 <b>𝐃𝐀𝐈𝐋𝐘 𝐋𝐄𝐀𝐃𝐄𝐑𝐁𝐎𝐀𝐑𝐃</b> 🏆\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"📅 <b>Date:</b> <code>{today_label}</code>\n"
        "⏰ <b>Reset:</b> <code>12:00 AM (BD Time)</code>\n"
        f"📩 <b>Today Total:</b> <code>{total_today_otps} OTP</code>  •  <code>৳{total_today_earnings:.2f}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    if not ranking:
        txt += (
            "<blockquote>📭 <b>No OTP activity recorded yet today.</b>\n"
            "<i>Receive OTPs to claim the #1 spot!</i></blockquote>\n\n"
        )
    else:
        txt += "🌟 <b>𝐓𝐎𝐏 𝟓 𝐏𝐄𝐑𝐅𝐎𝐑𝐌𝐄𝐑𝐒</b>\n\n"
        rank_badges = {
            1: "🥇",
            2: "🥈",
            3: "🥉",
            4: "4️⃣",
            5: "5️⃣",
        }
        lines_out = []
        for rank, (count, earnings, name, _uid) in enumerate(ranking, 1):
            safe_name = html.escape(name[:22])
            badge = rank_badges.get(rank, f"#{rank}")
            lines_out.append(
                f"{badge} <b>{safe_name}</b>\n"
                f"     📩 <code>{count} OTP</code>  •  💵 <code>৳{earnings:.2f}</code>"
            )
        txt += "<blockquote>" + "\n".join(lines_out) + "</blockquote>\n\n"

    txt += (
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🕓 <i>Updated: {updated_str}</i>"
    )

    # Controls for the PUBLIC Main Menu leaderboard only.
    # Admin Panel leaderboard remains separate and unchanged.
    kb = {
        "inline_keyboard": [
            [
                {"text": "REFRESH", "icon_custom_emoji_id": "6053323501073341449", "callback_data": "public_lb_refresh", "style": "success"},
                {"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "public_lb_close", "style": "danger"}
            ]
        ]
    }

    return render_body_text(txt), kb


def build_withdrawal_ui(chat_id, include_profile_back=False):
    u_data = get_user(chat_id)
    bal = get_fresh_balance(chat_id)
    u_data["balance"] = bal

    total_otp = int(u_data.get("total_otps", 0) or 0)
    if chat_id in pending_total_otp_sync:
        total_otp = int(pending_total_otp_sync[chat_id])
        if db:
            try:
                db.collection("users").document(str(chat_id)).set(
                    {"user_id": chat_id, "total_otps": total_otp},
                    merge=True
                )
                pending_total_otp_sync.pop(chat_id, None)
            except Exception as e:
                print(f"⚠️ Total OTP retry error for {chat_id}: {e}")
    elif db and time.time() - _fresh_total_otp_ts.get(chat_id, 0) >= FRESH_READ_TTL:
        try:
            otp_doc = db.collection("users").document(str(chat_id)).get()
            _fresh_total_otp_ts[chat_id] = time.time()
            if otp_doc.exists:
                otp_data = otp_doc.to_dict() or {}
                total_otp = int(otp_data.get("total_otps", 0) or 0)
                u_data["total_otps"] = total_otp
                if chat_id in user_cache:
                    user_cache[chat_id]["total_otps"] = total_otp
        except Exception as e:
            print(f"⚠️ Total OTP refresh error for {chat_id}: {e}")

    c_msg = bot_settings["custom_messages"].get("withdrawal", {})
    default_withdrawal_text = (
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "       💎 <b>WITHDRAWAL CENTER</b>\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "💰 <b>AVAILABLE BALANCE</b>\n<code>{bal} ৳</code>\n"
        "⚡ <b>MINIMUM PAYOUT</b>  <code>{min_w} ৳</code>\n"
        "📨 <b>TOTAL OTP</b>  <code>{total_otp}</code>\n"
        "👥 <b>TOTAL REFERRALS</b>  <code>{total_ref}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🏦 <b>SELECT PAYMENT METHOD</b>\n"
        "<i>Choose one of the methods below to continue.</i>"
    )
    raw_txt = c_msg.get("text", default_withdrawal_text).replace("{bal}", str(bal)).replace("{total_otp}", str(total_otp)).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
    txt = render_body_text(raw_txt)

    kb = []
    methods = [str(m).strip() for m in bot_settings.get("w_methods", []) if str(m).strip()]
    for m in methods:
        kb.append([{"text": f"💳  {m}", "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m}", "style": "primary"}])

    for b in c_msg.get("buttons", []):
        b_copy = b.copy()
        if "style" not in b_copy:
            b_copy["style"] = "primary"
        kb.append([b_copy])

    bottom_row = []
    if include_profile_back:
        bottom_row.append({"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "my_profile", "style": "primary"})
    bottom_row.append({"text": "✖ CANCEL", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"})
    kb.append(bottom_row)
    return txt, {"inline_keyboard": kb}


# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = normalize_bot_font(msg.get("text", ""))
    register_user_local(chat_id) # 🌟 Save User locally for Free Broadcasts!
    sync_user_identity(chat_id, msg)

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    # --- REFERRAL FIX: Save inviter BEFORE Force Join ---
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                if db:
                    doc = db.collection('users').document(str(chat_id)).get()
                    if not doc.exists:
                        get_user(chat_id)
                        db.collection('users').document(str(chat_id)).update({"referred_by": inviter, "ref_paid": False})
                        
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["GET NUMBER", "GET NUMBER STOCK", "GET NUMBER API", "Get Number (V1)", "Get Number (V2)", "TRAFFIC", "SELL ID", "LEADERBOARD", "Refer", "WITHDRAWAL", "iX Shop", "SUPPORT", "Admin Panel", "💎 MY PROFILE", "MY PROFILE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]
        
        # --- OTP Group Premium Emoji Setup Flow ---
        if state == "wait_for_otp_group_emoji":
            slot = temp_data.get(chat_id, {}).get("otp_slot")
            manager_msg_id = temp_data.get(chat_id, {}).get("msg_id")
            if slot not in OTP_GROUP_SLOTS:
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                txt_m, kb_m = build_otp_group_emoji_manager_ui()
                send_message(chat_id, txt_m, reply_markup=kb_m)
                return

            entities = msg.get("entities") or msg.get("caption_entities") or []
            raw_text = msg.get("text") or msg.get("caption") or ""
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = raw_text.encode("utf-16-le")
                    emoji_text = b_text[offset*2:(offset+length)*2].decode("utf-16-le")
                    break

            saved_value = None
            if custom_emoji_id:
                fallback_char = OTP_GROUP_SLOTS[slot]["fallback"]
                saved_value = {"id": str(custom_emoji_id), "char": emoji_text or fallback_char}
            else:
                # Also allow a standard emoji if the admin sends one cleanly without text.
                stripped = raw_text.strip()
                if stripped and len(stripped) <= 12 and not any(c.isascii() and c.isalnum() for c in stripped):
                    saved_value = {"id": "", "char": stripped}

            if saved_value:
                bot_settings.setdefault("otp_group_emojis", {})[slot] = saved_value
                save_db()
                delete_message(chat_id, msg["message_id"])
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                slot_label = OTP_GROUP_SLOTS[slot]["label"]
                notice = f"{PEM['ok']} <b>{html.escape(slot_label)}</b> ইমোজি সেভ হয়েছে!"
                txt_m, kb_m = build_otp_group_emoji_manager_ui(notice=notice)
                if manager_msg_id:
                    res = edit_message(chat_id, manager_msg_id, txt_m, reply_markup=kb_m)
                    if not (res or {}).get("ok"):
                        send_message(chat_id, txt_m, reply_markup=kb_m)
                else:
                    send_message(chat_id, txt_m, reply_markup=kb_m)
            else:
                send_message(
                    chat_id,
                    render_body_text(f"{PEM['no']} দয়া করে একটি <b>Telegram Premium Emoji</b> অথবা সাধারণ ইমোজি পাঠান।"),
                    reply_markup={"inline_keyboard": [[{"text": "Cancel", "callback_data": "setup_otp_group_emojis", "style": "danger"}]]}
                )
            return

        # 🌟 Auto Captcha Panel Setup Flow 
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Panel এর Username দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Panel এর Password দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ যেখান থেকে SMS/OTP ডাটা (JSON) আসবে সেই Link দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Data তে Number column এর নাম কী? (যেমন: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ Number Column এর Serial Number কত? (যেমন: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Message/OTP column এর নাম কী? (যেমন: message, sms):"), reply_markup=get_cancel_kb())
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ Message Column এর Serial Number কত? (যেমন: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                
                # Save the panel configuration
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\nবট এখন থেকে নিজেই ব্যাকগ্রাউন্ডে ক্যাপচা সলভ করে লগিন করে নিবে।"), reply_markup=main_menu(chat_id))
                
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # --- User Management Flows ---
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_bal = doc.to_dict().get('balance', 0.0)
                temp_data[chat_id]["target_uid"] = target_uid
                user_states[chat_id] = "wait_for_um_bal_amt"
                send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} ৳\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated successfully for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{amt} ৳</b> by an Admin."))
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc_ref = db.collection('users').document(str(target_uid))
                doc = doc_ref.get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_status = doc.to_dict().get("banned", False)
                new_status = not current_status
                doc_ref.update({"banned": new_status})
                
                user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
                
                status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                data = doc.to_dict()
                is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
                prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ৳
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
                kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        # --- Menu Design Flow ---
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                
                delete_message(chat_id, msg["message_id"])
                
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except Exception as e:
                 pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
            msg_text = _format_otp_group_message(num, app_full_name, iso, temp_data[chat_id]["otp"] if not temp_data[chat_id].get("message") else temp_data[chat_id]["message"])
            
            for fw in bot_settings.get("fw_groups", []):
                send_message(fw["chat_id"], msg_text, reply_markup=build_fw_otp_keyboard(otp, fw))
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_emoji_extract":
            entities = sorted(msg.get("entities", []) or [], key=lambda e: e.get("offset", 0))
            custom_emojis = []
            b_text = msg.get("text", "").encode("utf-16-le")
            for ent in entities:
                if ent.get("type") != "custom_emoji":
                    continue
                custom_emoji_id = ent.get("custom_emoji_id")
                if not custom_emoji_id:
                    continue
                offset = ent.get("offset", 0)
                length = ent.get("length", 0)
                emoji_text = b_text[offset*2:(offset+length)*2].decode("utf-16-le")
                custom_emojis.append({"id": str(custom_emoji_id), "char": emoji_text})

            if 1 <= len(custom_emojis) <= 2:
                temp_data[chat_id] = {
                    "emoji_ids": [e["id"] for e in custom_emojis],
                    "emoji_chars": [e["char"] for e in custom_emojis]
                }
                user_states[chat_id] = "wait_for_emoji_target"
                preview = " ".join(e["char"] for e in custom_emojis)
                send_message(chat_id, render_body_text(
                    f"{PEM['ok']} <b>{len(custom_emojis)} Premium Emoji selected:</b> {preview}\n\n"
                    "এখন Premium Emoji টি কোথায় সেট করবেন সেটা নির্বাচন করুন:"
                ), reply_markup=_emoji_management_target_keyboard())
            else:
                send_message(chat_id, render_body_text(
                    f"{PEM['no']} ১টি অথবা সর্বোচ্চ ২টি Telegram Premium/Custom Emoji একসাথে পাঠান।"
                ), reply_markup=get_cancel_kb())
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not str(doc.get("file_name", "")).lower().endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            content, dl_err = download_telegram_file(file_id)
            if content is None:
                send_message(chat_id, render_body_text(f"{PEM['no']} Could not download the file ({html.escape(str(dl_err or 'error'))}). Please upload it again."))
                return
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_txt":
            if "document" not in msg:
                send_message(chat_id, render_body_text(f"{PEM['warn']} Please upload a <b>.txt</b> or <b>.csv</b> file, or tap Cancel."), reply_markup=get_cancel_kb())
                return
            doc = msg["document"]
            filename = str(doc.get("file_name", ""))
            lower_filename = filename.lower()
            if not (lower_filename.endswith(".txt") or lower_filename.endswith(".csv")):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt or .csv file only."), reply_markup=get_cancel_kb())
                return
            file_id = doc["file_id"]
            status_res = send_message(chat_id, render_body_text("⏳ File received, downloading &amp; parsing..."))
            status_msg_id = (status_res.get("result") or {}).get("message_id")
            file_content, dl_err = download_telegram_file(file_id)
            if file_content is None:
                err_txt = f"{PEM['no']} Could not download the file ({html.escape(str(dl_err or 'error'))}). Please upload it again."
                if status_msg_id:
                    edit_message(chat_id, status_msg_id, render_body_text(err_txt), reply_markup=get_cancel_kb())
                else:
                    send_message(chat_id, render_body_text(err_txt), reply_markup=get_cancel_kb())
                return

            _strip_tbl = str.maketrans("", "", " \t\r\n-().\"'")
            if lower_filename.endswith(".csv"):
                csv_numbers = []
                try:
                    reader = csv.reader(file_content.splitlines())
                    for row in reader:
                        if len(row) < 4:
                            continue
                        value = str(row[3]).lstrip("\ufeff").translate(_strip_tbl)
                        if not value:
                            continue
                        digits = value[1:] if value.startswith("+") else value
                        if digits.isascii() and digits.isdigit():
                            csv_numbers.append(value)
                except Exception as csv_err:
                    err_txt = f"{PEM['no']} Invalid CSV file: {html.escape(str(csv_err))}"
                    if status_msg_id:
                        edit_message(chat_id, status_msg_id, render_body_text(err_txt), reply_markup=get_cancel_kb())
                    else:
                        send_message(chat_id, render_body_text(err_txt), reply_markup=get_cancel_kb())
                    return

                if not csv_numbers:
                    err_txt = f"{PEM['no']} No valid numbers found in CSV Column D."
                    if status_msg_id:
                        edit_message(chat_id, status_msg_id, render_body_text(err_txt), reply_markup=get_cancel_kb())
                    else:
                        send_message(chat_id, render_body_text(err_txt), reply_markup=get_cancel_kb())
                    return
                upload_numbers = csv_numbers
            else:
                txt_numbers = []
                for line in file_content.splitlines():
                    normalized = line.lstrip("\ufeff").translate(_strip_tbl)
                    if not normalized:
                        continue
                    digits = normalized[1:] if normalized.startswith("+") else normalized
                    if digits.isascii() and digits.isdigit():
                        txt_numbers.append(normalized)

                if not txt_numbers:
                    err_txt = f"{PEM['no']} No valid phone numbers found in TXT file."
                    if status_msg_id:
                        edit_message(chat_id, status_msg_id, render_body_text(err_txt), reply_markup=get_cancel_kb())
                    else:
                        send_message(chat_id, render_body_text(err_txt), reply_markup=get_cancel_kb())
                    return
                upload_numbers = txt_numbers

            temp_data[chat_id] = {"numbers": upload_numbers, "filename": filename}
            user_states[chat_id] = "wait_for_service"
            ok_txt = f"{PEM['ok']} File received (<b>{len(upload_numbers)}</b> numbers).\n\n📌 Enter the service name (e.g., WHATSAPP):"
            if status_msg_id:
                edit_message(chat_id, status_msg_id, render_body_text(ok_txt), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(ok_txt), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            if chat_id not in temp_data or "numbers" not in temp_data[chat_id]:
                user_states.pop(chat_id, None)
                send_message(chat_id, render_body_text("❌ Upload session expired. Please tap Upload Number again."), reply_markup=main_menu(chat_id))
                return
            temp_data[chat_id]["service"] = text.strip().upper()
            user_states[chat_id] = "wait_for_country"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Service set.\n\n🌍 Enter the country name (e.g., YEMEN):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_country" and text:
            if chat_id not in temp_data or "numbers" not in temp_data[chat_id]:
                user_states.pop(chat_id, None)
                send_message(chat_id, render_body_text("❌ Upload session expired. Please tap Upload Number again."), reply_markup=main_menu(chat_id))
                return
            country = text.strip().upper()
            temp_data[chat_id]["country"] = country
            user_states[chat_id] = "wait_for_file_rate"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Country set.\n\n💰 Enter the OTP reward rate for this file (e.g. 5.0):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_file_rate" and text:
            if chat_id not in temp_data or "numbers" not in temp_data[chat_id] or "country" not in temp_data[chat_id] or "service" not in temp_data[chat_id]:
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                send_message(chat_id, render_body_text("❌ Upload session expired. Please tap Upload Number again."), reply_markup=main_menu(chat_id))
                return
            try:
                rate = float(text.strip().replace(",", "."))
                if not math.isfinite(rate) or rate < 0:
                    raise ValueError
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid rate! Please enter a valid positive number (e.g. 5.0):"), reply_markup=get_cancel_kb())
                return
                
            country = temp_data[chat_id]["country"]
            service = temp_data[chat_id]["service"]
            raw_numbers = temp_data[chat_id]["numbers"]
            filename = temp_data[chat_id].get("filename", "upload.txt")
            
            clean_nums = []
            country_key = re.sub(r"[^A-Z]", "", str(country or "").upper())
            is_norway = country_key in {"NORWAY", "NO", "NORGE"}
            for raw_num in raw_numbers:
                s = str(raw_num or "")
                digits = s[1:] if s.startswith("+") else s
                if not (digits.isascii() and digits.isdigit()):
                    digits = re.sub(r"\D", "", s)
                if not digits:
                    continue
                if is_norway:
                    if digits.startswith("0047") and len(digits) == 12:
                        digits = digits[2:]
                    if len(digits) == 8:
                        digits = "47" + digits
                    elif len(digits) == 10 and digits.startswith("47"):
                        pass
                    elif len(digits) == 11 and digits.startswith("047"):
                        digits = digits[1:]
                clean_nums.append("+" + digits)

            if not clean_nums:
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                send_message(chat_id, render_body_text(f"{PEM['no']} No valid numbers found to save. Please try uploading again."), reply_markup=main_menu(chat_id))
                return
            
            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {
                "filename": filename, 
                "service": service, 
                "country": country, 
                "rate": rate,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
            }
            total_uploaded_stats += len(clean_nums)
            save_db()
            
            # Broadcast-only Premium Emoji resolution: use the exact configured
            # country/service mapping first, so custom names do not fall back to
            # a different Premium Emoji.  This does not change any other flag
            # or service detection logic in the bot.
            prem_flag_html = None
            country_label = re.sub(r"<tg-emoji[^>]*>.*?</tg-emoji>", " ", str(country or ""), flags=re.I)
            country_label = re.sub(r"<[^>]+>", " ", country_label).strip()
            label_upper = country_label.upper()
            flag_items = sorted(
                (bot_settings.get("premium_flags", {}) or {}).items(),
                key=lambda item: len(str((item[1] or {}).get("name", "") or "")),
                reverse=True,
            )
            for flag_code, flag_data in flag_items:
                flag_data = flag_data or {}
                iso = str(flag_data.get("iso", "") or "").strip().upper()
                name = str(flag_data.get("name", "") or "").strip()
                if (
                    label_upper == iso
                    or label_upper == name.upper()
                    or name.upper() in label_upper
                    or label_upper in name.upper()
                    or label_upper == str(flag_code).strip().upper()
                ) and flag_data.get("id"):
                    char = flag_data.get("char") or "🌍"
                    prem_flag_html = f'<tg-emoji emoji-id="{flag_data["id"]}">{char}</tg-emoji>'
                    break
            if not prem_flag_html:
                prem_flag_html = get_flag_info_html(clean_nums[0]) if clean_nums else f"{PEM['world']} "

            app_full_name, prem_app_html = get_service_info_html(service)
            service_label = re.sub(r"<tg-emoji[^>]*>.*?</tg-emoji>", " ", str(service or ""), flags=re.I)
            service_label = re.sub(r"<[^>]+>", " ", service_label).strip()
            service_upper = service_label.upper()
            app_items = sorted(
                (bot_settings.get("premium_apps", {}) or {}).items(),
                key=lambda item: len(str((item[1] or {}).get("name", "") or "")),
                reverse=True,
            )
            for app_key, app_data in app_items:
                app_data = app_data or {}
                app_name = str(app_data.get("name", app_key) or "").strip()
                if (
                    service_upper == app_name.upper()
                    or app_name.upper() in service_upper
                    or service_upper == str(app_key).strip().upper()
                ) and app_data.get("id"):
                    char = app_data.get("char") or "📱"
                    prem_app_html = f'<tg-emoji emoji-id="{app_data["id"]}">{char}</tg-emoji>'
                    break
            
            broadcast_txt = f"➖➖➖➖➖➖➖➖\n《 NEW NUMBERS 》\n➖➖➖➖➖➖➖➖\n{prem_flag_html} {country} {prem_app_html} {service}\n➖➖➖➖➖➖➖➖\n📤 Total Added: <b>{len(clean_nums)}</b>\n💰 Reward: <b>{rate} TK</b>\n➖➖➖➖➖➖➖➖\nUse /start to get your numbers!"
            broadcast_txt = render_body_text(broadcast_txt)
            
            # Free uploaded number list from temp_data and store only the broadcast text.
            temp_data[chat_id] = {"pending_number_broadcast": broadcast_txt}
            user_states[chat_id] = "wait_for_broadcast_choice"
            send_message(
                chat_id,
                render_body_text(f"{PEM['ok']} Numbers added to local stock with {rate} TK rate!\n\nChoose whether to broadcast this upload to users."),
                reply_markup={"inline_keyboard": [
                    [{"text": "📣 Broadcast", "callback_data": "upload_broadcast_send", "style": "success"}],
                    [{"text": "⏭ Skip", "callback_data": "upload_broadcast_skip", "style": "danger"}]
                ]}
            )
            return

        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ StexSMS API Key Added! Total Keys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_nx_srv_name" and text:
            srv = text.strip().upper()
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            if srv not in bot_settings["stex_services"]: bot_settings["stex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_stex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["stex_services"][srv][cnt]:
                bot_settings["stex_services"][srv][cnt].append(new_range)
                
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]:
                    bot_settings["search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]:
                    bot_settings["voltx_search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_zenex_key" and text:
            bot_settings["zenex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Zenex API Key Added! Total Keys: {len(bot_settings.get('zenex_keys', []))}"), reply_markup=zenex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_zsc" and text:
            code = text.strip().replace("+", "")
            if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
            bot_settings["zenex_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "zenex_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_zx_srv_name" and text:
            srv = text.strip().upper()
            if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
            if srv not in bot_settings["zenex_services"]: bot_settings["zenex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_zenex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["zenex_services"][srv]: bot_settings["zenex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            if new_range not in bot_settings["zenex_services"][srv][cnt]:
                bot_settings["zenex_services"][srv][cnt].append(new_range)
                if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                if new_range not in bot_settings["zenex_search_countries"]: bot_settings["zenex_search_countries"].append(new_range)
                save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            bot_settings["fj_channels"].append(parse_chat_id(text))
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:\n<i>(Note: For private links, use numeric IDs like -100...)</i>"), reply_markup=fj_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id" and text:
            bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Panel এর Login Link দিন:"), reply_markup=get_cancel_kb())
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF", "api_url": "", "token": "", "records": 0
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        elif state == "wait_for_p_api" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["token"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["full_api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_managed_service_rename" and text:
            old_service = str(temp_data.get(chat_id, {}).get("managed_service_old", "")).strip()
            new_service = text.strip()
            if not new_service or len(new_service) > 64:
                send_message(chat_id, render_body_text("❌ Enter a service name between 1 and 64 characters."))
                return
            if not old_service or old_service not in _managed_local_services():
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                send_message(chat_id, render_body_text("❌ The selected service no longer exists. Please open Manage Service &amp; Country again."))
                return
            if any(s.casefold() == new_service.casefold() and s != old_service for s in _managed_services()):
                send_message(chat_id, render_body_text("❌ A service with that name already exists. Please choose a different name."))
                return
            for batch in number_batches.values():
                if str(batch.get("service", "")).strip() == old_service:
                    batch["service"] = new_service
            prices = bot_settings.get("service_country_prices", {}) or {}
            if old_service in prices:
                prices[new_service] = prices.pop(old_service)
            bot_settings["service_country_prices"] = prices
            for number, service_name in list(assigned_number_services.items()):
                if str(service_name).strip() == old_service:
                    assigned_number_services[number] = new_service
            for session in user_active_sessions.values():
                if isinstance(session, dict) and str(session.get("service", "")).strip() == old_service:
                    session["service"] = new_service
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ <b>Service renamed successfully.</b>\n\nOld name: <code>{html.escape(old_service)}</code>\nNew name: <code>{html.escape(new_service)}</code>\n\nCountry, number batches, rates and assignment links were preserved."), reply_markup=_manage_service_country_keyboard())
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_managed_otp_rate" and text:
            state_data = temp_data.get(chat_id, {})
            service = str(state_data.get("managed_rate_service", "")).strip()
            country = str(state_data.get("managed_rate_country", "")).strip()
            try:
                new_rate = float(text.strip().replace(",", "."))
                if new_rate < 0 or not math.isfinite(new_rate):
                    raise ValueError
            except (ValueError, TypeError):
                send_message(chat_id, render_body_text("❌ Invalid rate. Send a valid number such as <code>2</code> or <code>0.5</code>."))
                return
            if not service or country not in _managed_countries(service):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                send_message(chat_id, render_body_text("❌ The selected service/country no longer exists."))
                return
            bot_settings.setdefault("service_country_prices", {}).setdefault(service, {})[country] = new_rate
            # Apply the new rate to currently assigned numbers of this exact service/country
            # so only future OTP credits use the new amount; completed balances/history are untouched.
            for assigned_num, assigned_service in list(assigned_number_services.items()):
                if str(assigned_service).strip() != service:
                    continue
                assigned_country = None
                normalized_num = _clean_assigned_number(assigned_num)
                for country_num, country_value in assigned_number_countries.items():
                    if _clean_assigned_number(country_num) == normalized_num:
                        assigned_country = str(country_value).strip()
                        break
                if assigned_country and assigned_country.casefold() == country.casefold():
                    _set_assigned_number_rate(assigned_num, new_rate)
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, state_data["msg_id"], render_body_text(f"✅ <b>OTP rate saved successfully.</b>\n\nService: <code>{html.escape(service)}</code>\nCountry: <code>{html.escape(country)}</code>\nNew rate: <b>{new_rate:g} TK / OTP</b>\n\nNew rate will apply to future successful OTP credits. Existing completed balances and OTP history were not changed."), reply_markup=_managed_countries_keyboard("rate", service))
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_service_country_price" and text:
            try:
                raw_price = text.strip().replace(",", ".")
                new_price = float(raw_price)
                if new_price < 0:
                    raise ValueError
                service = temp_data[chat_id]["price_service"]
                country = temp_data[chat_id]["price_country"]
                bot_settings.setdefault("service_country_prices", {})
                bot_settings["service_country_prices"].setdefault(service, {})[country] = new_price
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💎 <b>SELECT YOUR COUNTRY FOR CHANGE RATE:</b>"), reply_markup=set_price_countries_keyboard(service))
            except (ValueError, TypeError, KeyError):
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("❌ <b>Invalid price.</b>\n\nPlease send a valid number, for example: <code>0.5</code>"), reply_markup=set_price_country_prompt_keyboard(temp_data[chat_id].get("price_service", "")))
                # Keep the state active so the admin can retry without reopening the country.
                return
            if chat_id in user_states:
                del user_states[chat_id]
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_sell_id_link" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return
            raw_link = text.strip()
            if raw_link.lower() in {"clear", "remove", "off", "none"}:
                bot_settings["sell_id_link"] = ""
            else:
                if raw_link.startswith("@"):
                    raw_link = f"https://t.me/{raw_link[1:]}"
                elif raw_link.startswith("t.me/"):
                    raw_link = f"https://{raw_link}"
                if not (raw_link.startswith("https://") or raw_link.startswith("http://") or raw_link.startswith("tg://")):
                    send_message(chat_id, render_body_text("❌ Invalid link! Send a valid URL (e.g. <code>https://t.me/username</code> or <code>@username</code>) or type <code>clear</code>."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "callback_data": "back_to_admin", "style": "danger"}]]})
                    return
                bot_settings["sell_id_link"] = raw_link
            save_db()
            delete_message(chat_id, msg["message_id"])
            saved_val = bot_settings.get("sell_id_link") or "Not set"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ <b>SELL ID Link Updated!</b>\n\n🔗 <b>Current Link:</b> <code>{html.escape(saved_val)}</code>"), reply_markup=admin_sell_id_keyboard())
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_shop_link" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return
            raw_link = text.strip()
            if raw_link.lower() in {"clear", "remove", "off", "none"}:
                bot_settings["shop_link"] = ""
            else:
                if raw_link.startswith("@"):
                    raw_link = f"https://t.me/{raw_link[1:]}"
                elif raw_link.startswith("t.me/"):
                    raw_link = f"https://{raw_link}"
                if not (raw_link.startswith("https://") or raw_link.startswith("http://") or raw_link.startswith("tg://")):
                    send_message(chat_id, render_body_text("❌ Invalid link! Send a valid URL (e.g. <code>https://t.me/username</code> or <code>@username</code>) or type <code>clear</code>."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "callback_data": "back_to_admin", "style": "danger"}]]})
                    return
                bot_settings["shop_link"] = raw_link
            save_db()
            delete_message(chat_id, msg["message_id"])
            saved_val = bot_settings.get("shop_link") or "Not set"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ <b>iX Shop Link Updated!</b>\n\n🛒 <b>Current Link:</b> <code>{html.escape(saved_val)}</code>"), reply_markup=admin_shop_keyboard())
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_sell_id_text" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return
            formatted_html = extract_premium_html(msg)
            bot_settings["sell_id_text"] = formatted_html
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ <b>SELL ID Text Updated!</b>\n\n<b>Preview:</b>\n{formatted_html}"), reply_markup=admin_sell_id_keyboard())
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_shop_text" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return
            formatted_html = extract_premium_html(msg)
            bot_settings["shop_text"] = formatted_html
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ <b>iX Shop Text Updated!</b>\n\n<b>Preview:</b>\n{formatted_html}"), reply_markup=admin_shop_keyboard())
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_payout_group" and text:
            target = text.strip()
            # Telegram sendMessage target must be a chat ID or public @username; a t.me URL is only a display link.
            if target.startswith("https://t.me/") or target.startswith("http://t.me/"):
                bot_settings["payout_group"] = target
                bot_settings["payout_group_target"] = ""
            else:
                bot_settings["payout_group"] = target
                bot_settings["payout_group_target"] = target
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💸 <b>WITHDRAWAL MANAGEMENT</b>\n\nPayout group settings saved. For automatic payout posts, use a group chat ID (usually starts with <code>-100</code>) or a public <code>@username</code>. A private invite link alone cannot be used by the bot to send messages."), reply_markup=withdrawal_management_keyboard())
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "set_dxa":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                if key == "w_group":
                    target = normalize_withdrawal_group_target(text)
                    if not target:
                        delete_message(chat_id, msg["message_id"])
                        send_message(chat_id, render_body_text(
                            "❌ <b>Invalid withdrawal group target</b>\n\n"
                            "Send a public group link like <code>https://t.me/groupname</code>, "
                            "a public <code>@groupname</code>, or the numeric chat ID (usually starts with <code>-100</code>).\n\n"
                            "A private invite link such as <code>t.me/+...</code> cannot be used to send messages. "
                            "For a private group, add the bot to the group and send its numeric chat ID."
                        ))
                        return
                    bot_settings[key] = target
                elif key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                if key == "w_group":
                    test_result = send_message(
                        bot_settings[key],
                        "🔔 <b>Withdrawal Request Group Connected</b>\n\nThis is a test message. New withdrawal requests will be posted here."
                    )
                    if test_result.get("ok", False):
                        status_text = "✅ Group connection test succeeded. A test message was delivered."
                    else:
                        error_text = test_result.get("description", "Unknown Telegram API error")
                        status_text = "❌ Group connection test failed: <code>" + html.escape(str(error_text)) + "</code>\n\nCheck the chat ID and make sure the bot is a member with permission to send messages."
                    edit_message(chat_id, msg_id, render_body_text(
                        "💸 <b>WITHDRAWAL MANAGEMENT</b>\n\n"
                        "Withdrawal request group saved as: <code>" + html.escape(str(bot_settings[key])) + "</code>\n\n"
                        + status_text
                    ), reply_markup=withdrawal_management_keyboard())
                else:
                    edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
            except Exception as e:
                print(f"[WITHDRAWAL GROUP SETTING ERROR] {e}")
                delete_message(chat_id, msg["message_id"])
                if key == "w_group":
                    edit_message(chat_id, msg_id, render_body_text("💸 <b>WITHDRAWAL MANAGEMENT</b>\n\n❌ Invalid value! Please send a public group link, @username, or numeric chat ID."), reply_markup=withdrawal_management_keyboard())
                else:
                    edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=dxa_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            # 🌟 ১. প্রথমে Local থেকে নাম্বার খুঁজবে (যে কোনো দেশের জন্য)
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                if wait_msg_id: delete_message(chat_id, wait_msg_id)
                send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                return
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    
                    fetched_nums.append(num_str)
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            for _assigned_num in fetched_nums:
                assigned_number_owners[_clean_assigned_number(_assigned_num)] = chat_id
            save_db()

            kb = []
            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                display_num = str(num).replace("+", "").replace(" ", "").replace("-", "")
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id=\"{flag_emoji_id}\">{flag_data["char"]}</tg-emoji>'
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                premium_flag = get_premium_flag_for_number(num)
                number_btn = {"text": f"{display_num}", "copy_text": {"text": display_num}, "style": "success"}
                if premium_flag:
                    number_btn["icon_custom_emoji_id"] = premium_flag["id"]
                kb.append([number_btn])
            
            vtx_ext = "_vtx" if 'is_voltx_used' in locals() and is_voltx_used else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{vtx_ext}", "style": "danger"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
                
            kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            custom_star_html = f'<tg-emoji emoji-id=\"5305517382138112561\">⭐️</tg-emoji>'
            text_numbers = render_body_text(f"{country_emoji_html} {custom_star_html} NEW NUMBER\n")
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "prefix_removed": False}
                save_db()
            else:
                msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums, "prefix_removed": False}
                    save_db()
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} ৳!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    number_prompt = (
                        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                        "       📱 <b>ACCOUNT DETAILS</b>\n"
                        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"✅ <b>REQUEST AMOUNT</b>  <code>{amount} ৳</code>\n"
                        f"🏦 <b>PAYMENT METHOD</b>  <code>{html.escape(str(temp_data[chat_id]['method']))}</code>\n\n"
                        "🔢 <b>SEND YOUR ACCOUNT NUMBER</b>\n"
                        "<i>Double-check the number before sending it.</i>"
                    )
                    edit_message(chat_id, msg_id_to_edit, render_body_text(number_prompt), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id")) # ইউজারের মেসেজ ডিলিট

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except Exception:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key! Try again.</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount)
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            
            # Save to Firestore for History
            if db:
                try:
                    db.collection('withdrawals').document(req_id).set({
                        "user_id": str(chat_id),
                        "amount": amount,
                        "method": method,
                        "status": "pending",
                        "number": number,
                        "full_name": full_name,
                        "request_id": req_id,
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                except: pass
                
            withdrawal_group_target = normalize_withdrawal_group_target(bot_settings.get("w_group", ""))
            if withdrawal_group_target:
                admin_msg = (
                    "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                    "      💸 <b>NEW WITHDRAWAL</b>\n"
                    "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                    f"👤 <b>USER</b>\n<blockquote>{html.escape(full_name)}</blockquote>\n"
                    f"💰 <b>REQUESTED AMOUNT</b>  <code>{amount} ৳</code>\n"
                    f"🏦 <b>PAYMENT METHOD</b>  <code>{html.escape(str(method))}</code>\n"
                    f"📱 <b>ACCOUNT NUMBER</b>\n<code>{html.escape(str(number))}</code>\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧾 <b>REQUEST ID</b>  <code>{html.escape(str(req_id))}</code>\n"
                    "🟡 <b>STATUS</b>  <u>AWAITING REVIEW</u>\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "<i>Review the details carefully before taking action.</i>"
                )
                kb = {"inline_keyboard": [[{"text": "✅ APPROVE REQUEST", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "❌ REJECT", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
                group_result = send_message(withdrawal_group_target, render_body_text(admin_msg), reply_markup=kb)
                if not group_result.get("ok", False):
                    print(f"[WITHDRAWAL REQUEST GROUP SEND FAILED] target={withdrawal_group_target}: {group_result.get('description', group_result)}")
            else:
                print("[WITHDRAWAL REQUEST GROUP NOT CONFIGURED] Set a public @group username or numeric chat ID in Withdrawal Management.")
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = (
                f"{PEM['ok']} <b>WITHDRAWAL REQUEST SUBMITTED</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Your withdrawal request has been received successfully.\n\n"
                f"🧾 <b>REQUEST ID</b>\n<code>{html.escape(str(req_id))}</code>\n"
                f"💰 <b>AMOUNT</b>  <code>{amount} ৳</code>\n"
                f"🏦 <b>METHOD</b>  {html.escape(str(method))}\n"
                f"📱 <b>ACCOUNT / NUMBER</b>\n<code>{html.escape(str(number))}</code>\n\n"
                "⌛ <i>Your request is awaiting admin review.</i>"
            )
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # --- Regular Commands ---
    if text.startswith("/start"):
        get_user(chat_id)
        
        # --- PROCESS PENDING REFERRAL ---
        if db:
            doc = db.collection('users').document(str(chat_id)).get()
            if doc.exists:
                u_data = doc.to_dict()
                if u_data.get("referred_by") and not u_data.get("ref_paid"):
                    inviter = u_data["referred_by"]
                    db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                    reward = bot_settings.get("refer_reward", 0.2)
                    update_balance(inviter, reward)
                    db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)})
                    if inviter in user_cache:
                        user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
                    ref_msg = (
                        f"{PEM['gift']} <b>New Referral !</b>\n"
                        f"------------------\n"
                        f"🔥 <b>You Received {reward} TK</b>\n"
                        f"------------------\n"
                        f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                    )
                    send_message(inviter, render_body_text(ref_msg))
                    
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "LEADERBOARD":
        txt, markup = build_daily_leaderboard_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        # Old keyboard still on the user's phone -> refresh menu (Withdrawal is now inside MY PROFILE).
        send_message(
            chat_id,
            render_body_text(f"{PEM['ok']} Menu updated. Withdrawal is now inside <b>MY PROFILE</b>."),
            reply_markup=main_menu(chat_id)
        )

    elif text == "SELL ID":
        sell_link = str(bot_settings.get("sell_id_link", "") or "").strip()
        if sell_link.startswith("@"):
            sell_link = f"https://t.me/{sell_link[1:]}"
        elif sell_link.startswith("t.me/"):
            sell_link = f"https://{sell_link}"
        if sell_link and (sell_link.startswith("https://") or sell_link.startswith("http://") or sell_link.startswith("tg://")):
            kb = [
                [{"text": "SELL ID", "icon_custom_emoji_id": "5190576863226933563", "url": sell_link, "style": "success"}],
                [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
            ]
            sell_text = bot_settings.get("sell_id_text") or "💼 <b>SELL ID</b>\n\nTap the button below to sell your ID:"
            send_message(chat_id, render_body_text(sell_text), reply_markup={"inline_keyboard": kb})
        else:
            send_message(chat_id, render_body_text(f"{PEM['warn']} <b>SELL ID link is not set yet.</b>\nPlease contact support."))

    elif text == "iX Shop":
        shop_link = str(bot_settings.get("shop_link", "") or "").strip()
        if shop_link.startswith("@"):
            shop_link = f"https://t.me/{shop_link[1:]}"
        elif shop_link.startswith("t.me/"):
            shop_link = f"https://{shop_link}"
        if shop_link and (shop_link.startswith("https://") or shop_link.startswith("http://") or shop_link.startswith("tg://")):
            kb = [
                [{"text": "🛒 Open iX Shop", "url": shop_link, "style": "success"}],
                [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
            ]
            shop_text = bot_settings.get("shop_text") or "🛒 <b>iX SHOP</b>\n\nTap the button below to open iX Shop:"
            send_message(chat_id, render_body_text(shop_text), reply_markup={"inline_keyboard": kb})
        else:
            send_message(chat_id, render_body_text(f"{PEM['warn']} <b>iX Shop link is not set yet.</b>\nPlease contact support."))

    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text in ("GET NUMBER", "GET NUMBER STOCK", "GET NUMBER API", "Get Number (V1)", "Get Number (V2)"):
        if text == "GET NUMBER":
            # Old keyboard still on the user's phone -> refresh it with the two new buttons.
            send_message(chat_id, render_body_text(f"{PEM['ok']} Menu updated. Choose <b>Get Number (V1)</b> or <b>Get Number (V2)</b>."), reply_markup=main_menu(chat_id))
            return
        _mode = "stock" if text in ("Get Number (V1)", "GET NUMBER STOCK") else "api"
        user_number_mode[chat_id] = _mode
        api_country_hint.pop(chat_id, None)
        all_services = _services_for_mode(_mode)
        
        if not all_services:
            _empty_txt = "No stock numbers available!" if _mode == "stock" else "No API services available!"
            send_message(chat_id, render_body_text(f"{PEM['no']} {_empty_txt}"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            service_buttons = []
            for s in all_services:
                emoji_id = "5352694861990501856" # Default icon
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                service_buttons.append({"text": f"{s}\n\u200b", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"})
            for i in range(0, len(service_buttons), 2):
                kb.append(service_buttons[i:i + 2])
            
            for b in c_msg.get("buttons", []): 
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text in ("💎 MY PROFILE", "MY PROFILE"):
        sync_user_identity(chat_id, msg)
        send_message(chat_id, build_my_profile_text(chat_id), reply_markup=my_profile_keyboard())

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip(): txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        sup_link = bot_settings.get("support_link", "")
        contact_row = []
        if sup_link:
            contact_row.append({"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"})
        if DEVELOPER_LINK:
            contact_row.append({"text": "Developer", "url": DEVELOPER_LINK, "style": "primary"})
        if contact_row:
            kb.insert(0, contact_row)
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)

def expire_previous_number(chat_id, persist=True):
    """Expire the user's previous session without forcing duplicate DB writes.

    persist=False is used by the number-assignment flow so the previous-session
    cleanup and the new assignment are persisted together in one save_db() call.
    """
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        
        # API সিস্টেম থেকে রিমুভ করা যাতে ইনবক্সে আর মেসেজ না যায়
        for num in nums:
            stex_assigned_numbers.pop(num, None)
            voltx_assigned_numbers.pop(num, None)
            zenex_assigned_numbers.pop(num, None)
            assigned_number_services.pop(num, None)
            assigned_number_owners.pop(_clean_assigned_number(num), None)
        
        # আগের মেসেজ ইডিট করে Expired বাটন বসানো
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try:
            edit_message(chat_id, prev_msg_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": kb})
        except:
            pass
        del user_active_sessions[chat_id]
        if persist:
            save_db()

# ==========================================
# Callback Query Handler
# ==========================================
def _detect_country_code(number):
    """Detect the longest known country calling code from a full number."""
    clean = str(number or "").replace("+", "").replace(" ", "").replace("-", "").strip()
    if not clean:
        return ""

    # Prefer configured premium flags, then use the complete fallback map.
    codes = set(str(c) for c in bot_settings.get("premium_flags", {}).keys())
    codes.update(str(c) for c in FALLBACK_COUNTRY_CODES.keys())
    for code in sorted(codes, key=len, reverse=True):
        if clean.startswith(code) and len(clean) > len(code):
            return code
    return ""


def _remove_country_code_from_number(number):
    """Return only the national/local number by removing the detected country code."""
    clean = str(number or "").replace("+", "").replace(" ", "").replace("-", "").strip()
    if not clean:
        return clean
    code = _detect_country_code(clean)
    return clean[len(code):] if code else clean


def _add_country_code_to_number(number):
    """Return the original full number, without adding a duplicate '+' prefix."""
    clean = str(number or "").replace("+", "").replace(" ", "").replace("-", "").strip()
    return clean


def _toggle_prefix_display(session, reply_markup):
    """Toggle visible number buttons between full and country-code-free forms."""
    nums = [str(n) for n in session.get("nums", [])]
    remove_prefix = not bool(session.get("prefix_removed", False))
    new_rows = []
    changed = False

    for row in reply_markup.get("inline_keyboard", []):
        new_row = []
        for btn in row:
            b = dict(btn)
            copy_data = b.get("copy_text")
            copy_text = str(copy_data.get("text", "")) if isinstance(copy_data, dict) else ""
            candidate = copy_text or str(b.get("text", ""))
            normalized_candidate = candidate.replace("+", "").replace(" ", "").replace("-", "")

            matched_num = None
            for original in nums:
                original_clean = original.replace("+", "").replace(" ", "").replace("-", "")
                full_form = _add_country_code_to_number(original_clean)
                local_form = _remove_country_code_from_number(original_clean)
                if normalized_candidate in {full_form, local_form}:
                    matched_num = original_clean
                    break

            if matched_num:
                target_number = (
                    _remove_country_code_from_number(matched_num)
                    if remove_prefix
                    else _add_country_code_to_number(matched_num)
                )
                b["text"] = target_number
                if isinstance(copy_data, dict):
                    b["copy_text"] = dict(copy_data)
                    b["copy_text"]["text"] = target_number
                changed = changed or (target_number != candidate)

            new_row.append(b)
        new_rows.append(new_row)

    return new_rows, remove_prefix, changed


def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    # 🌟 Button Loading Fix: বাটন চাপার সাথে সাথেই টেলিগ্রামকে Response দিয়ে দেওয়া, যাতে বাটন আটকে না থাকে!
    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    # Service/Country management controls are admin-only.
    if (data == "manage_service_country" or data in {"msc_rename", "msc_delete", "msc_rate"}
            or data.startswith(("msc_srv_", "msc_cnt_", "msc_del_confirm_", "msc_del_cancel_"))):
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can manage services and countries.", show_alert=True)
            return

    # Withdrawal-management controls are admin-only.
    if (data in {"withdrawal_management", "withdrawal_requests", "set_payout_group", "dxa_toggle_w", "manage_w_methods", "add_wm", "dxa_w_group"}
            or data.startswith(("wview_", "del_wm_"))) and not is_admin(call.get("from", {}).get("id", chat_id)):
        answer_callback(call["id"], "🚫 Only bot admins can manage withdrawals.", show_alert=True)
        return

    msg_id = call["message"]["message_id"]

    # Admin chooses whether to broadcast a completed number-file upload.
    if data in {"upload_broadcast_send", "upload_broadcast_skip"}:
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can use this option.", show_alert=True)
            return
        pending = temp_data.get(chat_id, {}).get("pending_number_broadcast")
        if not pending:
            answer_callback(call["id"], "⚠️ This upload action has expired. No broadcast was sent.", show_alert=True)
            return

        if data == "upload_broadcast_send":
            def simple_broadcast(txt):
                b_session = requests.Session()
                url = f"{BASE_URL}/sendMessage"
                for u_id in list(all_known_users):
                    try:
                        b_session.post(url, json={"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=5)
                    except Exception:
                        pass
                    time.sleep(0.035)
            threading.Thread(target=simple_broadcast, args=(pending,)).start()
            edit_message(chat_id, msg_id, render_body_text("✅ Number file uploaded. Broadcast started."))
        else:
            edit_message(chat_id, msg_id, render_body_text("✅ Number file uploaded. Broadcast skipped; no users were notified."))

        temp_data[chat_id].pop("pending_number_broadcast", None)
        if chat_id in user_states and user_states.get(chat_id) == "wait_for_broadcast_choice":
            user_states.pop(chat_id, None)
        if chat_id in temp_data and not temp_data[chat_id]:
            temp_data.pop(chat_id, None)
        return

    if data == "add_prefix":
        session = user_active_sessions.get(chat_id)
        if not session:
            answer_callback(call["id"], "❌ Number session expired. Please get a new number.", show_alert=True)
            return

        msg_markup = call["message"].get("reply_markup") or {}
        new_rows, remove_prefix, changed = _toggle_prefix_display(session, msg_markup)
        for row in new_rows:
            for btn in row:
                if btn.get("callback_data") == "add_prefix":
                    btn["text"] = "Add Prefix" if remove_prefix else "Remove Prefix"

        if changed:
            result = edit_message_reply_markup(chat_id, msg_id, {"inline_keyboard": new_rows})
            if result and result.get("ok"):
                session["prefix_removed"] = remove_prefix
                save_db()
                answer_callback(call["id"], "✅ Country code removed." if remove_prefix else "✅ Country code added.", show_alert=False)
            else:
                answer_callback(call["id"], "⚠️ Could not update the number display.", show_alert=True)
        else:
            session["prefix_removed"] = remove_prefix
            # Keep the button label in sync even if the number was already in the target form.
            edit_message_reply_markup(chat_id, msg_id, {"inline_keyboard": new_rows})
            save_db()
            answer_callback(call["id"], "ℹ️ Country code removed already." if remove_prefix else "ℹ️ Country code is already added.", show_alert=False)
        return

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

        if data in ("my_profile", "my_profile_next", "my_profile_back"):
            sync_user_identity(chat_id, call.get("from", {}))
            profile_page = 2 if data == "my_profile_next" else 1
            edit_message(chat_id, msg_id, build_my_profile_text(chat_id, profile_page), reply_markup=my_profile_keyboard(profile_page))
            return

        if data == "open_withdrawal":
            if not bot_settings.get("withdraw_on", True):
                answer_callback(call["id"], "❌ Withdrawals are currently disabled.", show_alert=True)
                return
            txt, markup = build_withdrawal_ui(chat_id, include_profile_back=True)
            edit_message(chat_id, msg_id, txt, reply_markup=markup)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            # --- PROCESS PENDING REFERRAL ---
            if db:
                doc = db.collection('users').document(str(chat_id)).get()
                if doc.exists:
                    u_data = doc.to_dict()
                    if u_data.get("referred_by") and not u_data.get("ref_paid"):
                        inviter = u_data["referred_by"]
                        db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                        reward = bot_settings.get("refer_reward", 0.2)
                        update_balance(inviter, reward)
                        db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)})
                        if inviter in user_cache:
                            user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
                        ref_msg = (
                            f"{PEM['gift']} <b>New Referral !</b>\n"
                            f"------------------\n"
                            f"🔥 <b>You Received {reward} TK</b>\n"
                            f"------------------\n"
                            f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                        )
                        send_message(inviter, render_body_text(ref_msg))
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "public_lb_refresh":
        # Refresh ONLY the public Main Menu Daily Leaderboard.
        txt, markup = build_daily_leaderboard_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        return

    elif data == "public_lb_close":
        # Close ONLY the public Main Menu Daily Leaderboard message.
        delete_message(chat_id, msg_id)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        delete_message(chat_id, msg_id)

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_dxa_edit":
        was_withdraw_group = temp_data.get(chat_id, {}).get("key") == "w_group"
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        if was_withdraw_group:
            edit_message(chat_id, msg_id, render_body_text("💸 <b>WITHDRAWAL MANAGEMENT</b>"), reply_markup=withdrawal_management_keyboard())
        else:
            edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            btn_text = f"{c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    # 🌟 X রিমুভ করে ক্লিন রেঞ্জ নেওয়া হলো
                    num = t.get("real_range", t.get("number", "").replace("X", "").replace("x", "")).replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        # শুধুমাত্র StexSMS Services থেকে রেঞ্জ নিবো (Search Countries নিবো না, কারণ ওগুলোতে শুধু দেশের কোড থাকে)
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    # 🌟 এখানেও সেভ করা রেঞ্জ থেকে X সরিয়ে নিচ্ছি
                    known_ranges.add(r.replace("X", "").replace("x", ""))
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        temp_row = []
        for r, count in r_list:
            # 🌟 বাটনে এবং কলব্যাকে যাতে কোনো X না থাকে তা নিশ্চিত করা হলো
            clean_r = str(r).replace("X", "").replace("x", "")
            temp_row.append({"text": f"{clean_r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "callback_data": f"c_n_s_{clean_r}_{srv_query}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    # --- User Management Flows Integration ---
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data.startswith("um_all_page_") or data.startswith("um_banned_page_"):
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can view user lists.", show_alert=True)
            return
        listing_type = "banned" if data.startswith("um_banned_page_") else "all"
        try:
            page = int(data.rsplit("_", 1)[1])
        except (ValueError, IndexError):
            page = 0
        listing_text, listing_keyboard = render_user_management_listing(listing_type, page)
        edit_message(chat_id, msg_id, listing_text, reply_markup=listing_keyboard)
        answer_callback(call["id"])

    elif data == "um_all_user_balance":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can view all user balances.", show_alert=True)
            return
        send_message(chat_id, render_body_text("⏳ Preparing all user balances and CSV..."))
        threading.Thread(target=send_all_user_balance_report, args=(chat_id,), daemon=True).start()

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    # --- Menu Design Integration ---
    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except: pass

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"]) 
        if chat_id in user_states: del user_states[chat_id] 
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except: pass

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>\n\n<i>(Only normal Emojis supported here!)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ আপনার ব্যালেন্স অপর্যাপ্ত! মিনিমাম {min_w} ৳ প্রয়োজন।", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        amount_prompt = (
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "       💳 <b>PAYMENT DETAILS</b>\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"🏦 <b>METHOD SELECTED</b>\n<code>{html.escape(str(method))}</code>\n"
            f"💰 <b>AVAILABLE BALANCE</b>  <code>{bal} ৳</code>\n"
            f"📌 <b>MINIMUM AMOUNT</b>  <code>{min_w} ৳</code>\n\n"
            "✍️ <b>ENTER WITHDRAWAL AMOUNT</b>\n"
            "<i>Send the amount in numbers, for example: 100</i>"
        )
        edit_message(chat_id, msg_id, render_body_text(amount_prompt), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "setup_otp_group_emojis":
        user_states.pop(chat_id, None)
        temp_data.pop(chat_id, None)
        txt_m, kb_m = build_otp_group_emoji_manager_ui()
        edit_message(chat_id, msg_id, txt_m, reply_markup=kb_m)

    elif data.startswith("otp_slot_reset_"):
        slot = data[len("otp_slot_reset_"):]
        if slot in OTP_GROUP_SLOTS:
            bot_settings.setdefault("otp_group_emojis", {})[slot] = None
            save_db()
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            notice = f"{PEM['ok']} <b>{html.escape(OTP_GROUP_SLOTS[slot]['label'])}</b> ডিফল্ট ইমোজিতে রিসেট হয়েছে!"
            txt_m, kb_m = build_otp_group_emoji_manager_ui(notice=notice)
            edit_message(chat_id, msg_id, txt_m, reply_markup=kb_m)

    elif data.startswith("otp_slot_"):
        slot = data[len("otp_slot_"):]
        if slot not in OTP_GROUP_SLOTS:
            answer_callback(call["id"], "❌ Invalid emoji slot!", show_alert=True)
            return
        slot_info = OTP_GROUP_SLOTS[slot]
        current_html = _otp_group_emoji(slot, slot_info["fallback"])
        user_states[chat_id] = "wait_for_otp_group_emoji"
        temp_data[chat_id] = {"otp_slot": slot, "msg_id": msg_id}
        prompt = (
            f"✨ <b>SET {html.escape(slot_info['label'].upper())}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>কোথায় বসবে:</b> {html.escape(slot_info['where'])}\n"
            f"🎯 <b>বর্তমান ইমোজি:</b> {current_html}\n\n"
            "👇 এখন এই জায়গার জন্য আপনার পছন্দের <b>Telegram Premium Emoji</b> (অথবা সাধারণ ইমোজি) পাঠান:"
        )
        kb = {
            "inline_keyboard": [
                [{"text": "🔄 Reset This Slot", "callback_data": f"otp_slot_reset_{slot}", "style": "primary"}],
                [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "setup_otp_group_emojis", "style": "danger"}]
            ]
        }
        edit_message(chat_id, msg_id, prompt, reply_markup=kb)

    elif data == "otp_emoji_preview":
        sample_msg = _format_otp_group_message(
            "8801712345678",
            "Facebook",
            "BD",
            "Your Facebook confirmation code is 482910.",
            country_name_override="Bangladesh",
            otp_code="482910"
        )
        send_message(
            chat_id,
            sample_msg,
            reply_markup={"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
        )

    elif data == "otp_emoji_reset_all":
        bot_settings["otp_group_emojis"] = {s: None for s in OTP_GROUP_SLOTS}
        save_db()
        user_states.pop(chat_id, None)
        temp_data.pop(chat_id, None)
        txt_m, kb_m = build_otp_group_emoji_manager_ui(notice=f"{PEM['ok']} সব OTP Group ইমোজি ডিফল্টে রিসেট হয়েছে!")
        edit_message(chat_id, msg_id, txt_m, reply_markup=kb_m)

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text(
            "📝 <b>Send 1 or 2 Premium Emojis</b>\n\n"
            "এক মেসেজে ১টি অথবা ২টি Telegram Premium/Custom Emoji পাঠান।\n"
            "তারপর Service অথবা Country নির্বাচন করে যেটিতে সেট করতে চান সেটি বেছে নিন."
        ), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "emoji_target_service":
        if not temp_data.get(chat_id, {}).get("emoji_ids"):
            answer_callback(call["id"], "❌ Please send 1 or 2 Premium Emojis first!", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("🛠 <b>Select Service</b>\n\nযে Service-এ Premium Emoji সেট করতে চান সেটি নির্বাচন করুন:"), reply_markup=_emoji_management_services_keyboard())

    elif data == "emoji_target_country":
        if not temp_data.get(chat_id, {}).get("emoji_ids"):
            answer_callback(call["id"], "❌ Please send 1 or 2 Premium Emojis first!", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Select Country</b>\n\nযে Country-তে Premium Emoji সেট করতে চান সেটি নির্বাচন করুন:"), reply_markup=_emoji_management_countries_keyboard())

    elif data.startswith("emoji_set_srv_"):
        service = unquote(data[len("emoji_set_srv_"):])
        saved = temp_data.get(chat_id, {})
        ids = list(saved.get("emoji_ids") or [])[:2]
        chars = list(saved.get("emoji_chars") or [])[:2]
        if not ids:
            answer_callback(call["id"], "❌ Premium Emoji data পাওয়া যায়নি!", show_alert=True)
            return
        apps = bot_settings.setdefault("premium_apps", {})
        key = service.upper()
        existing = apps.get(key) or {}
        apps[key] = {
            "char": chars[0] if chars else existing.get("char", "📱"),
            "id": ids[0],
            "chars": chars,
            "ids": ids,
            "name": existing.get("name", service)
        }
        save_db()
        temp_data.pop(chat_id, None)
        user_states.pop(chat_id, None)
        preview = " ".join(chars)
        send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Service Premium Emoji saved!</b>\n\nService: <b>{html.escape(service)}</b>\nEmoji: {preview}"), reply_markup=emoji_settings_keyboard())
        answer_callback(call["id"], "✅ Saved!")

    elif data.startswith("emoji_set_cnt_"):
        country = unquote(data[len("emoji_set_cnt_"):])
        saved = temp_data.get(chat_id, {})
        ids = list(saved.get("emoji_ids") or [])[:2]
        chars = list(saved.get("emoji_chars") or [])[:2]
        if not ids:
            answer_callback(call["id"], "❌ Premium Emoji data পাওয়া যায়নি!", show_alert=True)
            return

        flags = bot_settings.setdefault("premium_flags", {})
        country_upper = country.upper()
        matched_key = None
        matched_data = None
        flag_items = sorted(flags.items(), key=lambda item: len(str((item[1] or {}).get("name", "") or "")), reverse=True)
        for code, data_item in flag_items:
            data_item = data_item or {}
            name = str(data_item.get("name", "") or "").strip()
            iso = str(data_item.get("iso", "") or "").strip().upper()
            if country_upper == name.upper() or name.upper() in country_upper or country_upper == iso or country_upper == str(code).upper():
                matched_key = code
                matched_data = data_item
                break

        if matched_key is None:
            matched_key = country_upper
            matched_data = {"name": country, "iso": "", "char": chars[0] if chars else "🌍"}

        matched_data = dict(matched_data or {})
        matched_data.update({
            "char": chars[0] if chars else matched_data.get("char", "🌍"),
            "id": ids[0],
            "chars": chars,
            "ids": ids,
            "name": matched_data.get("name") or country
        })
        flags[matched_key] = matched_data
        save_db()
        temp_data.pop(chat_id, None)
        user_states.pop(chat_id, None)
        preview = " ".join(chars)
        send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Country Premium Emoji saved!</b>\n\nCountry: <b>{html.escape(country)}</b>\nEmoji: {preview}"), reply_markup=emoji_settings_keyboard())
        answer_callback(call["id"], "✅ Saved!")

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "admin_sell_id_menu":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can manage SELL ID.", show_alert=True)
            return
        cur_link = str(bot_settings.get("sell_id_link", "") or "Not set")
        cur_text = str(bot_settings.get("sell_id_text") or "💼 <b>SELL ID</b>\n\nTap the button below to sell your ID:")
        edit_message(chat_id, msg_id, render_body_text(f"💼 <b>SELL ID SETTINGS</b>\n\n🔗 <b>Link:</b> <code>{html.escape(cur_link)}</code>\n\n📝 <b>Message Text:</b>\n{cur_text}"), reply_markup=admin_sell_id_keyboard())

    elif data == "admin_shop_menu":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can manage iX Shop.", show_alert=True)
            return
        cur_link = str(bot_settings.get("shop_link", "") or "Not set")
        cur_text = str(bot_settings.get("shop_text") or "🛒 <b>iX SHOP</b>\n\nTap the button below to open iX Shop:")
        edit_message(chat_id, msg_id, render_body_text(f"🛒 <b>iX SHOP SETTINGS</b>\n\n🔗 <b>Link:</b> <code>{html.escape(cur_link)}</code>\n\n📝 <b>Message Text:</b>\n{cur_text}"), reply_markup=admin_shop_keyboard())

    elif data == "set_sell_id_text":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can edit SELL ID text.", show_alert=True)
            return
        user_states[chat_id] = "wait_for_sell_id_text"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>EDIT SELL ID TEXT</b>\n\nSend the new message text to display above the SELL ID button (HTML &amp; Premium Emojis supported):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "admin_sell_id_menu", "style": "danger"}]]})

    elif data == "set_shop_text":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can edit iX Shop text.", show_alert=True)
            return
        user_states[chat_id] = "wait_for_shop_text"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>EDIT iX SHOP TEXT</b>\n\nSend the new message text to display above the iX Shop button (HTML &amp; Premium Emojis supported):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "admin_shop_menu", "style": "danger"}]]})

    elif data == "reset_sell_id_text":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can reset SELL ID text.", show_alert=True)
            return
        bot_settings["sell_id_text"] = "💼 <b>SELL ID</b>\n\nTap the button below to sell your ID:"
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"✅ <b>SELL ID Text Reset to Default!</b>\n\n{bot_settings['sell_id_text']}"), reply_markup=admin_sell_id_keyboard())

    elif data == "reset_shop_text":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can reset iX Shop text.", show_alert=True)
            return
        bot_settings["shop_text"] = "🛒 <b>iX SHOP</b>\n\nTap the button below to open iX Shop:"
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"✅ <b>iX Shop Text Reset to Default!</b>\n\n{bot_settings['shop_text']}"), reply_markup=admin_shop_keyboard())

    elif data == "set_sell_id_link":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can set the SELL ID link.", show_alert=True)
            return
        user_states[chat_id] = "wait_for_sell_id_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        current = str(bot_settings.get("sell_id_link", "") or "Not set")
        edit_message(chat_id, msg_id, render_body_text(f"🔗 <b>SET SELL ID LINK</b>\n\n<b>Current:</b> <code>{html.escape(current)}</code>\n\nSend the new SELL ID link (e.g. <code>https://t.me/username</code> or <code>@username</code>), or send <code>clear</code> to remove it:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "admin_sell_id_menu", "style": "danger"}]]})

    elif data == "set_shop_link":
        if not is_admin(call.get("from", {}).get("id", chat_id)):
            answer_callback(call["id"], "🚫 Only bot admins can set the iX Shop link.", show_alert=True)
            return
        user_states[chat_id] = "wait_for_shop_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        current = str(bot_settings.get("shop_link", "") or "Not set")
        edit_message(chat_id, msg_id, render_body_text(f"🛒 <b>SET iX SHOP LINK</b>\n\n<b>Current:</b> <code>{html.escape(current)}</code>\n\nSend the new iX Shop link (e.g. <code>https://t.me/username</code> or <code>@username</code>), or send <code>clear</code> to remove it:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "admin_shop_menu", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the numbers in a <b>.txt</b> or <b>.csv</b> file.\n\nCSV: only numbers from Column D are supported."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data == "dl_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ No used numbers found!", show_alert=True)
            return
        content = "\n".join(used_numbers_list).encode('utf-8')
        send_document(chat_id, "used_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "dl_unused":
        unused_list = [n["num"] for b in number_batches.values() for n in b["numbers"]]
        if not unused_list:
            answer_callback(call["id"], "❌ No unused numbers found!", show_alert=True)
            return
        content = "\n".join(unused_list).encode('utf-8')
        send_document(chat_id, "unused_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())

    elif data == "toggle_stex_auto":
        bot_settings["stex_auto"] = not bot_settings.get("stex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())
        answer_callback(call["id"], f"✅ Stex Auto Range is now {'ON' if bot_settings['stex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new StexSMS API Key (e.g. nxa_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})

    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select StexSMS Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ StexSMS Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})

    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})

    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>StexSMS Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "nx_add_srv":
        user_states[chat_id] = "wait_nx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        user_states[chat_id] = "wait_nx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("nx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
            bot_settings["stex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("nx_del_srv_"):
        srv = data.replace("nx_del_srv_", "")
        if srv in bot_settings["stex_services"]: del bot_settings["stex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})

    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["stex_services"].get(srv, {}): del bot_settings["stex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "toggle_voltx_auto":
        bot_settings["voltx_auto"] = not bot_settings.get("voltx_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())
        answer_callback(call["id"], f"✅ Voltx Auto Range is now {'ON' if bot_settings['voltx_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    # --- ZENEX CONTROL CALLBACKS ---
    elif data == "zenex_control":
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())

    elif data == "toggle_zenex_auto":
        bot_settings["zenex_auto"] = not bot_settings.get("zenex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())
        answer_callback(call["id"], f"✅ Zenex Auto Range is now {'ON' if bot_settings['zenex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_zenex_key":
        user_states[chat_id] = "wait_for_add_zenex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Zenex API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}]]})

    elif data == "view_zenex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("zenex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_znx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Zenex Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_znx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_keys", [])):
            del bot_settings["zenex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_zenex_keys", "id": call["id"]})

    elif data == "zenex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("zenex_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_zsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Zenex Allowed Ranges:</b>\nOnly these codes will be allowed in Zenex Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_zenex_search_country":
        user_states[chat_id] = "wait_for_add_zsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Zenex Range Code (e.g. 447):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_search_country", "style": "danger"}]]})

    elif data.startswith("del_zsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_search_countries", [])):
            del bot_settings["zenex_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "zenex_search_country", "id": call["id"]})

    elif data == "manage_zenex_srv":
        kb = []
        for srv in bot_settings.get("zenex_services", {}):
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": "5257969839313526622", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "zx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("💠 <b>Zenex Services Manager</b>\nManage your API-based manual services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "zx_add_srv":
        user_states[chat_id] = "wait_zx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_srv_"):
        srv = data.replace("zx_srv_", "")
        kb = []
        for c in bot_settings.get("zenex_services", {}).get(srv, {}):
            kb.append([{"text": f"{c} ({len(bot_settings['zenex_services'][srv][c])} Ranges)", "icon_custom_emoji_id": "5780471598922337683", "callback_data": f"zx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_zenex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_add_cnt_"):
        srv = data.replace("zx_add_cnt_", "")
        user_states[chat_id] = "wait_zx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. UK, USA):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["zenex_services"][srv].get(cnt, [])
        kb, row = [], []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"zx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_zx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 4473845XXX):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("zx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["zenex_services"].get(srv, {}).get(cnt, []):
            bot_settings["zenex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("zx_del_srv_"):
        srv = data.replace("zx_del_srv_", "")
        if srv in bot_settings["zenex_services"]: del bot_settings["zenex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_zenex_srv", "id": call["id"]})

    elif data.startswith("zx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["zenex_services"].get(srv, {}): del bot_settings["zenex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>\n\nSelect which type of panel system you want to manage:"
        kb = {"inline_keyboard": [
            [{"text": f"Manage API Panels ({api_count})", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"Manage Auto Captcha Panels ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {len(p_list)}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})

    elif data.startswith("add_ptype_"):
        pass

    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>\n<b>Num Col:</b> {p.get('num_col_name')} (Idx: {p.get('num_col_idx')})\n<b>Msg Col:</b> {p.get('msg_col_name')} (Idx: {p.get('msg_col_idx')})"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_api"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_tok"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Token for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_fapi"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                    
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                
                # 🌟 test connection supports sAjaxSource & HTML table parser
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                
            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return
                
                urls_to_try = []
                if full_url:
                    urls_to_try.append(full_url)
                else:
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.append(f"{url}{sep}token={token}")
                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                        urls_to_try.append(f"{url}{sep}key={token}")
                    
                parsed = []
                raw_text = ""
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                for try_url in urls_to_try:
                    try:
                        res = requests.get(try_url, headers=headers, timeout=10)
                        raw_text = res.text
                        parsed = parse_panel_response(raw_text, p)
                        if parsed:
                            if not full_url and try_url != url and token:
                                p["api_url"] = try_url.replace(token, "{token}")
                                save_db()
                            break
                    except: pass
                 
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = _get_effective_otp_service(num, msg, app_name)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "🔍 FULL TABLE DATA (A-Z)\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            fail_txt = f"⚠️ <b>Connected, but couldn't parse OTP data!</b>\n\n<i>আমি ওই লিংকের সম্পূর্ণ (A-Z) ডাটা একটি Text File এ পাঠিয়েছি। ফাইলটি ওপেন করে সঠিক Column Number (যেমন: [1], [3]) চেক করে প্যানেলে আপডেট করে নাও।</i>"
                            send_message(chat_id, render_body_text(fail_txt))
                        else:
                            send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but no HTML Table found!</b>\nMake sure the message link is correct."))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ <b>Error parsing HTML:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't find/parse OTP data.</b>\n\n<i>Make sure your API config is correct.</i>\n\nRaw HTML/Data (excerpt):\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "manage_service_country":
        user_states.pop(chat_id, None)
        temp_data.pop(chat_id, None)
        edit_message(chat_id, msg_id, render_body_text("📂 <b>MANAGE SERVICE &amp; COUNTRY</b>\n\nChoose an operation:"), reply_markup=_manage_service_country_keyboard())

    elif data == "msc_rename":
        services = _managed_local_services()
        if not services:
            answer_callback(call["id"], "❌ No uploaded services are available to rename.", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("✏️ <b>SELECT SERVICE TO RENAME</b>"), reply_markup=_managed_services_keyboard("rename", local_only=True))

    elif data == "msc_delete":
        services = _managed_local_services()
        if not services:
            answer_callback(call["id"], "❌ No uploaded services are available.", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("🗑️ <b>SELECT SERVICE FOR COUNTRY DELETION</b>"), reply_markup=_managed_services_keyboard("delete", local_only=True))

    elif data == "msc_rate":
        services = _managed_services()
        if not services:
            answer_callback(call["id"], "❌ No services are available.", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("💰 <b>SELECT SERVICE TO SET OTP RATE</b>"), reply_markup=_managed_services_keyboard("rate"))

    elif data.startswith("msc_srv_"):
        payload = data[len("msc_srv_"):]
        if "_" not in payload:
            answer_callback(call["id"], "❌ Invalid service selection.", show_alert=True)
            return
        action, service_key = payload.split("_", 1)
        local_only = action in {"rename", "delete"}
        service = _msc_find_service(service_key, local_only=local_only) if action in {"rename", "delete", "rate"} else None
        if service is None:
            answer_callback(call["id"], "❌ Service is no longer available.", show_alert=True)
            return
        if action == "rename":
            temp_data[chat_id] = {"msg_id": msg_id, "managed_service_old": service}
            user_states[chat_id] = "wait_for_managed_service_rename"
            edit_message(chat_id, msg_id, render_body_text(f"✏️ <b>RENAME SERVICE</b>\n\nCurrent name: <code>{html.escape(service)}</code>\n\nSend the new service name:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "callback_data": "msc_rename", "style": "danger"}]]})
        else:
            countries = _managed_countries(service, local_only=(action == "delete"))
            if not countries:
                answer_callback(call["id"], "❌ No countries are configured for this service.", show_alert=True)
                return
            title = "SELECT COUNTRY TO DELETE" if action == "delete" else "SELECT COUNTRY TO SET OTP RATE"
            edit_message(chat_id, msg_id, render_body_text(f"🌍 <b>{title}</b>\n\nService: <code>{html.escape(service)}</code>"), reply_markup=_managed_countries_keyboard(action, service, local_only=(action == "delete")))

    elif data.startswith("msc_cnt_"):
        payload = data[len("msc_cnt_"):]
        action, sep, rest = payload.partition("_")
        if not sep or "__" not in rest:
            answer_callback(call["id"], "❌ Invalid country selection.", show_alert=True)
            return
        service_key, country_key = rest.split("__", 1)
        local_only = action == "delete"
        service = _msc_find_service(service_key, local_only=local_only) if action in {"delete", "rate"} else None
        country = _msc_find_country(service, country_key, local_only=local_only) if service else None
        if service is None or country is None:
            answer_callback(call["id"], "❌ Service/Country is no longer available.", show_alert=True)
            return
        if action == "delete":
            confirm_data = f"msc_del_confirm_{_msc_key(service)}__{_msc_key(country)}"
            cancel_data = f"msc_del_cancel_{_msc_key(service)}__{_msc_key(country)}"
            kb = {"inline_keyboard": [[{"text": "✅ Confirm Delete", "callback_data": confirm_data, "style": "danger"}], [{"text": "Cancel", "callback_data": cancel_data, "style": "primary"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"⚠️ <b>CONFIRM COUNTRY DELETION</b>\n\nService: <code>{html.escape(service)}</code>\nCountry: <code>{html.escape(country)}</code>\n\nOnly this service's matching uploaded country files and available stock will be deleted. User balances and OTP history will not be changed."), reply_markup=kb)
        else:
            fallback = bot_settings.get("otp_reward", 0.0)
            for batch in number_batches.values():
                if str(batch.get("service", "")).strip() == service and str(batch.get("country", "")).strip() == country:
                    fallback = batch.get("rate", fallback)
                    break
            current = _get_service_country_price(service, country, fallback=fallback)
            temp_data[chat_id] = {"msg_id": msg_id, "managed_rate_service": service, "managed_rate_country": country}
            user_states[chat_id] = "wait_for_managed_otp_rate"
            edit_message(chat_id, msg_id, render_body_text(f"💰 <b>SET OTP RATE</b>\n\nService: <code>{html.escape(service)}</code>\nCountry: <code>{html.escape(country)}</code>\nCurrent rate: <b>{current:g} TK</b>\n\nSend the new rate:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "callback_data": f"msc_srv_rate_{_msc_key(service)}", "style": "danger"}]]})

    elif data.startswith("msc_del_cancel_"):
        payload = data[len("msc_del_cancel_"):]
        service = _msc_find_service(payload.split("__", 1)[0], local_only=True) if "__" in payload else None
        if service:
            _msc_refresh(chat_id, msg_id, render_body_text("🗑️ <b>SELECT COUNTRY TO DELETE</b>"), _managed_countries_keyboard("delete", service, local_only=True))
        else:
            _msc_refresh(chat_id, msg_id, render_body_text("📂 <b>MANAGE SERVICE &amp; COUNTRY</b>"), _manage_service_country_keyboard())

    elif data.startswith("msc_del_confirm_"):
        payload = data[len("msc_del_confirm_"):]
        if "__" not in payload:
            answer_callback(call["id"], "❌ Invalid deletion request.", show_alert=True)
            return
        service_key, country_key = payload.split("__", 1)
        service = _msc_find_service(service_key, local_only=True)
        country = _msc_find_country(service, country_key, local_only=True) if service else None
        if not service or not country:
            answer_callback(call["id"], "⚠️ No matching uploaded country files remain.", show_alert=True)
            _msc_refresh(chat_id, msg_id, render_body_text("📂 <b>MANAGE SERVICE &amp; COUNTRY</b>"), _manage_service_country_keyboard())
            return
        # list(...) snapshot: other threads (number upload / number fetch) change number_batches
        # at the same time; iterating the live dict could raise "dictionary changed size during
        # iteration" and abort the delete half-way.
        matching_ids = [bid for bid, batch in list(number_batches.items())
                        if isinstance(batch, dict)
                        and str(batch.get("service", "")).strip() == service
                        and str(batch.get("country", "")).strip() == country]
        removed_count = 0
        for batch_id in matching_ids:
            batch = number_batches.pop(batch_id, None) or {}
            removed_count += len(batch.get("numbers", []) or [])
        # Clear only price override for the selected service/country; other services stay untouched.
        # Keep a service-country rate if that country is still configured by an API provider.
        if country not in _managed_countries(service):
            prices = bot_settings.get("service_country_prices", {}) or {}
            service_prices = prices.get(service, {})
            for saved_country in list(service_prices):
                if str(saved_country).strip().casefold() == country.casefold():
                    service_prices.pop(saved_country, None)
            if not service_prices:
                prices.pop(service, None)
            bot_settings["service_country_prices"] = prices
        save_db()
        remaining = _managed_countries(service, local_only=True)
        _msc_refresh(chat_id, msg_id, render_body_text(f"✅ <b>Country deleted successfully.</b>\n\nService: <code>{html.escape(service)}</code>\nCountry: <code>{html.escape(country)}</code>\nAvailable numbers removed from stock: <b>{removed_count}</b>\n\nUser balance and OTP history were not modified."), _managed_countries_keyboard("delete", service, local_only=True) if remaining else _managed_services_keyboard("delete", local_only=True))
        # The background writer can lag up to ~15s on a big DB; if the bot restarted in that
        # window the deleted country came back. Flush right now so the delete is permanent.
        _write_local_db_now()

    elif data == "set_price":
        edit_message(chat_id, msg_id, render_body_text("💎 <b>SELECT YOUR SERVICE FOR CHANGE RATE:</b>"), reply_markup=set_price_services_keyboard())

    elif data.startswith("sp_srv_"):
        service = unquote(data[len("sp_srv_"):])
        if service not in _price_services():
            answer_callback(call["id"], "❌ Service is no longer configured!", show_alert=True)
            return
        countries = _price_countries_for_service(service)
        if not countries:
            answer_callback(call["id"], "❌ No countries configured for this service!", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>SELECT YOUR COUNTRY FOR CHANGE RATE:</b>"), reply_markup=set_price_countries_keyboard(service))

    elif data.startswith("sp_cnt_"):
        payload = data[len("sp_cnt_"):]
        if "__" not in payload:
            answer_callback(call["id"], "❌ Invalid country selection!", show_alert=True)
            return
        service_enc, country_enc = payload.split("__", 1)
        service = unquote(service_enc)
        country = unquote(country_enc)
        if service not in _price_services() or country not in _price_countries_for_service(service):
            answer_callback(call["id"], "❌ Service/Country is no longer configured!", show_alert=True)
            return
        name, _, _ = _country_display_info(country)
        temp_data[chat_id] = {"msg_id": msg_id, "price_service": service, "price_country": country}
        user_states[chat_id] = "wait_for_service_country_price"
        edit_message(chat_id, msg_id, render_body_text(f"💰 <b>Send Your New Price:</b>\n\n{html.escape(name)}"), reply_markup=set_price_country_prompt_keyboard(service))

    elif data == "withdrawal_management":
        if chat_id in user_states: user_states.pop(chat_id, None)
        edit_message(chat_id, msg_id, render_body_text("💸 <b>WITHDRAWAL MANAGEMENT</b>\n\nManage withdrawal availability, review requests, and configure the payout group."), reply_markup=withdrawal_management_keyboard())

    elif data == "withdrawal_requests":
        # Rehydrate pending requests after a bot restart when Firestore is available.
        if db:
            try:
                for doc in db.collection("withdrawals").where("status", "==", "pending").stream():
                    d = doc.to_dict() or {}
                    rid = str(d.get("request_id") or doc.id)
                    if rid not in pending_withdrawals and d.get("number"):
                        uid = d.get("user_id", "")
                        pending_withdrawals[rid] = {
                            "user_id": int(uid) if str(uid).isdigit() else uid,
                            "amount": d.get("amount", 0),
                            "method": d.get("method", "N/A"),
                            "number": d.get("number", ""),
                            "full_name": d.get("full_name", f"User {uid}")
                        }
            except Exception as load_pending_error:
                print(f"⚠️ Could not load pending withdrawals: {load_pending_error}")
        items = list(pending_withdrawals.items())
        if not items:
            body = "💸 <b>WITHDRAWAL REQUESTS</b>\n━━━━━━━━━━━━━━━━━━\n\n✅ No pending withdrawal requests right now."
        else:
            body = "💸 <b>WITHDRAWAL REQUESTS</b>\n━━━━━━━━━━━━━━━━━━\n\nSelect a request below to review and approve/reject it.\n\n"
            for req_id, req in items[:30]:
                body += f"👤 <b>{html.escape(str(req.get('full_name', 'User')))}</b> · <b>{req.get('amount', 0)} TK</b>\n🧾 <code>{html.escape(req_id)}</code>\n\n"
        edit_message(chat_id, msg_id, render_body_text(body), reply_markup=pending_withdrawals_keyboard())

    elif data.startswith("wview_"):
        req_id = data[len("wview_"):]
        req = pending_withdrawals.get(req_id)
        if not req:
            answer_callback(call["id"], "Request already processed or unavailable.", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💸 <b>WITHDRAWAL REQUESTS</b>\n\nNo pending request found for that item."), reply_markup=pending_withdrawals_keyboard())
            return
        num = str(req.get("number", ""))
        body = ("╭━━━━━━━━━━━━━━━━━━━━╮\n"
                "      💸 <b>WITHDRAWAL DETAILS</b>\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"👤 <b>USER</b>\n<a href='tg://user?id={req.get('user_id')}'>{html.escape(str(req.get('full_name', 'User')))}</a>\n"
                f"💰 <b>AMOUNT</b>  <code>{req.get('amount', 0)} ৳</code>\n"
                f"🏦 <b>METHOD</b>  <code>{html.escape(str(req.get('method', 'N/A')))}</code>\n"
                f"📱 <b>FULL ACCOUNT NUMBER</b>\n<code>{html.escape(num)}</code>\n\n"
                f"🧾 <b>REQUEST ID</b>  <code>{html.escape(req_id)}</code>\n"
                "🟡 <b>STATUS</b>  <u>PENDING</u>")
        kb = {"inline_keyboard": [[{"text": "✅ APPROVE", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "❌ REJECT", "callback_data": f"wrej_{req_id}", "style": "danger"}], [{"text": "⬅️ Back to Requests", "callback_data": "withdrawal_requests", "style": "primary"}]]}
        edit_message(chat_id, msg_id, render_body_text(body), reply_markup=kb)

    elif data == "set_payout_group":
        user_states[chat_id] = "wait_for_payout_group"
        temp_data[chat_id] = {"msg_id": msg_id}
        current = str(bot_settings.get("payout_group", "") or "Not configured")
        edit_message(chat_id, msg_id, render_body_text("📣 <b>SET PAYOUT GROUP</b>\n\nSend the payout group chat ID (for example <code>-1001234567890</code>) or a public group username (for example <code>@my_payout_group</code>). You can also send a t.me link to show an Open Group button, but the bot needs a chat ID or @username to post approved withdrawals automatically.\n\n<b>Current:</b> " + html.escape(current)), reply_markup={"inline_keyboard": [[{"text": "Cancel", "callback_data": "withdrawal_management", "style": "danger"}]]})

    elif data == "dxa_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "dxa_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("💸 <b>WITHDRAWAL MANAGEMENT</b>\n\nWithdrawal requests are now " + ("<b>ON</b>" if bot_settings["withdraw_on"] else "<b>OFF</b>") + "."), reply_markup=withdrawal_management_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data.startswith("dxa_"):
        key = data.replace("dxa_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_dxa"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_dxa_edit", "style": "danger"}]]}
            prompt = ("📣 <b>SET WITHDRAWAL REQUEST GROUP</b>\n\nSend a public group link like <code>https://t.me/groupname</code>, a public <code>@groupname</code>, or a numeric chat ID (usually <code>-100...</code>).\n\nPrivate invite links (<code>t.me/+...</code>) cannot be used by Telegram to send messages. For a private group, add the bot to the group and provide its numeric chat ID." if key_map[key] == "w_group" else f"📝 Please send the new value for <code>{key_map[key]}</code>:")
            edit_message(chat_id, msg_id, render_body_text(prompt), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data == "back_to_services":
        all_services = _services_for_mode(user_number_mode.get(chat_id))
        
        if not all_services:
            answer_callback(call["id"], "❌ No numbers or services available!", show_alert=True)
            return
            
        c_msg = bot_settings["custom_messages"].get("get_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
        
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        service_buttons = []
        for s in all_services:
            emoji_id = "5352694861990501856" 
            for app_key, app_data in apps_db.items():
                if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            service_buttons.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"})
        for i in range(0, len(service_buttons), 2):
            kb.append(service_buttons[i:i + 2])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        # Keep locally uploaded countries visible even after their stock reaches 0.
        # number_batches is persisted in bot_data.json, so this survives restarts.
        local_cnts = set([
            str(b.get("country", "")).strip()
            for b in number_batches.values()
            if str(b.get("service", "")).strip() == str(service).strip()
            and str(b.get("country", "")).strip()
        ])
        stex_cnts = set(bot_settings.get("stex_services", {}).get(service, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        zenex_cnts = set(bot_settings.get("zenex_services", {}).get(service, {}).keys())
        _mode = user_number_mode.get(chat_id)
        if _mode == "stock":
            all_countries = set(local_cnts)
        elif _mode == "api":
            all_countries = stex_cnts.union(voltx_cnts).union(zenex_cnts)
        else:
            all_countries = local_cnts.union(stex_cnts).union(voltx_cnts).union(zenex_cnts)
        
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        # Prefer the longest country name first (so "Nigeria" is not matched as "Niger").
        # Sorted once here instead of once for every country button.
        flag_items = sorted(
            flags_db.items(),
            key=lambda item: len(str((item[1] or {}).get("name", "") or "")),
            reverse=True,
        )
        for c in all_countries:
            emoji_id = "5780471598922337683" # Default flag
            # Country labels may contain an extra suffix/prefix (for example
            # "Tanzania 1", "Tanzania 36", or a Premium Emoji).  Resolve the
            # underlying country name instead of requiring an exact match.
            country_label = re.sub(r"<tg-emoji[^>]*>.*?</tg-emoji>", " ", str(c or ""), flags=re.I)
            country_label = re.sub(r"<[^>]+>", " ", country_label)
            country_label = country_label.strip()
            matched_flag = None

            # Prefer the longest country name first so names such as
            # "Nigeria" are not accidentally matched as "Niger".
            for flag_code, flag_data in flag_items:
                flag_data = flag_data or {}
                iso = str(flag_data.get("iso", "") or "").strip().upper()
                name = str(flag_data.get("name", "") or "").strip()
                label_upper = country_label.upper()
                if (
                    label_upper == iso
                    or label_upper == name.upper()
                    or name.upper() in label_upper
                    or label_upper in name.upper()
                    or str(c).strip().upper() == str(flag_code).strip().upper()
                ):
                    matched_flag = flag_data
                    break

            if matched_flag and matched_flag.get("id"):
                emoji_id = matched_flag["id"]
            
            # The service/country price is display/API pricing only.
            # Local uploaded numbers use their own batch rate when OTP is credited.
            otp_price = None
            service_price_map = bot_settings.get("service_country_prices", {}).get(_price_service_key(service), {}) or {}
            if c in service_price_map:
                otp_price = _get_service_country_price(service, c)
            else:
                # Preserve the old file-specific rate behaviour when no override exists.
                # Do not require b["numbers"] here: an uploaded country remains visible as (0).
                for b in ([] if _mode == "api" else number_batches.values()):
                    if (
                        str(b.get("service", "")).strip() == str(service).strip()
                        and str(b.get("country", "")).strip() == str(c).strip()
                        and "rate" in b
                    ):
                        otp_price = b.get("rate")
                        break
                if otp_price is None:
                    otp_price = bot_settings.get("otp_reward", 0.0)

            # Only Add Number/uploaded countries receive the local-stock count.
            # API/range-only countries keep their existing display without (0).
            local_stock_count = None
            for b in number_batches.values():
                if (
                    str(b.get("service", "")).strip() == str(service).strip()
                    and str(b.get("country", "")).strip() == str(c).strip()
                ):
                    local_stock_count = (local_stock_count or 0) + len(b.get("numbers", []) or [])

            if local_stock_count is not None and _mode != "api":
                country_btn_text = f"{c} | {otp_price}TK ({local_stock_count})"
            else:
                country_btn_text = f"{c} - {otp_price} TK/OTP"

            kb.append([{
                "text": country_btn_text,
                "icon_custom_emoji_id": emoji_id,
                "callback_data": f"g_c_{service}_{c}",
                "style": "success"
            }])        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_services", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        # ১. গ্লোবাল কুলডাউন চেক (সকল নাম্বার মেথডের জন্য)
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        
        # কুলডাউন আপডেট
        user_cooldowns[chat_id] = now
        
        # আগের নাম্বার এক্সপায়ার করা। Local assignment শেষ হওয়া পর্যন্ত
        # persist বন্ধ রাখা হবে, যাতে একই operation-এ DB বারবার rewrite না হয়।
        expire_previous_number(chat_id, persist=False)

        # যদি সার্চ নাম্বার থেকে আসে
        if data.startswith("c_n_s_"):
            is_voltx_req = data.endswith("_vtx")
            is_zenex_req = data.endswith("_znx")
            clean_data = data[:-4] if (is_voltx_req or is_zenex_req) else data
            parts_s = clean_data.split("_", 4)
            
            query = parts_s[3] if len(parts_s) > 3 else ""
            service_from_cb = parts_s[4] if len(parts_s) > 4 else None

            # `country` was previously undefined in this branch (it is only set further
            # below for the normal service flow) -> UnboundLocalError after the API
            # number was already taken, leaving "Processing... Finding Number..." forever.
            _hint = api_country_hint.get(chat_id) or {}
            country = _hint.get("country") if _hint.get("query") == query else None
            
            allowed_countries = bot_settings.get("search_countries", [])
            voltx_allowed = bot_settings.get("voltx_search_countries", [])
            
            zenex_allowed = bot_settings.get("zenex_search_countries", [])
            
            is_stex_allowed = any(query.startswith(c) for c in allowed_countries) if allowed_countries else False
            is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
            is_zenex_allowed = any(query.startswith(c) for c in zenex_allowed) if zenex_allowed else False
            is_zenex_req = data.endswith("_znx")
            
            if not is_voltx_req and not is_zenex_req and not is_stex_allowed and not is_voltx_allowed and not is_zenex_allowed:
                answer_callback(call["id"], "❌ This country code is not allowed for search!", show_alert=True)
                return
                
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = msg_id
            
            found_indices = []
            _skip_local = bool(_hint.get("force_api")) and _hint.get("query") == query
            for b_id, b_data in ([] if _skip_local else number_batches.items()):
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                api_found = False
                req_count = bot_settings.get("num_req", 1)
                
                # প্রথমে Zenex চেক করবে
                if is_zenex_allowed or is_zenex_req:
                    zenex_keys = bot_settings.get("zenex_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in zenex_keys:
                            try:
                                headers = {"mapikey": api_key}
                                payload = {"range": query, "is_national": False, "remove_plus": False}
                                res = requests.post(f"{ZENEX_BASE_URL}/v1/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("full_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("number", "")).replace("+", "")
                                    fetched_nums.append(num_str)
                                    zenex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_zenex_req = True 
                                    break
                            except: continue

                # তারপর Voltx চেক করবে
                if len(fetched_nums) < req_count and (is_voltx_allowed or is_voltx_req) and not is_zenex_req:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                payload = {"rid": query}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_voltx_req = True # মার্ক করে দিলাম যাতে পরবর্তীতে Voltx রিকোয়েস্ট হিসেবে কাজ করে
                                    break
                            except: continue

                # Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and (is_stex_allowed and not is_voltx_req and not is_zenex_req):
                    stex_keys = bot_settings.get("stex_keys", [])
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    break
                            except: continue
                        
                if not api_found:
                    answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id)
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    
                    # Use the configured service-country OTP rate when present; otherwise preserve upload-batch rate.
                    batch_data = number_batches[b_id]
                    fallback_rate = float(batch_data.get("rate", bot_settings.get("otp_reward", 0.0)))
                    assigned_service = str(service_from_cb or batch_data.get("service", "")).strip()
                    assigned_country = str(batch_data.get("country", "")).strip()
                    resolved_rate = _get_service_country_price(assigned_service, assigned_country, fallback=fallback_rate)
                    _set_assigned_number_rate(num_str, resolved_rate)
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            if service_from_cb:
                app_full_name, _ = get_service_info_html(service_from_cb)
                emoji_id_srv = "5337302974806922068"
                for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                    if service_from_cb.upper() == app_key or service_from_cb.upper() in app_key or app_key in service_from_cb.upper():
                        if "id" in app_data: emoji_id_srv = app_data["id"]; break
                kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "primary"}])

            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id=\"{flag_emoji_id}\">{flag_data["char"]}</tg-emoji>'
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                premium_flag = get_premium_flag_for_number(num)
                number_btn = {"text": f"{display_num}", "copy_text": {"text": display_num}, "style": "success"}
                if premium_flag:
                    number_btn["icon_custom_emoji_id"] = premium_flag["id"]
                kb.append([number_btn])
            
            vtx_ext = "_vtx" if is_voltx_req else "_znx" if is_zenex_req else ""
            srv_ext = f"_{service_from_cb}" if service_from_cb else ""
            kb.append([
                {"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "danger"},
                {"text": "Remove Prefix", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "add_prefix", "style": "primary"}
            ])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
                
            if service_from_cb:
                kb.append([
                    {"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"g_s_{service_from_cb}", "style": "danger"},
                    {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}
                ])
            
            text_numbers = render_body_text(f"{country_emoji_html} NEW NUMBER\n")
            for _assigned_num in fetched_nums:
                assigned_number_owners[_clean_assigned_number(_assigned_num)] = chat_id
                _num_country = country
                if not _num_country:
                    try: _num_country = get_flag_info_html(str(_assigned_num), return_full_name=True)
                    except Exception: _num_country = ""
                if _num_country:
                    assigned_number_countries[_clean_assigned_number(_assigned_num)] = _num_country
            if service_from_cb:
                for _assigned_num in fetched_nums:
                    assigned_number_services[_assigned_num] = service_from_cb
                    # Do not overwrite a local uploaded number's batch price.
                    # Only numbers that did not already receive a local rate are API numbers.
                    if _assigned_num not in assigned_number_rates:
                        _set_assigned_number_rate(_assigned_num, _get_price_for_number(service_from_cb, _assigned_num))
                save_db()
            edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "service": service_from_cb, "prefix_removed": False}
            # Stop the button's loading spinner now that the numbers are shown.
            threading.Thread(target=answer_callback, args=(call["id"],)).start()
            save_db()
            return

        # যদি আপলোড করা বা সার্ভিস থেকে আসে
        parts = data.split("_")
        service = parts[2]
        country = parts[3]
        _mode = user_number_mode.get(chat_id)  # "stock" | "api" | None (old combined behaviour)

        available_indices = []
        # Check Local Stock First. Only matching service/country batches are scanned.
        # Use reservoir sampling so selection remains random across the whole
        # matching stock without building a potentially huge candidate list.
        wanted_count = max(1, int(bot_settings.get("num_req", 1) or 1))
        eligible_seen = 0
        for b_id, b_data in number_batches.items():
            if b_data.get("service") != service or b_data.get("country") != country or _mode == "api":
                continue
            for idx, n_obj in enumerate(b_data.get("numbers", [])):
                if chat_id in n_obj.get("used_by", []):
                    continue
                eligible_seen += 1
                candidate = (b_id, idx)
                if len(available_indices) < wanted_count:
                    available_indices.append(candidate)
                else:
                    replace_at = random.randrange(eligible_seen)
                    if replace_at < wanted_count:
                        available_indices[replace_at] = candidate

        # GET NUMBER STOCK: uploaded files only, never fall back to the API ranges.
        if not available_indices and _mode == "stock":
            answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        # IF NO LOCAL STOCK, Check StexSMS, Voltx & Zenex Services
        if not available_indices:
            stex_srv_data = bot_settings.get("stex_services", {}).get(service, {}).get(country)
            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            zenex_srv_data = bot_settings.get("zenex_services", {}).get(service, {}).get(country)
            
            target_range = None
            is_voltx = False
            is_zenex = False
            
            if stex_srv_data and len(stex_srv_data) > 0:
                target_range = random.choice(stex_srv_data)
            elif voltx_srv_data and len(voltx_srv_data) > 0:
                target_range = random.choice(voltx_srv_data)
                is_voltx = True
            elif zenex_srv_data and len(zenex_srv_data) > 0:
                target_range = random.choice(zenex_srv_data)
                is_zenex = True
                
            if target_range:
                user_cooldowns[chat_id] = 0
                api_country_hint[chat_id] = {"query": str(target_range), "country": country, "force_api": _mode == "api"}
                vtx_flag = "_vtx" if is_voltx else "_znx" if is_zenex else ""
                handle_callback({"message": call["message"], "data": f"c_n_s_{target_range}_{service}{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Number out of stock or range missing!", show_alert=True)
                if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                return

        random.shuffle(available_indices)
        
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            
            fetched_nums.append(n_obj["num"])
            
            # Configured service-country OTP rate takes priority over file/global rate.
            batch_data = number_batches[b_id]
            fallback_rate = float(batch_data.get("rate", bot_settings.get("otp_reward", 0.0)))
            resolved_rate = _get_service_country_price(service, country, fallback=fallback_rate)
            _set_assigned_number_rate(n_obj["num"], resolved_rate)
            
            n_obj["shares"] += 1
            n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["to_remove"] = True
                used_numbers_list.append(n_obj["num"])

        # Remove only exhausted numbers from the batches that were actually used.
        # The old code rebuilt every uploaded batch on every assignment.
        for b_id in {b_id for b_id, _ in available_indices}:
            batch = number_batches.get(b_id)
            if batch and any(n.get("to_remove") for n in batch.get("numbers", [])):
                batch["numbers"] = [n for n in batch.get("numbers", []) if not n.get("to_remove")]

        if not fetched_nums:
            answer_callback(call["id"], "❌ You have already taken all numbers or stock is empty!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id = app_data["id"]
                    break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "primary"}]]
        
        flags_db = bot_settings.get("premium_flags", {})
        country_emoji_html = ""
        for num in fetched_nums:
            country_emoji_html = ""
            char_flag, iso = get_flag_and_code(num)
            display_num = str(num).replace("+", "").replace(" ", "").replace("-", "")
            
            flag_emoji_id = "5780471598922337683" # Default Flag
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: 
                        flag_emoji_id = flag_data["id"]
                        country_emoji_html = f'<tg-emoji emoji-id=\"{flag_emoji_id}\">{flag_data["char"]}</tg-emoji>'
                    break
            
            if not country_emoji_html: country_emoji_html = char_flag
            premium_flag = get_premium_flag_for_number(num)
            number_btn = {"text": f"{display_num}", "copy_text": {"text": display_num}, "style": "success"}
            if premium_flag:
                number_btn["icon_custom_emoji_id"] = premium_flag["id"]
            kb.append([number_btn])
            
        kb.append([
            {"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
            {"text": "Remove Prefix", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "add_prefix", "style": "primary"}
        ])
                   
        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        for c_b in c_btns: 
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([
            {"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"g_s_{service}", "style": "danger"},
            {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}
        ])
        
        text_numbers = render_body_text(f"{country_emoji_html} NEW NUMBER\n")
        for _assigned_num in fetched_nums:
            assigned_number_services[_assigned_num] = service
            assigned_number_countries[_clean_assigned_number(_assigned_num)] = country
            assigned_number_owners[_clean_assigned_number(_assigned_num)] = chat_id

        # Persist the complete local assignment once: expired session + assigned
        # numbers + service mapping + active session. This replaces multiple full
        # bot_data.json rewrites in the old flow.
        # Telegram API errors are returned as {"ok": false}; they do not raise
        # exceptions. Check the result explicitly so an unsuccessful edit does
        # not silently consume stock without showing the assigned numbers.
        delivery_ok = False
        try:
            edit_res = edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if edit_res and edit_res.get("ok"):
                delivery_ok = True
                session_msg_id = msg_id
            else:
                print(f"[LOCAL NUMBER DISPLAY] editMessageText failed for chat={chat_id}: "
                      f"{(edit_res or {}).get('description', edit_res)}")
        except Exception as e:
            print(f"[LOCAL NUMBER DISPLAY] editMessageText exception for chat={chat_id}: {e}")

        if not delivery_ok:
            # Try a normal send first. Keep the API's actual error in logs so a
            # country-specific Telegram rejection can be diagnosed precisely.
            try:
                msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
                if msg_res and msg_res.get("ok") and isinstance(msg_res.get("result"), dict):
                    delivery_ok = True
                    session_msg_id = msg_res["result"]["message_id"]
                else:
                    print(f"[LOCAL NUMBER DISPLAY] sendMessage failed for chat={chat_id}: "
                          f"{(msg_res or {}).get('description', msg_res)}")
            except Exception as e:
                msg_res = None
                print(f"[LOCAL NUMBER DISPLAY] sendMessage exception for chat={chat_id}: {e}")

            if not delivery_ok:
                # Fallback 1: remove custom emoji IDs from every button AND from
                # message text. A bad country-specific premium-flag emoji can
                # cause both editMessageText and sendMessage to be rejected.
                plain_kb = []
                for row in kb:
                    plain_row = []
                    for button in row:
                        plain_button = dict(button)
                        plain_button.pop("icon_custom_emoji_id", None)
                        plain_row.append(plain_button)
                    plain_kb.append(plain_row)
                plain_text = re.sub(
                    r'<tg-emoji\b[^>]*>(.*?)</tg-emoji>', r'\1', str(text_numbers), flags=re.I | re.S
                )
                try:
                    retry_res = send_message(chat_id, plain_text, reply_markup={"inline_keyboard": plain_kb})
                    if retry_res and retry_res.get("ok") and isinstance(retry_res.get("result"), dict):
                        delivery_ok = True
                        session_msg_id = retry_res["result"]["message_id"]
                        kb = plain_kb
                        text_numbers = plain_text
                    else:
                        print(f"[LOCAL NUMBER DISPLAY] plain text/keyboard retry failed for chat={chat_id}: "
                              f"{(retry_res or {}).get('description', retry_res)}")
                except Exception as e:
                    print(f"[LOCAL NUMBER DISPLAY] plain text/keyboard retry exception for chat={chat_id}: {e}")

            if not delivery_ok:
                # Fallback 2: basic Telegram-compatible buttons only. This also
                # handles API implementations that reject newer copy_text/style
                # fields while preserving the number as ordinary button text.
                basic_kb = []
                for row in kb:
                    basic_row = []
                    for button in row:
                        basic_button = {k: v for k, v in button.items()
                                        if k in ("text", "callback_data", "url", "web_app", "login_url", "switch_inline_query", "switch_inline_query_current_chat")}
                        if basic_button.get("text"):
                            basic_row.append(basic_button)
                    if basic_row:
                        basic_kb.append(basic_row)
                try:
                    basic_res = send_message(chat_id, plain_text, reply_markup={"inline_keyboard": basic_kb})
                    if basic_res and basic_res.get("ok") and isinstance(basic_res.get("result"), dict):
                        delivery_ok = True
                        session_msg_id = basic_res["result"]["message_id"]
                        kb = basic_kb
                        text_numbers = plain_text
                    else:
                        print(f"[LOCAL NUMBER DISPLAY] basic keyboard retry failed for chat={chat_id}: "
                              f"{(basic_res or {}).get('description', basic_res)}")
                except Exception as e:
                    print(f"[LOCAL NUMBER DISPLAY] basic keyboard retry exception for chat={chat_id}: {e}")

        if delivery_ok:
            user_active_sessions[chat_id] = {"msg_id": session_msg_id, "nums": fetched_nums, "service": service, "prefix_removed": False}
            # Stop the button's loading spinner now that the numbers are shown.
            threading.Thread(target=answer_callback, args=(call["id"],)).start()
            save_db()
        else:
            # Restore the local stock if Telegram rejected both ways of
            # displaying it, so numbers are not silently consumed.
            for b_id, idx in available_indices:
                batch = number_batches.get(b_id)
                if not batch:
                    continue
                nums = batch.get("numbers", [])
                if idx < len(nums):
                    n_obj = nums[idx]
                    if n_obj.get("num") in fetched_nums:
                        n_obj["shares"] = max(0, int(n_obj.get("shares", 0)) - 1)
                        used_by = n_obj.get("used_by", [])
                        if chat_id in used_by:
                            used_by.remove(chat_id)
                        n_obj.pop("to_remove", None)
                        if n_obj.get("num") in used_numbers_list:
                            used_numbers_list.remove(n_obj.get("num"))
            save_db()
            answer_callback(call["id"], "❌ নম্বর পাঠানো যায়নি। আবার চেষ্টা করুন।", show_alert=True)

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        # অ্যাডমিন চেক (User ID চেক করতে হবে)
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = str(req_data.get("full_name") or "User")
            
            # Keep the full account number visible to admins for payout processing.
            # The separate public payout group message below remains masked for privacy.
            masked_num = num
            
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
            new_text = (
                f"💎 <b>━━━ WITHDRAWAL {status_text} ━━━</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>USER NAME</b>\n<blockquote>{html.escape(full_name)}</blockquote>\n"
                f"💰 <b>AMOUNT</b>  <code>{amt} TK</code>\n"
                f"🏦 <b>PAYMENT METHOD</b>  {html.escape(str(req_data['method']))}\n"
                f"📱 <b>ACCOUNT NUMBER</b>\n<code>{html.escape(str(masked_num))}</code>\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🧾 <b>REQUEST ID</b>  <code>{html.escape(str(req_id))}</code>\n"
                f"{'✅' if action == 'APPROVE' else '❌'} <b>FINAL STATUS</b>  {status_text}\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            
            kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(new_text), reply_markup=kb)
            
            if action == "REJECT":
                update_balance(u_id, amt) 
                send_message(u_id, render_body_text(f"❌ Your {amt} TK withdrawal request was rejected. Balance refunded."))
            else:
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} TK withdrawal request has been paid successfully!"))
                payout_target = str(bot_settings.get("payout_group_target") or bot_settings.get("payout_group", "") or "").strip()
                if payout_target and not payout_target.startswith(("https://t.me/", "http://t.me/")):
                    payout_number = str(req_data.get("number", ""))
                    payout_masked = f"{payout_number[:4]}••••{payout_number[-3:]}" if len(payout_number) >= 7 else payout_number
                    payout_msg = (
                        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                        "       💎 <b>PAYOUT COMPLETED</b>\n"
                        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                        f"👤 <b>USER</b>\n<blockquote>{html.escape(str(full_name))}</blockquote>\n"
                        f"💰 <b>PAID AMOUNT</b>  <code>{amt} ৳</code>\n"
                        f"🏦 <b>PAYMENT METHOD</b>  <code>{html.escape(str(req_data.get('method', 'N/A')))}</code>\n"
                        f"📱 <b>ACCOUNT (MASKED)</b>\n<code>{html.escape(payout_masked)}</code>\n\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧾 <b>REFERENCE ID</b>  <code>{html.escape(str(req_id))}</code>\n"
                        "🟢 <b>PAYMENT STATUS</b>  <u>PAID</u>\n"
                        "━━━━━━━━━━━━━━━━━━━━"
                    )
                    try:
                        send_message(payout_target, render_body_text(payout_msg))
                    except Exception as payout_error:
                        print(f"⚠️ Payout group message failed: {payout_error}")
            
            if db:
                try: db.collection('withdrawals').document(req_id).update({"status": "approved" if action == "APPROVE" else "rejected"})
                except: pass
                
            del pending_withdrawals[req_id]
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

# ==========================================
# Polling Loop
# ==========================================
def poll_otp_with_status(number_id, num_str, owner_id, api_key):
    headers = {"X-API-Key": api_key}
    for _ in range(150): # 150 * 4 seconds = 10 Minutes Polling
        try:
            res = _timed_api_get(f"{STEX_BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=10, label="STEX:assigned_number_sms")
            data = res.json()
            if data.get("success") and data.get("otp"):
                print(f"[OTP TIMING][API RESULT] provider=STEX:assigned_number otp_detected_after_request")
                otp = str(data["otp"])
                msg_text = data.get("message", f"Your code is {otp}")
                
                # 🌟 সম্পূর্ণ মেসেজ থেকে ড্যাশসহ বা বড় OTP খোঁজার ফিক্স
                extracted_otp = extract_otp_code(msg_text)
                if extracted_otp and len(extracted_otp) > len(otp):
                    otp = extracted_otp
                    
                # 🌟 সম্পূর্ণ মেসেজ থেকে সার্ভিস/অ্যাপ চেনার ফিক্স
                app_name = data.get("service", "StexSMS Service")
                detected_app = detect_service(msg_text)
                if detected_app:
                    app_name = detected_app
                
                unique_id = f"POLL_{number_id}_{msg_text}"
                if unique_id not in processed_otps:
                    processed_otps.add(unique_id)
                    
                    char, iso = get_flag_and_code(num_str)
                    app_full_name, prem_app_html = _get_effective_otp_service(num_str, msg_text, app_name)
                    
                    global recent_traffic
                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    recent_traffic.append({"traffic_service": get_assigned_service_for_number(num_str), "service": app_full_name, "iso": iso, "flag": char, "number": num_str, "time": current_time, "traffic_source": "otp_group"})
                    save_local_db()
                    
                    display_num = f"+{num_str}" if not str(num_str).startswith("+") else str(num_str)
                    masked = mask_number(display_num)
                    lang = detect_language(msg_text)
                    
                    display_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} {masked} {lang}\n╚═══════════════╝")
                    
                    send_otp_to_groups_async(display_msg, otp)
                    
                    deliver_inbox_otp_fast(owner_id, otp, num_str if "num_str" in locals() else num, display_num, app_full_name, iso, prem_app_html)
                break
        except: pass
        time.sleep(4)





def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = _timed_api_get(f"{STEX_BASE_URL}/success-otp", headers=headers, timeout=10, label="STEX:success_otp")
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        print(f"[OTP TIMING][API RESULT] provider=STEX otp_records={len(resp_data['data']['otps'])}")
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Stex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"STEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                assigned_country = get_assigned_country_for_number(num)
                                app_full_name, prem_app_html = _get_effective_otp_service(num, msg_text, app_name)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"traffic_service": get_assigned_service_for_number(num), "service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "traffic_source": "otp_group"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = _format_otp_group_message(display_num, app_full_name, iso, msg_text, assigned_country, otp_code=otp)
                                
                                send_otp_to_groups_async(display_msg, otp)
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    deliver_inbox_otp_fast(owner_id, otp, num_str if "num_str" in locals() else num, display_num, app_full_name, iso, prem_app_html)
                except: pass
        except: pass
        time.sleep(5)


def stex_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            if stex_keys:
                api_key = stex_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{STEX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9]
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"STEX_{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic for Stex every 2 minutes
                    if bot_settings.get("stex_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
                        if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["stex_services"]:
                                bot_settings["stex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["stex_services"][srv]:
                                    bot_settings["stex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["stex_services"][srv][full_country_name]:
                                        bot_settings["stex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["search_countries"]:
                                        bot_settings["search_countries"].append(country_code)
                                        changed = True

                        _hit_srv, _hit_country, _hit_range = _recent_hit_index(recent_traffic, current_time)
                        services_to_remove = []
                        for srv, countries in list(bot_settings["stex_services"].items()):
                            srv_hit = _hit_srv.get(srv.upper(), 0)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = _hit_country.get((srv.upper(), country), 0)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = _hit_range.get((srv.upper(), rng), 0)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["stex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["stex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)


def voltx_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            if not bot_settings.get("voltx_on", True):
                time.sleep(5)
                continue
            voltx_keys = bot_settings.get("voltx_keys", [])
            if voltx_keys:
                api_key = voltx_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{VOLTX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9] # 9 ডিজিটের বেশি হলে প্রথম 9 ডিজিট নেবে
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic every 2 minutes (120 seconds)
                    if bot_settings.get("voltx_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
                        if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
                        
                        # --- ১. Auto ADD Logic ---
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)] # Top 6 Services
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["voltx_services"]:
                                bot_settings["voltx_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)] # Top 3 Countries
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["voltx_services"][srv]:
                                    bot_settings["voltx_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)] # Top 2 Ranges
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["voltx_services"][srv][full_country_name]:
                                        bot_settings["voltx_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    # 🌟 শুধুমাত্র ৩ ডিজিট কান্ট্রি কোড অ্যাড করবে
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["voltx_search_countries"]:
                                        bot_settings["voltx_search_countries"].append(country_code)
                                        changed = True

                        # --- ২. Auto DELETE Logic (Only if NO traffic in the LAST 120 SECONDS) ---
                        _hit_srv, _hit_country, _hit_range = _recent_hit_index(recent_traffic, current_time)
                        services_to_remove = []
                        for srv, countries in list(bot_settings["voltx_services"].items()):
                            # চেক করবে গত ১২০ সেকেন্ডে কোনো ট্রাফিক আছে কি না
                            srv_hit = _hit_srv.get(srv.upper(), 0)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = _hit_country.get((srv.upper(), country), 0)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = _hit_range.get((srv.upper(), rng), 0)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["voltx_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["voltx_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)


def zenex_console_listener():
    global recent_traffic, bot_settings
    last_auto_update = time.time()
    zenex_last_hits = {} 
    
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            if zenex_keys:
                api_key = zenex_keys[0]
                headers = {"mapikey": api_key}
                res = requests.get(f"{ZENEX_BASE_URL}/v1/active-ranges", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("success") and "data" in data and "active_ranges" in data["data"]:
                    current_time = time.time()
                    new_hits_added = False
                    
                    for hit in data["data"]["active_ranges"]:
                        range_str = str(hit.get("range", "")).replace("X", "").replace("x", "")
                        sid = str(hit.get("service", "Unknown")).upper()
                        hits_count = int(hit.get("hits", 1))
                        
                        if range_str:
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, "")
                            
                            range_key = f"{range_str}_{app_full_name}"
                            prev_hits = zenex_last_hits.get(range_key, 0)
                            
                            if hits_count > prev_hits:
                                new_hits = hits_count - prev_hits
                            else:
                                new_hits = hits_count
                                
                            zenex_last_hits[range_key] = hits_count
                            if new_hits > 150: new_hits = 150
                            
                            for _ in range(new_hits):
                                recent_traffic.append({
                                    "service": app_full_name,
                                    "iso": iso,
                                    "flag": char,
                                    "number": f"{range_str}XXX", 
                                    "time": current_time,
                                    "real_range": range_str,
                                    "source": "zenex"
                                })
                                new_hits_added = True
                            
                    if new_hits_added:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    if bot_settings.get("zenex_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
                        if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if t.get("source") == "zenex" and "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["zenex_services"]:
                                bot_settings["zenex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("source") == "zenex" and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["zenex_services"][srv]:
                                    bot_settings["zenex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and t.get("source") == "zenex" and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["zenex_services"][srv][full_country_name]:
                                        bot_settings["zenex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["zenex_search_countries"]:
                                        bot_settings["zenex_search_countries"].append(country_code)
                                        changed = True

                        _hit_srv, _hit_country, _hit_range = _recent_hit_index(recent_traffic, current_time, source="zenex")
                        services_to_remove = []
                        for srv, countries in list(bot_settings["zenex_services"].items()):
                            srv_hit = _hit_srv.get(srv.upper(), 0)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = _hit_country.get((srv.upper(), country), 0)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = _hit_range.get((srv.upper(), rng), 0)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["zenex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["zenex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)


def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = _timed_api_get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10, label="VOLTX:success_otp")
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        print(f"[OTP TIMING][API RESULT] provider=VOLTX otp_records={len(resp_data['data']['otps'])}")
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                assigned_country = get_assigned_country_for_number(num)
                                app_full_name, prem_app_html = _get_effective_otp_service(num, msg_text, app_name)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"traffic_service": get_assigned_service_for_number(num), "service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "traffic_source": "otp_group"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = _format_otp_group_message(display_num, app_full_name, iso, msg_text, assigned_country, otp_code=otp)
                                
                                send_otp_to_groups_async(display_msg, otp)
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for voltx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_voltx = str(voltx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_voltx == clean_api_num or (len(clean_voltx) >= 8 and clean_voltx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_voltx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    deliver_inbox_otp_fast(owner_id, otp, num_str if "num_str" in locals() else num, display_num, app_full_name, iso, prem_app_html)
                except: pass
        except: pass
        time.sleep(5)


def zenex_sms_listener():
    global processed_otps, recent_traffic, zenex_assigned_numbers
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            for api_key in zenex_keys:
                try:
                    headers = {"mapikey": api_key}
                    res = _timed_api_get(f"{ZENEX_BASE_URL}/v1/numsuccess/info", headers=headers, timeout=10, label="ZENEX:success_otp")
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        print(f"[OTP TIMING][API RESULT] provider=ZENEX otp_records={len(resp_data['data']['otps'])}")
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("otp", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("nid", otp))
                            
                            app_name = "Zenex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"ZENEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                assigned_country = get_assigned_country_for_number(num)
                                app_full_name, prem_app_html = _get_effective_otp_service(num, msg_text, app_name)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"traffic_service": get_assigned_service_for_number(num), "service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "traffic_source": "otp_group"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = _format_otp_group_message(display_num, app_full_name, iso, msg_text, assigned_country, otp_code=otp)
                                
                                send_otp_to_groups_async(display_msg, otp)
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for zenex_n, n_owner in zenex_assigned_numbers.items():
                                        clean_zenex = str(zenex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_zenex == clean_api_num or (len(clean_zenex) >= 8 and clean_zenex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_zenex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    deliver_inbox_otp_fast(owner_id, otp, num_str if "num_str" in locals() else num, display_num, app_full_name, iso, prem_app_html)
                except: pass
        except: pass
        time.sleep(5)


def timed_handle_message(msg, queued_at):
    started = time.time()
    try:
        handle_message(msg)
    except Exception as e:
        import traceback
        print(f"[MESSAGE ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        try:
            chat_id = (msg.get("chat") or {}).get("id")
            if chat_id:
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                send_message(chat_id, render_body_text("❌ Something went wrong while processing your request. Please try again."))
        except Exception:
            pass
    finally:
        done = time.time()
        if done - started > 0.5 or started - queued_at > 0.3:
            print(f"[UI TIMING] message wait={started - queued_at:.2f}s run={done - started:.2f}s")

def safe_handle_callback(call, queued_at=None):
    """Run handle_callback; if it crashes, never leave the user on 'Processing...'."""
    _started = time.time()
    try:
        handle_callback(call)
        _done = time.time()
        if _done - _started > 0.5 or (queued_at and _started - queued_at > 0.3):
            print(f"[UI TIMING] button data={str(call.get('data'))[:24]} wait={_started - (queued_at or _started):.2f}s run={_done - _started:.2f}s")
    except Exception as e:
        import traceback
        print(f"[CALLBACK ERROR] data={call.get('data')} -> {e}")
        traceback.print_exc()
        try:
            data = call.get("data", "") or ""
            if data.startswith(("g_c_", "c_n_")):
                chat_id = call["message"]["chat"]["id"]
                msg_id = call["message"]["message_id"]
                try: answer_callback(call["id"], "❌ Something went wrong. Please try again.", show_alert=True)
                except Exception: pass
                kb = [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_services", "style": "danger"}]]
                edit_message(chat_id, msg_id, render_body_text("❌ <b>Could not get a number.</b>\nPlease try again."), reply_markup={"inline_keyboard": kb})
        except Exception:
            pass


def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    
    threading.Thread(target=panel_supervisor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=stex_console_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_console_listener, daemon=True).start()
    threading.Thread(target=zenex_sms_listener, daemon=True).start()
    threading.Thread(target=zenex_console_listener, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    
    # 🌟 PRO-LEVEL FAST SYSTEM: 500 Workers Pool
    executor = ThreadPoolExecutor(max_workers=500)
    
    # Keep-Alive Flask Web Server for Hugging Face Spaces
    keep_alive_app = Flask(__name__)

    @keep_alive_app.route("/")
    def home():
        return "Bot is running 24/7!", 200

    def run_keep_alive():
        keep_alive_app.run(
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 7860)),
            use_reloader=False
        )

    threading.Thread(target=run_keep_alive, daemon=True).start()

    offset = None
    while True:
        try:
            # Do not send the literal string "None" as Telegram's offset.
            polling_method = "getUpdates?timeout=50"
            if offset is not None:
                polling_method += f"&offset={offset}"
            updates = api_call(polling_method)
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(timed_handle_message, update["message"], time.time())
                    elif "callback_query" in update: 
                        executor.submit(safe_handle_callback, update["callback_query"], time.time())
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
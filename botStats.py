from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests, os, re
from functools import wraps
from telegram.error import BadRequest
import time
import httpx
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
API_CACHE = {}

# Usuarios con acceso completo (IDs de Telegram)
#ALLOWED_USERS = {
    #1026764890: datetime.max, # pedirselo a @userinfobot Fran  
    #6810783940: datetime.max, #Mason
    #685157143: datetime.max, 
    #124308017: datetime.max,
    #7078970245: datetime.max,
    #128874195: datetime.max,
    #5873317278: datetime.max,
    #1072931541: datetime.max,
    #7595371685: datetime.max,
    #1734268379: datetime.max,
    #1454860111: datetime.max,
    #1381006468: datetime.max,
    #1019431393: datetime.max,
    #188209198: datetime.max,
#}

#def add_user_subscription(user_id: int, days: int = 30):
    #"""Añade un usuario con acceso durante X días (por defecto 30)."""
    #ALLOWED_USERS[user_id] = datetime.utcnow() + timedelta(days=days)

# 👉 Aquí añades usuarios cuando quieras
#add_user_subscription(123456789, days=30)  # Usuario válido durante 30 días

#def restricted(func):
    #@wraps(func)
    #async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        #user_id = None
        #if update.message:
            #user_id = update.message.from_user.id
        #elif update.callback_query:
            #user_id = update.callback_query.from_user.id

        #now = datetime.utcnow()
        #expiry = ALLOWED_USERS.get(user_id)

        #if not expiry or expiry < now:
            # ❌ No autorizado o caducado
            #if update.message:
                #await update.message.reply_text(
                    #"🚫 Solo usuarios suscritos pueden usar estadísticas.\n💳 Contacta con @MasonBetAdmin para acceder."
                #)
            #elif update.callback_query:
                #await update.callback_query.answer("🚫 Suscripción requerida", show_alert=True)
            #return
        #return await func(update, context, *args, **kwargs)
    #return wrapper



def safe_handler(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except BadRequest as e:
            msg = str(e)
            if "Query is too old" in msg or "Message is not modified" in msg:
                # Ignorar estos errores comunes
                return
            else:
                raise  # otros errores sí los dejamos pasar
        except Exception as e:
            print(f"⚠️ Error in handler {func.__name__}: {e}")
            return
    return wrapper

def api_get(path: str, params: dict, ttl: int = 60):
    key = (path, tuple(sorted(params.items())))
    now = time.time()
    if key in API_CACHE:
        exp, data = API_CACHE[key]
        if now < exp:
            return 200, data
    r = requests.get(f"{BASE}{path}", headers=BASE_HEADERS, params=params, timeout=20)
    try:
        data = r.json()
    except Exception:
        data = {}
    API_CACHE[key] = (now + ttl, data)
    return r.status_code, data

async def api_get_async(path, params):
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE}{path}", headers=BASE_HEADERS, params=params)
        return r.status_code, r.json()


# ----------------- CONFIG -----------------
TOKEN   = os.getenv("BOT_TOKEN",   "8421116318:AAGiLGwQtEDy796uy0qFOQD1X_X6zSGhb_E")
API_KEY = os.getenv("FOOTBALL_KEY","d9aead5de5f11be689ee1ae35e398a60")
SEASON  = 2025  # plan free (2021–2023)
BASE    = "https://v3.football.api-sports.io"
BASE_HEADERS = {"x-apisports-key": API_KEY}

# Acceso rápido (Top-5 + competiciones UEFA)
POPULAR_LEAGUES = {
    "La Liga (ESP)": "140",
    "Premier League (ENG)": "39",
    "Serie A (ITA)": "135",
    "Bundesliga (GER)": "78",
    "Ligue 1 (FRA)": "61",
    "Champions League": "2",
    "Europa League": "3",
    "Conference League": "848",
}

# Ligas permitidas por país (solo 1ª y 2ª división)
ALLOWED_LEAGUES = {
    # --- EUROPE ---
    "Spain": [140, 141],        # La Liga + La Liga2
    "England": [39, 40],        # Premier League + Championship
    "Italy": [135, 136],        # Serie A + Serie B
    "Germany": [78, 79],        # Bundesliga + Bundesliga 2
    "France": [61, 62],         # Ligue 1 + Ligue 2
    "Portugal": [94, 95],       # Primeira Liga + Liga Portugal 2
    "Netherlands": [88, 89],    # Eredivisie + Eerste Divisie
    "Turkey": [203, 204],       # Süper Lig + 1. Lig
    "Greece": [197, 198],       # Super League + Super League 2
    "Denmark": [80, 81],        # Superliga + 1st Division

    # --- AMERICAS ---
    "Brazil": [71, 72],         # Serie A + Serie B
    "Argentina": [128, 129],    # Liga Profesional + Primera Nacional
    "USA": [253, 254],          # MLS + USL Championship
    "Colombia": [239, 240],     # Primera A + Primera B

    # --- MIDDLE EAST ---
    "Saudi Arabia": [152, 153], # Pro League + Division 1

    # --- OTHERS ---
    "China": [169, 170],        # Super League + League One
}


# Regiones → países (puedes ampliar)
REGIONS = {
    "Europe": [
        "Spain","England","Italy","Germany","France","Portugal","Netherlands","Turkey","Greece","Denmark",
    ],
    "Americas": [
        "Brazil","Argentina","USA","Colombia",
    ],
    "Middle East": [
        "Saudi Arabia",
    ],
    "Others": [
        "China",
    ],
}

# Categorías (para navegación)
CATS = [
    "Passes", "Tackles", "Fouls", "Fouls Drawn",
    "Yellowcards", "Redcards", "Shots Total", "Shots On Target",
    "Assists", "Goals", "Saves", "Offsides", "Corners"
]

# ----------------- I18N -----------------
T = {
    "en": {
        "choose_lang": "Select your language / Selecciona tu idioma:",
        "welcome_card": (
            "❓ *What can this bot do?*\n\n"
            "⚽ *MasónBet Stats Bot* stats masonicas, gets football player stats in real time.\n\n"
            "✅ Goals, assists, shots on target, saves\n"
            "✅ Filter by minutes/form/starters\n"
            "✅ Search players & analyze history\n"
            "✅ Fast & accurate\n\n"
            "🔥 Start analyzing football stats today!"
        ),
        "commands": (
            "📌 *Available Commands:*\n"
            "/start - Start the bot\n"
            "/stats - View player stats (Region → Country → League → Team → Category)\n"
            "/player {name} - Search for a player\n"
            "/fixture TeamA vs TeamB - Head-to-head recent results\n"
            "/ranking - Top 10 players by stat (Region → Country → League → Category)\n"
            "/subscribe - Contact admin\n"
            "/help - Show this help"
        ),
        "main_menu_title": "Main menu",
        "btn_stats": "📊 Player stats",
        "btn_help": "❓ Help",
        "btn_back": "⬅️ Back",
        "btn_home": "🏠 Home",
        "btn_subscribe": "💳 Subscribe",

        "select_region": "🌍 Choose a region:",
        "select_country": "🗺️ Choose a country:",
        "select_league": f"🏆 Choose a league (Season {SEASON}/{SEASON+1}):",
        "select_team": "⚽ Choose a team:",
        "choose_category": "📈 Choose a stat category:",
        "no_teams": f"⚠️ No teams for season {SEASON}/{SEASON+1}.",
        "no_players": "⚠️ No player data yet for this team/season.",
        "subscribe_msg": "📩 Contact me at @MasonBetAdmin to subscribe.",
        "player_choose": "👤 Choose a player:",
        "player_summary_title": "📋 Player summary",
        "fx_prompt": "✍️ Please use: /fixture TeamA vs TeamB",
        "fx_search": "🔎 Fetching head-to-head…",
        "fx_no": "❌ No head-to-head data found.",
        "popular_block": "⭐ Quick access (popular leagues):",

        "region_europe": "🇪🇺 Europe",
        "region_americas": "🌎 Americas",
        "region_me": "🕌 Middle East",
        "region_others": "🌐 Others",
        "region_popular": "⭐ Quick access",
        "region_nationals": "🏳️ National Teams",
        "choose_country_national": "🏳️ Choose a country (national team):",
        "no_nat_team": "⚠️ No national team found for this country.",
    },
    "es": {
        "choose_lang": "Selecciona tu idioma / Select your language:",
        "welcome_card": (
            "❓ *¿Qué puede hacer este bot?*\n\n"
            "⚽ *MasónBet Stats Bot* Estadísticas masónicas en tiempo real.\n\n"
            "✅ Goles, asistencias, tiros a puerta, paradas\n"
            "✅ Filtro por minutos/forma/titulares\n"
            "✅ Búsqueda de jugadores e histórico\n"
            "✅ Rápido y preciso\n\n"
            "🔥 ¡Empieza a analizar estadísticas hoy!"
        ),
        "commands": (
            "📌 *Comandos disponibles:*\n"
            "/start - Iniciar el bot\n"
            "/stats - Ver estadísticas (Región → País → Liga → Equipo → Categoría)\n"
            "/fixture TeamA vs TeamB - Enfrentamientos recientes\n"
            "/ranking - Top 10 jugadores por estadisticas (Region → Pais → Liga → Categoria)\n"
            "/subscribe - Contactar con el admin\n"
            "/help - Mostrar esta ayuda"
        ),
        "main_menu_title": "Menú principal",
        "btn_stats": "📊 Estadísticas",
        "btn_help": "❓ Ayuda",
        "btn_back": "⬅️ Atrás",
        "btn_home": "🏠 Inicio",
        "btn_subscribe": "💳 Suscribirse",

        "select_region": "🌍 Elige una región:",
        "select_country": "🗺️ Elige un país:",
        "select_league": f"🏆 Elige una liga (Temporada {SEASON}/{SEASON+1}):",
        "select_team": "⚽ Elige un equipo:",
        "choose_category": "📈 Elige una categoría:",
        "no_teams": f"⚠️ No hay equipos para la temporada {SEASON}/{SEASON+1}.",
        "no_players": "⚠️ Aún no hay datos de jugadores para este equipo/temporada.",
        "subscribe_msg": "📩 Contáctame en @MasonBetAdmin para suscribirte.",
        "player_choose": "👤 Elige un jugador:",
        "player_summary_title": "📋 Resumen del jugador",
        "fx_prompt": "✍️ Usa: /fixture TeamA vs TeamB",
        "fx_search": "🔎 Obteniendo head-to-head…",
        "fx_no": "❌ No hay datos de enfrentamientos.",
        "popular_block": "⭐ Acceso rápido (ligas populares):",

        "region_europe": "🇪🇺 Europa",
        "region_americas": "🌎 Américas",
        "region_me": "🕌 Oriente Medio",
        "region_others": "🌐 Otras",
        "region_popular": "⭐ Acceso rápido",
        "region_nationals": "🏳️ Selecciones",
        "choose_country_national": "🏳️ Elige un país (selección):",
        "no_nat_team": "⚠️ No se encontró la selección de este país.",
    }
}
def tr(ctx, key):
    return T.get(ctx.user_data.get("lang","en"), T["en"]).get(key, key)

# ----------------- Helpers -----------------
def api_get(path: str, params: dict):
    r = requests.get(f"{BASE}{path}", headers=BASE_HEADERS, params=params, timeout=20)
    try: return r.status_code, r.json()
    except Exception: return r.status_code, {}

def B(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=data)

def make_keyboard(items, prefix="", cols=2):
    """items = [(label, value), ...] -> filas con N columnas"""
    rows, row = [], []
    for i, (label, val) in enumerate(items, start=1):
        row.append(B(label, f"{prefix}{val}"))
        if i % cols == 0:
            rows.append(row); row = []
    if row: rows.append(row)
    return rows

# --- categorías con slug seguro para callback_data ---
def slugify(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
CAT_SLUG = {slugify(c): c for c in CATS}

# ----------------- Keyboards -----------------
def kb_language():
    return InlineKeyboardMarkup([[B("🇬🇧 English", "lang_en"), B("🇪🇸 Español", "lang_es")]])

def kb_main(ctx):
    return InlineKeyboardMarkup([
        [B(tr(ctx,"btn_stats"),     "menu_stats")],
        [B(tr(ctx,"btn_help"),      "menu_help")],
        [B(tr(ctx,"btn_subscribe"), "menu_subscribe")],
    ])

def add_nav(ctx, rows):
    rows.append([B(tr(ctx,"btn_home"), "home")])
    return InlineKeyboardMarkup(rows)

def kb_regions(ctx):
    return InlineKeyboardMarkup([
        [B(tr(ctx,"region_europe"),  "region_Europe"), B(tr(ctx,"region_americas"), "region_Americas")],
        [B(tr(ctx,"region_me"),      "region_Middle East"), B(tr(ctx,"region_others"), "region_Others")],
        [B(tr(ctx,"region_popular"), "region_POPULAR"), B(tr(ctx,"region_nationals"), "region_NATIONALS")],
        [B(tr(ctx,"btn_home"), "home")]
    ])

# ----------------- START & MENÚ -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("lang", None)
    if update.message:
        await update.message.reply_text(tr(context,"choose_lang"), reply_markup=kb_language())
    else:
        await update.callback_query.edit_message_text(tr(context,"choose_lang"), reply_markup=kb_language())

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["lang"] = "en" if q.data=="lang_en" else "es"
    await q.edit_message_text(tr(context,"welcome_card"), parse_mode="Markdown")
    await q.message.reply_text(tr(context,"commands"), parse_mode="Markdown")
    await q.message.reply_text(f"🧭 *{tr(context,'main_menu_title')}*", parse_mode="Markdown",
                               reply_markup=kb_main(context))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(tr(context,"commands"), parse_mode="Markdown")

async def menu_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(tr(context,"commands"), parse_mode="Markdown",
                              reply_markup=InlineKeyboardMarkup([[B(tr(context,"btn_home"), "home")]]))

async def menu_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(tr(context,"subscribe_msg"),
                              reply_markup=InlineKeyboardMarkup([[B(tr(context,"btn_home"), "home")]]))

async def go_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(f"🧭 *{tr(context,'main_menu_title')}*", parse_mode="Markdown",
                              reply_markup=kb_main(context))

# ----------------- /stats → Región → País → Liga -----------------
#@restricted
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(tr(context,"select_region"), reply_markup=kb_regions(context))

#@restricted
async def menu_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(tr(context,"select_region"), reply_markup=kb_regions(context))

#@restricted
async def handle_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    region = q.data.replace("region_","")

    # Acceso rápido
    if region == "POPULAR":
        rows = make_keyboard(list(POPULAR_LEAGUES.items()), prefix="league_", cols=2)
        rows.append([B(tr(context,"btn_back"), "menu_stats"), B(tr(context,"btn_home"), "home")])
        await q.edit_message_text(tr(context,"popular_block"), reply_markup=InlineKeyboardMarkup(rows))
        return

    # Selecciones nacionales
    if region == "NATIONALS":
        all_countries = sorted(set(sum(REGIONS.values(), [])))
        rows = make_keyboard([(c, c) for c in all_countries], prefix="ncountry_", cols=2)
        rows.append([B(tr(context,"btn_back"), "menu_stats"), B(tr(context,"btn_home"), "home")])
        await q.edit_message_text(tr(context,"choose_country_national"), reply_markup=InlineKeyboardMarkup(rows))
        return

    # Clubes por regiones
    countries = REGIONS.get(region, [])
    rows = make_keyboard([(c, c) for c in countries], prefix="country_", cols=2)
    rows.append([B(tr(context,"btn_back"), "menu_stats"), B(tr(context,"btn_home"), "home")])
    await q.edit_message_text(tr(context,"select_country"), reply_markup=InlineKeyboardMarkup(rows))

def filter_top_leagues(leagues: list):
    out = []
    for item in leagues:
        lg = item["league"]
        if lg.get("type") != "League":
            continue
        name = lg.get("name","")
        if any(x in name.lower() for x in ["liga", "league", "serie", "bundesliga", "ligue", "division", "premier", "super"]):
            label = f"{name} ({lg.get('country') or item.get('country',{}).get('name','')})"
            out.append((label, lg["id"]))
    # dedupe
    seen=set(); filtered=[]
    for label, lid in out:
        if lid in seen: continue
        seen.add(lid); filtered.append((label,lid))
    return filtered[:30]

def filter_top_leagues(leagues: list):
    """Filtra ligas principales (fallback si el país no está en ALLOWED_LEAGUES)."""
    out = []
    for item in leagues:
        lg = item["league"]
        if lg.get("type") != "League":
            continue
        name = lg.get("name","")
        if any(x in name.lower() for x in [
            "liga", "league", "serie", "bundesliga", "ligue", 
            "division", "premier", "super"
        ]):
            label = f"{name} ({lg.get('country') or item.get('country',{}).get('name','')})"
            out.append((label, lg["id"]))
    # deduplicar
    seen=set(); filtered=[]
    for label, lid in out:
        if lid in seen: continue
        seen.add(lid); filtered.append((label,lid))
    return filtered[:30]

#@restricted
async def handle_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    country = q.data.replace("country_","")

    status, data = api_get("/leagues", {"country": country})
    leagues = data.get("response", []) if status == 200 else []

    # ✅ Filtro: si el país está en ALLOWED_LEAGUES → mostrar solo esas ligas
    if country in ALLOWED_LEAGUES:
        allowed_ids = set(ALLOWED_LEAGUES[country])
        leagues = [l for l in leagues if l["league"]["id"] in allowed_ids]
        options = [(f"{l['league']['name']} ({country})", l["league"]["id"]) for l in leagues]
    else:
        # fallback: mostrar ligas principales detectadas
        options = filter_top_leagues(leagues)

    if not options:
        rows = [[B(tr(context,"btn_back"), "menu_stats"), B(tr(context,"btn_home"), "home")]]
        await q.edit_message_text("⚠️ No leagues found for this country.", reply_markup=InlineKeyboardMarkup(rows))
        return

    rows = make_keyboard(options, prefix="league_", cols=2)
    rows.append([B(tr(context,"btn_back"), "menu_stats"), B(tr(context,"btn_home"), "home")])
    await q.edit_message_text(tr(context,"select_league"), reply_markup=InlineKeyboardMarkup(rows))


# --- Selecciones: país → selección (team) ---
#@restricted
async def handle_country_national(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    country = q.data.replace("ncountry_","")
    status, data = api_get("/teams", {"country": country, "type": "National"})
    items = data.get("response", []) if status==200 else []
    if not items:
        rows = [[B(tr(context,"btn_back"), "menu_stats"), B(tr(context,"btn_home"), "home")]]
        await q.edit_message_text(tr(context,"no_nat_team"), reply_markup=InlineKeyboardMarkup(rows))
        return
    teams = [(t["team"]["name"], t["team"]["id"]) for t in items]
    rows = make_keyboard(teams, prefix="nteam_", cols=2)
    rows.append([B(tr(context,"btn_back"), "menu_stats"), B(tr(context,"btn_home"), "home")])
    await q.edit_message_text(tr(context,"select_team"), reply_markup=InlineKeyboardMarkup(rows))

# ----------------- Liga → Equipo → Categoría -----------------
#@restricted
@safe_handler
async def handle_league(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    league_id = q.data.replace("league_","")
    context.user_data["league_id"] = league_id

    st, d = api_get("/teams", {"league": league_id, "season": SEASON})
    teams = d.get("response", []) if st == 200 else []
    if not teams:
        await q.edit_message_text(
            tr(context,"no_teams"),
            reply_markup=InlineKeyboardMarkup(
                [[B(tr(context,"btn_back"), "menu_stats"),
                  B(tr(context,"btn_home"), "home")]]
            )
        )
        return

    # 🔹 Si venimos de /ranking → elegir categoría en vez de equipo
    if context.user_data.get("mode") == "ranking":
        cat_pairs = [(c, slugify(c)) for c in CATS]
        kb = make_keyboard(cat_pairs, prefix=f"rankcat_{league_id}_", cols=2)
        kb.append([B(tr(context,"btn_back"), f"country_{context.user_data.get('country','')}"),
                   B(tr(context,"btn_home"), "home")])
        await q.edit_message_text("📊 Choose ranking category:", reply_markup=InlineKeyboardMarkup(kb))
        return

    # 🔹 Flujo normal stats → elegir equipo
    team_pairs = [(t["team"]["name"], t["team"]["id"]) for t in teams]
    kb = make_keyboard(team_pairs, prefix="team_", cols=2)
    kb.append([B(tr(context,"btn_back"), "menu_stats"), B(tr(context,"btn_home"), "home")])
    await q.edit_message_text(tr(context,"select_team"), reply_markup=InlineKeyboardMarkup(kb))



@safe_handler
async def handle_fx_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    home_id = q.data.replace("fxhome_","")
    context.user_data["fx_home"] = home_id

    league_id = context.user_data.get("league_id")
    st, d = api_get("/teams", {"league": league_id, "season": SEASON})
    teams = d.get("response", []) if st == 200 else []

    team_pairs = [(t["team"]["name"], t["team"]["id"]) for t in teams]
    kb = make_keyboard(team_pairs, prefix="fxaway_", cols=2)
    kb.append([B("⬅️ Back", f"league_{league_id}")])
    await q.edit_message_text("🚗 Select Away Team:", reply_markup=InlineKeyboardMarkup(kb))

@safe_handler
async def handle_fx_away(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    away_id = q.data.replace("fxaway_","")
    context.user_data["fx_away"] = away_id

    kb = [
        [B("Last 5 matches", "fxrange_5"), B("Last 10 matches", "fxrange_10")],
        [B("⬅️ Back", f"fxhome_{context.user_data['fx_home']}")]
    ]
    await q.edit_message_text("📊 Choose head-to-head range:", reply_markup=InlineKeyboardMarkup(kb))

@safe_handler
async def handle_fx_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    rng = int(q.data.replace("fxrange_", ""))

    home_id = int(context.user_data["fx_home"])
    away_id = int(context.user_data["fx_away"])
    name1, name2 = context.user_data.get("fx_names", ("Home", "Away"))

    # Traemos los últimos N enfrentamientos entre ambos (en cualquier cancha)
    st, d = api_get("/fixtures/headtohead", {"h2h": f"{home_id}-{away_id}", "last": rng})
    fixtures = d.get("response", []) if st == 200 else []
    if not fixtures:
        await q.edit_message_text("⚠️ No head-to-head data found.")
        return

    # Subconjuntos por condición (desde la perspectiva de 'home_id')
    fixtures_A_home = [fx for fx in fixtures if fx["teams"]["home"]["id"] == home_id]
    fixtures_A_away = [fx for fx in fixtures if fx["teams"]["away"]["id"] == home_id]

    def summarize_score(fixts):
        wA=wB=dr=gA=gB=0
        lines=[]
        for fx in fixts:
            ft = (fx["score"].get("fulltime") or {})
            g1 = ft.get("home") or 0
            g2 = ft.get("away") or 0
            # mapea a A/B según IDs reales del fixture
            idH = fx["teams"]["home"]["id"]
            if idH == home_id:
                gA += g1; gB += g2
                if   g1>g2: wA+=1
                elif g2>g1: wB+=1
                else: dr+=1
            else:
                # A es visitante en este fixture
                gA += g2; gB += g1
                if   g2>g1: wA+=1
                elif g1>g2: wB+=1
                else: dr+=1
            lines.append(f"- {fx['teams']['home']['name']} {g1}-{g2} {fx['teams']['away']['name']}")
        return lines, wA, dr, wB, gA, gB

    def avg_stats_for(fixts, team_id):
        bucket = {}
        for fx in fixts:
            fid = fx["fixture"]["id"]
            st_s, d_s = api_get("/fixtures/statistics", {"fixture": fid, "team": team_id})
            if st_s == 200 and d_s.get("response"):
                for kv in d_s["response"][0].get("statistics", []):
                    typ = kv.get("type","")
                    val = safe_int(kv.get("value"))
                    if val is None: 
                        continue
                    bucket.setdefault(typ, []).append(val)
        return {k: round(sum(v)/len(v), 2) for k,v in bucket.items() if v}

    # ---------- BLOQUE 1: cuando A fue LOCAL ----------
    lines = [f"🏟️ *{name1}* vs *{name2}* — last {rng} (A HOME)\n"]
    if fixtures_A_home:
        list_lines, wA, dr, wB, gA, gB = summarize_score(fixtures_A_home)
        lines += list_lines
        lines.append(f"\n🏆 {name1}: {wA} | 🤝 Draws: {dr} | {name2}: {wB}")
        lines.append(f"⚽ Goals — {name1}: {gA} | {name2}: {gB}\n")

        avg_A_home = avg_stats_for(fixtures_A_home, home_id)  # A en casa
        avg_B_away = avg_stats_for(fixtures_A_home, away_id)  # B de visita

        # Muestra un set “rico” de categorías
        cats = [
            "Total Shots","Shots on Goal","Shots on Target","Shots Total",
            "Corners","Offsides","Fouls","Fouls committed","Fouls suffered",
            "Tackles","Yellow Cards","Red Cards","Goalkeeper Saves","Possession"
        ]
        seen=set()
        for cat in cats:
            # empareja claves por contains para cubrir variantes
            a_val = next((v for k,v in avg_A_home.items() if cat.lower() in k.lower()), None)
            b_val = next((v for k,v in avg_B_away.items() if cat.lower() in k.lower()), None)
            if a_val is None and b_val is None: 
                continue
            key = cat.lower()
            if key in seen: 
                continue
            seen.add(key)
            lines.append(f"🏠 {name1} {cat}: *{a_val if a_val is not None else '-'}*")
            lines.append(f"🚗 {name2} {cat}: *{b_val if b_val is not None else '-'}*\n")
    else:
        lines.append("_No mutual matches with A at home in this range._\n")

    # ---------- BLOQUE 2: cuando A fue VISITANTE ----------
    lines.append(f"\n🚗 *{name1}* vs *{name2}* — last {rng} (A AWAY)\n")
    if fixtures_A_away:
        list_lines, wA, dr, wB, gA, gB = summarize_score(fixtures_A_away)
        lines += list_lines
        lines.append(f"\n🏆 {name1}: {wA} | 🤝 Draws: {dr} | {name2}: {wB}")
        lines.append(f"⚽ Goals — {name1}: {gA} | {name2}: {gB}\n")

        avg_A_away = avg_stats_for(fixtures_A_away, home_id)  # A de visita (mismo team_id)
        avg_B_home = avg_stats_for(fixtures_A_away, away_id)  # B en casa

        cats = [
            "Total Shots","Shots on Goal","Shots on Target","Shots Total",
            "Corners","Offsides","Fouls","Fouls committed","Fouls suffered",
            "Tackles","Yellow Cards","Red Cards","Goalkeeper Saves","Possession"
        ]
        seen=set()
        for cat in cats:
            a_val = next((v for k,v in avg_A_away.items() if cat.lower() in k.lower()), None)
            b_val = next((v for k,v in avg_B_home.items() if cat.lower() in k.lower()), None)
            if a_val is None and b_val is None: 
                continue
            key = cat.lower()
            if key in seen: 
                continue
            seen.add(key)
            lines.append(f"🚗 {name1} {cat}: *{a_val if a_val is not None else '-'}*")
            lines.append(f"🏠 {name2} {cat}: *{b_val if b_val is not None else '-'}*\n")
    else:
        lines.append("_No mutual matches with A away in this range._\n")

    await q.edit_message_text("\n".join(lines), parse_mode="Markdown")




#@restricted
async def handle_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data.startswith("nteam_"):
        team_id = q.data.replace("nteam_","")
    else:
        team_id = q.data.replace("team_","")
    context.user_data["team_id"] = team_id
    # usar slugs seguros
    cat_pairs = [(c, slugify(c)) for c in CATS]
    kb = make_keyboard(cat_pairs, prefix="cat_", cols=2)
    back_cb = f"league_{context.user_data.get('league_id','')}" if context.user_data.get("league_id") else "menu_stats"
    kb.append([B(tr(context,"btn_back"), back_cb), B(tr(context,"btn_home"), "home")])
    await q.edit_message_text(tr(context,"choose_category"), reply_markup=InlineKeyboardMarkup(kb))
    kb = make_keyboard(cat_pairs, prefix="cat_", cols=2)
    kb.append([B("🏆 Team Ranking", f"ranking_{context.user_data['league_id']}")])

@safe_handler
#@restricted
async def handle_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    league_id = q.data.replace("ranking_", "")
    context.user_data["league_id"] = league_id
    cat_pairs = [(c, slugify(c)) for c in CATS]
    kb = make_keyboard(cat_pairs, prefix=f"rankcat_{league_id}_", cols=2)
    kb.append([B(tr(context,"btn_back"), f"league_{league_id}"), B(tr(context,"btn_home"), "home")])
    await q.edit_message_text("🏆 Choose ranking category:", reply_markup=InlineKeyboardMarkup(kb))

@safe_handler
#@restricted
async def handle_ranking_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, league_id, cat_slug = q.data.split("_", 2)

    # Guardamos datos
    context.user_data["ranking_league"] = league_id
    context.user_data["ranking_cat"] = cat_slug

    kb = [
        [B("Last 5",  "rankrange_5"),
         B("Last 10", "rankrange_10"),
         B("Last 15", "rankrange_15")],
        [B(tr(context,"btn_back"), f"ranking_{league_id}"),
         B(tr(context,"btn_home"), "home")]
    ]
    await q.edit_message_text("📊 Choose sample size:", reply_markup=InlineKeyboardMarkup(kb))

@safe_handler
async def handle_ranking_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    rng = int(q.data.replace("rankrange_", ""))

    league_id = context.user_data["ranking_league"]
    cat_slug  = context.user_data["ranking_cat"]
    category_label = CAT_SLUG.get(cat_slug, cat_slug)

    # Obtener equipos de la liga
    st, d = api_get("/teams", {"league": league_id, "season": SEASON})
    teams = d.get("response", []) if st == 200 else []

    # 📊 Ranking de jugadores
    players = {}  # {pid: {"name":..., "team":..., "values":[...] }}

    for t in teams:
        tid = t["team"]["id"]
        tname = t["team"]["name"]

        # Últimos N partidos de ese equipo
        st_fx, d_fx = api_get("/fixtures", {"league": league_id, "season": SEASON, "team": tid, "last": rng})
        fixtures = d_fx.get("response", []) if st_fx == 200 else []

        for fx in fixtures:
            fid = fx["fixture"]["id"]
            st_s, d_s = api_get("/fixtures/players", {"fixture": fid, "team": tid})
            if st_s != 200: 
                continue

            for block in d_s.get("response", []):
                for pl in block.get("players", []):
                    pname = pl["player"]["name"]
                    pid   = pl["player"]["id"]
                    stt   = (pl.get("statistics") or [{}])[0]

                    val = map_stat(stt, category_label)
                    if val is None:
                        continue

                    if pid not in players:
                        players[pid] = {"name": pname, "team": tname, "values": []}
                    players[pid]["values"].append(val)

    # Construir ranking: calcular promedio de cada jugador
    ranking = []
    for pid, data in players.items():
        vals = data["values"]
        if not vals:
            continue
        avg = round(sum(vals) / len(vals), 1)
        ranking.append((avg, data["name"], data["team"], vals))

    # Ordenar por promedio descendente
    ranking.sort(reverse=True, key=lambda x: x[0])
    top10 = ranking[:10]

    # Construcción del mensaje
    lines = [f"🏆 *Top 10 Players for {category_label}* (last {rng} matches)\n"]
    for avg, pname, tname, vals in top10:
        seq = ", ".join(str(v) for v in vals)
        lines.append(f"👤 {pname} ({tname})\n({len(vals)}/{rng}) {seq} (Avg {avg})\n")

    kb = [[B(tr(context,"btn_back"), f"rankcat_{league_id}_{cat_slug}"),
           B(tr(context,"btn_home"), "home")]]
    await q.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))



# ----------------- Mapping stats (player totals) -----------------
def map_stat(stats, category_label: str):
    c = category_label.lower()
    try:
        if c == "goals":             return stats["goals"]["total"]
        if c == "assists":           return stats["goals"]["assists"]
        if c == "passes":            return stats["passes"]["total"]
        if c == "shots total":       return stats["shots"]["total"]
        if c == "shots on target" or c == "soa":  return stats["shots"]["on"]
        if c == "yellowcards":       return stats["cards"]["yellow"]
        if c == "redcards":          return stats["cards"]["red"]
        if c == "fouls":             return stats["fouls"]["committed"]
        if c == "fouls drawn":       return stats["fouls"]["drawn"]
        if c == "tackles":           return stats["tackles"]["total"]
        if c == "saves":             return stats["goals"]["saves"]
        if c == "offsides":          return stats.get("offsides","-")
    except Exception:
        return "-"
    return "-"

# ---------- TEAM/PLAYER match-stat matching for /fixtures endpoints ----------
def match_type_matches(stat_type: str, cat_slug: str) -> bool:
    s = stat_type.lower()
    c = cat_slug
    if c in ("shots-on-target","soa"):    return ("on target" in s) or ("on goal" in s)
    if c == "shots-total":                return "total shots" in s or s == "shots"
    if c == "passes":                     return "passes" in s
    if c == "goals":                      return "goals" in s
    if c == "fouls":                      return "fouls committed" in s or s == "fouls"
    if c == "fouls-drawn":                return "fouls suffered" in s or "fouls drawn" in s
    if c == "tackles":                    return "tackles" in s
    if c == "saves":                      return "saves" in s
    if c == "yellowcards":                return "yellow cards" in s
    if c == "redcards":                   return "red cards" in s
    if c == "offsides":                   return "offsides" in s
    if c == "corners":                    return "corner" in s
    
    return False

def safe_int(x):
    try:
        # algunos valores vienen como "12%" o None
        if isinstance(x, str) and x.endswith('%'):
            x = x[:-1]
        return int(x)
    except Exception:
        try:
            return float(x)
        except Exception:
            return None

# ----------------- CATEGORY → elegir modo (Global / Timeline / Team Timeline) -----------------
@safe_handler
#@restricted
async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cat_slug = q.data.replace("cat_","")   # slug seguro
    category_label = CAT_SLUG.get(cat_slug, cat_slug)
    team_id = context.user_data.get("team_id")

    # ⚽ Solo Team Timeline para Throw-ins y Goal Kicks
    if category_label in ("Corners",):
        kb = [
            [B("🏟️ Team Timeline", f"teamtl_{team_id}_{cat_slug}")],
            [B(tr(context,"btn_back"), f"team_{team_id}"), B(tr(context,"btn_home"), "home")]
        ]
    else:
        kb = [
            [B("🌍 Global Totals", f"global_{team_id}_{cat_slug}")],
            [B("📊 Player Timeline", f"timeline_{team_id}_{cat_slug}")],
            [B("🏟️ Team Timeline", f"teamtl_{team_id}_{cat_slug}")]
        ]
        kb.append([B(tr(context,"btn_back"), f"team_{team_id}"), B(tr(context,"btn_home"), "home")])

    await q.edit_message_text(f"📈 {category_label} — Choose mode:",
                              reply_markup=InlineKeyboardMarkup(kb))

# ----------------- GLOBAL (totales por jugador) -----------------

@safe_handler
#@restricted
async def handle_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, team_id, cat_slug = q.data.split("_", 2)
    category_label = CAT_SLUG.get(cat_slug, cat_slug)

    # roster
    page = 1; players = []
    while True:
        status, data = api_get("/players", {"team": team_id, "season": SEASON, "league": context.user_data.get("league_id"), "page": page})
        if status != 200: break
        chunk = data.get("response", [])
        if not chunk: break
        players += chunk
        if page >= int(data.get("paging",{}).get("total",1)): break
        page += 1

    if not players:
        await q.edit_message_text(tr(context,"no_players"),
                                  reply_markup=InlineKeyboardMarkup([[B(tr(context,"btn_home"), "home")]]))
        return

    lines = [f"🌍 *{category_label}* — Season {SEASON}/{SEASON+1}\n"]
    for p in players[:25]:
        name = p["player"]["name"]
        st   = p["statistics"][0]
        val  = map_stat(st, category_label)
        lines.append(f"• {name}: `{val}`")

    kb = [[B(tr(context,"btn_back"), f"cat_{cat_slug}"), B(tr(context,"btn_home"), "home")]]
    await q.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

# ----------------- TIMELINE (jugador por partido) -----------------
@safe_handler
#@restricted
async def handle_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, team_id, cat_slug = q.data.split("_", 2)
    category_label = CAT_SLUG.get(cat_slug, cat_slug)
    kb = [
        [B("Last 5",  f"tlrange_{team_id}_{cat_slug}_5"), B("Last 10", f"tlrange_{team_id}_{cat_slug}_10")],
        [B("Last 15", f"tlrange_{team_id}_{cat_slug}_15")],
        [B(tr(context,"btn_back"), f"cat_{cat_slug}"), B(tr(context,"btn_home"), "home")]
    ]
    await q.edit_message_text(f"📊 {category_label} — Choose range:", reply_markup=InlineKeyboardMarkup(kb))


@safe_handler
#@restricted
async def handle_timeline_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, team_id, cat_slug, rng = q.data.split("_", 3)
    context.user_data["tl_params"] = {"team_id": team_id, "cat_slug": cat_slug, "rng": rng, "homeaway": "all"}

    # Llamamos a la función que dibuja todo de golpe
    await render_timeline_all(q, context)

def filter_fixtures(fixtures, team_id, homeaway):
    """Filtra fixtures por local/visitante"""
    if homeaway == "all":
        return fixtures
    out = []
    for fx in fixtures:
        home_id = fx["teams"]["home"]["id"]
        if homeaway == "home" and home_id == int(team_id):
            out.append(fx)
        elif homeaway == "away" and home_id != int(team_id):
            out.append(fx)
    return out


@safe_handler
async def render_timeline_all(q, context):
    params = context.user_data.get("tl_params", {})
    team_id = params.get("team_id")
    cat_slug = params.get("cat_slug")
    rng = params.get("rng")
    homeaway = params.get("homeaway", "all")
    category_label = CAT_SLUG.get(cat_slug, cat_slug)

    # Fixtures del equipo
    fx_params = {"team": team_id, "season": SEASON, "league": context.user_data.get("league_id")}
    if rng in ("5", "10", "15"):
        fx_params["last"] = int(rng)
    st_fx, d_fx = api_get("/fixtures", fx_params)
    fixtures = d_fx.get("response", []) if st_fx == 200 else []
    if not fixtures:
        await q.edit_message_text("⚠️ No matches found.",
                                  reply_markup=InlineKeyboardMarkup([[B(tr(context,"btn_home"), "home")]]))
        return

    # Filtrar home/away
    fixtures = filter_fixtures(fixtures, team_id, homeaway)
    fixtures = sorted(fixtures, key=lambda x: x["fixture"]["timestamp"] or 0)

    # 📌 Roster REAL sacado de /fixtures/players
    players = {}        # {player_id: {"id":..., "name":...}}
    fixture_stats = {}  # {fixture_id: {player_id: stats}}

    for fx in fixtures:
        fid = fx["fixture"]["id"]
        st_status, st_data = api_get("/fixtures/players", {"fixture": fid, "team": team_id})
        if st_status == 200:
            fixture_stats[fid] = {}
            for block in st_data.get("response", []):
                for pl in block.get("players", []):
                    pid = pl["player"]["id"]
                    pname = pl["player"]["name"]
                    stt = (pl.get("statistics") or [{}])[0]

                    players[pid] = {"id": pid, "name": pname}   # guardamos jugador
                    fixture_stats[fid][pid] = stt               # guardamos stats

    if not players:
        await q.edit_message_text(tr(context,"no_players"),
                                  reply_markup=InlineKeyboardMarkup([[B(tr(context,"btn_home"), "home")]]))
        return

    # Construcción del mensaje
    rng_label = f"last {rng}" if rng in ("5", "10", "15") else "season"
    lines = [
        f"📊 *{category_label}* — Player Timeline ({rng_label})\n"
        f"Filter: *{homeaway.upper()}*"
    ]

    for p in list(players.values())[:25]:  # límite para no saturar
        pid = p["id"]
        name = p["name"]
        values = []

        for fx in fixtures:
            fid = fx["fixture"]["id"]
            stt = fixture_stats.get(fid, {}).get(pid)

            if stt:
                minutes = stt.get("games", {}).get("minutes", 0)
                if minutes and minutes > 0:  
                    v = map_stat(stt, category_label)
                    values.append(v if v is not None else 0)
                else:
                    values.append("-")
            else:
                values.append("-")

        nums = [safe_int(v) for v in values if v != "-" and safe_int(v) is not None]
        avg = round(sum(nums) / len(nums), 2) if nums else 0

        seq = ", ".join(str(v) for v in values)
        lines.append(f"(Avg {avg}) {name}: {seq}")

    # Botones
    kb = [
        [B("🏠 Home", "tlfilter_home"), B("🚗 Away", "tlfilter_away"), B("🌍 All", "tlfilter_all")],
        [B(tr(context,"btn_back"), f"cat_{cat_slug}"), B(tr(context,"btn_home"), "home")]
    ]
    await q.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))



def set_tl_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    context.user_data["tl_params"]["homeaway"] = mode
    return render_timeline_all(update.callback_query, context)

@safe_handler
#@restricted
async def handle_timeline_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, player_id, team_id, cat_slug, rng = q.data.split("_", 4)
    category_label = CAT_SLUG.get(cat_slug, cat_slug)

    # Fixtures del equipo
    params = {"team": team_id, "season": SEASON, "league": context.user_data.get("league_id")}
    if rng in ("5", "10", "15"):
        params["last"] = int(rng)

    st_fx, d_fx = api_get("/fixtures", params)
    fixtures = d_fx.get("response", []) if st_fx == 200 else []
    if not fixtures:
        await q.edit_message_text("⚠️ No matches found.",
                                  reply_markup=InlineKeyboardMarkup([[B(tr(context,"btn_home"), "home")]]))
        return

    # Ordenar por fecha (cronológico)
    fixtures = sorted(fixtures, key=lambda x: x["fixture"]["timestamp"] or 0)

    # 📌 Cargar stats por fixture
    fixture_stats = {}
    for fx in fixtures:
        fid = fx["fixture"]["id"]
        st_status, st_data = api_get(
            "/fixtures/players",
            {"fixture": fid, "team": team_id, "league": context.user_data.get("league_id")}
        )
        if st_status == 200:
            fixture_stats[fid] = {}
            for block in st_data.get("response", []):
                for pl in block.get("players", []):
                    pid = pl["player"]["id"]
                    stt = (pl.get("statistics") or [{}])[0]
                    fixture_stats[fid][pid] = stt

    # Construir la secuencia de valores SOLO para este jugador
    values = []
    for fx in fixtures:
        fid = fx["fixture"]["id"]
        stt = fixture_stats.get(fid, {}).get(int(player_id))

        if stt:
            minutes = stt.get("games", {}).get("minutes", 0)
            if minutes and minutes > 0:
                # Jugó → 0 si no tiene stat
                v = map_stat(stt, category_label)
                values.append(v if v is not None else 0)
            else:
                # Estuvo convocado pero no jugó
                values.append("-")
        else:
            # Ni aparece en el fixture
            values.append("-")

    # Calcular promedio ignorando los "-"
    nums = [safe_int(v) for v in values if v != "-" and safe_int(v) is not None]
    avg = round(sum(nums) / len(nums), 2) if nums else 0

    seq = " ".join(str(v) for v in values)
    text = (
        f"📊 *{category_label}* — Player Timeline "
        f"({'last '+rng if rng in ('5','10','15') else 'season'})\n"
        f"Avg: *{avg}*\n"
        f"`{seq}`"
    )

    kb = [[B(tr(context,"btn_back"), f"tlrange_{team_id}_{cat_slug}_{rng}"),
           B(tr(context,"btn_home"), "home")]]
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))




# ----------------- TEAM TIMELINE (estadística del equipo por partido) -----------------
@safe_handler
#@restricted
async def handle_team_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, team_id, cat_slug = q.data.split("_", 2)
    category_label = CAT_SLUG.get(cat_slug, cat_slug)
    kb = [
        [B("Last 5", f"teamrange_{team_id}_{cat_slug}_5"),
         B("Last 10", f"teamrange_{team_id}_{cat_slug}_10")],
        [B("Last 15", f"teamrange_{team_id}_{cat_slug}_15")],
        [B("All season", f"teamrange_{team_id}_{cat_slug}_all")],
        [B(tr(context,"btn_back"), f"cat_{cat_slug}"), B(tr(context,"btn_home"), "home")]
    ]
    await q.edit_message_text(f"🏟️ {category_label} — Team range:", reply_markup=InlineKeyboardMarkup(kb))


#@restricted
@safe_handler
async def handle_team_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, team_id, cat_slug, rng = q.data.split("_", 3)

    # 🔹 Guardamos los parámetros en user_data
    context.user_data["team_tl_params"] = {
        "team_id": team_id,
        "cat_slug": cat_slug,
        "rng": rng,
        "homeaway": context.user_data.get("team_tl_params", {}).get("homeaway", "all")
    }

    # 1️⃣ Obtener fixtures filtrados por liga+season
    params = {"team": team_id, "season": SEASON, "league": context.user_data.get("league_id")}
    if rng in ("5", "10", "15"):
        params["last"] = int(rng)

    st_fx, d_fx = api_get("/fixtures", params)
    fixtures = d_fx.get("response", []) if st_fx == 200 else []
    if not fixtures:
        await q.edit_message_text("⚠️ No matches found.",
                                  reply_markup=InlineKeyboardMarkup([[B(tr(context,"btn_home"), "home")]]))
        return

    fixtures = sorted(fixtures, key=lambda x: x["fixture"]["timestamp"] or 0)

    # 🔹 Guardamos fixtures en memoria
    context.user_data["team_tl_fixtures"] = fixtures

    # 🔹 Render inicial (usa la nueva función)
    await render_team_timeline(q, context)



@safe_handler
async def render_team_timeline(q, context):
    params = context.user_data.get("team_tl_params", {})
    team_id = params.get("team_id")
    cat_slug = params.get("cat_slug")
    rng = params.get("rng")
    homeaway = params.get("homeaway", "all")
    category_label = CAT_SLUG.get(cat_slug, cat_slug)

    # Usamos los fixtures ya guardados
    fixtures = context.user_data.get("team_tl_fixtures", [])

    # Filtramos según home/away/all
    fixtures = filter_fixtures(fixtures, team_id, homeaway)
    fixtures = sorted(fixtures, key=lambda x: x["fixture"]["timestamp"] or 0)

    # Estadísticas por fixture
    values = []
    for fx in fixtures:
        fid = fx["fixture"]["id"]
        st_status, st_data = api_get("/fixtures/statistics", {"fixture": fid, "team": team_id})
        stats = st_data.get("response", []) if st_status == 200 else []

        val = "-"
        if stats:
            val = 0
            for kv in stats[0].get("statistics", []):
                if match_type_matches(kv.get("type", ""), cat_slug):
                    val = kv.get("value", 0) or 0
                    break
        values.append(val)

    # Promedio
    nums = [safe_int(v) for v in values if isinstance(v, (int, float))]
    avg = round(sum(nums) / len(nums), 2) if nums else 0
    seq = " ".join(str(v) for v in values)

    text = (
        f"🏟️ *{category_label}* — Team Timeline "
        f"({'last '+rng if rng in ('5','10','15') else 'season'})\n"
        f"Filter: *{homeaway.upper()}*\n"
        f"Avg: *{avg}*\n"
        f"`{seq}`"
    )

    kb = [
        [B("🏠 Home", f"teamfilter_home_{team_id}_{cat_slug}_{rng}"),
         B("🚗 Away", f"teamfilter_away_{team_id}_{cat_slug}_{rng}"),
         B("🌍 All", f"teamfilter_all_{team_id}_{cat_slug}_{rng}")],
        [B(tr(context,"btn_back"), f"teamtl_{team_id}_{cat_slug}"),
         B(tr(context,"btn_home"), "home")]
    ]
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))


async def set_team_tl_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    q = update.callback_query
    await q.answer()

    params = context.user_data.get("team_tl_params", {})
    params["homeaway"] = mode
    context.user_data["team_tl_params"] = params

    # Usar los fixtures ya guardados en memoria
    return await render_team_timeline(q, context)


#@restricted
async def handle_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data.startswith("nteam_"):
        team_id = q.data.replace("nteam_","")
    else:
        team_id = q.data.replace("team_","")
    context.user_data["team_id"] = team_id

    # usar slugs seguros
    cat_pairs = [(c, slugify(c)) for c in CATS]
    kb = make_keyboard(cat_pairs, prefix="cat_", cols=2)

    # ✅ botón de ranking general de la liga
    if context.user_data.get("league_id"):
        kb.append([B("🏆 Team Ranking", f"ranking_{context.user_data['league_id']}")])

    back_cb = f"league_{context.user_data.get('league_id','')}" if context.user_data.get("league_id") else "menu_stats"
    kb.append([B(tr(context,"btn_back"), back_cb), B(tr(context,"btn_home"), "home")])

    await q.edit_message_text(tr(context,"choose_category"), reply_markup=InlineKeyboardMarkup(kb))


# ----------------- /subscribe -----------------
async def subscribe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(tr(context, "subscribe_msg"))


# ----------------- /fixture -----------------
def parse_fixture_args(text: str):
    m = re.search(r"/fixture\s+(.+?)\s+(?:vs|-)\s+(.+)$", text, re.IGNORECASE)
    return (m.group(1).strip(), m.group(2).strip()) if m else (None, None)

def find_team_id_by_name(name: str):
    status, data = api_get("/teams", {"search": name})
    if status == 200 and data.get("response"):
        item = data["response"][0]
        return item["team"]["id"], item["team"]["name"]
    return None, None

@safe_handler
async def fixture_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    a, b = parse_fixture_args(text)
    if not a or not b:
        await update.message.reply_text(tr(context,"fx_prompt"))
        return

    id1, name1 = find_team_id_by_name(a)
    id2, name2 = find_team_id_by_name(b)
    if not id1 or not id2:
        await update.message.reply_text(tr(context,"fx_no"))
        return

    # Guarda en memoria para el siguiente paso
    context.user_data["fx_home"]  = id1
    context.user_data["fx_away"]  = id2
    context.user_data["fx_names"] = (name1, name2)

    kb = InlineKeyboardMarkup([[B("Last 5", "fxrange_5"), B("Last 10", "fxrange_10")]])
    await update.message.reply_text(
        f"📊 Choose range for *{name1}* vs *{name2}*",
        parse_mode="Markdown",
        reply_markup=kb
    )

@safe_handler
async def ranking_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Resetear flow para ranking
    context.user_data["mode"] = "ranking"
    await update.message.reply_text(
        "🌍 Choose a region for ranking:",
        reply_markup=kb_regions(context)
    )



# ----------------- main -----------------
def main():
    app = Application.builder().token(TOKEN).build()

    # /start + idioma + menú
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(set_language, pattern=r"^lang_(en|es)$"))
    app.add_handler(CallbackQueryHandler(go_home,     pattern=r"^home$"))

    # Navegación /stats
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CallbackQueryHandler(menu_stats,     pattern=r"^menu_stats$"))
    app.add_handler(CallbackQueryHandler(handle_region,  pattern=r"^region_.+"))
    app.add_handler(CallbackQueryHandler(handle_country, pattern=r"^country_.+"))
    app.add_handler(CallbackQueryHandler(handle_country_national, pattern=r"^ncountry_.+"))
    app.add_handler(CallbackQueryHandler(handle_league,  pattern=r"^league_\d+$"))
    app.add_handler(CallbackQueryHandler(handle_team,    pattern=r"^(team_|nteam_)\d+$"))

    # Categoría → modos
    app.add_handler(CallbackQueryHandler(handle_category, pattern=r"^cat_[a-z0-9\-]+$"))
    app.add_handler(CallbackQueryHandler(handle_global,   pattern=r"^global_\d+_[a-z0-9\-]+$"))
    app.add_handler(CallbackQueryHandler(handle_timeline, pattern=r"^timeline_\d+_[a-z0-9\-]+$"))
    app.add_handler(CallbackQueryHandler(handle_timeline_range, pattern=r"^tlrange_\d+_[a-z0-9\-]+_(5|10|15|all)$"))
    app.add_handler(CallbackQueryHandler(handle_timeline_show,  pattern=r"^tlshow_\d+_\d+_[a-z0-9\-]+_(5|10|15|all)$"))

    # Team timeline
    app.add_handler(CallbackQueryHandler(handle_team_timeline, pattern=r"^teamtl_\d+_[a-z0-9\-]+$"))
    app.add_handler(CallbackQueryHandler(handle_team_range,    pattern=r"^teamrange_\d+_[a-z0-9\-]+_(5|10|15|all)$"))

    # /fixture, /subscribe
    app.add_handler(CommandHandler("subscribe", subscribe_cmd))
    app.add_handler(CallbackQueryHandler(menu_help,      pattern=r"^menu_help$"))
    app.add_handler(CallbackQueryHandler(menu_subscribe, pattern=r"^menu_subscribe$"))
        # Player timeline filtros (home/away/all)
    app.add_handler(CallbackQueryHandler(lambda u,c: set_tl_filter(u,c,"home"), pattern=r"^tlfilter_home$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: set_tl_filter(u,c,"away"), pattern=r"^tlfilter_away$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: set_tl_filter(u,c,"all"),  pattern=r"^tlfilter_all$"))
    app.add_handler(CallbackQueryHandler(handle_ranking, pattern=r"^ranking_\d+$"))
    app.add_handler(CallbackQueryHandler(handle_ranking_category, pattern=r"^rankcat_\d+_[a-z0-9\-]+$"))

    app.add_handler(CallbackQueryHandler(lambda u,c: set_team_tl_filter(u,c,"home"), pattern=r"^teamfilter_home_.*$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: set_team_tl_filter(u,c,"away"), pattern=r"^teamfilter_away_.*$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: set_team_tl_filter(u,c,"all"),  pattern=r"^teamfilter_all_.*$"))

     # Fixture flow
    app.add_handler(CommandHandler("fixture", fixture_cmd))
    app.add_handler(CallbackQueryHandler(handle_fx_home,  pattern=r"^fxhome_\d+$"))
    app.add_handler(CallbackQueryHandler(handle_fx_away,  pattern=r"^fxaway_\d+$"))
    app.add_handler(CallbackQueryHandler(handle_fx_range, pattern=r"^fxrange_(5|10)$"))

    #rankings
    app.add_handler(CommandHandler("ranking", ranking_cmd))
    app.add_handler(CallbackQueryHandler(handle_ranking_range, pattern=r"^rankrange_(5|10|15)$"))

    

    print("✅ Bot en marcha…")
    app.run_polling()

if __name__ == "__main__":
    main()

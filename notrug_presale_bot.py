import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# SETTINGS
BOT_TOKEN = "8846896745:AAG8beZgp073zP4APn7EiZzyKSj7897CgQ8"
ADMIN_ID = 6365046594
GROUP_USERNAME = "@notrugfun"
PRESALE_WALLET = "34mXwN264GLwPkTmVTkBt1PukREwTJ2Ks5wYdqYWScXz"
NOTRUG_PER_SOL = 750000

# DATABASE
def init_db():
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            username TEXT,
            wallet TEXT,
            tx_hash TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_order(telegram_id, username, wallet, tx_hash):
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (telegram_id, username, wallet, tx_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        (telegram_id, username, wallet, tx_hash, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = c.fetchall()
    conn.close()
    return orders

# MESSAGES
def get_presale_info():
    return (
        "🛡 *$NOTRUG — Telegram Exclusive Presale*\n\n"
        "The most honest project in crypto.\n"
        "We will rug you. Just... not yet. 🏖\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 *YOU ARE EARLY. THIS IS EXCLUSIVE.*\n\n"
        "We are launching a public presale soon on smithii.io\n"
        "but Telegram members get a private deal first:\n\n"
        "✅ *Telegram Price: 1 SOL = 750,000 NOTRUG*\n"
        "⚠️ Public Presale on smithii.io: 1 SOL = 500,000 NOTRUG\n\n"
        "*You get 50% MORE tokens by buying now!*\n"
        "*Smart money moves early.* 🧠\n\n"
        "This offer is ONLY for Telegram members. 🤫"
    )

def get_step1_msg():
    return (
        "📋 *Step 1 of 3*\n\n"
        "Send SOL to our presale wallet:\n\n"
        "`" + PRESALE_WALLET + "`\n\n"
        "⚠️ *Solana network only!*\n\n"
        "Once sent, type anything here to continue ✅"
    )

def get_step2_msg():
    return (
        "📋 *Step 2 of 3*\n\n"
        "Please send your *TX hash* here:\n"
        "(Copy it from your Phantom transaction history)"
    )

def get_step3_msg():
    return (
        "✅ *TX hash received!*\n\n"
        "📋 *Step 3 of 3*\n\n"
        "Now send your *Phantom wallet address*\n"
        "We will send NOTRUG directly to this address 👇\n\n"
        "💡 Don't have Phantom? Download at phantom.app — free!"
    )

def get_why_notrug():
    return (
        "🔥 *WHY $NOTRUG?*\n\n"
        "The ONLY project in crypto that tells you\n"
        "exactly when we rug. Day 365. Not before. 🏖\n\n"
        "✅ 650M tokens locked on Streamflow\n"
        "✅ Monthly burns — supply drops every month\n"
        "✅ Full on-chain transparency\n"
        "✅ Earn free tokens: @NOTRUGairdrop_bot\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Send any amount of SOL you wish!\n\n"
        "Others rug without warning.\n"
        "We rug with a countdown. ⏳\n\n"
        "🌐 notrug.fun"
    )

# HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["step"] = 0
    await handle_message(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    chat_type = update.message.chat.type
    text = update.message.text.strip()

    # GROUP: Yönlendir
    if chat_type in ["group", "supergroup"]:
        keywords = ["join presale", "presale", "how to buy", "where to buy", "satın al", "nasıl", "buy notrug"]
        if any(kw in text.lower() for kw in keywords):
            username = user.username or user.first_name
            msg = (
                "👋 @" + username + "\n\n"
                "DM our presale bot for exclusive access:\n"
                "👉 @NOTRUGpresale_bot\n\n"
                "*1 SOL = 750,000 NOTRUG* 🔥\n"
                "Better than public presale price!"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # DM: Step sistemi
    step = context.user_data.get("step", 0)

    # Step 0: Presale bilgisi ver
    if step == 0:
        await update.message.reply_text(get_presale_info(), parse_mode="Markdown")
        await update.message.reply_text(get_step1_msg(), parse_mode="Markdown")
        await update.message.reply_text(get_why_notrug(), parse_mode="Markdown")
        context.user_data["step"] = 1
        return

    # Step 1: SOL gönderildi, TX hash iste
    if step == 1:
        await update.message.reply_text(get_step2_msg(), parse_mode="Markdown")
        context.user_data["step"] = 2
        return

    # Step 2: TX hash al, wallet iste
    if step == 2:
        context.user_data["tx_hash"] = text
        await update.message.reply_text(get_step3_msg(), parse_mode="Markdown")
        context.user_data["step"] = 3
        return

    # Step 3: Wallet al, sipariş tamamla
    if step == 3:
        wallet = text
        tx_hash = context.user_data.get("tx_hash", "Unknown")
        username = user.username or user.first_name

        save_order(user.id, username, wallet, tx_hash)
        context.user_data["step"] = 0

        # Kullanıcıya onay
        confirm = (
            "🎉 *Order Complete!*\n\n"
            "TX: `" + tx_hash[:40] + "...`\n"
            "Your wallet: `" + wallet[:20] + "...`\n\n"
            "✅ We will send your NOTRUG shortly!\n"
            "Usually within 1-2 hours 🛡\n\n"
            "Questions? Join us: t.me/notrugfun"
        )
        await update.message.reply_text(confirm, parse_mode="Markdown")

        # Admina bildirim
        notif = (
            "🔔 *NEW PRESALE ORDER!*\n\n"
            "👤 User: @" + username + "\n"
            "🆔 ID: " + str(user.id) + "\n"
            "🔗 TX Hash: `" + tx_hash + "`\n"
            "💼 Send NOTRUG to: `" + wallet + "`\n\n"
            "📊 Check TX on solscan.io\n"
            "SOL amount x " + str(NOTRUG_PER_SOL) + " = NOTRUG to send\n\n"
            "⚡ Send NOTRUG manually!"
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=notif,
            parse_mode="Markdown"
        )
        return

async def orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    orders = get_all_orders()
    if not orders:
        await update.message.reply_text("No orders yet!")
        return
    text = "*ALL ORDERS*\n\n"
    for o in orders[:10]:
        text += "#{} @{} | TX: {}... | Wallet: {}...\n".format(
            o[0], o[2], str(o[4])[:20], str(o[3])[:15]
        )
    await update.message.reply_text(text, parse_mode="Markdown")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    orders = get_all_orders()
    text = (
        "*$NOTRUG PRESALE STATS*\n\n"
        "Total orders: *" + str(len(orders)) + "*\n"
        "Presale price: *1 SOL = " + str(NOTRUG_PER_SOL) + " NOTRUG*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# MAIN
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", orders_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("$NOTRUG Presale Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()

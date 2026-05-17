import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8846896745:AAG8beZgp073zP4APn7EiZzyKSj7897CgQ8"
ADMIN_ID = 6365046594
PRESALE_WALLET = "34mXwN264GLwPkTmVTkBt1PukREwTJ2Ks5wYdqYWScXz"
NOTRUG_PER_SOL = 750000

def init_db():
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            step INTEGER DEFAULT 0,
            tx_hash TEXT,
            updated_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            username TEXT,
            wallet TEXT,
            tx_hash TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_user_step(telegram_id):
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("SELECT step, tx_hash FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return 0, None

def set_user_step(telegram_id, step, tx_hash=None):
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (telegram_id, step, tx_hash, updated_at) VALUES (?, ?, ?, ?)",
              (telegram_id, step, tx_hash, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_order(telegram_id, username, wallet, tx_hash):
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("INSERT INTO orders (telegram_id, username, wallet, tx_hash, created_at) VALUES (?, ?, ?, ?, ?)",
              (telegram_id, username, wallet, tx_hash, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = c.fetchall()
    conn.close()
    return orders

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    set_user_step(telegram_id, 0)
    await handle_message(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    chat_type = update.message.chat.type
    text = update.message.text.strip()
    telegram_id = user.id
    username = user.username or user.first_name

    # GROUP
    if chat_type in ["group", "supergroup"]:
        keywords = ["join presale", "presale", "how to buy", "where to buy", "buy notrug", "satın al", "nasıl"]
        if any(kw in text.lower() for kw in keywords):
            msg = (
                "👋 @" + (user.username or user.first_name) + "\n\n"
                "DM our presale bot for exclusive access:\n"
                "👉 @NOTRUGpresale_bot\n\n"
                "*1 SOL = 750,000 NOTRUG* 🔥\n"
                "Better than public presale price!"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # DM
    step, saved_tx = get_user_step(telegram_id)

    if step == 0:
        # Presale bilgisi
        msg1 = (
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
            "This offer is ONLY for Telegram members. 🤫\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 *WHY $NOTRUG?*\n\n"
            "The ONLY project that tells you exactly when we rug.\n"
            "Day 365. Not before. 🏖\n\n"
            "✅ 650M tokens locked on Streamflow\n"
            "✅ Monthly burns — supply drops every month\n"
            "✅ Earn free tokens: @NOTRUGairdrop_bot\n\n"
            "Others rug without warning.\n"
            "We rug with a countdown. ⏳\n\n"
            "🌐 notrug.fun"
        )
        await update.message.reply_text(msg1, parse_mode="Markdown")

        # Step 1 mesajı
        msg2 = (
            "📋 *Step 1 of 3*\n\n"
            "Send SOL to our presale wallet:\n\n"
            "`" + PRESALE_WALLET + "`\n\n"
            "⚠️ *Solana network only!*\n\n"
            "Once sent, type anything here to continue ✅"
        )
        await update.message.reply_text(msg2, parse_mode="Markdown")
        set_user_step(telegram_id, 1)
        return

    if step == 1:
        msg = (
            "📋 *Step 2 of 3*\n\n"
            "Please send your *TX hash* here:\n"
            "(Copy it from your Phantom transaction history)"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        set_user_step(telegram_id, 2)
        return

    if step == 2:
        tx_hash = text
        set_user_step(telegram_id, 3, tx_hash)
        msg = (
            "✅ *TX hash received!*\n\n"
            "📋 *Step 3 of 3*\n\n"
            "Now send your *Phantom wallet address*\n"
            "We will send NOTRUG directly to this address 👇\n\n"
            "💡 Don't have Phantom? Download at phantom.app"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    if step == 3:
        wallet = text
        tx_hash = saved_tx or "Unknown"

        save_order(telegram_id, username, wallet, tx_hash)
        set_user_step(telegram_id, 0)

        confirm = (
            "🎉 *Order Complete!*\n\n"
            "TX: `" + str(tx_hash)[:40] + "...`\n"
            "Your wallet: `" + wallet[:20] + "...`\n\n"
            "✅ We will send your NOTRUG shortly!\n"
            "Usually within 1-2 hours 🛡\n\n"
            "Questions? Join us: t.me/notrugfun"
        )
        await update.message.reply_text(confirm, parse_mode="Markdown")

        notif = (
            "🔔 *NEW PRESALE ORDER!*\n\n"
            "👤 User: @" + username + "\n"
            "🆔 ID: " + str(telegram_id) + "\n"
            "🔗 TX Hash: `" + str(tx_hash) + "`\n"
            "💼 Send NOTRUG to: `" + wallet + "`\n\n"
            "📊 Check TX on solscan.io\n"
            "SOL amount x " + str(NOTRUG_PER_SOL) + " = NOTRUG\n\n"
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
        text += "#{} @{} | {}\n".format(o[0], o[2], str(o[3])[:15])
    await update.message.reply_text(text, parse_mode="Markdown")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    orders = get_all_orders()
    text = (
        "*PRESALE STATS*\n\n"
        "Total orders: *" + str(len(orders)) + "*\n"
        "Price: *1 SOL = " + str(NOTRUG_PER_SOL) + " NOTRUG*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

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

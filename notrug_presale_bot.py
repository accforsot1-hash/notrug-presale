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
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        step INTEGER DEFAULT 0,
        tx_hash TEXT,
        updated_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        username TEXT,
        wallet TEXT,
        tx_hash TEXT,
        created_at TEXT
    )""")
    conn.commit()
    conn.close()

def get_step(tid):
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("SELECT step, tx_hash FROM users WHERE telegram_id=?", (tid,))
    row = c.fetchone()
    conn.close()
    return (row[0], row[1]) if row else (0, None)

def set_step(tid, step, tx=None):
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (telegram_id,step,tx_hash,updated_at) VALUES (?,?,?,?)",
              (tid, step, tx, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_order(tid, username, wallet, tx):
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("INSERT INTO orders (telegram_id,username,wallet,tx_hash,created_at) VALUES (?,?,?,?,?)",
              (tid, username, wallet, tx, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_orders():
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY created_at DESC")
    r = c.fetchall()
    conn.close()
    return r

MSG_INFO = (
    "NOTRUG - Telegram Exclusive Presale\n\n"
    "The most honest project in crypto.\n"
    "We will rug you. Just... not yet.\n\n"
    "YOU ARE EARLY. THIS IS EXCLUSIVE.\n\n"
    "We are launching a public presale soon on smithii.io\n"
    "but Telegram members get a private deal first:\n\n"
    "Telegram Price: 1 SOL = 750,000 NOTRUG\n"
    "Public Presale on smithii.io: 1 SOL = 500,000 NOTRUG\n\n"
    "You get 50% MORE tokens by buying now!\n"
    "Smart money moves early.\n\n"
    "This offer is ONLY for Telegram members.\n\n"
    "WHY NOTRUG?\n\n"
    "The ONLY project that tells you exactly when we rug.\n"
    "Day 365. Not before.\n\n"
    "650M tokens locked on Streamflow\n"
    "Monthly burns - supply drops every month\n"
    "Earn free tokens: @NOTRUGairdrop_bot\n\n"
    "Others rug without warning.\n"
    "We rug with a countdown.\n\n"
    "notrug.fun"
)

MSG_STEP1 = (
    "Step 1 of 3\n\n"
    "Send SOL to our presale wallet:\n\n"
    + PRESALE_WALLET + "\n\n"
    "Solana network only!\n\n"
    "Once sent, type anything here to continue"
)

MSG_STEP2 = (
    "Step 2 of 3\n\n"
    "Please send your TX hash here:\n"
    "(Copy it from your Phantom transaction history)"
)

MSG_STEP3 = (
    "TX hash received!\n\n"
    "Step 3 of 3\n\n"
    "Now send your Phantom wallet address\n"
    "We will send NOTRUG directly to this address\n\n"
    "Don't have Phantom? Download at phantom.app - it's free!"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tid = update.effective_user.id
    set_step(tid, 0)
    await handle_message(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    tid = user.id
    username = user.username or user.first_name
    text = update.message.text.strip()
    chat_type = update.message.chat.type

    if chat_type in ["group", "supergroup"]:
        keywords = ["join presale", "presale", "how to buy", "buy notrug", "where to buy"]
        if any(k in text.lower() for k in keywords):
            msg = (
                "Hey @" + (user.username or user.first_name) + "!\n\n"
                "DM our presale bot for exclusive access:\n"
                "@NOTRUGpresale_bot\n\n"
                "1 SOL = 750,000 NOTRUG\n"
                "Better than public presale price!"
            )
            await update.message.reply_text(msg)
        return

    step, saved_tx = get_step(tid)

    if step == 0:
        await update.message.reply_text(MSG_INFO)
        await update.message.reply_text(MSG_STEP1)
        set_step(tid, 1)
        return

    if step == 1:
        await update.message.reply_text(MSG_STEP2)
        set_step(tid, 2)
        return

    if step == 2:
        set_step(tid, 3, text)
        await update.message.reply_text(MSG_STEP3)
        return

    if step == 3:
        wallet = text
        tx = saved_tx or "Unknown"
        save_order(tid, username, wallet, tx)
        set_step(tid, 0)

        await update.message.reply_text(
            "Order Complete!\n\n"
            "TX: " + str(tx)[:50] + "\n"
            "Your wallet: " + wallet[:30] + "\n\n"
            "We will send your NOTRUG shortly!\n"
            "Usually within 1-2 hours\n\n"
            "Questions? t.me/notrugfun"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "NEW PRESALE ORDER!\n\n"
                "User: @" + username + "\n"
                "ID: " + str(tid) + "\n"
                "TX Hash: " + str(tx) + "\n"
                "Send NOTRUG to: " + wallet + "\n\n"
                "Check TX on solscan.io\n"
                "SOL amount x " + str(NOTRUG_PER_SOL) + " = NOTRUG to send\n\n"
                "Send NOTRUG manually!"
            )
        )

async def orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    orders = get_orders()
    if not orders:
        await update.message.reply_text("No orders yet!")
        return
    text = "ALL ORDERS\n\n"
    for o in orders[:10]:
        text += "#{} @{} | {}\n".format(o[0], o[2], str(o[4])[:20])
    await update.message.reply_text(text)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    orders = get_orders()
    await update.message.reply_text(
        "PRESALE STATS\n\n"
        "Total orders: " + str(len(orders)) + "\n"
        "Price: 1 SOL = " + str(NOTRUG_PER_SOL) + " NOTRUG"
    )

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", orders_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("NOTRUG Presale Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()

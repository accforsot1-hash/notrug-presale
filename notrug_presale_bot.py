import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ==================== SETTINGS ====================
BOT_TOKEN = "8846896745:AAG8beZgp073zP4APn7EiZzyKSj7897CgQ8"
ADMIN_ID = 6365046594
GROUP_ID = "@notrugfun"
PRESALE_WALLET = "34mXwN264GLwPkTmVTkBt1PukREwTJ2Ks5wYdqYWScXz"
NOTRUG_PER_SOL = 750000
CONTRACT_ADDRESS = "EN3ceLyhXL6QoCia2hjf8r8F6sKY2oat7wUpHGJPJKF4"

# ==================== DATABASE ====================
def init_db():
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            username TEXT,
            wallet TEXT,
            sol_amount REAL,
            notrug_amount REAL,
            tx_hash TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_order(telegram_id, username, wallet, sol_amount, notrug_amount, tx_hash):
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (telegram_id, username, wallet, sol_amount, notrug_amount, tx_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (telegram_id, username, wallet, sol_amount, notrug_amount, tx_hash, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_orders():
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = c.fetchall()
    conn.close()
    return orders

def get_total_raised():
    conn = sqlite3.connect("presale.db")
    c = conn.cursor()
    c.execute("SELECT SUM(sol_amount) FROM orders WHERE status = 'completed'")
    result = c.fetchone()[0]
    conn.close()
    return result or 0

# ==================== PRESALE MESSAGE ====================
PRESALE_MSG = f"""
🛡️ *$NOTRUG — Telegram Exclusive Presale*

The most honest project in crypto.
We will rug you. Just... not yet. 🏖️

━━━━━━━━━━━━━━━━━━━━
🔥 *YOU ARE EARLY. THIS IS EXCLUSIVE.*

We are launching a public presale soon on smithii.io
but Telegram members get a private deal first:

✅ *Telegram Price: 1 SOL = {NOTRUG_PER_SOL:,} NOTRUG*
⚠️ Public Presale on smithii.io: 1 SOL = 500,000 NOTRUG

*You get 50% MORE tokens by buying now!*
*Smart money moves early.* 🧠

This offer is ONLY for Telegram members. 🤫

━━━━━━━━━━━━━━━━━━━━
📋 *HOW TO BUY — 3 STEPS*

1️⃣ Send SOL to our presale wallet:
`{PRESALE_WALLET}`
⚠️ *Send on Solana network only!*

2️⃣ Send your TX hash here

3️⃣ Send your *Phantom Wallet address* (Solana network)
💡 Don't have Phantom? Download at phantom.app — free!

✅ NOTRUG sent directly to your Phantom wallet within 1-2 hours!

━━━━━━━━━━━━━━━━━━━━
🔥 *WHY $NOTRUG?*

The ONLY project in crypto that tells you
exactly when we rug. Day 365. Not before. 🏖️

✅ 650M tokens locked on Streamflow
✅ Monthly burns 🔥 — supply drops every month
✅ Full on-chain transparency
✅ Earn free tokens: @NOTRUGairdrop\_bot

━━━━━━━━━━━━━━━━━━━━
⚠️ Send any amount of SOL you wish!

"Others rug without warning.
We rug with a countdown." ⏳

🌐 notrug.fun
"""

# ==================== COMMANDS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step'] = 0
    await handle_message(update, context)

async def presale_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mesaj 1: Tanıtım
    msg1 = (
        "🛡️ *$NOTRUG — Telegram Exclusive Presale*\n\n"
        "The most honest project in crypto.\n"
        "We will rug you. Just\.\.\. not yet\. 🏖️\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 *YOU ARE EARLY\. THIS IS EXCLUSIVE\.*\n\n"
        "We are launching a public presale soon on smithii\.io\n"
        "but Telegram members get a private deal first:\n\n"
        "✅ *Telegram Price: 1 SOL = 750,000 NOTRUG*\n"
        "⚠️ Public Presale on smithii\.io: 1 SOL = 500,000 NOTRUG\n\n"
        "*You get 50% MORE tokens by buying now\!*\n"
        "*Smart money moves early\.* 🧠\n\n"
        "This offer is ONLY for Telegram members\. 🤫"
    )
    await update.message.reply_text(msg1, parse_mode="MarkdownV2")

    # Mesaj 2: Presale cüzdan adresi - kopyalanabilir
    msg2 = (
        "📋 *STEP 1 — Send SOL here:*\n\n"
        "`34mXwN264GLwPkTmVTkBt1PukREwTJ2Ks5wYdqYWScXz`\n\n"
        "⚠️ *Solana network only\!*\n"
        "Tap the address above to copy it\!"
    )
    await update.message.reply_text(msg2, parse_mode="MarkdownV2")

    # Mesaj 3: Adımlar
    msg3 = (
        "📋 *STEP 2 & 3*\n\n"
        "After sending SOL:\n\n"
        "2️⃣ Send your *TX hash* here\n\n"
        "3️⃣ Send your *Phantom Wallet address*\n"
        "💡 Don't have Phantom? phantom\.app — free\!\n\n"
        "✅ NOTRUG sent to your wallet within 1\-2 hours\!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 *WHY $NOTRUG?*\n\n"
        "The ONLY project that tells you exactly when we rug\.\n"
        "Day 365\. Not before\. 🏖️\n\n"
        "✅ 650M tokens locked on Streamflow\n"
        "✅ Monthly burns 🔥\n"
        "✅ Earn free tokens: @NOTRUGairdrop\_bot\n\n"
        "\"Others rug without warning\.\n"
        "We rug with a countdown\.\" ⏳\n\n"
        "🌐 notrug\.fun"
    )
    await update.message.reply_text(msg3, parse_mode="MarkdownV2")

async def orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    orders = get_orders()
    total = get_total_raised()

    if not orders:
        await update.message.reply_text("No orders yet!")
        return

    text = f"📋 *ALL ORDERS*\nTotal raised: *{total:.2f} SOL*\n\n"
    for o in orders[:10]:
        text += f"#{o[0]} @{o[2]} | {o[4]} SOL → {o[5]:,.0f} NOTRUG | {o[8]}\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    orders = get_orders()
    total_sol = sum(o[4] for o in orders)
    total_notrug = sum(o[5] for o in orders)

    text = (
        "*$NOTRUG PRESALE STATS*\n\n"
        f"Total orders: *{len(orders)}*\n"
        f"Total SOL raised: *{total_sol:.2f} SOL*\n"
        f"Total NOTRUG sold: *{total_notrug:,.0f}*\n\n"
        f"Presale price: *1 SOL = {NOTRUG_PER_SOL:,} NOTRUG*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    user = update.effective_user
    chat_type = update.message.chat.type

    # Group message handler - "join presale" tetikleyici
    if chat_type in ["group", "supergroup"]:
        if any(phrase in text for phrase in ["join presale", "presale", "how to buy", "where to buy", "satın al", "nasıl alırım"]):
            # Gruba kısa mesaj at
            await update.message.reply_text(
                f"👋 @{user.username or user.first_name}!\n\n"
                f"DM our presale bot for exclusive access:\n"
                f"👉 @NOTRUGpresale\\_bot\n\n"
                f"*1 SOL = {NOTRUG_PER_SOL:,} NOTRUG* 🔥",
                parse_mode="Markdown"
            )
        return

    # DM handler
    if chat_type == "private":
        step = context.user_data.get('step', 0)

        # Step 0: Herhangi bir mesaj → Presale başlat
        if step == 0:
            await presale_cmd(update, context)
            context.user_data['step'] = 1
            await update.message.reply_text(
                "📋 *Step 1 of 3*\n\n"
                "Send SOL to our presale wallet:\n\n"
                "`34mXwN264GLwPkTmVTkBt1PukREwTJ2Ks5wYdqYWScXz`\n\n"
                "⚠️ *Solana network only!*\n\n"
                "Once sent, type anything here to continue ✅",
                parse_mode="Markdown"
            )
            return

        # Step 1: SOL gönderildi, TX hash iste
        if step == 1:
            context.user_data['step'] = 2
            await update.message.reply_text(
                "📋 *Step 2 of 3*\n\n"
                "Now send your *TX hash* here:\n"
                "_\(Copy it from your Phantom transaction history\)_",
                parse_mode="Markdown"
            )
            return

        # Step 2: TX hash alındı, wallet iste
        if step == 2:
            context.user_data['tx_hash'] = text.strip()
            context.user_data['step'] = 3
            await update.message.reply_text(
                "✅ *TX hash received!*\n\n"
                "📋 *Step 3 of 3*\n\n"
                "Now send your *Phantom wallet address*\n"
                "_We will send your NOTRUG to this address_ 👇",
                parse_mode="Markdown"
            )
            return

        # Step 3: Wallet alındı, sipariş tamamlandı
        if step == 3:
            wallet = text.strip()
            tx_hash = context.user_data.get('tx_hash', 'Unknown')

            save_order(
                user.id,
                user.username or user.first_name,
                wallet,
                0,
                0,
                tx_hash
            )

            context.user_data['step'] = 0

            await update.message.reply_text(
                f"🎉 *Order Complete!*

"
                f"TX: `{tx_hash[:30]}...`
"
                f"Your wallet: `{wallet[:20]}...`

"
                f"✅ We will send your NOTRUG to your wallet!
"
                f"_Usually within 1-2 hours_ 🛡️

"
                f"Questions? Join us: t.me/notrugfun",
                parse_mode="Markdown"
            )

            admin_msg = (
                f"🔔 *NEW PRESALE ORDER!*

"
                f"👤 User: @{user.username or user.first_name}
"
                f"🆔 ID: `{user.id}`
"
                f"🔗 TX Hash: `{tx_hash}`
"
                f"💼 Send NOTRUG to: `{wallet}`

"
                f"📊 Check TX on solscan.io
"
                f"SOL amount × {NOTRUG_PER_SOL:,} = NOTRUG to send

"
                f"⚡ Send NOTRUG manually!"
            )
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_msg,
                parse_mode="Markdown"
            )
            return

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "presale":
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=PRESALE_MSG,
            parse_mode="Markdown"
        )

# ==================== MAIN ====================
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("presale", presale_cmd))
    app.add_handler(CommandHandler("orders", orders_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("$NOTRUG Presale Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()

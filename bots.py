import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== 🔧 APNI DETAILS ==========
BOT_TOKEN = '8752816178:AAEtDQ0ZM044A2QkARO62_kZsjfNE8jFo-g'
ADMIN_ID = 7984167671
OWNER_USERNAME = '@OmegaRaptor'

# 🔗 7 FORCE JOIN LINKS
FORCE_JOIN_LINKS = [
    'https://t.me/+DM0r_Yk8VyhkODVl',
    'https://t.me/+KviYlzQmOQw0ZGY0',
    'https://t.me/+yMOLCXfPm345ZmZl',
    'https://t.me/+dRPH3_VPPnBjODM1',
    'https://t.me/+JuHVDqmr7HEwNDI1',
    'https://t.me/PrimeXstoree',
    'https://t.me/ZyroxEra',
]

# ========== BUTTON TEXTS ==========
CHANNEL_BUTTONS = [
    "🔥 Developer 🤖",
    "✨ Join Must",
    "Main Channel ⚡",
    "Join Must 💎",
    "RBH Backup 🦖",
    "Must Join 🦖",
    "Join Must 🦖",
]

VERIFY_BTN = "✅ I've Joined All ✅"
SHARE_BTN = "🔗 Share Link 🔗"
STATS_BTN = "📊 My Stats 📊"
BOTSTATS_BTN = "🤖 Bot Stats 🤖"
WITHDRAW_BTN = "🎁 Withdraw 🎁"
HELP_BTN = "❓ Help ❓"
BACK_BTN = "🔙 Back 🔙"

# ========== FILES ==========
REFERRALS_FILE = 'referrals.json'
REQUESTS_FILE = 'requests.json'
USER_JOINS_FILE = 'joins.json'
STATS_FILE = 'stats.json'

LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def fancy(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ',
        'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ',
        'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ'
    }
    words = text.lower().split()
    fancy_words = []
    for word in words:
        if word:
            first = word[0].upper()
            rest = ''.join(small_caps.get(c, c) for c in word[1:])
            fancy_words.append(first + rest)
    return ' '.join(fancy_words)

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {'users': 0, 'bots': 0, 'referrals': 0, 'active': 0, 'date': ''}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)

def update_stats(user_id):
    stats = load_stats()
    today = datetime.now().strftime('%Y-%m-%d')
    users = load_data(REFERRALS_FILE)
    stats['users'] = len(users)
    if stats['date'] != today:
        stats['active'] = 0
        stats['date'] = today
    stats['active'] += 1
    save_stats(stats)

def update_bot_count():
    stats = load_stats()
    stats['bots'] += 1
    save_stats(stats)

def update_referral_count():
    stats = load_stats()
    stats['referrals'] += 1
    save_stats(stats)

def get_force_keyboard():
    keyboard = []
    for i, link in enumerate(FORCE_JOIN_LINKS):
        btn_text = CHANNEL_BUTTONS[i] if i < len(CHANNEL_BUTTONS) else f"Join Channel {i+1}"
        keyboard.append([InlineKeyboardButton(fancy(btn_text), url=link)])
    keyboard.append([InlineKeyboardButton(fancy(VERIFY_BTN), callback_data='verify')])
    return InlineKeyboardMarkup(keyboard)

def get_menu_keyboard(ref_link, can_withdraw):
    keyboard = [
        [InlineKeyboardButton(fancy(SHARE_BTN), url=ref_link)],
        [InlineKeyboardButton(fancy(STATS_BTN), callback_data='stats')],
        [InlineKeyboardButton(fancy(BOTSTATS_BTN), callback_data='botstats')],
    ]
    if can_withdraw:
        keyboard.append([InlineKeyboardButton(fancy(WITHDRAW_BTN), callback_data='withdraw')])
    keyboard.append([InlineKeyboardButton(fancy(HELP_BTN), callback_data='help')])
    return InlineKeyboardMarkup(keyboard)

def get_back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton(fancy(BACK_BTN), callback_data='menu')]])

async def check_force_joined(user_id, context):
    data = load_data(USER_JOINS_FILE)
    if str(user_id) in data and data[str(user_id)].get('verified'):
        return True
    
    all_joined = True
    for link in FORCE_JOIN_LINKS:
        try:
            if 't.me/' in link:
                username = link.split('t.me/')[-1].split('?')[0]
                if not username.startswith('@'):
                    username = '@' + username
                member = await context.bot.get_chat_member(chat_id=username, user_id=user_id)
                if member.status in ['left', 'kicked']:
                    all_joined = False
                    break
        except:
            all_joined = False
    
    if all_joined:
        data[str(user_id)] = {'verified': True}
        save_data(USER_JOINS_FILE, data)
    return all_joined

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username or "No username"
    
    update_stats(user_id)
    
    if not await check_force_joined(user_id, context):
        msg = f"💰 *{fancy('refer and earn bot')}* 💰\n\n{LINE}\n\n⚠️ *ACCESS RESTRICTED*\n\n👋 *Hey {first_name.upper()}!*\n\nYou need to join our *{len(FORCE_JOIN_LINKS)} channels* first.\n\n{LINE}\n\n🎁 *What You'll Get After Joining:*\n\n✅ Refer 5 friends → Free Custom Bot\n✅ Earn unlimited bots\n✅ 24/7 support\n\n👇 *Join all channels below:*"
        
        await update.message.reply_text(msg, reply_markup=get_force_keyboard(), parse_mode='Markdown')
        return
    
    referrals = load_data(REFERRALS_FILE)
    uid = str(user_id)
    
    args = context.args
    if args and args[0].startswith('ref_'):
        referrer = args[0].replace('ref_', '')
        if uid != referrer and uid not in referrals.get(referrer, {}).get('users', []):
            if referrer not in referrals:
                referrals[referrer] = {'count': 0, 'users': [], 'can_withdraw': False}
            if uid not in referrals[referrer]['users']:
                referrals[referrer]['count'] += 1
                referrals[referrer]['users'].append(uid)
                update_referral_count()
                if referrals[referrer]['count'] >= 5:
                    referrals[referrer]['can_withdraw'] = True
                    await context.bot.send_message(
                        chat_id=int(referrer),
                        text=f"🎉 *CONGRATULATIONS!*\n\n{LINE}\n\nYou have referred 5 people!\n\n✅ You are eligible for a *FREE CUSTOM BOT*!",
                        parse_mode='Markdown'
                    )
                save_data(REFERRALS_FILE, referrals)
    
    if uid not in referrals:
        referrals[uid] = {'count': 0, 'users': [], 'can_withdraw': False}
        save_data(REFERRALS_FILE, referrals)
    
    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{uid}"
    count = referrals[uid]['count']
    can_withdraw = referrals[uid]['can_withdraw']
    
    msg = f"💰 *{fancy('refer and earn bot')}* 💰\n\n{LINE}\n\n👋 Welcome *{first_name.upper()}*!\n\n{LINE}\n\n📊 *Your Stats*\n├ Referrals: {count}/5\n└ Status: {'✅ Ready to Withdraw' if can_withdraw else f'❌ Need {5-count} more'}\n\n{LINE}\n\n🎯 *How It Works*\n1️⃣ Share your referral link\n2️⃣ Get 5 friends to join\n3️⃣ Claim your Free Custom Bot\n\n{LINE}\n\n🔗 *Your Referral Link*\n{ref_link}"
    
    await update.message.reply_text(msg, reply_markup=get_menu_keyboard(ref_link, can_withdraw), parse_mode='Markdown')

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    first_name = query.from_user.first_name
    
    if await check_force_joined(user_id, context):
        data = load_data(USER_JOINS_FILE)
        data[str(user_id)] = {'verified': True}
        save_data(USER_JOINS_FILE, data)
        
        referrals = load_data(REFERRALS_FILE)
        if str(user_id) not in referrals:
            referrals[str(user_id)] = {'count': 0, 'users': [], 'can_withdraw': False}
            save_data(REFERRALS_FILE, referrals)
        
        bot_username = context.bot.username
        ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        msg = f"✅ *VERIFICATION SUCCESSFUL*\n\n{LINE}\n\nWelcome *{first_name.upper()}*!\n\n🔗 *Your Referral Link*\n{ref_link}\n\nShare this link to earn a Free Custom Bot!"
        
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(fancy(SHARE_BTN), url=ref_link)]]), parse_mode='Markdown')
    else:
        msg = f"❌ *VERIFICATION FAILED*\n\n{LINE}\n\nYou haven't joined all {len(FORCE_JOIN_LINKS)} channels yet."
        await query.edit_message_text(msg, reply_markup=get_force_keyboard(), parse_mode='Markdown')

async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    data = load_data(REFERRALS_FILE).get(uid, {'count': 0, 'can_withdraw': False})
    remaining = 5 - data['count'] if data['count'] < 5 else 0
    msg = f"📊 *YOUR STATS*\n\n{LINE}\n\n✅ Referrals: {data['count']}/5\n📉 Remaining: {remaining}\n🎁 Status: {'✅ Ready' if data['can_withdraw'] else '🔒 Locked'}"
    await query.edit_message_text(msg, reply_markup=get_back_button(), parse_mode='Markdown')

async def bot_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stats = load_stats()
    requests = load_data(REQUESTS_FILE)
    pending = sum(1 for r in requests.values() if r.get('status') == 'pending')
    completed = sum(1 for r in requests.values() if r.get('status') == 'completed')
    msg = f"🤖 *BOT STATS*\n\n{LINE}\n\n📊 *Overall:*\n├ Users: {stats['users']}\n├ Active Today: {stats['active']}\n├ Bots Made: {stats['bots']}\n└ Referrals: {stats['referrals']}\n\n📋 *Requests:*\n├ Pending: {pending}\n└ Completed: {completed}"
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data='botstats')], [InlineKeyboardButton("🔙 Back", callback_data='menu')]]
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def withdraw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    data = load_data(REFERRALS_FILE).get(uid, {})
    if not data.get('can_withdraw'):
        await query.edit_message_text("❌ *NOT ELIGIBLE*\n\nRefer 5 people first.", parse_mode='Markdown')
        return
    msg = f"🎁 *CLAIM YOUR FREE BOT*\n\n{LINE}\n\nReply with your bot requirement.\nExample: \"I need a welcome bot\"\n\n📞 Contact: {OWNER_USERNAME}"
    context.user_data['waiting'] = True
    await query.edit_message_text(msg, reply_markup=get_back_button(), parse_mode='Markdown')

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting'):
        return
    user_id = update.effective_user.id
    username = update.effective_user.username or "No username"
    first_name = update.effective_user.first_name
    req = update.message.text
    requests = load_data(REQUESTS_FILE)
    req_id = len(requests) + 1
    requests[req_id] = {'user_id': user_id, 'username': username, 'name': first_name, 'requirement': req, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 'pending'}
    save_data(REQUESTS_FILE, requests)
    refs = load_data(REFERRALS_FILE)
    if str(user_id) in refs:
        refs[str(user_id)]['can_withdraw'] = False
        refs[str(user_id)]['count'] = 0
        save_data(REFERRALS_FILE, refs)
    await update.message.reply_text(f"✅ *Request #{req_id} Submitted!*\n\nYou will be notified within 24-48 hours.", parse_mode='Markdown')
    admin_txt = f"🔔 *NEW REQUEST #{req_id}*\n\n👤 {first_name} (@{username})\n📝 {req}"
    keyboard = [[InlineKeyboardButton("✅ Done", callback_data=f"done_{req_id}"), InlineKeyboardButton("💬 Chat", url=f"tg://user?id={user_id}")]]
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    context.user_data['waiting'] = False

async def done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.answer("Unauthorized!", show_alert=True)
        return
    req_id = query.data.split('_')[1]
    reqs = load_data(REQUESTS_FILE)
    if int(req_id) in reqs:
        reqs[int(req_id)]['status'] = 'completed'
        save_data(REQUESTS_FILE, reqs)
        update_bot_count()
        user_id = reqs[int(req_id)]['user_id']
        await context.bot.send_message(chat_id=user_id, text=f"🎉 *BOT READY!*\n\nYour bot (Request #{req_id}) is ready!\nContact {OWNER_USERNAME}", parse_mode='Markdown')
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"✅ Request #{req_id} completed!")

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = f"❓ *HELP*\n\n{LINE}\n\n1️⃣ Join {len(FORCE_JOIN_LINKS)} channels\n2️⃣ Click Verify\n3️⃣ Share your link\n4️⃣ Get 5 friends\n5️⃣ Claim free bot"
    await query.edit_message_text(msg, reply_markup=get_back_button(), parse_mode='Markdown')

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    first_name = query.from_user.first_name
    data = load_data(REFERRALS_FILE).get(uid, {'count': 0, 'can_withdraw': False})
    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{uid}"
    msg = f"💰 *{fancy('refer and earn bot')}* 💰\n\n{LINE}\n\n👋 Welcome *{first_name.upper()}*!\n\n📊 Referrals: {data['count']}/5\n🎁 Status: {'✅ Ready' if data['can_withdraw'] else '🔒 Locked'}"
    await query.edit_message_text(msg, reply_markup=get_menu_keyboard(ref_link, data['can_withdraw']), parse_mode='Markdown')

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern='verify'))
    app.add_handler(CallbackQueryHandler(stats_callback, pattern='stats'))
    app.add_handler(CallbackQueryHandler(bot_stats_callback, pattern='botstats'))
    app.add_handler(CallbackQueryHandler(withdraw_callback, pattern='withdraw'))
    app.add_handler(CallbackQueryHandler(help_callback, pattern='help'))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern='menu'))
    app.add_handler(CallbackQueryHandler(done_callback, pattern='done_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
    
    print("💰 Refer And Earn Bot is running...")
    print(f"👤 Admin ID: {ADMIN_ID}")
    print(f"🔗 Force Join Channels: {len(FORCE_JOIN_LINKS)}")
    app.run_polling()

if __name__ == '__main__':
    main()
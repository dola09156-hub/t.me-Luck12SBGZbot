import os
import random
import logging
from datetime import time as dtime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TOKEN = os.environ["BOT_TOKEN"]

FACTS = [
    "The first World Cup was held in Uruguay in 1930, and Uruguay won it.",
    "Brazil has won the World Cup five times, more than any other nation.",
    "Pelé is the only player to have won three World Cups.",
    "Miroslav Klose holds the record for most World Cup goals, with 16.",
    "Just Fontaine scored 13 goals at the 1958 World Cup, still the record for a single tournament.",
    "The fastest goal in World Cup history was scored by Hakan Şükür in 2002, just 11 seconds after kickoff.",
    "The biggest international win on record is Australia 31-0 American Samoa, played in 2001.",
    "Yellow and red cards were first used at the 1970 World Cup.",
    "The penalty kick was introduced in 1891.",
    "Arsenal went the entire 2003-04 Premier League season unbeaten and became known as 'The Invincibles'.",
    "Lionel Messi has won a record eight Ballon d'Or awards.",
    "Cristiano Ronaldo is the all-time top scorer in the Champions League.",
    "Real Madrid has won more European Cup and Champions League titles than any other club.",
    "The first Women's World Cup was held in 1991, and the USA won it.",
    "FIFA has more than 200 member associations, which is more than the United Nations has members.",
    "The Premier League began in 1992.",
    "Argentina won the World Cup in 1978, 1986 and 2022.",
    "Goalkeepers are the only players allowed to handle the ball inside their own penalty area.",
]

RULES = [
    ("Offside", "A player is offside if they are closer to the opponent's goal line than both the ball and the second last defender when the ball is played to them, and they are in the opponent's half."),
    ("Penalty Kick", "A penalty is awarded when a defender commits a foul inside their own penalty area. The ball is placed 11 metres from goal, and only the kicker and the goalkeeper take part."),
    ("Match Length", "A match has two halves of 45 minutes each. The referee adds extra time at the end of each half for stoppages."),
    ("Yellow and Red Cards", "A yellow card is a warning. Two yellow cards in one match lead to a red card, and a player who gets a red card must leave the pitch."),
    ("Corner Kick", "A corner is awarded when the defending team last touches the ball before it crosses their own goal line. The ball is kicked from the corner of the pitch."),
    ("Throw-in", "When the ball goes out over the sideline, the team that did not touch it last restarts play with a throw-in, using both hands and keeping both feet on the ground."),
]

# (question, [options], index of correct option)
QUIZ = [
    ("Which country has won the most World Cups?", ["Germany", "Brazil", "Italy", "Argentina"], 1),
    ("Who holds the record for most World Cup goals?", ["Pelé", "Ronaldo (Brazil)", "Miroslav Klose", "Lionel Messi"], 2),
    ("Where was the first World Cup held in 1930?", ["Brazil", "Uruguay", "Italy", "England"], 1),
    ("Who is the only player to win three World Cups?", ["Maradona", "Pelé", "Zidane", "Cruyff"], 1),
    ("How many players does each team have on the pitch?", ["9", "10", "11", "12"], 2),
    ("How long are the two halves of a standard match?", ["30 minutes each", "40 minutes each", "45 minutes each", "50 minutes each"], 2),
    ("In which year did the Premier League begin?", ["1985", "1992", "1998", "2001"], 1),
    ("Which team went unbeaten through the 2003-04 Premier League season?", ["Chelsea", "Manchester United", "Arsenal", "Liverpool"], 2),
]

MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("⚽ Football Fact", callback_data="fact"),
     InlineKeyboardButton("🧠 Quiz", callback_data="quiz")],
    [InlineKeyboardButton("📖 Rules Explained", callback_data="rule"),
     InlineKeyboardButton("🔔 Daily Fact", callback_data="subscribe")],
])


def fact_text():
    return f"⚽ *Football fact*\n\n{random.choice(FACTS)}"


def rule_text():
    name, body = random.choice(RULES)
    return f"📖 *{name}*\n\n{body}"


def quiz_markup(qi):
    _, options, _ = QUIZ[qi]
    rows = [[InlineKeyboardButton(opt, callback_data=f"ans:{qi}:{ci}")] for ci, opt in enumerate(options)]
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "friend"
    await update.message.reply_text(
        f"👋 Hi {name}! Welcome to your football fact corner.\n\n"
        "Get football facts, test yourself with a quiz, or learn the rules in plain language.\n\n"
        "Choose an option:",
        reply_markup=MENU,
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start - Main menu\n"
        "/fact - Random football fact\n"
        "/quiz - Football quiz question\n"
        "/rules - A rule explained simply\n"
        "/subscribe - Get one fact every day\n"
        "/unsubscribe - Stop daily facts\n"
        "/about - About this bot"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This bot shares free football facts, quizzes and simple rule "
        "explanations for fans of all levels. It is for fun and learning only."
    )


async def fact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fact_text(), parse_mode="Markdown", reply_markup=MENU)


async def rule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(rule_text(), parse_mode="Markdown", reply_markup=MENU)


async def quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qi = random.randrange(len(QUIZ))
    await update.effective_message.reply_text(f"🧠 *Quiz*\n\n{QUIZ[qi][0]}", parse_mode="Markdown", reply_markup=quiz_markup(qi))


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, qi, ci = q.data.split(":")
    qi, ci = int(qi), int(ci)
    question, options, correct = QUIZ[qi]
    if ci == correct:
        result = "✅ Correct! Well done."
    else:
        result = f"❌ Not quite. The answer is: {options[correct]}"
    next_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Next question", callback_data="quiz")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ])
    await q.edit_message_text(f"🧠 {question}\n\n{result}", reply_markup=next_markup)


# ---------- Daily fact subscriptions (in memory; resets on redeploy) ----------
SUBSCRIBERS = set()


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SUBSCRIBERS.add(update.effective_chat.id)
    await update.effective_message.reply_text("🔔 Subscribed! You will get one football fact every day. Use /unsubscribe to stop.")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SUBSCRIBERS.discard(update.effective_chat.id)
    await update.message.reply_text("🔕 Unsubscribed. Come back any time with /subscribe.")


async def daily_job(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(SUBSCRIBERS):
        try:
            await context.bot.send_message(chat_id, fact_text(), parse_mode="Markdown")
        except Exception as e:
            log.warning("Could not send to %s: %s", chat_id, e)
            SUBSCRIBERS.discard(chat_id)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("ans:"):
        await answer(update, context)
    elif q.data == "fact":
        await q.message.reply_text(fact_text(), parse_mode="Markdown", reply_markup=MENU)
    elif q.data == "rule":
        await q.message.reply_text(rule_text(), parse_mode="Markdown", reply_markup=MENU)
    elif q.data == "quiz":
        await quiz_cmd(update, context)
    elif q.data == "menu":
        await q.message.reply_text("Choose an option:", reply_markup=MENU)
    elif q.data == "subscribe":
        await subscribe(update, context)


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use the buttons below or type /help.", reply_markup=MENU)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("fact", fact_cmd))
    app.add_handler(CommandHandler("rules", rule_cmd))
    app.add_handler(CommandHandler("quiz", quiz_cmd))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # Daily fact at 08:00 UTC
    app.job_queue.run_daily(daily_job, time=dtime(hour=8, minute=0))

    log.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()

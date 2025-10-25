import logging
import os
import threading
from datetime import datetime, timedelta, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from database import Database
from price_checker import PriceChecker

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress logs
        pass


# Thêm function này
def start_health_server():
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    logger.info(f"Health check server started on port {port}")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize components
db = Database()
price_checker = PriceChecker()
scheduler = AsyncIOScheduler()

# Store bot application globally for scheduler access
bot_app = None


def get_vn_time():
    """Get current Vietnam time (UTC+7)"""
    return datetime.now(timezone.utc) + timedelta(hours=7)


def is_trading_hours() -> bool:
    """Check if current time is within trading hours (9:00-11:30, 13:00-15:00 VN time)"""
    vn_time = get_vn_time()
    current_time = vn_time.time()

    # Check if weekend
    if vn_time.weekday() >= 5:
        return False

    # Morning session: 9:00 - 11:30
    morning_start = datetime.strptime("09:00", "%H:%M").time()
    morning_end = datetime.strptime("11:30", "%H:%M").time()

    # Afternoon session: 13:00 - 15:00
    afternoon_start = datetime.strptime("13:00", "%H:%M").time()
    afternoon_end = datetime.strptime("15:00", "%H:%M").time()

    # Check if in trading hours
    in_morning = morning_start <= current_time <= morning_end
    in_afternoon = afternoon_start <= current_time <= afternoon_end

    return in_morning or in_afternoon

def format_price(price: float) -> str:
    """Format price nicely - remove .0 for whole numbers"""
    if price == int(price):
        return f"{int(price):,}"
    else:
        return f"{price:,.1f}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    welcome_msg = """
🤖 *Chào mừng đến với Stock Alert Bot!*

📊 Bot giúp bạn theo dõi giá cổ phiếu và nhận thông báo khi đạt ngưỡng mong muốn.

*Các lệnh có sẵn:*
/alert <MÃ> <GIÁ> - Đặt cảnh báo (VD: /alert HPG 25500)
/list - Xem danh sách cảnh báo
/edit <MÃ> <GIÁ> - Sửa giá alert (VD: /edit HPG 26500)
/remove <MÃ> - Xóa alert theo mã
/clear - Xóa tất cả alerts
/price <MÃ> - Kiểm tra giá hiện tại# Check status
fly status

# Check recent logs
fly logs --limit 200

# Check machine events
fly machine list

/guide - Xem hướng dẫn
/help - Trợ giúp

*Lưu ý:*
• Giá hiển thị đầy đủ (26,200 = 26,200 VNĐ)
• Bot kiểm tra giá mỗi 10 giây
• Cảnh báo tự động xóa sau khi kích hoạt

Bắt đầu bằng cách gõ: /alert HPG 25500
    """
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show command list"""
    help_msg = """
📋 *Danh sách lệnh:*

/alert <MÃ> <GIÁ> - Đặt cảnh báo
/list - Xem danh sách alerts
/edit <MÃ> <GIÁ> - Sửa giá alert
/remove <MÃ> - Xóa alert
/clear - Xóa tất cả
/price <MÃ> - Kiểm tra giá
/guide - Hướng dẫn chi tiết

*Ví dụ:*
`/alert HPG 26500`
`/price HPG`
`/edit HPG 27000`
    """
    await update.message.reply_text(help_msg, parse_mode='Markdown')

async def guide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed guide"""
    guide_msg = """
📖 *Hướng dẫn chi tiết:*

*1️⃣ Đặt cảnh báo:*
`/alert HPG 25500`
→ Nhận thông báo khi HPG đạt ≥ 25,500 VNĐ

*2️⃣ Xem danh sách:*
`/list`
→ Hiển thị tất cả cảnh báo với giá hiện tại

*3️⃣ Sửa giá alert:*
`/edit HPG 26500`
→ Sửa alert HPG thành giá mới 26,500 VNĐ

*4️⃣ Xóa alert:*
`/remove HPG` - Xóa alert của mã HPG
`/clear` - Xóa tất cả alerts

*5️⃣ Kiểm tra giá:*
`/price HPG`
→ Xem giá hiện tại của HPG

*Lưu ý:*
• Mỗi mã chỉ có 1 alert
• Alert tự động xóa sau khi kích hoạt
• Giá hiển thị đầy đủ VNĐ

*Ví dụ thực tế:*
• `/alert VNM 80000` - Báo khi VNM ≥ 80,000 VNĐ
• `/list` - Xem alerts
• `/edit VNM 81000` - Sửa thành 81,000 VNĐ
• `/remove VNM` - Xóa alert VNM
• `/clear` - Xóa hết
    """
    await update.message.reply_text(guide_msg, parse_mode='Markdown')


async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /alert command"""
    # Safety check
    if not update.message:
        return

    chat_id = update.effective_chat.id

    # Check command format
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Sai cú pháp!\n\n"
            "Đúng: /alert <MÃ> <GIÁ>\n"
            "Ví dụ: /alert HPG 25500"
        )
        return

    symbol = context.args[0].upper()
    try:
        target_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Giá không hợp lệ! Vui lòng nhập số.")
        return

    if target_price <= 0:
        await update.message.reply_text("❌ Giá phải lớn hơn 0!")
        return

    # Validate symbol
    await update.message.reply_text(f"⏳ Đang kiểm tra mã {symbol}...")
    is_valid = await price_checker.validate_symbol(symbol)

    if not is_valid:
        await update.message.reply_text(
            f"❌ Không tìm thấy mã {symbol}!\n"
            "Vui lòng kiểm tra lại mã cổ phiếu."
        )
        return

    # Get current price
    current_price = await price_checker.get_price(symbol)

    # Check if alert already exists
    if db.alert_exists(chat_id, symbol):
        await update.message.reply_text(
            f"⚠️ *Cảnh báo đã tồn tại!*\n\n"
            f"Bạn đã có alert cho *{symbol}*\n\n"
            f"Dùng `/list` để xem tất cả alerts",
            parse_mode='Markdown'
        )
        return

    # Add alert to database
    if db.add_alert(chat_id, symbol, target_price):
        msg = (
            f"✅ *Đã đặt cảnh báo!*\n\n"
            f"📊 Mã: *{symbol}*\n"
            f"🎯 Giá mục tiêu: *{format_price(target_price)}* VNĐ\n"
            f"💰 Giá hiện tại: *{format_price(current_price)}* VNĐ\n\n"
            f"Bot sẽ thông báo khi {symbol} đạt ≥ {format_price(target_price)}"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Lỗi khi đặt cảnh báo. Vui lòng thử lại!")


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all alerts for user"""
    if not update.message:
        return

    chat_id = update.effective_chat.id
    alerts = db.get_user_alerts(chat_id)

    if not alerts:
        await update.message.reply_text(
            "📭 Bạn chưa có cảnh báo nào!\n\n"
            "Đặt cảnh báo bằng: /alert HPG 25500"
        )
        return

    msg = "📋 *Danh sách cảnh báo:*\n\n"

    for alert_id, symbol, target_price in alerts:
        current_price = await price_checker.get_price(symbol)

        # Calculate distance to target
        if current_price:
            distance = target_price - current_price
            distance_pct = (distance / current_price * 100) if current_price else 0

            if distance > 0:
                status = f"📈 Còn {format_price(distance)} ({distance_pct:.1f}%)"
            else:
                status = f"✅ Đã đạt!"

            msg += f"*ID {alert_id}:* {symbol}\n"
            msg += f"  🎯 Target: {format_price(target_price)}\n"
            msg += f"  💰 Hiện tại: {format_price(current_price)}\n"
            msg += f"  {status}\n\n"
        else:
            msg += f"*ID {alert_id}:* {symbol}\n"
            msg += f"  🎯 Target: {format_price(target_price)}\n"
            msg += f"  💰 Hiện tại: N/A\n\n"

    msg += f"_Tổng: {len(alerts)} cảnh báo_\n\n"
    msg += "💡 *Thao tác:*\n"
    msg += "`/edit <MÃ> <GIÁ>` - Sửa\n"
    msg += "`/remove <MÃ>` - Xóa alert\n"
    msg += "`/clear` - Xóa tất cả"

    await update.message.reply_text(msg, parse_mode='Markdown')


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove alerts for a symbol"""
    if not update.message:
        return

    chat_id = update.effective_chat.id

    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Sai cú pháp!\n\n"
            "Đúng: /remove <MÃ>\n"
            "Ví dụ: /remove HPG"
        )
        return

    symbol = context.args[0].upper()
    count = db.remove_alerts_by_symbol(chat_id, symbol)

    if count > 0:
        await update.message.reply_text(
            f"✅ Đã xóa cảnh báo cho mã *{symbol}*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ Không tìm thấy cảnh báo nào cho mã *{symbol}*",
            parse_mode='Markdown'
        )

async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit alert price"""
    if not update.message:
        return

    chat_id = update.effective_chat.id

    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Sai cú pháp!\n\n"
            "Đúng: /edit <MÃ> <GIÁ_MỚI>\n"
            "Ví dụ: /edit HPG 26.5"
        )
        return

    symbol = context.args[0].upper()

    try:
        new_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text(
            "❌ Giá không hợp lệ!\n"
            "Giá phải là số"
        )
        return

    if new_price <= 0:
        await update.message.reply_text("❌ Giá phải lớn hơn 0!")
        return

    # Check if user has alert for this symbol
    if not db.alert_exists(chat_id, symbol):
        await update.message.reply_text(
            f"❌ Bạn chưa có alert cho mã *{symbol}*\n\n"
            f"Dùng /alert {symbol} {int(new_price)} để tạo mới",
            parse_mode='Markdown'
        )
        return

    # Update alert
    if db.update_alert_by_symbol(chat_id, symbol, new_price):
        current_price = await price_checker.get_price(symbol)

        msg = (
            f"✅ *Đã cập nhật alert!*\n\n"
            f"📊 Mã: *{symbol}*\n"
            f"🎯 Giá mới: *{format_price(new_price)}* VNĐ\n"
        )

        if current_price:
            msg += f"💰 Giá hiện tại: *{format_price(current_price)}* VNĐ\n"

            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Lỗi khi cập nhật alert!")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all alerts for user"""
    if not update.message:
        return

    chat_id = update.effective_chat.id
    count = db.clear_user_alerts(chat_id)

    if count > 0:
        await update.message.reply_text(
            f"✅ Đã xóa tất cả {count} cảnh báo!"
        )
    else:
        await update.message.reply_text(
            "📭 Bạn chưa có cảnh báo nào để xóa!"
        )


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check current price of a stock"""
    if not update.message:
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Sai cú pháp!\n\n"
            "Đúng: /price <MÃ>\n"
            "Ví dụ: /price HPG"
        )
        return

    symbol = context.args[0].upper()
    await update.message.reply_text(f"⏳ Đang lấy giá {symbol}...")

    info = await price_checker.get_stock_info(symbol)

    if info:
        change_emoji = "🟢" if info['change'] > 0 else "🔴" if info['change'] < 0 else "⚪"
        msg = (
            f"{change_emoji} *{info['symbol']}*\n\n"
            f"💰 Giá: *{format_price(info['price'])}* VNĐ\n"
            f"📈 Thay đổi: {info['change']:+,.0f} ({info['change_percent']:+.2f}%)\n"
            f"📊 Cao: {format_price(info['high'])} | Thấp: {format_price(info['low'])}\n"
            f"📦 KL: {info['volume']:,.0f}\n"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"❌ Không tìm thấy thông tin cho mã *{symbol}*",
            parse_mode='Markdown'
        )


async def check_alerts():
    """Background task to check all alerts"""

    if not is_trading_hours():
        logger.debug("Outside trading hours, skipping price check")
        return

    alerts = db.get_all_alerts()

    for alert_id, chat_id, symbol, target_price in alerts:
        try:
            current_price = await price_checker.get_price(symbol)

            if current_price is None:
                continue

            # Check if price reached target
            if current_price >= target_price:
                # Send notification
                msg = (
                    f"🎯 *CẢNH BÁO GIÁ!*\n\n"
                    f"📊 *{symbol}* đã đạt mục tiêu!\n\n"
                    f"🎯 Giá mục tiêu: *{format_price(target_price)}* VNĐ\n"
                    f"💰 Giá hiện tại: *{format_price(current_price)}* VNĐ\n\n"
                    f"_Cảnh báo đã được tự động xóa_"
                )

                try:
                    await bot_app.bot.send_message(
                        chat_id=chat_id,
                        text=msg,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error sending notification: {e}")

                # Remove alert after notification
                db.remove_alerts_by_symbol(chat_id,symbol)
                logger.info(f"Alert triggered and removed: {symbol} @ {target_price} for chat {chat_id}")

        except Exception as e:
            logger.error(f"Error checking alert {alert_id}: {e}")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    if not update.message:
        return

    await update.message.reply_text(
        "❌ Lệnh không hợp lệ!\n\n"
        "Gõ /help để xem danh sách lệnh."
    )


def main():
    """Start the bot"""
    global bot_app

    # Create application
    bot_app = Application.builder().token(config.BOT_TOKEN).build()

    # Add command handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("guide", guide_command))
    bot_app.add_handler(CommandHandler("alert", alert_command))
    bot_app.add_handler(CommandHandler("list", list_command))
    bot_app.add_handler(CommandHandler("remove", remove_command))
    bot_app.add_handler(CommandHandler("edit", edit_command))
    bot_app.add_handler(CommandHandler("clear", clear_command))
    bot_app.add_handler(CommandHandler("price", price_command))

    # Set bot commands menu (shows when user types /)
    async def post_init(application: Application) -> None:
        """Set bot commands after initialization"""
        await application.bot.set_my_commands([
            ("alert", "Đặt cảnh báo giá"),
            ("list", "Xem danh sách alerts"),
            ("edit", "Sửa giá alert"),
            ("remove", "Xóa alert"),
            ("clear", "Xóa tất cả"),
            ("price", "Kiểm tra giá hiện tại"),
            ("help", "Danh sách lệnh"),
            ("guide", "Hướng dẫn chi tiết"),
        ])

        # Start scheduler in async context
        if not scheduler.running:
            scheduler.start()  # ← MOVE vào đây!
            logger.info(f"Scheduler started - checking prices every {config.CHECK_INTERVAL} seconds")

    bot_app.post_init = post_init

    # Schedule price checking job (but don't start scheduler yet)
    scheduler.add_job(
        check_alerts,  # ← Function thật
        'interval',
        seconds=config.CHECK_INTERVAL,
        id='check_alerts'
    )
    # ← XÓA scheduler.start() ở đây!

    logger.info("Bot started successfully!")

    # Start health check server
    start_health_server()

    # Start bot
    bot_app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

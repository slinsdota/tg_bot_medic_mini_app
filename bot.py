from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
import json
import html
import logging

TELEGRAM_BOT_TOKEN = "8250987817:AAFx70NebFO6Lrl-xS7RDz6zaeM01bdzNrA"
WEB_APP_URL = "https://slinsdota.github.io/medic_mini_app2/"  

# Включите логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с кнопкой запуска Mini App"""
    keyboard = [
        [KeyboardButton(
            text="🧪 Открыть анализатор",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    welcome_message = (
        "👋 Добро пожаловать в Медицинский анализатор!\n\n"
        "🧪 Нажмите на кнопку ниже, чтобы открыть приложение "
        "и ввести результаты ваших лабораторных анализов.\n\n"
        "📊 Приложение поможет вам расшифровать:\n"
        "• Общий анализ крови (ОАК)\n"
        "• Биохимический анализ крови\n"
        "• Общий анализ мочи (ОАМ)\n"
        "• Гемостазиограмму"
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик данных из Web App"""
    try:
        logger.info(f"Получены данные из Web App")
        
        # Получаем данные из web_app
        if update.message and update.message.web_app_data:
            data_string = update.message.web_app_data.data
            logger.info(f"Данные: {data_string}")
            
            # Парсим JSON
            data = json.loads(data_string)
            
            # Определяем тип анализа
            type_names = {
                'blood-general': 'Общий анализ крови',
                'blood-bio': 'Биохимический анализ крови',
                'urine-general': 'Общий анализ мочи',
                'hemostasis': 'Гемостазиограмма'
            }
            
            analysis_type = type_names.get(data.get('type', ''), 'Неизвестный анализ')
            
            # Форматируем сообщение
            message_text = f"🧪 <b>{analysis_type}</b>\n\n"
            
            # Добавляем результаты
            results = data.get('results', [])
            if results:
                for result in results:
                    status = result.get('status', '')
                    status_icon = "✅" if status == 'normal' else "⚠️" if status == 'warning' else "❌"
                    
                    parameter = html.escape(result.get('parameter', ''))
                    value = html.escape(result.get('value', ''))
                    explanation = html.escape(result.get('explanation', ''))
                    
                    message_text += f"{status_icon} <b>{parameter}:</b> {value}\n"
                    message_text += f"{explanation}\n\n"
                
                # Добавляем общую рекомендацию
                has_warnings = any(r.get('status') == 'warning' for r in results)
                if has_warnings:
                    message_text += (
                        "💡 <b>Рекомендация:</b> Некоторые показатели требуют внимания. "
                        "Рекомендуется проконсультироваться с врачом для точной диагностики "
                        "и назначения лечения."
                    )
                else:
                    message_text += (
                        "🎉 <b>Отличные результаты!</b> Все показатели в норме. "
                        "Продолжайте вести здоровый образ жизни!"
                    )
            else:
                message_text += "Результаты не получены."
            
            # Отправляем сообщение
            await update.message.reply_text(
                message_text, 
                parse_mode='HTML'
            )
            
            logger.info("Результаты успешно отправлены")
            
        else:
            logger.warning("web_app_data не найдено в сообщении")
            await update.message.reply_text(
                "❌ Данные из мини-приложения не получены."
            )
        
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        await update.message.reply_text(
            "❌ Ошибка обработки данных. Неверный формат JSON."
        )
    except Exception as e:
        logger.error(f"Ошибка обработки данных: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке результатов"
        )


def main():
    """Запуск бота"""
    logger.info("Запуск бота...")
    
    # Создаем Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data)
    )
    
    logger.info("Бот запущен и готов к работе")
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

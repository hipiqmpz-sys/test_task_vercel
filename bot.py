import requests
from supabase import create_client

# 1. НАСТРОЙКИ
CRM_URL = "CRM_URL"
CRM_API_KEY = "CRM_API_KEY"

SUPABASE_URL = "SUPABASE_URL"
SUPABASE_KEY = "SUPABASE_KEY"

TELEGRAM_TOKEN = "token"
TELEGRAM_CHAT_ID = "chatid"

# Инициализация Supabase 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def send_telegram_alert(first_name, total_sum, city):
    """Функция для отправки уведомления в Telegram"""
    message = (
        f"🔥 *КРУПНЫЙ ЗАКАЗ!*\n\n"
        f"👤 Клиент: {first_name}\n"
        f"💰 Сумма: {total_sum:,.0f} ₸\n"
        f"📍 Город: {city}\n"
        f"🚀 Проверьте RetailCRM!"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
        print(f"✅ Уведомление отправлено в Telegram для {first_name}")
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")


def sync_orders():
    print("--- Начинаю синхронизацию ---")

    # 2. Получаем заказы из RetailCRM
    crm_endpoint = f"{CRM_URL}/api/v5/orders"
    params = {"apiKey": CRM_API_KEY}

    try:
        response = requests.get(crm_endpoint, params=params)
        response.raise_for_status() 

        data = response.json()
        orders = data.get('orders', [])

    except Exception as e:
        print(f"❌ Ошибка при запросе к RetailCRM: {e}")
        return

    if not orders:
        print("⚠️ Заказов не найдено.")
        return

    print(f"📦 Найдено заказов: {len(orders)}")

    # 3. Цикл обработки заказов
    for order in orders:
        # Извлекаем данные (используем .get чтобы не было ошибок если поля нет)
        external_id = str(order.get('id'))
        first_name = order.get('firstName', 'Клиент')
        last_name = order.get('lastName', '')
        total_sum = float(order.get('totalSumm', 0))
        city = order.get('delivery', {}).get('address', {}).get('city', 'Не указан')
        status = order.get('status', 'new')

        # Подготовка для Supabase
        db_data = {
            "external_id": external_id,
            "first_name": first_name,
            "last_name": last_name,
            "total_sum": total_sum,
            "city": city,
            "status": status
        }

        # Сохраняем в Supabase (upsert предотвращает дубликаты)
        try:
            supabase.table("orders").upsert(db_data, on_conflict="external_id").execute()
        except Exception as e:
            print(f"⚠️ Ошибка Supabase для заказа {external_id}: {e}")

        # ПРОВЕРКА УСЛОВИЯ ДЛЯ ТЕЛЕГРАМА (50 000 тенге)
        if total_sum > 50000:
            send_telegram_alert(first_name, total_sum, city)

    print("--- Синхронизация завершена успешно! ---")


if __name__ == "__main__":
    sync_orders()

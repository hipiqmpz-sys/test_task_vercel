import requests
from supabase import create_client

# 1. RetailCRM
CRM_URL = "CRM_URL"
CRM_API_KEY = "CRM_API_KEY"

# 2. Supabase
SUPABASE_URL = "SUPABASE_URL"
SUPABASE_KEY = "SUPABASE_KEY"

# Инициализация клиента Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def sync_orders():
    print("--- Начинаю синхронизацию ---")

    # Получаем заказы из RetailCRM
    # Метод /api/v5/orders возвращает список всех заказов
    crm_endpoint = f"{CRM_URL}/api/v5/orders"
    params = {"apiKey": CRM_API_KEY}

    response = requests.get(crm_endpoint, params=params)

    if response.status_code == 200:
        orders = response.json().get('orders', [])
        print(f"Получено заказов из CRM: {len(orders)}")

        for order in orders:
            # Извлекаем нужные данные
            # Важно: в API RetailCRM сумма лежит в totalSumm
            first_name = order.get('firstName', 'Не указано')
            last_name = order.get('lastName', '')
            total_sum = order.get('totalSumm', 0)
            city = order.get('delivery', {}).get('address', {}).get('city', 'Не указан')
            external_id = str(order.get('id'))  # ID заказа в самой CRM

            # Подготовка данных для Supabase
            data = {
                "external_id": external_id,
                "first_name": first_name,
                "last_name": last_name,
                "total_sum": total_sum,
                "city": city,
                "status": order.get('status', 'new')
            }

            # Записываем в Supabase
            try:
                supabase.table("orders").upsert(data, on_conflict="external_id").execute()

                # Условие для Telegram (Шаг 5 задания)
                if total_sum > 50000:
                    print(f"!!! VIP Заказ: {first_name} на сумму {total_sum} ₸")

            except Exception as e:
                print(f"Ошибка при сохранении заказа {external_id}: {e}")

        print("--- Синхронизация завершена успешно ---")
    else:
        print(f"Ошибка при запросе к CRM: {response.status_code} - {response.text}")


if __name__ == "__main__":
    sync_orders()

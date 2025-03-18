import firebase_admin, _config
from datetime import datetime
from firebase_admin import credentials, firestore
import logging

class FireBase:
    def __init__(self):
        """Инициализирует соединение с Firebase"""
        cred = credentials.Certificate(_config.FIREBASE_CRED)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def init(self, user_id: str, user_name: str):
        """Создает коллекцию users, если её нет, и добавляет документ с user_id"""
        if not user_id:
            return {"status": "error", "message": "user_id не может быть пустым"}
        
        if not user_name:
            return {"status": "error", "message": "user_name не может быть пустым"}
        
        user_ref = self.db.collection("users").document(user_id)
        
        try:
            if not user_ref.get().exists:
                user_ref.set({"id": user_id, "user_name": user_name})
                return {"status": "success", "message": "Пользователь создан, все команды можно узанть по команде /help", "data": {"user_id": user_id, "user_name": user_name}}
            else:
                return {"status": "error", "message": "Пользователь уже существует"}
        except Exception as e:
            return {"status": "error", "message": f"Ошибка базы данных: {str(e)}"}

    def add_bank_account(self, user_id: str, name_bank: str, value):
        """Добавляет банковский счет пользователю."""
        if not user_id:
            return {"status": "error", "message": "user_id не может быть пустым"}

        if not name_bank:
            return {"status": "error", "message": "Название банка не может быть пустым"}

        try:
            if isinstance(value, str):
                value = value.replace(",", ".")
            value = float(value)
        except ValueError:
            return {"status": "error", "message": "Некорректное значение суммы"}

        user_ref = self.db.collection("users").document(user_id)  # Гарантируем правильный user_id
        if not user_ref.get().exists:
            return {"status": "error", "message": "Пользователь не найден"}

        try:
            user_ref.update({f"bank_accounts.{name_bank}": value})
            return {"status": "success", "message": "Банковский счет обновлен", "data": {"user_id": user_id, "bank": name_bank, "value": value}}
        except Exception as e:
            return {"status": "error", "message": f"Ошибка базы данных: {str(e)}"}

    def get_bank_accounts(self, user_id: str):
        """Получает банковские счета пользователя и возвращает их в формате JSON."""
        if not user_id:
            return {"status": "error", "message": "user_id не может быть пустым"}

        user_ref = self.db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            return {"status": "error", "message": "Пользователь не найден"}

        user_info = user_data.to_dict()
        bank_accounts = user_info.get("bank_accounts", {})

        return {"status": "success", "data": bank_accounts}

    def add_debt(self, user_id: str, debt_name: str, amount, due_date: str):
        """Добавляет долг пользователю."""

        if not user_id:
            return {"status": "error", "message": "user_id не может быть пустым"}

        if not debt_name:
            return {"status": "error", "message": "Название долга не может быть пустым"}

        # Преобразование суммы в float
        try:
            if isinstance(amount, str):
                amount = amount.replace(",", ".")
            amount = float(amount)
        except ValueError:
            return {"status": "error", "message": "Некорректное значение суммы"}

        # Проверка формата даты
        try:
            datetime.strptime(due_date, "%d.%m.%Y")
        except ValueError:
            return {"status": "error", "message": "Некорректный формат даты (нужен DD.MM.YYYY)"}

        # Проверяем, существует ли пользователь
        user_ref = self.db.collection("users").document(user_id)
        if not user_ref.get().exists:
            return {"status": "error", "message": "Пользователь не найден"}

        # Создаем запись в коллекции `debts`
        debt_ref = user_ref.collection("debts").document(debt_name)
        try:
            debt_ref.set({
                "amount": amount,
                "due_date": due_date
            })
            return {
                "status": "success",
                "message": f"Долг '{debt_name}' на сумму {amount} добавлен. Вернуть до {due_date}.",
                "data": {"debt_name": debt_name, "amount": amount, "due_date": due_date}
            }
        except Exception as e:
            return {"status": "error", "message": f"Ошибка базы данных: {str(e)}"}
    
    

    def get_debts(self, user_id: str):
        """Возвращает все долги пользователя в формате JSON."""
        if not user_id:
            return {"status": "error", "message": "user_id не может быть пустым"}

        user_ref = self.db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            return {"status": "error", "message": "Пользователь не найден"}

        # Получаем данные из подколлекции debts
        debts_ref = user_ref.collection("debts")
        debts_docs = debts_ref.stream()
        debts = {doc.id: doc.to_dict() for doc in debts_docs}

        return {"status": "success", "debts": debts} if debts else {"status": "error", "message": "Нет долгов"}


    def delete_bank_account(self, user_id: str, bank_name: str):
        """Удаляет банковский счет пользователя после подтверждения."""
        
        if not user_id:
            return {"status": "error", "message": "❌ user_id не может быть пустым"}

        if not bank_name:
            return {"status": "error", "message": "❌ Название банка не может быть пустым"}

        # Проверяем, существует ли пользователь
        user_ref = self.db.collection("users").document(user_id)
        user_data = user_ref.get()
        
        if not user_data.exists:
            return {"status": "error", "message": "❌ Пользователь не найден"}

        user_info = user_data.to_dict()
        bank_accounts = user_info.get("bank_accounts", {})

        if bank_name not in bank_accounts:
            return {"status": "error", "message": f"❌ Банк '{bank_name}' не найден в вашем списке."}

        # Удаляем банк
        try:
            user_ref.update({f"bank_accounts.{bank_name}": firestore.DELETE_FIELD})
            return {"status": "success", "message": f"✅ Банк '{bank_name}' успешно удален."}
        except Exception as e:
            return {"status": "error", "message": f"❌ Ошибка базы данных: {str(e)}"}


    def delete_debt(self, user_id: str, debt_name: str):
        """Удаляет долг пользователя."""

        if not user_id:
            return {"status": "error", "message": "❌ user_id не может быть пустым"}

        if not debt_name:
            return {"status": "error", "message": "❌ Название долга не может быть пустым"}

        user_ref = self.db.collection("users").document(user_id)
        if not user_ref.get().exists:
            return {"status": "error", "message": "❌ Пользователь не найден"}

        debt_ref = user_ref.collection("debts").document(debt_name)
        if not debt_ref.get().exists:
            return {"status": "error", "message": "❌ Долг не найден"}

        try:
            debt_ref.delete()
            return {"status": "success", "message": f"✅ Долг '{debt_name}' удален."}
        except Exception as e:
            return {"status": "error", "message": f"❌ Ошибка базы данных: {str(e)}"}
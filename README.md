# Transaction Risk System

Проект предназначен для классификации банковских транзакций по уровню риска и сложности верификации, а также для прогнозирования общего объёма транзакций.  
Система состоит из двух основных частей:
- API (Flask) — предоставляет модель как сервис
- Пользовательское приложение (Streamlit) — графический интерфейс, работающий через API

---

## Установка и запуск проекта

### 1. Системные требования

- **Python 3.10**
- pip (устанавливается вместе с Python)
- macOS / Linux (Windows поддерживается, но команды активации отличаются)

Проверка версии Python:

```bash
python --version
```

Версия должна быть **3.10.x**.

---

### 2. Создание виртуального окружения

В корне проекта выполните:

```bash
python -m venv venv
```

---

### 3. Активация виртуального окружения

#### macOS / Linux

```bash
source venv/bin/activate
```

После активации в терминале появится префикс `(venv)`.

---

### 4. Установка зависимостей

Все необходимые библиотеки перечислены в файле `requirements.txt`.

Установка выполняется **строго после активации виртуального окружения**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Проверка корректности установки:

```bash
python -c "import flask, streamlit, sklearn, pandas, joblib; print('OK')"
```

---

### 5. Запуск API (Flask)

API использует заранее обученные и сохранённые модели и **не обучает их заново**.

Запуск API:

```bash
python api_app.py
```

По умолчанию API доступно по адресу:

```
http://127.0.0.1:8000
```

Проверка состояния API:

```bash
curl http://127.0.0.1:8000/health
```

Ожидаемый ответ:

```json
{"status": "ok"}
```

---

### 6. Запуск пользовательского приложения (Streamlit)

Streamlit-приложение работает **через API**, поэтому API должно быть запущено **в отдельном терминале**.

В новом терминале (с активированным `venv`) выполните:

```bash
streamlit run ui_app.py
```

По умолчанию приложение открывается по адресу:

```
http://localhost:8501
```

---

### 7. Структура проекта

```
transaction_risk_system/
│
├── api_app.py                # Flask API
├── ui_app.py                 # Streamlit интерфейс
├── requirements.txt          # Зависимости
├── README.md                 # Документация
│
├── models/                   # Сохранённые модели и артефакты
│   ├── best_model_risk.joblib
│   ├── best_model_complexity.joblib
│   ├── forecast_total_volume.joblib
│   └── forecast_total_volume_history.csv
│
├── notebooks/                # Jupyter-ноутбуки (обучение и анализ)
├── docs/                     # Дополнительная документация
└── venv/                     # Виртуальное окружение
```

---

### 8. Краткий сценарий запуска

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api_app.py
# в новом терминале
streamlit run ui_app.py
```

---

Проект готов к использованию и демонстрации.

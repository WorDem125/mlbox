# Развёртывание окружения и установка библиотек  
**macOS / Windows**

Данная инструкция описывает полный процесс подготовки рабочего окружения:
создание виртуального окружения, установка библиотек и проверка готовности проекта.

---

## 1. Проверка Python

Перед началом убедитесь, что Python установлен.

### macOS
bash
python3 --version

** Windows (PowerShell или cmd) **

python --version


### Переход в папку проекта

# macOS

cd ~/Desktop/transaction_risk_system

# Windows

# Создание виртуального окружения (venv)

*** macOS ***

python3 -m venv venv

*** Windows ***

python -m venv venv

# Активация виртуального окружения

**macOS**
source venv/bin/activate

**Windows (PowerShell)**
.\venv\Scripts\Activate.ps1

**Windows (cmd)**
venv\Scripts\activate.bat

# Установка билиотек
**MAC**

**python3 -m pip install --upgrade pip**
PC

python -m pip install --upgrade pip

MAC

python3 -m pip install --upgrade setuptools wheel

PC

python -m pip install --upgrade setuptools wheel
MAC

pip install -r requirements.txt
PC

pip install -r requirements.txt

python -c "import numpy, pandas, sklearn; print('OK')"



 # Если PowerShell блокирует активацию (Windows)
 Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser


*** Обновление pip***
python -m pip install --upgrade pip
python -m pip install --upgrade pip setuptools wheel
*** Установка библиотек из requirements.txt ***
pip install -r requirements.txt

**Проверка корректности установки**
python -c "import numpy, pandas, sklearn, sqlalchemy, streamlit, flask, fastapi; print('OK')"

**Запуск проекта**

python app.py
streamlit run dashboard.py

 **Выход из виртуального окружения**
 deactivate


*** Самый быстрый и правильный фикс (macOS)***

deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip certifi
pip install -r requirements.txt
 или
python -m pip install --upgrade --force-reinstall certifi
pip install -r requirements.txt


**Фикс ошибки TLS / certifi на Windows**
deactivate
Remove-Item -Recurse -Force venv
rmdir /s /q venv
python -m venv venv
.\venv\Scripts\Activate.ps1
venv\Scripts\activate.bat
python -m pip install --upgrade pip certifi
pip install -r requirements.txt







Фикс ошибки TLS / certifi на Windows (pip, HTTPS, SSL)

Иногда на Windows при установке библиотек возникает ошибка, связанная с TLS/SSL сертификатами (certifi, pip). Решение — полная пересборка виртуального окружения.
	1.	Выйти из виртуального окружения (если оно активно):
deactivate
	2.	Полностью удалить старое виртуальное окружение.

Для PowerShell:
Remove-Item -Recurse -Force venv

Если PowerShell не сработал, через CMD:
rmdir /s /q venv
	3.	Создать новое виртуальное окружение:
python -m venv venv
	4.	Активировать виртуальное окружение.

PowerShell:
.\venv\Scripts\Activate.ps1

CMD:
venv\Scripts\activate.bat

После активации в терминале должно появиться (venv).
	5.	Обновить pip и certifi (обязательный шаг):
python -m pip install –upgrade pip certifi
	6.	Установить зависимости проекта:
pip install -r requirements.txt

Если PowerShell блокирует активацию виртуального окружения, выполнить один раз:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

После этого закрыть PowerShell, открыть заново и снова активировать venv.
**Если PowerShell блокирует активацию**
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Подготовка к демоэкзамену

## Настройка окружения

### Создайте виртуальное окружение

**Windows**

```powershell
python -m venv venv
```

**Linux**

```sh
python3 -m venv venv
```

### Активируйте его

**Windows**

```powershell
venv\Scripts\activate
```

**MacOS / Linux**

```sh
source venv/bin/activate
```

### Установите зависимости

```sh
pip install -r requirements.txt
```

### Запустите сервер

```sh
fastapi dev main.py
```
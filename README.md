# Измеритель скорости интернета

CLI команда для замера скорости интернета.
**Последовательно** запускает определенное количество запросов к заданному url и замеряет скорость в Мб/с,
а также среднее время запроса и объем скачанных данных.

## Quick Start

1. **Клонировать репозиторий**

```shell
git clone https://github.com/M4kar0vAl/speed-tester.git
```

2. **Перейти в директорию проекта**

```shell
cd speed-tester
```

### Для `uv`:

3. **Выполнить команду проверки скорости**

```shell
uv run python -m speed_tester <url>
```

**Просмотр доступных опций:**
```shell
uv run python -m speed_tester --help
```

### Для `pip`:

3. **Создать виртуальное окружение**

```shell
python -m venv .venv
```

4. **Активировать виртуальное окружение**

**Для Windows:**
```shell
.venv\Scripts\activate
```

**Для Linux / MacOS:**
```shell
source venv/bin/activate
```

5. **Установить зависимости**

```shell
pip install httpx==0.28.1 typer==0.27.2 rich==15.0.0
```

6. **Перейти в `src`**

```shell
cd src
```

7. **Выполнить команду проверки скорости**

```shell
python -m speed_tester <url>
```

**Просмотр доступных опций:**
```shell
python -m speed_tester --help
```

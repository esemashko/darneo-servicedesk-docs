# Darneo ServiceDesk Docs

Заготовка пользовательской документации Darneo ServiceDesk.

Документация рассчитана на конечного пользователя: оператора, сотрудника поддержки, руководителя группы или другого человека, который работает в интерфейсе модуля.

## Локальный просмотр

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Открыть в браузере:

```text
http://127.0.0.1:8000
```

## Проверка сборки

```bash
mkdocs build --strict
```

## Публикация

После push в `main` сайт можно публиковать через GitHub Pages. Workflow уже лежит в `.github/workflows/pages.yml`.

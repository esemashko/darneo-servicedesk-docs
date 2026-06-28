# Darneo ServiceDesk Docs

Документация для модуля Darneo ServiceDesk.

Проект собран на [MkDocs Material](https://squidfunk.github.io/mkdocs-material/): пишем обычные Markdown-файлы в `docs/`, а GitHub Pages собирает из них сайт.

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

После запуска документация будет доступна по адресу:

```text
http://127.0.0.1:8000
```

## Сборка

```bash
mkdocs build --strict
```

## Публикация на GitHub Pages

В репозитории уже добавлен workflow `.github/workflows/pages.yml`.

Чтобы сайт начал публиковаться:

1. Залейте ветку `main` на GitHub.
2. Откройте `Settings -> Pages`.
3. В поле `Build and deployment` выберите `GitHub Actions`.
4. Запустите workflow `Deploy documentation` или дождитесь следующего push в `main`.

Адрес сайта после публикации:

```text
https://esemashko.github.io/darneo-servicedesk-docs/
```

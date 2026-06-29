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

## Скриншоты для документации

Скриншоты разделов обслуживания генерируются из локального Storybook фронтенда:

```bash
cd ../app
yarn build-storybook

cd ../darneo-servicedesk-docs
python tools/generate-maintenance-screenshots.py
```

Скрипт сохраняет только нужные фрагменты интерфейса в
`docs/assets/screenshots/settings/maintenance/`.

## Публикация

Перед первым запуском нужно включить GitHub Pages в настройках репозитория:

1. Откройте `Settings -> Pages`.
2. В блоке `Build and deployment` выберите `Source: GitHub Actions`.
3. Сохраните настройку.
4. После этого запустите workflow `Deploy documentation` или сделайте push в `main`.

Workflow уже лежит в `.github/workflows/pages.yml`.

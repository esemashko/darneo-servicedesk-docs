# Обзор архитектуры

Модуль состоит из фронтенда, backend-слоя Bitrix и update-пакетов.

## Основные части

| Часть | Где находится | За что отвечает |
| --- | --- | --- |
| Фронтенд | `app/` | Vue-интерфейс |
| Backend | `bitrix/modules/darneo.servicedesk/` | API, сервисы, ORM, агенты |
| Обновления | `iupdate/` | Файлы поставки |

## Поток запроса

```mermaid
sequenceDiagram
    participant UI as Vue UI
    participant API as Bitrix AJAX
    participant Service as Service layer
    participant DB as MySQL

    UI->>API: action=darneo:servicedesk.*
    API->>Service: проверка и бизнес-логика
    Service->>DB: чтение или запись
    DB-->>Service: результат
    Service-->>API: данные
    API-->>UI: JSON-ответ
```

## Правило для новых функций

Новая функция должна иметь:

- понятный пользовательский сценарий;
- backend-контракт;
- проверку прав;
- тесты по нужному слою;
- описание в документации, если функция видна пользователю или администратору.

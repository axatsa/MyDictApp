# MyDict Widget — macOS & Windows

Красивый Electron виджет для быстрого доступа к словам из MyDict на Desktop.

**Важно:** Это отдельное приложение, которое работает на Mac/Windows локально и подключается к API серверу.

## 📦 Установка зависимостей

```bash
cd electron-widget
npm install
```

## 🚀 Разработка

```bash
npm start
```

## 🔨 Сборка для распространения

### macOS только
```bash
npm run build:mac
# Результат: dist/MyDict Widget.dmg и dist/MyDict Widget.zip
```

### Windows только
```bash
npm run build:win
# Результат: dist/MyDict Widget.exe и dist/MyDict Widget.msi
```

### Mac + Windows
```bash
npm run build:all
# Результат: оба варианта
```

Скомпилированные файлы будут в папке `dist/`

## 📤 Распространение

⚠️ **Скомпилированные файлы (`.app`, `.exe`, `.dmg`, `.msi`) НЕ коммитим в git!**

Вместо этого:
1. Собираешь локально: `npm run build:all`
2. Загружаешь в GitHub Releases
3. Пользователи скачивают оттуда

Исходный код (маленький) остается в репозитории.

## ⚙️ Конфигурация API

Отредактируй `widget.js` и измени `API_BASE_URL`:

```javascript
const API_BASE_URL = 'http://localhost:8000'; // локально
// или
const API_BASE_URL = 'https://mydict.example.com'; // на продакшене
```

## 🎨 Особенности

- ✨ Как основной сайт — красивый дизайн с цветными фонами
- 🎲 Случайные слова с бэкенда
- 🌍 Выбор языка: EN, UZ, KR
- ⌨️ Space/Enter для следующего слова
- 📊 Счетчик слов из базы

## 📝 Как использовать

1. Собери приложение: `npm run build:all`
2. Установи на Mac/Windows
3. Убедись что API доступен (по умолчанию localhost:8000)
4. Запусти, выбери язык, нажимай на слово для новых слов

## 🐛 Debug

Раскомментируй в `main.js`:
```javascript
mainWindow.webDevTools.openDevTools();
```

## 📊 Размер на сервере

- Исходный код: ~50 KB (коммитим)
- node_modules: ~300 MB (в .gitignore)
- dist/: (в .gitignore, не коммитим)
- **Total в git: минимум**

# TradingViewCorrelations 📊 — Сбор корреляций криптовалют с BTC

Автоматически собирает **корреляции криптовалют с биткоином** на [TradingView](https://www.tradingview.com/).
Он проходит по всем тикерам, получает значение корреляции с BTC и сохраняет результат в текстовый и Excel-файл.

> ⚡ **Корреляция** показывает, насколько сильно движение актива повторяет движение BTC.
> - `1` → движутся одинаково 
> - `-1` → движутся в противоположные стороны 
> - `0` → движения не связаны  

---

## Технологии

- **Python:** 3.12.3
- **Docker:** для запуска проекта в контейнере
- **Библиотеки:**  
`botasaurus` — парсер TradingView  
`requests` — отправка HTTP-запросов  
`InquirerPy` — меню в терминале  
`rich` — оформление вывода  

---

## 🚀 Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/pp112/TradingView_Correlations.git
cd TradingView_Correlations/
```

### 2. Сборка Docker-образа
```bash
docker compose build
```

### 3. Запуск контейнера
#### Bash (Linux / macOS)
```bash
docker compose run --rm tradingview_corrs
```

#### Windows (PowerShell)
```powershell
docker run -it -v "${PWD}/results:/app/results" -v "${PWD}/output:/app/output" tradingview_corrs
```

#### Windows (cmd)
```cmd
docker run -it -v "%cd%\results:/app/results" -v "%cd%\output:/app/output" tradingview_corrs
```

**Примечания:**

- Директории `results` и `output` создаются автоматически.
- В `results` появятся файлы с результатами:  
  `Корреляция_дд.мм.гг_чч-мм.xlsx`  
  `Корреляция_дд.мм.гг_чч-мм.txt`
- В `output` могут появляться скриншоты капчи, если TradingView потребует авторизацию. Если капчи нет — папка останется пустой.

---

## ✅ Пример результата

### TXT
BTCUSDT.P: 1.00  
ETHUSDT.P: 0.87  
XRPUSDT.P: 0.45  


### Excel
| Тикер     | Корреляция |
| --------- | ---------- |
| BTCUSDT.P | 1.00       |
| ETHUSDT.P | 0.87       |
| XRPUSDT.P | 0.45       |


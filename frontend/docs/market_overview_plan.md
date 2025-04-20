
# MarketOverview Angular Page – Full Functional Plan

## 1. UI - Pagina `MarketOverviewComponent`

### 1.1. Sidebar cu filtre interdependente
- Filtrare după:
  - Țară (din `exchanges.json`)
  - Bursă (din `exchanges.json`)
  - Sector, Industry Group, Industry, Sub-Industry (din `gics.json`)
  - Interval de timp (1d, 1w, 1m, YTD)
- Se folosește `Reactive Forms` + `Angular Material`
- Fiecare selecție actualizează dinamic următorul filtru

### 1.2. Harta Mondială Interactivă (GeoJSON + D3.js)
- Colorează țările după media variației simbolurilor pe bursele lor:
  - Verde: creștere
  - Roșu: scădere
  - Gri: lipsă date
- Tooltip:
  - Media % schimb
  - Top companii
- Click pe țară => filtrează restul componentelor

### 1.3. Vizualizări statistice
- Carduri agregate:
  - Media creștere
  - Volum total
  - Număr simboluri
  - Top 5 gainers/losers
- Grafice:
  - Pie chart pe sector
  - Bar chart variație pe industrie
  - Line chart cu evoluție medie în timp

### 1.4. Tabel cu simboluri
- Coloane:
  - Simbol, Nume, Țară, Bursă, Preț, % schimb, Volum
- Selectabil (checkbox)
- Buton „Exportă JSON” pentru salvare simboluri curente

### 1.5. Buton „Testează strategie”
- Trimite `.json` cu simbolurile selectate la backend
- Pagina nouă `/strategy-testing` permite alegerea unei strategii
- Rulează backtest și returnează grafice PnL

## 2. Backend FastAPI - Extensii

### 2.1. Endpointuri noi:
- `GET /filters/sectors`
- `GET /filters/countries`
- `GET /filters/exchanges?country=XX`
- `GET /instruments/filter?...`
- `GET /instruments/summary?symbols=...`
- `GET /yf/top-companies/{country}`
- `POST /export/json` – generează `.json` cu simboluri
- `POST /backtest/upload` – trimite fișier pentru test strategie

## 3. Structură Modulară Angular

```
app/
  market-overview/
    market-overview.component.ts
    filters/
      filter-form.component.ts
    charts/
      country-map.component.ts
      sector-pie.component.ts
      industry-bar.component.ts
      trend-line.component.ts
    cards/
      performance-cards.component.ts
    tables/
      instrument-table.component.ts
    export/
      export-selected.component.ts
```

## 4. Bonus Features (Dezvoltate Extins)

### 4.1. Export as Watchlist
- Salvează `.json` care poate fi importat în strategii live trading

### 4.2. Live Auto-Refresh
- Pagină se actualizează automat la fiecare 5 minute pentru bursele deschise

### 4.3. Map Drilldown
- Harta permite zoom și afișează burse / companii în detaliu

### 4.4. Heatmap Sectorial
- Vizualizare cu pătrate (sector → industrie → companie)
- Colorează în funcție de variație sau volum

## 5. Tehnologii Cheie

- Angular 19 + Material + RxJS
- D3.js + GeoJSON
- FastAPI backend + yfinance + FinanceDatabase
- Local JSON/CSV pentru caching date

## 6. Indicatori Tehnici și Indicatori Custom (AI-powered)

### 6.1. Indicatori Tehnici Clasici
- Calculați cu pandas-ta, ta-lib, finta etc.
- Agregați într-un scor tehnic sintetic

### 6.2. Indicatori Personalizați – Analiză AI
- Analiză pe baza datelor de la `/yf/finances` etc.
- Return JSON:
```json
{
  "symbol": "AAPL",
  "rank": 2,
  "score": 87,
  "recommendation": "buy"
}
```

### 6.3. Utilizare ulterioară
- Backtesting
- Strategii live trading

## 7. Suport pentru Indicatori Custom-Made

### 7.1. Tipuri
- Politici, strategii companie, oportunități externe

### 7.2. Structură
```json
{
  "symbol": "TSLA",
  "indicator_name": "Political Stability Score",
  "value": 72,
  "scale": "0-100",
  "description": "Based on recent elections and regulatory changes."
}
```

## 8. Evaluare Completă Multi-Factorială

### 8.1. Sute de indicatori prin:
- ta-lib, pandas-ta, finta, btalib, vectorbt

### 8.2. Evaluare Globală Simbol
```json
{
  "symbol": "MSFT",
  "score_technical": 91,
  "score_fundamental": 84,
  "score_sentiment": 70,
  "score_custom": 80,
  "overall_recommendation": "buy"
}
```

### 8.3. Dashboard avansat

### 8.4. AI Adaptive Score

### 8.5. Backtesting Multi-Factor

### 8.6. Semnale + Alerte

### 8.7. Performanță: cache + async update

## 9. Symbol Detail Component

### 9.1. Funcții:
- Toți indicatorii, grafice, heatmap, scor AI

### 9.2. Structură UI:
```
symbol-detail/
  header-summary/
  indicators-table/
  ai-analysis-panel/
  chart-view/
  live-connection-toggle/
```

### 9.3. Endpointuri:
- `/symbol/indicators/{symbol}`
- `/symbol/ai-evaluation/{symbol}`
- `/symbol/live/{symbol}`


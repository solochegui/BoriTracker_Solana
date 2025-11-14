📝 README.md para BoriTracker V6.5
# 🤖 BoriTracker V6.5 - Bot de Trading Cuantitativo de Frecuencia Dual

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Dependencies](https://img.shields.io/badge/Dependencies-Pandas%2C%20Numpy%2C%20Requests-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Version](https://img.shields.io/badge/Version-V6.5-red)

BoriTracker es una herramienta de trading algorítmico diseñada para monitorear y ejecutar estrategias de inversión en criptomonedas con un enfoque especial en el ecosistema de **Solana** (incluyendo BoriCoin, **BRCN**) y activos de alta capitalización. Utiliza un sistema de **frecuencia dual** para el monitoreo en tiempo real y la ejecución de la lógica de trading, ofreciendo un análisis detallado de PnL, Alpha y Drawdown.

---

## ✨ Características Principales de la V6.5

* **Frecuencia Dual:** Actualización de la **visualización en tiempo real** (0.1s) y ejecución de la **lógica de trading/API** en un intervalo seguro y definido (`TICK_INTERVAL_SECONDS`).
* **Estrategia RSI Adaptativa:** Ejecuta señales de compra en condiciones de **sobreventa** (RSI < 25) y venta/cierre en **sobrecompra** (RSI > 75).
* **Gestión de Riesgo Integrada:** Implementa órdenes de **Stop Loss (SL)** y **Take Profit (TP)** automáticas.
* **Monitoreo del Ecosistema Solana:** Incluye activos clave como **SOL, JUP, PYTH** y monitorea el rendimiento de **BoriCoin (BRCN)**.
* **Reporte de Analítica Avanzada:** Genera un reporte final detallado con **PnL Neto Cerrado**, desglose de comisiones, Alpha (rendimiento vs. índice) y métricas de riesgo como Drawdown y Sharpe Ratio.
* **Modo SIMULACIÓN/LIVE:** Permite practicar con capital ficticio y datos reales, o cambiar a `LIVE TRADING` para ejecutar órdenes reales (requiere integración con exchange, actualmente simulada).

---

## 🛠️ Instalación y Requerimientos

El BoriTracker requiere Python 3.x y las siguientes librerías:

### 1. Requerimientos de Python

Instala las dependencias usando `pip`:

```bash
pip install pandas numpy requests matplotlib

2. Configuración de la API (Datos)
El bot utiliza la API pública de CoinGecko para obtener precios en tiempo real. No se requiere API Key para el modo de precios simples, pero está diseñado para que la LiveFetcher maneje la integración.
3. Ejecución
 * Clona el repositorio:
   git clone [https://github.com/solochegui/Trading_Bot.git](https://github.com/solochegui/Trading_Bot.git)
cd Trading_Bot

 * Ejecuta el script:
   python Bori_tracker.py

 * El bot te preguntará si deseas iniciar en modo SIMULACIÓN (recomendado para pruebas) o LIVE TRADING.
⚙️ Configuración del Bot (Parámetros Clave)
Los parámetros de configuración se encuentran centralizados en la clase BotConfiguration dentro de Bori_tracker.py. Modifica los siguientes valores para ajustar tu estrategia:
| Parámetro | Descripción | Valor Predeterminado |
|---|---|---|
| INITIAL_USDC_BALANCE | Capital de inicio para la simulación. | 1000.00 |
| TICK_INTERVAL_SECONDS | Frecuencia de la lógica de trading y llamadas API. | 4.8 |
| RSI_PERIOD | Período del Indicador RSI. | 5 |
| RSI_BUY_THRESHOLD | Nivel de RSI para señal de COMPRA (sobreventa). | 25 |
| RSI_SELL_THRESHOLD | Nivel de RSI para señal de VENTA (sobrecompra). | 75 |
| STOP_LOSS_PCT | Porcentaje de Stop Loss automático. | 0.03 (3.0%) |
| TAKE_PROFIT_PCT | Porcentaje de Take Profit automático. | 0.15 (15.0%) |
| ASSETS_TO_TRACK | Lista de tickers a monitorear. | 30 activos |
📈 La Estrategia de Inversión
Este bot implementa una estrategia de "Reversión a la Media Extrema" utilizando el Índice de Fuerza Relativa (RSI).
 * Compra: Ejecutada cuando el RSI es extremadamente bajo (sobreventa) en un intento de capturar un rebote del precio.
 * Venta: Activada por Take Profit (asegurar una ganancia del 15%) o Stop Loss (limitar la pérdida al 3%).
 * Consejo de Chegui: Recuerda que la estrategia más útil es el Trading con Órdenes Limitadas. Este bot te ayuda a identificar el momento ideal para colocar esas órdenes en plataformas como Coinbase Advanced, Binance o Kraken.
📧 Colaboración y Contacto
Soy Chegui, el creador de Non Fungible Metaverse y colaborador de BoriCoin.
Si deseas contribuir a mejorar este bot, reportar un bug o discutir estrategias de inversión en Forex, criptomonedas o el mercado de valores, ¡no dudes en contactarme!
> ¡El éxito en el trading se basa en el control de riesgo y la disciplina!
> 

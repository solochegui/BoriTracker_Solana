```markdown
# 🚀 BoriTracker Solana — Demo Trading Bot (RSI)

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Issues](https://img.shields.io/github/issues/solochegui/BoriTracker_Solana)](https://github.com/solochegui/BoriTracker_Solana/issues)

BoriTracker Solana es un script demo en Python que simula un trading bot en vivo orientado a activos del ecosistema Solana (por ejemplo, BoriCoin / BRCN simulado) y otros tokens listados en plataformas como Coinbase. El bot usa un enfoque de Mean Reversion basado en RSI y cuenta con gestión de riesgo (SL / TP), dashboard en terminal y controles manuales para simular intervención humana.

---

## 🧭 Tabla de contenidos
- [Características](#-características)
- [Visión general](#-visión-general)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso (ejecución)](#-uso-ejecución)
- [Controles en vivo](#-controles-en-vivo)
- [Estrategia & gestión de riesgo](#-estrategia--gestión-de-riesgo)
- [Reporte final y métricas](#-reporte-final-y-métricas)
- [Cómo integrar una API real (Coinbase)](#-cómo-integrar-una-api-real-coinbase)
- [Roadmap / Próximos pasos](#-roadmap--próximos-pasos)
- [Contribuir](#-contribuir)
- [Seguridad y manejo de credenciales](#-seguridad-y-manejo-de-credenciales)
- [Licencia & Agradecimientos](#-licencia--agradecimientos)
- [Contacto](#-contacto)

---

## ✨ Características
- Simulación en tiempo real con dashboard en terminal (colores).
- Indicador técnico RSI (14 periodos) para señales de compra/venta.
- Gestión automática de riesgo: Stop Loss (SL) y Take Profit (TP).
- Controles manuales (compra/venta/stop) durante la ejecución.
- Reporte final con métricas clave (PnL, drawdown, Sharpe, Sortino).
- Diseño modular: fácil intercambio de la fuente de datos (`LiveFetcher`) por una API real.

---

## 🧠 Visión general
El bot está diseñado como demo educativo y de prototipado. No es un sistema para operar con fondos reales sin pruebas extensivas y controles adicionales. Permite experimentar con:
- Estrategias basadas en RSI.
- Reglas SL/TP.
- Simulación de múltiples activos en paralelo.
- Visualización rápida en terminal.

---

## ⚙️ Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/solochegui/BoriTracker_Solana.git
cd BoriTracker_Solana
```

2. Crea y activa un entorno virtual (recomendado):
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

3. Instala dependencias:
```bash
pip install -r requirements.txt
```

Ejemplo mínimo de `requirements.txt`:
```
pandas
numpy
matplotlib
colorama
tabulate
requests
```

---

## 🔧 Configuración

- Archivo principal: `Bori_tracker.py`
- Clase para reemplazar en producción: `LiveFetcher` — actualmente simula datos. Reemplázala por integración real a Coinbase (ver sección más abajo).
- Parámetros ajustables (en `BotConfiguration` o al inicio del script):
  - Capital inicial
  - Umbrales RSI (compra/venta)
  - Stop Loss (SL) y Take Profit (TP)
  - Intervalo / tick (por defecto 5s)

Variables de entorno recomendadas para credenciales/alertas:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

No introduzcas tokens en el código ni los subas al repo.

Puedes crear un `.env` local (no commiteado) o exportar las variables:
```bash
export TELEGRAM_BOT_TOKEN="xxx"
export TELEGRAM_CHAT_ID="yyy"
```

Si compartes screenshots o logs, revoca cualquier token usado en pruebas.

---

## ▶️ Uso (ejecución)

Guarda el script como `Bori_tracker.py` (ya incluido) y ejecuta:
```bash
python Bori_tracker.py
```

El dashboard se actualizará cada N segundos (según tu configuración). Al finalizar con `q`, el bot cerrará posiciones abiertas y generará el reporte final.

---

## ⌨️ Controles en vivo

Mientras el bot corre, puedes usar las teclas:
| Tecla | Acción | Descripción |
|---:|---|---|
| c | COMPRA MANUAL | Forzar compra al activo más sobrevendido (RSI bajo). |
| v | VENTA MANUAL | Forzar venta de la posición abierta con mejor candidato para cerrar. |
| q | DETENER SIMULACIÓN | Detiene la simulación y genera el reporte final. |

---

## 📈 Estrategia & gestión de riesgo

Estrategia (RSI 14):
- Señal de COMPRA: RSI < 25 (sobrevendido).
- Señal de VENTA: RSI > 75 (sobrecomprado).

Gestión de Riesgo:
- Stop Loss: venta automática si precio baja X% (p. ej. 3%).
- Take Profit: venta automática si precio sube Y% (p. ej. 15%).

Ajusta umbrales en `BotConfiguration`.

---

## 📊 Reporte final (métricas explicadas)
Al terminar la simulación se genera un reporte con:

- Rendimiento Neto (PnL): ganancia o pérdida neta (%) sobre capital inicial.
- Drawdown Máximo: mayor caída desde un pico hasta un valle.
- Sharpe Ratio: rendimiento medio ajustado por volatilidad.
- Sortino Ratio: similar al Sharpe pero sólo considera volatilidad negativa.
- Win Rate: % operaciones ganadoras.
- Avg. Risk/Reward: relación promedio entre ganancias y pérdidas en trades.

Estas métricas ayudan a evaluar rendimiento y riesgo de la estrategia.

---

## 🔁 Cómo integrar una API real (Coinbase / proveedor de mercado)

1. Identifica el endpoint de precios en tiempo real (Coinbase Advanced / Market Data).
2. Reemplaza `LiveFetcher.fetch_latest_prices()` por una implementación real:
   - Autenticación segura: usa variables de entorno o vaults (no commitees claves).
   - Maneja rate limits (429) y backoff exponencial.
   - Normaliza la estructura de datos para que el resto del bot no cambie.

Ejemplo conceptual (pseudocódigo):
```python
class LiveFetcher:
    def __init__(self, api_key, api_secret, base_url):
        ...
    def fetch_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        # Llamar a la API del exchange y devolver {symbol: price}
        ...
```

Asegúrate de testear en entorno sandbox / paper trading antes de operar en real.

---

## 🛠️ Roadmap / Próximos pasos
- [ ] Integración real con Coinbase o proveedor de market data.
- [ ] Módulo de backtesting para validar la estrategia con históricos.
- [ ] Soporte multi-exchange y ejecución real (paper trading).
- [ ] Añadir más estrategias (MACD, Bollinger, EMA, etc.).
- [ ] UI web ligera para visualización y control remoto.
- [ ] Tests unitarios y CI.

---

## 🤝 Contribuir
¡Contribuciones bienvenidas! Puedes:
- Abrir issues con ideas o bugs.
- Enviar PRs para features, fixes o mejoras de documentación.
- Seguir estas reglas básicas:
  - Código limpio y documentado.
  - Añadir tests cuando sea posible.
  - No incluir claves ni tokens en commits.

---

## 🔐 Seguridad y manejo de credenciales
- Nunca subas tokens/API keys al repositorio.
- Usa variables de entorno (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) o un gestor de secretos.
- Si por error expones una clave: revócala inmediatamente (BotFather / proveedor).
- Añade `.env` en `.gitignore` si usas archivos locales para variables.

Ejemplo `.gitignore`:
```
.env
.venv/
__pycache__/
```

Ejemplo `.env.example`:
```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
COINBASE_API_KEY=
COINBASE_API_SECRET=
```

---

## 🧾 Licencia & Agradecimientos
Este proyecto se publica bajo la licencia MIT.  
Desarrollado por **Soy Chegui (Solochegui)** — Non Fungible Metaverse.  
Gracias a la comunidad por la inspiración y feedback.

---

## ✉️ Contacto
- GitHub: https://github.com/solochegui
- Repo: https://github.com/solochegui/BoriTracker_Solana

---

> Nota final: este repositorio contiene una demo/ejemplo. No uses este bot para operar fondos reales sin implementar protección adicional, pruebas exhaustivas y auditoría de riesgos.
```

📄 README.md (Versión Decorada y Extendida con Manual)
# 🚀 BoriTracker V6.5: Estrategia de Acumulación DCA (Solana & Multi-Asset)

[![Strategy](https://img.shields.io/badge/Strategy-DCA%20Pure%20Accumulation-4D9AFA?style=flat&logo=bitcoin&logoColor=white)](https://es.wikipedia.org/wiki/Dollar_cost_averaging)
[![Assets](https://img.shields.io/badge/Assets-30%20Crypto%20Pairs%20%2B%20BRCN-FFA500?style=flat&logo=solana&logoColor=white)](https://boricoin.io/)
[![Built With](https://img.shields.io/badge/Built%20With-Python%20%7C%20Pandas%20%7C%20CoinGecko%20API-33CC33?style=flat&logo=python&logoColor=white)](#instalación-y-requerimientos)

## 💡 Introducción por Chegui, Creador de NFM

Hola, soy **Chegui**, creador de Non Fungible Metaverse y colaborador de BoriCoin.

Este proyecto, el **BoriTracker V6.5**, es el resultado de nuestra estrategia enfocada en la acumulación de valor. En lugar de especular a corto plazo, implementamos una rigurosa metodología de **Dólar Cost Averaging (DCA)**, buscando solo puntos de sobreventa extrema en el mercado para ejecutar órdenes de compra.

Creemos firmemente en el potencial de activos sólidos, especialmente los que residen en la red Solana, como **BoriCoin (BRCN)**, cuya confianza y éxito están respaldados por inversiones clave, como la de Flaco Flow (José Santana).

---

## ⚙️ Estrategia y Parámetros Clave (Modo DCA Puro)

El script está optimizado para funcionar con un capital inicial de **$1,000.00 USD**, distribuido entre 30 activos para una gestión de riesgo diversificada.

| Característica | Detalle Técnico | Valor/Umbral |
| :--- | :--- | :--- |
| **Objetivo** | Acumulación pura (Solo órdenes de Compra). | 🟢 **BUY ONLY** |
| **Señal de Entrada** | RSI (Relative Strength Index) en sobreventa extrema. | RSI $\le 15$ |
| **Sensibilidad RSI** | Periodo utilizado para el cálculo del RSI. | `5` períodos |
| **Velocidad de Lógica** | Frecuencia de chequeo de la API y ejecución de órdenes. | `12.0` segundos |
| **Visualización** | Interfaz actualizada con flechas (**▲/▼**) de tendencia. | `0.1` segundos |
| **Capital Base** | Capital de referencia para la simulación/operación. | `$1,000.00` |

---

## 🛠️ Instalación y Requerimientos

### 1. Requerimientos de Python

Asegúrate de tener Python 3.x y las siguientes bibliotecas instaladas en tu entorno.

```bash
# Instalar dependencias necesarias
pip install pandas numpy requests matplotlib

2. Estructura de Archivos
Asegúrate de que el archivo Bori_tracker.py y este README.md se encuentren en el mismo directorio.
3. Configuración Inicial (Crítica)
Antes de ejecutar, debes revisar y editar las siguientes líneas en el archivo Bori_tracker.py dentro de la clase BotConfiguration:
# LÍNEAS A REVISAR EN 'Bori_tracker.py'
self.INITIAL_USDC_BALANCE = 1000.00 
self.API_KEY = "TU_API_KEY_AQUI" 
self.API_SECRET = "TU_API_SECRET_AQUI"
# ... (asegúrate que el RSI_BUY_THRESHOLD esté en 15)

📖 Manual de Uso del BoriTracker
1. Inicio del Script
Ejecuta el script desde tu terminal:
python Bori_tracker.py

El programa te pedirá que elijas el modo:
| Opción | Modo | Descripción |
|---|---|---|
| 1 | SIMULACIÓN 🟢 | Recomendado para probar la estrategia. Utiliza datos de CoinGecko y datos simulados para BRCN. No hay riesgo. |
| 2 | LIVE TRADING 🔴 | Diseñado para operar con API Key real en un exchange. Requiere API Key real y conlleva riesgo financiero. |
2. Interpretación de la Interfaz en Vivo
La interfaz se actualiza constantemente para ofrecerte información clave:
A. Sección de Rendimiento y Fondos
 * 💰 PORTAFOLIO VALOR TOTAL: El valor actual de todos tus activos más el USDC restante.
 * 💵 INVERSIÓN TOTAL ACUMULADA: El capital real que ha sido gastado en compras de activos.
 * 💸 USDC RESTANTE: El capital que aún está disponible en caja para futuras compras DCA.
 * ⭐ ALPHA (Valor Agregado): Muestra si tu portafolio está superando al índice de mercado simulado.
B. Sección de Activos (Flechas Indicadoras)
La columna Precio (Tendencia) ofrece la retroalimentación inmediata solicitada:
| Símbolo | Color | Significado |
|---|---|---|
| ▲ (\u25b2) | Verde | El precio del activo subió desde el último chequeo. |
| ▼ (\u25bc) | Rojo | El precio del activo bajó desde el último chequeo. |
| ⬥ (\u25c6) | Amarillo | El precio del activo no tuvo cambio significativo. |
3. Detener y Reporte Final
Para finalizar la simulación o el trading:
 * Presiona Ctrl + C en la terminal.
 * El script se detendrá y generará el Reporte Final de Acumulación.
 * Este reporte incluirá:
   * Detalle bancario del capital invertido, comisiones y USDC disponible.
   * Métricas avanzadas (Sharpe Ratio, Max Drawdown).
   * Un Gráfico de la evolución del valor total de tu portafolio comparado con el Benchmark.
🤝 Contribución y Licencia
Este proyecto es una herramienta de inversión y educación. Si tienes mejoras o sugerencias para la estrategia DCA, ¡las contribuciones son bienvenidas!
Este proyecto se distribuye bajo la Licencia MIT.
Desarrollado por Chegui, creador de Non Fungible Metaverse.

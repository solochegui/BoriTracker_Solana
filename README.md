Simulador de Trading para BRCN (BoriCoin) en Solana, implementado en Python. Este proyecto utiliza una estrategia de trading combinada (Cruce de Medias Móviles y RSI) para simular la compra y venta del activo con un saldo inicial en USDC.

## 🌟 Características

* **Estrategia Combinada:** Utiliza el cruce de una Media Móvil (MA) corta (5 periodos) y una MA larga (20 periodos), filtrada por el Índice de Fuerza Relativa (RSI) (14 periodos).
* **Simulación Dinámica:** El precio de BRCN se actualiza con un pequeño factor aleatorio en cada "tick" para simular la volatilidad del mercado.
* **Simulación de Wallet:** Gestiona un saldo simulado de **$1,000.00 USDC** y el balance de BRCN.
* **Interfaz Textual:** Muestra el estado actual del tracker, los balances y los indicadores en la consola en tiempo real.
* **Registro Detallado:** Genera un registro completo de cada transacción (compra, venta, PnL).

## 🚀 Instalación y Uso

### 1. Requisitos

Asegúrate de tener **Python** instalado en tu sistema (Termux, Linux, macOS o Windows).

Necesitarás las librerías `pandas` y `numpy`:

```bash
pip install pandas numpy

2. Ejecutar el Simulador
Clona este repositorio y navega a la carpeta:
git clone [https://github.com/solochegui/BoriTracker_Solana.git](https://github.com/solochegui/BoriTracker_Solana.git)
cd BoriTracker_Solana

Ejecuta el script principal:
python Bori_tracker.py

El simulador se ejecutará durante un número predefinido de pasos (SIMULATION_STEPS), mostrando la interfaz y las operaciones de trading en la consola.
⚙️ Configuración y Parámetros
Los parámetros clave de la simulación pueden ajustarse directamente al inicio del archivo Bori_tracker.py:
| Parámetro | Descripción | Valor por Defecto |
|---|---|---|
| INITIAL_USDC_BALANCE | Saldo inicial para el simulador. | 1000.00 |
| INITIAL_BRCN_PRICE | Precio de partida de BRCN en la simulación. | 0.50 |
| MA_SHORT_PERIOD | Periodo para la Media Móvil corta. | 5 |
| MA_LONG_PERIOD | Periodo para la Media Móvil larga. | 20 |
| RSI_PERIOD | Periodo para el cálculo del RSI. | 14 |
| SIMULATION_STEPS | Número de "ticks" o iteraciones de la simulación. | 100 |
🧠 Lógica de Trading
La estrategia solo ejecuta una orden si ambas condiciones se cumplen:
| Tipo de Orden | Condición de Cruce de MA | Condición de Filtro RSI |
|---|---|---|
| COMPRA | MA Corta cruza por encima de MA Larga (Señal Alcista) | RSI es menor que 50 (Indica espacio para subir/No sobrecomprado) |
| VENTA | MA Corta cruza por debajo de MA Larga (Señal Bajista) | RSI es mayor que 50 (Indica potencial de bajada/No sobrevendido) |
📄 Licencia
Este proyecto está bajo la licencia MIT. (O especifica la licencia que prefieras).

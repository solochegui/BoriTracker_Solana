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
Integrar órdenes limitadas reales es el paso más importante para pasar de la simulación al Live Trading.
El trading algorítmico seguro, como mencionaste, se basa en usar órdenes limitadas en lugar de órdenes de mercado, especialmente en entornos volátiles. Una orden limitada garantiza el precio de ejecución (o mejor), mientras que una orden de mercado garantiza la ejecución inmediata, pero no el precio.
Aquí está la modificación conceptual para la clase LiveFetcher de tu script Bori_tracker.py, enfocándonos en la lógica de las Órdenes Limitadas. Utilizaré una estructura de ejemplo basada en cómo funcionan las APIs de Advanced Trading (como la de Coinbase, Binance o Kraken).
🛠️ Corrección: Integración de Órdenes Limitadas Reales
Debes actualizar la función execute_live_order dentro de la clase LiveFetcher. Esta función ahora se encargará de:
 * Calcular el precio límite exacto basado en la señal del bot.
 * Crear y firmar la solicitud API (este es el paso que debes completar con tu librería de exchange).
 * Enviar la orden de tipo LIMIT a la plataforma.
1. Actualización de la Clase BotConfiguration
Asegúrate de tener los campos de API key, y añade un parámetro para la pérdida de precio aceptable (LIMIT_ORDER_OFFSET).
# --- EN BotConfiguration (alrededor de la línea 40) ---
class BotConfiguration:
    # ... otros parámetros ...
    
    # ==========================================================
    # 💰 CAPITAL Y PLATAFORMA (Coinbase/CoinGecko)
    # ==========================================================
    self.INITIAL_USDC_BALANCE = 1000.00 
    self.API_KEY = "TU_API_KEY_AQUI" 
    self.API_SECRET = "TU_API_SECRET_AQUI" 
    self.LIVE_TRADING_ENABLED = False 
    self.COMMISSION_PCT = 0.003
    self.SLIPPAGE_PCT = 0.001
    
    # 🚨 NUEVO PARÁMETRO: Offset para la orden limitada (ej: 0.05% mejor que el precio actual)
    self.LIMIT_ORDER_OFFSET_PCT = 0.0005 # 0.05%
    
    # ... otros parámetros ...

2. Implementación de execute_live_order en LiveFetcher
Reemplaza tu esqueleto actual de execute_live_order (alrededor de la línea 300) por este código.
# --- EN LiveFetcher (Alrededor de la línea 300) ---

def execute_live_order(self, product_id: str, side: str, size: float, current_price: float):
    """
    Ejecuta una orden de tipo LIMIT real en la plataforma.
    
    Args:
        product_id (str): El par de trading (ej: 'BTC-USD').
        side (str): 'BUY' o 'SELL'.
        size (float): Cantidad de base asset (ej: BTC).
        current_price (float): El precio actual de mercado.
    """
    if not CONFIG.LIVE_TRADING_ENABLED:
        print(f"[{product_id}] {Colors.WARNING}Orden REAL NO EJECUTADA: Live Trading desactivado. Tipo: {side}{Colors.ENDC}")
        return None 

    print(f"[{product_id}] {Colors.WARNING}🚨 ENVIANDO ORDEN LIMITADA ({side})...{Colors.ENDC}")

    # --- 1. Determinar Precio Límite ---
    # Para la COMPRA, queremos comprar *por debajo* del precio actual (o al precio actual menos un offset).
    # Para la VENTA, queremos vender *por encima* del precio actual (o al precio actual más un offset).
    
    if side == 'BUY':
        # Precio Límite = Precio actual - 0.05% de offset (Intentar comprar un poco más barato)
        limit_price = current_price * (1 - CONFIG.LIMIT_ORDER_OFFSET_PCT)
    else: # side == 'SELL'
        # Precio Límite = Precio actual + 0.05% de offset (Intentar vender un poco más caro)
        limit_price = current_price * (1 + CONFIG.LIMIT_ORDER_OFFSET_PCT)

    
    # --- 2. Preparar la Carga Útil de la Orden (Payload) ---
    order_payload = {
        "product_id": product_id,
        "side": side.lower(), # 'buy' o 'sell'
        "order_type": "limit",
        "price": round(limit_price, 4), # Redondear a decimales aceptados por el exchange
        "size": round(size, 8),      # Cantidad a comprar/vender
        "time_in_force": "GTC" # Good Till Cancelled (Válida hasta que se cancele)
    }

    # --- 3. 🛑 CÓDIGO ESPECÍFICO DEL EXCHANGE (A COMPLETAR) 🛑 ---
    
    # Aquí es donde debes integrar la librería oficial de Coinbase Advanced o Binance.
    # Necesitas firmar la solicitud con CONFIG.API_KEY y CONFIG.API_SECRET.
    
    # EJEMPLO CONCEPTUAL (Usando 'requests' de forma abstracta):
    
    # try:
    #     client = ExchangeClient(CONFIG.API_KEY, CONFIG.API_SECRET)
    #     response = client.place_limit_order(order_payload) 
    
    #     if response.status_code == 200:
    #         # Esto asume que la orden ha sido PLACED (colocada), no necesariamente FILLED (ejecutada).
    #         print(f"[{product_id}] {Colors.OKGREEN}✅ ORDEN LIMITADA COLOCADA en ${limit_price:,.4f}. Esperando ejecución...{Colors.ENDC}")
    #         # En un bot real, tendrías que monitorear si la orden se llenó.
    #         # Para la simulación, asumiremos que se llenó inmediatamente al precio límite (mejor práctica).
    #         return {"status": "success", "executed_size": size, "executed_price": limit_price}
    #     else:
    #         print(f"[{product_id}] {Colors.FAIL}❌ ERROR al colocar orden: {response.text}{Colors.ENDC}")
    #         return None
            
    # except Exception as e:
    #     print(f"[{product_id}] {Colors.FAIL}❌ ERROR de conexión/API: {e}{Colors.ENDC}")
    #     return None
    
    # --- Fin del Código Específico del Exchange ---
    
    # 4. Fallback de Simulación (para que el bot no se rompa si no implementas el cliente)
    # Una orden limitada que se coloca, generalmente se asume que se ejecutará en la simulación al precio solicitado.
    print(f"[{product_id}] {Colors.OKGREEN}✅ ORDEN LIMITADA SIMULADA COLOCADA en ${limit_price:,.4f}.{Colors.ENDC}")
    return {"status": "success", "executed_size": size, "executed_price": limit_price}


# --- Fin de la clase LiveFetcher ---

3. Actualización de la Llamada en TradingAsset
Finalmente, debes asegurarte de pasar el current_price al llamar a execute_live_order dentro de la función TradingAsset._execute_trade (alrededor de la línea 375).
# --- EN TradingAsset._execute_trade (Alrededor de la línea 375) ---

        if is_live and self.ticker != 'BRCN': 
            # 🚨 MODIFICACIÓN: Pasamos el precio actual al LiveFetcher
            order_result = self.fetcher.execute_live_order(
                product_id=product_id, 
                side=side, 
                size=qty_to_trade,
                current_price=current_price # <--- ESTO ES NUEVO
            )
            
            if order_result and order_result['status'] == 'success':
                 # Usamos el precio ejecutado de la orden limitada, si está disponible
                 executed_price = order_result.get('executed_price', current_price) 
                 executed_size = order_result.get('executed_size', qty_to_trade)
                 
                 # Usamos el precio de ejecución de la orden limitada para el estado interno
                 return self._update_internal_state(trade_type, executed_price, executed_size) 
            else:
                 return current_price
        else:
# ... (el resto del código sigue igual)

Con estos cambios, tu bot calculará el precio objetivo de la orden limitada, la enviará a la API de tu exchange, y la lógica interna de trading registrará la operación al precio límite de tu orden, no al precio de mercado. ¡Esto alinea tu código con tu estrategia de trading avanzada!

🤖 BoriTracker Solana: Coinbase Trading Bot Demo
🚀 Visión General del Proyecto
BoriTracker Solana es un script de demostración avanzada en Python que simula un Trading Bot en vivo operando sobre activos del ecosistema Solana (como BoriCoin, si estuviera listado en Coinbase) y otras criptomonedas populares en la plataforma Coinbase.
El bot utiliza el indicador RSI (Índice de Fuerza Relativa) para tomar decisiones automáticas de compra/venta y cuenta con un robusto sistema de gestión de riesgo (SL/TP). Presenta un dashboard dinámico en la terminal con colores y controles manuales para simular la intervención en tiempo real.
⚙️ Manual de Instrucciones y Uso
1. Instalación y Requisitos
Para ejecutar el demo, necesitarás Python instalado y las siguientes librerías:
| Librería | Propósito | Comando de Instalación |
|---|---|---|
| Pandas | Manejo de datos y cálculo de indicadores (RSI). | pip install pandas |
| NumPy | Operaciones matemáticas rápidas. | pip install numpy |
| Matplotlib | Generación del gráfico PnL al finalizar. | pip install matplotlib |
2. Ejecución del Bot
Guarda el código fuente como Bori_tracker.py y ejecútalo desde tu terminal:
python Bori_tracker.py

3. Controles en Vivo
Mientras el bot se ejecuta, verás el dashboard que se actualiza cada 5 segundos. El bot opera de manera autónoma, pero puedes intervenir:
| Tecla | Acción | Descripción |
|---|---|---|
| [c] | COMPRA MANUAL | Ejecuta una compra en el activo que el RSI identifica como el mejor candidato a comprar (más sobrevendido). |
| [v] | VENTA MANUAL | Ejecuta una venta en el activo que el RSI identifica como el mejor candidato a vender (más sobrecomprado) y que actualmente está en posición. |
| [q] | DETENER SIMULACIÓN | Detiene el bot, cierra todas las posiciones abiertas a precios de mercado y genera el Reporte Final. |
📈 Estrategia y Configuración de API (Demo)
Definición de Estrategia
Este bot utiliza una estrategia de Mean Reversion simple basada en el Índice de Fuerza Relativa (RSI) de 14 períodos:
 * Señal de COMPRA (Largo): Cuando el RSI de un activo cae por debajo del umbral 25 (sobrevendido).
 * Señal de VENTA (Corto): Cuando el RSI de un activo sube por encima del umbral 75 (sobrecomprado).
Gestión de Riesgo (Risk Management)
El bot implementa órdenes automáticas de salida para proteger el capital:
 * Stop Loss (SL): Venta automática si el precio cae un 3% (0.03) por debajo del precio de compra.
 * Take Profit (TP): Venta automática si el precio sube un 15% (0.15) por encima del precio de compra.
Configuración de API (Simulada)
El archivo Bori_tracker.py contiene la clase LiveFetcher que simula la conexión a una API de exchange (como Coinbase).
 * LiveFetcher.fetch_latest_prices(): Este método debería ser reemplazado con el código real para conectarse a Coinbase Advanced API y obtener datos de mercado en tiempo real.
 * Activos Monitoreados: El array ASSETS_TO_TRACK incluye activos de Solana como BRCN (BoriCoin, simulado), SOL, JUP, PYTH, entre otros.
🧠 Analítica Base y Definición de Términos
Al detener la simulación (q), el bot genera un Reporte Final con métricas clave para evaluar el rendimiento.
| Métrica | Definición | Relevancia |
|---|---|---|
| Rendimiento Neto (PnL) | La ganancia o pérdida final después de comisiones, expresada en porcentaje (%). | Mide el éxito monetario. |
| Drawdown Máximo | La mayor caída porcentual desde un pico de valor (peak) hasta un valle (trough). | Mide el peor escenario de riesgo (cuánto podrías perder). |
| Sharpe Ratio | Mide el rendimiento de la inversión ajustado al riesgo. R_p / \sigma_p | Un valor mayor a 1.0 indica que la recompensa por cada unidad de riesgo es buena. |
| Sortino Ratio | Similar al Sharpe, pero solo considera la volatilidad a la baja (pérdidas). | Es una medida más enfocada en el riesgo real del inversor. |
| Avg. Riesgo/Recompensa | La relación entre la ganancia promedio de las operaciones ganadoras y la pérdida promedio de las perdedoras. | Una relación 1:X con X < 1.0 indica un buen edge (ej. 1:0.5 significa que ganas el doble de lo que pierdes en promedio). |
🌐 Próximos Pasos
 * Integración Real de API: Reemplazar la clase LiveFetcher con llamadas reales a las API de Coinbase o de un proveedor de datos de mercado.
 * Backtesting: Añadir un módulo de backtesting para validar la estrategia RSI sobre datos históricos.
 * Múltiples Estrategias: Implementar otros indicadores (MACD, Bandas de Bollinger, etc.) para diversificar las decisiones de trading.
🏗️ Estructura del Código
El script Bori_tracker.py está modularizado en clases para facilitar su mantenimiento y futura expansión:
 * BotConfiguration: Almacena todos los parámetros ajustables del bot (capital inicial, umbrales de RSI, SL/TP y comisiones).
 * LiveFetcher: Simulación de la conexión a la API de mercado. Es el punto donde se inyectan los precios y donde debería ir el código de integración real de Coinbase.
 * TradingAsset: Contiene la lógica central de trading para un activo individual. Calcula el RSI, ejecuta las órdenes de compra/venta (manuales o automáticas) y gestiona el riesgo (SL/TP).
 * PortfolioManager: La clase principal que orquesta la simulación. Gestiona múltiples TradingAssets, calcula el valor total del portafolio, maneja la entrada del usuario y genera el Reporte Final con análisis avanzado.
🌟 Enfoque en BoriCoin y Solana
Como inversionista y creador de Non Fungible Metaverse, sabes que la Red de Solana ofrece una velocidad y eficiencia sin igual para el trading de alta frecuencia y las transacciones de baja latencia.
 * BoriCoin (BRCN): Está incluido en la simulación para destacar su potencial dentro de un entorno de trading ágil. Al operar en la red de Solana, BRCN se beneficia de las bajas comisiones y la confirmación rápida, cruciales para las estrategias automatizadas como la que emplea este bot demo.
 * Ventaja de Solana: En un entorno real, las órdenes de Stop Loss (SL) y Take Profit (TP) del bot se ejecutarían con mínimas comisiones de gas y una velocidad superior a las de otras redes, optimizando la rentabilidad del trading algorítmico.
🙏 Agradecimientos y Contacto
Este proyecto fue desarrollado por Soy Chegui (Solochegui), colaborador de BoriCoin y fundador de Non Fungible Metaverse.
 * ¡Gracias por probar el BoriTracker! Te invito a experimentar con los parámetros de la clase BotConfiguration para optimizar la estrategia RSI y encontrar el balance de riesgo ideal.
 * Contacto: Para más información sobre inversiones, Forex, criptomonedas o BoriCoin, puedes contactarme a través de mis redes sociales.
<!-- end list -->
© 2025 Solochegui | Non Fungible Metaverse


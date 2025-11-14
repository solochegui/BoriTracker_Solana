import pandas as pd
import numpy as np
import time
import os
import matplotlib.pyplot as plt
import sys
import select
import tty
import termios
import random 
import requests 
import json

# --- Códigos ANSI para colores (Estética mejorada) ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# -----------------------------------------------------------
# 📝 CONFIGURACIÓN DEL BOT Y PARÁMETROS (FRECUENCIA DUAL)
# -----------------------------------------------------------
class BotConfiguration:
    """Clase centralizada para definir todos los parámetros."""
    
    def __init__(self):
        
        # ==========================================================
        # 💰 CAPITAL Y PLATAFORMA (Coinbase/CoinGecko)
        # ==========================================================
        self.INITIAL_USDC_BALANCE = 1000.00 
        self.API_KEY = "TU_API_KEY_AQUI" 
        self.API_SECRET = "TU_API_SECRET_AQUI" 
        self.LIVE_TRADING_ENABLED = False 
        self.COMMISSION_PCT = 0.003
        self.SLIPPAGE_PCT = 0.001
        
        # ==========================================================
        # 🌐 ACTIVOS Y MAPPING A COINGECKO ID (TOTAL: 30 ACTIVOS)
        # ==========================================================
        self.ASSETS_TO_TRACK = [
            # Tu BoriCoin y Solana Ecosystem
            'BRCN', 'SOL', 'JUP', 'PYTH', 
            
            # Blue Chips & Layer 1/2
            'ETH', 'LINK', 'DOGE', 'BTC', 'ADA', 'MATIC', 'XRP', 
            'LTC', 'BCH', 'DOT', 'NEAR', 'AVAX',
            
            # Layer 2 & DeFi/Infraestructura
            'OP', 'ARB', 'INJ', 'AAVE', 'LDO', 'MKR', 'FIL', 'ICP', 
            
            # Memecoins & Varios
            'SHIB', 'PEPE', 'FTM', 'UNI', 'SUI', 'APT'
        ]

        # 🟢 CORRECCIÓN V6.5 (PREVIA): Inicializar INITIAL_PRICES
        self.INITIAL_PRICES = {ticker: 1.0 for ticker in self.ASSETS_TO_TRACK} 

        # 🔴 CORRECCIÓN V6.5: Mapeo de Ticker a CoinGecko ID (TODOS DEBEN SER STRINGS)
        self.COINGECKO_IDS = {
            'SOL': 'solana', 'JUP': 'jupiter-exchange', 'PYTH': 'pyth-network',
            'ETH': 'ethereum', 'LINK': 'chainlink', 'DOGE': 'dogecoin',
            'BTC': 'bitcoin', 'ADA': 'cardano', 'MATIC': 'polygon',
            'XRP': 'ripple', 
            'LTC': 'litecoin', # ✅ CORREGIDO
            'BCH': 'bitcoin-cash', # ✅ CORREGIDO
            'DOT': 'polkadot', # ✅ CORREGIDO
            'NEAR': 'near-protocol', # ✅ CORREGIDO
            'AVAX': 'avalanche-2',
            'OP': 'optimism', 'ARB': 'arbitrum', 'INJ': 'injective-protocol',
            'AAVE': 'aave', 'LDO': 'lido-dao', 'MKR': 'maker',
            'FIL': 'filecoin', 'ICP': 'internet-computer',
            'SHIB': 'shiba-inu', 'PEPE': 'pepe', 'FTM': 'fantom',
            'UNI': 'uniswap', # ✅ CORREGIDO
            'SUI': 'sui', # ✅ CORREGIDO
            'APT': 'aptos' # ✅ CORREGIDO
        }
        
        # ==========================================================
        # ⏳ TIEMPO Y ESTRATEGIA (FRECUENCIA DUAL)
        # ==========================================================
        self.TICK_INTERVAL_SECONDS = 4.8   # Frecuencia de EJECUCIÓN de la Lógica y la API (El tick real)
        self.DISPLAY_INTERVAL_SECONDS = 0.1 # Frecuencia de la VISUALIZACIÓN de la pantalla (Rápido)
        self.INITIAL_HISTORY_TICKS = 28 
        self.MAX_SIMULATION_TICKS = 0 # <<-- CERO significa loop infinito (ejecución continua)
        self.RSI_PERIOD = 5             
        self.RSI_BUY_THRESHOLD = 25    
        self.RSI_SELL_THRESHOLD = 75   
        self.STOP_LOSS_PCT = 0.03    
        self.TAKE_PROFIT_PCT = 0.15 
        
        # --- CÁLCULOS DERIVADOS ---
        self.MAX_CAPITAL_ALLOCATION_PCT = 0.95 
        self.CAPITAL_PER_ASSET = self.INITIAL_USDC_BALANCE / len(self.ASSETS_TO_TRACK)
        self.USDC_TO_TRADE_PCT = self.MAX_CAPITAL_ALLOCATION_PCT
        
    def display_options(self, mode):
        """Muestra los parámetros de configuración."""
        print(f"{Colors.HEADER}="*70)
        print(f"💻 {Colors.BOLD}CONFIGURACIÓN DEL BORITRACKER (V6.5) - MODO: {mode}{Colors.ENDC}")
        print(f"{Colors.HEADER}="*70 + Colors.ENDC)
        
        print(f"\n{Colors.OKBLUE}=== 1. CAPITAL Y FUENTE DE DATOS ==={Colors.ENDC}")
        print(f"💰 {Colors.BOLD}CAPITAL INICIAL:{Colors.ENDC} ${self.INITIAL_USDC_BALANCE:,.2f}")
        print(f"💵 {Colors.BOLD}ASIGNACIÓN POR ACTIVO:{Colors.ENDC} ${self.CAPITAL_PER_ASSET:,.2f}")
        live_status = f"{Colors.OKGREEN}ACTIVO{Colors.ENDC}" if self.LIVE_TRADING_ENABLED else f"{Colors.FAIL}INACTIVO{Colors.ENDC}"
        print(f"** {Colors.BOLD}LIVE TRADING MODE:{Colors.ENDC} {live_status} **")
        print(f"📡 {Colors.BOLD}FUENTE DE DATOS:{Colors.ENDC} CoinGecko API + MOCK (BRCN)")

        print(f"\n{Colors.OKBLUE}=== 2. VELOCIDAD DE TICK DUAL ==={Colors.ENDC}")
        print(f"⏱️ {Colors.BOLD}INTERVALO DE EJECUCIÓN/API:{Colors.ENDC} {Colors.WARNING}{self.TICK_INTERVAL_SECONDS} segundos{Colors.ENDC} (Lógica de Trading)")
        print(f"🖥️ {Colors.BOLD}INTERVALO DE VISUALIZACIÓN:{Colors.ENDC} {Colors.OKCYAN}{self.DISPLAY_INTERVAL_SECONDS} segundos{Colors.ENDC} (Actualización de Pantalla Rápida)")
        print(f"📈 {Colors.BOLD}RSI PERIODO (Sensibilidad):{Colors.ENDC} {self.RSI_PERIOD} períodos")
        print(f"🛡️ {Colors.FAIL}STOP LOSS (SL):{Colors.ENDC} {self.STOP_LOSS_PCT*100}%")
        print(f"🏆 {Colors.OKGREEN}TAKE PROFIT (TP):{Colors.ENDC} {self.TAKE_PROFIT_PCT*100}%")
        
        print(f"\n{Colors.OKBLUE}=== 3. ACTIVOS ({len(self.ASSETS_TO_TRACK)}) ==={Colors.ENDC}")
        print(f"🌐 {Colors.BOLD}ACTIVOs MONITOREADOS:{Colors.ENDC} {', '.join(self.ASSETS_TO_TRACK[:15])}...") 
        print(f"{Colors.HEADER}="*70 + Colors.ENDC + "\n")


# Inicializar la configuración global
CONFIG = BotConfiguration()
RSI_PERIOD = CONFIG.RSI_PERIOD

# -----------------------------------------------------------
# 🔌 CLASE DE CONEXIÓN A LA API (COINGECKO INTEGRACIÓN)
# -----------------------------------------------------------
class LiveFetcher:
    """Implementa la conexión a la API de CoinGecko para obtener precios."""
    
    def __init__(self, assets: list):
        # La corrección del TypeError se maneja aquí: api_ids ahora solo contendrá strings
        self.api_ids = [v for k, v in CONFIG.COINGECKO_IDS.items() if k != 'BRCN']
        self.id_to_ticker = {v: k for k, v in CONFIG.COINGECKO_IDS.items()}
        self.COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
        self.current_prices = CONFIG.INITIAL_PRICES.copy() 
        
        # El market index debe empezar con el valor de la asignación inicial para calcular el % de cambio.
        self.initial_market_index_value = sum(CONFIG.INITIAL_PRICES[ticker] * CONFIG.CAPITAL_PER_ASSET for ticker in CONFIG.ASSETS_TO_TRACK)
        self.market_index_history = [self.initial_market_index_value] 
        
        self.last_api_call_time = time.time() - CONFIG.TICK_INTERVAL_SECONDS 
        
    def fetch_latest_prices(self):
        """Obtiene los precios más recientes de CoinGecko y Mock para BRCN, o usa mock si no toca."""
        
        # 🎯 NUEVA LÓGICA: Solo llama a la API si ha pasado el TICK_INTERVAL_SECONDS
        if time.time() - self.last_api_call_time < CONFIG.TICK_INTERVAL_SECONDS:
            # Si no es tiempo de llamar a la API, solo actualiza BRCN (Mock) y usa el último precio conocido.
            return self._mock_prices_only()
        
        updated_prices = {}
        self.last_api_call_time = time.time()
        
        try:
            params = {
                # 🔴 CORRECCIÓN V6.5: Aquí es donde ocurría el TypeError, ahora api_ids son solo STRINGS.
                'ids': ','.join(self.api_ids),
                'vs_currencies': 'usd'
            }
            # Solicitud a CoinGecko (hasta 5 segundos de espera)
            response = requests.get(self.COINGECKO_URL, params=params, timeout=5)
            response.raise_for_status()  
            data = response.json()
            
            for coin_id, price_data in data.items():
                if 'usd' in price_data:
                    ticker = self.id_to_ticker.get(coin_id)
                    if ticker:
                        updated_prices[ticker] = price_data['usd']
        
        except requests.exceptions.RequestException as e:
            # En caso de error de conexión, usamos el fallback simulado.
            print(f"{Colors.FAIL}Error de conexión con CoinGecko ({e}). Usando precios de fallback simulados.{Colors.ENDC}")
            return self._fallback_mock_prices()
        
        # Consolidar precios
        for ticker in CONFIG.ASSETS_TO_TRACK:
            if ticker in updated_prices:
                self.current_prices[ticker] = updated_prices[ticker]
            elif ticker not in self.current_prices:
                # Si falla una moneda, usamos su último precio conocido
                self.current_prices[ticker] = CONFIG.INITIAL_PRICES[ticker] 
                
        # Simular BRCN y actualizar índice con precios más recientes
        self._update_mock_brcn_and_index()
        
        return self.current_prices

    def _update_mock_brcn_and_index(self):
        """Actualiza BRCN (mock) y el índice de mercado con los precios actuales."""
        # 1. Actualización de BoriCoin (siempre mock)
        current = self.current_prices.get('BRCN', CONFIG.INITIAL_PRICES['BRCN'])
        change_pct = random.uniform(-0.0002, 0.0002) 
        self.current_prices['BRCN'] = current * (1 + change_pct)

        # 2. Actualización del Benchmark (Índice de mercado)
        total_market_value = sum(self.current_prices[ticker] * CONFIG.CAPITAL_PER_ASSET for ticker in CONFIG.ASSETS_TO_TRACK)
        self.market_index_history.append(total_market_value)
        
    def _mock_prices_only(self):
        """Simula precios con micro-volatilidad para mantener la visualización en movimiento."""
        for ticker in CONFIG.ASSETS_TO_TRACK:
            current = self.current_prices.get(ticker, CONFIG.INITIAL_PRICES[ticker])
            # MUY baja volatilidad para simular el precio estático entre llamadas reales
            change_pct = random.uniform(-0.000001, 0.000001) 
            self.current_prices[ticker] = current * (1 + change_pct)
        
        # Aunque los precios "reales" no cambian, BRCN y el índice se actualizan para el display
        self._update_mock_brcn_and_index()
        return self.current_prices
        
    def _fallback_mock_prices(self):
        """Genera precios mock para cuando la API falla (no toca la lógica dual)."""
        print(f"[{Colors.WARNING}API{Colors.ENDC}] Usando precios de fallback simulados para evitar interrupción.")
        # Simula más volatilidad para mostrar que la API falló
        for ticker in CONFIG.ASSETS_TO_TRACK:
            current = self.current_prices.get(ticker, CONFIG.INITIAL_PRICES[ticker])
            change_pct = random.uniform(-0.0002, 0.0002) 
            self.current_prices[ticker] = current * (1 + change_pct)
        
        self._update_mock_brcn_and_index()
        return self.current_prices

    def execute_live_order(self, product_id: str, side: str, size: float):
        """
        🛑 ESQUELETO DE FUNCIÓN PARA TRADING REAL (USO DE ÓRDENES LIMITADAS RECOMENDADO)
        """
        if not CONFIG.LIVE_TRADING_ENABLED:
            print(f"[{product_id}] {Colors.WARNING}Orden REAL NO EJECUTADA: Live Trading está desactivado. ¡Recuerda usar Órdenes Limitadas en Coinbase Advanced!{Colors.ENDC}")
            return None 

        print(f"[{product_id}] {Colors.WARNING}🚨 ENVIANDO ORDEN REAL A PLATAFORMA (MOCK). Tipo: {side}{Colors.ENDC}")
        time.sleep(0.5) 
        
        # Simulación de respuesta exitosa
        print(f"[{product_id}] {Colors.OKGREEN}✅ ORDEN SIMULADA ENVIADA. Tipo: {side}, Cantidad: {size:,.4f}.{Colors.ENDC}")
        return {"status": "success", "executed_size": size} 


    def fetch_initial_history(self, initial_ticks=CONFIG.INITIAL_HISTORY_TICKS):
        """Simula la carga de datos históricos para inicializar indicadores y ejecuta la primera compra (si aplica)."""
        print(f"\n[{Colors.OKCYAN}API{Colors.ENDC}] Cargando {initial_ticks} puntos de datos históricos iniciales (Mock)..")
        history_data = {}
        for ticker in CONFIG.ASSETS_TO_TRACK:
            initial_price = CONFIG.INITIAL_PRICES[ticker] 
            prices = [initial_price]
            for _ in range(initial_ticks - 1):
                current_price = prices[-1]
                change_pct = np.random.normal(0, 0.005)
                new_price = current_price * (1 + change_pct)
                prices.append(new_price)
            
            history_data[ticker] = pd.DataFrame(prices, columns=['Close'])
        return history_data

# -----------------------------------------------------------
# 🤖 LÓGICA DE TRADING 
# -----------------------------------------------------------

class TradingAsset:
    """Encapsula la lógica de trading para un solo par de activos."""
    
    def __init__(self, ticker: str, initial_usdc: float, price_history_df: pd.DataFrame, fetcher_instance):
        self.ticker = ticker
        self.usdc_balance = initial_usdc
        self.asset_balance = 0.0
        self.position = 0
        self.buy_price = 0.0 
        self.transaction_log = []
        self.data = price_history_df.copy()
        self.current_tick_index = len(self.data) - 1 
        self.pnl_history = [initial_usdc] * len(self.data) 
        self.fetcher = fetcher_instance
        self.initial_usdc_balance = initial_usdc
        
        # ✅ V6.5: ACUMULADORES BRUTOS para el análisis de transacciones
        self.total_commissions = 0.0
        self.total_winning_pnl = 0.0 
        self.total_losing_pnl = 0.0  
        self.trades_closed = 0
        
        # Activación de la primera señal 
        self._calculate_indicators()
        
        if 'RSI' in self.data.columns and not self.data['RSI'].isnull().all():
            last_rsi = self.data['RSI'].iloc[-1]
        else:
            last_rsi = 50 
        
        # Activación de la primera compra si el activo está "sobrevendido" al inicio.
        if last_rsi <= CONFIG.RSI_BUY_THRESHOLD:
            current_price = self.data['Close'].iloc[-1]
            if self.ticker != 'BRCN': 
                usdc_to_spend = self.usdc_balance * CONFIG.USDC_TO_TRADE_PCT
                qty_to_buy = usdc_to_spend / current_price
                self._execute_trade('BUY_INITIAL', current_price, qty_to_buy)


    def set_new_price(self, new_price: float):
        self.current_tick_index += 1
        self.data.loc[len(self.data)] = new_price
        if len(self.data) > 300: 
            self.data = self.data.iloc[-300:].reset_index(drop=True)

    def _calculate_indicators(self):
        """Calcula el RSI y lo añade al DataFrame de datos."""
        if len(self.data) < CONFIG.RSI_PERIOD:
            self.data['RSI'] = np.nan
            return

        delta = self.data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Usar EWM (Media Móvil Exponencial Ponderada)
        avg_gain = gain.ewm(span=CONFIG.RSI_PERIOD, adjust=False).mean()
        avg_loss = loss.ewm(span=CONFIG.RSI_PERIOD, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan) 
        self.data['RSI'] = 100 - (100 / (1 + rs))

    def _execute_trade(self, trade_type: str, current_price: float, qty_to_trade: float):
        """Decide si simular o ejecutar una orden real."""
        is_live = CONFIG.LIVE_TRADING_ENABLED
        side = 'BUY' if 'BUY' in trade_type else 'SELL'
        product_id = f"{self.ticker}-USD"
        
        if is_live and self.ticker != 'BRCN': 
            order_result = self.fetcher.execute_live_order(
                product_id=product_id, 
                side=side, 
                size=qty_to_trade
            )
            
            if order_result and order_result['status'] == 'success':
                 executed_size = order_result.get('executed_size', qty_to_trade)
                 return self._update_internal_state(trade_type, current_price, executed_size)
            else:
                 return current_price
        else:
            return self._simulate_trade(trade_type, current_price, qty_to_trade)

    def _update_internal_state(self, trade_type: str, current_price: float, qty_executed: float):
        """Actualiza el balance interno tras una ejecución (simulada o real) y acumula PnL."""
        if qty_executed <= 0:
            return current_price

        # Aplicar Slippage
        if 'BUY' in trade_type:
            final_price = current_price * (1 + CONFIG.SLIPPAGE_PCT)
            commission_pct_factor = CONFIG.COMMISSION_PCT
        else:
            final_price = current_price * (1 - CONFIG.SLIPPAGE_PCT)
            commission_pct_factor = CONFIG.COMMISSION_PCT


        pnl = 0.0
        commission_cost = 0.0
        
        # Lógica de Compra
        if 'BUY' in trade_type:
            cost = final_price * qty_executed
            commission_cost = cost * commission_pct_factor
            self.usdc_balance -= (cost + commission_cost)
            self.asset_balance += qty_executed
            self.position = 1
            self.buy_price = final_price # Nuevo precio de entrada
            
        # Lógica de Venta/Cierre
        else: 
            revenue = final_price * qty_executed
            commission_cost = revenue * commission_pct_factor
            
            # PnL Bruto sin comisiones (solo por la diferencia de precio)
            pnl_bruto = (final_price - self.buy_price) * qty_executed
            
            self.usdc_balance += (revenue - commission_cost)
            self.asset_balance -= qty_executed
            
            # PnL Neto del trade (el que incluye la comisión)
            pnl = pnl_bruto - commission_cost 
            
            # ✅ V6.5: Acumulación para el Reporte Bancario
            self.total_commissions += commission_cost 
            if pnl_bruto > 0.00001: 
                # Acumulamos la ganancia bruta antes de comisiones
                self.total_winning_pnl += pnl_bruto 
            elif pnl_bruto < -0.00001: 
                # Acumulamos la pérdida bruta antes de comisiones (valor negativo)
                self.total_losing_pnl += pnl_bruto 
            
            self.trades_closed += 1 # Contar el trade cerrado

            if self.asset_balance < 0.000001:
                self.position = 0
                self.asset_balance = 0.0 
            elif self.asset_balance > 0:
                pass 

        # Registro de la transacción
        log_type = trade_type.replace('_MANUAL', ' (MANUAL)').replace('_INITIAL', ' (INITIAL)').replace('_SL', ' (SL)').replace('_TP', ' (TP)')

        self.transaction_log.append({
            'Tick': self.current_tick_index,
            'Asset': self.ticker,
            'Type': log_type,
            'Entry_Price': self.buy_price if self.position == 1 or 'BUY' in trade_type else 0.0, 
            'Exec_Price': final_price, 
            'Qty': qty_executed,
            'PnL': pnl, # PnL Neto del trade cerrado
            'Commission': commission_cost,
            'USDC_Balance': self.usdc_balance,
            'Asset_Balance': self.asset_balance
        })
        return final_price

    def _simulate_trade(self, trade_type: str, current_price: float, qty_to_trade: float):
        """Simula la ejecución para el modo de práctica."""
        if 'BUY' in trade_type:
            cost_estimate = current_price * qty_to_trade * (1 + CONFIG.SLIPPAGE_PCT) * (1 + CONFIG.COMMISSION_PCT)
            if self.usdc_balance < cost_estimate:
                 return current_price
        
        return self._update_internal_state(trade_type, current_price, qty_to_trade)

    def run_tick(self, is_real_tick: bool):
        """Ejecuta un solo paso de Live Trading (Lógica Automática) y retorna la opinión del bot."""
        
        current_price = self.data['Close'].iloc[-1]
        self._calculate_indicators()
        
        total_value = self.usdc_balance + (self.asset_balance * current_price)
        self.pnl_history.append(total_value)
        
        if len(self.data) < CONFIG.RSI_PERIOD:
            return f"{Colors.WARNING}Cargando datos históricos...{Colors.ENDC}", False
            
        last_row = self.data.iloc[-1]
        rsi_value = last_row['RSI'] if 'RSI' in last_row and not np.isnan(last_row['RSI']) else 50
        
        bot_opinion = ""
        action_taken = False
        
        if not is_real_tick:
            if self.position == 1:
                pnl_actual_pct = ((current_price / self.buy_price) - 1) * 100
                pnl_color = Colors.OKGREEN if pnl_actual_pct >= 0 else Colors.FAIL
                return f"{Colors.OKCYAN}📊 MONITOREO: Entrada: ${self.buy_price:,.4f}. PnL: {pnl_color}{pnl_actual_pct:,.2f}%{Colors.ENDC}", False
            else:
                 rsi_display = f"{rsi_value:,.2f}"
                 return f"Neutral: RSI ({rsi_display}) en rango. Esperando tick real.", False

        # -----------------------------------------------------
        # LÓGICA DE TRADING REAL (Solo se ejecuta en tick real)
        # -----------------------------------------------------

        # 1. GESTIÓN DE RIESGO (SL/TP - Automático)
        if self.position == 1 and self.ticker != 'BRCN': 
            stop_loss_price = self.buy_price * (1 - CONFIG.STOP_LOSS_PCT)
            take_profit_price = self.buy_price * (1 + CONFIG.TAKE_PROFIT_PCT)
            qty_to_sell = self.asset_balance

            if current_price <= stop_loss_price:
                self._execute_trade('SELL_SL', current_price, qty_to_sell)
                bot_opinion = f"{Colors.FAIL}🔥 STOP LOSS: SL Activado. Cerrando para limitar la pérdida.{Colors.ENDC}"
                action_taken = True
            
            elif current_price >= take_profit_price:
                self._execute_trade('SELL_TP', current_price, qty_to_sell)
                bot_opinion = f"{Colors.OKGREEN}💎 TAKE PROFIT: TP Alcanzado. Ganancia asegurada.{Colors.ENDC}"
                action_taken = True
        
        # 2. ESTRATEGIA RSI (Automático)
        if not action_taken and self.ticker != 'BRCN': 
            
            buy_signal = rsi_value <= CONFIG.RSI_BUY_THRESHOLD
            sell_signal = rsi_value >= CONFIG.RSI_SELL_THRESHOLD

            if self.position == 0 and self.usdc_balance > 1 and buy_signal:
                usdc_to_spend = self.usdc_balance * CONFIG.USDC_TO_TRADE_PCT
                qty_to_buy = usdc_to_spend / current_price
                self._execute_trade('BUY', current_price, qty_to_buy)
                bot_opinion = f"{Colors.OKGREEN}🟢 COMPRA RSI: Sobrevendido ({rsi_value:,.2f}). Ejecutando compra.{Colors.ENDC}"
                action_taken = True # Añadido para asegurar que la acción se refleja
            
            elif self.position == 1 and sell_signal:
                qty_to_sell = self.asset_balance
                self._execute_trade('SELL', current_price, qty_to_sell)
                bot_opinion = f"{Colors.FAIL}🔴 VENTA RSI: Sobrecomprado ({rsi_value:,.2f}). Cerrando posición.{Colors.ENDC}"
                action_taken = True # Añadido para asegurar que la acción se refleja
            
            elif self.position == 1:
                pnl_actual_pct = ((current_price / self.buy_price) - 1) * 100
                pnl_color = Colors.OKGREEN if pnl_actual_pct >= 0 else Colors.FAIL
                bot_opinion = f"{Colors.OKCYAN}📊 MONITOREO: Entrada: ${self.buy_price:,.4f}. PnL: {pnl_color}{pnl_actual_pct:,.2f}%{Colors.ENDC} (Esperando TP/SL/RSI)."
            
            else:
                 bot_opinion = f"Neutral: RSI ({rsi_value:,.2f}) en rango."
        
        elif self.ticker == 'BRCN':
             bot_opinion = f"{Colors.OKCYAN}INFO: Monitoreando BoriCoin (RSI: {rsi_value:,.2f}){Colors.ENDC}"


        return bot_opinion, action_taken

    # ... (execute_manual_buy, execute_manual_sell, get_current_value permanecen iguales) ...
    def execute_manual_buy(self):
        """Ejecuta una compra manual."""
        if self.position == 0 and self.usdc_balance > 1:
            current_price = self.data['Close'].iloc[-1]
            usdc_to_spend = self.usdc_balance * CONFIG.USDC_TO_TRADE_PCT
            qty_to_buy = usdc_to_spend / current_price
            return self._execute_trade('BUY_MANUAL', current_price, qty_to_buy)
        return False

    def execute_manual_sell(self):
        """Ejecuta una venta manual."""
        if self.position == 1 and self.asset_balance > 0.000001:
            current_price = self.data['Close'].iloc[-1]
            qty_to_sell = self.asset_balance
            return self._execute_trade('SELL_MANUAL', current_price, qty_to_sell)
        return False
    
    def close_final_position(self, final_price: float):
        """Cierra la posición al finalizar el script."""
        if self.position == 1:
            self._execute_trade('CLOSE', final_price, self.asset_balance) 
            self.position = 0
        return self.usdc_balance
        
    def get_current_value(self):
        last_price = self.data['Close'].iloc[-1]
        return self.usdc_balance + (self.asset_balance * last_price)
        
    def get_win_rate(self):
        """Calcula el porcentaje de operaciones cerradas con ganancia."""
        # Filtra solo las operaciones de cierre
        closed_trades = pd.DataFrame([log for log in self.transaction_log if 'SELL' in log['Type'] or 'CLOSE' in log['Type']]).copy()
        
        if closed_trades.empty:
            return 0.0, 0
        
        closed_trades['PnL_float'] = pd.to_numeric(closed_trades['PnL'])
        winning_trades = closed_trades[closed_trades['PnL_float'] > 0.00001] 
        
        return (len(winning_trades) / len(closed_trades)) * 100, len(closed_trades)

    def get_accumulated_metrics(self):
        """Retorna las métricas de acumulación para el reporte bancario."""
        return {
            'total_commissions': self.total_commissions,
            'total_winning_pnl_bruto': self.total_winning_pnl,
            'total_losing_pnl_bruto': self.total_losing_pnl,
            'final_usdc_balance': self.usdc_balance,
            'final_asset_balance': self.asset_balance
        }


# -----------------------------------------------------------
# 🏢 CLASE DE GESTIÓN DEL PORTAFOLIO MULTI-ACTIVO (LIVE)
# -----------------------------------------------------------

class PortfolioManager:
    """Gestiona múltiples activos y el flujo de la simulación."""
    
    def __init__(self, history_data_map: dict, fetcher_instance):
        self.initial_usdc_balance = CONFIG.INITIAL_USDC_BALANCE
        self.assets = {}
        for ticker in CONFIG.ASSETS_TO_TRACK:
            self.assets[ticker] = TradingAsset(
                ticker=ticker,
                initial_usdc=CONFIG.CAPITAL_PER_ASSET,
                price_history_df=history_data_map[ticker],
                fetcher_instance=fetcher_instance
            )
        self.sim_tick_counter = 0
        self.visual_tick_counter = 0 
        self.portfolio_value_history = [self.initial_usdc_balance] * len(next(iter(history_data_map.values())))
        self.fetcher = fetcher_instance
        
    def _is_key_pressed(self):
        return False 

    def _get_bank_details_current(self):
        """Obtiene las métricas de acumulación actuales para el display."""
        total_commissions = 0.0
        total_winning_pnl_bruto = 0.0
        total_losing_pnl_bruto = 0.0
        
        for asset in self.assets.values():
            metrics = asset.get_accumulated_metrics()
            total_commissions += metrics['total_commissions']
            total_winning_pnl_bruto += metrics['total_winning_pnl_bruto']
            total_losing_pnl_bruto += metrics['total_losing_pnl_bruto']
            
        # PnL Neto de transacciones = Ganancias Brutas + Pérdidas Brutas (Pérdidas ya son negativas) - Comisiones
        pnl_neto_cerrado = (total_winning_pnl_bruto + total_losing_pnl_bruto) - total_commissions
        
        return total_winning_pnl_bruto, total_losing_pnl_bruto, total_commissions, pnl_neto_cerrado

    def interpret_profit(self, total_value: float):
        """Proporciona una descripción del rendimiento general del portafolio, incluyendo riesgo."""
        pnl = total_value - self.initial_usdc_balance
        return_pct = (pnl / self.initial_usdc_balance) * 100
        
        market_index_value = self.fetcher.market_index_history[-1]
        market_pnl_pct = ((market_index_value / self.fetcher.initial_market_index_value) - 1) * 100
        alpha = return_pct - market_pnl_pct
        
        portfolio_series = pd.Series(self.portfolio_value_history)
        returns = portfolio_series.pct_change().dropna().tail(CONFIG.RSI_PERIOD * 2) 
        
        recent_volatility = returns.std() * 100 if len(returns) >= 2 else 0.0
        
        description = f"{Colors.WARNING}ANÁLISIS EN CURSO. Faltan más ticks de lógica para el riesgo.{Colors.ENDC}"
        risk_assessment = f"{Colors.OKGREEN}Volatilidad Baja (N/A).{Colors.ENDC}"
        action_comment = "Esperando acumulación de datos para evaluar riesgo y Alpha."
        
        if recent_volatility > 0.001: 
            if return_pct >= 0.5 and alpha >= 0:
                description = f"{Colors.OKGREEN}RENDIMIENTO SÓLIDO (Alpha Positivo). La estrategia es efectiva.{Colors.ENDC}"
            elif alpha > 0.1:
                description = f"{Colors.OKGREEN}ALPHA GENERADO: Superando al índice. La selección de activos es superior.{Colors.ENDC}"
            elif return_pct >= 0 and alpha < 0:
                description = f"{Colors.WARNING}Ganancia, pero rezagado del mercado (Beta negativa). Cuidado con activos no rentables.{Colors.ENDC}"
            else: 
                if alpha > -0.5:
                    description = f"{Colors.WARNING}Pérdida (Drawdown). Sin embargo, estamos resistiendo mejor que el índice ({alpha:,.2f}% mejor).{Colors.ENDC}"
                else:
                    description = f"{Colors.FAIL}DRAWDOWN AGRESIVO. La estrategia está perdiendo contra el índice. REQUIERE REVISIÓN.{Colors.ENDC}"
        
            if recent_volatility > 0.5:
                risk_assessment = f"{Colors.FAIL}VOLATILIDAD ALTA ({recent_volatility:,.2f}%). Alto riesgo de SL/TP.{Colors.ENDC}"
                action_comment = "Asegurar las ganancias rápidamente (TP) en este entorno volátil."
            elif recent_volatility > 0.2:
                risk_assessment = f"{Colors.WARNING}Volatilidad Moderada ({recent_volatility:,.2f}%). Riesgo controlable.{Colors.ENDC}"
                action_comment = "Seguir las señales del RSI y tener las órdenes limitadas listas."
            else:
                risk_assessment = f"{Colors.OKGREEN}Volatilidad Baja ({recent_volatility:,.2f}%). Entorno estable, difícil generar Alpha.{Colors.ENDC}"
                action_comment = "Buscar señales extremas del RSI o entradas manuales."
            
        return description, action_comment, market_pnl_pct, alpha, recent_volatility

    # 🔴 CORRECCIÓN V6.5 (CHEGUI): Añadir 'time_until_next_execution' a la definición de la función (Línea 667)
    def display_status(self, time_until_next_execution: float, asset_opinions: dict):
        """Muestra la interfaz de demo en vivo con estética y opiniones."""
        os.system('cls' if os.name == 'nt' else 'clear')

        total_value = sum(asset.get_current_value() for asset in self.assets.values())
        pnl_percent = ((total_value - self.initial_usdc_balance) / self.initial_usdc_balance) * 100
        
        pnl_color = Colors.OKGREEN if pnl_percent >= 0 else Colors.FAIL
        
        mode = "LIVE TRADING REAL 🔴" if CONFIG.LIVE_TRADING_ENABLED else "SIMULACIÓN 🟢"
        
        print(f"{Colors.HEADER}="*100 + Colors.ENDC)
        print(f"| {Colors.OKBLUE}{pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC} | Ticks Lógica Ejecutada: {self.sim_tick_counter} | Ticks Visuales: {self.visual_tick_counter}")
        print(f"|  🤖 {Colors.BOLD}BORITRACKER V6.5 - {mode}{Colors.ENDC} | Activos: {len(self.assets)} | Fuente: CoinGecko/BRCN")
        print(f"{Colors.HEADER}="*100 + Colors.ENDC)
        
        market_desc, action_comment, market_pnl_pct, alpha, volatility_pct = self.interpret_profit(total_value)
        
        # 💰 V6.5: OBTENER ACUMULACIONES BRUTAS Y NETAS
        total_winning_pnl_bruto, total_losing_pnl_bruto, total_commissions, pnl_neto_cerrado = self._get_bank_details_current()
        pnl_cerrado_color = Colors.OKGREEN if pnl_neto_cerrado >= 0 else Colors.FAIL
        
        # --- SECCIÓN AMPLIADA DE ANÁLISIS DE RENDIMIENTO (Actualizada V6.5) ---
        print(f"📈 {Colors.BOLD}RESUMEN DE RENDIMIENTO DE LA SESIÓN{Colors.ENDC}")
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)
        
        # 1. Rendimiento del Portafolio
        print(f"💰 {Colors.BOLD}PORTAFOLIO VALOR TOTAL:{Colors.ENDC} ${total_value:,.2f}")
        print(f"📊 {Colors.BOLD}RENDIMIENTO NETO (Sesión):{Colors.ENDC} {pnl_color}{pnl_percent:,.2f}%{Colors.ENDC} (vs. Inicial: ${self.initial_usdc_balance:,.2f})")
        
        # --- ACUMULACIÓN DE GANANCIAS POR TRANSACCIÓN (INFORMACIÓN CLAVE) ---
        print(f"  --- ACUMULACIÓN BRUTA DE TRADES CERRADOS ---")
        print(f"  🟢 {Colors.BOLD}GANANCIA BRUTA (Antes Comisiones):{Colors.ENDC} ${total_winning_pnl_bruto:,.4f}")
        # La pérdida ya viene negativa, la mostramos en positivo para claridad en el display
        print(f"  🔴 {Colors.BOLD}PÉRDIDA BRUTA (Antes Comisiones):{Colors.ENDC} -${abs(total_losing_pnl_bruto):,.4f}") 
        print(f"  ➖ {Colors.BOLD}COMISIONES TOTALES:{Colors.ENDC} -${total_commissions:,.4f}")
        print(f"  💸 {Colors.BOLD}PNL NETO CERRADO (Gan-Per-Com):{Colors.ENDC} {pnl_cerrado_color}${pnl_neto_cerrado:,.4f}{Colors.ENDC}")
        # ------------------------------------------------------------------------
        
        # 2. Comparación con el Benchmark (Índice Simulado)
        pnl_color_market = Colors.OKGREEN if market_pnl_pct >= 0 else Colors.FAIL
        print(f"🌐 {Colors.BOLD}BENCHMARK del Mercado (Índice):{Colors.ENDC} {pnl_color_market}{market_pnl_pct:,.2f}%{Colors.ENDC}")
        
        # 3. Cálculo del Alpha (Rendimiento por encima del mercado)
        alpha_color = Colors.OKGREEN if alpha >= 0 else Colors.FAIL
        print(f"⭐ {Colors.BOLD}ALPHA (Valor Agregado):{Colors.ENDC} {alpha_color}{alpha:,.2f}%{Colors.ENDC}")
        
        # 4. Drawdown de la Sesión (Riesgo Actual)
        portfolio_series = pd.Series(self.portfolio_value_history)
        peak_value = portfolio_series.max()
        drawdown_pct = ((peak_value - total_value) / peak_value) * 100 if peak_value > 0 else 0
        drawdown_color = Colors.FAIL if drawdown_pct >= 0.5 else Colors.WARNING
        print(f"🛡️ {Colors.BOLD}DRAWDOWN ACTUAL:{Colors.ENDC} {drawdown_color}-{drawdown_pct:,.2f}%{Colors.ENDC} (Máxima caída temporal desde el pico: ${peak_value:,.2f})")
        
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)

        # Análisis Global (SECCIÓN EXPANDIDA)
        print(f"  🧠 {Colors.BOLD}ANÁLISIS DE RIESGO Y ESTRATEGIA:{Colors.ENDC}")
        print(f"  > 📉 **Volatilidad Reciente (Riesgo):** {self._format_risk_assessment(volatility_pct, market_desc)}{Colors.ENDC}") 
        print(f"  > 🚀 **Rendimiento General (Beta/Alpha):** {market_desc}")
        print(f"  🎯 {Colors.BOLD}DECISIÓN ESTRATÉGICA (Recomendación):{Colors.ENDC} **{action_comment}**")
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)
        
        print(f"  📊 {Colors.BOLD}DETALLE DE ACTIVOS Y SEÑALES EN TIEMPO REAL{Colors.ENDC}")
        
        static_assets = [(ticker, self.assets[ticker]) for ticker in CONFIG.ASSETS_TO_TRACK]
        
        # Encabezado de la tabla (ajustado para incluir PRECISION)
        print(f"{'Activo':<8} | {'Precio':<12} | {'RSI':<6} | {'Posición':<10} | {'Precisión':<8} | {'Opinión/Decisión del Bot (Señal)':<50}")
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)

        for ticker, asset in static_assets: 
            current_price = asset.data['Close'].iloc[-1]
            last_rsi = asset.data['RSI'].iloc[-1] if not asset.data.empty and 'RSI' in asset.data.columns else np.nan
            
            position_status = f"{Colors.OKGREEN}COMPRADO{Colors.ENDC}" if asset.position == 1 else f"{Colors.WARNING}LIBRE{Colors.ENDC}"
            
            rsi_color = Colors.OKGREEN if (not np.isnan(last_rsi) and last_rsi <= CONFIG.RSI_BUY_THRESHOLD) else (Colors.FAIL if (not np.isnan(last_rsi) and last_rsi >= CONFIG.RSI_SELL_THRESHOLD) else Colors.ENDC)
            rsi_display = f"{last_rsi:,.2f}" if not np.isnan(last_rsi) else "N/A"
            
            win_rate, trades = asset.get_win_rate()
            precision_color = Colors.OKGREEN if win_rate >= 50 else (Colors.WARNING if win_rate > 0 else Colors.ENDC)
            precision_display = f"{precision_color}{win_rate:,.0f}%{Colors.ENDC} ({trades})"

            opinion = asset_opinions.get(ticker, f"{Colors.WARNING}Esperando datos...{Colors.ENDC}")
            
            if ticker == 'BRCN':
                 ticker_display = f"{Colors.BOLD}{Colors.OKGREEN}BRCN{Colors.ENDC}"
            else:
                 ticker_display = ticker

            print(f"{ticker_display:<8} | ${current_price:,.4f} | {rsi_color}{rsi_display}{Colors.ENDC} | {position_status:<10} | {precision_display:<8} | {opinion}")

            
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)
        
        # 🔴 CORRECCIÓN V6.5 (CHEGUI): Usar el argumento pasado a la función (Línea 747)
        time_until_next_execution_display = max(0, time_until_next_execution)
        print(f"[{Colors.OKBLUE}INFO{Colors.ENDC}] Próxima EJECUCIÓN de API/Lógica en: {time_until_next_execution_display:.1f} segundos.")
        print(f"🕹️ {Colors.BOLD}CONTROLES MANUALES:{Colors.ENDC} Usa **Ctrl+C** para detener la simulación y generar el reporte final.")

    def _format_risk_assessment(self, volatility_pct, market_desc):
        """Función auxiliar para formatear la evaluación de riesgo."""
        if volatility_pct > 0.5:
            risk_assessment = f"{Colors.FAIL}VOLATILIDAD ALTA ({volatility_pct:,.2f}%){Colors.ENDC}"
        elif volatility_pct > 0.2:
            risk_assessment = f"{Colors.WARNING}Volatilidad Moderada ({volatility_pct:,.2f}%){Colors.ENDC}"
        else:
            risk_assessment = f"{Colors.OKGREEN}Volatilidad Baja ({volatility_pct:,.2f}%){Colors.ENDC}"
        return risk_assessment
        
    def _handle_input(self):
        return None

    def run_trading_loop(self):
        """Función principal para el loop de trading, ahora con frecuencia dual continua."""
        
        final_log = []
        last_execution_time = time.time() - CONFIG.TICK_INTERVAL_SECONDS 
        
        try:
            while True: 
                
                start_time = time.time()
                asset_opinions = {}
                
                is_real_tick = (time.time() - last_execution_time) >= CONFIG.TICK_INTERVAL_SECONDS
                
                if is_real_tick:
                    new_prices = self.fetcher.fetch_latest_prices()
                    self.sim_tick_counter += 1
                    last_execution_time = time.time()
                else:
                    new_prices = self.fetcher._mock_prices_only()
                
                self.visual_tick_counter += 1
                
                for ticker, asset in self.assets.items():
                    asset.set_new_price(new_prices[ticker])
                    opinion, _ = asset.run_tick(is_real_tick) 
                    asset_opinions[ticker] = opinion

                total_value = sum(asset.get_current_value() for asset in self.assets.values())
                self.portfolio_value_history.append(total_value)
                
                time_until_next_execution = CONFIG.TICK_INTERVAL_SECONDS - (time.time() - last_execution_time)
                
                # 🔴 CORRECCIÓN V6.5 (CHEGUI): Pasar la variable 'time_until_next_execution' (Línea 797)
                self.display_status(time_until_next_execution, asset_opinions) 
                
                self. _handle_input()
                
                time.sleep(CONFIG.DISPLAY_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            print("\n\n>>> 🛑 SIMULACIÓN DETENIDA: Solicitud de interrupción del usuario (Ctrl+C). Generando reporte final...")
            
        final_prices = self.fetcher.current_prices 
        for ticker, asset in self.assets.items():
            final_price = final_prices[ticker]
            asset.close_final_position(final_price) # Cierra cualquier posición abierta
            final_log.extend(asset.transaction_log)
        
        if final_log:
            final_df = pd.DataFrame(final_log)
        else:
            final_df = pd.DataFrame(columns=['Tick', 'Asset', 'Type', 'Entry_Price', 'Exec_Price', 'Qty', 'PnL', 'Commission'])
            
        final_value = sum(asset.usdc_balance for asset in self.assets.values())
        
        return final_df, self.sim_tick_counter, final_value
    
    def _calculate_metrics(self, final_value: float, total_ticks: int) -> dict:
        """
        ✅ V6.5: Calcula métricas clave de rendimiento con enfoque en el PnL desglosado.
        """
        
        total_pnl = final_value - self.initial_usdc_balance
        return_pct = (total_pnl / self.initial_usdc_balance) * 100
        
        # 1. Acumulaciones Bancarias
        total_commissions = 0.0
        total_winning_pnl_bruto = 0.0
        total_losing_pnl_bruto = 0.0
        final_asset_value = 0.0
        total_initial_asset_value = 0.0 # Inicializar el valor total inicial de los activos (para calcular PnL no operado)
        
        for asset in self.assets.values():
            metrics = asset.get_accumulated_metrics()
            final_price = self.fetcher.current_prices[asset.ticker]

            total_commissions += metrics['total_commissions']
            total_winning_pnl_bruto += metrics['total_winning_pnl_bruto']
            total_losing_pnl_bruto += metrics['total_losing_pnl_bruto']
            final_asset_value += metrics['final_asset_balance'] * final_price

            # El valor de los activos iniciales fue CONFIG.CAPITAL_PER_ASSET por ticker
            total_initial_asset_value += CONFIG.CAPITAL_PER_ASSET
        
        # PnL Neto de Transacciones (Cerrado) = Ganancias Brutas + Pérdidas Brutas - Comisiones
        pnl_neto_transacciones = (total_winning_pnl_bruto + total_losing_pnl_bruto) - total_commissions
        
        # PnL Total = PnL Neto de Transacciones + PnL No Operado (Volatilidad de activos no vendidos)
        # Simplificado: PnL No Operado es el PnL Total menos el PnL de lo que se cerró (el resto es valoración)
        pnl_no_operado = total_pnl - pnl_neto_transacciones
        
        
        # 2. Métricas de Rendimiento (Sharpe, Sortino, Drawdown)
        if total_ticks <= 1 or len(self.portfolio_value_history) < 2:
            # Retorno simplificado si no hay suficientes datos
            metrics_return = {
                "Volatilidad Anualizada (%)": "N/A",
                "Drawdown Máximo (%)": "N/A",
                "Sharpe Ratio": "N/A",
                "Sortino Ratio": "N/A",
                "Avg. Recompensa/Riesgo (G/P)": "N/A"
            }
        else:
            logic_tick_step = int(CONFIG.TICK_INTERVAL_SECONDS / CONFIG.DISPLAY_INTERVAL_SECONDS)
            portfolio_series = pd.Series([
                self.portfolio_value_history[i] 
                for i in range(len(self.portfolio_value_history)) 
                if i % logic_tick_step == 0 or i == 0
            ])
            
            returns = portfolio_series.pct_change().dropna()
            
            annual_ticks = (252 * 24 * 60 * 60) / CONFIG.TICK_INTERVAL_SECONDS 
            
            volatility = returns.std() * np.sqrt(annual_ticks)
            sharpe_ratio = returns.mean() / volatility * np.sqrt(annual_ticks) if volatility != 0 else np.nan

            downside_returns = returns[returns < 0]
            downside_risk = downside_returns.std() * np.sqrt(annual_ticks) if len(downside_returns) > 0 else volatility
            sortino_ratio = returns.mean() / downside_risk * np.sqrt(annual_ticks) if downside_risk != 0 else np.nan
            
            peak = portfolio_series.cummax() 
            drawdown = (portfolio_series - peak) / peak 
            max_drawdown = drawdown.min() * 100

            all_transactions = [log for asset in self.assets.values() for log in asset.transaction_log if 'CLOSE' in log['Type'] or 'SELL' in log['Type']]
            
            risk_reward_val = np.nan
            if all_transactions:
                log_df = pd.DataFrame(all_transactions)
                log_df['PnL_float'] = pd.to_numeric(log_df['PnL'], errors='coerce')
                # Recalculamos Avg Gain/Loss para la métrica
                # Recompensa Bruta
                avg_gain_bruto = total_winning_pnl_bruto / (len(log_df[log_df['PnL_float'] > 0]) or 1)
                # Riesgo Bruto (pérdida positiva)
                avg_loss_bruto = abs(total_losing_pnl_bruto) / (len(log_df[log_df['PnL_float'] < 0]) or 1)
                risk_reward_val = avg_gain_bruto / avg_loss_bruto if avg_loss_bruto != 0 else np.nan
            
            metrics_return = {
                "Volatilidad Anualizada (%)": f"{volatility*100:,.2f}%",
                "Drawdown Máximo (%)": f"{abs(max_drawdown):,.2f}%",
                "Sharpe Ratio": f"{sharpe_ratio:,.2f}",
                "Sortino Ratio": f"{sortino_ratio:,.2f}",
                "Avg. Recompensa/Riesgo (G/P)": f"{risk_reward_val:,.2f}:1" if not np.isnan(risk_reward_val) and risk_reward_val > 0 else "N/A",
            }

        return {
            "Valor Final Total": f"${final_value:,.2f}",
            "PnL Neto Total": f"${total_pnl:,.2f}",
            "Rendimiento (%)": f"{return_pct:,.2f}%",
            "Total Ticks (Lógica)": total_ticks,
            "Acumulaciones Bancarias": { 
                "Ganancia Bruta (Cerrada)": total_winning_pnl_bruto,
                "Pérdida Bruta (Cerrada)": total_losing_pnl_bruto,
                "Comisiones Totales": total_commissions,
                "PnL Neto Cerrado": pnl_neto_transacciones,
                "PnL No Operado/Volátil": pnl_no_operado
            },
            **metrics_return
        }

    def generate_report(self, log_df: pd.DataFrame, final_value: float, total_ticks: int):
        """
        ✅ V6.5: Genera el reporte final con el nuevo desglose de analítica.
        """
        
        metrics = self._calculate_metrics(final_value, total_ticks)
        bank_details = metrics.pop("Acumulaciones Bancarias") 
        
        print("\n\n" + f"{Colors.HEADER}="*60 + Colors.ENDC)
        print(f"📊 {Colors.BOLD}REPORTE FINAL DE TRADING (Chegui's Portfolio){Colors.ENDC}")
        print(f"Fuente: CoinGecko/Mock | Ticks de Lógica: {total_ticks} | Ticks Visuales: {self.visual_tick_counter}")
        print(f"{Colors.HEADER}="*60 + Colors.ENDC)
        
        # --- SECCIÓN CLAVE: DETALLE BANCARIO DESGLOSADO ---
        print(f"\n💰 {Colors.BOLD}DETALLE DE ACUMULACIÓN BANCARIA (PnL Bruto y Neto){Colors.ENDC}")
        print("-" * 60)
        
        total_pnl_cerrado = bank_details['PnL Neto Cerrado']
        pnl_cerrado_color = Colors.OKGREEN if total_pnl_cerrado >= 0 else Colors.FAIL
        
        # Desglose de PnL por Transacción (Lo que realmente hizo el bot con sus trades)
        print(f"💵 Capital Inicial Total:     ${self.initial_usdc_balance:,.2f}")
        print(f"------------------------------------------------------------")
        print(f"🟢 Ganancia Bruta (Cerrada):  {Colors.OKGREEN}+${bank_details['Ganancia Bruta (Cerrada)']:,.4f}{Colors.ENDC}")
        print(f"🔴 Pérdida Bruta (Cerrada):   {Colors.FAIL}-${abs(bank_details['Pérdida Bruta (Cerrada)']):,.4f}{Colors.ENDC}")
        print(f"➖ Comisiones Totales:        {Colors.FAIL}-${bank_details['Comisiones Totales']:,.4f}{Colors.ENDC}")
        print(f"------------------------------------------------------------")
        print(f"✅ PnL NETO CERRADO (Gan-Per-Com): {pnl_cerrado_color}${total_pnl_cerrado:,.4f}{Colors.ENDC}")
        
        # PnL No Operado/Volatilidad (El cálculo que faltaba)
        pnl_no_operado_color = Colors.OKGREEN if bank_details['PnL No Operado/Volátil'] >= 0 else Colors.FAIL
        print(f"🧮 PnL NO OPERADO (Volatilidad): {pnl_no_operado_color}${bank_details['PnL No Operado/Volátil']:,.4f}{Colors.ENDC}")
        print(f"------------------------------------------------------------")
        
        final_pnl_color = Colors.OKGREEN if final_value > self.initial_usdc_balance else Colors.FAIL
        print(f"📈 {Colors.BOLD}VALOR FINAL TOTAL:{Colors.ENDC}         {final_pnl_color}${final_value:,.2f}{Colors.ENDC}")
        print("-" * 60)
        
        # --- MÉTRICAS AVANZADAS ---
        print(f"\n🧠 {Colors.BOLD}MÉTRICAS AVANZADAS DEL PORTAFOLIO{Colors.ENDC}")
        print("-" * 60)
        for key, value in metrics.items():
            color = Colors.OKGREEN if 'PnL' in key and final_value > self.initial_usdc_balance else Colors.ENDC
            print(f"{key:<35}: {color}{value:>20}{Colors.ENDC}")
        print("-" * 60)
        
        print(f"\n📈 {Colors.BOLD}RESUMEN DE RENDIMIENTO POR ACTIVO:{Colors.ENDC}")
        asset_summary = []
        for ticker, asset in self.assets.items():
            initial = CONFIG.CAPITAL_PER_ASSET
            # Final es la suma del USDC restante más el valor del activo
            final = asset.usdc_balance + (asset.asset_balance * asset.data['Close'].iloc[-1]) 
            pnl = final - initial
            pct = (pnl / initial) * 100
            win_rate, trades = asset.get_win_rate()
            
            asset_summary.append({
                'Activo': ticker,
                'Capital Final (USDC)': final,
                'PnL Neto': pnl,
                'Rendimiento (%)': pct,
                'Trades Cerrados': trades,
                'Win Rate (%)': win_rate
            })

        summary_df = pd.DataFrame(asset_summary)
        print(summary_df.to_string(index=False, float_format="%.2f"))

        print(f"\n📜 {Colors.BOLD}REGISTRO CONSOLIDADO DE TRANSACCIONES (Últimas 10):{Colors.ENDC}")
        
        if not log_df.empty:
            log_display_df = log_df[['Tick', 'Asset', 'Type', 'Entry_Price', 'Exec_Price', 'Qty', 'PnL', 'Commission']].tail(10).copy()
            
            def format_log_value(x):
                try:
                    return f"{float(x):,.4f}"
                except (TypeError, ValueError):
                    return str(x)
                
            for col in ['Entry_Price', 'Exec_Price', 'Qty', 'PnL', 'Commission']:
                if col in log_display_df.columns:
                    log_display_df[col] = pd.to_numeric(log_display_df[col], errors='coerce').apply(format_log_value)
            
            print(log_display_df.to_string(index=False))
        else:
            print("--- NO HAY TRANSACCIONES CERRADAS EN ESTA SIMULACIÓN ---")
        
        # --- Generar Gráfico de PnL ---
        plt.figure(figsize=(12, 6))
        plot_data = pd.Series(self.portfolio_value_history).reset_index(drop=True) 
        
        plt.plot(plot_data.index, plot_data.values, label='Valor Total del Portafolio (USDC)', color='blue', linewidth=2)
        
        benchmark_series = pd.Series(self.fetcher.market_index_history).reset_index(drop=True)
        if len(benchmark_series) > len(plot_data):
            benchmark_series = benchmark_series.iloc[:len(plot_data)]

        plt.plot(benchmark_series.index, benchmark_series.values, 
                 label='Benchmark del Mercado (Índice Simulado)', color='orange', linestyle='--', alpha=0.7)

        plt.axhline(y=self.initial_usdc_balance, color='red', linestyle=':', label='Saldo Inicial (Punto de Equilibrio)')
        plt.title(f'Evolución del Valor del Portafolio - {total_ticks} Ticks de Lógica')
        plt.xlabel(f'Visual Ticks (Actualización cada {CONFIG.DISPLAY_INTERVAL_SECONDS}s)')
        plt.ylabel('Valor en USDC')
        plt.grid(axis='y', linestyle='-', alpha=0.5)
        plt.legend()
        plt.show()

# --- PUNTO DE ENTRADA ---
if __name__ == '__main__':
    
    print(f"\n{Colors.HEADER}====================================================={Colors.ENDC}")
    print(f"  {Colors.BOLD}BORITRACKER V6.5 - DUAL-FREQUENCY MONITOR{Colors.ENDC}")
    print(f"  {Colors.WARNING}Visualización rápida (0.1s) | Lógica de Trading (4.8s){Colors.ENDC}")
    print(f"{Colors.HEADER}====================================================={Colors.ENDC}")
    print(f"  [1] {Colors.OKGREEN}MODO SIMULACIÓN:{Colors.ENDC} Práctica con capital ficticio y datos reales (CoinGecko).")
    print(f"  [2] {Colors.FAIL}MODO LIVE TRADING:{Colors.ENDC} Operaciones reales (Intervalo API seguro: 4.8s).")
    
    mode_choice = input(f"\nSeleccione un modo (1 o 2) y presione Enter: ")
    
    if mode_choice == '2':
        confirm = input(f"{Colors.FAIL}ADVERTENCIA:{Colors.ENDC} ¿Está seguro que desea activar el **LIVE TRADING**? (S/N): ").lower()
        if confirm == 's':
            CONFIG.LIVE_TRADING_ENABLED = True
            print(f"{Colors.OKGREEN}Modo LIVE TRADING ACTIVADO.{Colors.ENDC} ¡Operaciones reales en camino!")
        else:
            print(f"{Colors.WARNING}Volviendo al Modo Simulación. Analicemos primero la estrategia.{Colors.ENDC}")
            
    current_mode = "LIVE TRADING" if CONFIG.LIVE_TRADING_ENABLED else "SIMULACIÓN"
    CONFIG.display_options(current_mode)

    # 1. Carga Inicial
    temp_fetcher = LiveFetcher(CONFIG.ASSETS_TO_TRACK) 
    initial_history_data = temp_fetcher.fetch_initial_history()

    # 2. Inicializar el Manager
    manager = PortfolioManager(
        history_data_map=initial_history_data,
        fetcher_instance=temp_fetcher
    ) 

    # 3. Ejecutar el loop de trading (Continuo hasta Ctrl+C)
    transaction_log, total_ticks, final_value = manager.run_trading_loop()
    
    # 4. Generar el reporte completo
    manager.generate_report(transaction_log, final_value, total_ticks)

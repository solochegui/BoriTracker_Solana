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
import warnings
# Suprimir advertencias de Matplotlib/Pandas
warnings.filterwarnings("ignore")

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
# 📝 CONFIGURACIÓN DEL BOT Y PARÁMETROS (MODO DCA)
# -----------------------------------------------------------
class BotConfiguration:
    """Clase centralizada para definir todos los parámetros."""
    
    def __init__(self):
        
        # ==========================================================
        # 💰 CAPITAL Y PLATAFORMA (Coinbase/CoinGecko)
        # ==========================================================
        # CHEGUI: CAPITAL AJUSTADO A $1,000.00 como punto de referencia.
        self.INITIAL_USDC_BALANCE = 1000.00 
        self.API_KEY = "TU_API_KEY_AQUI" 
        self.API_SECRET = "TU_API_SECRET_AQUI"
        self.LIVE_TRADING_ENABLED = False 
        self.COMMISSION_PCT = 0.003
        self.SLIPPAGE_PCT = 0.001
        
        # 🚨 PARÁMETRO DE ORDEN LIMITADA 
        self.LIMIT_ORDER_OFFSET_PCT = 0.0005 
        
        # ==========================================================
        # 🌐 ACTIVOS Y MAPPING A COINGECKO ID (TOTAL: 30 ACTIVOS)
        # ==========================================================
        self.ASSETS_TO_TRACK = [
            'BRCN', 'SOL', 'JUP', 'PYTH', 
            'ETH', 'LINK', 'DOGE', 'BTC', 'ADA', 'MATIC', 'XRP', 
            'LTC', 'BCH', 'DOT', 'NEAR', 'AVAX',
            'OP', 'ARB', 'INJ', 'AAVE', 'LDO', 'MKR', 'FIL', 'ICP', 
            'SHIB', 'PEPE', 'FTM', 'UNI', 'SUI', 'APT'
        ]

        self.INITIAL_PRICES = {ticker: 1.0 for ticker in self.ASSETS_TO_TRACK} 

        self.COINGECKO_IDS = {
            'SOL': 'solana', 'JUP': 'jupiter-exchange', 'PYTH': 'pyth-network',
            'ETH': 'ethereum', 'LINK': 'chainlink', 'DOGE': 'dogecoin',
            'BTC': 'bitcoin', 'ADA': 'cardano', 'MATIC': 'polygon',
            'XRP': 'ripple', 
            'LTC': 'litecoin', 
            'BCH': 'bitcoin-cash', 
            'DOT': 'polkadot', 
            'NEAR': 'near-protocol', 
            'AVAX': 'avalanche-2',
            'OP': 'optimism', 'ARB': 'arbitrum', 'INJ': 'injective-protocol',
            'AAVE': 'aave', 'LDO': 'lido-dao', 'MKR': 'maker',
            'FIL': 'filecoin', 'ICP': 'internet-computer',
            'SHIB': 'shiba-inu', 'PEPE': 'pepe', 'FTM': 'fantom',
            'UNI': 'uniswap', 
            'SUI': 'sui', 
            'APT': 'aptos' 
        }
        
        # ==========================================================
        # ⏳ TIEMPO Y ESTRATEGIA (MODO DCA/ACUMULACIÓN)
        # ==========================================================
        self.TICK_INTERVAL_SECONDS = 12.0   
        self.DISPLAY_INTERVAL_SECONDS = 0.001 
        self.INITIAL_HISTORY_TICKS = 28 
        self.MAX_SIMULATION_TICKS = 0 
        self.RSI_PERIOD = 5             
        # El bot solo buscará este umbral para comprar
        self.RSI_BUY_THRESHOLD = 15    
        # ESTOS PARÁMETROS YA NO SE USAN EN EL MODO DCA
        self.RSI_SELL_THRESHOLD = 999 
        self.STOP_LOSS_PCT = 0.00    
        self.TAKE_PROFIT_PCT = 0.00 
        
        # --- CÁLCULOS DERIVADOS ---
        self.MAX_CAPITAL_ALLOCATION_PCT = 0.95 
        # La asignación por activo se calcula automáticamente en base a 1000
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
        print(f"📡 {Colors.BOLD}ESTRATEGIA:{Colors.ENDC} {Colors.OKGREEN}ACUMULACIÓN PURA (DCA en RSI bajo){Colors.ENDC}")

        print(f"\n{Colors.OKBLUE}=== 2. VELOCIDAD DE TICK DUAL ==={Colors.ENDC}")
        print(f"⏱️ {Colors.BOLD}INTERVALO DE EJECUCIÓN/API:{Colors.ENDC} {Colors.WARNING}{self.TICK_INTERVAL_SECONDS} segundos{Colors.ENDC} (Lógica de Trading)")
        print(f"🖥️ {Colors.BOLD}INTERVALO DE VISUALIZACIÓN:{Colors.ENDC} {Colors.OKCYAN}{self.DISPLAY_INTERVAL_SECONDS} segundos{Colors.ENDC} (Actualización de Pantalla)")
        print(f"📈 {Colors.BOLD}RSI PERIODO (Sensibilidad):{Colors.ENDC} {self.RSI_PERIOD} períodos")
        print(f"📉 {Colors.BOLD}RSI COMPRA (Umbral Extremo):{Colors.ENDC} {Colors.OKGREEN}{self.RSI_BUY_THRESHOLD}{Colors.ENDC} (SOLO COMPRA AQUÍ)")
        print(f"🛡️ {Colors.FAIL}STOP LOSS (SL):{Colors.ENDC} DESACTIVADO")
        print(f"🏆 {Colors.OKGREEN}TAKE PROFIT (TP):{Colors.ENDC} DESACTIVADO")
        
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
    """Clase para manejar precios en tiempo real y simulación de mercado."""
    def __init__(self, assets: list):
        self.api_ids = [v for k, v in CONFIG.COINGECKO_IDS.items() if k != 'BRCN']
        self.id_to_ticker = {v: k for k, v in CONFIG.COINGECKO_IDS.items()}
        self.COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
        self.current_prices = CONFIG.INITIAL_PRICES.copy() 
        self.previous_prices = CONFIG.INITIAL_PRICES.copy() # Nuevo para seguimiento de flechas
        
        # CORRECCIÓN DE ALPHA/BENCHMARK: Índice inicial = Capital inicial del portafolio.
        self.initial_market_index_value = CONFIG.INITIAL_USDC_BALANCE 
        self.market_index_history = [self.initial_market_index_value]
        
        self.last_api_call_time = time.time() - CONFIG.TICK_INTERVAL_SECONDS 

    # --- MÉTODO CORREGIDO/REINCORPORADO PARA EL ERROR ANTERIOR ---
    def fetch_initial_history(self, initial_ticks=CONFIG.INITIAL_HISTORY_TICKS):
        """Carga los datos iniciales (simulados) antes de que empiece el loop en vivo."""
        return self._simulate_initial_history(initial_ticks)

    def _simulate_initial_history(self, initial_ticks):
        print(f"\n[{Colors.OKCYAN}API{Colors.ENDC}] Cargando {initial_ticks} puntos de datos históricos iniciales (Mock)...")
        history_data = {}
        for ticker in CONFIG.ASSETS_TO_TRACK:
            initial_price = CONFIG.INITIAL_PRICES[ticker] 
            prices = [initial_price]
            # Simular una serie de precios que varía ligeramente
            for _ in range(initial_ticks - 1):
                current_price = prices[-1]
                change_pct = np.random.normal(0, 0.005) # Pequeña variación
                new_price = current_price * (1 + change_pct)
                prices.append(new_price)
            
            history_data[ticker] = pd.DataFrame(prices, columns=['Close'])
        return history_data
    # -----------------------------------------------------------------------------
        
    def fetch_latest_prices(self):
        updated_prices = {}
        if time.time() - self.last_api_call_time < CONFIG.TICK_INTERVAL_SECONDS:
            return self._mock_prices_only()
        
        self.last_api_call_time = time.time()
        self.previous_prices = self.current_prices.copy() # Guardar precios anteriores

        try:
            params = {'ids': ','.join(self.api_ids), 'vs_currencies': 'usd'}
            response = requests.get(self.COINGECKO_URL, params=params, timeout=5)
            response.raise_for_status()  
            data = response.json()
            
            for coin_id, price_data in data.items():
                if 'usd' in price_data:
                    ticker = self.id_to_ticker.get(coin_id)
                    if ticker:
                        updated_prices[ticker] = price_data['usd']
        
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}Error de conexión con CoinGecko ({e}). Usando precios de fallback simulados.{Colors.ENDC}")
            return self._fallback_mock_prices()
        
        for ticker in CONFIG.ASSETS_TO_TRACK:
            if ticker in updated_prices:
                self.current_prices[ticker] = updated_prices[ticker]
            elif ticker not in self.current_prices:
                self.current_prices[ticker] = CONFIG.INITIAL_PRICES[ticker] 
                
        self._update_mock_brcn_and_index()
        
        return self.current_prices

    def _update_mock_brcn_and_index(self):
        current = self.current_prices.get('BRCN', CONFIG.INITIAL_PRICES['BRCN'])
        change_pct = random.uniform(-0.0002, 0.0002) 
        self.current_prices['BRCN'] = current * (1 + change_pct)

        # Cálculo de nuevo valor de índice (Benchmark)
        price_changes = [
            (self.current_prices[ticker] - self.previous_prices[ticker]) / self.previous_prices[ticker]
            for ticker in CONFIG.ASSETS_TO_TRACK
            if ticker != 'BRCN' and self.previous_prices.get(ticker, 0) > 0
        ]
        
        avg_change_pct = np.mean(price_changes) if price_changes else 0.0
        
        previous_market_index_value = self.market_index_history[-1]
        new_market_index_value = previous_market_index_value * (1 + avg_change_pct)
        
        self.market_index_history.append(new_market_index_value)
        
    def _mock_prices_only(self):
        self.previous_prices = self.current_prices.copy()
        
        for ticker in CONFIG.ASSETS_TO_TRACK:
            current = self.current_prices.get(ticker, CONFIG.INITIAL_PRICES[ticker])
            # Variación mínima para ticks visuales (sin llamada API)
            change_pct = random.uniform(-0.000001, 0.000001) 
            self.current_prices[ticker] = current * (1 + change_pct)
        
        self._update_mock_brcn_and_index()
        return self.current_prices
        
    def _fallback_mock_prices(self):
        print(f"[{Colors.WARNING}API{Colors.ENDC}] Usando precios de fallback simulados para evitar interrupción.")
        self.previous_prices = self.current_prices.copy()

        for ticker in CONFIG.ASSETS_TO_TRACK:
            current = self.current_prices.get(ticker, CONFIG.INITIAL_PRICES[ticker])
            change_pct = random.uniform(-0.0002, 0.0002) 
            self.current_prices[ticker] = current * (1 + change_pct)
        
        self._update_mock_brcn_and_index()
        return self.current_prices

    def get_price_indicator(self, ticker: str):
        """Retorna el símbolo de flecha de dirección de precio."""
        current = self.current_prices.get(ticker, 0)
        previous = self.previous_prices.get(ticker, current)
        
        if current > previous:
            return f"{Colors.OKGREEN}\u25b2{Colors.ENDC}" # Flecha arriba verde
        elif current < previous:
            return f"{Colors.FAIL}\u25bc{Colors.ENDC}"  # Flecha abajo roja
        else:
            return f"{Colors.WARNING}\u25c6{Colors.ENDC}" # Rombo amarillo (sin cambio)

# ... (Clase TradingAsset se mantiene sin cambios en su lógica principal) ...
class TradingAsset:
    """Encapsula la lógica de trading para un solo par de activos."""
    
    def __init__(self, ticker: str, initial_usdc: float, price_history_df: pd.DataFrame, fetcher_instance):
        self.ticker = ticker
        self.usdc_balance = initial_usdc
        self.asset_balance = 0.0
        self.buy_price_avg = 0.0 
        self.transaction_log = []
        self.data = price_history_df.copy()
        self.current_tick_index = len(self.data) - 1 
        self.fetcher = fetcher_instance
        self.initial_usdc_balance = initial_usdc
        
        self.total_commissions = 0.0
        self.total_winning_pnl = 0.0 
        self.total_losing_pnl = 0.0  
        self.trades_closed = 0
        
        self._calculate_indicators()
        
    def set_new_price(self, new_price: float):
        self.current_tick_index += 1
        self.data.loc[len(self.data)] = new_price
        if len(self.data) > 300: 
            self.data = self.data.iloc[-300:].reset_index(drop=True)

    def _calculate_indicators(self):
        if len(self.data) < CONFIG.RSI_PERIOD:
            self.data['RSI'] = np.nan
            return

        delta = self.data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(span=CONFIG.RSI_PERIOD, adjust=False).mean()
        avg_loss = loss.ewm(span=CONFIG.RSI_PERIOD, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan) 
        self.data['RSI'] = 100 - (100 / (1 + rs))

    def _execute_trade(self, trade_type: str, current_price: float, qty_to_trade: float):
        """Simula o ejecuta una orden de COMPRA."""
        is_live = CONFIG.LIVE_TRADING_ENABLED
        side = 'BUY'
        product_id = f"{self.ticker}-USD"
        
        if is_live and self.ticker != 'BRCN': 
            # Implementar lógica de API de Coinbase/Binance aquí si LIVE es True
            # Nota: Esto es un placeholder, ya que no tengo acceso a tus credenciales
            # Simulación de ejecución exitosa
            executed_price = current_price * (1 + CONFIG.SLIPPAGE_PCT)
            executed_size = qty_to_trade
            return self._update_internal_state(trade_type, executed_price, executed_size)
            
        else:
            return self._simulate_trade(trade_type, current_price, qty_to_trade)

    def _update_internal_state(self, trade_type: str, execution_price: float, qty_executed: float):
        """Actualiza el balance interno tras una ejecución de COMPRA."""
        if qty_executed <= 0:
            return execution_price

        # Lógica de Compra (ÚNICA LÓGICA PERMITIDA)
        if 'BUY' in trade_type:
            final_price = execution_price
            cost = final_price * qty_executed
            commission_cost = cost * CONFIG.COMMISSION_PCT
            
            if self.usdc_balance < cost + commission_cost:
                 return final_price # Fallo por falta de fondos
                 
            # Cálculo de la Media de Compra (Ponderado)
            total_cost_viejo = self.buy_price_avg * self.asset_balance
            total_cost_nuevo = total_cost_viejo + cost
            self.asset_balance += qty_executed
            
            self.usdc_balance -= (cost + commission_cost)
            
            if self.asset_balance > 0:
                self.buy_price_avg = total_cost_nuevo / self.asset_balance
            
            pnl = 0.0 # PnL es CERO en una compra
            self.total_commissions += commission_cost
            
        else: 
            return execution_price

        # Registro de la transacción (Solo se registran COMPRAS)
        log_type = trade_type.replace('_MANUAL', ' (MANUAL)').replace('_INITIAL', ' (INITIAL)')

        self.transaction_log.append({
            'Tick': self.current_tick_index,
            'Asset': self.ticker,
            'Type': log_type,
            'Avg_Entry_Price': self.buy_price_avg, 
            'Exec_Price': final_price, 
            'Qty_Bought': qty_executed,
            'USDC_Remaining': self.usdc_balance,
            'Asset_Total': self.asset_balance,
            'Commission': commission_cost,
        })
        return final_price

    def _simulate_trade(self, trade_type: str, current_price: float, qty_to_trade: float):
        """Simula la ejecución para el modo de práctica."""
        execution_price = current_price * (1 + CONFIG.SLIPPAGE_PCT) 

        cost_estimate = execution_price * qty_to_trade * (1 + CONFIG.COMMISSION_PCT)
        if self.usdc_balance < cost_estimate:
             return current_price
        
        return self._update_internal_state(trade_type, execution_price, qty_to_trade)

    def run_tick(self, is_real_tick: bool):
        """Ejecuta un solo paso de Live Trading (Solo COMPRA)."""
        
        current_price = self.data['Close'].iloc[-1]
        self._calculate_indicators()
        
        if len(self.data) < CONFIG.RSI_PERIOD:
            return f"{Colors.WARNING}Cargando datos históricos...{Colors.ENDC}", False
            
        last_row = self.data.iloc[-1]
        rsi_value = last_row['RSI'] if 'RSI' in last_row and not np.isnan(last_row['RSI']) else 50
        
        bot_opinion = ""
        action_taken = False
        
        # --- Lógica de Display (Monitoreo) ---
        if self.asset_balance > 0.000001:
            pnl_actual_pct = ((current_price / self.buy_price_avg) - 1) * 100
            pnl_color = Colors.OKGREEN if pnl_actual_pct >= 0 else Colors.FAIL
            opinion = f"{Colors.OKCYAN}📊 ACUMULANDO: Avg. Entrada: ${self.buy_price_avg:,.4f}. PnL No Realizado: {pnl_color}{pnl_actual_pct:,.2f}%{Colors.ENDC}"
        else:
            opinion = f"Neutral: Buscando señal de Compra. RSI: {rsi_value:,.2f}"

        # -----------------------------------------------------
        # LÓGICA DE TRADING REAL (Solo se ejecuta en tick real)
        # -----------------------------------------------------

        if is_real_tick and self.ticker != 'BRCN': 
            
            buy_signal = rsi_value <= CONFIG.RSI_BUY_THRESHOLD
            
            if self.usdc_balance > 1 and buy_signal:
                # Compra fraccionada del 10% del capital restante asignado al activo
                usdc_to_spend = self.usdc_balance * CONFIG.USDC_TO_TRADE_PCT / 10 
                qty_to_buy = usdc_to_spend / current_price
                
                # Ejecutar la compra
                if self._execute_trade('BUY_DCA', current_price, qty_to_buy) != current_price:
                    opinion = f"{Colors.OKGREEN}🟢 COMPRA DCA: RSI Sobrevendido ({rsi_value:,.2f}). Ejecutando acumulación.{Colors.ENDC}"
                    action_taken = True 
                else:
                    opinion = f"{Colors.WARNING}Neutral: Falta de fondos para la compra fraccionada.{Colors.ENDC}"

        return opinion, action_taken

    def execute_manual_buy(self):
        """Ejecuta una compra manual."""
        if self.usdc_balance > 1:
            current_price = self.data['Close'].iloc[-1]
            usdc_to_spend = self.usdc_balance * CONFIG.USDC_TO_TRADE_PCT 
            qty_to_buy = usdc_to_spend / current_price
            return self._execute_trade('BUY_MANUAL', current_price, qty_to_buy)
        return False
        
    def close_final_position(self, final_price: float):
        current_value = self.usdc_balance + (self.asset_balance * final_price)
        return current_value 
        
    def get_current_value(self):
        last_price = self.data['Close'].iloc[-1]
        return self.usdc_balance + (self.asset_balance * last_price)
        
    def get_accumulated_metrics(self):
        """Retorna las métricas de acumulación para el reporte bancario."""
        return {
            'total_commissions': self.total_commissions,
            'final_usdc_balance': self.usdc_balance,
            'final_asset_balance': self.asset_balance,
            # Total invertido = Capital inicial asignado - USDC restante
            'total_invested': (self.initial_usdc_balance - self.usdc_balance) 
        }


# -----------------------------------------------------------
# 🏢 CLASE DE GESTIÓN DEL PORTAFOLIO MULTI-ACTIVO (LIVE)
# -----------------------------------------------------------

class PortfolioManager:
    """Gestiona múltiples activos y el flujo de la simulación."""
    
    def __init__(self, history_data_map: dict, fetcher_instance):
        self.initial_usdc_balance = CONFIG.INITIAL_USDC_BALANCE
        self.assets = {}
        # Inicializar cada activo con su porción de capital, pero sin posición inicial
        for ticker in CONFIG.ASSETS_TO_TRACK:
            self.assets[ticker] = TradingAsset(
                ticker=ticker,
                initial_usdc=CONFIG.CAPITAL_PER_ASSET,
                price_history_df=history_data_map[ticker],
                fetcher_instance=fetcher_instance
            )
        self.sim_tick_counter = 0
        self.visual_tick_counter = 0 
        # Inicializar el historial de valor del portafolio con el valor inicial
        self.portfolio_value_history = [self.initial_usdc_balance] * len(next(iter(history_data_map.values())))
        self.fetcher = fetcher_instance
        
    def _get_bank_details_current(self):
        """Obtiene las métricas de acumulación actuales para el display (CORREGIDO)."""
        total_commissions = 0.0
        total_usdc_spent = 0.0
        total_usdc_available = 0.0 
        
        for asset in self.assets.values():
            metrics = asset.get_accumulated_metrics()
            total_commissions += metrics['total_commissions']
            total_usdc_available += metrics['final_usdc_balance']
            total_usdc_spent += metrics['total_invested'] 
            
        # PnL no realizado (Unrealized PnL)
        total_value = sum(asset.get_current_value() for asset in self.assets.values())
        unrealized_pnl = total_value - self.initial_usdc_balance
        
        return total_usdc_spent, total_commissions, unrealized_pnl, total_usdc_available

    def interpret_profit(self, total_value: float):
        pnl = total_value - self.initial_usdc_balance
        return_pct = (pnl / self.initial_usdc_balance) * 100
        
        market_index_value = self.fetcher.market_index_history[-1]
        market_pnl_pct = ((market_index_value / self.fetcher.initial_market_index_value) - 1) * 100
        alpha = return_pct - market_pnl_pct
        
        portfolio_series = pd.Series(self.portfolio_value_history)
        returns = portfolio_series.pct_change().dropna().tail(CONFIG.RSI_PERIOD * 2) 
        recent_volatility = returns.std() * 100 if len(returns) >= 2 else 0.0
        
        description = f"{Colors.OKGREEN}MODO ACUMULACIÓN: Esperando puntos de entrada óptimos (RSI {CONFIG.RSI_BUY_THRESHOLD}).{Colors.ENDC}"
        action_comment = "Estrategia DCA pura. Buscando solo sobreventa."
        risk_assessment = f"{Colors.WARNING}Riesgo de volatilidad: {recent_volatility:,.2f}% (Solo afecta al PnL no realizado).{Colors.ENDC}"

        return description, action_comment, market_pnl_pct, alpha, recent_volatility

    def display_status(self, time_until_next_execution: float, asset_opinions: dict):
        """Muestra la interfaz de demo en vivo (Actualizada con flechas)."""
        os.system('cls' if os.name == 'nt' else 'clear')

        total_value = sum(asset.get_current_value() for asset in self.assets.values())
        pnl_percent = ((total_value - self.initial_usdc_balance) / self.initial_usdc_balance) * 100
        
        pnl_color = Colors.OKGREEN if pnl_percent >= 0 else Colors.FAIL
        
        mode = "LIVE DCA 🔴" if CONFIG.LIVE_TRADING_ENABLED else "SIMULACIÓN DCA 🟢"
        
        print(f"{Colors.HEADER}="*100 + Colors.ENDC)
        print(f"| {Colors.OKBLUE}{pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC} | Ticks Lógica Ejecutada: {self.sim_tick_counter} | Ticks Visuales: {self.visual_tick_counter}")
        print(f"|  🤖 {Colors.BOLD}BORITRACKER V6.5 - MODO {mode}{Colors.ENDC} | Activos: {len(self.assets)} | Fuente: CoinGecko/BRCN")
        print(f"{Colors.HEADER}="*100 + Colors.ENDC)
        
        market_desc, action_comment, market_pnl_pct, alpha, volatility_pct = self.interpret_profit(total_value)
        
        # Uso de los valores corregidos
        total_invested, total_commissions, unrealized_pnl, usdc_remaining = self._get_bank_details_current()
        pnl_cerrado_color = Colors.OKGREEN if unrealized_pnl >= 0 else Colors.FAIL
        
        # --- SECCIÓN ACUMULACIÓN/INVERSIÓN ---
        print(f"📈 {Colors.BOLD}RESUMEN DE RENDIMIENTO DE LA SESIÓN{Colors.ENDC}")
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)
        
        # VALORES CLAVE AJUSTADOS
        print(f"💰 {Colors.BOLD}PORTAFOLIO VALOR TOTAL:{Colors.ENDC} ${total_value:,.2f}")
        print(f"💵 {Colors.BOLD}INVERSIÓN TOTAL ACUMULADA (GASTADO):{Colors.ENDC} ${total_invested:,.4f}")
        print(f"💸 {Colors.BOLD}USDC RESTANTE (DISPONIBLE):{Colors.ENDC} ${usdc_remaining:,.4f}")
        print(f"  --- PNL NO REALIZADO (VALOR DE MERCADO) ---")
        print(f"  💸 {Colors.BOLD}PNL NO REALIZADO (UNREALIZED PNL):{Colors.ENDC} {pnl_cerrado_color}${unrealized_pnl:,.4f}{Colors.ENDC}")
        print(f"  📊 {Colors.BOLD}RENDIMIENTO NETO (Sesión):{Colors.ENDC} {pnl_color}{pnl_percent:,.2f}%{Colors.ENDC} (vs. Inicial: ${self.initial_usdc_balance:,.2f})")
        
        # 2. Comparación con el Benchmark
        pnl_color_market = Colors.OKGREEN if market_pnl_pct >= 0 else Colors.FAIL
        alpha_color = Colors.OKGREEN if alpha >= 0 else Colors.FAIL
        print(f"🌐 {Colors.BOLD}BENCHMARK del Mercado (Índice):{Colors.ENDC} {pnl_color_market}{market_pnl_pct:,.2f}%{Colors.ENDC}")
        print(f"⭐ {Colors.BOLD}ALPHA (Valor Agregado):{Colors.ENDC} {alpha_color}{alpha:,.2f}%{Colors.ENDC}")
        
        # 3. Drawdown de la Sesión (Riesgo Actual)
        portfolio_series = pd.Series(self.portfolio_value_history)
        peak_value = portfolio_series.max()
        drawdown_pct = ((peak_value - total_value) / peak_value) * 100 if peak_value > 0 else 0
        drawdown_color = Colors.FAIL if drawdown_pct >= 0.5 else Colors.WARNING
        print(f"🛡️ {Colors.BOLD}DRAWDOWN ACTUAL (No Realizado):{Colors.ENDC} {drawdown_color}-{drawdown_pct:,.2f}%{Colors.ENDC} (Máxima caída temporal desde el pico: ${peak_value:,.2f})")
        
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)

        # Análisis Global
        print(f"  🧠 {Colors.BOLD}ANÁLISIS DE RIESGO Y ESTRATEGIA (DCA):{Colors.ENDC}")
        print(f"  > 📉 **Volatilidad Reciente (Riesgo):** {self._format_risk_assessment(volatility_pct, market_desc)}{Colors.ENDC}") 
        print(f"  > 🚀 **Rendimiento General (Beta/Alpha):** {market_desc}")
        print(f"  🎯 {Colors.BOLD}DECISIÓN ESTRATÉGICA (Recomendación):{Colors.ENDC} **{action_comment}**")
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)
        
        print(f"  📊 {Colors.BOLD}DETALLE DE ACTIVOS Y SEÑALES EN TIEMPO REAL{Colors.ENDC}")
        
        static_assets = [(ticker, self.assets[ticker]) for ticker in CONFIG.ASSETS_TO_TRACK]
        
        # Encabezado de la tabla
        print(f"{'Activo':<8} | {'Precio (Tendencia)':<20} | {'RSI':<6} | {'Qty Acumulada':<13} | {'Avg. Entrada':<12} | {'Opinión/Decisión del Bot (Señal)':<50}")
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)

        for ticker, asset in static_assets: 
            current_price = asset.data['Close'].iloc[-1]
            last_rsi = asset.data['RSI'].iloc[-1] if not asset.data.empty and 'RSI' in asset.data.columns else np.nan
            
            rsi_color = Colors.OKGREEN if (not np.isnan(last_rsi) and last_rsi <= CONFIG.RSI_BUY_THRESHOLD) else (Colors.FAIL if (not np.isnan(last_rsi) and last_rsi >= CONFIG.RSI_SELL_THRESHOLD) else Colors.ENDC)
            rsi_display = f"{last_rsi:,.2f}" if not np.isnan(last_rsi) else "N/A"
            
            qty_display = f"{asset.asset_balance:,.4f}"
            avg_entry_display = f"${asset.buy_price_avg:,.4f}" if asset.asset_balance > 0 else "---"

            opinion = asset_opinions.get(ticker, f"{Colors.WARNING}Esperando datos...{Colors.ENDC}")
            
            if ticker == 'BRCN':
                 ticker_display = f"{Colors.BOLD}{Colors.OKGREEN}BRCN{Colors.ENDC}"
            else:
                 ticker_display = ticker

            # MEJORA: Indicador de precio con flechas
            price_indicator = self.fetcher.get_price_indicator(ticker)
            price_display = f"${current_price:,.4f} {price_indicator}"


            print(f"{ticker_display:<8} | {price_display:<20} | {rsi_color}{rsi_display}{Colors.ENDC} | {qty_display:<13} | {avg_entry_display:<12} | {opinion}")

            
        print(f"{Colors.OKCYAN}-" * 100 + Colors.ENDC)
        
        time_until_next_execution_display = max(0, time_until_next_execution)
        print(f"[{Colors.OKBLUE}INFO{Colors.ENDC}] Próxima EJECUCIÓN de API/Lógica en: {time_until_next_execution_display:.1f} segundos.")
        print(f"🕹️ {Colors.BOLD}CONTROLES MANUALES:{Colors.ENDC} Usa **Ctrl+C** para detener la simulación y generar el reporte final.")

    def _format_risk_assessment(self, volatility_pct, market_desc):
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
        """Función principal para el loop de trading."""
        
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
                
                self.display_status(time_until_next_execution, asset_opinions) 
                
                self. _handle_input()
                
                time.sleep(CONFIG.DISPLAY_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            print("\n\n>>> 🛑 SIMULACIÓN DETENIDA: Solicitud de interrupción del usuario (Ctrl+C). Generando reporte final...")
            
        final_prices = self.fetcher.current_prices 
        final_value = sum(asset.usdc_balance + (asset.asset_balance * final_prices[ticker]) for ticker, asset in self.assets.items())
        
        for asset in self.assets.values(): 
            final_log.extend(asset.transaction_log)

        if final_log:
            final_df = pd.DataFrame(final_log)
        else:
            final_df = pd.DataFrame(columns=['Tick', 'Asset', 'Type', 'Avg_Entry_Price', 'Exec_Price', 'Qty_Bought', 'USDC_Remaining', 'Asset_Total', 'Commission'])
            
        return final_df, self.sim_tick_counter, final_value
    
    def _calculate_metrics(self, final_value: float, total_ticks: int) -> dict:
        """Calcula métricas clave de rendimiento para el modo DCA."""
        
        total_pnl = final_value - self.initial_usdc_balance
        return_pct = (total_pnl / self.initial_usdc_balance) * 100
        
        total_commissions = 0.0
        total_invested = 0.0
        total_usdc_available = 0.0
        
        for asset in self.assets.values():
            metrics = asset.get_accumulated_metrics()
            total_commissions += metrics['total_commissions']
            total_invested += metrics['total_invested']
            total_usdc_available += metrics['final_usdc_balance']
        
        unrealized_pnl = final_value - self.initial_usdc_balance 

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

        peak = portfolio_series.cummax() 
        drawdown = (portfolio_series - peak) / peak 
        max_drawdown = drawdown.min() * 100
            
        return {
            "Valor Final Total (Mercado)": f"${final_value:,.2f}",
            "Capital Invertido Neto": f"${total_invested:,.2f}",
            "PnL No Realizado (Total)": f"${unrealized_pnl:,.2f}",
            "Rendimiento (%)": f"{return_pct:,.2f}%",
            "Total Ticks (Lógica)": total_ticks,
            "Acumulaciones Bancarias": { 
                "Capital Invertido (Neto)": total_invested,
                "Comisiones Totales": total_commissions,
                "USDC Disponible": total_usdc_available
            },
            "Volatilidad Anualizada (%)": f"{volatility*100:,.2f}%",
            "Drawdown Máximo (%)": f"{abs(max_drawdown):,.2f}%",
            "Sharpe Ratio": f"{sharpe_ratio:,.2f}",
            "Sortino Ratio": "N/A (Solo Compras)",
            "Avg. Recompensa/Riesgo (G/P)": "N/A (Solo Compras)"
        }

    def generate_report(self, log_df: pd.DataFrame, final_value: float, total_ticks: int):
        """Genera el reporte final para el modo DCA."""
        
        metrics = self._calculate_metrics(final_value, total_ticks)
        bank_details = metrics.pop("Acumulaciones Bancarias") 
        
        print("\n\n" + f"{Colors.HEADER}="*60 + Colors.ENDC)
        print(f"📊 {Colors.BOLD}REPORTE FINAL DE ACUMULACIÓN (DCA Pura){Colors.ENDC}")
        print(f"Fuente: CoinGecko/Mock | Ticks de Lógica: {total_ticks} | Ticks Visuales: {self.visual_tick_counter}")
        print(f"{Colors.HEADER}="*60 + Colors.ENDC)
        
        # --- SECCIÓN CLAVE: DETALLE BANCARIO DESGLOSADO ---
        print(f"\n💰 {Colors.BOLD}DETALLE DE FONDOS Y ACUMULACIÓN{Colors.ENDC}")
        print("-" * 60)
        
        unrealized_pnl = final_value - self.initial_usdc_balance
        pnl_color = Colors.OKGREEN if unrealized_pnl >= 0 else Colors.FAIL
        
        print(f"💵 Capital Inicial Total:     ${self.initial_usdc_balance:,.2f}")
        print(f"------------------------------------------------------------")
        print(f"🟢 Capital Invertido (Neto):  ${bank_details['Capital Invertido (Neto)']:,.4f}")
        print(f"➖ Comisiones Totales:        {Colors.FAIL}-${bank_details['Comisiones Totales']:,.4f}{Colors.ENDC}")
        print(f"------------------------------------------------------------")
        print(f"💸 USDC Disponible (Caja):  ${bank_details['USDC Disponible']:,.2f}")
        print(f"📈 {Colors.BOLD}VALOR FINAL TOTAL:{Colors.ENDC}         {pnl_color}${final_value:,.2f}{Colors.ENDC}")
        print("-" * 60)
        print(f"✅ PnL NO REALIZADO (Unrealized): {pnl_color}${unrealized_pnl:,.2f}{Colors.ENDC}")
        print("-" * 60)
        
        # --- MÉTRICAS AVANZADAS ---
        print(f"\n🧠 {Colors.BOLD}MÉTRICAS AVANZADAS DEL PORTAFOLIO{Colors.ENDC}")
        print("-" * 60)
        for key, value in metrics.items():
            color = Colors.OKGREEN if 'Rendimiento' in key and final_value > self.initial_usdc_balance else Colors.ENDC
            print(f"{key:<35}: {color}{value:>20}{Colors.ENDC}")
        print("-" * 60)
        
        print(f"\n📈 {Colors.BOLD}RESUMEN DE ACUMULACIÓN POR ACTIVO:{Colors.ENDC}")
        asset_summary = []
        for ticker, asset in self.assets.items():
            final_price = asset.data['Close'].iloc[-1]
            current_value = asset.usdc_balance + (asset.asset_balance * final_price)
            pnl_unrealized = current_value - CONFIG.CAPITAL_PER_ASSET
            pct = (pnl_unrealized / CONFIG.CAPITAL_PER_ASSET) * 100
            
            asset_summary.append({
                'Activo': ticker,
                'Qty Acumulada': asset.asset_balance,
                'Avg. Entrada': asset.buy_price_avg,
                'PnL No Realizado': pnl_unrealized,
                'Rendimiento (%)': pct,
            })

        summary_df = pd.DataFrame(asset_summary)
        print(summary_df.to_string(index=False, float_format="%.4f"))

        print(f"\n📜 {Colors.BOLD}REGISTRO CONSOLIDADO DE TRANSACCIONES (Últimas 10 Compras):{Colors.ENDC}")
        
        if not log_df.empty:
            log_display_df = log_df[['Tick', 'Asset', 'Type', 'Avg_Entry_Price', 'Exec_Price', 'Qty_Bought', 'USDC_Remaining', 'Asset_Total', 'Commission']].tail(10).copy()
            
            def format_log_value(x):
                try:
                    return f"{float(x):,.4f}"
                except (TypeError, ValueError):
                    return str(x)
                
            for col in ['Avg_Entry_Price', 'Exec_Price', 'Qty_Bought', 'USDC_Remaining', 'Asset_Total', 'Commission']:
                if col in log_display_df.columns:
                    log_display_df[col] = pd.to_numeric(log_display_df[col], errors='coerce').apply(format_log_value)
            
            print(log_display_df.to_string(index=False))
        else:
            print("--- NO HAY COMPRAS REGISTRADAS EN ESTA SIMULACIÓN ---")
        
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
        plt.title(f'Evolución del Valor del Portafolio - {total_ticks} Ticks de Lógica (MODO DCA)')
        plt.xlabel(f'Visual Ticks (Actualización cada {CONFIG.DISPLAY_INTERVAL_SECONDS}s)')
        plt.ylabel('Valor en USDC')
        plt.grid(axis='y', linestyle='-', alpha=0.5)
        plt.legend()
        plt.show()

# --- PUNTO DE ENTRADA ---
if __name__ == '__main__':
    
    print(f"\n{Colors.HEADER}====================================================={Colors.ENDC}")
    print(f"  {Colors.BOLD}BORITRACKER V6.5 - MODO ACUMULACIÓN (DCA){Colors.ENDC}")
    print(f"  {Colors.WARNING}Solo Compras en RSI bajo | No hay Ventas (SL/TP desactivados){Colors.ENDC}")
    print(f"{Colors.HEADER}====================================================={Colors.ENDC}")
    
    # Menú de selección
    print(f"\nSeleccione el modo de operación:")
    print(f"1. {Colors.OKCYAN}Modo SIMULACIÓN{Colors.ENDC} (Recomendado para pruebas)")
    print(f"2. {Colors.FAIL}Modo LIVE TRADING{Colors.ENDC} (Requiere API Key real y opera en Coinbase)")
    
    mode_choice = input(f"\nSeleccione un modo (1 o 2) y presione Enter: ")
    
    if mode_choice == '2':
        confirm = input(f"{Colors.FAIL}ADVERTENCIA:{Colors.ENDC} ¿Está seguro que desea activar el **LIVE TRADING**? (S/N): ").lower()
        if confirm == 's':
            CONFIG.LIVE_TRADING_ENABLED = True
            print(f"{Colors.OKGREEN}Modo LIVE TRADING ACTIVADO.{Colors.ENDC} ¡Operaciones reales en camino!")
        else:
            print(f"{Colors.WARNING}Volviendo al Modo Simulación. Analicemos primero la estrategia.{Colors.ENDC}")
            
    current_mode = "LIVE DCA" if CONFIG.LIVE_TRADING_ENABLED else "SIMULACIÓN DCA"
    CONFIG.display_options(current_mode)

    # 1. Carga Inicial
    temp_fetcher = LiveFetcher(CONFIG.ASSETS_TO_TRACK) 
    # La corrección está aquí: la función fetch_initial_history ya está en LiveFetcher
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

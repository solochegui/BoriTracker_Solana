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

# --- Códigos ANSI para colores ---
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
# 📝 CONFIGURACIÓN DEL BOT Y PARÁMETROS (EXTENDIDA)
# -----------------------------------------------------------
class BotConfiguration:
    """
    Clase centralizada para definir todos los parámetros de configuración, 
    gestión de riesgo y estrategia del BoriTracker.
    """
    def __init__(self):
        
        # ==========================================================
        # 💰 PARÁMETROS DE CAPITAL Y PLATAFORMA (Coinbase)
        # ==========================================================
        self.INITIAL_USDC_BALANCE = 1000.00
        # Porcentaje del capital total que se asigna a una posición
        self.MAX_CAPITAL_ALLOCATION_PCT = 0.95 
        # Comisión de la plataforma (simulada)
        self.COMMISSION_PCT = 0.003  # 0.3%
        # Deslizamiento simulado por la ejecución de la orden
        self.SLIPPAGE_PCT = 0.001    # 0.1% 
        
        # ==========================================================
        # ⏳ PARÁMETROS DE TIEMPO Y SIMULACIÓN
        # ==========================================================
        self.TICK_INTERVAL_SECONDS = 5
        # Periodo RSI * 2 para asegurar datos iniciales (28 ticks por defecto)
        self.INITIAL_HISTORY_TICKS = 28 
        # Límite máximo de ticks de simulación antes de detenerse automáticamente (0 = Infinito)
        self.MAX_SIMULATION_TICKS = 0 
        
        # ==========================================================
        # 📊 ESTRATEGIA RSI Y GESTIÓN DE RIESGO
        # ==========================================================
        # Periodo (lookback) para el cálculo del RSI (14 es estándar)
        self.RSI_PERIOD = 14
        # Umbral bajo: RSI <= 25 (Señal de COMPRA / Sobrevendido)
        self.RSI_BUY_THRESHOLD = 25    
        # Umbral alto: RSI >= 75 (Señal de VENTA / Sobrecomprado)
        self.RSI_SELL_THRESHOLD = 75   
        
        # Stop Loss: Porcentaje de pérdida aceptable desde el precio de entrada
        self.STOP_LOSS_PCT = 0.03    # 3%
        # Take Profit: Porcentaje de ganancia para cerrar automáticamente
        self.TAKE_PROFIT_PCT = 0.15  # 15%
        
        # ==========================================================
        # 🌐 ACTIVOS Y PRECIOS INICIALES
        # ==========================================================
        self.ASSETS_TO_TRACK = [
            'BRCN', 'SOL', 'JUP', 'PYTH', 'RENDER', 
            'BONK', 'ETH', 'LINK', 'AVAX', 'DOGE'
        ] 
        self.INITIAL_PRICES = { 
            'BRCN': 0.50, 'SOL': 150.00, 'JUP': 1.00, 'PYTH': 0.50, 'RENDER': 7.50, 
            'BONK': 0.000025, 'ETH': 3500.00, 'LINK': 15.00, 'AVAX': 30.00, 'DOGE': 0.15
        }
        
        # --- CÁLCULOS DERIVADOS ---
        self.CAPITAL_PER_ASSET = self.INITIAL_USDC_BALANCE / len(self.ASSETS_TO_TRACK)
        self.USDC_TO_TRADE_PCT = self.MAX_CAPITAL_ALLOCATION_PCT

    def display_options(self):
        """Muestra los parámetros de configuración en el inicio."""
        print(f"{Colors.HEADER}="*70)
        print(f"💻 {Colors.BOLD}CONFIGURACIÓN ACTUAL DEL BOT (DEMO) V4.3{Colors.ENDC}")
        print(f"{Colors.HEADER}="*70 + Colors.ENDC)
        
        print(f"\n{Colors.OKBLUE}=== 1. CAPITAL Y PLATAFORMA ==={Colors.ENDC}")
        print(f"💰 {Colors.BOLD}CAPITAL INICIAL:{Colors.ENDC} ${self.INITIAL_USDC_BALANCE:,.2f}")
        print(f"💼 {Colors.BOLD}ASIGNACIÓN MÁXIMA POR TRADE:{Colors.ENDC} {self.MAX_CAPITAL_ALLOCATION_PCT*100}% del capital disponible.")
        print(f"💸 {Colors.BOLD}COMISIÓN (Simulada):{Colors.ENDC} {self.COMMISSION_PCT*100}%")
        print(f"🌪️ {Colors.BOLD}SLIPPAGE (Simulado):{Colors.ENDC} {self.SLIPPAGE_PCT*100}%")
        
        print(f"\n{Colors.OKBLUE}=== 2. TIEMPO Y SIMULACIÓN ==={Colors.ENDC}")
        print(f"⏳ {Colors.BOLD}INTERVALO DE TICK:{Colors.ENDC} {self.TICK_INTERVAL_SECONDS} segundos")
        print(f"📚 {Colors.BOLD}TICKS HISTÓRICOS INICIALES:{Colors.ENDC} {self.INITIAL_HISTORY_TICKS} (Necesario para RSI)")
        print(f"🛑 {Colors.BOLD}LÍMITE DE TICKS (0=∞):{Colors.ENDC} {self.MAX_SIMULATION_TICKS}")
        
        print(f"\n{Colors.OKBLUE}=== 3. ESTRATEGIA RSI Y RIESGO ==={Colors.ENDC}")
        print(f"📈 {Colors.BOLD}RSI PERIODO:{Colors.ENDC} {self.RSI_PERIOD} períodos")
        print(f"🟢 {Colors.BOLD}RSI COMPRA (Sobrevendido):{Colors.ENDC} <={self.RSI_BUY_THRESHOLD}")
        print(f"🔴 {Colors.BOLD}RSI VENTA (Sobrecomprado):{Colors.ENDC} >={self.RSI_SELL_THRESHOLD}")
        print(f"🛡️ {Colors.FAIL}STOP LOSS (SL):{Colors.ENDC} {self.STOP_LOSS_PCT*100}%")
        print(f"🏆 {Colors.OKGREEN}TAKE PROFIT (TP):{Colors.ENDC} {self.TAKE_PROFIT_PCT*100}%")
        
        print(f"\n{Colors.OKBLUE}=== 4. ACTIVOS ==={Colors.ENDC}")
        print(f"🌐 {Colors.BOLD}ACTIVOS MONITOREADOS:{Colors.ENDC} {', '.join(self.ASSETS_TO_TRACK)}")
        print(f"{Colors.HEADER}="*70 + Colors.ENDC + "\n")


# Inicializar la configuración global
CONFIG = BotConfiguration()
RSI_PERIOD = CONFIG.RSI_PERIOD

# -----------------------------------------------------------
# 🔌 CLASE DE CONEXIÓN A LA API (PLACEHOLDER)
# -----------------------------------------------------------
class LiveFetcher:
    """Simula la conexión y obtención de precios de la API de Coinbase."""
    
    def __init__(self, assets: list):
        self.product_ids = [f"{ticker}-USDC" for ticker in assets]
        self.current_prices = CONFIG.INITIAL_PRICES.copy() 
        self.market_index_history = [CONFIG.INITIAL_USDC_BALANCE] 
        
    def fetch_latest_prices(self):
        """
        🛑 REEMPLAZAR: CÓDIGO REAL DE LA API DE COINBASE (Live Prices) 🛑
        """
        # --- MOCK DE TIEMPO REAL (Simula el cambio) ---
        total_market_value_change = 0
        for ticker in CONFIG.ASSETS_TO_TRACK:
            current = self.current_prices[ticker]
            change_pct = random.uniform(-0.0002, 0.0002) 
            self.current_prices[ticker] = current * (1 + change_pct)
            total_market_value_change += change_pct * CONFIG.CAPITAL_PER_ASSET
        
        last_index = self.market_index_history[-1]
        market_change = (total_market_value_change / CONFIG.INITIAL_USDC_BALANCE) * last_index
        self.market_index_history.append(last_index + market_change)
        
        return self.current_prices

    def fetch_initial_history(self, initial_ticks=CONFIG.INITIAL_HISTORY_TICKS):
        """Simula la carga de datos históricos para inicializar indicadores."""
        print(f"\n[{Colors.OKCYAN}API{Colors.ENDC}] Cargando {initial_ticks} puntos de datos históricos iniciales...")
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
    
    def __init__(self, ticker: str, initial_usdc: float, price_history_df: pd.DataFrame):
        self.ticker = ticker
        self.usdc_balance = initial_usdc
        self.asset_balance = 0.0
        self.position = 0
        self.buy_price = 0.0 
        self.transaction_log = []
        self.data = price_history_df.copy()
        self.current_tick_index = len(self.data) - 1 
        self.pnl_history = [initial_usdc] * len(self.data) 
        
    def set_new_price(self, new_price: float):
        self.current_tick_index += 1
        self.data.loc[len(self.data)] = new_price
        if len(self.data) > 300: 
            self.data = self.data.iloc[-300:].reset_index(drop=True)
            
    def _calculate_indicators(self):
        delta = self.data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(span=CONFIG.RSI_PERIOD, adjust=False).mean()
        avg_loss = loss.ewm(span=CONFIG.RSI_PERIOD, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan) 
        self.data['RSI'] = 100 - (100 / (1 + rs))

    def _simulate_trade(self, type: str, current_price: float, qty_to_trade: float):
        if qty_to_trade <= 0:
            return current_price

        # Aplicar Slippage
        if type in ('BUY', 'BUY_MANUAL'):
            final_price = current_price * (1 + CONFIG.SLIPPAGE_PCT)
        elif type in ('SELL', 'CLOSE', 'SELL_SL', 'SELL_TP', 'SELL_MANUAL'):
            final_price = current_price * (1 - CONFIG.SLIPPAGE_PCT)
        else:
            final_price = current_price

        pnl = 0.0
        if type in ('SELL', 'CLOSE', 'SELL_SL', 'SELL_TP', 'SELL_MANUAL') and self.position == 1:
            pnl = (final_price - self.buy_price) * qty_to_trade 
        
        if type in ('BUY', 'BUY_MANUAL'):
            self.buy_price = final_price 

        commission_cost = 0.0

        if type in ('BUY', 'BUY_MANUAL'):
            cost = final_price * qty_to_trade
            commission_cost = cost * CONFIG.COMMISSION_PCT
            
            if self.usdc_balance < cost + commission_cost:
                return current_price 
            
            self.usdc_balance -= (cost + commission_cost)
            self.asset_balance += qty_to_trade
            self.position = 1

        elif type in ('SELL', 'CLOSE', 'SELL_SL', 'SELL_TP', 'SELL_MANUAL'):
            revenue = final_price * qty_to_trade
            commission_cost = revenue * CONFIG.COMMISSION_PCT

            self.usdc_balance += (revenue - commission_cost)
            self.asset_balance -= qty_to_trade
            if self.asset_balance < 0.000001:
                self.position = 0
                self.asset_balance = 0.0
        
        log_type = type if 'MANUAL' not in type else type.replace('_MANUAL', ' (MANUAL)')

        self.transaction_log.append({
            'Tick': self.current_tick_index,
            'Asset': self.ticker,
            'Type': log_type,
            'Entry_Price': self.buy_price, 
            'Exec_Price': final_price, 
            'Qty': qty_to_trade,
            'PnL': pnl,
            'Commission': commission_cost,
            'USDC_Balance': self.usdc_balance,
            'Asset_Balance': self.asset_balance
        })
        
        return final_price

    def run_tick(self):
        """Ejecuta un solo paso de Live Trading (Lógica Automática)."""
        
        current_price = self.data['Close'].iloc[-1]
        self._calculate_indicators()
        
        total_value = self.usdc_balance + (self.asset_balance * current_price)
        self.pnl_history.append(total_value)
        
        if len(self.data) < CONFIG.RSI_PERIOD:
            return True
            
        last_row = self.data.iloc[-1]
            
        # 1. GESTIÓN DE RIESGO (SL/TP - Automático)
        if self.position == 1:
            stop_loss_price = self.buy_price * (1 - CONFIG.STOP_LOSS_PCT)
            take_profit_price = self.buy_price * (1 + CONFIG.TAKE_PROFIT_PCT)
            qty_to_sell = self.asset_balance

            if current_price <= stop_loss_price:
                self._simulate_trade('SELL_SL', current_price, qty_to_sell)
                print(f"[{self.ticker}] {Colors.FAIL}🛑 SL ejecutado{Colors.ENDC}: {qty_to_sell:,.4f} @ ${current_price:,.4f}")
            
            elif current_price >= take_profit_price:
                self._simulate_trade('SELL_TP', current_price, qty_to_sell)
                print(f"[{self.ticker}] {Colors.OKGREEN}🟢 TP ejecutado{Colors.ENDC}: {qty_to_sell:,.4f} @ ${current_price:,.4f}")
        
        # 2. ESTRATEGIA RSI (Automático)
        buy_signal = last_row['RSI'] <= CONFIG.RSI_BUY_THRESHOLD
        sell_signal = last_row['RSI'] >= CONFIG.RSI_SELL_THRESHOLD

        if self.position == 0 and buy_signal and self.usdc_balance > 1:
            usdc_to_spend = self.usdc_balance * CONFIG.USDC_TO_TRADE_PCT
            qty_to_buy = usdc_to_spend / current_price
            self._simulate_trade('BUY', current_price, qty_to_buy)
            print(f"[{self.ticker}] {Colors.OKGREEN}🟢 COMPRA ejecutada (RSI Auto){Colors.ENDC}: {qty_to_buy:,.4f} @ ${current_price:,.4f}")
        
        elif self.position == 1 and sell_signal:
            qty_to_sell = self.asset_balance
            self._simulate_trade('SELL', current_price, qty_to_sell)
            print(f"[{self.ticker}] {Colors.FAIL}🔴 VENTA ejecutada (RSI Auto){Colors.ENDC}: {qty_to_sell:,.4f} @ ${current_price:,.4f}")

        return True

    def execute_manual_buy(self):
        """Ejecuta una compra manual."""
        if self.position == 0 and self.usdc_balance > 1:
            current_price = self.data['Close'].iloc[-1]
            usdc_to_spend = self.usdc_balance * CONFIG.USDC_TO_TRADE_PCT
            qty_to_buy = usdc_to_spend / current_price
            self._simulate_trade('BUY_MANUAL', current_price, qty_to_buy)
            return True
        return False

    def execute_manual_sell(self):
        """Ejecuta una venta manual."""
        if self.position == 1 and self.asset_balance > 0.000001:
            current_price = self.data['Close'].iloc[-1]
            qty_to_sell = self.asset_balance
            self._simulate_trade('SELL_MANUAL', current_price, qty_to_sell)
            return True
        return False
    
    def close_final_position(self, final_price: float):
        if self.position == 1:
            self._simulate_trade('CLOSE', final_price, self.asset_balance)
            self.position = 0
        return self.usdc_balance
        
    def get_current_value(self):
        last_price = self.data['Close'].iloc[-1]
        return self.usdc_balance + (self.asset_balance * last_price)
        
    def get_win_rate(self):
        """Calcula el porcentaje de operaciones cerradas con ganancia."""
        closed_trades = pd.DataFrame(self.transaction_log)
        if closed_trades.empty:
            return 0.0, 0
        
        closed_trades = closed_trades[closed_trades['Type'].str.contains('SELL|CLOSE')].copy()
        if closed_trades.empty:
             return 0.0, 0
             
        closed_trades['PnL_float'] = pd.to_numeric(closed_trades['PnL'])
        winning_trades = closed_trades[closed_trades['PnL_float'] > 0]
        
        return (len(winning_trades) / len(closed_trades)) * 100, len(closed_trades)


# -----------------------------------------------------------
# 🏢 CLASE DE GESTIÓN DEL PORTAFOLIO MULTI-ACTIVO (LIVE)
# -----------------------------------------------------------

class PortfolioManager:
    """Gestiona múltiples activos y el flujo de la simulación."""
    
    def __init__(self, history_data_map: dict):
        self.initial_usdc_balance = CONFIG.INITIAL_USDC_BALANCE
        self.assets = {}
        for ticker in CONFIG.ASSETS_TO_TRACK:
            self.assets[ticker] = TradingAsset(
                ticker=ticker,
                initial_usdc=CONFIG.CAPITAL_PER_ASSET,
                price_history_df=history_data_map[ticker]
            )
        self.sim_tick_counter = 0
        self.portfolio_value_history = [self.initial_usdc_balance] * len(next(iter(history_data_map.values())))
        self.fetcher = LiveFetcher(CONFIG.ASSETS_TO_TRACK)

    def _is_key_pressed(self):
        """Revisa si se ha presionado una tecla sin bloquear la ejecución."""
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def interpret_profit(self, total_value: float):
        """Proporciona una descripción del rendimiento general del portafolio, incluyendo benchmarking."""
        pnl = total_value - self.initial_usdc_balance
        return_pct = (pnl / self.initial_usdc_balance) * 100
        
        market_index_value = self.fetcher.market_index_history[-1]
        market_pnl = market_index_value - self.initial_usdc_balance
        market_pnl_pct = (market_pnl / self.initial_usdc_balance) * 100
        
        description = ""
        action_comment = ""
        
        if return_pct >= 0.5 and pnl > market_pnl:
            description = f"{Colors.OKGREEN}**OUTPERFORMING**: Bot supera al mercado. ¡Racha de ganancias!{Colors.ENDC}"
            action_comment = "Mantener estrategia y asegurar TP."
        elif return_pct >= 0.0:
            description = f"{Colors.OKGREEN}Ganancia leve: El bot está en verde, riesgo controlado.{Colors.ENDC}"
            action_comment = "Monitorear de cerca."
        elif pnl > market_pnl:
            description = f"{Colors.WARNING}Pérdida mínima: Bot sufre menos que el mercado (Defensa activa).{Colors.ENDC}"
            action_comment = "Permitir al bot ejecutar SL."
        else:
            description = f"{Colors.FAIL}**UNDERPERFORMING**: Pérdida y el bot se rezaga del mercado.{Colors.ENDC}"
            action_comment = "Considerar VENTA MANUAL o ajustes SL."
            
        return description, action_comment, market_pnl_pct

    def display_status(self, next_tick_in: float):
        """Muestra la interfaz de demo en vivo con colores."""
        os.system('cls' if os.name == 'nt' else 'clear')

        total_value = sum(asset.get_current_value() for asset in self.assets.values())
        pnl_percent = ((total_value - self.initial_usdc_balance) / self.initial_usdc_balance) * 100
        
        # Color del rendimiento
        pnl_color = Colors.OKGREEN if pnl_percent >= 0 else Colors.FAIL
        
        print(f"| {Colors.OKBLUE}{pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC} | Tick: {self.sim_tick_counter}")
        print(f"{Colors.HEADER}="*60 + Colors.ENDC)
        print(f"  🤖 {Colors.BOLD}COINBASE TRADING BOT DEMO | LIVE SIMULATION{Colors.ENDC}")
        print(f"{Colors.HEADER}="*60 + Colors.ENDC)
        
        market_desc, action_comment, market_pnl_pct = self.interpret_profit(total_value)

        print(f"📈 {Colors.BOLD}Valor Total del Portafolio:{Colors.ENDC} ${total_value:,.2f} (Rendimiento: {pnl_color}{pnl_percent:,.2f}%{Colors.ENDC})")
        print(f"Benchmark del Mercado (Índice Simulado): {market_pnl_pct:,.2f}%")
        print(f"{Colors.OKCYAN}-" * 60 + Colors.ENDC)

        # 🧠 INTÉRPRETE DE GANANCIA (USDC)
        print(f"  🧠 {Colors.BOLD}ANÁLISIS GLOBAL (USDC):{Colors.ENDC} {market_desc}")
        print(f"  🎯 {Colors.BOLD}Recomendación de Estrategia:{Colors.ENDC} **{action_comment}**")
        print(f"{Colors.OKCYAN}-" * 60 + Colors.ENDC)

        print(f"  📊 {Colors.BOLD}DESGLOSE DE ACTIVOS POR RSI{Colors.ENDC} (Decisión del Bot)")
        
        sorted_assets = sorted(self.assets.items(), key=lambda item: item[1].data['RSI'].iloc[-1] if len(item[1].data) >= CONFIG.RSI_PERIOD else 50)
        
        best_buy_candidate = sorted_assets[0][0] if sorted_assets[0][1].position == 0 and len(sorted_assets[0][1].data) >= CONFIG.RSI_PERIOD else None
        best_sell_candidate = sorted_assets[-1][0] if sorted_assets[-1][1].position == 1 and len(sorted_assets[-1][1].data) >= CONFIG.RSI_PERIOD else None
        
        # Encabezado de la tabla
        print(f"{'Activo':<8} | {'Precio':<12} | {'RSI':<6} | {'Posición':<10} | {'Win Rate (C)':<15}")
        print(f"{Colors.OKCYAN}-" * 60 + Colors.ENDC)

        for ticker, asset in sorted_assets:
            current_price = asset.data['Close'].iloc[-1]
            last_rsi = asset.data['RSI'].iloc[-1] if not asset.data.empty and 'RSI' in asset.data.columns else 0
            
            position_status = f"{Colors.OKGREEN}COMPRADO{Colors.ENDC}" if asset.position == 1 else f"{Colors.WARNING}LIBRE{Colors.ENDC}"
            
            win_rate, trades = asset.get_win_rate()
            
            highlight_char = ""
            # Color del RSI
            rsi_color = Colors.OKGREEN if last_rsi <= CONFIG.RSI_BUY_THRESHOLD else (Colors.FAIL if last_rsi >= CONFIG.RSI_SELL_THRESHOLD else Colors.ENDC)
            
            if ticker == best_buy_candidate:
                 highlight_char = f"{Colors.OKGREEN}C{Colors.ENDC}" # Candidato a Compra
            elif ticker == best_sell_candidate:
                 highlight_char = f"{Colors.FAIL}V{Colors.ENDC}" # Candidato a Venta
            
            print(f"{ticker:<8} | ${current_price:,.4f} | {rsi_color}{last_rsi:,.2f}{Colors.ENDC} | {position_status:<20} | {win_rate:,.1f}% ({trades}) {highlight_char}")
            
        print(f"{Colors.OKCYAN}-" * 60 + Colors.ENDC)
        # 🕹️ BOTONES DE INTERACCIÓN EN VIVO
        print(f"[{Colors.OKBLUE}INFO{Colors.ENDC}] Próximo tick: {next_tick_in:.1f} segundos.")
        print(f"🕹️ {Colors.BOLD}CONTROLES MANUALES{Colors.ENDC} (Actúan sobre el mejor candidato):")
        
        buy_target = best_buy_candidate if best_buy_candidate else "[Ninguno Disponible]"
        sell_target = best_sell_candidate if best_sell_candidate else "[Ninguno Abierto]"
        
        print(f"  [{Colors.OKGREEN}c{Colors.ENDC}]: {Colors.OKGREEN}COMPRA MANUAL{Colors.ENDC} (Actúa sobre: {buy_target})")
        print(f"  [{Colors.FAIL}v{Colors.ENDC}]: {Colors.FAIL}VENTA MANUAL{Colors.ENDC} (Actúa sobre: {sell_target})")
        print("  [q]: DETENER SIMULACIÓN")
        
    def _handle_input(self):
        """Procesa la entrada del usuario para acciones manuales."""
        if self._is_key_pressed():
            key_input = sys.stdin.read(1)
            
            if key_input.lower() == 'q':
                return 'QUIT'
            
            sorted_assets = sorted(self.assets.items(), key=lambda item: item[1].data['RSI'].iloc[-1] if len(item[1].data) >= CONFIG.RSI_PERIOD else 50)
            
            best_buy_candidate_ticker = sorted_assets[0][0] if sorted_assets[0][1].position == 0 and len(sorted_assets[0][1].data) >= CONFIG.RSI_PERIOD else None
            best_sell_candidate_ticker = sorted_assets[-1][0] if sorted_assets[-1][1].position == 1 and len(sorted_assets[-1][1].data) >= CONFIG.RSI_PERIOD else None

            if key_input.lower() == 'c' and best_buy_candidate_ticker:
                target_asset = self.assets[best_buy_candidate_ticker]
                if target_asset.execute_manual_buy():
                    print(f"\n{Colors.OKGREEN}✅ [MANUAL] Ejecutada compra en {best_buy_candidate_ticker} (RSI más bajo){Colors.ENDC}")
            
            elif key_input.lower() == 'v' and best_sell_candidate_ticker:
                target_asset = self.assets[best_sell_candidate_ticker]
                if target_asset.execute_manual_sell():
                    print(f"\n{Colors.FAIL}❌ [MANUAL] Ejecutada venta en {best_sell_candidate_ticker} (RSI más alto){Colors.ENDC}")
            
        return None

    def run_simulation(self):
        """Ejecuta el Live Trading tick por tick."""
        
        old_settings = None
        try:
            if sys.stdin.isatty():
                old_settings = termios.tcgetattr(sys.stdin)
                tty.setcbreak(sys.stdin.fileno())
        except Exception:
            pass

        try:
            while True:
                
                start_time = time.time()
                
                # 1. 🌐 OBTENER PRECIOS
                new_prices = self.fetcher.fetch_latest_prices()
                self.sim_tick_counter += 1
                
                # --- NUEVA VERIFICACIÓN DE LÍMITE DE TICKS ---
                if CONFIG.MAX_SIMULATION_TICKS > 0 and self.sim_tick_counter > CONFIG.MAX_SIMULATION_TICKS:
                    print(f"\n\n>>> 🛑 SIMULACIÓN DETENIDA: Límite de {CONFIG.MAX_SIMULATION_TICKS} ticks alcanzado.")
                    break
                # ---------------------------------------------
                
                # 2. 📈 EJECUTAR TRADES
                for ticker, asset in self.assets.items():
                    asset.set_new_price(new_prices[ticker])
                    asset.run_tick()

                # 3. 📊 ACTUALIZAR PNL
                total_value = sum(asset.get_current_value() for asset in self.assets.values())
                self.portfolio_value_history.append(total_value)
                
                # 4. ⏱ ESPERAR
                elapsed = time.time() - start_time
                wait_time = CONFIG.TICK_INTERVAL_SECONDS - elapsed
                
                self.display_status(max(0, wait_time)) 
                
                # 5. 🛑 DETENCIÓN MANUAL
                user_action = self._handle_input()
                if user_action == 'QUIT':
                    print("\n\n>>> 🛑 SIMULACIÓN DETENIDA: Solicitud de detención del usuario (tecla 'q').")
                    break
                
                if wait_time > 0:
                    time.sleep(wait_time)
                
        finally:
            if old_settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        final_log = []
        final_prices = self.fetcher.current_prices 

        for ticker, asset in self.assets.items():
            final_price = final_prices[ticker]
            asset.close_final_position(final_price)
            final_log.extend(asset.transaction_log)
        
        # Se asegura de crear un DataFrame con las columnas correctas, incluso si está vacío
        if final_log:
            final_df = pd.DataFrame(final_log)
        else:
            final_df = pd.DataFrame(columns=['Tick', 'Asset', 'Type', 'Entry_Price', 'Exec_Price', 'Qty', 'PnL', 'Commission'])
            
        final_value = sum(asset.usdc_balance for asset in self.assets.values())
        
        return final_df, self.sim_tick_counter, final_value
    
    # --- CÁLCULO DE MÉTRICAS AVANZADAS (CORREGIDA) ---
    def _calculate_metrics(self, final_value: float, total_ticks: int) -> dict:
        """Calcula métricas clave de rendimiento (Sharpe, Sortino, Drawdown, etc.)."""
        
        total_pnl = final_value - self.initial_usdc_balance
        return_pct = (total_pnl / self.initial_usdc_balance) * 100
        
        portfolio_series = pd.Series(self.portfolio_value_history).iloc[-(total_ticks + 1):] 
        returns = portfolio_series.pct_change().dropna()
        
        # Volatilidad (Anualizada)
        volatility = returns.std() * np.sqrt(252 * (60*60*24 / CONFIG.TICK_INTERVAL_SECONDS)) 
        
        # Sharpe Ratio (Tasa libre de riesgo = 0)
        sharpe_ratio = returns.mean() / volatility * np.sqrt(252 * (60*60*24 / CONFIG.TICK_INTERVAL_SECONDS)) if volatility != 0 else np.nan

        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_risk = downside_returns.std() * np.sqrt(252 * (60*60*24 / CONFIG.TICK_INTERVAL_SECONDS)) if len(downside_returns) > 0 else volatility
        sortino_ratio = returns.mean() / downside_risk * np.sqrt(252 * (60*60*24 / CONFIG.TICK_INTERVAL_SECONDS)) if downside_risk != 0 else np.nan
        
        # Drawdown Máximo
        peak = portfolio_series.cummax() 
        drawdown = (portfolio_series - peak) / peak 
        max_drawdown = drawdown.min() * 100

        # Riesgo/Recompensa 
        all_transactions = [log for asset in self.assets.values() for log in asset.transaction_log]
        
        risk_reward = np.nan
        if all_transactions:
            log_df = pd.DataFrame(all_transactions)
            log_df['PnL_float'] = pd.to_numeric(log_df['PnL'])
            avg_gain = log_df[log_df['PnL_float'] > 0]['PnL_float'].mean()
            avg_loss = log_df[log_df['PnL_float'] < 0]['PnL_float'].mean()
            risk_reward = abs(avg_gain / avg_loss) if avg_loss != 0 else np.nan

        return {
            "Valor Final Total": f"${final_value:,.2f}",
            "PnL Neto": f"${total_pnl:,.2f}",
            "Rendimiento (%)": f"{return_pct:,.2f}%",
            "Volatilidad Anualizada (%)": f"{volatility*100:,.2f}%",
            "Drawdown Máximo (%)": f"{abs(max_drawdown):,.2f}%",
            "Sharpe Ratio": f"{sharpe_ratio:,.2f}",
            "Sortino Ratio": f"{sortino_ratio:,.2f}",
            "Avg. Riesgo/Recompensa": f"1:{1/risk_reward:,.2f}" if not np.isnan(risk_reward) and risk_reward > 0 else "N/A",
            "Total Ticks": total_ticks,
        }

    def generate_report(self, log_df: pd.DataFrame, final_value: float, total_ticks: int):
        """Genera el reporte final."""
        
        metrics = self._calculate_metrics(final_value, total_ticks)
        
        print("\n\n" + f"{Colors.HEADER}="*60 + Colors.ENDC)
        print(f"📊 {Colors.BOLD}REPORTE FINAL DE LA SIMULACIÓN Y ANÁLISIS FINANCIERO{Colors.ENDC}")
        print(f"{Colors.HEADER}="*60 + Colors.ENDC)
        
        print(f"\n🧠 {Colors.BOLD}MÉTRICAS AVANZADAS DEL PORTAFOLIO{Colors.ENDC}")
        print("-" * 60)
        for key, value in metrics.items():
            color = Colors.OKGREEN if 'PnL' in key and final_value > self.initial_usdc_balance else Colors.ENDC
            print(f"{key:<30}: {color}{value:>25}{Colors.ENDC}")
        print("-" * 60)

        print(f"\n📘 {Colors.BOLD}TÉRMINOS ANALÍTICOS Y ESTRATEGIA:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}* Sharpe Ratio:{Colors.ENDC} Mide el rendimiento ajustado al riesgo (cuánta recompensa por unidad de riesgo). Un valor > 1.0 es generalmente bueno.")
        print(f"{Colors.OKCYAN}* Sortino Ratio:{Colors.ENDC} Similar a Sharpe, pero solo penaliza la volatilidad a la baja (pérdidas). Más enfocado en el riesgo real del inversor.")
        print(f"{Colors.OKCYAN}* Drawdown Máximo:{Colors.ENDC} La mayor caída de pico a valle en el valor del portafolio. Mide el peor riesgo de pérdida en un momento dado.")
        print(f"{Colors.OKCYAN}* Avg. Riesgo/Recompensa:{Colors.ENDC} Relación entre la ganancia promedio de las operaciones ganadoras y la pérdida promedio de las perdedoras.")
        print("-" * 60)

        print(f"\n📈 {Colors.BOLD}RESUMEN DE RENDIMIENTO POR ACTIVO:{Colors.ENDC}")
        asset_summary = []
        for ticker, asset in self.assets.items():
            initial = CONFIG.CAPITAL_PER_ASSET
            final = asset.usdc_balance
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

        # --- CORRECCIÓN DE KEYERROR PARA DATAFRAME VACÍO ---
        print(f"\n📜 {Colors.BOLD}REGISTRO CONSOLIDADO DE TRANSACCIONES (Últimas 10):{Colors.ENDC}")
        
        if not log_df.empty:
            # Imprime solo si hay transacciones registradas
            print(log_df[['Tick', 'Asset', 'Type', 'Entry_Price', 'Exec_Price', 'Qty', 'PnL', 'Commission']].tail(10).to_string(index=False, float_format="%.4f"))
        else:
            # Mensaje amigable si no hay transacciones
            print("--- NO HAY TRANSACCIONES CERRADAS EN ESTA SIMULACIÓN ---")
        
        # --- FIN DE CORRECCIÓN ---
        
        plt.figure(figsize=(12, 6))
        plot_data = pd.Series(self.portfolio_value_history).reset_index(drop=True) 
        
        plt.plot(plot_data.index, plot_data.values, label='Valor Total del Portafolio (USDC)', color='blue')
        plt.plot(pd.Series(self.fetcher.market_index_history).reset_index(drop=True).iloc[CONFIG.RSI_PERIOD * 2 - 1:], 
                 label='Benchmark del Mercado (Índice Simulado)', color='orange', linestyle=':')

        plt.axhline(y=self.initial_usdc_balance, color='green', linestyle='--', label='Saldo Inicial')
        plt.title(f'Evolución del Valor del Portafolio (PnL Acumulado) - {total_ticks} Ticks')
        plt.xlabel('Tick de Simulación (Cada 5 segundos)')
        plt.ylabel('Valor en USDC')
        plt.grid(True, linestyle='--')
        plt.legend()
        plt.show()


# --- PUNTO DE ENTRADA ---
if __name__ == '__main__':
    
    # Muestra las opciones configurables antes de arrancar
    CONFIG.display_options()
    
    # 1. CARGA INICIAL DE DATOS
    temp_fetcher = LiveFetcher(CONFIG.ASSETS_TO_TRACK)
    initial_history_data = temp_fetcher.fetch_initial_history()

    # 2. Inicializar el Manager
    manager = PortfolioManager(
        history_data_map=initial_history_data
    ) 

    # 3. Ejecutar la simulación
    transaction_log, total_ticks, final_value = manager.run_simulation()
    
    # 4. Generar el reporte completo
    manager.generate_report(transaction_log, final_value, total_ticks)

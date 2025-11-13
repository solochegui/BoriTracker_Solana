import pandas as pd
import numpy as np
import time
import os
import matplotlib.pyplot as plt
import sys
import select
import tty
import termios

# --- CONFIGURACIÓN DE LA SIMULACIÓN ---
INITIAL_USDC_BALANCE = 1000.00
INITIAL_BRCN_PRICE = 0.50 
MA_SHORT_PERIOD = 5
MA_LONG_PERIOD = 20
RSI_PERIOD = 14
# SIMULATION_STEPS se ELIMINA para un loop infinito
USDC_TO_TRADE_PCT = 0.95 

# --- PARÁMETROS DE ESTRATEGIA "BUY LOW, SELL HIGH" ---
RSI_BUY_THRESHOLD = 30    
RSI_SELL_THRESHOLD = 70   

# --- PARÁMETROS DE GESTIÓN DE RIESGO Y REALISMO ---
STOP_LOSS_PCT = 0.05    
TAKE_PROFIT_PCT = 0.10  
SLIPPAGE_PCT = 0.001    
COMMISSION_PCT = 0.003  

# --- UTILITY CLASS: BoriTracker ---
class BoriTracker:
    """
    Simulador de trading PRO para BRCN/USDC en Solana con loop interactivo.
    """
    def __init__(self, initial_usdc: float, initial_price: float):
        """Inicializa los balances y el historial de precios."""
        self.initial_usdc_balance = initial_usdc
        self.usdc_balance = initial_usdc
        self.brcn_balance = 0.0
        self.is_connected = False
        self.position = 0 
        self.buy_price = 0.0 
        
        # Historial de precios y transacciones
        max_period = max(MA_LONG_PERIOD, RSI_PERIOD)
        self.price_history = [initial_price] * max_period 
        self.transaction_log = []
        self.portfolio_value_history = [initial_usdc] * max_period 

        # Inicializamos el DataFrame de historial
        self.data = pd.DataFrame(self.price_history, columns=['Close'])
        self.sim_tick_counter = 0 # Contador manual de ticks

    def connect_wallet(self):
        """Simula la conexión a Phantom Wallet."""
        self.is_connected = True
        print("-----------------------------------------------------")
        print("👻 Phantom Wallet Conectada (Simulada)")
        print(f"💰 Saldo Inicial USDC: ${self.usdc_balance:,.2f}")
        print("-----------------------------------------------------")

    def _simulate_price_change(self):
        """Simula un nuevo precio con un cambio más realista."""
        current_price = self.price_history[-1]
        change_pct = np.random.normal(0, 0.005) 
        new_price = current_price * (1 + change_pct)
        self.price_history.append(new_price)
        self.data.loc[len(self.data)] = new_price
        if len(self.data) > 300:
            self.data = self.data.iloc[-300:].reset_index(drop=True)
        self.sim_tick_counter += 1

    def _calculate_indicators(self):
        """Calcula MA y RSI."""
        self.data['MA_Short'] = self.data['Close'].rolling(window=MA_SHORT_PERIOD).mean()
        self.data['MA_Long'] = self.data['Close'].rolling(window=MA_LONG_PERIOD).mean()

        delta = self.data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(span=RSI_PERIOD, adjust=False).mean()
        avg_loss = loss.ewm(span=RSI_PERIOD, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan) 
        self.data['RSI'] = 100 - (100 / (1 + rs))

    def _simulate_trade(self, type: str, current_price: float, qty_to_trade: float):
        """Simula y registra la transacción, aplicando Slippage y Comisiones."""
        
        if qty_to_trade <= 0:
            return current_price

        # 1. Aplicar Slippage
        if type == 'BUY':
            final_price = current_price * (1 + SLIPPAGE_PCT)
        elif type in ('SELL', 'CLOSE', 'SELL_SL', 'SELL_TP'):
            final_price = current_price * (1 - SLIPPAGE_PCT)
        else:
            final_price = current_price

        # 2. Calcular PnL si es una venta/cierre
        pnl = 0.0
        if type in ('SELL', 'CLOSE', 'SELL_SL', 'SELL_TP'):
            pnl = (final_price - self.buy_price) * qty_to_trade 
        elif type == 'BUY':
            self.buy_price = final_price 

        # 3. Actualizar Balances y Comisiones
        commission_cost = 0.0

        if type == 'BUY':
            cost = final_price * qty_to_trade
            commission_cost = cost * COMMISSION_PCT
            
            if self.usdc_balance < cost + commission_cost:
                return current_price 
            
            self.usdc_balance -= (cost + commission_cost)
            self.brcn_balance += qty_to_trade

        elif type in ('SELL', 'CLOSE', 'SELL_SL', 'SELL_TP'):
            revenue = final_price * qty_to_trade
            commission_cost = revenue * COMMISSION_PCT

            self.usdc_balance += (revenue - commission_cost)
            self.brcn_balance -= qty_to_trade


        # 4. Registrar la transacción
        self.transaction_log.append({
            'Tick': len(self.transaction_log) + 1,
            'Type': type,
            'Entry_Price': self.buy_price, 
            'Exec_Price': final_price, 
            'Qty': qty_to_trade,
            'PnL': pnl,
            'Commission': commission_cost,
            'USDC_Balance': self.usdc_balance,
            'BRCN_Balance': self.brcn_balance
        })
        
        return final_price

    def display_status(self, current_price: float):
        """Muestra una interfaz de texto en la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')

        last_row = self.data.iloc[-1]
        total_value = self.usdc_balance + (self.brcn_balance * current_price)

        print(f"| {pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')} | Tick: {self.sim_tick_counter}")
        print("=====================================================")
        print("  BRCN Tracker PRO | Estrategia: Buy Low/Sell High (RSI) + SL/TP")
        print("=====================================================")

        # Sección de Precio y Valor
        print(f"💰 Precio BRCN/USDC: ${current_price:,.4f}")
        print(f"📈 Valor Total (USDC): ${total_value:,.2f}")
        print("-----------------------------------------------------")

        # Sección de Balances
        print("  📊 WALLET SIMULADA")
        print(f"    USDC Balance: ${self.usdc_balance:,.2f}")
        print(f"    BRCN Balance: {self.brcn_balance:,.4f}")
        print(f"    Posición Abierta: {'Si' if self.position == 1 else 'No'}")
        if self.position == 1:
            change_pct = (current_price - self.buy_price) / self.buy_price * 100
            print(f"    @ Precio de Compra: ${self.buy_price:,.4f} ({change_pct:+.2f}%)")
        
        # Sección de Indicadores
        print("-----------------------------------------------------")
        print("  🧪 INDICADORES (RSI Buy/Sell Threshold: 30/70)")
        if 'RSI' in self.data.columns and not pd.isna(last_row['RSI']):
            print(f"    MA Corta ({MA_SHORT_PERIOD}): {last_row['MA_Short']:,.4f}")
            print(f"    MA Larga ({MA_LONG_PERIOD}):  {last_row['MA_Long']:,.4f}")
            print(f"    RSI ({RSI_PERIOD}):           {last_row['RSI']:,.2f}")
        
        print("\n\nPresiona 'q' y luego [ENTER] para DETENER la simulación.")

    # Función para detectar entrada de teclado (adaptada para Unix/Termux)
    def _is_key_pressed(self):
        """Revisa si se ha presionado una tecla sin bloquear la ejecución."""
        # Esta solución funciona en la mayoría de los entornos Linux/Termux/MacOS
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def run_simulation(self):
        """Ejecuta el backtest tick por tick en un loop infinito."""

        self.connect_wallet()
        max_period = max(MA_LONG_PERIOD, RSI_PERIOD)
        
        # Configurar la terminal para lectura de caracteres (solo Unix/Termux)
        old_settings = None
        try:
            # Intentar configurar la terminal para lectura sin bloqueo
            if sys.stdin.isatty():
                old_settings = termios.tcgetattr(sys.stdin)
                tty.setcbreak(sys.stdin.fileno())
        except Exception:
            # Si falla (ej. Windows), el usuario tendrá que presionar ENTER después de 'q'
            pass

        try:
            while True:
                self._simulate_price_change()
                self._calculate_indicators()
                current_price = self.data['Close'].iloc[-1]
                
                # Guardamos el valor del portafolio en cada tick
                total_value = self.usdc_balance + (self.brcn_balance * current_price)
                self.portfolio_value_history.append(total_value)
                
                # --- CONDICIÓN DE DETENCIÓN 1: CAPITAL AGOTADO ---
                if self.usdc_balance < 1.0 and self.brcn_balance == 0.0 and len(self.transaction_log) > 0:
                    print("\n\n>>> 🛑 SIMULACIÓN DETENIDA: Se ha agotado el capital en USDC y no hay posición abierta.")
                    break

                # --- CONDICIÓN DE DETENCIÓN 2: ENTRADA DE USUARIO ---
                if self._is_key_pressed():
                    key_input = sys.stdin.read(1)
                    if key_input.lower() == 'q':
                        print("\n\n>>> 🛑 SIMULACIÓN DETENIDA: Solicitud de detención del usuario (tecla 'q').")
                        break
                
                # Solo ejecutamos la lógica si tenemos suficientes datos para los indicadores
                if len(self.data) >= max_period:
                    last_row = self.data.iloc[-1]
                    
                    # 1. GESTIÓN DE RIESGO (Stop-Loss/Take-Profit)
                    if self.position == 1:
                        stop_loss_price = self.buy_price * (1 - STOP_LOSS_PCT)
                        take_profit_price = self.buy_price * (1 + TAKE_PROFIT_PCT)
                        qty_to_sell = self.brcn_balance

                        # Stop-Loss
                        if current_price <= stop_loss_price:
                            self._simulate_trade('SELL_SL', current_price, qty_to_sell)
                            self.position = 0
                            print(f"\n>>>> 🛑 STOP-LOSS ejecutado: {qty_to_sell:,.4f} BRCN @ ${current_price:,.4f}")
                        
                        # Take-Profit
                        elif current_price >= take_profit_price:
                            self._simulate_trade('SELL_TP', current_price, qty_to_sell)
                            self.position = 0
                            print(f"\n>>>> 🟢 TAKE-PROFIT ejecutado: {qty_to_sell:,.4f} BRCN @ ${current_price:,.4f}")
                    
                    # 2. ESTRATEGIA "BUY LOW, SELL HIGH" (RSI)
                    buy_signal = last_row['RSI'] <= RSI_BUY_THRESHOLD
                    sell_signal = last_row['RSI'] >= RSI_SELL_THRESHOLD

                    # Abrir posición de COMPRA 
                    if self.position == 0 and buy_signal and self.usdc_balance > 1:
                        usdc_to_spend = self.usdc_balance * USDC_TO_TRADE_PCT
                        qty_to_buy = usdc_to_spend / current_price
                        self._simulate_trade('BUY', current_price, qty_to_buy)
                        self.position = 1
                        print(f"\n>>>> 🟢 COMPRA ejecutada (RSI < {RSI_BUY_THRESHOLD}): {qty_to_buy:,.4f} BRCN @ ${current_price:,.4f}")
                    
                    # Cerrar posición de VENTA
                    elif self.position == 1 and sell_signal:
                        qty_to_sell = self.brcn_balance
                        self._simulate_trade('SELL', current_price, qty_to_sell)
                        self.position = 0
                        print(f"\n>>>> 🔴 VENTA/Cierre ejecutada (RSI > {RSI_SELL_THRESHOLD}): {qty_to_sell:,.4f} BRCN @ ${current_price:,.4f}")
                    
                self.display_status(current_price)
                time.sleep(0.05) 

        finally:
            # Restaurar la configuración de la terminal
            if old_settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        # --- RESUMEN FINAL ---
        final_price = self.data['Close'].iloc[-1]

        # 3. Cerrar cualquier posición abierta al final
        if self.position == 1:
            self._simulate_trade('CLOSE', final_price, self.brcn_balance)
            self.position = 0

        final_value = self.usdc_balance + (self.brcn_balance * final_price)
        
        return pd.DataFrame(self.transaction_log), self.sim_tick_counter

    def _calculate_metrics(self, log_df: pd.DataFrame, final_value: float, total_ticks: int) -> dict:
        """Calcula métricas clave de rendimiento."""
        
        total_pnl = final_value - self.initial_usdc_balance
        return_pct = (total_pnl / self.initial_usdc_balance) * 100
        
        # Ajuste en Drawdown para la longitud variable
        portfolio_series = pd.Series(self.portfolio_value_history).iloc[-(total_ticks + 1):] 
        peak = portfolio_series.cummax() 
        drawdown = (portfolio_series - peak) / peak 
        max_drawdown = drawdown.min() * 100

        closed_trades = log_df[log_df['Type'].str.contains('SELL|CLOSE|SELL_SL|SELL_TP')]
        closed_trades['PnL_float'] = pd.to_numeric(closed_trades['PnL'])
        winning_trades = closed_trades[closed_trades['PnL_float'] > 0]
        win_rate = (len(winning_trades) / len(closed_trades)) * 100 if len(closed_trades) > 0 else 0


        return {
            "Valor Final Total": f"${final_value:,.2f}",
            "PnL Neto": f"${total_pnl:,.2f}",
            "Rendimiento (%)": f"{return_pct:,.2f}%",
            "Drawdown Máximo (%)": f"{abs(max_drawdown):,.2f}%",
            "Tasa de Ganancia (Win Rate)": f"{win_rate:,.2f}%",
            "Total Ticks": total_ticks,
            "Total Transacciones": len(log_df)
        }

    def generate_report(self, log_df: pd.DataFrame, final_value: float, total_ticks: int):
        """Genera el reporte final y el gráfico de PnL. CORRECCIÓN: Paréntesis cerrados."""
        
        # >>> ESTA LÍNEA ESTÁ CORREGIDA <<<
        metrics = self._calculate_metrics(log_df, final_value, total_ticks)
        
        print("\n\n" + "="*50)
        print("✅ SIMULACIÓN FINALIZADA Y REPORTE DE BACKTESTING")
        print("="*50)
        
        # Reporte de Métricas Clave
        print("\n📊 MÉTRICAS DE RENDIMIENTO")
        print("-" * 35)
        for key, value in metrics.items():
            print(f"{key:<30}: {value:>15}")
        print("-" * 35)
        
        # Registro Completo
        print("\n📝 REGISTRO COMPLETO DE TRANSACCIONES:")
        print(log_df[['Tick', 'Type', 'Entry_Price', 'Exec_Price', 'Qty', 'PnL', 'Commission']].to_string(index=False, float_format="%.4f"))
        
        # Gráfico de PnL Acumulado
        plt.figure(figsize=(12, 6))
        
        # Ajuste de longitud para el gráfico
        plot_data = pd.Series(self.portfolio_value_history).iloc[-(total_ticks + 1):].reset_index(drop=True) 
        
        plt.plot(plot_data.index, plot_data.values, label='Valor Total del Portafolio (USDC)', color='blue')
        plt.axhline(y=self.initial_usdc_balance, color='green', linestyle='--', label='Saldo Inicial')
        plt.title(f'Evolución del Valor del Portafolio (PnL Acumulado) - {total_ticks} Ticks')
        plt.xlabel('Tick de Simulación')
        plt.ylabel('Valor en USDC')
        plt.grid(True, linestyle='--')
        plt.legend()
        plt.show()

# --- PUNTO DE ENTRADA ---
if __name__ == '__main__':
    tracker = BoriTracker(
        initial_usdc=INITIAL_USDC_BALANCE, 
        initial_price=INITIAL_BRCN_PRICE
    )

    # Ejecutar la simulación. Devuelve el log y el número de ticks.
    transaction_log, total_ticks = tracker.run_simulation()
    
    # Recalcular el valor final para el reporte
    final_price = tracker.data['Close'].iloc[-1]
    final_value = tracker.usdc_balance + (tracker.brcn_balance * final_price)

    # Generar el reporte completo
    tracker.generate_report(transaction_log, final_value, total_ticks)


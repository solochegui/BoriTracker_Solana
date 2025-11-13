import pandas as pd
import numpy as np
import time
import os

# --- CONFIGURACIÓN DE LA SIMULACIÓN ---
INITIAL_USDC_BALANCE = 1000.00
INITIAL_BRCN_PRICE = 0.50 # Precio inicial simulado de BoriCoin
MA_SHORT_PERIOD = 5
MA_LONG_PERIOD = 20
RSI_PERIOD = 14
SIMULATION_STEPS = 100 # Número de "ticks" o pasos a simular

# --- UTILITY CLASS: BoriTracker ---
class BoriTracker:
    """
    Simulador de trading para BRCN/USDC en Solana con estrategia de MA + RSI.
    Incluye una interfaz de consola y simulación de wallet.
    """
    def __init__(self, initial_usdc: float, initial_price: float):
        """Inicializa los balances y el historial de precios."""
        self.usdc_balance = initial_usdc
        self.brcn_balance = 0.0
        self.is_connected = False
        self.position = 0 # 0: Sin posición, 1: Comprado (en BRCN)
        self.buy_price = 0.0
        
        # Historial de precios y transacciones (para indicadores y logs)
        self.price_history = [initial_price] * max(MA_LONG_PERIOD, RSI_PERIOD) 
        self.transaction_log = []
        
        # Inicializamos el DataFrame de historial (necesario para pandas)
        self.data = pd.DataFrame(self.price_history, columns=['Close'])

    def connect_wallet(self):
        """Simula la conexión a Phantom Wallet."""
        self.is_connected = True
        print("-----------------------------------------------------")
        print("👻 Phantom Wallet Conectada (Simulada)")
        print(f"💰 Saldo Inicial USDC: ${self.usdc_balance:,.2f}")
        print("-----------------------------------------------------")

    def _simulate_price_change(self):
        """Simula un nuevo precio con un pequeño cambio aleatorio."""
        current_price = self.price_history[-1]
        
        # Ruido aleatorio (cambio entre -1% y +1%)
        change_pct = np.random.normal(0, 0.005) # Pequeño cambio aleatorio
        new_price = current_price * (1 + change_pct)
        
        # Añadir el nuevo precio al historial y actualizar el DataFrame
        self.price_history.append(new_price)
        self.data.loc[len(self.data)] = new_price # Agrega nueva fila
        
        # Mantiene el historial en un tamaño manejable (los últimos 100 periodos)
        if len(self.data) > 100:
            self.data = self.data.iloc[-100:].reset_index(drop=True)

    def _calculate_indicators(self):
        """Calcula MA y RSI en base al historial de precios (self.data)."""
        
        # 1. Medias Móviles
        self.data['MA_Short'] = self.data['Close'].rolling(window=MA_SHORT_PERIOD).mean()
        self.data['MA_Long'] = self.data['Close'].rolling(window=MA_LONG_PERIOD).mean()
        
        # 2. RSI (Relative Strength Index)
        delta = self.data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=RSI_PERIOD).mean()
        avg_loss = loss.rolling(window=RSI_PERIOD).mean()
        
        rs = avg_gain / avg_loss
        self.data['RSI'] = 100 - (100 / (1 + rs))

    def _simulate_trade(self, type: str, price: float, quantity: float):
        """Simula y registra la transacción."""
        
        # Calcular PnL si es una venta/cierre
        pnl = 0
        if type in ('SELL', 'CLOSE'):
            pnl = (price - self.buy_price) * quantity
        elif type == 'BUY':
            self.buy_price = price
        
        # Actualizar balances
        if type == 'BUY':
            cost = price * quantity
            self.usdc_balance -= cost
            self.brcn_balance += quantity
            
        elif type in ('SELL', 'CLOSE'):
            revenue = price * quantity
            self.usdc_balance += revenue
            self.brcn_balance -= quantity

        # Registrar la transacción
        self.transaction_log.append({
            'Tick': len(self.transaction_log) + 1,
            'Time': pd.to_datetime('now').strftime('%H:%M:%S'),
            'Type': type,
            'Price': f"{price:,.4f}",
            'Qty': f"{quantity:,.4f}",
            'PnL': f"${pnl:,.2f}",
            'USDC_Balance': f"${self.usdc_balance:,.2f}",
            'BRCN_Balance': f"{self.brcn_balance:,.4f}"
        })

    def display_status(self, current_price: float):
        """Muestra una interfaz de texto en la consola."""
        os.system('cls' if os.name == 'nt' else 'clear') # Limpia la consola
        
        last_row = self.data.iloc[-1]
        
        # Calcular el valor total del portafolio
        total_value = self.usdc_balance + (self.brcn_balance * current_price)
        
        print(f"| {pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')} |")
        print("=====================================================")
        print("  BRCN Tracker | Estrategia: MA/RSI | Solana (Simulado)")
        print("=====================================================")
        
        # Sección de Precio y Valor
        print(f"💰 Precio BRCN/USDC: ${current_price:,.4f}")
        print(f"📈 Valor Total (USDC): ${total_value:,.2f}")
        print("-----------------------------------------------------")
        
        # Sección de Balances
        print("  📊 WALLET SIMULADA")
        print(f"    USDC Balance: ${self.usdc_balance:,.2f}")
        print(f"    BRCN Balance: {self.brcn_balance:,.4f}")
        
        # Sección de Indicadores
        print("-----------------------------------------------------")
        print("  🧪 INDICADORES")
        # Asegúrate de que los indicadores existan antes de imprimir
        if 'RSI' in self.data.columns and not pd.isna(last_row['RSI']):
            print(f"    MA Corta ({MA_SHORT_PERIOD}): {last_row['MA_Short']:,.4f}")
            print(f"    MA Larga ({MA_LONG_PERIOD}):  {last_row['MA_Long']:,.4f}")
            print(f"    RSI ({RSI_PERIOD}):           {last_row['RSI']:,.2f}")
            
    def run_simulation(self):
        """Ejecuta el backtest tick por tick."""
        
        self.connect_wallet()
        
        for tick in range(SIMULATION_STEPS):
            self._simulate_price_change()
            self._calculate_indicators()
            current_price = self.data['Close'].iloc[-1]

            # Solo ejecutamos la lógica si tenemos suficientes datos para los indicadores
            if len(self.data) >= max(MA_LONG_PERIOD, RSI_PERIOD):
                
                # --- Lógica de Trading Combinada ---
                
                last_row = self.data.iloc[-1]
                prev_row = self.data.iloc[-2]

                # Condición de COMPRA: Cruce alcista de MA Y RSI NO sobrecomprado (< 50)
                buy_signal = (prev_row['MA_Short'] < prev_row['MA_Long'] and 
                              last_row['MA_Short'] > last_row['MA_Long'] and
                              last_row['RSI'] < 50)

                # Condición de VENTA: Cruce bajista de MA Y RSI NO sobrevendido (> 50)
                sell_signal = (prev_row['MA_Short'] > prev_row['MA_Long'] and 
                               last_row['MA_Short'] < last_row['MA_Long'] and
                               last_row['RSI'] > 50)
                
                # 1. EJECUTAR VENTA (Cerrar posición)
                if self.position == 1 and sell_signal:
                    qty_to_sell = self.brcn_balance # Vender todo
                    self._simulate_trade('SELL', current_price, qty_to_sell)
                    self.position = 0
                    print(f"\n>>>> 🔴 VENTA ejecutada: {qty_to_sell:,.4f} BRCN @ ${current_price:,.4f}")
                    
                # 2. EJECUTAR COMPRA (Abrir posición)
                elif self.position == 0 and buy_signal and self.usdc_balance > 1:
                    # Comprar con el 95% del USDC disponible
                    usdc_to_spend = self.usdc_balance * 0.95
                    qty_to_buy = usdc_to_spend / current_price
                    self._simulate_trade('BUY', current_price, qty_to_buy)
                    self.position = 1
                    print(f"\n>>>> 🟢 COMPRA ejecutada: {qty_to_buy:,.4f} BRCN @ ${current_price:,.4f}")
            
            self.display_status(current_price)
            time.sleep(0.5) # Simula un delay entre ticks
            
        # --- RESUMEN FINAL ---
        final_price = self.data['Close'].iloc[-1]
        
        # Cerrar cualquier posición abierta al final
        if self.position == 1:
            self._simulate_trade('CLOSE', final_price, self.brcn_balance)
            self.position = 0

        final_value = self.usdc_balance + (self.brcn_balance * final_price)
        
        print("\n\n" + "="*50)
        print("✅ SIMULACIÓN FINALIZADA")
        print(f"Precio final BRCN: ${final_price:,.4f}")
        print(f"Saldo Final USDC: ${self.usdc_balance:,.2f}")
        print(f"Valor Final Total: ${final_value:,.2f}")
        
        return pd.DataFrame(self.transaction_log)


# --- PUNTO DE ENTRADA ---
if __name__ == '__main__':
    tracker = BoriTracker(
        initial_usdc=INITIAL_USDC_BALANCE, 
        initial_price=INITIAL_BRCN_PRICE
    )
    
    # Ejecutar la simulación
    log = tracker.run_simulation()
    
    print("\n" + "="*50)
    print("📝 REGISTRO COMPLETO DE TRANSACCIONES:")
    print(log.to_string())



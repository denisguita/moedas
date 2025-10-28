"""
Serviço de Integração com o Telegram para CriptoBR IA PRO
Envia alertas de compra/venda e relatórios em tempo real
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class TelegramAlertService:
    def __init__(self, bot_token: str, chat_id: str):
        """
        Inicializa o serviço de alertas do Telegram
        
        Args:
            bot_token: Token do bot do Telegram
            chat_id: ID do chat para receber as mensagens
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.alert_history = []
        
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Envia uma mensagem de texto para o Telegram
        
        Args:
            message: Conteúdo da mensagem
            parse_mode: Modo de formatação (HTML ou Markdown)
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Mensagem enviada com sucesso para Telegram")
                return True
            else:
                print(f"✗ Erro ao enviar mensagem: {response.status_code}")
                print(f"  Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao conectar com Telegram: {e}")
            return False
    
    def send_alert(self, crypto_symbol: str, signal_type: str, price: float, 
                   confidence: float, rsi: float, volume: float) -> bool:
        """
        Envia um alerta de compra/venda para o Telegram
        
        Args:
            crypto_symbol: Símbolo da criptomoeda (ex: BTC, ETH)
            signal_type: Tipo de sinal (COMPRA ou VENDA)
            price: Preço atual
            confidence: Confiança do sinal (0-100)
            rsi: Valor do RSI
            volume: Volume de negociação
            
        Returns:
            True se enviado com sucesso
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determinar emoji e cor baseado no tipo de sinal
        if signal_type == "COMPRA":
            emoji = "🟢"
            color = "#10b981"
            acao = "ENTRADA RECOMENDADA"
        else:
            emoji = "🔴"
            color = "#ef4444"
            acao = "SAÍDA RECOMENDADA"
        
        # Formatar a mensagem
        message = f"""
{emoji} <b>ALERTA DE {signal_type}</b> {emoji}

<b>Moeda:</b> {crypto_symbol}
<b>Preço:</b> R$ {price:.8f}
<b>RSI:</b> {rsi:.2f}
<b>Volume:</b> {volume:,.0f}
<b>Confiança:</b> {confidence:.1f}%

<b>Ação:</b> {acao}
<b>Hora:</b> {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CriptoBR IA PRO - Inteligência Financeira
"""
        
        success = self.send_message(message)
        
        if success:
            self.alert_history.append({
                'timestamp': timestamp,
                'crypto': crypto_symbol,
                'signal': signal_type,
                'price': price,
                'confidence': confidence,
                'rsi': rsi,
                'volume': volume
            })
        
        return success
    
    def send_daily_report(self, cryptos_data: List[Dict]) -> bool:
        """
        Envia um relatório diário com análise das criptomoedas
        
        Args:
            cryptos_data: Lista com dados das criptomoedas
            
        Returns:
            True se enviado com sucesso
        """
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Calcular estatísticas
        total_cryptos = len(cryptos_data)
        gainers = sum(1 for c in cryptos_data if c.get('change24h', 0) > 0)
        losers = total_cryptos - gainers
        avg_rsi = sum(c.get('rsi', 50) for c in cryptos_data) / total_cryptos if total_cryptos > 0 else 0
        
        # Encontrar melhor e pior performance
        best_crypto = max(cryptos_data, key=lambda x: x.get('change24h', 0))
        worst_crypto = min(cryptos_data, key=lambda x: x.get('change24h', 0))
        
        # Contar sinais
        buy_signals = sum(1 for c in cryptos_data if c.get('signal') == 'COMPRA')
        sell_signals = sum(1 for c in cryptos_data if c.get('signal') == 'VENDA')
        
        message = f"""
📊 <b>RELATÓRIO DIÁRIO - CriptoBR IA PRO</b> 📊

<b>Data:</b> {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>RESUMO DO MERCADO:</b>
• Moedas Analisadas: {total_cryptos}
• Em Alta: {gainers} 📈
• Em Baixa: {losers} 📉
• RSI Médio: {avg_rsi:.2f}

<b>SINAIS DETECTADOS:</b>
• Sinais de COMPRA: {buy_signals} 🟢
• Sinais de VENDA: {sell_signals} 🔴

<b>PERFORMANCE:</b>
• Melhor: {best_crypto.get('symbol', 'N/A')} (+{best_crypto.get('change24h', 0):.2f}%)
• Pior: {worst_crypto.get('symbol', 'N/A')} ({worst_crypto.get('change24h', 0):.2f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>RECOMENDAÇÕES:</b>
"""
        
        if buy_signals > 0:
            message += f"\n✓ Existem {buy_signals} oportunidades de COMPRA identificadas"
        if sell_signals > 0:
            message += f"\n✓ Existem {sell_signals} oportunidades de VENDA identificadas"
        
        message += "\n\n💡 Verifique o dashboard para mais detalhes!"
        
        return self.send_message(message)
    
    def send_test_message(self) -> bool:
        """
        Envia uma mensagem de teste para verificar a conectividade
        
        Returns:
            True se enviado com sucesso
        """
        message = """
✅ <b>CriptoBR IA PRO - Teste de Conectividade</b> ✅

A integração com o Telegram está <b>funcionando corretamente!</b>

Você receberá alertas de compra/venda e relatórios diários neste chat.

🔔 Ative as notificações para não perder nenhum alerta!
"""
        return self.send_message(message)
    
    def get_alert_history(self) -> List[Dict]:
        """
        Retorna o histórico de alertas enviados
        
        Returns:
            Lista com histórico de alertas
        """
        return self.alert_history
    
    def send_portfolio_summary(self, portfolio_data: Dict) -> bool:
        """
        Envia um resumo da carteira
        
        Args:
            portfolio_data: Dados da carteira do utilizador
            
        Returns:
            True se enviado com sucesso
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        total_value = portfolio_data.get('total_value', 0)
        total_change = portfolio_data.get('total_change', 0)
        cryptos = portfolio_data.get('cryptos', [])
        
        message = f"""
💼 <b>RESUMO DA CARTEIRA</b> 💼

<b>Hora:</b> {timestamp}

<b>Valor Total:</b> R$ {total_value:,.2f}
<b>Variação 24h:</b> {total_change:+.2f}%

<b>MOEDAS NA CARTEIRA:</b>
"""
        
        for crypto in cryptos:
            symbol = crypto.get('symbol', 'N/A')
            amount = crypto.get('amount', 0)
            value = crypto.get('value', 0)
            change = crypto.get('change24h', 0)
            
            emoji = "📈" if change > 0 else "📉"
            message += f"\n• {symbol}: {amount:.8f} (R$ {value:,.2f}) {emoji} {change:+.2f}%"
        
        return self.send_message(message)


# Exemplo de uso
if __name__ == "__main__":
    # Configurar com as credenciais do utilizador
    TELEGRAM_TOKEN = "7834485201:AAExDXuQJprwbv3ofUIOg5zrliXrDeA0-vU"
    TELEGRAM_CHAT_ID = "695440902"
    
    # Criar instância do serviço
    service = TelegramAlertService(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    
    # Testar envio de mensagem
    print("Testando envio de mensagem...")
    service.send_test_message()
    
    # Testar alerta de compra
    print("\nTestando alerta de compra...")
    service.send_alert(
        crypto_symbol="BTC",
        signal_type="COMPRA",
        price=67234.56,
        confidence=85.7,
        rsi=28.5,
        volume=1250000
    )
    
    # Testar relatório diário
    print("\nTestando relatório diário...")
    cryptos_data = [
        {'symbol': 'BTC', 'change24h': 2.34, 'rsi': 65, 'signal': 'COMPRA'},
        {'symbol': 'ETH', 'change24h': -1.23, 'rsi': 72, 'signal': 'VENDA'},
        {'symbol': 'PEPE', 'change24h': 4.09, 'rsi': 27, 'signal': 'COMPRA'},
    ]
    service.send_daily_report(cryptos_data)


from typing import List, Dict, Any

class LLMService:
    @staticmethod
    def generate_assessment(data: List[Dict[str, Any]], anomalies: List[Dict[str, Any]], ticker_info: Dict[str, Any] = None, language: str = 'pl') -> Dict[str, Any]:
        """
        Generuje syntetyczną ocenę i interpretację wyników analizy.
        Obsługuje języki 'pl' (polski) i 'en' (angielski).
        """
        
        # Mapowanie tekstów lokalizowanych
        lang_map = {
            'pl': {
                'neutral': 'Neutralny', 'hold': 'Trzymaj', 'buy': 'Kupuj', 'sell': 'Sprzedaj', 
                'bullish': 'Byczy', 'bearish': 'Niedźwiedzi', 'slight_bull': 'Lekko Byczy', 'slight_bear': 'Lekko Niedźwiedzi',
                'no_data': 'Brak danych do analizy.', 'low_conf': 'Niska', 'med_conf': 'Średnia', 'high_conf': 'Wysoka',
                'uptrend': 'trendzie wzrostowym', 'downtrend': 'trendzie spadkowym', 'neutral_trend': 'trendzie bocznym',
                'momentum_building': 'rośnie (Bycze)', 'momentum_weakening': 'słabnie (Niedźwiedzie)', 'momentum_dying': 'zanika',
                'overbought': 'Wykupiony', 'oversold': 'Wyprzedany', 'rsi_neutral': 'Neutralny',
                'testing_res': 'testuje opór (Górna Wstęga)', 'testing_supp': 'testuje wsparcie (Dolna Wstęga)',
                'anomaly_detected': 'Ostatni ruch oznaczony jako anomalia, wskazująca na ekstremalną zmienność.',
                'volatility_normal': 'Zmienność rynku w normie.',
                'market_overview': 'Przegląd Rynku', 'tech_analysis': 'Analiza Techniczna', 'anomaly_check': 'Sprawdzenie Anomalii', 'conclusion': 'Wniosek',
                'overview_template': "{name} ({symbol}) działa w sektorze {sector}. {fund_text}Aktywo znajduje się obecnie w {trend_desc} względem 50-dniowej Średniej Wykładniczej.",
                'tech_template': "Momentum obecnie {momentum_desc}. Wskaźnik RSI wynosi {rsi:.1f}, co klasyfikuje aktywo jako {rsi_desc}. Jeśli chodzi o akcję cenową, aktywo {bb_desc}.",
                'vol_template': "{anomaly_text} ATR wskazuje poziom zmienności {atr:.2f}.",
                'concl_template': "Biorąc pod uwagę momentum i strukturę rynku, krótkoterminowa perspektywa jest {sentiment}. Model sugeruje strategię typu {recommendation}.",
                'pe_text': "Przy wskaźniku P/E równym {pe:.2f}, ",
                'unknown_asset': 'Nieznane Aktywo', 'unknown_sector': 'Nieznany Sektor'
            },
            'en': {
                'neutral': 'Neutral', 'hold': 'Hold', 'buy': 'Buy', 'sell': 'Sell',
                'bullish': 'Bullish', 'bearish': 'Bearish', 'slight_bull': 'Slightly Bullish', 'slight_bear': 'Slightly Bearish',
                'no_data': 'No data available for analysis.', 'low_conf': 'Low', 'med_conf': 'Medium', 'high_conf': 'High',
                'uptrend': 'Uptrend', 'downtrend': 'Downtrend', 'neutral_trend': 'Sideways Trend',
                'momentum_building': 'building up (Bullish)', 'momentum_weakening': 'weakening (Bearish)', 'momentum_dying': 'dying out',
                'overbought': 'Overbought', 'oversold': 'Oversold', 'rsi_neutral': 'Neutral',
                'testing_res': 'testing resistance (Upper Band)', 'testing_supp': 'testing support (Lower Band)',
                'anomaly_detected': 'The latest movement is flagged as anomalous, indicating extreme volatility.',
                'volatility_normal': 'Market volatility is within expected parameters.',
                'market_overview': 'Market Overview', 'tech_analysis': 'Technical Analysis', 'anomaly_check': 'Anomaly Check', 'conclusion': 'Conclusion',
                'overview_template': "{name} ({symbol}) operates in the {sector} sector. {fund_text}The asset is currently demonstrating a {trend_desc} relative to its 50-day Exponential Moving Average.",
                'tech_template': "Momentum is currently {momentum_desc}. The Relative Strength Index (RSI) is at {rsi:.1f}, which classifies the asset as {rsi_desc}. Regarding price action, the asset is {bb_desc}.",
                'vol_template': "{anomaly_text} The Average True Range (ATR) indicates a volatility level of {atr:.2f}.",
                'concl_template': "Taking into account both the technical momentum and the current market structure, the immediate outlook is {sentiment}. The model recommends a {recommendation} strategy.",
                'pe_text': "Trading at a P/E ratio of {pe:.2f}, ",
                'unknown_asset': 'Unknown Asset', 'unknown_sector': 'Unknown Sector'
            }
        }
        
        # Wybór słownika na podstawie języka
        L = lang_map.get(language, lang_map['pl'])

        if not anomalies:
            return {
                "sentiment": L['neutral'],
                "recommendation": L['hold'],
                "summary": L['no_data'],
                "confidence": L['low_conf']
            }
            
        # Pobranie ostatniego punktu danych do analizy bieżącej (sentyment)
        last_point = anomalies[-1]
        
        # Wyciągnięcie wskaźników technicznych do syntezy
        close_price = last_point.get('close')
        rsi = last_point.get('rsi')
        macd = last_point.get('macd')
        macd_signal = last_point.get('macd_signal')
        ema_50 = last_point.get('ema_50')
        bb_upper = last_point.get('bb_upper')
        bb_lower = last_point.get('bb_lower')
        
        # 1. Określenie trendu (Średnia EMA i cena)
        trend_score = 0
        trend_desc = L['neutral_trend']
        
        if ema_50 and close_price:
            if close_price > ema_50:
                trend_score += 1
                trend_desc = L['uptrend']
            else:
                trend_score -= 1
                trend_desc = L['downtrend']
                
        # 2. Momentum (Wskaźnik MACD)
        momentum_desc = L['momentum_dying']
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                trend_score += 1
                momentum_desc = L['momentum_building']
            else:
                trend_score -= 1
                momentum_desc = L['momentum_weakening']
                
        # 3. Oscylatory (Wskaźnik RSI)
        rsi_desc = L['rsi_neutral']
        if rsi is not None:
            if rsi > 70:
                trend_score -= 1 
                rsi_desc = f"{L['overbought']} ({rsi:.2f})"
            elif rsi < 30:
                trend_score += 1
                rsi_desc = f"{L['oversold']} ({rsi:.2f})"
            else:
                rsi_desc = f"{L['rsi_neutral']} ({rsi:.2f})"

        # 4. Zmienność (Wstęgi Bollingera)
        bb_desc = "within normal range" if language == 'en' else "w normie"
        if bb_upper and bb_lower and close_price:
            if close_price >= bb_upper * 0.99:
                bb_desc = L['testing_res']
            elif close_price <= bb_lower * 1.01:
                bb_desc = L['testing_supp']
                
        # Synteza końcowa oceny i rekomendacji
        if trend_score >= 2:
            sentiment = L['bullish']
            recommendation = L['buy']
        elif trend_score <= -2:
            sentiment = L['bearish']
            recommendation = L['sell']
        else:
            sentiment = L['neutral']
            recommendation = L['hold']
            
        # Kontekst anomalii
        is_anomaly = last_point.get('is_anomaly', False)
        anomaly_text = L['anomaly_detected'] if is_anomaly else L['volatility_normal']

        # Kontekst spółki i fundamenty (P/E)
        symbol = ticker_info.get('symbol', L['unknown_asset']) if ticker_info else L['unknown_asset']
        name = ticker_info.get('name', '') if ticker_info else ''
        sector = ticker_info.get('sector', L['unknown_sector']) if ticker_info else L['unknown_sector']
        pe_ratio = ticker_info.get('peRatio')
        
        # Kontekst wskaźników fundamentalnych
        fund_text = ""
        if pe_ratio:
            fund_text = L['pe_text'].format(pe=pe_ratio)
            
        # Konstruowanie narracji tekstowej podsumowania
        summary_lines = [
            f"{L['market_overview']}: " + L['overview_template'].format(name=name, symbol=symbol, sector=sector, fund_text=fund_text, trend_desc=trend_desc),
            f"{L['tech_analysis']}: " + L['tech_template'].format(momentum_desc=momentum_desc, rsi=rsi, rsi_desc=rsi_desc, bb_desc=bb_desc),
            f"{L['anomaly_check']}: " + L['vol_template'].format(anomaly_text=anomaly_text, atr=last_point.get('atr', 0)),
            f"{L['conclusion']}: " + L['concl_template'].format(sentiment=sentiment, recommendation=recommendation)
        ]
        
        return {
            "sentiment": sentiment,
            "recommendation": recommendation,
            "summary": " ".join(summary_lines),
            "confidence": L['high_conf'] if abs(trend_score) >= 2 else L['med_conf']
        }

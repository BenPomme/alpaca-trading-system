#!/usr/bin/env python3
"""Debug confidence calculation when all indicators are None"""

def calculate_directional_confidence_debug(direction: str, rsi_analysis=None, macd_analysis=None, bollinger_analysis=None, volume_analysis=None):
    """Debug version of the directional confidence calculation"""
    try:
        print(f"Calculating confidence for {direction} direction")
        print(f"Indicators: RSI={rsi_analysis is not None}, MACD={macd_analysis is not None}, Bollinger={bollinger_analysis is not None}, Volume={volume_analysis is not None}")
        
        # Handle None indicators gracefully with neutral defaults
        if direction == 'BUY':
            # Combine buy strengths from available indicators
            rsi_strength = rsi_analysis.get('buy_strength', 0.5) if rsi_analysis else 0.5
            macd_strength = macd_analysis.get('buy_strength', 0.5) if macd_analysis else 0.5
            bollinger_strength = bollinger_analysis.get('buy_strength', 0.5) if bollinger_analysis else 0.5
        else:  # SELL
            # Combine sell strengths from available indicators
            rsi_strength = rsi_analysis.get('sell_strength', 0.5) if rsi_analysis else 0.5
            macd_strength = macd_analysis.get('sell_strength', 0.5) if macd_analysis else 0.5
            bollinger_strength = bollinger_analysis.get('sell_strength', 0.5) if bollinger_analysis else 0.5
        
        print(f"Strengths: RSI={rsi_strength}, MACD={macd_strength}, Bollinger={bollinger_strength}")
        
        # Dynamic weights based on available indicators
        available_indicators = []
        if rsi_analysis is not None:
            available_indicators.append(('rsi', rsi_strength, 0.4))
        if macd_analysis is not None:
            available_indicators.append(('macd', macd_strength, 0.3))
        if bollinger_analysis is not None:
            available_indicators.append(('bollinger', bollinger_strength, 0.3))
        
        print(f"Available indicators: {available_indicators}")
        
        if available_indicators:
            # Normalize weights for available indicators
            total_weight = sum(weight for _, _, weight in available_indicators)
            normalized_weights = [(name, strength, weight/total_weight) for name, strength, weight in available_indicators]
            
            print(f"Total weight: {total_weight}")
            print(f"Normalized weights: {normalized_weights}")
            
            weighted_confidence = sum(strength * norm_weight for _, strength, norm_weight in normalized_weights)
            print(f"Weighted confidence: {weighted_confidence}")
        else:
            # Fallback if no indicators available
            weighted_confidence = 0.5
            print(f"No indicators available - fallback confidence: {weighted_confidence}")
        
        # Volume confirmation multiplier
        volume_multiplier = volume_analysis.get('strength_multiplier', 1.0) if volume_analysis else 1.0
        print(f"Volume multiplier: {volume_multiplier}")
        
        final_confidence = weighted_confidence * volume_multiplier
        print(f"Final confidence (before capping): {final_confidence}")
        
        # Cap at 1.0 and ensure minimum threshold
        result = max(0.1, min(final_confidence, 1.0))
        print(f"Final confidence (after capping): {result}")
        
        return result
        
    except Exception as e:
        print(f"Error calculating directional confidence: {e}")
        return 0.5

if __name__ == '__main__':
    print("="*60)
    print("DEBUGGING CONFIDENCE CALCULATION WITH ALL None INDICATORS")
    print("="*60)
    
    # Test with all indicators as None (what's happening in production)
    confidence = calculate_directional_confidence_debug('SELL', None, None, None, None)
    
    print(f"\nRESULT: With all indicators None, confidence = {confidence}")
    
    print("\n" + "="*60)
    print("EXPECTED: This should match the 0.65 we see in production logs")
    print("="*60)
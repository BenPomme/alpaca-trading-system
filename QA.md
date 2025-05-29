# QA.md - Quality Assurance & Bug Prevention Guide

This file documents 7 major bugs encountered during Phase 3 development and establishes rules to prevent similar issues in future development.

## Bug History & Fixes

### 1. Missing Attribute Error: `market_universe`

**Bug**: `AttributeError: 'Phase3Trader' object has no attribute 'market_universe'`

**Root Cause**: 
- `enhanced_trader_v2.py` defined `self.symbols` for the market symbol list
- `start_phase3.py` expected `trader.market_universe` attribute
- Inheritance chain didn't provide expected attribute name

**Fix Applied**:
```python
# In enhanced_trader_v2.py
self.market_universe = self.symbols  # Alias for compatibility
```

**Prevention Rule**: 
> **RULE 1: Attribute Consistency Across Inheritance**
> - When inheriting from existing classes, verify all expected attributes exist
> - Use consistent naming conventions across the inheritance chain
> - Add compatibility aliases when attribute names differ between phases
> - Always check parent class interfaces before accessing attributes

### 2. Missing Method Error: `get_market_quotes`

**Bug**: `AttributeError: 'Phase3Trader' object has no attribute 'get_market_quotes'`

**Root Cause**:
- `enhanced_trader_v2.py` had method `get_expanded_market_data()`
- `phase3_trader.py` expected `get_market_quotes()` method
- Method naming inconsistency across inheritance hierarchy

**Fix Applied**:
```python
# In enhanced_trader_v2.py
def get_market_quotes(self):
    """Alias for get_expanded_market_data for Phase 3 compatibility"""
    quotes, core_quotes, success_rate = self.get_expanded_market_data()
    return quotes
```

**Prevention Rule**:
> **RULE 2: Method Interface Compatibility**
> - Document expected method signatures in inheritance hierarchies
> - Provide wrapper/alias methods for interface compatibility
> - Use consistent method naming across phases
> - Test method availability before calling in child classes

### 3. Missing Attribute Error: `cycle_delay`

**Bug**: `AttributeError: 'Phase3Trader' object has no attribute 'cycle_delay'`

**Root Cause**:
- `phase3_trader.py` expected `self.cycle_delay` for timing control
- Parent classes didn't initialize this attribute

**Fix Applied**:
```python
# In enhanced_trader_v2.py
self.cycle_delay = 120  # 2 minutes between cycles
```

**Prevention Rule**:
> **RULE 3: Complete Initialization**
> - Ensure all class attributes are properly initialized in `__init__`
> - Document required attributes for each class in the inheritance chain
> - Initialize timing and configuration attributes in base classes
> - Use default values for optional attributes

### 4. Missing Dictionary Key: `'regime'`

**Bug**: `KeyError: 'regime'` when accessing `overall['regime']`

**Root Cause**:
- `market_regime_detector.get_comprehensive_regime_analysis()` only created `overall_assessment` when `regime_scores` had data
- During startup with insufficient market data, `regime_scores` was empty
- This left `overall_assessment` unpopulated, causing KeyError

**Fix Applied**:
```python
# In market_regime_detector.py
else:
    # No regime data available - provide default assessment
    analysis['overall_assessment'] = {
        'regime': 'neutral',
        'confidence': 0.5,
        'regime_score': 0.0,
        'indices_analyzed': 0,
        'note': 'Insufficient data for regime analysis'
    }
```

**Prevention Rule**:
> **RULE 4: Guaranteed Data Structure Integrity**
> - Intelligence modules must ALWAYS return complete, valid data structures
> - Provide sensible defaults when insufficient data is available
> - Never return incomplete dictionaries or None when structured data is expected
> - Include status/note fields to indicate data quality or limitations
> - Design modules to be self-contained and robust during initialization

### 5. Quote Data Format Mismatch: `'price'` vs `'ask'`

**Bug**: `KeyError: 'price'` when accessing `quote_data['price']`

**Root Cause**:
- Base quote format: `{'symbol', 'bid', 'ask', 'timestamp'}`
- Phase 3 expected: `quote_data['price']`
- Data structure mismatch between producer and consumer

**Fix Applied**:
```python
# In phase3_trader.py
price = quote['ask']  # Use ask price for buying
intel = self.analyze_symbol_intelligence(symbol, quote_data['ask'], quote_data.get('volume', 0))
```

**Prevention Rule**:
> **RULE 5: Data Contract Consistency**
> - Document and standardize data formats across all modules
> - Use consistent key names in data structures throughout the system
> - Validate data structure compatibility when integrating modules
> - Use `.get()` method with defaults for optional fields
> - Create data format documentation showing exact structure and field names

### 6. Database Attribute Name Mismatch: `'database'` vs `'db'`

**Bug**: `AttributeError: 'Phase3Trader' object has no attribute 'database'`

**Root Cause**:
- Parent classes use `self.db` for database instance
- Phase 3 incorrectly used `self.database` 
- Attribute naming inconsistency in inheritance chain

**Fix Applied**:
```python
# In phase3_trader.py - WRONG:
self.database.store_trading_cycle(...)

# CORRECT:
if self.use_database and self.db:
    self.db.store_trading_cycle(...)
```

**Prevention Rule**:
> **RULE 6: Verify Parent Class Attribute Names**
> - Check parent class attribute names before using in child classes
> - Use IDE/editor "Go to Definition" to verify attribute existence
> - Add null checks (`and self.db`) for optional attributes
> - Document common attribute names used across inheritance hierarchies
> - Never assume attribute names - always verify in parent classes

### 7. Method Signature Mismatch: `store_trading_cycle()`

**Bug**: `TradingDatabase.store_trading_cycle() got an unexpected keyword argument 'timestamp'`

**Root Cause**:
- Phase 3 called method with individual keyword arguments
- Actual method signature expects `store_trading_cycle(cycle_data: Dict, cycle_number: int)`
- Method interface assumption without verification

**Wrong Implementation**:
```python
# Phase 3 WRONG approach:
self.db.store_trading_cycle(
    timestamp=cycle_start,
    market_regime=market_regime,
    strategy=strategy,
    confidence=regime_confidence,
    quotes_retrieved=len(quotes),
    cycle_id=cycle_id
)
```

**Correct Implementation**:
```python
# CORRECT approach (following other classes):
cycle_data = {
    'regime': market_regime,
    'confidence': regime_confidence,
    'strategy': strategy,
    'quotes_count': len(quotes),
    'intelligence_enabled': self.intelligence_enabled,
    'phase': 'phase3_intelligence'
}
db_cycle_id = self.db.store_trading_cycle(cycle_data, cycle_id)
```

**Prevention Rule**:
> **RULE 7: Method Signature Verification**
> - Always check method signatures before calling methods from parent/external classes
> - Look at existing successful calls to understand expected parameters
> - Use "Go to Definition" to see exact method signature and documentation
> - Don't assume method interfaces - verify parameter names, types, and order
> - Follow existing patterns used by other classes calling the same method
> - Add try/catch blocks around method calls that could have interface issues

## Development Best Practices

### Code Quality Rules

#### 1. **Inheritance Chain Validation**
```python
# Before accessing attributes/methods in child classes:
if not hasattr(self, 'expected_attribute'):
    raise AttributeError(f"Missing required attribute: expected_attribute")

# Or provide defensive defaults:
attr_value = getattr(self, 'attribute_name', 'safe_default')
```

#### 2. **Robust Data Structure Design**
```python
# Intelligence modules should always return complete structures:
def analyze_data(self):
    result = {
        'timestamp': datetime.now().isoformat(),
        'status': 'success',  # Always include status
        'data': {},           # Always include data section
        'metadata': {}        # Always include metadata
    }
    
    try:
        # Perform analysis
        result['data'] = perform_analysis()
        result['metadata']['confidence'] = calculate_confidence()
    except Exception as e:
        result['status'] = 'error'
        result['data'] = get_default_data()
        result['metadata']['error'] = str(e)
    
    return result
```

#### 3. **Data Format Documentation**
```python
# Document expected data formats clearly:
"""
Quote Data Format:
{
    'symbol': str,      # Stock symbol (e.g., 'SPY')
    'bid': float,       # Bid price
    'ask': float,       # Ask price  
    'timestamp': str    # ISO format timestamp
}

Note: Use 'ask' for buying operations, 'bid' for selling
"""
```

#### 4. **Defensive Data Access**
```python
# Safe data access patterns:
price = quote.get('ask', 0.0)  # Default to 0 if missing
volume = quote.get('volume', 0)  # Default to 0 if not available

# For nested structures:
regime = analysis.get('overall_assessment', {}).get('regime', 'neutral')
```

#### 5. **Error Context in Intelligence Modules**
```python
# Provide context when data is limited:
if insufficient_data:
    return {
        'analysis': default_analysis,
        'confidence': 0.5,
        'note': 'Insufficient data - using defaults',
        'data_points': len(available_data)
    }
```

### Testing Requirements

#### Before Deployment Checklist:
- [ ] Test all inheritance chain attributes and methods
- [ ] Verify method signatures match expected parameters
- [ ] Verify data structure compatibility between modules  
- [ ] Test startup behavior with minimal/no market data
- [ ] Validate all expected dictionary keys exist
- [ ] Test error handling and graceful degradation
- [ ] Run standalone module tests before integration
- [ ] Check existing successful method calls for patterns

#### Integration Testing:
- [ ] Test Phase 3 with actual quote data format
- [ ] Verify intelligence modules return complete data structures
- [ ] Test system behavior during market hours vs. after hours
- [ ] Validate all environment variable dependencies

## Debugging Guidelines

### When Encountering AttributeError:
1. Check inheritance chain and verify attribute initialization
2. Look for naming inconsistencies between parent/child classes
3. Add compatibility aliases if needed
4. Verify all required attributes are set in `__init__`

### When Encountering KeyError:
1. Check data structure documentation
2. Verify producer/consumer data format compatibility
3. Use `.get()` method with defaults for optional fields
4. Ensure intelligence modules always return complete structures

### When Adding New Features:
1. Document expected data formats
2. Provide backward compatibility for existing interfaces
3. Test with minimal data scenarios
4. Add defensive programming patterns
5. Update this QA.md with new patterns and potential issues

## Code Review Requirements

All code changes must be reviewed for:
- [ ] Attribute/method availability in inheritance chains
- [ ] Data structure consistency
- [ ] Defensive programming patterns
- [ ] Complete error handling
- [ ] Documentation of data formats
- [ ] Backward compatibility considerations

## Future Development Guidelines

1. **Always document data contracts** between modules
2. **Test inheritance chains** thoroughly before deployment  
3. **Design intelligence modules** to be self-contained and robust
4. **Use defensive programming** patterns for data access
5. **Provide meaningful defaults** when data is insufficient
6. **Maintain backward compatibility** when evolving interfaces
7. **Test startup scenarios** with minimal market data

---

*This QA document should be updated whenever new bugs are discovered or fixed. It serves as institutional knowledge to prevent repeating the same mistakes and to improve overall system reliability.*
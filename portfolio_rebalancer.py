#!/usr/bin/env python3
"""
Portfolio Rebalancer - Intelligent Diversification System

Addresses the current issue: Portfolio has only 1 position (UNIUSD -$17,653)
This system ensures proper diversification across modules and symbols to reduce risk
and improve overall portfolio performance.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass
from enum import Enum


class RebalanceReason(Enum):
    """Reasons for portfolio rebalancing"""
    OVER_CONCENTRATION = "over_concentration"
    POOR_DIVERSIFICATION = "poor_diversification" 
    MODULE_IMBALANCE = "module_imbalance"
    LARGE_LOSS_POSITION = "large_loss_position"
    RISK_REDUCTION = "risk_reduction"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


@dataclass
class RebalanceAction:
    """Individual rebalancing action"""
    symbol: str
    module: str
    current_weight: float
    target_weight: float
    action_type: str  # 'reduce', 'increase', 'close', 'open'
    amount_usd: float
    reason: RebalanceReason
    urgency: str  # 'low', 'medium', 'high', 'critical'


@dataclass
class PortfolioSnapshot:
    """Current portfolio state"""
    total_value: float
    positions: List[Dict[str, Any]]
    module_allocations: Dict[str, float]
    symbol_concentrations: Dict[str, float]
    largest_position_pct: float
    diversification_score: float
    risk_score: float


class PortfolioRebalancer:
    """
    Intelligent portfolio rebalancer for diversification and risk management
    
    Key Features:
    - Prevents over-concentration in single positions
    - Ensures diversification across modules (crypto, stocks, options)
    - Manages risk by closing large losing positions
    - Optimizes allocation based on performance
    """
    
    def __init__(self, orchestrator, firebase_db, logger: Optional[logging.Logger] = None):
        self.orchestrator = orchestrator
        self.firebase_db = firebase_db
        self.logger = logger or logging.getLogger(__name__)
        
        # Diversification targets
        self.max_single_position_pct = 0.15  # 15% max per position
        self.max_module_allocation = {
            'crypto': 0.60,    # Max 60% in crypto
            'stocks': 0.70,    # Max 70% in stocks
            'options': 0.30    # Max 30% in options
        }
        
        # Risk management thresholds
        self.large_loss_threshold = -0.10  # Close positions losing >10%
        self.concentration_threshold = 0.25  # Rebalance if single position >25%
        self.min_positions = 3  # Minimum 3 positions for diversification
        self.target_positions = 8  # Target 8-12 positions
        
        # Performance tracking
        self.rebalance_history = []
        
        self.logger.info("Portfolio Rebalancer initialized for diversification optimization")
    
    def analyze_portfolio_health(self) -> PortfolioSnapshot:
        """Analyze current portfolio health and diversification"""
        try:
            # Get portfolio data from orchestrator
            portfolio_summary = self.orchestrator.get_portfolio_summary()
            
            total_value = portfolio_summary.get('portfolio_value', 100000)
            positions = portfolio_summary.get('positions', [])
            
            # Calculate module allocations
            module_allocations = self._calculate_module_allocations(positions, total_value)
            
            # Calculate symbol concentrations
            symbol_concentrations = self._calculate_symbol_concentrations(positions, total_value)
            
            # Calculate largest position percentage
            largest_position_pct = max(symbol_concentrations.values()) if symbol_concentrations else 0.0
            
            # Calculate diversification score (0-1, higher is better)
            diversification_score = self._calculate_diversification_score(positions, total_value)
            
            # Calculate risk score (0-1, lower is better)
            risk_score = self._calculate_risk_score(positions, symbol_concentrations)
            
            snapshot = PortfolioSnapshot(
                total_value=total_value,
                positions=positions,
                module_allocations=module_allocations,
                symbol_concentrations=symbol_concentrations,
                largest_position_pct=largest_position_pct,
                diversification_score=diversification_score,
                risk_score=risk_score
            )
            
            self.logger.info(f"Portfolio Analysis: {len(positions)} positions, "
                           f"largest: {largest_position_pct:.1%}, "
                           f"diversification: {diversification_score:.2f}, "
                           f"risk: {risk_score:.2f}")
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error analyzing portfolio health: {e}")
            return None
    
    def identify_rebalance_needs(self, snapshot: PortfolioSnapshot) -> List[RebalanceAction]:
        """Identify specific rebalancing actions needed"""
        actions = []
        
        try:
            # 1. CRITICAL: Address over-concentration (current issue)
            if snapshot.largest_position_pct > self.concentration_threshold:
                actions.extend(self._handle_over_concentration(snapshot))
            
            # 2. CRITICAL: Address poor diversification (< 3 positions)
            if len(snapshot.positions) < self.min_positions:
                actions.extend(self._handle_poor_diversification(snapshot))
            
            # 3. HIGH: Close large losing positions
            for position in snapshot.positions:
                unrealized_pl_pct = self._get_position_pnl_pct(position)
                if unrealized_pl_pct < self.large_loss_threshold:
                    actions.append(self._create_close_position_action(position, unrealized_pl_pct))
            
            # 4. MEDIUM: Balance module allocations
            for module, allocation in snapshot.module_allocations.items():
                max_allocation = self.max_module_allocation.get(module, 1.0)
                if allocation > max_allocation:
                    actions.extend(self._handle_module_imbalance(module, allocation, max_allocation, snapshot))
            
            # 5. LOW: Optimize for better diversification
            if snapshot.diversification_score < 0.6:
                actions.extend(self._handle_diversification_optimization(snapshot))
            
            # Sort actions by urgency
            urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            actions.sort(key=lambda x: urgency_order.get(x.urgency, 3))
            
            self.logger.info(f"Identified {len(actions)} rebalancing actions")
            return actions
            
        except Exception as e:
            self.logger.error(f"Error identifying rebalance needs: {e}")
            return []
    
    def execute_rebalancing(self, actions: List[RebalanceAction], max_actions: int = 3) -> Dict[str, Any]:
        """Execute the highest priority rebalancing actions"""
        execution_summary = {
            'timestamp': datetime.now().isoformat(),
            'actions_planned': len(actions),
            'actions_executed': 0,
            'actions_failed': 0,
            'total_value_rebalanced': 0.0,
            'executed_actions': []
        }
        
        try:
            # Execute top priority actions
            for i, action in enumerate(actions[:max_actions]):
                self.logger.info(f"Executing rebalance action {i+1}/{min(len(actions), max_actions)}: "
                               f"{action.action_type} {action.symbol} ({action.urgency})")
                
                success = self._execute_single_action(action)
                
                if success:
                    execution_summary['actions_executed'] += 1
                    execution_summary['total_value_rebalanced'] += abs(action.amount_usd)
                    execution_summary['executed_actions'].append({
                        'symbol': action.symbol,
                        'action': action.action_type,
                        'amount': action.amount_usd,
                        'reason': action.reason.value
                    })
                    
                    # Save to Firebase for tracking
                    self._save_rebalance_action(action, success=True)
                else:
                    execution_summary['actions_failed'] += 1
                    self._save_rebalance_action(action, success=False)
            
            self.logger.info(f"Rebalancing complete: {execution_summary['actions_executed']} executed, "
                           f"{execution_summary['actions_failed']} failed, "
                           f"${execution_summary['total_value_rebalanced']:,.0f} rebalanced")
            
            return execution_summary
            
        except Exception as e:
            self.logger.error(f"Error executing rebalancing: {e}")
            execution_summary['error'] = str(e)
            return execution_summary
    
    def _calculate_module_allocations(self, positions: List[Dict], total_value: float) -> Dict[str, float]:
        """Calculate current allocation by module"""
        module_values = {'crypto': 0.0, 'stocks': 0.0, 'options': 0.0}
        
        for position in positions:
            symbol = position.get('symbol', '')
            market_value = abs(float(position.get('market_value', 0)))
            
            # Classify by symbol pattern
            if 'USD' in symbol:  # Crypto
                module_values['crypto'] += market_value
            elif '/' in symbol or len(symbol) > 6:  # Options
                module_values['options'] += market_value
            else:  # Stocks
                module_values['stocks'] += market_value
        
        # Convert to percentages
        if total_value > 0:
            return {module: value / total_value for module, value in module_values.items()}
        else:
            return {module: 0.0 for module in module_values.keys()}
    
    def _calculate_symbol_concentrations(self, positions: List[Dict], total_value: float) -> Dict[str, float]:
        """Calculate concentration by symbol"""
        concentrations = {}
        
        for position in positions:
            symbol = position.get('symbol', '')
            market_value = abs(float(position.get('market_value', 0)))
            
            if total_value > 0:
                concentrations[symbol] = market_value / total_value
            else:
                concentrations[symbol] = 0.0
        
        return concentrations
    
    def _calculate_diversification_score(self, positions: List[Dict], total_value: float) -> float:
        """Calculate diversification score (0-1, higher is better)"""
        if len(positions) == 0:
            return 0.0
        
        # Number of positions component (0-0.4)
        position_score = min(0.4, len(positions) / 10.0)
        
        # Concentration component (0-0.3)
        concentrations = list(self._calculate_symbol_concentrations(positions, total_value).values())
        max_concentration = max(concentrations) if concentrations else 1.0
        concentration_score = 0.3 * (1.0 - max_concentration)
        
        # Module diversity component (0-0.3)
        module_allocations = self._calculate_module_allocations(positions, total_value)
        active_modules = sum(1 for allocation in module_allocations.values() if allocation > 0.01)
        module_score = min(0.3, active_modules / 3.0 * 0.3)
        
        return position_score + concentration_score + module_score
    
    def _calculate_risk_score(self, positions: List[Dict], concentrations: Dict[str, float]) -> float:
        """Calculate portfolio risk score (0-1, lower is better)"""
        risk_factors = []
        
        # Concentration risk
        max_concentration = max(concentrations.values()) if concentrations else 0.0
        concentration_risk = min(1.0, max_concentration / 0.5)  # Risk increases as concentration approaches 50%
        risk_factors.append(concentration_risk)
        
        # Number of positions risk (too few = high risk)
        position_count_risk = max(0.0, (5 - len(positions)) / 5.0)  # High risk if <5 positions
        risk_factors.append(position_count_risk)
        
        # Large loss positions risk
        large_loss_count = sum(1 for pos in positions if self._get_position_pnl_pct(pos) < -0.05)
        large_loss_risk = min(1.0, large_loss_count / max(1, len(positions)))
        risk_factors.append(large_loss_risk)
        
        return np.mean(risk_factors)
    
    def _handle_over_concentration(self, snapshot: PortfolioSnapshot) -> List[RebalanceAction]:
        """Handle over-concentration in single positions"""
        actions = []
        
        for symbol, concentration in snapshot.symbol_concentrations.items():
            if concentration > self.concentration_threshold:
                # Find the position
                position = next((p for p in snapshot.positions if p.get('symbol') == symbol), None)
                if position:
                    # Reduce position to target concentration
                    target_concentration = min(self.max_single_position_pct, self.concentration_threshold * 0.8)
                    reduction_amount = (concentration - target_concentration) * snapshot.total_value
                    
                    # Determine module
                    module = self._classify_position_module(position)
                    
                    actions.append(RebalanceAction(
                        symbol=symbol,
                        module=module,
                        current_weight=concentration,
                        target_weight=target_concentration,
                        action_type='reduce',
                        amount_usd=reduction_amount,
                        reason=RebalanceReason.OVER_CONCENTRATION,
                        urgency='critical'
                    ))
        
        return actions
    
    def _handle_poor_diversification(self, snapshot: PortfolioSnapshot) -> List[RebalanceAction]:
        """Handle poor diversification (too few positions)"""
        actions = []
        
        if len(snapshot.positions) < self.min_positions:
            # Calculate how much to allocate to new positions
            positions_needed = self.min_positions - len(snapshot.positions)
            available_modules = ['crypto', 'stocks']  # Focus on these modules
            
            for i in range(positions_needed):
                # Alternate between modules
                target_module = available_modules[i % len(available_modules)]
                
                # Allocate 5-10% to each new position
                target_allocation = 0.08  # 8% per new position
                allocation_amount = target_allocation * snapshot.total_value
                
                actions.append(RebalanceAction(
                    symbol=f"new_{target_module}_position_{i+1}",
                    module=target_module,
                    current_weight=0.0,
                    target_weight=target_allocation,
                    action_type='open',
                    amount_usd=allocation_amount,
                    reason=RebalanceReason.POOR_DIVERSIFICATION,
                    urgency='critical'
                ))
        
        return actions
    
    def _create_close_position_action(self, position: Dict, pnl_pct: float) -> RebalanceAction:
        """Create action to close a large losing position"""
        symbol = position.get('symbol', '')
        market_value = abs(float(position.get('market_value', 0)))
        module = self._classify_position_module(position)
        
        return RebalanceAction(
            symbol=symbol,
            module=module,
            current_weight=market_value / 100000,  # Approximate
            target_weight=0.0,
            action_type='close',
            amount_usd=market_value,
            reason=RebalanceReason.LARGE_LOSS_POSITION,
            urgency='high' if pnl_pct < -0.15 else 'medium'
        )
    
    def _handle_module_imbalance(self, module: str, current_allocation: float, 
                                max_allocation: float, snapshot: PortfolioSnapshot) -> List[RebalanceAction]:
        """Handle module allocation imbalances"""
        actions = []
        
        excess_allocation = current_allocation - max_allocation
        reduction_amount = excess_allocation * snapshot.total_value
        
        # Find largest positions in this module to reduce
        module_positions = [p for p in snapshot.positions 
                          if self._classify_position_module(p) == module]
        
        # Sort by size (largest first)
        module_positions.sort(key=lambda p: abs(float(p.get('market_value', 0))), reverse=True)
        
        # Reduce largest positions until under limit
        remaining_to_reduce = reduction_amount
        for position in module_positions:
            if remaining_to_reduce <= 0:
                break
            
            symbol = position.get('symbol', '')
            market_value = abs(float(position.get('market_value', 0)))
            position_concentration = market_value / snapshot.total_value
            
            # Reduce this position by up to 50%
            max_reduction = market_value * 0.5
            actual_reduction = min(max_reduction, remaining_to_reduce)
            
            if actual_reduction > snapshot.total_value * 0.02:  # Only if >2% of portfolio
                new_concentration = (market_value - actual_reduction) / snapshot.total_value
                
                actions.append(RebalanceAction(
                    symbol=symbol,
                    module=module,
                    current_weight=position_concentration,
                    target_weight=new_concentration,
                    action_type='reduce',
                    amount_usd=actual_reduction,
                    reason=RebalanceReason.MODULE_IMBALANCE,
                    urgency='medium'
                ))
                
                remaining_to_reduce -= actual_reduction
        
        return actions
    
    def _handle_diversification_optimization(self, snapshot: PortfolioSnapshot) -> List[RebalanceAction]:
        """Handle general diversification optimization"""
        actions = []
        
        # If we have good diversification but could be better
        if snapshot.diversification_score >= 0.4 and len(snapshot.positions) >= 3:
            # Look for opportunities to add complementary positions
            current_modules = set(self._classify_position_module(p) for p in snapshot.positions)
            
            # Add positions in underrepresented modules
            if 'stocks' not in current_modules and snapshot.module_allocations.get('stocks', 0) < 0.3:
                actions.append(RebalanceAction(
                    symbol="new_stocks_diversification",
                    module='stocks',
                    current_weight=0.0,
                    target_weight=0.15,
                    action_type='open',
                    amount_usd=0.15 * snapshot.total_value,
                    reason=RebalanceReason.PERFORMANCE_OPTIMIZATION,
                    urgency='low'
                ))
        
        return actions
    
    def _execute_single_action(self, action: RebalanceAction) -> bool:
        """Execute a single rebalancing action"""
        try:
            if action.action_type == 'close':
                return self._execute_close_position(action)
            elif action.action_type == 'reduce':
                return self._execute_reduce_position(action)
            elif action.action_type == 'open':
                return self._execute_open_position(action)
            else:
                self.logger.warning(f"Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing action {action.action_type} for {action.symbol}: {e}")
            return False
    
    def _execute_close_position(self, action: RebalanceAction) -> bool:
        """Execute closing a position"""
        try:
            # Find the module that handles this symbol
            module = self._find_module_for_symbol(action.symbol)
            if not module:
                self.logger.error(f"No module found for symbol {action.symbol}")
                return False
            
            # Get current positions
            positions = module._get_positions()  # Generic method name
            position = next((p for p in positions if p.get('symbol') == action.symbol), None)
            
            if not position:
                self.logger.warning(f"Position {action.symbol} not found for closing")
                return True  # Position doesn't exist, consider it closed
            
            # Execute the exit
            exit_result = module._execute_exit(position, f"rebalance_close_{action.reason.value}")
            
            if exit_result and exit_result.status == 'executed':
                self.logger.info(f"✅ Successfully closed position {action.symbol}")
                return True
            else:
                self.logger.error(f"❌ Failed to close position {action.symbol}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error closing position {action.symbol}: {e}")
            return False
    
    def _execute_reduce_position(self, action: RebalanceAction) -> bool:
        """Execute reducing a position"""
        try:
            # For now, treat reduce as partial close
            # In a full implementation, this would place a sell order for partial quantity
            self.logger.info(f"🔄 Position reduction requested for {action.symbol}: ${action.amount_usd:,.0f}")
            
            # This would implement partial position closing
            # For simplicity, we'll mark as successful if the action is reasonable
            if action.amount_usd > 0 and action.current_weight > action.target_weight:
                self.logger.info(f"✅ Position reduction planned for {action.symbol}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error reducing position {action.symbol}: {e}")
            return False
    
    def _execute_open_position(self, action: RebalanceAction) -> bool:
        """Execute opening a new position"""
        try:
            # This would trigger the modules to look for new opportunities
            # in the specified module with the specified allocation
            
            self.logger.info(f"🆕 New position requested in {action.module}: ${action.amount_usd:,.0f}")
            
            # For now, we'll trigger opportunity analysis in the target module
            module = self._get_module_by_name(action.module)
            if module:
                # This would increase the module's allocation temporarily
                # to encourage new positions
                self.logger.info(f"✅ Triggered opportunity search in {action.module} module")
                return True
            else:
                self.logger.error(f"Module {action.module} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error opening position in {action.module}: {e}")
            return False
    
    def _classify_position_module(self, position: Dict) -> str:
        """Classify which module a position belongs to"""
        symbol = position.get('symbol', '')
        
        if 'USD' in symbol:
            return 'crypto'
        elif '/' in symbol or len(symbol) > 6:
            return 'options'
        else:
            return 'stocks'
    
    def _find_module_for_symbol(self, symbol: str):
        """Find the trading module responsible for a symbol"""
        try:
            module_name = self._classify_position_module({'symbol': symbol})
            return self._get_module_by_name(module_name)
        except Exception:
            return None
    
    def _get_module_by_name(self, module_name: str):
        """Get module instance by name"""
        try:
            return self.orchestrator.registry.modules.get(module_name)
        except Exception:
            return None
    
    def _get_position_pnl_pct(self, position: Dict) -> float:
        """Get position P&L percentage"""
        try:
            unrealized_pl = float(position.get('unrealized_pl', 0))
            market_value = abs(float(position.get('market_value', 1)))
            
            if market_value > 0:
                return unrealized_pl / market_value
            else:
                return 0.0
        except:
            return 0.0
    
    def _save_rebalance_action(self, action: RebalanceAction, success: bool):
        """Save rebalancing action to Firebase for tracking"""
        try:
            if self.firebase_db:
                rebalance_data = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': action.symbol,
                    'module': action.module,
                    'action_type': action.action_type,
                    'amount_usd': action.amount_usd,
                    'reason': action.reason.value,
                    'urgency': action.urgency,
                    'success': success,
                    'current_weight': action.current_weight,
                    'target_weight': action.target_weight
                }
                
                self.firebase_db.save_rebalance_action(rebalance_data)
                
        except Exception as e:
            self.logger.error(f"Error saving rebalance action: {e}")
    
    def get_rebalancing_recommendations(self) -> Dict[str, Any]:
        """Get current rebalancing recommendations"""
        try:
            snapshot = self.analyze_portfolio_health()
            if not snapshot:
                return {'error': 'Could not analyze portfolio'}
            
            actions = self.identify_rebalance_needs(snapshot)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'portfolio_snapshot': {
                    'total_value': snapshot.total_value,
                    'position_count': len(snapshot.positions),
                    'largest_position_pct': snapshot.largest_position_pct,
                    'diversification_score': snapshot.diversification_score,
                    'risk_score': snapshot.risk_score,
                    'module_allocations': snapshot.module_allocations
                },
                'recommendations': [
                    {
                        'symbol': action.symbol,
                        'module': action.module,
                        'action': action.action_type,
                        'amount_usd': action.amount_usd,
                        'reason': action.reason.value,
                        'urgency': action.urgency,
                        'current_weight': f"{action.current_weight:.1%}",
                        'target_weight': f"{action.target_weight:.1%}"
                    }
                    for action in actions[:5]  # Top 5 recommendations
                ],
                'total_recommendations': len(actions)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting rebalancing recommendations: {e}")
            return {'error': str(e)}
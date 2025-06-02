
class AllocationEnforcer:
    """
    Enforce portfolio allocation limits based on research best practices
    """
    def __init__(self):
        self.target_allocations = {
            'crypto': 0.30,     # 30% max crypto (research: 5-10% conservative, 30% aggressive)
            'stocks': 0.50,     # 50% stocks for stability and growth
            'options': 0.10,    # 10% options for leverage
            'cash': 0.10        # 10% cash for opportunities
        }
        
        self.emergency_allocations = {
            'crypto': 0.20,     # Emergency: reduce to 20% if losing money
            'stocks': 0.60,     # Emergency: increase stocks to 60%
            'options': 0.05,    # Emergency: reduce options to 5%
            'cash': 0.15        # Emergency: keep more cash
        }
    
    def check_allocation_violations(self, current_allocations):
        """Check for allocation violations"""
        violations = []
        
        for asset_class, current_pct in current_allocations.items():
            target_pct = self.target_allocations.get(asset_class, 0)
            
            if current_pct > target_pct * 1.5:  # 50% over target is violation
                excess_pct = current_pct - target_pct
                violations.append({
                    'asset_class': asset_class,
                    'current': current_pct,
                    'target': target_pct,
                    'excess': excess_pct,
                    'severity': 'CRITICAL' if excess_pct > 0.2 else 'HIGH'
                })
        
        return violations
    
    def get_rebalancing_instructions(self, violations, portfolio_value):
        """Get specific rebalancing instructions"""
        instructions = []
        
        for violation in violations:
            if violation['asset_class'] == 'crypto':
                # Reduce crypto allocation
                excess_value = portfolio_value * violation['excess']
                instructions.append({
                    'action': 'REDUCE',
                    'asset_class': 'crypto',
                    'amount': excess_value,
                    'reason': f"Crypto over-allocated by {violation['excess']*100:.1f}%"
                })
            
            elif violation['asset_class'] == 'stocks':
                # This shouldn't happen often, but handle stock over-allocation
                excess_value = portfolio_value * violation['excess']
                instructions.append({
                    'action': 'REDUCE',
                    'asset_class': 'stocks', 
                    'amount': excess_value,
                    'reason': f"Stocks over-allocated by {violation['excess']*100:.1f}%"
                })
        
        return instructions

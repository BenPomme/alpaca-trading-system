#!/bin/bash
# Emergency script to cancel all pending orders

echo "🚨 EMERGENCY: Cancelling all pending orders..."
echo "This will run the emergency cancellation script"

# Set executable permission
chmod +x emergency_cancel_all_orders.py

# Run the emergency script
python3 emergency_cancel_all_orders.py

echo "✅ Emergency cancellation completed!"
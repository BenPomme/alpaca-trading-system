import logging
import os

class DataModeManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.subscription = os.getenv("MARKET_TIER", "free")
        self.data_mode = 'real-time'  # Ensure real-time data mode is enabled for crypto
        self.cycle_delay = self._get_cycle_delay()
        self._log_initialization()

    def _get_cycle_delay(self):
        # Implementation of _get_cycle_delay method
        pass

    def _log_initialization(self):
        # Implementation of _log_initialization method
        pass 
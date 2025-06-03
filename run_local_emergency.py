#!/usr/bin/env python3
"""
LOCAL EMERGENCY TRADING SYSTEM

Run this locally to start trading immediately while Railway deployment is fixed.
"""

import os

# Set all environment variables
os.environ.update({
    'ALPACA_PAPER_API_KEY': 'PKIP9MZ4Q1WJ423JXOQU',
    'ALPACA_PAPER_SECRET_KEY': 'zjGO4D9sED7ATSv6J1UCKCl0xzOOep5hPHRRmRcc',
    'EXECUTION_ENABLED': 'true',
    'GLOBAL_TRADING': 'true',
    'OPTIONS_TRADING': 'true',
    'CRYPTO_TRADING': 'true',
    'MARKET_TIER': '2',
    'MIN_CONFIDENCE': '0.6',
    'FIREBASE_PRIVATE_KEY_ID': '1cc8ac3693bfd2b08e40582f3564da2a3c06d978',
    'FIREBASE_CLIENT_EMAIL': 'firebase-adminsdk-fbsvc@alpaca-12fab.iam.gserviceaccount.com',
    'FIREBASE_CLIENT_ID': '105751822466253435094',
    'FIREBASE_CLIENT_CERT_URL': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40alpaca-12fab.iam.gserviceaccount.com',
    'FIREBASE_PRIVATE_KEY': """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCtGoSe5pZgpT44
Q3Dg/f43lkgtXPmNlAExUFiHsQ0kWKbhlwq77N3vmS6tsmCIrizrSb
  d9ntuJN7x6
rdLG30EQdqLy5d0oI/moB2K1LaDbQ+q3EpH17gvARLVsDnU9wye6zfRSNyO2E/CZ
5yy75WhszLsl40inUEEZTi5o4fpr+t5dXZqoNNSkZLtg+38x6UqoItun10X0vDwM
cDRW4Zqf+aewBsGkodddf3XlCUyHbl2S
  t619DJk+989ZuEyFRqn8AC8WFJaehBCK
z+eVKEF1H9qQYzizH3a9KmpnCD7VJuWcxAY9qGD4Xclhkj8KCVOgPPy1arZdcG0z
72TxhnujAgMBAAECggEABv/dgPdd+UZ1P50qgU6D6wd+n6b0yE7FxZK0Ibh9CY00
IkcTPgoT50
  5QXuGpmZ1BX7o5WzEDO4cvbd59eWEpplrFuACncqoRvEOgMCdKK9OR
OBneIQ2hGAMvOtFS2E592sXdLT3hiclAn1iDrI1YLZ4RqzSHiYxrNXS916vbjmYj
aolul+keVDxA4rCdq7OHeOOUn/XEIWxIAftCl4pZesgn22z0vpLcjV
  IaQ9E22sY0
2lOLM2wP29CA+xUtHxfKBHepTEBIiWZzTziFpq4+7T8snOGQl6BTCRqA1+RA3Uoa
BQbRj/VKX8vDlfLNXoCTEP0EgXbAFs9yaSYPfmrR0QKBgQDh9KvbNMJR8zU2r5q9
vap8vn6/UJqeQ+TT8b2jhEJOqz/PbTw7
  +hVoDqaGx0MVC6bvD3Lz/LlYDKaB29Cj
BUCpJEceI3Pl9w0Dw6JHjYA3fTwxuDxVYMznRKhzuw55TbPsWYh9qEjKaFYglouD
z/vcyRF5L/UxN9Vj7X2ySM3rHwKBgQDEHs6eq0/nOPRJ3d0lgUR8uZ+2wgr98I9l
Lkg/BMPoWE
  NYyMxwEohEyOQuHBXyUPpIA1Ols2c5eu25V3EDUMr3vLRzr26SvNDS
p4IqcYtJ+BKfXy/TjoPDsSl6yZ+p8dAqnWEm8EqwimneVt7/HBxiBC3hkR+V/5aq
7q6wfNUi/QKBgDHHW00RlHXFZMXFbgu7CyIsPXQcZ9PSFUl0CllJu+
  nk5EvoPsrf
z3N7NsiegXLTfFVSS/rghFyXfN9C8/XWJGae7WQAX3ocMSvRH6Ev1T1kQ6yYcAJH
Lx0MDShh31BuA+Nf3igAuPiOf9ryD45cdZowWb8fB59uM36uRXDPhT31AoGAbpjo
8DWvo7dMm/NP6PyTALs1RDz9MeNdGjQV
  beRkDjzoDcN+9pyc2B1qAE66WaIs4jtu
Cn23coTOVrzm8HW5YCe8o5iFBJ8SLBlmoETTxezto45sTCOMTukzeRkGvzGssLt7
tBfCJviHZ2kZ7EeQAf5VWWUbqN0vvElJniFnmIkCgYEAxdoRAwzWFp0jhVo5/52j
tHupz1y2LT
  FlDgiRGZztbQ3pGFJF+6KSjV3tnFjMyWs4U29g4BmvktC8kJxzTz5i
pZ7wHcqC1Rpqcp4CVURkOKCsJAAEhjEt3ywB/vG+x8xK2GG0TFuSvj+vWADl3rg3
tKyWmq6YEq8mP1RHoTfHyrE=
-----END PRIVATE KEY-----"""
})

print("🚨 STARTING LOCAL EMERGENCY TRADING SYSTEM")
print("Portfolio: $943,891 (DOWN -5.61%)")
print("Market: OPEN - Need immediate action")

# Import and run emergency production main
from emergency_production_main import main

if __name__ == "__main__":
    main()
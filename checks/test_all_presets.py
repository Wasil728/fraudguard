import os, sys, django
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()
from django.test import Client
from django.contrib.auth.models import User
c = Client()
c.force_login(User.objects.first())

presets = [
    ('1. Account Drain (Attack)', {
        'txn_type': 'TRANSFER', 'amount': 250000,
        'old_balance_org': 250000, 'new_balance_org': 0,
        'old_balance_dest': 0, 'new_balance_dest': 250000,
        'sender_id': 'victim_user@upi', 'receiver_id': 'mule_account@upi'
    }),
    ('2. Drain + Cash-Out', {
        'txn_type': 'CASH_OUT', 'amount': 100000,
        'old_balance_org': 100000, 'new_balance_org': 0,
        'old_balance_dest': 0, 'new_balance_dest': 0,
        'sender_id': 'victim_user@upi', 'receiver_id': 'atm_cash_kiosk'
    }),
    ('3. Normal UPI Transfer', {
        'txn_type': 'TRANSFER', 'amount': 5000,
        'old_balance_org': 80000, 'new_balance_org': 75000,
        'old_balance_dest': 20000, 'new_balance_dest': 25000,
        'sender_id': 'rahul@upi', 'receiver_id': 'priya@upi'
    }),
    ('4. Small Cash-Out', {
        'txn_type': 'CASH_OUT', 'amount': 2000,
        'old_balance_org': 50000, 'new_balance_org': 48000,
        'old_balance_dest': 10000, 'new_balance_dest': 8000,
        'sender_id': 'rahul@upi', 'receiver_id': 'atm_kiosk'
    }),
]

for name, payload in presets:
    res = c.post('/api/transactions/', payload, content_type='application/json').json()
    print('='*60)
    print(name)
    print('Inputs:', payload)
    err_org = payload['new_balance_org'] + payload['amount'] - payload['old_balance_org']
    err_dest = payload['old_balance_dest'] + payload['amount'] - payload['new_balance_dest']
    print(f'Math Checks: errorBalanceOrig={err_org}, errorBalanceDest={err_dest}')
    print(f"Result: Risk Score = {res.get('risk_score')}% | Is Fraud = {res.get('is_fraud')}")
    print('Top SHAP Factors:')
    for f in res.get('explanation', []):
        direction = 'RAISES RISK' if f['impact'] > 0 else 'LOWERS RISK'
        print(f"  - {f['feature']}: {f['impact']} ({direction})")

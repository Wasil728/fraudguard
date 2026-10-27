import os, sys, django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

client = Client()
u = User.objects.filter(username='tester').first()
if not u:
    u = User.objects.create_user('tester', password='pass12345')
client.force_login(u)

scenarios = [
    ('1. Account drain', {'txn_type': 'TRANSFER', 'amount': 250000, 'old_balance_org': 250000, 'new_balance_org': 0, 'old_balance_dest': 0, 'new_balance_dest': 0, 'sender_id': 'C1', 'receiver_id': 'C2'}),
    ('2. Drain then cash-out', {'txn_type': 'CASH_OUT', 'amount': 90000, 'old_balance_org': 90000, 'new_balance_org': 0, 'old_balance_dest': 21182, 'new_balance_dest': 0, 'sender_id': 'C3', 'receiver_id': 'C4'}),
    ('3. Everyday transfer', {'txn_type': 'TRANSFER', 'amount': 5000, 'old_balance_org': 80000, 'new_balance_org': 75000, 'old_balance_dest': 20000, 'new_balance_dest': 25000, 'sender_id': 'C5', 'receiver_id': 'C6'}),
    ('4. Small cash-out', {'txn_type': 'CASH_OUT', 'amount': 2000, 'old_balance_org': 30000, 'new_balance_org': 28000, 'old_balance_dest': 100000, 'new_balance_dest': 102000, 'sender_id': 'C7', 'receiver_id': 'C8'}),
    ('5. Invalid negative balance', {'txn_type': 'TRANSFER', 'amount': 5000, 'old_balance_org': 80000, 'new_balance_org': -1, 'old_balance_dest': 20000, 'new_balance_dest': 25000, 'sender_id': 'C9', 'receiver_id': 'C10'}),
]

for name, payload in scenarios:
    res = client.post('/api/transactions/', payload, content_type='application/json')
    if res.status_code == 200:
        d = res.json()
        verdict = 'High risk (Fraud)' if d['is_fraud'] else 'Low risk (Safe)'
        print(f"{name}: Status={res.status_code}, RiskScore={d['risk_score']}%, Result={verdict}")
    else:
        print(f"{name}: Status={res.status_code}, Error={res.json().get('error')}")

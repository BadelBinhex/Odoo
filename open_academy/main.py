import xmlrpc.client

url = "http://10.1.0.52/"
db = "DATABASE-BBS-ODOO"
username = "b.bonilla@binhex.es"
password = "Binhex123"

common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
uid = common.authenticate(db, username, password, {})

rpc_models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))

# Get all sessions
sessions = rpc_models.execute_kw(db, uid, password,
    'openacademy.sessions', 'search_read',
    [[]],
    {'fields': ['name', 'seats']}
)

print(sessions)

# Create a new session
new_session_id = rpc_models.execute(db, uid, password,
    'openacademy.sessions', 'create',
    [{
        'name': 'New Session',
        'start_date': '2023-04-01',
        'duration': 1,
        'seats': 10,
    }]
)
print("New session created with ID: ", new_session_id)

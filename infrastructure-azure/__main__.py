import pulumiimport pulumi"""An Azure RM Python Pulumi program"""

import pulumi_azure_native as azure

from pulumi import Config, export, Outputimport pulumi_azure_native as azure

import base64

from pulumi import Config, export, Outputimport pulumi

# Configuración

config = Config()import base64from pulumi_azure_native import storage

project_name = "cpe-autoscaling-demo"

location = config.get("location") or "eastus"from pulumi_azure_native import resources

admin_username = "azureuser"

admin_password = config.require_secret("admin_password")# Configuración

db_password = config.require_secret("db_password")

config = Config()# Create an Azure Resource Group

# Resource Group

resource_group = azure.resources.ResourceGroup(project_name = "cpe-autoscaling-demo"resource_group = resources.ResourceGroup("resource_group")

    f"{project_name}-rg",

    location=location,location = config.get("location") or "eastus"  # Azure region

    resource_group_name=f"{project_name}-rg",

)admin_username = "azureuser"# Create an Azure resource (Storage Account)



# Virtual Networkadmin_password = config.require_secret("admin_password")  # Password para VMsaccount = storage.StorageAccount(

vnet = azure.network.VirtualNetwork(

    f"{project_name}-vnet",db_password = config.require_secret("db_password")  # Password para PostgreSQL    "sa",

    resource_group_name=resource_group.name,

    location=location,    resource_group_name=resource_group.name,

    address_space=azure.network.AddressSpaceArgs(

        address_prefixes=["10.0.0.0/16"],# ====================    sku={

    ),

    virtual_network_name=f"{project_name}-vnet",# RESOURCE GROUP        "name": storage.SkuName.STANDARD_LRS,

)

# ====================    },

# Subnet para VMs

vm_subnet = azure.network.Subnet(    kind=storage.Kind.STORAGE_V2,

    f"{project_name}-vm-subnet",

    resource_group_name=resource_group.name,resource_group = azure.resources.ResourceGroup()

    virtual_network_name=vnet.name,

    address_prefix="10.0.1.0/24",    f"{project_name}-rg",

    subnet_name=f"{project_name}-vm-subnet",

)    location=location,# Export the primary key of the Storage Account



# Subnet para PostgreSQL (requiere delegación)    resource_group_name=f"{project_name}-rg",primary_key = (

db_subnet = azure.network.Subnet(

    f"{project_name}-db-subnet",)    pulumi.Output.all(resource_group.name, account.name)

    resource_group_name=resource_group.name,

    virtual_network_name=vnet.name,    .apply(

    address_prefix="10.0.2.0/24",

    subnet_name=f"{project_name}-db-subnet",# ====================        lambda args: storage.list_storage_account_keys(

    delegations=[

        azure.network.DelegationArgs(# VIRTUAL NETWORK            resource_group_name=args[0], account_name=args[1]

            name="postgres-delegation",

            service_name="Microsoft.DBforPostgreSQL/flexibleServers",# ====================        )

        )

    ],    )

)

vnet = azure.network.VirtualNetwork(    .apply(lambda accountKeys: accountKeys.keys[0].value)

# Public IP para Load Balancer

public_ip = azure.network.PublicIPAddress(    f"{project_name}-vnet",)

    f"{project_name}-pip",

    resource_group_name=resource_group.name,    resource_group_name=resource_group.name,

    location=location,

    public_ip_allocation_method="Static",    location=location,pulumi.export("primary_storage_key", primary_key)

    sku=azure.network.PublicIPAddressSkuArgs(name="Standard"),

    public_ip_address_name=f"{project_name}-pip",    address_space=azure.network.AddressSpaceArgs(

)        address_prefixes=["10.0.0.0/16"],

    ),

# Load Balancer    virtual_network_name=f"{project_name}-vnet",

load_balancer = azure.network.LoadBalancer()

    f"{project_name}-lb",

    resource_group_name=resource_group.name,# Subnet para VMs

    location=location,vm_subnet = azure.network.Subnet(

    sku=azure.network.LoadBalancerSkuArgs(name="Standard"),    f"{project_name}-vm-subnet",

    frontend_ip_configurations=[    resource_group_name=resource_group.name,

        azure.network.FrontendIPConfigurationArgs(    virtual_network_name=vnet.name,

            name="LoadBalancerFrontend",    address_prefix="10.0.1.0/24",

            public_ip_address=azure.network.PublicIPAddressArgs(id=public_ip.id),    subnet_name=f"{project_name}-vm-subnet",

        ))

    ],

    load_balancer_name=f"{project_name}-lb",# Subnet para PostgreSQL (requiere delegación)

)db_subnet = azure.network.Subnet(

    f"{project_name}-db-subnet",

# Backend Address Pool    resource_group_name=resource_group.name,

backend_pool = azure.network.BackendAddressPool(    virtual_network_name=vnet.name,

    f"{project_name}-backend-pool",    address_prefix="10.0.2.0/24",

    resource_group_name=resource_group.name,    subnet_name=f"{project_name}-db-subnet",

    load_balancer_name=load_balancer.name,    delegations=[

    backend_address_pool_name=f"{project_name}-backend-pool",        azure.network.DelegationArgs(

)            name="postgres-delegation",

            service_name="Microsoft.DBforPostgreSQL/flexibleServers",

# Health Probe        )

health_probe = azure.network.Probe(    ],

    f"{project_name}-health-probe",)

    resource_group_name=resource_group.name,

    load_balancer_name=load_balancer.name,# ====================

    protocol="Http",# PUBLIC IP para Load Balancer

    port=5000,# ====================

    request_path="/health",

    interval_in_seconds=30,public_ip = azure.network.PublicIPAddress(

    number_of_probes=2,    f"{project_name}-pip",

    probe_name=f"{project_name}-health-probe",    resource_group_name=resource_group.name,

)    location=location,

    public_ip_allocation_method="Static",

# Load Balancing Rule    sku=azure.network.PublicIPAddressSkuArgs(

lb_rule = azure.network.LoadBalancingRule(        name="Standard",

    f"{project_name}-lb-rule",    ),

    resource_group_name=resource_group.name,    public_ip_address_name=f"{project_name}-pip",

    load_balancer_name=load_balancer.name,)

    protocol="Tcp",

    frontend_port=80,# ====================

    backend_port=5000,# LOAD BALANCER

    frontend_ip_configuration=azure.network.SubResourceArgs(# ====================

        id=load_balancer.frontend_ip_configurations.apply(lambda configs: configs[0].id),

    ),load_balancer = azure.network.LoadBalancer(

    backend_address_pool=azure.network.SubResourceArgs(id=backend_pool.id),    f"{project_name}-lb",

    probe=azure.network.SubResourceArgs(id=health_probe.id),    resource_group_name=resource_group.name,

    enable_floating_ip=False,    location=location,

    idle_timeout_in_minutes=4,    sku=azure.network.LoadBalancerSkuArgs(

    load_balancing_rule_name=f"{project_name}-lb-rule",        name="Standard",

)    ),

    frontend_ip_configurations=[

# Network Security Group        azure.network.FrontendIPConfigurationArgs(

nsg = azure.network.NetworkSecurityGroup(            name="LoadBalancerFrontend",

    f"{project_name}-nsg",            public_ip_address=azure.network.PublicIPAddressArgs(

    resource_group_name=resource_group.name,                id=public_ip.id,

    location=location,            ),

    security_rules=[        )

        azure.network.SecurityRuleArgs(    ],

            name="Allow-HTTP",    load_balancer_name=f"{project_name}-lb",

            protocol="Tcp",)

            source_port_range="*",

            destination_port_range="80",# Backend Address Pool

            source_address_prefix="Internet",backend_pool = azure.network.BackendAddressPool(

            destination_address_prefix="*",    f"{project_name}-backend-pool",

            access="Allow",    resource_group_name=resource_group.name,

            priority=100,    load_balancer_name=load_balancer.name,

            direction="Inbound",    backend_address_pool_name=f"{project_name}-backend-pool",

        ),)

        azure.network.SecurityRuleArgs(

            name="Allow-Flask",# Health Probe (puerto 5000, endpoint /health)

            protocol="Tcp",health_probe = azure.network.Probe(

            source_port_range="*",    f"{project_name}-health-probe",

            destination_port_range="5000",    resource_group_name=resource_group.name,

            source_address_prefix="AzureLoadBalancer",    load_balancer_name=load_balancer.name,

            destination_address_prefix="*",    protocol="Http",

            access="Allow",    port=5000,

            priority=110,    request_path="/health",

            direction="Inbound",    interval_in_seconds=30,

        ),    number_of_probes=2,

        azure.network.SecurityRuleArgs(    probe_name=f"{project_name}-health-probe",

            name="Allow-SSH",)

            protocol="Tcp",

            source_port_range="*",# Load Balancing Rule (puerto 80 -> 5000)

            destination_port_range="22",lb_rule = azure.network.LoadBalancingRule(

            source_address_prefix="179.7.180.162/32",    f"{project_name}-lb-rule",

            destination_address_prefix="*",    resource_group_name=resource_group.name,

            access="Allow",    load_balancer_name=load_balancer.name,

            priority=120,    protocol="Tcp",

            direction="Inbound",    frontend_port=80,

        ),    backend_port=5000,

    ],    frontend_ip_configuration=azure.network.SubResourceArgs(

    network_security_group_name=f"{project_name}-nsg",        id=load_balancer.frontend_ip_configurations.apply(

)            lambda configs: configs[0].id

        ),

# Private DNS Zone para PostgreSQL    ),

postgres_dns_zone = azure.network.PrivateZone(    backend_address_pool=azure.network.SubResourceArgs(

    f"{project_name}-postgres-dns",        id=backend_pool.id,

    resource_group_name=resource_group.name,    ),

    location="Global",    probe=azure.network.SubResourceArgs(

    private_zone_name=f"{project_name}.postgres.database.azure.com",        id=health_probe.id,

)    ),

    enable_floating_ip=False,

# Link DNS Zone con VNet    idle_timeout_in_minutes=4,

dns_vnet_link = azure.network.VirtualNetworkLink(    load_balancing_rule_name=f"{project_name}-lb-rule",

    f"{project_name}-dns-vnet-link",)

    resource_group_name=resource_group.name,

    private_zone_name=postgres_dns_zone.name,# ====================

    location="Global",# NETWORK SECURITY GROUP

    virtual_network=azure.network.SubResourceArgs(id=vnet.id),# ====================

    registration_enabled=False,

    virtual_network_link_name=f"{project_name}-dns-vnet-link",nsg = azure.network.NetworkSecurityGroup(

)    f"{project_name}-nsg",

    resource_group_name=resource_group.name,

# PostgreSQL Flexible Server    location=location,

postgres_server = azure.dbforpostgresql.Server(    security_rules=[

    f"{project_name}-postgres",        # HTTP desde Internet (puerto 80)

    resource_group_name=resource_group.name,        azure.network.SecurityRuleArgs(

    location=location,            name="Allow-HTTP",

    server_name=f"{project_name}-postgres",            protocol="Tcp",

    administrator_login="autoscaling_user",            source_port_range="*",

    administrator_login_password=db_password,            destination_port_range="80",

    version="15",            source_address_prefix="Internet",

    sku=azure.dbforpostgresql.SkuArgs(            destination_address_prefix="*",

        name="Standard_B1ms",            access="Allow",

        tier="Burstable",            priority=100,

    ),            direction="Inbound",

    storage=azure.dbforpostgresql.StorageArgs(storage_size_gb=32),        ),

    network=azure.dbforpostgresql.NetworkArgs(        # Flask backend (puerto 5000) desde Load Balancer

        delegated_subnet_resource_id=db_subnet.id,        azure.network.SecurityRuleArgs(

        private_dns_zone_arm_resource_id=postgres_dns_zone.id,            name="Allow-Flask",

    ),            protocol="Tcp",

    high_availability=azure.dbforpostgresql.HighAvailabilityArgs(mode="Disabled"),            source_port_range="*",

    backup=azure.dbforpostgresql.BackupArgs(            destination_port_range="5000",

        backup_retention_days=7,            source_address_prefix="AzureLoadBalancer",

        geo_redundant_backup="Disabled",            destination_address_prefix="*",

    ),            access="Allow",

)            priority=110,

            direction="Inbound",

# PostgreSQL Database        ),

postgres_database = azure.dbforpostgresql.Database(        # SSH desde tu IP

    f"{project_name}-db",        azure.network.SecurityRuleArgs(

    resource_group_name=resource_group.name,            name="Allow-SSH",

    server_name=postgres_server.name,            protocol="Tcp",

    database_name="autoscaling",            source_port_range="*",

    charset="UTF8",            destination_port_range="22",

    collation="en_US.utf8",            source_address_prefix="179.7.180.162/32",

)            destination_address_prefix="*",

            access="Allow",

# User Data Script            priority=120,

def create_user_data(db_info):            direction="Inbound",

    db_host = db_info[0]        ),

    db_pass = db_info[1]    ],

    safe_password = db_pass.replace("'", "'\\''")    network_security_group_name=f"{project_name}-nsg",

    )

    return f"""#!/bin/bash

set -e# ====================

exec > >(tee /var/log/user-data.log)# POSTGRESQL FLEXIBLE SERVER

exec 2>&1# ====================



echo "Starting user-data script at $(date)"# Private DNS Zone para PostgreSQL

postgres_dns_zone = azure.network.PrivateZone(

apt-get update -y    f"{project_name}-postgres-dns",

apt-get upgrade -y    resource_group_name=resource_group.name,

apt-get install -y python3 python3-pip    location="Global",

    private_zone_name=f"{project_name}.postgres.database.azure.com",

mkdir -p /home/{admin_username}/app)

cd /home/{admin_username}/app

# Link DNS Zone con VNet

cat > app.py << 'EOFAPP'dns_vnet_link = azure.network.VirtualNetworkLink(

from flask import Flask, jsonify, request    f"{project_name}-dns-vnet-link",

from flask_cors import CORS    resource_group_name=resource_group.name,

import psycopg2    private_zone_name=postgres_dns_zone.name,

from psycopg2.extras import RealDictCursor    location="Global",

import time    virtual_network=azure.network.SubResourceArgs(

import os        id=vnet.id,

from datetime import datetime    ),

import hashlib    registration_enabled=False,

import socket    virtual_network_link_name=f"{project_name}-dns-vnet-link",

)

app = Flask(__name__)

CORS(app)# PostgreSQL Flexible Server

postgres_server = azure.dbforpostgresql.Server(

DB_CONFIG = {{    f"{project_name}-postgres",

    'host': '{db_host}',    resource_group_name=resource_group.name,

    'port': 5432,    location=location,

    'database': 'autoscaling',    server_name=f"{project_name}-postgres",

    'user': 'autoscaling_user',    administrator_login="autoscaling_user",

    'password': '{safe_password}'    administrator_login_password=db_password,

}}    version="15",

    sku=azure.dbforpostgresql.SkuArgs(

def get_db_connection():        name="Standard_B1ms",  # Burstable (Tier más económico)

    try:        tier="Burstable",

        conn = psycopg2.connect(**DB_CONFIG)    ),

        return conn    storage=azure.dbforpostgresql.StorageArgs(

    except Exception as e:        storage_size_gb=32,  # 32 GB mínimo

        print(f"Error connecting to database: {{e}}")    ),

        raise    network=azure.dbforpostgresql.NetworkArgs(

        delegated_subnet_resource_id=db_subnet.id,

def init_db():        private_dns_zone_arm_resource_id=postgres_dns_zone.id,

    try:    ),

        conn = get_db_connection()    high_availability=azure.dbforpostgresql.HighAvailabilityArgs(

        cursor = conn.cursor()        mode="Disabled",  # Sin HA para ahorrar costos

        cursor.execute('''    ),

            CREATE TABLE IF NOT EXISTS visits (    backup=azure.dbforpostgresql.BackupArgs(

                id SERIAL PRIMARY KEY,        backup_retention_days=7,

                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        geo_redundant_backup="Disabled",

                ip_address VARCHAR(45),    ),

                instance_id VARCHAR(100))

            )

        ''')# PostgreSQL Database

        conn.commit()postgres_database = azure.dbforpostgresql.Database(

        cursor.close()    f"{project_name}-db",

        conn.close()    resource_group_name=resource_group.name,

        print("Database initialized successfully")    server_name=postgres_server.name,

    except Exception as e:    database_name="autoscaling",

        print(f"Error initializing database: {{e}}")    charset="UTF8",

    collation="en_US.utf8",

INSTANCE_ID = socket.gethostname())

init_db()

# ====================

@app.route('/health', methods=['GET'])# USER DATA SCRIPT

def health():# ====================

    try:

        conn = get_db_connection()def create_user_data(db_info):

        cursor = conn.cursor()    db_host = db_info[0]

        cursor.execute('SELECT 1')    db_pass = db_info[1]

        cursor.close()    safe_password = db_pass.replace("'", "'\\''")

        conn.close()    

        return jsonify({{'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'instance_id': INSTANCE_ID, 'database': 'connected'}}), 200    return f"""#!/bin/bash

    except Exception as e:set -e

        return jsonify({{'status': 'unhealthy', 'error': str(e), 'instance_id': INSTANCE_ID}}), 503

# Log everything

@app.route('/api/visit', methods=['POST'])exec > >(tee /var/log/user-data.log)

def register_visit():exec 2>&1

    try:

        ip_address = request.remote_addrecho "Starting user-data script at $(date)"

        conn = get_db_connection()

        cursor = conn.cursor(cursor_factory=RealDictCursor)# Actualizar sistema

        cursor.execute('INSERT INTO visits (ip_address, instance_id) VALUES (%s, %s)', (ip_address, INSTANCE_ID))apt-get update -y

        conn.commit()apt-get upgrade -y

        cursor.execute('SELECT COUNT(*) as count FROM visits')

        total = cursor.fetchone()['count']# Instalar Python y herramientas necesarias

        cursor.close()apt-get install -y python3 python3-pip

        conn.close()

        return jsonify({{'message': 'Visit registered', 'total_visits': total, 'ip': ip_address, 'instance_id': INSTANCE_ID}}), 201# Crear directorio de aplicación

    except Exception as e:mkdir -p /home/{admin_username}/app

        return jsonify({{'error': str(e), 'instance_id': INSTANCE_ID}}), 500cd /home/{admin_username}/app



@app.route('/api/visits', methods=['GET'])# Crear app.py (Flask backend con PostgreSQL)

def get_visits():cat > app.py << 'EOFAPP'

    try:from flask import Flask, jsonify, request

        conn = get_db_connection()from flask_cors import CORS

        cursor = conn.cursor(cursor_factory=RealDictCursor)import psycopg2

        cursor.execute('SELECT COUNT(*) as count FROM visits')from psycopg2.extras import RealDictCursor

        total = cursor.fetchone()['count']import time

        cursor.execute('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 10')import os

        recent = cursor.fetchall()from datetime import datetime

        cursor.close()import hashlib

        conn.close()import socket

        return jsonify({{'total_visits': total, 'recent_visits': recent, 'instance_id': INSTANCE_ID}}), 200

    except Exception as e:app = Flask(__name__)

        return jsonify({{'error': str(e), 'instance_id': INSTANCE_ID}}), 500CORS(app)



@app.route('/api/stress', methods=['POST'])# Configuracion de la base de datos PostgreSQL (Azure)

def stress_test():DB_CONFIG = {{

    data = request.get_json() or {{}}    'host': '{db_host}',

    duration = min(int(data.get('duration', 5)), 30)    'port': 5432,

    intensity = min(int(data.get('intensity', 1000000)), 10000000)    'database': 'autoscaling',

    start_time = time.time()    'user': 'autoscaling_user',

    iterations = 0    'password': '{safe_password}'

    while time.time() - start_time < duration:}}

        for i in range(intensity):

            hashlib.sha256(str(i).encode()).hexdigest()def get_db_connection():

        iterations += 1    try:

    elapsed = time.time() - start_time        conn = psycopg2.connect(**DB_CONFIG)

    return jsonify({{'message': 'Stress test completed', 'duration': elapsed, 'iterations': iterations, 'intensity': intensity, 'instance_id': INSTANCE_ID}}), 200        return conn

    except Exception as e:

@app.route('/api/metrics', methods=['GET'])        print(f"Error connecting to database: {{e}}")

def get_metrics():        raise

    import psutil

    return jsonify({{'cpu_percent': psutil.cpu_percent(interval=1), 'memory_percent': psutil.virtual_memory().percent, 'timestamp': datetime.now().isoformat(), 'instance_id': INSTANCE_ID}}), 200def init_db():

    try:

@app.route('/', methods=['GET'])        conn = get_db_connection()

def home():        cursor = conn.cursor()

    return jsonify({{'message': 'Autoscaling Demo API (Azure)', 'version': '2.0.0', 'database': 'PostgreSQL (Azure Flexible Server)', 'instance_id': INSTANCE_ID, 'endpoints': ['/health', '/api/visit', '/api/visits', '/api/stress', '/api/metrics']}}), 200        cursor.execute('''

            CREATE TABLE IF NOT EXISTS visits (

if __name__ == '__main__':                id SERIAL PRIMARY KEY,

    app.run(host='0.0.0.0', port=5000, debug=False)                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

EOFAPP                ip_address VARCHAR(45),

                instance_id VARCHAR(100)

pip3 install flask flask-cors psutil psycopg2-binary            )

nohup python3 app.py > /var/log/flask-app.log 2>&1 &        ''')

        conn.commit()

echo "User-data script completed successfully at $(date)"        cursor.close()

"""        conn.close()

        print("Database initialized successfully")

user_data_output = Output.all(    except Exception as e:

    postgres_server.fully_qualified_domain_name,        print(f"Error initializing database: {{e}}")

    db_password

).apply(create_user_data)# Obtener instance ID (hostname en Azure)

INSTANCE_ID = socket.gethostname()

user_data_base64 = user_data_output.apply(

    lambda ud: base64.b64encode(ud.encode()).decode()# Inicializar BD al arrancar

)init_db()



# VM Scale Set@app.route('/health', methods=['GET'])

vmss = azure.compute.VirtualMachineScaleSet(def health():

    f"{project_name}-vmss",    try:

    resource_group_name=resource_group.name,        conn = get_db_connection()

    location=location,        cursor = conn.cursor()

    vm_scale_set_name=f"{project_name}-vmss",        cursor.execute('SELECT 1')

    sku=azure.compute.SkuArgs(        cursor.close()

        name="Standard_B1s",        conn.close()

        tier="Standard",        return jsonify({{'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'instance_id': INSTANCE_ID, 'database': 'connected'}}), 200

        capacity=1,    except Exception as e:

    ),        return jsonify({{'status': 'unhealthy', 'error': str(e), 'instance_id': INSTANCE_ID}}), 503

    upgrade_policy=azure.compute.UpgradePolicyArgs(mode="Automatic"),

    virtual_machine_profile=azure.compute.VirtualMachineScaleSetVMProfileArgs(@app.route('/api/visit', methods=['POST'])

        os_profile=azure.compute.VirtualMachineScaleSetOSProfileArgs(def register_visit():

            computer_name_prefix=project_name[:10],    try:

            admin_username=admin_username,        ip_address = request.remote_addr

            admin_password=admin_password,        conn = get_db_connection()

            linux_configuration=azure.compute.LinuxConfigurationArgs(        cursor = conn.cursor(cursor_factory=RealDictCursor)

                disable_password_authentication=False,        

            ),        cursor.execute(

            custom_data=user_data_base64,            'INSERT INTO visits (ip_address, instance_id) VALUES (%s, %s)',

        ),            (ip_address, INSTANCE_ID)

        storage_profile=azure.compute.VirtualMachineScaleSetStorageProfileArgs(        )

            image_reference=azure.compute.ImageReferenceArgs(        conn.commit()

                publisher="Canonical",        

                offer="0001-com-ubuntu-server-jammy",        cursor.execute('SELECT COUNT(*) as count FROM visits')

                sku="22_04-lts-gen2",        total = cursor.fetchone()['count']

                version="latest",        

            ),        cursor.close()

            os_disk=azure.compute.VirtualMachineScaleSetOSDiskArgs(        conn.close()

                create_option="FromImage",        

                caching="ReadWrite",        return jsonify({{'message': 'Visit registered', 'total_visits': total, 'ip': ip_address, 'instance_id': INSTANCE_ID}}), 201

                managed_disk=azure.compute.VirtualMachineScaleSetManagedDiskParametersArgs(    except Exception as e:

                    storage_account_type="Standard_LRS",        return jsonify({{'error': str(e), 'instance_id': INSTANCE_ID}}), 500

                ),

            ),@app.route('/api/visits', methods=['GET'])

        ),def get_visits():

        network_profile=azure.compute.VirtualMachineScaleSetNetworkProfileArgs(    try:

            network_interface_configurations=[        conn = get_db_connection()

                azure.compute.VirtualMachineScaleSetNetworkConfigurationArgs(        cursor = conn.cursor(cursor_factory=RealDictCursor)

                    name=f"{project_name}-nic-config",        

                    primary=True,        cursor.execute('SELECT COUNT(*) as count FROM visits')

                    ip_configurations=[        total = cursor.fetchone()['count']

                        azure.compute.VirtualMachineScaleSetIPConfigurationArgs(        

                            name=f"{project_name}-ip-config",        cursor.execute('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 10')

                            subnet=azure.compute.ApiEntityReferenceArgs(id=vm_subnet.id),        recent = cursor.fetchall()

                            load_balancer_backend_address_pools=[        

                                azure.compute.SubResourceArgs(id=backend_pool.id)        cursor.close()

                            ],        conn.close()

                        )        

                    ],        return jsonify({{'total_visits': total, 'recent_visits': recent, 'instance_id': INSTANCE_ID}}), 200

                    network_security_group=azure.compute.SubResourceArgs(id=nsg.id),    except Exception as e:

                )        return jsonify({{'error': str(e), 'instance_id': INSTANCE_ID}}), 500

            ],

        ),@app.route('/api/stress', methods=['POST'])

    ),def stress_test():

)    data = request.get_json() or {{}}

    duration = min(int(data.get('duration', 5)), 30)

# Autoscale Settings    intensity = min(int(data.get('intensity', 1000000)), 10000000)

autoscale_setting = azure.insights.AutoscaleSetting(    

    f"{project_name}-autoscale",    start_time = time.time()

    resource_group_name=resource_group.name,    iterations = 0

    location=location,    

    autoscale_setting_name=f"{project_name}-autoscale",    while time.time() - start_time < duration:

    target_resource_uri=vmss.id,        for i in range(intensity):

    enabled=True,            hashlib.sha256(str(i).encode()).hexdigest()

    profiles=[        iterations += 1

        azure.insights.AutoscaleProfileArgs(    

            name="Default-Profile",    elapsed = time.time() - start_time

            capacity=azure.insights.ScaleCapacityArgs(    return jsonify({{'message': 'Stress test completed', 'duration': elapsed, 'iterations': iterations, 'intensity': intensity, 'instance_id': INSTANCE_ID}}), 200

                minimum="1",

                maximum="3",@app.route('/api/metrics', methods=['GET'])

                default="1",def get_metrics():

            ),    import psutil

            rules=[    return jsonify({{

                azure.insights.ScaleRuleArgs(        'cpu_percent': psutil.cpu_percent(interval=1),

                    metric_trigger=azure.insights.MetricTriggerArgs(        'memory_percent': psutil.virtual_memory().percent,

                        metric_name="Percentage CPU",        'timestamp': datetime.now().isoformat(),

                        metric_resource_uri=vmss.id,        'instance_id': INSTANCE_ID

                        time_grain="PT1M",    }}), 200

                        statistic="Average",

                        time_window="PT5M",@app.route('/', methods=['GET'])

                        time_aggregation="Average",def home():

                        operator="GreaterThan",    return jsonify({{

                        threshold=70,        'message': 'Autoscaling Demo API (Azure)',

                    ),        'version': '2.0.0',

                    scale_action=azure.insights.ScaleActionArgs(        'database': 'PostgreSQL (Azure Flexible Server)',

                        direction="Increase",        'instance_id': INSTANCE_ID,

                        type="ChangeCount",        'endpoints': ['/health', '/api/visit', '/api/visits', '/api/stress', '/api/metrics']

                        value="1",    }}), 200

                        cooldown="PT5M",

                    ),if __name__ == '__main__':

                ),    app.run(host='0.0.0.0', port=5000, debug=False)

                azure.insights.ScaleRuleArgs(EOFAPP

                    metric_trigger=azure.insights.MetricTriggerArgs(

                        metric_name="Percentage CPU",# Instalar dependencias de Python

                        metric_resource_uri=vmss.id,pip3 install flask flask-cors psutil psycopg2-binary

                        time_grain="PT1M",

                        statistic="Average",# Ejecutar la aplicación en background

                        time_window="PT5M",nohup python3 app.py > /var/log/flask-app.log 2>&1 &

                        time_aggregation="Average",

                        operator="LessThan",echo "User-data script completed successfully at $(date)"

                        threshold=30,"""

                    ),

                    scale_action=azure.insights.ScaleActionArgs(# Combinar hostname del postgres y password

                        direction="Decrease",user_data_output = Output.all(

                        type="ChangeCount",    postgres_server.fully_qualified_domain_name,

                        value="1",    db_password

                        cooldown="PT5M",).apply(create_user_data)

                    ),

                ),# Codificar en base64

            ],user_data_base64 = user_data_output.apply(

        )    lambda ud: base64.b64encode(ud.encode()).decode()

    ],)

)

# ====================

# Outputs# VM SCALE SET

export("resource_group_name", resource_group.name)# ====================

export("load_balancer_ip", public_ip.ip_address)

export("load_balancer_url", Output.concat("http://", public_ip.ip_address))vmss = azure.compute.VirtualMachineScaleSet(

export("postgres_server", postgres_server.fully_qualified_domain_name)    f"{project_name}-vmss",

export("vmss_name", vmss.name)    resource_group_name=resource_group.name,

export("location", location)    location=location,

    vm_scale_set_name=f"{project_name}-vmss",
    sku=azure.compute.SkuArgs(
        name="Standard_B1s",  # Instancia pequeña (similar a t3.micro)
        tier="Standard",
        capacity=1,  # Inicialmente 1 instancia
    ),
    upgrade_policy=azure.compute.UpgradePolicyArgs(
        mode="Automatic",
    ),
    virtual_machine_profile=azure.compute.VirtualMachineScaleSetVMProfileArgs(
        os_profile=azure.compute.VirtualMachineScaleSetOSProfileArgs(
            computer_name_prefix=project_name[:10],
            admin_username=admin_username,
            admin_password=admin_password,
            linux_configuration=azure.compute.LinuxConfigurationArgs(
                disable_password_authentication=False,
            ),
            custom_data=user_data_base64,
        ),
        storage_profile=azure.compute.VirtualMachineScaleSetStorageProfileArgs(
            image_reference=azure.compute.ImageReferenceArgs(
                publisher="Canonical",
                offer="0001-com-ubuntu-server-jammy",
                sku="22_04-lts-gen2",
                version="latest",
            ),
            os_disk=azure.compute.VirtualMachineScaleSetOSDiskArgs(
                create_option="FromImage",
                caching="ReadWrite",
                managed_disk=azure.compute.VirtualMachineScaleSetManagedDiskParametersArgs(
                    storage_account_type="Standard_LRS",
                ),
            ),
        ),
        network_profile=azure.compute.VirtualMachineScaleSetNetworkProfileArgs(
            network_interface_configurations=[
                azure.compute.VirtualMachineScaleSetNetworkConfigurationArgs(
                    name=f"{project_name}-nic-config",
                    primary=True,
                    ip_configurations=[
                        azure.compute.VirtualMachineScaleSetIPConfigurationArgs(
                            name=f"{project_name}-ip-config",
                            subnet=azure.compute.ApiEntityReferenceArgs(
                                id=vm_subnet.id,
                            ),
                            load_balancer_backend_address_pools=[
                                azure.compute.SubResourceArgs(
                                    id=backend_pool.id,
                                )
            ],
                        )
                    ],
                    network_security_group=azure.compute.SubResourceArgs(
                        id=nsg.id,
                    ),
                )
            ],
        ),
    ),
)

# ====================
# AUTOSCALE SETTINGS
# ====================

autoscale_setting = azure.insights.AutoscaleSetting(
    f"{project_name}-autoscale",
    resource_group_name=resource_group.name,
    location=location,
    autoscale_setting_name=f"{project_name}-autoscale",
    target_resource_uri=vmss.id,
    enabled=True,
    profiles=[
        azure.insights.AutoscaleProfileArgs(
            name="Default-Profile",
            capacity=azure.insights.ScaleCapacityArgs(
                minimum="1",
                maximum="3",
                default="1",
            ),
            rules=[
                # Scale UP: CPU > 70%
                azure.insights.ScaleRuleArgs(
                    metric_trigger=azure.insights.MetricTriggerArgs(
                        metric_name="Percentage CPU",
                        metric_resource_uri=vmss.id,
                        time_grain="PT1M",
                        statistic="Average",
                        time_window="PT5M",
                        time_aggregation="Average",
                        operator="GreaterThan",
                        threshold=70,
                    ),
                    scale_action=azure.insights.ScaleActionArgs(
                        direction="Increase",
                        type="ChangeCount",
                        value="1",
                        cooldown="PT5M",
                    ),
                ),
                # Scale DOWN: CPU < 30%
                azure.insights.ScaleRuleArgs(
                    metric_trigger=azure.insights.MetricTriggerArgs(
                        metric_name="Percentage CPU",
                        metric_resource_uri=vmss.id,
                        time_grain="PT1M",
                        statistic="Average",
                        time_window="PT5M",
                        time_aggregation="Average",
                        operator="LessThan",
                        threshold=30,
                    ),
                    scale_action=azure.insights.ScaleActionArgs(
                        direction="Decrease",
                        type="ChangeCount",
                        value="1",
                        cooldown="PT5M",
                    ),
                ),
            ],
        )
    ],
)

# ====================
# OUTPUTS
# ====================

export("resource_group_name", resource_group.name)
export("load_balancer_ip", public_ip.ip_address)
export("load_balancer_url", Output.concat("http://", public_ip.ip_address))
export("postgres_server", postgres_server.fully_qualified_domain_name)
export("vmss_name", vmss.name)
export("location", location)

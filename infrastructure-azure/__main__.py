import pulumi
import pulumi_azure_native as azure
from pulumi import Config, export, Output
import base64

config = Config()
project_name = "cpe-autoscaling-demo"
location = config.get("location") or "eastus"
admin_username = "azureuser"
admin_password = config.require_secret("admin_password")
db_password = config.require_secret("db_password")

resource_group = azure.resources.ResourceGroup(
    f"{project_name}-rg",
    location=location,
    resource_group_name=f"{project_name}-rg",
)

vnet = azure.network.VirtualNetwork(
    f"{project_name}-vnet",
    resource_group_name=resource_group.name,
    location=location,
    address_space=azure.network.AddressSpaceArgs(address_prefixes=["10.0.0.0/16"]),
    virtual_network_name=f"{project_name}-vnet",
)

vm_subnet = azure.network.Subnet(
    f"{project_name}-vm-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24",
    subnet_name=f"{project_name}-vm-subnet",
)

db_subnet = azure.network.Subnet(
    f"{project_name}-db-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.2.0/24",
    subnet_name=f"{project_name}-db-subnet",
    delegations=[
        azure.network.DelegationArgs(
            name="postgres-delegation",
            service_name="Microsoft.DBforPostgreSQL/flexibleServers",
        )
    ],
)

public_ip = azure.network.PublicIPAddress(
    f"{project_name}-pip",
    resource_group_name=resource_group.name,
    location=location,
    public_ip_allocation_method="Static",
    sku=azure.network.PublicIPAddressSkuArgs(name="Standard"),
    public_ip_address_name=f"{project_name}-pip",
)

load_balancer = azure.network.LoadBalancer(
    f"{project_name}-lb",
    resource_group_name=resource_group.name,
    location=location,
    sku=azure.network.LoadBalancerSkuArgs(name="Standard"),
    frontend_ip_configurations=[
        azure.network.FrontendIPConfigurationArgs(
            name="LoadBalancerFrontend",
            public_ip_address=azure.network.PublicIPAddressArgs(id=public_ip.id),
        )
    ],
    load_balancer_name=f"{project_name}-lb",
)

backend_pool = azure.network.LoadBalancerBackendAddressPool(
    f"{project_name}-backend-pool",
    resource_group_name=resource_group.name,
    load_balancer_name=load_balancer.name,
    backend_address_pool_name=f"{project_name}-backend-pool",
)

health_probe = azure.network.LoadBalancerProbe(
    f"{project_name}-health-probe",
    resource_group_name=resource_group.name,
    load_balancer_name=load_balancer.name,
    protocol="Http",
    port=5000,
    request_path="/health",
    interval_in_seconds=30,
    number_of_probes=2,
    probe_name=f"{project_name}-health-probe",
)

lb_rule = azure.network.LoadBalancingRule(
    f"{project_name}-lb-rule",
    resource_group_name=resource_group.name,
    load_balancer_name=load_balancer.name,
    protocol="Tcp",
    frontend_port=80,
    backend_port=5000,
    frontend_ip_configuration=azure.network.SubResourceArgs(
        id=load_balancer.frontend_ip_configurations.apply(lambda configs: configs[0].id),
    ),
    backend_address_pool=azure.network.SubResourceArgs(id=backend_pool.id),
    probe=azure.network.SubResourceArgs(id=health_probe.id),
    enable_floating_ip=False,
    idle_timeout_in_minutes=4,
    load_balancing_rule_name=f"{project_name}-lb-rule",
)

nsg = azure.network.NetworkSecurityGroup(
    f"{project_name}-nsg",
    resource_group_name=resource_group.name,
    location=location,
    security_rules=[
        azure.network.SecurityRuleArgs(
            name="Allow-HTTP",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="80",
            source_address_prefix="Internet",
            destination_address_prefix="*",
            access="Allow",
            priority=100,
            direction="Inbound",
        ),
        azure.network.SecurityRuleArgs(
            name="Allow-Flask",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="5000",
            source_address_prefix="AzureLoadBalancer",
            destination_address_prefix="*",
            access="Allow",
            priority=110,
            direction="Inbound",
        ),
        azure.network.SecurityRuleArgs(
            name="Allow-SSH",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="22",
            source_address_prefix="179.7.180.162/32",
            destination_address_prefix="*",
            access="Allow",
            priority=120,
            direction="Inbound",
        ),
    ],
    network_security_group_name=f"{project_name}-nsg",
)

postgres_dns_zone = azure.network.PrivateZone(
    f"{project_name}-postgres-dns",
    resource_group_name=resource_group.name,
    location="Global",
    private_zone_name=f"{project_name}.postgres.database.azure.com",
)

dns_vnet_link = azure.network.VirtualNetworkLink(
    f"{project_name}-dns-vnet-link",
    resource_group_name=resource_group.name,
    private_zone_name=postgres_dns_zone.name,
    location="Global",
    virtual_network=azure.network.SubResourceArgs(id=vnet.id),
    registration_enabled=False,
    virtual_network_link_name=f"{project_name}-dns-vnet-link",
)

postgres_server = azure.dbforpostgresql.Server(
    f"{project_name}-postgres",
    resource_group_name=resource_group.name,
    location=location,
    server_name=f"{project_name}-postgres",
    administrator_login="autoscaling_user",
    administrator_login_password=db_password,
    version="15",
    sku=azure.dbforpostgresql.SkuArgs(name="Standard_B1ms", tier="Burstable"),
    storage=azure.dbforpostgresql.StorageArgs(storage_size_gb=32),
    network=azure.dbforpostgresql.NetworkArgs(
        delegated_subnet_resource_id=db_subnet.id,
        private_dns_zone_arm_resource_id=postgres_dns_zone.id,
    ),
    high_availability=azure.dbforpostgresql.HighAvailabilityArgs(mode="Disabled"),
    backup=azure.dbforpostgresql.BackupArgs(backup_retention_days=7, geo_redundant_backup="Disabled"),
)

postgres_database = azure.dbforpostgresql.Database(
    f"{project_name}-db",
    resource_group_name=resource_group.name,
    server_name=postgres_server.name,
    database_name="autoscaling",
    charset="UTF8",
    collation="en_US.utf8",
)

def create_user_data(db_info):
    db_host = db_info[0]
    db_pass = db_info[1]
    
    user_data_script = f"""#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting user-data script at $(date)"

# Actualizar sistema
apt-get update -y
apt-get upgrade -y

# Instalar dependencias
apt-get install -y git python3 python3-pip python3-venv

# Clonar repositorio
cd /home/{admin_username}
git clone https://github.com/ChristianPE1/Registro-Visitas-WebApp.git app
cd app/backend

# Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variables de entorno
cat > .env << 'EOFENV'
DB_HOST={db_host}
DB_PORT=5432
DB_NAME=autoscaling
DB_USER=autoscaling_user
DB_PASSWORD={db_pass}
FLASK_ENV=production
EOFENV

# Modificar app.py para usar variables de entorno
cat > app_config.py << 'EOFCONFIG'
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {{
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}}
EOFCONFIG

# Instalar python-dotenv
pip install python-dotenv

# Ejecutar aplicación
nohup python3 app.py > /var/log/flask-app.log 2>&1 &

echo "User-data script completed successfully at $(date)"
"""
    return user_data_script

user_data_output = Output.all(postgres_server.fully_qualified_domain_name, db_password).apply(create_user_data)
user_data_base64 = user_data_output.apply(lambda ud: base64.b64encode(ud.encode()).decode())

vmss = azure.compute.VirtualMachineScaleSet(
    f"{project_name}-vmss",
    resource_group_name=resource_group.name,
    location=location,
    vm_scale_set_name=f"{project_name}-vmss",
    sku=azure.compute.SkuArgs(name="Standard_B1s", tier="Standard", capacity=1),
    upgrade_policy=azure.compute.UpgradePolicyArgs(mode="Automatic"),
    virtual_machine_profile=azure.compute.VirtualMachineScaleSetVMProfileArgs(
        os_profile=azure.compute.VirtualMachineScaleSetOSProfileArgs(
            computer_name_prefix=project_name[:10],
            admin_username=admin_username,
            admin_password=admin_password,
            linux_configuration=azure.compute.LinuxConfigurationArgs(disable_password_authentication=False),
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
                managed_disk=azure.compute.VirtualMachineScaleSetManagedDiskParametersArgs(storage_account_type="Standard_LRS"),
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
                            subnet=azure.compute.ApiEntityReferenceArgs(id=vm_subnet.id),
                            load_balancer_backend_address_pools=[azure.compute.SubResourceArgs(id=backend_pool.id)],
                        )
                    ],
                    network_security_group=azure.compute.SubResourceArgs(id=nsg.id),
                )
            ],
        ),
    ),
)

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
            capacity=azure.insights.ScaleCapacityArgs(minimum="1", maximum="3", default="1"),
            rules=[
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

export("resource_group_name", resource_group.name)
export("load_balancer_ip", public_ip.ip_address)
export("load_balancer_url", Output.concat("http://", public_ip.ip_address))
export("postgres_server", postgres_server.fully_qualified_domain_name)
export("vmss_name", vmss.name)
export("location", location)

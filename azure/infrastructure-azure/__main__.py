import pulumi
import pulumi_azure_native as azure
from pulumi_azure_native import network
from pulumi import Config, export, Output
import base64

config = Config()
project_name = "cpe-autoscaling-demo"
location = config.get("location") or "westus"  # PostgreSQL disponible en West US
admin_username = "azureuser"
admin_password = config.require_secret("admin_password")
db_password = config.require_secret("db_password")
subscription_id = "1eb83675-114b-4f93-8921-f055b5bd6ea8"

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

# Public IP para NAT Gateway
nat_gateway_ip = azure.network.PublicIPAddress(
    f"{project_name}-nat-pip",
    resource_group_name=resource_group.name,
    location=location,
    public_ip_allocation_method="Static",
    sku=azure.network.PublicIPAddressSkuArgs(name="Standard"),
    public_ip_address_name=f"{project_name}-nat-pip",
)

# NAT Gateway para conectividad saliente
nat_gateway = azure.network.NatGateway(
    f"{project_name}-nat-gateway",
    resource_group_name=resource_group.name,
    location=location,
    nat_gateway_name=f"{project_name}-nat-gateway",
    sku=azure.network.NatGatewaySkuArgs(name="Standard"),
    public_ip_addresses=[azure.network.SubResourceArgs(id=nat_gateway_ip.id)],
    idle_timeout_in_minutes=10,
)

# NSG con todas las reglas (incluyendo monitoreo)
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
            source_address_prefix="*",
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
            source_address_prefix="*",
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
        azure.network.SecurityRuleArgs(
            name="Allow-Grafana",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="3000",
            source_address_prefix="179.7.180.162/32",
            destination_address_prefix="*",
            access="Allow",
            priority=130,
            direction="Inbound",
        ),
        azure.network.SecurityRuleArgs(
            name="Allow-Prometheus",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="9090",
            source_address_prefix="179.7.180.162/32",
            destination_address_prefix="*",
            access="Allow",
            priority=140,
            direction="Inbound",
        ),
    ],
    network_security_group_name=f"{project_name}-nsg",
)

vm_subnet = azure.network.Subnet(
    f"{project_name}-vm-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24",
    subnet_name=f"{project_name}-vm-subnet",
    nat_gateway=azure.network.SubResourceArgs(id=nat_gateway.id),
    network_security_group=azure.network.NetworkSecurityGroupArgs(id=nsg.id),
)

db_subnet = azure.network.Subnet(
    f"{project_name}-db-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.2.0/24",
    subnet_name=f"{project_name}-db-subnet",
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
    backend_address_pools=[
        azure.network.BackendAddressPoolArgs(
            name=f"{project_name}-backend-pool",
        )
    ],
    probes=[
        azure.network.ProbeArgs(
            name=f"{project_name}-health-probe",
            protocol="Http",
            port=5000,
            request_path="/health",
            interval_in_seconds=15,
            number_of_probes=2,
        ),
        azure.network.ProbeArgs(
            name=f"{project_name}-grafana-probe",
            protocol="Http",
            port=3000,
            request_path="/api/health",
            interval_in_seconds=15,
            number_of_probes=2,
        ),
        azure.network.ProbeArgs(
            name=f"{project_name}-prometheus-probe",
            protocol="Http",
            port=9090,
            request_path="/-/healthy",
            interval_in_seconds=15,
            number_of_probes=2,
        ),
    ],
    inbound_nat_pools=[
        azure.network.InboundNatPoolArgs(
            name=f"{project_name}-ssh-nat-pool",
            frontend_ip_configuration=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/frontendIPConfigurations/LoadBalancerFrontend"
                )
            ),
            protocol="Tcp",
            frontend_port_range_start=50000,
            frontend_port_range_end=50099,
            backend_port=22,
        )
    ],
    load_balancing_rules=[
        azure.network.LoadBalancingRuleArgs(
            name=f"{project_name}-lb-rule",
            frontend_ip_configuration=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/frontendIPConfigurations/LoadBalancerFrontend"
                )
            ),
            backend_address_pool=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/backendAddressPools/", f"{project_name}-backend-pool"
                )
            ),
            probe=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/probes/", f"{project_name}-health-probe"
                )
            ),
            protocol="Tcp",
            frontend_port=80,
            backend_port=5000,
            enable_floating_ip=False,
            idle_timeout_in_minutes=4,
        ),
        azure.network.LoadBalancingRuleArgs(
            name=f"{project_name}-grafana-rule",
            frontend_ip_configuration=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/frontendIPConfigurations/LoadBalancerFrontend"
                )
            ),
            backend_address_pool=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/backendAddressPools/", f"{project_name}-backend-pool"
                )
            ),
            probe=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/probes/", f"{project_name}-grafana-probe"
                )
            ),
            protocol="Tcp",
            frontend_port=3000,
            backend_port=3000,
            enable_floating_ip=False,
            idle_timeout_in_minutes=4,
        ),
        azure.network.LoadBalancingRuleArgs(
            name=f"{project_name}-prometheus-rule",
            frontend_ip_configuration=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/frontendIPConfigurations/LoadBalancerFrontend"
                )
            ),
            backend_address_pool=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/backendAddressPools/", f"{project_name}-backend-pool"
                )
            ),
            probe=azure.network.SubResourceArgs(
                id=Output.concat(
                    "/subscriptions/", subscription_id,
                    "/resourceGroups/", resource_group.name,
                    "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                    "/probes/", f"{project_name}-prometheus-probe"
                )
            ),
            protocol="Tcp",
            frontend_port=9090,
            backend_port=9090,
            enable_floating_ip=False,
            idle_timeout_in_minutes=4,
        ),
    ],
    load_balancer_name=f"{project_name}-lb",
)

# PostgreSQL Flexible Server (B1ms - Burstable, 1 vCore, 2 GiB RAM, 32 GiB storage)
postgres_server = azure.dbforpostgresql.Server(
    f"{project_name}-postgres",
    resource_group_name=resource_group.name,
    location=location,
    server_name=f"{project_name}-postgres",
    administrator_login="autoscaling_user",
    administrator_login_password=db_password,
    version=azure.dbforpostgresql.ServerVersion.SERVER_VERSION_13,
    sku=azure.dbforpostgresql.SkuArgs(
        name="Standard_B1ms",
        tier=azure.dbforpostgresql.SkuTier.BURSTABLE
    ),
    storage=azure.dbforpostgresql.StorageArgs(
        storage_size_gb=32
    ),
    backup=azure.dbforpostgresql.BackupArgs(
        backup_retention_days=7,
        geo_redundant_backup=azure.dbforpostgresql.GeoRedundantBackupEnum.DISABLED
    ),
    high_availability=azure.dbforpostgresql.HighAvailabilityArgs(
        mode=azure.dbforpostgresql.HighAvailabilityMode.DISABLED
    ),
    create_mode=azure.dbforpostgresql.CreateMode.CREATE,
)

# Firewall rule para permitir servicios de Azure
postgres_firewall = azure.dbforpostgresql.FirewallRule(
    f"{project_name}-postgres-fw",
    resource_group_name=resource_group.name,
    server_name=postgres_server.name,
    firewall_rule_name="AllowAzureServices",
    start_ip_address="0.0.0.0",
    end_ip_address="0.0.0.0",
)


def create_user_data(db_info):
    db_host = db_info[0]
    db_pass = db_info[1]
    
    user_data_script = f"""#!/bin/bash
set -ex
exec > >(tee -a /var/log/user-data.log)
exec 2>&1

echo "=========================================="
echo "Starting user-data script at $(date)"
echo "=========================================="

# Actualizar sistema
echo "[$(date)] Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"

# Instalar dependencias
echo "[$(date)] Installing dependencies..."
apt-get install -y git python3 python3-pip python3-venv stress-ng postgresql-client

# Clonar repositorio
echo "[$(date)] Cloning repository..."
cd /home/{admin_username}
rm -rf app || true
git clone https://github.com/ChristianPE1/Registro-Visitas-WebApp.git app
chown -R {admin_username}:{admin_username} app

# Configurar Backend
echo "[$(date)] Setting up Flask backend..."
cd /home/{admin_username}/app/backend
sudo -u {admin_username} python3 -m venv venv
sudo -u {admin_username} bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Configurar variables de entorno para PostgreSQL
cat > .env << 'EOFENV'
DB_HOST={db_host}
DB_PORT=5432
DB_NAME=postgres
DB_USER=autoscaling_user
DB_PASSWORD={db_pass}
FLASK_ENV=production
EOFENV

# Crear base de datos si no existe
echo "[$(date)] Creating database if not exists..."
PGPASSWORD='{db_pass}' psql -h {db_host} -U autoscaling_user -d postgres -c "SELECT 1" 2>&1 || echo "Database connection test completed"

# Crear systemd service para Flask
echo "[$(date)] Creating Flask systemd service..."
cat > /tmp/flask-app.service << 'EOFSVC'
[Unit]
Description=Flask Autoscaling Demo App
After=network.target

[Service]
Type=simple
User={admin_username}
WorkingDirectory=/home/{admin_username}/app/backend
Environment="PATH=/home/{admin_username}/app/backend/venv/bin"
EnvironmentFile=/home/{admin_username}/app/backend/.env
ExecStart=/home/{admin_username}/app/backend/venv/bin/python3 /home/{admin_username}/app/backend/app.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/flask-app.log
StandardError=append:/var/log/flask-app-error.log

[Install]
WantedBy=multi-user.target
EOFSVC

sudo mv /tmp/flask-app.service /etc/systemd/system/flask-app.service

# Habilitar e iniciar Flask service
echo "[$(date)] Starting Flask service..."
sudo systemctl daemon-reload
sudo systemctl enable flask-app.service
sudo systemctl start flask-app.service

# Esperar a que Flask esté listo
echo "[$(date)] Waiting for Flask to be ready..."
for i in {{1..30}}; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "[$(date)] Flask is UP!"
        break
    fi
    echo "[$(date)] Attempt $i: Flask not ready yet..."
    sleep 2
done

# Verificar estado final
echo "[$(date)] Flask service status:"
sudo systemctl status flask-app.service --no-pager || true

echo "[$(date)] Flask process:"
ps aux | grep -E 'python.*app.py' | grep -v grep || echo "No Flask process found!"

echo "[$(date)] Testing local endpoint:"
curl -v http://localhost:5000/health || echo "Health check failed"

echo "[$(date)] User-data script completed successfully at $(date)"
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
    upgrade_policy=azure.compute.UpgradePolicyArgs(mode="Manual"),
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
        diagnostics_profile=azure.compute.DiagnosticsProfileArgs(
            boot_diagnostics=azure.compute.BootDiagnosticsArgs(enabled=True)
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
                            load_balancer_backend_address_pools=[
                                azure.compute.SubResourceArgs(
                                    id=Output.concat(
                                        "/subscriptions/", subscription_id,
                                        "/resourceGroups/", resource_group.name,
                                        "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                                        "/backendAddressPools/", f"{project_name}-backend-pool"
                                    )
                                )
                            ],
                            load_balancer_inbound_nat_pools=[
                                azure.compute.SubResourceArgs(
                                    id=Output.concat(
                                        "/subscriptions/", subscription_id,
                                        "/resourceGroups/", resource_group.name,
                                        "/providers/Microsoft.Network/loadBalancers/", f"{project_name}-lb",
                                        "/inboundNatPools/", f"{project_name}-ssh-nat-pool"
                                    )
                                )
                            ],
                        )
                    ],
                )
            ],
        ),
    ),
    opts=pulumi.ResourceOptions(
        depends_on=[load_balancer, vm_subnet, nat_gateway, postgres_firewall]
    ),
)

autoscale_setting = azure.monitor.AutoscaleSetting(
    f"{project_name}-autoscale",
    resource_group_name=resource_group.name,
    location=location,
    autoscale_setting_name=f"{project_name}-autoscale",
    target_resource_uri=vmss.id,
    enabled=True,
    profiles=[
        azure.monitor.AutoscaleProfileArgs(
            name="Default-Profile",
            capacity=azure.monitor.ScaleCapacityArgs(minimum="1", maximum="5", default="1"),
            rules=[
                azure.monitor.ScaleRuleArgs(
                    metric_trigger=azure.monitor.MetricTriggerArgs(
                        metric_name="Percentage CPU",
                        metric_resource_uri=vmss.id,
                        time_grain="PT1M",
                        statistic="Average",
                        time_window="PT2M",
                        time_aggregation="Average",
                        operator="GreaterThan",
                        threshold=70,
                    ),
                    scale_action=azure.monitor.ScaleActionArgs(
                        direction="Increase",
                        type="ChangeCount",
                        value="1",
                        cooldown="PT2M",
                    ),
                ),
                azure.monitor.ScaleRuleArgs(
                    metric_trigger=azure.monitor.MetricTriggerArgs(
                        metric_name="Percentage CPU",
                        metric_resource_uri=vmss.id,
                        time_grain="PT1M",
                        statistic="Average",
                        time_window="PT2M",
                        time_aggregation="Average",
                        operator="LessThan",
                        threshold=30,
                    ),
                    scale_action=azure.monitor.ScaleActionArgs(
                        direction="Decrease",
                        type="ChangeCount",
                        value="1",
                        cooldown="PT2M",
                    ),
                ),
            ],
        )
    ],
)

export("resource_group_name", resource_group.name)
export("load_balancer_ip", public_ip.ip_address)
export("load_balancer_url", public_ip.ip_address.apply(lambda ip: f"http://{ip}" if ip else "Pending..."))
export("postgres_server", postgres_server.fully_qualified_domain_name)
export("vmss_name", vmss.name)
export("location", location)
export("ssh_command", public_ip.ip_address.apply(lambda ip: f"ssh -p 5000X {admin_username}@{ip}  (X=instance ID, ej: 50001 para instancia 1)" if ip else "Pending..."))
export("health_endpoint", public_ip.ip_address.apply(lambda ip: f"http://{ip}/health" if ip else "Pending..."))
export("grafana_url", public_ip.ip_address.apply(lambda ip: f"http://{ip}:3000 (admin/admin)" if ip else "Pending..."))
export("prometheus_url", public_ip.ip_address.apply(lambda ip: f"http://{ip}:9090" if ip else "Pending..."))

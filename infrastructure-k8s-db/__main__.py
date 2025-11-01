"""
Pila 2: Base de Datos PostgreSQL - Micro-Stack Independiente
Implementa: Micro-Stack Pattern (Cap 5)
- Ciclos de vida separados: DB independiente del cluster
- Radio de explosión limitado
- Datos persistentes separados de la infraestructura efímera
"""

import pulumi
import pulumi_azure_native as azure
from pulumi import Config, export, Output, StackReference

config = Config()
project_name = "cpe-k8s-autoscaling"
location = config.get("location") or "westus"  # westus - disponibilidad de PostgreSQL Flexible Server
db_admin_user = "postgres_admin"
db_admin_password = config.require_secret("db_admin_password")
db_name = "autoscaling_db"

# StackReference - Obtener outputs de la pila base
# Principio: "Piezas pequeñas y débilmente acopladas" (Cap 1)
base_stack = StackReference("organization/k8s-base/production")
resource_group_name = base_stack.get_output("resource_group_name")
vnet_name = base_stack.get_output("vnet_name")
aks_subnet_id = base_stack.get_output("aks_subnet_id")

# Obtener el resource group existente
resource_group = azure.resources.get_resource_group(
    resource_group_name=resource_group_name
)

# Subnet dedicada para PostgreSQL (Private Link)
db_subnet = azure.network.Subnet(
    f"{project_name}-db-subnet",
    resource_group_name=resource_group_name,
    virtual_network_name=vnet_name,
    subnet_name=f"{project_name}-db-subnet",
    address_prefix="10.0.2.0/24",
    delegations=[
        azure.network.DelegationArgs(
            name="PostgreSQLFlexibleServerDelegation",
            service_name="Microsoft.DBforPostgreSQL/flexibleServers"
        )
    ]
)

# Azure Database for PostgreSQL Flexible Server
# Tier: Burstable (bajo costo) con 1 vCore y 2 GiB RAM
# Principio: "Minimizar variación" + "Hacer reproducible"
postgres_server = azure.dbforpostgresql.Server(
    f"{project_name}-postgres",
    resource_group_name=resource_group_name,
    location=location,
    server_name=f"{project_name}-postgres",
    
    # Credenciales de admin
    administrator_login=db_admin_user,
    administrator_login_password=db_admin_password,
    
    # Versión de PostgreSQL
    version=azure.dbforpostgresql.ServerVersion.SERVER_VERSION_14,
    
    # SKU - Burstable tier para minimizar costos
    sku=azure.dbforpostgresql.SkuArgs(
        name="Standard_B1ms",  # 1 vCore, 2 GiB RAM
        tier=azure.dbforpostgresql.SkuTier.BURSTABLE
    ),
    
    # Storage - 32 GiB (mínimo)
    storage=azure.dbforpostgresql.StorageArgs(
        storage_size_gb=32,
        auto_grow=azure.dbforpostgresql.StorageAutoGrow.ENABLED  # Auto-crecimiento habilitado
    ),
    
    # Backup - 7 días de retención
    backup=azure.dbforpostgresql.BackupArgs(
        backup_retention_days=7,
        geo_redundant_backup=azure.dbforpostgresql.GeoRedundantBackupEnum.DISABLED  # Reducir costos
    ),
    
    # Alta disponibilidad deshabilitada (reducir costos)
    high_availability=azure.dbforpostgresql.HighAvailabilityArgs(
        mode=azure.dbforpostgresql.HighAvailabilityMode.DISABLED
    ),
    
    # Red - Delegated subnet
    network=azure.dbforpostgresql.NetworkArgs(
        delegated_subnet_resource_id=db_subnet.id
    ),
    
    # Modo de creación
    create_mode=azure.dbforpostgresql.CreateMode.CREATE,
    
    tags={
        "component": "database",
        "iac-pattern": "micro-stack-db",
        "lifecycle": "persistent-data"
    }
)

# Base de datos dentro del servidor
database = azure.dbforpostgresql.Database(
    f"{project_name}-db",
    resource_group_name=resource_group_name,
    server_name=postgres_server.name,
    database_name=db_name,
    charset="UTF8",
    collation="en_US.utf8",
    opts=pulumi.ResourceOptions(depends_on=[postgres_server])
)

# Firewall rule para permitir servicios de Azure
# Esto permite que AKS se conecte a la DB
postgres_firewall_azure = azure.dbforpostgresql.FirewallRule(
    f"{project_name}-postgres-fw-azure",
    resource_group_name=resource_group_name,
    server_name=postgres_server.name,
    firewall_rule_name="AllowAzureServices",
    start_ip_address="0.0.0.0",
    end_ip_address="0.0.0.0",
    opts=pulumi.ResourceOptions(depends_on=[postgres_server])
)

# Connection string para aplicaciones
# Formato: postgresql://user:password@host:5432/database
connection_string = Output.all(
    postgres_server.fully_qualified_domain_name,
    db_admin_password,
    db_name
).apply(lambda args: f"postgresql://{db_admin_user}:{args[1]}@{args[0]}:5432/{args[2]}")

# Exports - Para usar en la pila de despliegue
export("postgres_server_name", postgres_server.name)
export("postgres_fqdn", postgres_server.fully_qualified_domain_name)
export("postgres_admin_user", db_admin_user)
export("database_name", db_name)
export("connection_string", connection_string)  # Secreto - Pulumi lo marca automáticamente

# Información útil
export("db_subnet_id", db_subnet.id)
export("postgres_version", "14")
export("postgres_sku", "Standard_B1ms (1 vCore, 2 GiB RAM)")
export("storage_size_gb", "32")

# Verificación
export("db_status", Output.concat(
    "PostgreSQL Flexible Server desplegado: ",
    postgres_server.fully_qualified_domain_name,
    " | Database: ", db_name,
    " | Micro-Stack independiente del cluster AKS"
))

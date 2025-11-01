"""
Pila 2: Base de Datos PostgreSQL - Micro-Stack Independiente
Implementa: Micro-Stack Pattern (Cap 5)
- Ciclos de vida separados: DB independiente del cluster
- Radio de explosión limitado
- Datos persistentes separados de la infraestructura efímera
"""

import pulumi
import pulumi_gcp as gcp
from pulumi import Config, export, Output, StackReference
import random
import string

config = Config()
project_name = "cpe-autoscaling"
project_id = "cpe-autoscaling-k8s"
region = config.get("region") or "us-central1"
db_admin_password = config.require_secret("db_admin_password")
db_name = "autoscaling_db"

# StackReference - Obtener outputs de la pila base
# Principio: "Piezas pequeñas y débilmente acopladas" (Cap 1)
base_stack = StackReference("ChristianPE1-org/gcp-base/production")
gke_zone = base_stack.get_output("zone")

# Cloud SQL Instance - PostgreSQL
# Tier: db-f1-micro (la instancia más pequeña y económica)
postgres_instance = gcp.sql.DatabaseInstance(
    f"{project_name}-postgres",
    name=f"{project_name}-postgres",
    database_version="POSTGRES_15",  # Versión estable
    region=region,
    
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-f1-micro",  # 1 vCPU compartida, 0.6 GB RAM (más barato)
        
        # Configuración de disponibilidad (deshabilitada para ahorrar)
        availability_type="ZONAL",  # Single-zone (no HA para ahorrar)
        
        # Backups
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            enabled=True,
            start_time="03:00",  # 3 AM
            point_in_time_recovery_enabled=False  # Deshabilitado para ahorrar
        ),
        
        # Configuración de IP (permitir conexiones desde cualquier lugar)
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=True,  # Habilitar IP pública
            authorized_networks=[
                gcp.sql.DatabaseInstanceSettingsIpConfigurationAuthorizedNetworkArgs(
                    name="allow-all",
                    value="0.0.0.0/0"  # Permitir todas las IPs (para desarrollo)
                )
            ]
        ),
        
        # Configuración de disco
        disk_autoresize=True,
        disk_size=10,  # 10 GB (mínimo)
        disk_type="PD_HDD",  # Disco HDD (más barato que SSD)
        
        # Flags de PostgreSQL
        database_flags=[
            gcp.sql.DatabaseInstanceSettingsDatabaseFlagArgs(
                name="max_connections",
                value="100"
            )
        ]
    ),
    
    # Protección contra eliminación accidental
    deletion_protection=False  # False para poder destruir fácilmente en desarrollo
)

# Usuario administrador de PostgreSQL
postgres_user = gcp.sql.User(
    f"{project_name}-postgres-user",
    name="postgres",
    instance=postgres_instance.name,
    password=db_admin_password
)

# Base de datos
postgres_database = gcp.sql.Database(
    f"{project_name}-database",
    name=db_name,
    instance=postgres_instance.name,
    charset="UTF8",
    collation="en_US.UTF8"
)

# Exports
export("postgres_instance_name", postgres_instance.name)
export("postgres_connection_name", postgres_instance.connection_name)
export("postgres_public_ip", postgres_instance.public_ip_address)
export("postgres_first_ip", postgres_instance.first_ip_address)
export("postgres_admin_user", postgres_user.name)
export("database_name", postgres_database.name)

# Connection string para aplicaciones
export("connection_string", Output.all(
    postgres_instance.public_ip_address,
    postgres_user.name,
    db_admin_password,
    postgres_database.name
).apply(
    lambda args: f"postgresql://{args[1]}:{args[2]}@{args[0]}:5432/{args[3]}"
))

export("db_status", Output.concat(
    "Cloud SQL PostgreSQL desplegado en ", region,
    " (db-f1-micro, 10GB HDD). Base de datos: ", postgres_database.name
))

"""
Pila 1: Infraestructura Base - AKS Cluster
Implementa: Principios IaC Capítulos 2, 3, 4
- Define todo como código (Cap 4)
- Hacer reproducible (Cap 2)
- IaaS Layer (Cap 3)
"""

import pulumi
import pulumi_azure_native as azure
from pulumi import Config, export, Output

config = Config()
project_name = "cpe-k8s-autoscaling"
location = config.get("location") or "eastus"  # AKS disponible en East US
admin_username = "azureuser"
ssh_public_key = config.require("ssh_public_key")
subscription_id = "1eb83675-114b-4f93-8921-f055b5bd6ea8"

# Resource Group - Contenedor de todos los recursos
resource_group = azure.resources.ResourceGroup(
    f"{project_name}-rg",
    location=location,
    resource_group_name=f"{project_name}-rg",
    tags={
        "project": "autoscaling-demo",
        "environment": "production",
        "managed-by": "pulumi",
        "iac-pattern": "micro-stack-base"
    }
)

# Virtual Network - Red privada para AKS
vnet = azure.network.VirtualNetwork(
    f"{project_name}-vnet",
    resource_group_name=resource_group.name,
    location=location,
    virtual_network_name=f"{project_name}-vnet",
    address_space=azure.network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"]
    ),
    tags={
        "component": "networking"
    }
)

# Subnet para AKS cluster
aks_subnet = azure.network.Subnet(
    f"{project_name}-aks-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name=f"{project_name}-aks-subnet",
    address_prefix="10.0.1.0/24",
)

# Network Security Group - Seguridad de red
nsg = azure.network.NetworkSecurityGroup(
    f"{project_name}-nsg",
    resource_group_name=resource_group.name,
    location=location,
    network_security_group_name=f"{project_name}-nsg",
    security_rules=[
        # Permitir tráfico HTTP desde internet
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
        # Permitir tráfico HTTPS
        azure.network.SecurityRuleArgs(
            name="Allow-HTTPS",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="443",
            source_address_prefix="*",
            destination_address_prefix="*",
            access="Allow",
            priority=110,
            direction="Inbound",
        ),
        # Grafana (solo desde tu IP)
        azure.network.SecurityRuleArgs(
            name="Allow-Grafana",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="3000",
            source_address_prefix="179.7.180.162/32",
            destination_address_prefix="*",
            access="Allow",
            priority=120,
            direction="Inbound",
        ),
        # Prometheus (solo desde tu IP)
        azure.network.SecurityRuleArgs(
            name="Allow-Prometheus",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="9090",
            source_address_prefix="179.7.180.162/32",
            destination_address_prefix="*",
            access="Allow",
            priority=130,
            direction="Inbound",
        ),
    ],
    tags={
        "component": "security"
    }
)

# AKS Cluster - Kubernetes managed service
# Principio: "Asumir sistemas no confiables" + "Cosas desechables"
aks_cluster = azure.containerservice.ManagedCluster(
    f"{project_name}-aks",
    resource_group_name=resource_group.name,
    location=location,
    resource_name=f"{project_name}-aks",
    
    # DNS prefix para el cluster
    dns_prefix=f"{project_name}",
    
    # Identidad del cluster (System Assigned)
    identity=azure.containerservice.ManagedClusterIdentityArgs(
        type=azure.containerservice.ResourceIdentityType.SYSTEM_ASSIGNED
    ),
    
    # Network Profile - Azure CNI para mejor control
    network_profile=azure.containerservice.ContainerServiceNetworkProfileArgs(
        network_plugin="azure",  # Azure CNI
        service_cidr="10.1.0.0/16",
        dns_service_ip="10.1.0.10",
        load_balancer_sku="standard",
    ),
    
    # System Node Pool - Para componentes críticos del sistema
    # Principio: "Minimizar variación" - Todos los nodos son iguales
    agent_pool_profiles=[
        azure.containerservice.ManagedClusterAgentPoolProfileArgs(
            name="systempool",
            count=1,  # 1 nodo fijo para sistema
            vm_size="Standard_B2s",  # 2 vCPU, 4 GB RAM (bajo costo)
            os_type="Linux",
            os_sku="Ubuntu",
            mode="System",  # Node pool de sistema
            vnet_subnet_id=aks_subnet.id,
            enable_auto_scaling=False,  # Sin autoscaling para pool de sistema
            type="VirtualMachineScaleSets",
            tags={
                "pool": "system",
                "role": "infrastructure"
            }
        ),
    ],
    
    # Habilitar RBAC y Azure AD
    enable_rbac=True,
    
    # Kubernetes version
    kubernetes_version="1.28.3",
    
    # Autoescalado del cluster
    auto_scaler_profile=azure.containerservice.ManagedClusterPropertiesAutoScalerProfileArgs(
        scale_down_delay_after_add="5m",
        scale_down_unneeded_time="5m",
        scan_interval="30s",
    ),
    
    tags={
        "component": "kubernetes",
        "iac-principle": "reproducible-desechable"
    }
)

# Frontend Node Pool - Pool separado para frontend
# Principio: "Piezas pequeñas y débilmente acopladas" (Cap 1)
frontend_node_pool = azure.containerservice.AgentPool(
    f"{project_name}-frontend-pool",
    resource_group_name=resource_group.name,
    resource_name=f"{project_name}-aks",
    agent_pool_name="frontend",
    count=1,  # Mínimo 1 nodo
    vm_size="Standard_B2s",
    os_type="Linux",
    os_sku="Ubuntu",
    mode="User",  # Node pool de usuario
    vnet_subnet_id=aks_subnet.id,
    enable_auto_scaling=True,
    min_count=1,
    max_count=3,  # Escala hasta 3 nodos
    type="VirtualMachineScaleSets",
    node_labels={
        "workload": "frontend",
        "tier": "web"
    },
    node_taints=[],
    tags={
        "pool": "frontend",
        "autoscaling": "enabled"
    },
    opts=pulumi.ResourceOptions(depends_on=[aks_cluster])
)

# Backend Node Pool - Pool separado para backend
# Principio: "Piezas pequeñas y débilmente acopladas"
backend_node_pool = azure.containerservice.AgentPool(
    f"{project_name}-backend-pool",
    resource_group_name=resource_group.name,
    resource_name=f"{project_name}-aks",
    agent_pool_name="backend",
    count=1,  # Mínimo 1 nodo
    vm_size="Standard_B2s",
    os_type="Linux",
    os_sku="Ubuntu",
    mode="User",
    vnet_subnet_id=aks_subnet.id,
    enable_auto_scaling=True,
    min_count=1,
    max_count=5,  # Escala hasta 5 nodos (más carga esperada)
    type="VirtualMachineScaleSets",
    node_labels={
        "workload": "backend",
        "tier": "application"
    },
    node_taints=[],
    tags={
        "pool": "backend",
        "autoscaling": "enabled"
    },
    opts=pulumi.ResourceOptions(depends_on=[aks_cluster])
)

# Exports - Para usar en otras pilas
export("resource_group_name", resource_group.name)
export("aks_cluster_name", aks_cluster.name)
export("aks_cluster_id", aks_cluster.id)
export("vnet_id", vnet.id)
export("vnet_name", vnet.name)
export("aks_subnet_id", aks_subnet.id)
export("location", location)

# Información útil para conectarse
export("kubeconfig_command", Output.concat(
    "az aks get-credentials --resource-group ", 
    resource_group.name, 
    " --name ", 
    aks_cluster.name
))

# Información del cluster
export("aks_fqdn", aks_cluster.fqdn)
export("aks_node_resource_group", aks_cluster.node_resource_group)

# Verificación de estado
export("cluster_status", Output.concat(
    "Cluster desplegado en ", location, 
    " con 3 node pools: system (1 nodo), frontend (1-3 nodos), backend (1-5 nodos)"
))

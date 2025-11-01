"""
Pila 1: Infraestructura Base - GKE Cluster (Google Kubernetes Engine)
Implementa: Principios IaC Capítulos 2, 3, 4
- Define todo como código (Cap 4)
- Hacer reproducible (Cap 2)
- IaaS Layer (Cap 3)
"""

import pulumi
import pulumi_gcp as gcp
from pulumi import Config, export, Output

config = Config()
project_name = "cpe-autoscaling"
project_id = "cpe-autoscaling-k8s"  # Tu proyecto de GCP
region = config.get("region") or "us-central1"  # Región con mejores precios
zone = config.get("zone") or "us-central1-a"

# GKE Cluster - Kubernetes managed service en GCP
# Principio: "Asumir sistemas no confiables" + "Cosas desechables"
gke_cluster = gcp.container.Cluster(
    f"{project_name}-gke",
    name=f"{project_name}-gke",
    location=zone,  # Zonal cluster (más barato que regional)
    
    # Eliminar node pool por defecto (crearemos uno personalizado)
    remove_default_node_pool=True,
    initial_node_count=1,
    deletion_protection=False,  # Permitir eliminación fácil para desarrollo
    
    # Configuración de red
    network="default",  # Usar VPC default
    subnetwork="default",
    
    # Configuración de IP para servicios y pods
    ip_allocation_policy=gcp.container.ClusterIpAllocationPolicyArgs(
        cluster_ipv4_cidr_block="/16",  # CIDR para pods
        services_ipv4_cidr_block="/22"  # CIDR para servicios
    ),
    
    # Habilitar autoscaling del cluster
    cluster_autoscaling=gcp.container.ClusterClusterAutoscalingArgs(
        enabled=True,
        resource_limits=[
            gcp.container.ClusterClusterAutoscalingResourceLimitArgs(
                resource_type="cpu",
                minimum=2,
                maximum=8  # Límite conservador para cuenta gratuita
            ),
            gcp.container.ClusterClusterAutoscalingResourceLimitArgs(
                resource_type="memory",
                minimum=4,
                maximum=16  # GB
            )
        ],
        autoscaling_profile="OPTIMIZE_UTILIZATION"  # Optimizar costos
    ),
    
    # Configuración de mantenimiento
    maintenance_policy=gcp.container.ClusterMaintenancePolicyArgs(
        daily_maintenance_window=gcp.container.ClusterMaintenancePolicyDailyMaintenanceWindowArgs(
            start_time="03:00"  # 3 AM
        )
    ),
    
    # Addons útiles
    addons_config=gcp.container.ClusterAddonsConfigArgs(
        http_load_balancing=gcp.container.ClusterAddonsConfigHttpLoadBalancingArgs(
            disabled=False  # Habilitar LoadBalancer
        ),
        horizontal_pod_autoscaling=gcp.container.ClusterAddonsConfigHorizontalPodAutoscalingArgs(
            disabled=False  # HPA habilitado
        )
    )
)

# Node Pool principal - Para todas las cargas de trabajo
# Principio: "Minimizar variación" - Pool único que escala según demanda
primary_node_pool = gcp.container.NodePool(
    f"{project_name}-primary-pool",
    name="primary-pool",
    cluster=gke_cluster.name,
    location=zone,
    
    # Configuración de nodos
    initial_node_count=1,  # Empezar con 1 nodo (ahorro de costos)
    
    # Autoscaling de nodos
    autoscaling=gcp.container.NodePoolAutoscalingArgs(
        min_node_count=1,
        max_node_count=3  # Máximo 3 nodos + 1 de sistema = 4 total
    ),
    
    # Configuración del nodo
    node_config=gcp.container.NodePoolNodeConfigArgs(
        machine_type="e2-small",  # 2 vCPU, 2 GB RAM (costo más bajo)
        disk_size_gb=30,  # 30 GB de disco (suficiente y económico)
        disk_type="pd-standard",  # Disco estándar (más barato)
        
        # Scopes necesarios
        oauth_scopes=[
            "https://www.googleapis.com/auth/compute",
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring"
        ],
        
        # Labels para organización
        labels={
            "pool": "primary",
            "environment": "production",
            "workload": "mixed"  # Frontend y backend en el mismo pool
        },
        
        # Tags para firewall
        tags=["gke-node", f"{project_name}-gke"],
        
        # Metadata
        metadata={
            "disable-legacy-endpoints": "true"
        }
    ),
    
    # Configuración de administración
    management=gcp.container.NodePoolManagementArgs(
        auto_repair=True,
        auto_upgrade=True
    ),
    
    opts=pulumi.ResourceOptions(depends_on=[gke_cluster])
)

# Exports - Para usar en otras pilas
export("cluster_name", gke_cluster.name)
export("cluster_endpoint", gke_cluster.endpoint)
export("cluster_master_version", gke_cluster.master_version)
export("project_id", project_id)
export("region", region)
export("zone", zone)

# Comando para obtener kubeconfig
export("kubeconfig_command", Output.concat(
    "gcloud container clusters get-credentials ",
    gke_cluster.name,
    " --zone=",
    zone,
    " --project=",
    project_id
))

# Información del cluster
export("cluster_status", Output.concat(
    "GKE Cluster desplegado en ", zone,
    " con node pool 'primary' (1-3 nodos e2-small). Autoscaling habilitado."
))

"""
Pila 3: Despliegue de Aplicaciones en Kubernetes - PaaS Layer
Implementa: "Probar y entregar continuamente" (Cap 4)
- Aplica manifiestos de Kubernetes
- Gestiona secretos de manera segura
- Integración con pilas base y DB
"""

import pulumi
import pulumi_kubernetes as k8s
from pulumi import Config, export, Output, StackReference
import base64

config = Config()
project_name = "cpe-k8s-autoscaling"

# Docker images - Configurables desde Pulumi config
backend_image = config.get("backend_image") or "BACKEND_IMAGE_PLACEHOLDER"
frontend_image = config.get("frontend_image") or "FRONTEND_IMAGE_PLACEHOLDER"

# StackReferences - Obtener outputs de pilas anteriores
# Principio: "Piezas pequeñas y débilmente acopladas" (Cap 1)
base_stack = StackReference("organization/k8s-base/production")
db_stack = StackReference("organization/k8s-db/production")

# Obtener información del cluster AKS
resource_group_name = base_stack.get_output("resource_group_name")
aks_cluster_name = base_stack.get_output("aks_cluster_name")

# Obtener información de la base de datos
postgres_fqdn = db_stack.get_output("postgres_fqdn")
postgres_admin_user = db_stack.get_output("postgres_admin_user")
database_name = db_stack.get_output("database_name")
db_password = config.require_secret("db_admin_password")  # Mismo password que usaste en la pila DB

# Provider de Kubernetes - Conecta con AKS
k8s_provider = k8s.Provider(
    "k8s-provider",
    kubeconfig=Output.all(resource_group_name, aks_cluster_name).apply(
        lambda args: f"""
apiVersion: v1
kind: Config
clusters:
- cluster:
    server: https://cpe-k8s-autoscaling-aks-XXXXX.hcp.eastus.azmk8s.io
  name: {args[1]}
contexts:
- context:
    cluster: {args[1]}
    user: clusterUser_{args[0]}_{args[1]}
  name: {args[1]}
current-context: {args[1]}
users:
- name: clusterUser_{args[0]}_{args[1]}
"""
    )
)

# NOTA: En producción, obtener kubeconfig con:
# az aks get-credentials --resource-group <RG> --name <AKS-NAME>
# Y luego usar: pulumi config set kubeconfig <path-to-kubeconfig>

# Backend Namespace
backend_ns = k8s.core.v1.Namespace(
    "backend-namespace",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="backend",
        labels={
            "name": "backend",
            "environment": "production"
        }
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Backend Secret - Credenciales de DB
backend_secret = k8s.core.v1.Secret(
    "backend-db-secret",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="db-credentials",
        namespace=backend_ns.metadata.name
    ),
    type="Opaque",
    string_data={
        "DB_HOST": postgres_fqdn,
        "DB_PORT": "5432",
        "DB_NAME": database_name,
        "DB_USER": postgres_admin_user,
        "DB_PASSWORD": db_password
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[backend_ns])
)

# Backend ConfigMap
backend_config = k8s.core.v1.ConfigMap(
    "backend-config",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="backend-config",
        namespace=backend_ns.metadata.name
    ),
    data={
        "FLASK_ENV": "production",
        "PORT": "5000"
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[backend_ns])
)

# Backend Deployment
backend_deployment = k8s.apps.v1.Deployment(
    "backend-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="backend",
        namespace=backend_ns.metadata.name,
        labels={
            "app": "backend",
            "tier": "application"
        }
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=2,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "backend"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={
                    "app": "backend",
                    "tier": "application"
                },
                annotations={
                    "prometheus.io/scrape": "true",
                    "prometheus.io/port": "5000",
                    "prometheus.io/path": "/metrics"
                }
            ),
            spec=k8s.core.v1.PodSpecArgs(
                affinity=k8s.core.v1.AffinityArgs(
                    node_affinity=k8s.core.v1.NodeAffinityArgs(
                        required_during_scheduling_ignored_during_execution=k8s.core.v1.NodeSelectorArgs(
                            node_selector_terms=[
                                k8s.core.v1.NodeSelectorTermArgs(
                                    match_expressions=[
                                        k8s.core.v1.NodeSelectorRequirementArgs(
                                            key="workload",
                                            operator="In",
                                            values=["backend"]
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                ),
                containers=[
                    k8s.core.v1.ContainerArgs(
                        name="backend",
                        image=backend_image,
                        image_pull_policy="Always",
                        ports=[
                            k8s.core.v1.ContainerPortArgs(
                                container_port=5000,
                                name="http"
                            )
                        ],
                        env=[
                            k8s.core.v1.EnvVarArgs(
                                name="FLASK_ENV",
                                value_from=k8s.core.v1.EnvVarSourceArgs(
                                    config_map_key_ref=k8s.core.v1.ConfigMapKeySelectorArgs(
                                        name="backend-config",
                                        key="FLASK_ENV"
                                    )
                                )
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="DB_HOST",
                                value_from=k8s.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=k8s.core.v1.SecretKeySelectorArgs(
                                        name="db-credentials",
                                        key="DB_HOST"
                                    )
                                )
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="DB_PORT",
                                value_from=k8s.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=k8s.core.v1.SecretKeySelectorArgs(
                                        name="db-credentials",
                                        key="DB_PORT"
                                    )
                                )
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="DB_NAME",
                                value_from=k8s.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=k8s.core.v1.SecretKeySelectorArgs(
                                        name="db-credentials",
                                        key="DB_NAME"
                                    )
                                )
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="DB_USER",
                                value_from=k8s.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=k8s.core.v1.SecretKeySelectorArgs(
                                        name="db-credentials",
                                        key="DB_USER"
                                    )
                                )
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="DB_PASSWORD",
                                value_from=k8s.core.v1.EnvVarSourceArgs(
                                    secret_key_ref=k8s.core.v1.SecretKeySelectorArgs(
                                        name="db-credentials",
                                        key="DB_PASSWORD"
                                    )
                                )
                            ),
                        ],
                        liveness_probe=k8s.core.v1.ProbeArgs(
                            http_get=k8s.core.v1.HTTPGetActionArgs(
                                path="/health",
                                port=5000
                            ),
                            initial_delay_seconds=30,
                            period_seconds=10
                        ),
                        readiness_probe=k8s.core.v1.ProbeArgs(
                            http_get=k8s.core.v1.HTTPGetActionArgs(
                                path="/health",
                                port=5000
                            ),
                            initial_delay_seconds=10,
                            period_seconds=5
                        ),
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={"cpu": "100m", "memory": "128Mi"},
                            limits={"cpu": "500m", "memory": "512Mi"}
                        )
                    )
                ]
            )
        )
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[backend_secret, backend_config]
    )
)

# Backend Service
backend_service = k8s.core.v1.Service(
    "backend-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="backend-service",
        namespace=backend_ns.metadata.name,
        labels={"app": "backend"}
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        type="ClusterIP",
        selector={"app": "backend"},
        ports=[
            k8s.core.v1.ServicePortArgs(
                name="http",
                port=80,
                target_port=5000
            )
        ]
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[backend_deployment])
)

# Backend HPA
backend_hpa = k8s.autoscaling.v2.HorizontalPodAutoscaler(
    "backend-hpa",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="backend-hpa",
        namespace=backend_ns.metadata.name
    ),
    spec=k8s.autoscaling.v2.HorizontalPodAutoscalerSpecArgs(
        scale_target_ref=k8s.autoscaling.v2.CrossVersionObjectReferenceArgs(
            api_version="apps/v1",
            kind="Deployment",
            name="backend"
        ),
        min_replicas=2,
        max_replicas=10,
        metrics=[
            k8s.autoscaling.v2.MetricSpecArgs(
                type="Resource",
                resource=k8s.autoscaling.v2.ResourceMetricSourceArgs(
                    name="cpu",
                    target=k8s.autoscaling.v2.MetricTargetArgs(
                        type="Utilization",
                        average_utilization=70
                    )
                )
            ),
            k8s.autoscaling.v2.MetricSpecArgs(
                type="Resource",
                resource=k8s.autoscaling.v2.ResourceMetricSourceArgs(
                    name="memory",
                    target=k8s.autoscaling.v2.MetricTargetArgs(
                        type="Utilization",
                        average_utilization=80
                    )
                )
            )
        ]
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[backend_deployment])
)

# Frontend Namespace
frontend_ns = k8s.core.v1.Namespace(
    "frontend-namespace",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="frontend",
        labels={
            "name": "frontend",
            "environment": "production"
        }
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Frontend ConfigMap (Nginx config)
frontend_nginx_config = k8s.core.v1.ConfigMap(
    "frontend-nginx-config",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="nginx-config",
        namespace=frontend_ns.metadata.name
    ),
    data={
        "default.conf": """
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend-service.backend.svc.cluster.local;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
"""
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[frontend_ns])
)

# Frontend Deployment
frontend_deployment = k8s.apps.v1.Deployment(
    "frontend-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="frontend",
        namespace=frontend_ns.metadata.name,
        labels={"app": "frontend"}
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "frontend"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "frontend"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                affinity=k8s.core.v1.AffinityArgs(
                    node_affinity=k8s.core.v1.NodeAffinityArgs(
                        required_during_scheduling_ignored_during_execution=k8s.core.v1.NodeSelectorArgs(
                            node_selector_terms=[
                                k8s.core.v1.NodeSelectorTermArgs(
                                    match_expressions=[
                                        k8s.core.v1.NodeSelectorRequirementArgs(
                                            key="workload",
                                            operator="In",
                                            values=["frontend"]
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                ),
                containers=[
                    k8s.core.v1.ContainerArgs(
                        name="frontend",
                        image=frontend_image,
                        image_pull_policy="Always",
                        ports=[
                            k8s.core.v1.ContainerPortArgs(
                                container_port=80,
                                name="http"
                            )
                        ],
                        volume_mounts=[
                            k8s.core.v1.VolumeMountArgs(
                                name="nginx-config",
                                mount_path="/etc/nginx/conf.d",
                                read_only=True
                            )
                        ],
                        liveness_probe=k8s.core.v1.ProbeArgs(
                            http_get=k8s.core.v1.HTTPGetActionArgs(
                                path="/health",
                                port=80
                            ),
                            initial_delay_seconds=10,
                            period_seconds=10
                        ),
                        readiness_probe=k8s.core.v1.ProbeArgs(
                            http_get=k8s.core.v1.HTTPGetActionArgs(
                                path="/health",
                                port=80
                            ),
                            initial_delay_seconds=5,
                            period_seconds=5
                        ),
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={"cpu": "50m", "memory": "64Mi"},
                            limits={"cpu": "200m", "memory": "256Mi"}
                        )
                    )
                ],
                volumes=[
                    k8s.core.v1.VolumeArgs(
                        name="nginx-config",
                        config_map=k8s.core.v1.ConfigMapVolumeSourceArgs(
                            name="nginx-config"
                        )
                    )
                ]
            )
        )
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[frontend_nginx_config])
)

# Frontend Service (LoadBalancer)
frontend_service = k8s.core.v1.Service(
    "frontend-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="frontend-service",
        namespace=frontend_ns.metadata.name,
        labels={"app": "frontend"}
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        type="LoadBalancer",
        selector={"app": "frontend"},
        ports=[
            k8s.core.v1.ServicePortArgs(
                name="http",
                port=80,
                target_port=80
            )
        ]
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[frontend_deployment])
)

# Frontend HPA
frontend_hpa = k8s.autoscaling.v2.HorizontalPodAutoscaler(
    "frontend-hpa",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="frontend-hpa",
        namespace=frontend_ns.metadata.name
    ),
    spec=k8s.autoscaling.v2.HorizontalPodAutoscalerSpecArgs(
        scale_target_ref=k8s.autoscaling.v2.CrossVersionObjectReferenceArgs(
            api_version="apps/v1",
            kind="Deployment",
            name="frontend"
        ),
        min_replicas=1,
        max_replicas=5,
        metrics=[
            k8s.autoscaling.v2.MetricSpecArgs(
                type="Resource",
                resource=k8s.autoscaling.v2.ResourceMetricSourceArgs(
                    name="cpu",
                    target=k8s.autoscaling.v2.MetricTargetArgs(
                        type="Utilization",
                        average_utilization=60
                    )
                )
            )
        ]
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[frontend_deployment])
)

# Exports
export("backend_namespace", backend_ns.metadata.name)
export("frontend_namespace", frontend_ns.metadata.name)
export("backend_service_name", backend_service.metadata.name)
export("frontend_service_name", frontend_service.metadata.name)
export("frontend_url", frontend_service.status.apply(
    lambda status: f"http://{status.load_balancer.ingress[0].ip}" if status and status.load_balancer and status.load_balancer.ingress else "Pending..."
))

export("deployment_status", Output.concat(
    "Backend desplegado en namespace 'backend' (2-10 replicas) | ",
    "Frontend desplegado en namespace 'frontend' (1-5 replicas) | ",
    "Autoscaling habilitado con HPA"
))

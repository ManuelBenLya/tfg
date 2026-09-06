from locust import HttpUser, task, between
import random

TOKENS_SERVIDORES = [
    "sl1RqB4xMJSSjXhwtqE6pHflHZDE3iz2TBG7RWjJNRI"
]

class AgenteSimulado(HttpUser):
    # ¡AQUÍ ESTÁ LA SOLUCIÓN! Definimos el host base para que Locust no se queje
    host = "https://api-monitor-tfg.onrender.com"
    wait_time = between(9, 11)

    def on_start(self):
        self.token = random.choice(TOKENS_SERVIDORES)

    @task
    def enviar_telemetria(self):
        payload = {
            "cpu_usage_pct": round(random.uniform(5.0, 95.0), 2),
            "disk_usage_pct": round(random.uniform(10.0, 90.0), 2),
            "disk_os_gb": round(random.uniform(30.0, 60.0), 2),
            "disk_db_gb": round(random.uniform(10.0, 200.0), 2),
            "disk_logs_gb": round(random.uniform(1.0, 20.0), 2),
            "disk_free_gb": round(random.uniform(50.0, 500.0), 2),
            "ram_usage_mb": int(random.uniform(1024, 16384)),
            "network_latency_ms": int(random.uniform(15, 120)),
            "discos_json": [{"montaje": "/", "estado": "ok"}] 
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Server-Token": self.token,
            "Content-Type": "application/json"
        }

        # Lanzamos la petición usando solo la ruta, ya que el host está definido arriba
        with self.client.post("/api/metricas/", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            elif response.status_code == 422:
                print(f"\n--- ERROR DE VALIDACIÓN ---\n{response.text}\n")
                response.failure(f"Error 422")
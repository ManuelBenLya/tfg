import os
import sys
import time
import psutil
import requests
import subprocess
import platform
import re
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QStyle, 
                             QDialog, QVBoxLayout, QListWidget, QFormLayout, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QThread, pyqtSignal, QSettings

HOST_PING = "8.8.8.8"

def medir_latencia(host: str) -> float:
    parametro_count = "-n" if platform.system().lower() == "windows" else "-c"
    comando = ["ping", parametro_count, "1", host]
    try:
        resultado = subprocess.run(
            comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        if resultado.returncode == 0:
            match = re.search(r'(?:time|tiempo)\s*[=<]\s*([\d\.,]+)\s*ms', resultado.stdout, re.IGNORECASE)
            if match:
                valor_str = match.group(1).replace(",", ".")
                return round(float(valor_str), 2)
    except Exception:
        pass
    return 0.0

# --- NUEVA FUNCIÓN PARA CALCULAR EL TAMAÑO DE CARPETAS ---
def obtener_tamano_carpeta_gb(ruta_carpeta: str) -> float:
    """Calcula el tamaño de una carpeta en Gigabytes. Devuelve 0.0 si no existe."""
    total_size = 0
    if not os.path.exists(ruta_carpeta):
        return 0.0
    
    try:
        # Recorremos recursivamente todos los archivos
        for dirpath, dirnames, filenames in os.walk(ruta_carpeta):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except PermissionError:
        pass # Ignoramos carpetas a las que el usuario no tiene acceso
        
    return round(total_size / (1024**3), 2) # Convertimos bytes a GB


# --- NUEVA: VENTANA DE CONFIGURACIÓN ---
class VentanaConfiguracion(QDialog):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.setWindowTitle("Configuración del Agente")
        self.resize(400, 150)
        
        # QSettings permite guardar datos en el SO para no perderlos al cerrar
        self.settings = QSettings("MiTFG", "AgenteMonitorizacion")
        
        layout = QFormLayout()
        
        self.input_url = QLineEdit()
        # Cargamos el valor guardado, o uno por defecto
        self.input_url.setText(self.settings.value("api_url", "http://127.0.0.1:8000/api/metricas/"))
        layout.addRow("URL de la API:", self.input_url)
        
        self.input_token = QLineEdit()
        self.input_token.setText(self.settings.value("token", ""))
        self.input_token.setPlaceholderText("Pega aquí el Token generado en Next.js")
        layout.addRow("Token de Acceso:", self.input_token)
        
        btn_guardar = QPushButton("Guardar y Aplicar")
        btn_guardar.setStyleSheet("background-color: #2563eb; color: white; padding: 5px; border-radius: 3px;")
        btn_guardar.clicked.connect(self.guardar)
        layout.addRow(btn_guardar)
        
        self.setLayout(layout)
        
    def guardar(self):
        url = self.input_url.text().strip()
        token = self.input_token.text().strip()
        
        if not url or not token:
            QMessageBox.warning(self, "Error", "La URL y el Token son obligatorios.")
            return
            
        # Guardamos en el sistema
        self.settings.setValue("api_url", url)
        self.settings.setValue("token", token)
        
        # Actualizamos el hilo en caliente
        self.parent_app.thread.actualizar_credenciales(url, token)
        QMessageBox.information(self, "Éxito", "Configuración guardada. El agente usará estas credenciales.")
        self.close()


# --- VENTANA DEL HISTORIAL ---
class VentanaMetricas(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial de Recolección")
        self.resize(400, 400) 
        
        layout = QVBoxLayout()
        self.lista_logs = QListWidget()
        self.lista_logs.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                color: #a6accd;
                font-family: monospace;
                font-size: 12px;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        layout.addWidget(self.lista_logs)
        self.setLayout(layout)

    def agregar_registro(self, mensaje):
        hora_actual = datetime.now().strftime("%H:%M:%S")
        self.lista_logs.insertItem(0, f"[{hora_actual}] {mensaje}")
        if self.lista_logs.count() > 50:
            self.lista_logs.takeItem(50)


# --- HILO DE RECOLECCIÓN DINÁMICO ---
class RecolectorThread(QThread):
    nuevo_log = pyqtSignal(str) 

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.is_paused = False
        
        self.settings = QSettings("MiTFG", "AgenteMonitorizacion")
        self.url = self.settings.value("api_url", "http://127.0.0.1:8000/api/metricas/")
        self.token = self.settings.value("token", "")
        
        # 🌟 Caché de tamaño de carpetas pesadas
        self.ultimo_calculo_disco = 0.0
        self.cached_os_gb = 0.0
        self.cached_logs_gb = 0.0
        self.cached_db_gb = 0.0

    def actualizar_credenciales(self, url, token):
        self.url = url
        self.token = token

    def run(self):
        self.nuevo_log.emit("Iniciando servicio de recolección...")
        while self.is_running:
            if not self.token:
                self.nuevo_log.emit("⚠ Falta el Token. Ve a Configuración.")
                time.sleep(5)
                continue

            if not self.is_paused:
                try:
                    cpu = psutil.cpu_percent(interval=1)
                    ram_mb = psutil.virtual_memory().used / (1024 * 1024)
                    
                    # Calcular el tamaño de las carpetas solo cada 5 minutos (300 segundos) para no ralentizar el bucle
                    ahora_ts = time.time()
                    if ahora_ts - self.ultimo_calculo_disco > 300:
                        if platform.system().lower() == "windows":
                            self.cached_os_gb = obtener_tamano_carpeta_gb("C:\\Windows")
                            self.cached_logs_gb = obtener_tamano_carpeta_gb("C:\\Windows\\System32\\winevt\\Logs")
                            self.cached_db_gb = 0.0
                        else:
                            self.cached_os_gb = obtener_tamano_carpeta_gb("/usr")
                            self.cached_logs_gb = obtener_tamano_carpeta_gb("/var/log")
                            self.cached_db_gb = obtener_tamano_carpeta_gb("/var/lib/postgresql")
                        self.ultimo_calculo_disco = ahora_ts

                    # 🌟 DETECCIÓN DE TODOS LOS DISCOS MONTADOS
                    discos = []
                    particiones = psutil.disk_partitions(all=False)
                    for part in particiones:
                        # Filtrar CD-ROMs y montajes sin sistema de archivos
                        if 'cdrom' in part.opts or part.fstype == '':
                            continue
                        # Evitar disqueteras antiguas en Windows (A: o B:)
                        if platform.system().lower() == "windows" and part.device.startswith(('A:', 'B:')):
                            continue
                        
                        try:
                            uso = psutil.disk_usage(part.mountpoint)
                            
                            # Identificar si es el disco del sistema principal (C: o /)
                            es_principal = False
                            if platform.system().lower() == "windows":
                                es_principal = part.mountpoint.upper().startswith('C:')
                            else:
                                es_principal = part.mountpoint == '/'
                                
                            if es_principal:
                                t_os = self.cached_os_gb
                                t_logs = self.cached_logs_gb
                                t_db = self.cached_db_gb
                            else:
                                t_os = 0.0
                                t_logs = 0.0
                                t_db = 0.0
                                
                            discos.append({
                                "device": part.mountpoint,
                                "usage_pct": round(uso.percent, 2),
                                "free_gb": round(uso.free / (1024**3), 2),
                                "os_gb": t_os,
                                "logs_gb": t_logs,
                                "db_gb": t_db
                            })
                        except Exception:
                            continue

                    # Identificamos el disco principal para mantener compatibilidad
                    disco_principal = next((d for d in discos if d["device"] == ('C:\\' if platform.system().lower() == "windows" else '/')), discos[0] if discos else None)
                    
                    latencia = medir_latencia(HOST_PING)
                    
                    payload = {
                        "cpu_usage_pct": round(cpu, 2),
                        "ram_usage_mb": round(ram_mb, 2),
                        "disk_usage_pct": disco_principal["usage_pct"] if disco_principal else 0.0,
                        "disk_os_gb": disco_principal["os_gb"] if disco_principal else 0.0,
                        "disk_db_gb": disco_principal["db_gb"] if disco_principal else 0.0,
                        "disk_logs_gb": disco_principal["logs_gb"] if disco_principal else 0.0,
                        "disk_free_gb": disco_principal["free_gb"] if disco_principal else 0.0,
                        "network_latency_ms": latencia,
                        "discos_json": discos
                    }
                    
                    headers = {
                        "x-server-token": self.token,
                        "Content-Type": "application/json"
                    }
                    
                    response = requests.post(self.url, json=payload, headers=headers)
                    if response.status_code == 201:
                        lib_gb = disco_principal["free_gb"] if disco_principal else 0.0
                        self.nuevo_log.emit(f"OK | CPU: {cpu}% | RAM: {ram_mb:.0f}MB | DiscoLibre: {lib_gb}GB")
                    else:
                        self.nuevo_log.emit(f"ERROR 422 | {response.text}")                     
                except Exception as e:
                    self.nuevo_log.emit(f"ERROR | Excepción: {e}")
            
            for _ in range(5):
                if not self.is_running:
                    break
                time.sleep(1)

    def detener_por_completo(self):
        self.is_running = False

    def pausar(self):
        self.is_paused = True
        self.nuevo_log.emit("--- RECOLECCIÓN PAUSADA ---")

    def reanudar(self):
        self.is_paused = False
        self.nuevo_log.emit("--- RECOLECCIÓN REANUDADA ---")


# --- APLICACIÓN DE LA BANDEJA DEL SISTEMA ---
class AgenteTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.thread = RecolectorThread()
        self.ventana_logs = VentanaMetricas()
        self.ventana_config = VentanaConfiguracion(self)
        
        self.thread.nuevo_log.connect(self.ventana_logs.agregar_registro)
        
        self.tray_icon = QSystemTrayIcon()
        icono_defecto = self.app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icono_defecto)
        self.tray_icon.setToolTip("Agente de Monitorización")
        
        self.menu = QMenu()
        
        self.accion_configurar = QAction("⚙ Configurar Agente")
        self.accion_configurar.triggered.connect(self.mostrar_config)
        
        self.accion_ver_metricas = QAction("📊 Ver historial (Logs)")
        self.accion_ver_metricas.triggered.connect(self.mostrar_logs)
        
        self.accion_iniciar = QAction("▶ Iniciar Recolección")
        self.accion_iniciar.triggered.connect(self.iniciar)
        
        self.accion_parar = QAction("⏸ Parar Recolección")
        self.accion_parar.triggered.connect(self.parar)
        self.accion_parar.setEnabled(False)
        
        self.accion_salir = QAction("✖ Salir")
        self.accion_salir.triggered.connect(self.salir)
        
        self.menu.addAction(self.accion_configurar)
        self.menu.addAction(self.accion_ver_metricas)
        self.menu.addSeparator()
        self.menu.addAction(self.accion_iniciar)
        self.menu.addAction(self.accion_parar)
        self.menu.addSeparator()
        self.menu.addAction(self.accion_salir)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

    def mostrar_config(self):
        self.ventana_config.show()
        self.ventana_config.activateWindow()

    def mostrar_logs(self):
        self.ventana_logs.show()
        self.ventana_logs.activateWindow()

    def iniciar(self):
        if not self.thread.isRunning():
            self.thread.start()
        else:
            self.thread.reanudar()
            
        self.accion_iniciar.setEnabled(False)
        self.accion_parar.setEnabled(True)

    def parar(self):
        self.thread.pausar()
        self.accion_iniciar.setEnabled(True)
        self.accion_parar.setEnabled(False)

    def salir(self):
        self.thread.detener_por_completo()
        if self.thread.isRunning():
            self.thread.wait()
        self.ventana_logs.close()
        self.ventana_config.close()
        self.tray_icon.hide()
        self.app.quit()

    def ejecutar(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = AgenteTrayApp()
    app.ejecutar()
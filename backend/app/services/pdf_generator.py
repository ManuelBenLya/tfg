from fpdf import FPDF
from datetime import datetime
import io

# 🧠 1. EL MOTOR SIMBÓLICO (Sistema Basado en Reglas)
def generar_conclusion_simbolica(cpu_avg, ram_avg, disco_avg, umbral_ram):
    conclusion = "El servidor presenta un rendimiento estable y opera dentro de los parámetros de normalidad. "
    problemas = []

    # Reglas de producción (If-Then)
    if cpu_avg > 85:
        problemas.append("La carga del procesador es críticamente alta, sugiriendo un posible cuello de botella en cómputo.")
    elif cpu_avg > 70:
        problemas.append("La CPU muestra un uso elevado continuo.")

    # RAM (ram_avg está en MB, umbral_ram está en MB)
    if umbral_ram and ram_avg > umbral_ram:
        problemas.append("La memoria RAM ha superado el umbral establecido, existe riesgo de inestabilidad o swap excesivo.")
    elif umbral_ram and ram_avg > umbral_ram * 0.9:
        problemas.append("La memoria RAM está cerca del umbral límite de capacidad.")

    if disco_avg > 90:
        problemas.append("El almacenamiento está a punto de agotarse. Se requiere limpieza urgente o ampliación de volumen.")

    # Resolución del motor
    if problemas:
        conclusion = "ATENCIÓN: Se han detectado los siguientes riesgos estructurales: " + " ".join(problemas)
    
    return conclusion

# 📄 2. EL GENERADOR DEL PDF
def crear_reporte_pdf(servidor, metricas_resumen, usuario_email):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- CABECERA ---
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "SITEM - Informe de Rendimiento de Infraestructura", ln=True, align="C")
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 5, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.cell(0, 5, f"Generado por: {usuario_email}", ln=True, align="C")
    pdf.ln(10)

    # --- 1. INFO DEL SERVIDOR ---
    pdf.set_font("helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, " 1. INFORMACIÓN DEL NODO", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 6, f"Nombre del Servidor: {servidor.nombre}", ln=True)
    pdf.cell(0, 6, f"Dirección IP: {servidor.ip_direccion}", ln=True)
    pdf.cell(0, 6, f"Estado Actual: {servidor.estado}", ln=True)
    pdf.ln(5)

    # --- 2. ANÁLISIS DE RECURSOS ---
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, " 2. ANÁLISIS DE RECURSOS (MÉTRICAS MEDIAS)", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    
    # Extraemos los datos que nos hayan pasado
    cpu = metricas_resumen.get("cpu_avg", 0)
    ram = metricas_resumen.get("ram_avg", 0)
    disco = metricas_resumen.get("disco_avg", 0)
    
    pdf.cell(0, 6, f"Uso medio de CPU: {cpu}% (Umbral: {servidor.umbral_cpu}%)", ln=True)
    pdf.cell(0, 6, f"Uso medio de RAM: {ram:.0f} MB (Umbral: {servidor.umbral_ram:.0f} MB)", ln=True)
    pdf.cell(0, 6, f"Uso medio de Disco: {disco}% (Umbral: {servidor.umbral_disco}%)", ln=True)
    pdf.ln(5)

    # --- 3. CONCLUSIÓN DEL SISTEMA ---
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, " 3. DIAGNÓSTICO DEL SISTEMA", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    
    # Llamamos a nuestro motor de reglas
    diagnostico = generar_conclusion_simbolica(cpu, ram, disco, servidor.umbral_ram)
    pdf.multi_cell(0, 6, diagnostico)

    # Convertimos el PDF a bytes para enviarlo por HTTP sin guardarlo en disco
    pdf_str = pdf.output(dest='S') 
    if isinstance(pdf_str, str):
        pdf_bytes = pdf_str.encode('latin1')
    else:
        pdf_bytes = pdf_str
    return io.BytesIO(pdf_bytes)
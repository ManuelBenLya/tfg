def evaluar_umbral_cpu(uso_actual: float, umbral_limite: float) -> bool:
    """Función lógica del motor de alertas."""
    return uso_actual >= umbral_limite

def test_motor_alertas_valores_limite():
    """Valida el comportamiento del disparador de alertas ante vectores límite."""
    umbral_configurado = 90.0
    
    # Caso 1: Por debajo del umbral (Sin alerta)
    assert evaluar_umbral_cpu(89.9, umbral_configurado) is False
    
    # Caso 2: Exactamente igual al umbral (Debe saltar la alerta)
    assert evaluar_umbral_cpu(90.0, umbral_configurado) is True
    
    # Caso 3: Superando el umbral (Debe saltar la alerta)
    assert evaluar_umbral_cpu(95.5, umbral_configurado) is True
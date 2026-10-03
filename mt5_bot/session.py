"""
Módulo de sesiones operativas.
Define horarios de operación según sesiones de mercado (Londres, NY, etc.)
y permite filtrar operaciones por horario.
"""

from datetime import datetime, time, timedelta
from typing import Tuple, List
import pytz


# Sesiones operativas globales
SESSIONS = {
    "LONDON": {
        "start": time(8, 0),      # 08:00 UTC
        "end": time(16, 30),      # 16:30 UTC
        "name": "London Session"
    },
    "NEW_YORK": {
        "start": time(13, 0),     # 13:00 UTC
        "end": time(21, 0),       # 21:00 UTC
        "name": "New York Session"
    },
    "TOKYO": {
        "start": time(22, 0),     # 22:00 UTC (00:00 JST)
        "end": time(7, 0),        # 07:00 UTC (15:00 JST)
        "name": "Tokyo Session"
    },
    "SYDNEY": {
        "start": time(20, 0),     # 20:00 UTC (06:00 AEDT)
        "end": time(5, 0),        # 05:00 UTC (15:00 AEDT)
        "name": "Sydney Session"
    },
    "LONDON_NY_OVERLAP": {
        "start": time(13, 0),     # 13:00 UTC
        "end": time(16, 30),      # 16:30 UTC
        "name": "London-NY Overlap (Alta volatilidad)"
    }
}

# Zonas horarias
TIMEZONES = {
    "UTC": pytz.UTC,
    "London": pytz.timezone("Europe/London"),
    "NewYork": pytz.timezone("America/New_York"),
    "Tokyo": pytz.timezone("Asia/Tokyo"),
    "Sydney": pytz.timezone("Australia/Sydney"),
}


def get_current_time_utc() -> datetime:
    """Obtiene la hora actual en UTC."""
    return datetime.now(pytz.UTC).replace(tzinfo=None)


def is_time_in_range(current_time: time, start: time, end: time) -> bool:
    """
    Verifica si la hora actual está dentro del rango.
    Maneja casos donde el rango cruza la medianoche (ej: Tokyo).
    """
    if start <= end:
        return start <= current_time < end
    else:
        # El rango cruza la medianoche
        return current_time >= start or current_time < end


def is_session_active(session_name: str, timezone_str: str = "UTC") -> bool:
    """
    Verifica si una sesión específica está activa en una zona horaria.

    Args:
        session_name: Nombre de la sesión ("LONDON", "NEW_YORK", etc.)
        timezone_str: Zona horaria ("UTC", "London", "NewYork", etc.)

    Returns:
        True si la sesión está activa, False si no.
    """
    if session_name not in SESSIONS:
        print(f"Sesión '{session_name}' no encontrada.")
        return False

    if timezone_str not in TIMEZONES:
        print(f"Zona horaria '{timezone_str}' no soportada.")
        return False

    session = SESSIONS[session_name]
    tz = TIMEZONES[timezone_str]

    # Obtener hora actual en la zona especificada
    now_utc = datetime.now(pytz.UTC)
    now_local = now_utc.astimezone(tz).replace(tzinfo=None)
    current_time = now_local.time()

    is_active = is_time_in_range(current_time, session["start"], session["end"])
    return is_active


def get_active_sessions(timezone_str: str = "UTC") -> List[str]:
    """
    Retorna lista de sesiones activas en este momento.
    """
    active = []
    for session_name in SESSIONS.keys():
        if is_session_active(session_name, timezone_str):
            active.append(session_name)
    return active


def can_trade_in_session(allowed_sessions: List[str], timezone_str: str = "UTC") -> bool:
    """
    Verifica si actualmente se puede operar en las sesiones permitidas.

    Args:
        allowed_sessions: Lista de sesiones permitidas (ej: ["LONDON", "LONDON_NY_OVERLAP"])
        timezone_str: Zona horaria

    Returns:
        True si al menos una sesión permitida está activa.
    """
    active = get_active_sessions(timezone_str)
    for session in allowed_sessions:
        if session in active:
            return True
    return False


def get_trading_window_info(allowed_sessions: List[str], timezone_str: str = "UTC") -> dict:
    """
    Retorna información sobre la ventana de operación actual.
    """
    active_sessions = get_active_sessions(timezone_str)
    can_trade = can_trade_in_session(allowed_sessions, timezone_str)

    tz = TIMEZONES.get(timezone_str, pytz.UTC)
    now_utc = datetime.now(pytz.UTC)
    now_local = now_utc.astimezone(tz).replace(tzinfo=None)

    return {
        "current_time": now_local,
        "timezone": timezone_str,
        "active_sessions": active_sessions,
        "allowed_sessions": allowed_sessions,
        "can_trade": can_trade,
        "active_and_allowed": [s for s in active_sessions if s in allowed_sessions]
    }


def print_trading_window(allowed_sessions: List[str], timezone_str: str = "UTC") -> None:
    """
    Imprime información formateada sobre la ventana de operación.
    """
    info = get_trading_window_info(allowed_sessions, timezone_str)
    
    print("\n" + "=" * 60)
    print("ESTADO DE SESIÓN OPERATIVA")
    print("=" * 60)
    print(f"Hora actual ({info['timezone']}): {info['current_time'].strftime('%H:%M:%S')}")
    print(f"Sesiones activas: {', '.join(info['active_sessions']) if info['active_sessions'] else 'Ninguna'}")
    print(f"Sesiones permitidas: {', '.join(info['allowed_sessions'])}")
    print(f"¿Se puede operar?: {'✓ SÍ' if info['can_trade'] else '✗ NO'}")
    if info['active_and_allowed']:
        print(f"Sesiones activas y permitidas: {', '.join(info['active_and_allowed'])}")
    print("=" * 60 + "\n")

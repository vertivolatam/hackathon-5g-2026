"""Red: contrato Ethernet RMII (port de eth.rs) + WiFi MicroPython.

Ethernet 100M = EMAC interno del P4 + PHY IP101GRI por RMII. Sin driver
RMII en MicroPython 2026: el bring-up de referencia es ESP-IDF
(`esp_eth` + PHY IP101). Este módulo fija el contrato de pines para no
adivinarlos después, y aporta el helper WiFi que sí usa el firmware
(la radio va por SDIO vía el módulo C5/C6, no por estos pines).
"""
import time

# Dirección PHY por defecto del IP101GRI en la NANO.
PHY_ADDR_DEFAULT = 1


def rmii_summary():
    """Devuelve el mapa RMII en una línea para el log de arranque.

    Returns:
        str: pines REF_CLK/TX_EN/TXD/CRS_DV/RXD/MDC/MDIO/RST. Sirve como
            recordatorio impreso de no colgar GPIOs RMII en boot
            (GPIO35 es strapping).
    """
    return (
        "RMII IP101GRI: REF_CLK=50 TX_EN=49 TXD0=34 TXD1=35 "
        "CRS_DV=28 RXD0=29 RXD1=30 MDC=31 MDIO=52 RST=51"
    )


def wifi_connect(ssid, password, timeout_s=20):
    """Conecta la interfaz STA a la red dada y espera a tener IP.

    Activa la interfaz si estaba apagada; si ya hay conexión, no hace
    nada y devuelve la configuración actual.

    Args:
        ssid: nombre de la red WiFi.
        password: clave de la red.
        timeout_s: segundos máximos esperando asociación + DHCP.

    Returns:
        tuple: ifconfig (ip, máscara, gateway, DNS).

    Raises:
        RuntimeError: si expira el timeout sin asociar.
    """
    import network

    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        sta.connect(ssid, password)
        t0 = time.time()
        while not sta.isconnected():
            if time.time() - t0 > timeout_s:
                raise RuntimeError("wifi timeout: " + ssid)
            time.sleep(1)
    return sta.ifconfig()

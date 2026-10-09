"""RSSI de trampa: de la telemetría a Prometheus.

La trampa publica `rssi_dbm` (CSQ del RG255C) en su telemetría y el
backend lo expone como gauge por trampa para el dashboard de enlace.
"""


def test_rssi_telemetria_llega_a_metrics(client):
    r = client.post(
        "/api/telemetry",
        json={"topic": "agrivision/finca-norte/trap-07/telemetry",
              "payload": {"trap_id": "trap-07", "rssi_dbm": -73}},
    )
    assert r.status_code == 201
    body = client.get("/metrics").text
    assert 'agrivision_trap_rssi_dbm{trap_id="trap-07"} -73.0' in body


def test_telemetria_sin_rssi_no_rompe_metrics(client):
    r = client.post("/api/telemetry", json={"topic": "t", "payload": {}})
    assert r.status_code == 201
    assert client.get("/metrics").status_code == 200

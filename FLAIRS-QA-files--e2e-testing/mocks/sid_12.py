sensor_pucks = {
    "27455018-2023-0728-1818-243931896413": {
        "type": "pucks",
        "attributes": {
            "bluetooth-tx-power-mw": 500,
            "setpoint-bound-low": 10.0,
            "updated-at": "2023-07-28T18:20:26.065124+00:00",
            "display-number": "2745",
            "is-gateway": False,
            "ignore-readings-for-room": False,
            "reporting-interval-ds": 255,
            "ir-download": False,
            "current-humidity": None,
            "puck-display-color": "white",
            "connected-gateway-puck-id": "7a04d15b-088c-5215-f666-18b30254749b",
            "name": "Bedroom-2745",
            "features": None,
            "inactive": True,
            "demo-mode": 0,
            "locked": False,
            "last-reported-as-gateway": False,
            "current-rssi": None,
            "beacon-interval-ms": 4095,
            "temperature-offset-c": None,
            "temperature-offset-override-c": None,
            "sub-ghz-radio-tx-power-mw": None,
            "voltage": None,
            "humidity-offset": None,
            "current-temperature-c": None,
            "created-at": "2023-07-28T18:18:24.585745+00:00",
            "orientation": "standing",
            "setpoint-bound-high": 32.23,
            "oauth-app-assigned-at": None,
            "ir-setup-enabled": None
        },
        "id": "27455018-2023-0728-1818-243931896413",
        "relationships": {
            "sensor-readings": {
                "links": {
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/sensor-readings"
                }
            },
            "room": {
                "links": {
                    "self": "/api/pucks/27455018-2023-0728-1818-243931896413/relationships/room",
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/room"
                },
                "data": {
                    "type": "rooms",
                    "id": "13"
                }
            },
            "beacon-sightings": {
                "links": {
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/beacon-sightings"
                }
            },
            "hardware-version": {
                "links": {
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/hardware-version"
                },
                "data": None
            },
            "closest-vents": {
                "links": {
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/closest-vents"
                }
            },
            "current-state": {
                "links": {
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/current-state"
                }
            },
            "structure": {
                "links": {
                    "self": "/api/pucks/27455018-2023-0728-1818-243931896413/relationships/structure",
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/structure"
                },
                "data": {
                    "type": "structures",
                    "id": "12"
                }
            },
            "current-reading": {
                "links": {
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/current-reading"
                }
            },
            "puck-states": {
                "links": {
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/puck-states"
                }
            },
            "hvac-units": {
                "links": {
                    "self": "/api/pucks/27455018-2023-0728-1818-243931896413/relationships/hvac-units",
                    "related": "/api/pucks/27455018-2023-0728-1818-243931896413/hvac-units"
                },
                "data": []
            }
        }
    }
}

gateway_pucks = {
    "7a04d15b-088c-5215-f666-18b30254749b": {
        "type": "pucks",
        "attributes": {
            "bluetooth-tx-power-mw": 500,
            "setpoint-bound-low": 10.0,
            "updated-at": "2023-07-28T18:17:59.328754+00:00",
            "display-number": "7a04",
            "is-gateway": True,
            "ignore-readings-for-room": False,
            "reporting-interval-ds": 255,
            "ir-download": False,
            "current-humidity": None,
            "puck-display-color": "white",
            "connected-gateway-puck-id": "7a04d15b-088c-5215-f666-18b30254749b",
            "name": "Den-7a04",
            "features": None,
            "inactive": True,
            "demo-mode": 0,
            "locked": False,
            "last-reported-as-gateway": True,
            "current-rssi": None,
            "beacon-interval-ms": 4095,
            "temperature-offset-c": None,
            "temperature-offset-override-c": None,
            "sub-ghz-radio-tx-power-mw": None,
            "voltage": None,
            "humidity-offset": None,
            "current-temperature-c": None,
            "created-at": "2023-04-03T22:56:47.985194+00:00",
            "orientation": "standing",
            "setpoint-bound-high": 32.23,
            "oauth-app-assigned-at": None,
            "ir-setup-enabled": None
        },
        "id": "7a04d15b-088c-5215-f666-18b30254749b",
        "relationships": {
            "sensor-readings": {
                "links": {
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/sensor-readings"
                }
            },
            "room": {
                "links": {
                    "self": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/relationships/room",
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/room"
                },
                "data": {
                    "type": "rooms",
                    "id": "12"
                }
            },
            "beacon-sightings": {
                "links": {
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/beacon-sightings"
                }
            },
            "hardware-version": {
                "links": {
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/hardware-version"
                },
                "data": None
            },
            "closest-vents": {
                "links": {
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/closest-vents"
                }
            },
            "current-state": {
                "links": {
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/current-state"
                }
            },
            "structure": {
                "links": {
                    "self": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/relationships/structure",
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/structure"
                },
                "data": {
                    "type": "structures",
                    "id": "12"
                }
            },
            "current-reading": {
                "links": {
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/current-reading"
                }
            },
            "puck-states": {
                "links": {
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/puck-states"
                }
            },
            "hvac-units": {
                "links": {
                    "self": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/relationships/hvac-units",
                    "related": "/api/pucks/7a04d15b-088c-5215-f666-18b30254749b/hvac-units"
                },
                "data": []
            }
        }
    }

}

vents = {
    "36700065-2023-0728-1821-467384768527": {
        "type": "vents",
        "attributes": {
            "updated-at": "2023-07-28T18:22:22.384135+00:00",
            "has-buzzed": False,
            "percent-open-reason": None,
            "percent-open": 100,
            "motor-overdrive-ms": 400,
            "name": "Bedroom-3670",
            "connected-gateway-puck-id": "7a04d15b-088c-5215-f666-18b30254749b",
            "inactive": True,
            "setup-lightstrip": 5,
            "current-rssi": None,
            "voltage": None,
            "created-at": "2023-07-28T18:21:46.852620+00:00"
        },
        "id": "36700065-2023-0728-1821-467384768527",
        "relationships": {
            "sensor-readings": {
                "links": {
                    "related": "/api/vents/36700065-2023-0728-1821-467384768527/sensor-readings"
                }
            },
            "vent-states": {
                "links": {
                    "related": "/api/vents/36700065-2023-0728-1821-467384768527/vent-states"
                }
            },
            "room": {
                "links": {
                    "self": "/api/vents/36700065-2023-0728-1821-467384768527/relationships/room",
                    "related": "/api/vents/36700065-2023-0728-1821-467384768527/room"
                },
                "data": {
                    "type": "rooms",
                    "id": "13"
                }
            },
            "closest-puck": {
                "links": {
                    "related": "/api/vents/36700065-2023-0728-1821-467384768527/closest-pucks"
                }
            },
            "current-state": {
                "links": {
                    "related": "/api/vents/36700065-2023-0728-1821-467384768527/current-state"
                }
            },
            "structure": {
                "links": {
                    "self": "/api/vents/36700065-2023-0728-1821-467384768527/relationships/structure",
                    "related": "/api/vents/36700065-2023-0728-1821-467384768527/structure"
                },
                "data": {
                    "type": "structures",
                    "id": "12"
                }
            },
            "current-reading": {
                "links": {
                    "related": "/api/vents/36700065-2023-0728-1821-467384768527/current-reading"
                }
            }
        }
    }
}

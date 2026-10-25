"""Test energy sites."""
import pytest

from teslajsonpy.const import DEFAULT_ENERGYSITE_NAME
from teslajsonpy.controller import Controller
from teslajsonpy.energy import SolarPowerwallSite, SolarSite

from tests.tesla_mock import (
    SITE_SUMMARY,
    ENERGYSITES,
    SITE_CONFIG,
    SITE_DATA,
    TeslaMock,
)


@pytest.mark.asyncio
async def test_energysite_setup(monkeypatch):
    """Test setup of energysites in Controller.connect()."""
    TeslaMock(monkeypatch)
    _controller = Controller(None)
    await _controller.connect()
    await _controller.generate_energysite_objects()

    solar_site = _controller.energysites[12345]
    powerwall_site = _controller.energysites[67890]

    assert _controller.energysites is not None
    assert solar_site.resource_type == ENERGYSITES[0]["resource_type"]
    assert powerwall_site.resource_type == ENERGYSITES[1]["resource_type"]


@pytest.mark.asyncio
async def test_solar_site(monkeypatch):
    """Test SolarSite class."""
    TeslaMock(monkeypatch)
    _controller = Controller(None)
    await _controller.connect()
    await _controller.generate_energysite_objects()

    _solar_site = _controller.energysites[12345]

    assert _solar_site._api is not None
    assert _solar_site._energysite is not None

    assert _solar_site.energysite_id == ENERGYSITES[0]["energy_site_id"]
    assert _solar_site.has_battery == ENERGYSITES[0]["components"]["battery"]
    assert _solar_site.has_load_meter == ENERGYSITES[0]["components"]["load_meter"]
    assert _solar_site.has_solar == ENERGYSITES[0]["components"]["solar"]
    assert _solar_site.id == ENERGYSITES[0]["id"]
    assert _solar_site.resource_type == ENERGYSITES[0]["resource_type"]
    assert _solar_site.site_name == SITE_CONFIG["site_name"]

    assert _solar_site.grid_power == SITE_DATA["grid_power"]
    assert _solar_site.load_power == SITE_DATA["load_power"]
    assert _solar_site.solar_power == SITE_DATA["solar_power"]
    assert _solar_site.solar_type == ENERGYSITES[0]["components"]["solar_type"]


@pytest.mark.asyncio
async def test_powerwall_site(monkeypatch):
    """Test PowerwallSite class."""
    TeslaMock(monkeypatch)
    _controller = Controller(None)
    await _controller.connect()
    await _controller.generate_energysite_objects()

    _solar_powerwall_site = _controller.energysites[67890]

    assert _solar_powerwall_site._api is not None
    assert _solar_powerwall_site._energysite is not None

    assert _solar_powerwall_site.energysite_id == ENERGYSITES[1]["energy_site_id"]
    assert (
        _solar_powerwall_site.has_load_meter
        == ENERGYSITES[1]["components"]["load_meter"]
    )
    assert _solar_powerwall_site.id == ENERGYSITES[1]["id"]
    assert _solar_powerwall_site.has_battery == ENERGYSITES[1]["components"]["battery"]
    assert _solar_powerwall_site.has_solar == ENERGYSITES[1]["components"]["solar"]
    assert _solar_powerwall_site.resource_type == ENERGYSITES[1]["resource_type"]
    assert _solar_powerwall_site.site_name == ENERGYSITES[1]["site_name"]
    assert (
        _solar_powerwall_site.percentage_charged
        == SITE_SUMMARY["percentage_charged"]
    )
    assert (
        _solar_powerwall_site.battery_power
        == SITE_SUMMARY["battery_power"]
    )
    assert (
        _solar_powerwall_site.grid_power
        == SITE_DATA["grid_power"]
    )
    assert (
        _solar_powerwall_site.grid_status
        == SITE_DATA["grid_status"]
    )
    assert (
        _solar_powerwall_site.load_power
        == SITE_DATA["load_power"]
    )
    assert (
        _solar_powerwall_site.solar_power
        == SITE_DATA["solar_power"]
    )
    assert (
        _solar_powerwall_site.solar_type == ENERGYSITES[1]["components"]["solar_type"]
    )


@pytest.mark.asyncio
async def test_energysite_with_no_name(monkeypatch):
    """Test EnergySite base class with no name."""
    _mock = TeslaMock(monkeypatch)
    _api = Controller(None)
    _energysite = _mock.data_request_energysites()[0]
    _site_config = {12345: _mock.data_request_site_config()}
    _site_data = {12345: _mock.data_request_site_data()}
    _sensor = SolarSite(_api, _energysite, _site_config, _site_data)

    assert _sensor.site_name == DEFAULT_ENERGYSITE_NAME


@pytest.mark.asyncio
async def test_set_operation_mode(monkeypatch):
    """Test set operation mode."""
    TeslaMock(monkeypatch)
    _controller = Controller(None)
    await _controller.connect()
    await _controller.generate_energysite_objects()
    _energysite = _controller.energysites[67890]

    assert await _energysite.set_operation_mode("autonomous") is None


@pytest.mark.asyncio
async def test_set_reserve_percent(monkeypatch):
    """Test set reserve percent."""
    TeslaMock(monkeypatch)
    _controller = Controller(None)
    await _controller.connect()
    await _controller.generate_energysite_objects()
    _energysite = _controller.energysites[67890]

    assert await _energysite.set_reserve_percent(10) is None


@pytest.mark.asyncio
async def test_set_grid_charging(monkeypatch):
    """Test set grid charging."""
    TeslaMock(monkeypatch)
    _controller = Controller(None)
    await _controller.connect()
    await _controller.generate_energysite_objects()
    _energysite = _controller.energysites[67890]

    assert await _energysite.set_grid_charging(True) is None


@pytest.mark.asyncio
async def test_set_export_rule(monkeypatch):
    """Test set export rule."""
    TeslaMock(monkeypatch)
    _controller = Controller(None)
    await _controller.connect()
    await _controller.generate_energysite_objects()
    _energysite = _controller.energysites[67890]

    assert await _energysite.set_export_rule("pv_only") is None


# Test reponse with "grid_status" of "Unknown"

def _solar_powerwall_site(api, *, site_data=None, components=None, user_settings=None):
    """Create a real SDK SolarPowerwallSite from response-shaped data."""
    return SolarPowerwallSite(
        api,
        {
            "energy_site_id": 12345,
            "resource_type": "battery",
            "components": {"battery": True, "solar": True},
        },
        {
            "site_name": "Test Powerwall",
            "version": "24.44.0",
            "components": components or {},
            "user_settings": user_settings or {},
        },
        site_data or {},
        {"percentage_charged": 50, "site_name": "Test Powerwall"},
    )


@pytest.mark.parametrize(
    ("site_data", "components", "user_settings", "expected"),
    [
        ({"storm_mode_capable": True}, {"storm_mode_capable": False}, {}, True),
        ({"storm_mode_capable": False}, {"storm_mode_capable": True}, {}, False),
        ({}, {"storm_mode_capable": True}, {}, True),
        ({}, {"storm_mode_capable": False}, {"storm_mode_enabled": True}, False),
        ({}, {}, {"storm_mode_enabled": False}, True),
        ({}, {}, {}, False),
    ],
    ids=[
        "site-data-true-wins",
        "site-data-false-wins",
        "component-capability-true",
        "component-capability-false-wins",
        "reported-setting-implies-capability",
        "no-capability-data",
    ],
)
def test_storm_mode_capability_is_truthful(
    site_data, components, user_settings, expected
):
    """Capability respects explicit false and only infers from reported settings."""
    site = _solar_powerwall_site(
        None,
        site_data=site_data,
        components=components,
        user_settings=user_settings,
    )

    assert site.storm_mode_capable is expected


def test_storm_mode_missing_state_remains_unknown():
    """Missing Storm Watch state is represented as unknown, not inactive data."""
    site = _solar_powerwall_site(None)

    assert site.storm_mode_capable is False
    assert site.storm_mode_enabled is None
    assert site.storm_mode_active is None
    assert site.storm_mode_states == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ({"Code": 200}, True),
        ({"code": 201}, True),
        ({"code": "200"}, True),
        ({"result": True}, True),
        ({"code": 200, "result": False}, False),
        ({"code": 400, "result": True}, False),
        ({"code": "400", "result": True}, False),
        ({"result": False}, False),
        ({"code": True, "result": True}, False),
        ({"code": "accepted", "result": True}, False),
    ],
    ids=[
        "http-200",
        "http-201",
        "string-http-200",
        "result-true",
        "false-result-dominates",
        "numeric-failure-dominates",
        "string-failure-dominates",
        "false-result",
        "boolean-code-rejected",
        "nonnumeric-code-rejected",
    ],
)
async def test_set_storm_mode_serializes_the_documented_command(response, expected):
    """Storm mode uses the existing endpoint and only mutates accepted settings."""
    calls = []

    async def fake_api(name, **kwargs):
        calls.append((name, kwargs))
        return {"response": response}

    site = _solar_powerwall_site(
        fake_api, user_settings={"storm_mode_enabled": False}
    )

    assert await site.set_storm_mode(True) is expected
    assert calls == [
        (
            "STORM_MODE_SETTINGS",
            {
                "path_vars": {"site_id": 12345},
                "wake_if_asleep": False,
                "enabled": True,
            },
        )
    ]
    assert site.storm_mode_enabled is expected

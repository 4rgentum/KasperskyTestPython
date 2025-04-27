import os
import pytest
from framework.config_reader import ConfigLoader
import framework.validators as v

# --- Helpers ---

def write_config(tmp_path, content):
    config_file = tmp_path / "config.ini"
    config_file.write_text(content)
    return str(config_file)

def base_config(**overrides):
    config = {
        "ScanMemoryLimit": "8192",
        "PackageType": "rpm",
        "ExecArgMax": "50",
        "AdditionalDNSLookup": "true",
        "CoreDumps": "no",
        "RevealSensitiveInfoInTraces": "yes",
        "ExecEnvMax": "50",
        "MaxInotifyWatches": "300000",
        "CoreDumpsPath": "/tmp",
        "UseFanotify": "false",
        "KsvlaMode": "yes",
        "MachineId": "7b5cc0e7-0205-48e1-bf63-347531eef193",
        "StartupTraces": "no",
        "MaxInotifyInstances": "2048",
        "Locale": "en_US.UTF-8",
        "ConnectTimeout": "20m",
        "MaxVirtualMemory": "auto",
        "MaxMemory": "70.5",
        "PingInterval": "3000"
    }
    config.update(overrides)
    return f"""
[General]
ScanMemoryLimit={config["ScanMemoryLimit"]}
PackageType={config["PackageType"]}
ExecArgMax={config["ExecArgMax"]}
AdditionalDNSLookup={config["AdditionalDNSLookup"]}
CoreDumps={config["CoreDumps"]}
RevealSensitiveInfoInTraces={config["RevealSensitiveInfoInTraces"]}
ExecEnvMax={config["ExecEnvMax"]}
MaxInotifyWatches={config["MaxInotifyWatches"]}
CoreDumpsPath={config["CoreDumpsPath"]}
UseFanotify={config["UseFanotify"]}
KsvlaMode={config["KsvlaMode"]}
MachineId={config["MachineId"]}
StartupTraces={config["StartupTraces"]}
MaxInotifyInstances={config["MaxInotifyInstances"]}
Locale={config["Locale"]}

[Watchdog]
ConnectTimeout={config["ConnectTimeout"]}
MaxVirtualMemory={config["MaxVirtualMemory"]}
MaxMemory={config["MaxMemory"]}
PingInterval={config["PingInterval"]}
""".strip()

# --- Tests for General Integers

@pytest.mark.parametrize("param,min_val,max_val", [
    ("ScanMemoryLimit", 1024, 8192),
    ("ExecArgMax", 10, 100),
    ("ExecEnvMax", 10, 100),
    ("MaxInotifyWatches", 1000, 1000000),
    ("MaxInotifyInstances", 1024, 8192)
])
@pytest.mark.parametrize("value_type,expected", [
    ("min", True),
    ("max", True),
    ("below", False),
    ("text", False)
])
def test_general_integers(param, min_val, max_val, value_type, expected, tmp_path, monkeypatch):
    if value_type == "min":
        value = str(min_val)
    elif value_type == "max":
        value = str(max_val)
    elif value_type == "below":
        value = str(min_val - 1)
    else:
        value = "notanumber"

    config_text = base_config(**{param: value})
    config_path = write_config(tmp_path, config_text)
    monkeypatch.setenv("CONFIG_PATH", config_path)
    loader = ConfigLoader()
    sec = loader.get_section("General")

    if value_type == "text":
        assert not v.is_int_in_range(sec[param], min_val, max_val)
    else:
        assert v.is_int_in_range(sec[param], min_val, max_val) == expected

# --- Tests for Enums and Booleans

@pytest.mark.parametrize("param,validator,valid_values,invalid_value", [
    ("PackageType", v.is_valid_package_type, ["rpm", "DEB"], "zip"),
    ("AdditionalDNSLookup", v.is_boolean, ["true", "No"], "maybe"),
    ("CoreDumps", v.is_boolean, ["yes", "false"], "perhaps"),
    ("RevealSensitiveInfoInTraces", v.is_boolean, ["yes", "no"], "wrong"),
    ("UseFanotify", v.is_boolean, ["yes", "no"], "maybe"),
    ("KsvlaMode", v.is_boolean, ["yes", "no"], "fail"),
    ("StartupTraces", v.is_boolean, ["true", "false"], "undefined"),
])
def test_general_enums_booleans(param, validator, valid_values, invalid_value, tmp_path, monkeypatch):
    for val in valid_values:
        config_text = base_config(**{param: val})
        config_path = write_config(tmp_path, config_text)
        monkeypatch.setenv("CONFIG_PATH", config_path)
        loader = ConfigLoader()
        sec = loader.get_section("General")
        assert validator(sec[param])

    config_text = base_config(**{param: invalid_value})
    config_path = write_config(tmp_path, config_text)
    monkeypatch.setenv("CONFIG_PATH", config_path)
    loader = ConfigLoader()
    sec = loader.get_section("General")
    assert not validator(sec[param])

# --- Tests for CoreDumpsPath

def test_core_dumps_path(tmp_path, monkeypatch):
    config_text = base_config(CoreDumpsPath=str(tmp_path))
    config_path = write_config(tmp_path, config_text)
    monkeypatch.setenv("CONFIG_PATH", config_path)
    loader = ConfigLoader()
    sec = loader.get_section("General")
    assert v.is_existing_directory(sec["CoreDumpsPath"])

@pytest.mark.parametrize("path", ["/nonexistent", "relative/path"])
def test_invalid_core_dumps_path(path, tmp_path, monkeypatch):
    config_text = base_config(CoreDumpsPath=path)
    config_path = write_config(tmp_path, config_text)
    monkeypatch.setenv("CONFIG_PATH", config_path)
    loader = ConfigLoader()
    sec = loader.get_section("General")
    assert not v.is_existing_directory(sec["CoreDumpsPath"])

# --- Tests for UUID and Locale

@pytest.mark.parametrize("uuid_val,expected", [
    ("7b5cc0e7-0205-48e1-bf63-347531eef193", True),
    ("invalid-uuid", False)
])
def test_machine_id(uuid_val, expected, tmp_path, monkeypatch):
    config_text = base_config(MachineId=uuid_val)
    config_path = write_config(tmp_path, config_text)
    monkeypatch.setenv("CONFIG_PATH", config_path)
    loader = ConfigLoader()
    sec = loader.get_section("General")
    assert v.is_valid_uuid(sec["MachineId"]) == expected

@pytest.mark.parametrize("locale_val,expected", [
    ("en_US.UTF-8", True),
    ("english_US", False)
])
def test_locale(locale_val, expected, tmp_path, monkeypatch):
    config_text = base_config(Locale=locale_val)
    config_path = write_config(tmp_path, config_text)
    monkeypatch.setenv("CONFIG_PATH", config_path)
    loader = ConfigLoader()
    sec = loader.get_section("General")
    assert v.is_valid_locale(sec["Locale"]) == expected

# --- Tests for Watchdog Section

@pytest.mark.parametrize("param,validator,min_val,max_val", [
    ("ConnectTimeout", v.is_valid_timeout_with_m, 1, 120),
    ("PingInterval", v.is_int_in_range, 100, 10000)
])
@pytest.mark.parametrize("value_type,expected", [
    ("min", True),
    ("max", True),
    ("below", False),
    ("text", False)
])
def test_watchdog_ranges(param, validator, min_val, max_val, value_type, expected, tmp_path, monkeypatch):
    if value_type == "min":
        value = f"{min_val}m" if param == "ConnectTimeout" else str(min_val)
    elif value_type == "max":
        value = f"{max_val}m" if param == "ConnectTimeout" else str(max_val)
    elif value_type == "below":
        value = f"{min_val - 1}m" if param == "ConnectTimeout" else str(min_val - 1)
    else:
        value = "invalid"

    config_text = base_config(**{param: value})
    config_path = write_config(tmp_path, config_text)
    monkeypatch.setenv("CONFIG_PATH", config_path)
    loader = ConfigLoader()
    sec = loader.get_section("Watchdog")
    assert validator(sec[param], min_val, max_val) == expected

@pytest.mark.parametrize("param,value,expected", [
    ("MaxVirtualMemory", "auto", True),
    ("MaxVirtualMemory", "50.5", True),
    ("MaxVirtualMemory", "150", False),
    ("MaxMemory", "off", True),
    ("MaxMemory", "25.0", True),
    ("MaxMemory", "0", False)
])
def test_watchdog_memory(param, value, expected, tmp_path, monkeypatch):
    config_text = base_config(**{param: value})
    config_path = write_config(tmp_path, config_text)
    monkeypatch.setenv("CONFIG_PATH", config_path)
    loader = ConfigLoader()
    sec = loader.get_section("Watchdog")
    assert v.is_valid_memory_value(sec[param]) == expected

# --- Missing Section / Unknown Key

def test_missing_section(tmp_path, monkeypatch):
    content = base_config()
    content = content.replace("[Watchdog]", "")
    path = write_config(tmp_path, content)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    with pytest.raises(ValueError):
        loader.get_section("Watchdog")

def test_unknown_key(tmp_path, monkeypatch):
    content = base_config() + "\nDummyKey=somevalue\n"
    path = write_config(tmp_path, content)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    with pytest.raises(ValueError):
        loader.get_value("General", "DummyKey")

def test_missing_machine_id(tmp_path, monkeypatch):
    config = base_config()
    config = config.replace("MachineId=7b5cc0e7-0205-48e1-bf63-347531eef193", "")
    path = write_config(tmp_path, config)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    with pytest.raises(ValueError):
        loader.get_value("General", "MachineId")

def test_missing_connect_timeout(tmp_path, monkeypatch):
    config = base_config()
    config = config.replace("ConnectTimeout=20m", "")
    path = write_config(tmp_path, config)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    with pytest.raises(ValueError):
        loader.get_value("Watchdog", "ConnectTimeout")

def test_empty_file(tmp_path, monkeypatch):
    empty_config = ""
    path = write_config(tmp_path, empty_config)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    with pytest.raises(ValueError):
        loader.get_section("General")

def test_connect_timeout_without_m(tmp_path, monkeypatch):
    config = base_config(ConnectTimeout="20")  # без 'm'
    path = write_config(tmp_path, config)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    sec = loader.get_section("Watchdog")
    assert not v.is_valid_timeout_with_m(sec["ConnectTimeout"], 1, 120)

def test_max_memory_non_numeric(tmp_path, monkeypatch):
    config = base_config(MaxMemory="abc")
    path = write_config(tmp_path, config)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    sec = loader.get_section("Watchdog")
    assert not v.is_valid_memory_value(sec["MaxMemory"])

def test_core_dumps_path_relative(tmp_path, monkeypatch):
    config = base_config(CoreDumpsPath="relative/path")
    path = write_config(tmp_path, config)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    sec = loader.get_section("General")
    assert not v.is_existing_directory(sec["CoreDumpsPath"])

def test_use_fanotify_invalid(tmp_path, monkeypatch):
    config = base_config(UseFanotify="maybe")
    path = write_config(tmp_path, config)
    monkeypatch.setenv("CONFIG_PATH", path)
    loader = ConfigLoader()
    sec = loader.get_section("General")
    assert not v.is_boolean(sec["UseFanotify"])

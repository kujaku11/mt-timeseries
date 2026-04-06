# -*- coding: utf-8 -*-
"""Minimal FDSN helper utilities used by mt_timeseries."""

from __future__ import annotations

from loguru import logger

period_code_dict = {
    "F": {"min": 1000, "max": 5000},
    "G": {"min": 1000, "max": 5000},
    "D": {"min": 250, "max": 1000},
    "C": {"min": 250, "max": 1000},
    "E": {"min": 80, "max": 250},
    "S": {"min": 10, "max": 80},
    "H": {"min": 80, "max": 250},
    "B": {"min": 10, "max": 80},
    "M": {"min": 1, "max": 10},
    "L": {"min": 0.95, "max": 1.05},
    "V": {"min": 0.095, "max": 0.105},
    "U": {"min": 0.0095, "max": 0.0105},
    "R": {"min": 0.0001, "max": 0.001},
    "P": {"min": 0.00001, "max": 0.0001},
    "T": {"min": 0.000001, "max": 0.00001},
    "Q": {"min": 0, "max": 0.000001},
}

measurement_code_dict = {
    "tilt": "A",
    "creep": "B",
    "calibration": "C",
    "pressure": "D",
    "magnetics": "F",
    "gravity": "G",
    "humidity": "I",
    "temperature": "K",
    "water_current": "O",
    "electric": "Q",
    "rain_fall": "R",
    "linear_strain": "S",
    "tide": "T",
    "wind": "W",
}

measurement_code_dict_reverse = {
    value: key for key, value in measurement_code_dict.items()
}
measurement_code_dict_reverse["Y"] = "auxiliary"

orientation_code_dict = {
    "N": {"min": 0, "max": 15},
    "E": {"min": 75, "max": 90},
    "Z": {"min": 0, "max": 15},
    "1": {"min": 15, "max": 45},
    "2": {"min": 45, "max": 75},
    "3": {"min": 15, "max": 75},
}

mt_code_dict = {"magnetics": "h", "electric": "e"}


def get_period_code(sample_rate: float) -> str:
    period_code = "A"
    for key, value_dict in sorted(period_code_dict.items()):
        if value_dict["min"] <= sample_rate <= value_dict["max"]:
            period_code = key
            break
    return period_code


def get_measurement_code(measurement: str) -> str:
    sensor_code = "Y"
    for key, code in measurement_code_dict.items():
        if measurement.lower() in key:
            sensor_code = code
    return sensor_code


def get_orientation_code(azimuth: float, orientation: str = "horizontal") -> str:
    orientation_code = "1"
    horizontal_keys = ["N", "E", "1", "2"]
    vertical_keys = ["Z", "3"]

    azimuth = abs(azimuth) % 91
    if orientation == "horizontal":
        test_keys = horizontal_keys
    elif orientation == "vertical":
        test_keys = vertical_keys
    else:
        raise ValueError(
            f"{orientation} not supported must be [ 'horizontal' | 'vertical' ]"
        )

    for key in test_keys:
        angle_min = orientation_code_dict[key]["min"]
        angle_max = orientation_code_dict[key]["max"]
        if angle_min <= azimuth <= angle_max:
            orientation_code = key
            break

    return orientation_code


def make_channel_code(channel_obj: object) -> str:
    period_code = get_period_code(channel_obj.sample_rate)
    sensor_code = get_measurement_code(channel_obj.component)
    if sensor_code == "Y":
        sensor_code = get_measurement_code(channel_obj.type)

    if "z" in channel_obj.component.lower():
        orientation_code = get_orientation_code(
            channel_obj.measurement_tilt, orientation="vertical"
        )
    else:
        orientation_code = get_orientation_code(channel_obj.measurement_azimuth)

    return f"{period_code}{sensor_code}{orientation_code}"


def read_channel_code(channel_code: str) -> dict[str, dict[str, int] | str | bool]:
    if len(channel_code) != 3:
        msg = "Input FDSN channel code is not proper format, should be 3 letters"
        logger.error(msg)
        raise ValueError(msg)

    try:
        period_range = period_code_dict[channel_code[0].upper()]
    except KeyError:
        period_range = {"min": 1, "max": 1}

    try:
        component = measurement_code_dict_reverse[channel_code[1].upper()]
    except KeyError as error:
        msg = f"Could not find component for {channel_code[1]}"
        logger.error(msg)
        raise ValueError(msg) from error

    vertical = False
    try:
        orientation = orientation_code_dict[channel_code[2].upper()]
        if channel_code[2].upper() in ["3", "Z"]:
            vertical = True
    except KeyError as error:
        msg = f"Could not find orientation for {channel_code[2]}."
        logger.error(msg)
        raise ValueError(msg) from error

    return {
        "period": period_range,
        "component": component,
        "orientation": orientation,
        "vertical": vertical,
    }


def make_mt_channel(
    code_dict: dict[str, dict[str, int] | str | bool], angle_tol: int = 15
) -> str:
    component = code_dict["component"]
    orientation = code_dict["orientation"]
    vertical = code_dict["vertical"]

    mt_component = mt_code_dict.get(component, component)
    mt_dir = "z"

    if not vertical:
        if orientation["min"] >= 0 and orientation["max"] <= angle_tol:
            mt_dir = "x"
        elif orientation["min"] >= angle_tol and orientation["max"] <= 45:
            mt_dir = "1"
        elif orientation["min"] >= (90 - angle_tol) and orientation["max"] <= 90:
            mt_dir = "y"
        elif orientation["min"] >= 45 and orientation["max"] <= (90 - angle_tol):
            mt_dir = "2"
    else:
        if orientation["min"] >= 0 and orientation["max"] <= angle_tol:
            mt_dir = "z"
        elif orientation["min"] >= angle_tol and orientation["max"] <= 90:
            mt_dir = "3"

    return f"{mt_component}{mt_dir}"

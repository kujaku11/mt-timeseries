# mt-timeseries

mt-timeseries provides container classes for magnetotelluric (MT) time series
data with metadata-aware processing and conversion utilities.

The two primary classes are:

- ChannelTS: single-channel time series container backed by xarray.DataArray.
- RunTS: multi-channel run container backed by xarray.Dataset.

## Why use mt-timeseries

- Metadata-first design using mt_metadata Survey/Station/Run/Channel hierarchy.
- Time-indexed containers with automatic start/end/sample-rate handling.
- Channel and run slicing, merging, decimation, and resampling.
- Instrument response removal and calibration workflows.
- ObsPy conversion support for interoperable seismic/MT workflows.
- Plotting helpers for time series and spectra.

## Core data model

- ChannelTS stores one component (for example ex, ey, hx, hy, hz).
- RunTS stores many ChannelTS objects aligned on one time coordinate.
- Both classes keep metadata synchronized with the underlying xarray object.

## ChannelTS overview

ChannelTS is the main single-channel object for MT time series. It supports
electric, magnetic, and auxiliary channel types and stores data plus metadata in
one consistent object.

### Important functionality

- Accepts input from numpy arrays, pandas Series/DataFrames, or xarray.DataArray.
- Maintains synchronized metadata and data-array attributes.
- Supports instrument response handling via ChannelResponse.
- Supports calibration with response removal.
- Supports decimation/resampling and robust channel merging.
- Supports conversion to/from ObsPy Trace objects.

### Key attributes and properties

- ts: channel samples as numpy array.
- time_index: datetime index for samples.
- channel_type: electric, magnetic, or auxiliary.
- component: channel component code (for example ex, hy, temperature).
- sample_rate: samples per second.
- sample_interval: inverse of sample_rate.
- start: start time (MTime).
- end: end time (MTime, derived from data/time index).
- n_samples: number of samples.
- channel_response: filter chain used for calibration/response operations.
- channel_metadata, run_metadata, station_metadata, survey_metadata: metadata objects.

### Key methods

- copy(data=True): copy object with or without data.
- has_data(): check whether time series data are present.
- compute_sample_rate(): estimate sample rate from the time index.
- remove_instrument_response(...): calibrate by removing filter response stages.
- get_slice(start, end=None, n_samples=None): extract a time window.
- decimate(new_sample_rate, ...): multi-stage decimation.
- resample_poly(new_sample_rate, ...): polyphase FIR resampling.
- merge(other, gap_method=..., new_sample_rate=..., resample_method=...): merge one
  or more channel segments.
- to_xarray(): return xarray.DataArray with updated metadata attrs.
- to_obspy_trace(...): convert to ObsPy Trace.
- from_obspy_trace(trace): load from ObsPy Trace.
- plot(): quick time-series plot.
- welch_spectra(...): compute Welch PSD.
- plot_spectra(...): plot PSD.

## RunTS overview

RunTS is the multi-channel run container. It aligns channels on one time axis,
tracks run/station/survey metadata, and provides run-level processing.

### Important functionality

- Builds a run from ChannelTS objects, DataArrays, or an existing Dataset.
- Validates metadata consistency with dataset start/end/sample-rate.
- Aligns channels in time and fills/handles gaps during merges.
- Provides run-level calibration, decimation, and resampling.
- Converts complete runs to/from ObsPy Stream objects.
- Provides quick plotting of all channels and run spectra.

### Key attributes and properties

- dataset: xarray.Dataset containing all channel variables.
- channels: list of channel names present in the run.
- sample_rate: run sample rate inferred from data or metadata.
- sample_interval: inverse of sample_rate.
- start: run start time.
- end: run end time.
- filters: dictionary of response filters used by channels.
- run_metadata, station_metadata, survey_metadata: metadata objects.
- summarize_metadata: flattened dictionary of channel metadata attributes.

### Key methods

- set_dataset(array_list, align_type="outer"): build/replace run dataset from inputs.
- add_channel(channel): add one ChannelTS or DataArray to the run.
- validate_metadata(): synchronize and validate metadata against dataset.
- get_slice(start, end=None, n_samples=None): extract a time slice of the run.
- calibrate(...): calibrate all channels using each channel response.
- decimate(new_sample_rate, ...): decimate all channels.
- resample_poly(new_sample_rate, ...): polyphase FIR resampling of all channels.
- resample(new_sample_rate, ...): nearest-neighbor resampling.
- merge(other, gap_method=..., new_sample_rate=..., resample_method=...): merge runs.
- to_obspy_stream(...): convert run to ObsPy Stream.
- from_obspy_stream(stream, run_metadata=None): build run from ObsPy Stream.
- plot(...): multi-panel channel time-series plot.
- plot_spectra(...): multi-channel spectra plot.

## Minimal usage example

```python
import numpy as np

from mt_timeseries import ChannelTS, RunTS

# Build two electric channels
ex = ChannelTS(
    channel_type="electric",
    channel_metadata={"component": "ex", "sample_rate": 256.0},
)
ex.start = "2020-01-01T00:00:00+00:00"
ex.ts = np.random.randn(4096)

ey = ChannelTS(
    channel_type="electric",
    channel_metadata={"component": "ey", "sample_rate": 256.0},
)
ey.start = ex.start
ey.ts = np.random.randn(4096)

# Combine into a run
run = RunTS(array_list=[ex, ey])
print(run.channels)      # ['ex', 'ey']
print(run.sample_rate)   # 256.0

# Slice and resample
chunk = run.get_slice(start=run.start, n_samples=1024)
run_16hz = run.decimate(new_sample_rate=16.0)
```

## Notes

- Channel merge and run merge operations create monotonic time indices and
  interpolate gaps using a configurable method.
- For downsampling, decimate or resample_poly are preferred over simple
  nearest-neighbor resample to reduce aliasing risk.

## Installation

Install the latest release from PyPI:

```bash
pip install mt-timeseries
```

Install from source for local development:

```bash
git clone https://github.com/kujaku11/mt-timeseries.git
cd mt-timeseries
pip install -e .
```

Install with test dependencies:

```bash
pip install -e .[test]
```

## Contributing

Contributions are welcome and appreciated.

Typical workflow:

1. Fork the repository and create a feature branch.
2. Make focused changes with tests where appropriate.
3. Run the test suite locally.
4. Open a pull request against main with a clear description.

Run tests:

```bash
pytest tests
```

Useful development install:

```bash
pip install -e .[dev]
```

## Raising Issues

If you find a bug, have a feature request, or need clarification, open an issue
in the GitHub issue tracker.

Please include:

- What you expected to happen.
- What happened instead, including full error messages and tracebacks.
- A minimal reproducible example, if possible.
- Environment details: operating system, Python version, and package versions.

Issue tracker:

- https://github.com/kujaku11/mt-timeseries/issues



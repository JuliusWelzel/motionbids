# Inertial sensors — Movella DOT (`.xdf`)

Batch-converts Movella DOT IMU streams stored in XDF (LabStreamingLayer) files.

**This example shows how to:**

- Load XDF files with multiple streams using [`pyxdf`](https://github.com/xdf-modules/pyxdf)
- Detect the Movella DOT IMU stream automatically
- Compute the true sampling rate from timestamps (Movella reports a `0 Hz` nominal rate)
- Build `ACCEL` + `GYRO` channel metadata for each sensor
- Batch-process several subjects in a single run

!!! note "Requirements"
    ```bash
    pip install motionbids pyxdf numpy
    ```

```python title="examples/from_xdf_movella.py"
--8<-- "examples/from_xdf_movella.py"
```

## Next Steps

- [Vicon example](vicon-c3d.md) — optical marker conversion from C3D
- [Workflow Guide](../workflow.md) — step-by-step explanation of each stage
- [Class Reference](../class-reference.md) — `MotionData` and `Channel` API

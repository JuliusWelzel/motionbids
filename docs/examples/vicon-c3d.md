# Optical motion capture — Vicon (`.c3d`)

Converts 3D marker trajectories from a Vicon C3D recording into BIDS.

**This example shows how to:**

- Load a C3D file with [`ezc3d`](https://github.com/pyomeca/ezc3d)
- Read marker trajectories and the capture frame rate
- Convert marker units from millimetres (C3D default) to metres (BIDS)
- Build consistent `POS` channel metadata — one channel per marker and axis
- Validate, export, and plot a marker trajectory to sanity-check the result

!!! note "Requirements"
    ```bash
    pip install motionbids ezc3d numpy pandas matplotlib
    ```

```python title="examples/from_c3d_vicon.py"
--8<-- "examples/from_c3d_vicon.py"
```

## Next Steps

- [Movella DOT example](movella-xdf.md) — IMU conversion from XDF
- [Workflow Guide](../workflow.md) — step-by-step explanation of each stage
- [Class Reference](../class-reference.md) — `MotionData` and `Channel` API

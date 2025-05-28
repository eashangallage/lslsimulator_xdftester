
import pyxdf
import numpy as np

def verify_xdf_recording(xdf_filepath):
    """
    Loads an XDF file and verifies the integrity of the recorded LSL streams.

    Args:
        xdf_filepath (str): The path to the .xdf file to verify.
    """
    print(f"--- Verifying XDF file: {xdf_filepath} ---")

    try:
        # Load the XDF file
        # The output 'data' is a list of dictionaries, one for each stream.
        # 'header' contains global metadata, usually not needed for stream verification.
        streams, header = pyxdf.load_xdf(xdf_filepath)
        print(f"Successfully loaded {len(streams)} stream(s) from {xdf_filepath}\n")

    except Exception as e:
        print(f"Error loading XDF file: {e}")
        print("Please ensure the file path is correct and the .xdf file is not corrupted.")
        return

    expected_eeg_streams = {
        "EEG_Stream_1Hz": {"type": "EEG", "n_channels": 4, "srate": 1},
        "EEG_Stream_10Hz": {"type": "EEG", "n_channels": 8, "srate": 10},
        "EEG_Stream_250Hz": {"type": "EEG", "n_channels": 16, "srate": 250},
        "EEG_Stream_500Hz": {"type": "EEG", "n_channels": 32, "srate": 500},
    }
    expected_marker_stream = {
        "name": "Test_Markers", "type": "Markers", "n_channels": 1, "srate": 0
    }

    found_eeg_streams = {name: False for name in expected_eeg_streams}
    found_marker_stream = False

    for i, stream in enumerate(streams):
        stream_name = stream['info']['name'][0]
        stream_type = stream['info']['type'][0]
        n_channels = int(stream['info']['channel_count'][0])
        srate = float(stream['info']['nominal_srate'][0])
        # Data is in stream['time_series'] and timestamps in stream['time_stamps']
        time_series = stream['time_series']
        time_stamps = stream['time_stamps']

        print(f"--- Stream {i+1}: {stream_name} ---")
        print(f"  Type: {stream_type}")
        print(f"  Channels: {n_channels}")
        print(f"  Nominal Sample Rate: {srate} Hz")
        print(f"  Total Samples: {len(time_series)}")

        if len(time_series) > 0:
            print(f"  First 5 Samples (data):")
            # Handle potential non-uniform marker data
            if stream_type == "Markers":
                for j in range(min(5, len(time_series))):
                    print(f"    Sample {j+1}: {time_series[j]} @ {time_stamps[j]:.4f}")
            else: # Numeric data
                for j in range(min(5, len(time_series))):
                    # Ensure printing numeric data nicely, up to 5 channels
                    print(f"    Sample {j+1}: {time_series[j][:min(5, n_channels)]}... @ {time_stamps[j]:.4f}")
            print(f"  Last Sample (data): {time_series[-1]} @ {time_stamps[-1]:.4f}")

            # Basic check for actual sampling rate (approximate)
            if srate > 0 and len(time_stamps) > 1:
                actual_duration = time_stamps[-1] - time_stamps[0]
                if actual_duration > 0:
                    actual_srate = (len(time_stamps) - 1) / actual_duration
                    print(f"  Actual Sample Rate (approx): {actual_srate:.2f} Hz")
                    if abs(actual_srate - srate) / srate > 0.1: # Allow 10% deviation
                        print(f"  WARNING: Actual sample rate differs significantly from nominal for {stream_name}.")
                else:
                    print("  Warning: Stream duration is zero or has only one sample.")
            elif srate == 0 and len(time_series) > 1: # For markers, check irregularity
                interval_std = np.std(np.diff(time_stamps))
                print(f"  Marker Interval Std Dev: {interval_std:.4f}s (indicates irregularity if > 0)")


        # --- Specific checks for our simulated streams ---
        if stream_name in expected_eeg_streams:
            expected = expected_eeg_streams[stream_name]
            if (stream_type == expected["type"] and
                n_channels == expected["n_channels"] and
                srate == expected["srate"]):
                print(f"  [VERIFIED]: Matches expected EEG stream configuration for {stream_name}.")
                found_eeg_streams[stream_name] = True
            else:
                print(f"  [MISMATCH]: {stream_name} properties do not match expected configuration.")
        elif stream_name == expected_marker_stream["name"]:
            expected = expected_marker_stream
            if (stream_type == expected["type"] and
                n_channels == expected["n_channels"] and
                srate == expected["srate"]):
                print(f"  [VERIFIED]: Matches expected Marker stream configuration.")
                found_marker_stream = True
            else:
                print(f"  [MISMATCH]: {stream_name} properties do not match expected configuration.")
        else:
            print(f"  [INFO]: This stream ({stream_name}) is not one of the expected simulated streams.")

        print("-" * 40)

    print("\n--- Summary of Verification ---")
    all_expected_found = True
    for name, found in found_eeg_streams.items():
        if found:
            print(f"✓ Found and verified expected EEG stream: {name}")
        else:
            print(f"✗ MISSING or MISCONFIGURED expected EEG stream: {name}")
            all_expected_found = False

    if found_marker_stream:
        print(f"✓ Found and verified expected Marker stream: {expected_marker_stream['name']}")
    else:
        print(f"✗ MISSING or MISCONFIGURED expected Marker stream: {expected_marker_stream['name']}")
        all_expected_found = False

    if all_expected_found:
        print("\nAll expected simulated streams were found and verified with their basic properties.")
        print("This suggests LabRecorder successfully captured all streams as intended!")
    else:
        print("\nSome expected streams were missing or misconfigured. Review the output for details.")
        print("This might indicate an issue with LabRecorder's recording or stream generation.")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    # --- IMPORTANT: CHANGE THIS TO YOUR XDF FILE PATH ---
    # Example: xdf_file = "my_recorded_data.xdf"
    # Or provide the full path: xdf_file = "/home/eashan/Documents/my_recordings/data.xdf"
    xdf_file_to_check = "my_recorded_streams.xdf" # <--- EDIT THIS LINE

    # Call the verification function
    verify_xdf_recording(xdf_file_to_check)
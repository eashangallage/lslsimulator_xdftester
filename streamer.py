import time
import random
import threading
from pylsl import StreamInfo, StreamOutlet

# --- Configuration for EEG Streams ---
eeg_stream_configs = [
    {"name": "EEG_Stream_1Hz", "type": "EEG", "n_channels": 4, "srate": 1, "amplitude": 50},
    {"name": "EEG_Stream_10Hz", "type": "EEG", "n_channels": 8, "srate": 10, "amplitude": 100},
    {"name": "EEG_Stream_250Hz", "type": "EEG", "n_channels": 16, "srate": 250, "amplitude": 200},
    {"name": "EEG_Stream_500Hz", "type": "EEG", "n_channels": 32, "srate": 500, "amplitude": 400},
]

# --- Configuration for Marker Stream ---
marker_stream_config = {
    "name": "Test_Markers",
    "type": "Markers",
    "n_channels": 1,
    "srate": 0,  # Irregularly sampled
    "marker_interval_ms": [500, 2000], # Min and max interval for markers
    "marker_types": ["Onset", "Stimulus", "Response", "Error", "Event_A", "Event_B"],
}

# --- Global stop event for threads ---
stop_event = threading.Event()

def create_eeg_stream(config):
    """Creates and streams simulated EEG data."""
    info = StreamInfo(
        config["name"],
        config["type"],
        config["n_channels"],
        config["srate"],
        'float32',
        config["name"].lower().replace(" ", "") + "_uid"
    )
    outlet = StreamOutlet(info)
    print(f"[{config['name']}] LSL stream created with {config['n_channels']} channels at {config['srate']} Hz.")

    sample_count = 0
    while not stop_event.is_set():
        # Simulate EEG data (simple sine wave + random noise)
        sample = [
            config["amplitude"] * (random.uniform(-0.5, 0.5) + 0.2 * (sample_count % (config["srate"] * 2)) / config["srate"])
            for _ in range(config["n_channels"])
        ]
        outlet.push_sample(sample)
        sample_count += 1
        time.sleep(1.0 / config["srate"])
    print(f"[{config['name']}] Stream stopped.")

def create_marker_stream(config):
    """Creates and streams random markers."""
    info = StreamInfo(
        config["name"],
        config["type"],
        config["n_channels"],
        config["srate"],
        'string',
        config["name"].lower().replace(" ", "") + "_uid"
    )
    outlet = StreamOutlet(info)
    print(f"[{config['name']}] LSL stream created.")

    while not stop_event.is_set():
        marker = random.choice(config["marker_types"])
        outlet.push_sample([marker])
        print(f"[{config['name']}] Sent marker: {marker}")
        sleep_time = random.uniform(config["marker_interval_ms"][0], config["marker_interval_ms"][1]) / 1000.0
        time.sleep(sleep_time)
    print(f"[{config['name']}] Stream stopped.")

if __name__ == "__main__":
    threads = []

    # Start EEG streams
    for config in eeg_stream_configs:
        thread = threading.Thread(target=create_eeg_stream, args=(config,))
        threads.append(thread)
        thread.start()

    # Start Marker stream
    marker_thread = threading.Thread(target=create_marker_stream, args=(marker_stream_config,))
    threads.append(marker_thread)
    marker_thread.start()

    print("\nAll LSL streams started. Press Ctrl+C to stop...\n")

    try:
        while True:
            time.sleep(1) # Keep main thread alive
    except KeyboardInterrupt:
        print("\nStopping all LSL streams...")
        stop_event.set() # Signal threads to stop
        for thread in threads:
            thread.join() # Wait for all threads to finish
        print("All LSL streams stopped.")
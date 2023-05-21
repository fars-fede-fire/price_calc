import datetime
import json
import os
import numpy as np

def prepare_data(manufactor, model, type, mode, method, history_data):
	"""Creates a .json file based on sensor history."""
    # Count the number of objects in the list
	count = len(history_data)

	states = np.array([float(d['state']) for d in history_data])
	timestamps = np.array([datetime.datetime.fromisoformat(item['last_changed']) for item in history_data])
	# Calculate the differences between adjacent states
	state_deltas = np.diff(states)
	state_deltas_as_list = state_deltas.tolist()
	time_deltas = np.diff(timestamps)
	max_time_delta = np.max(time_deltas)
	min_time_delta = np.min(time_deltas)
	mean_time_delta = (np.mean(time_deltas)).total_seconds()
	duration_in_minutes = (timestamps[-1] - timestamps[0]).total_seconds() // 60

	data_dir = f"{os.path.dirname(__file__)}/data"
	file_name = f"{manufactor}_{model}_{mode}"
	file_path = f"{data_dir}/{file_name}".lower()

	data_as_json = {
		"appliance_type": type,
		"appliance_manufactor": manufactor,
		"appliance_model": model,
		"appliance_mode": mode,
		"measure_method": method,
		"duration_in_minutes": int(duration_in_minutes),
		"energy_use_resolution_in_seconds": int(mean_time_delta),
		"energy_usage": state_deltas_as_list
	}


	if os.path.exists(f"{file_path}.json"):
		file_path_incrementor = 1
		file_path_mod = file_path
		while os.path.exists(f"{file_path_mod}.json"):
			file_path_mod = f"{file_path}_{file_path_incrementor}"
			file_path_incrementor += 1
		file_path = file_path_mod


	with open(f"{file_path}.json", "w", encoding='utf-8') as file:
		file.write(json.dumps(data_as_json))

	return f"{file_path}.json"
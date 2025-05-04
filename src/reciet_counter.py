import json
import os

def get_next_receipt_number(filename="receipt_counter.json"):
    """
    Retrieves the next receipt number, initializing the counter if the file
    doesn't exist.

    Args:
        filename (str, optional): The name of the file to store the counter.
                                     Defaults to "receipt_counter.json".

    Returns:
        int: The next receipt number.
    """
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({"receipt_number": 1}, f)  # Initialize to 1 for the first receipt
        return 1
    else:
        with open(filename, 'r+') as f:
            try:
                data = json.load(f)
                current_number = data.get("receipt_number", 1)
                next_number = current_number + 1
                f.seek(0)
                json.dump({"receipt_number": next_number}, f)
                f.truncate()
                return next_number
            except json.JSONDecodeError:
                # Handle potential file corruption by resetting the counter
                with open(filename, 'w') as f:
                    json.dump({"receipt_number": 1}, f)
                return 1


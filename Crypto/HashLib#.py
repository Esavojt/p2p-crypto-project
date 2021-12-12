import hashlib
import time

class Block:

    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp or time.time()

    @property
    def calculate_hash(self):
        block_of_string = "{}{}{}{}{}".format(self.index, self.proof_no,
                                              self.prev_hash, self.data,
                                              self.timestamp)

        return hashlib.sha256(block_of_string.encode()).hexdigest()

    def __repr__(self):
        return "{} - {} - {} - {} - {}".format(self.index, self.proof_no,
                                               self.prev_hash, self.data,
                                               self.timestamp)
    

    {
    "index": 2,
    "proof": 21,
    "prev_hash": "6e27587e8a27d6fe376d4fd9b4edc96c8890346579e5cbf558252b24a8257823",
    "transactions": [
        {'sender': '0', 'recipient': 'Quincy Larson', 'quantity': 1}
    ],
    "timestamp": 1521646442.4096143
}
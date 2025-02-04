import json
import sys
from copy import deepcopy

config_flag = "c"
input_flag = "i"
output_flag = "o"

class Enigma:
    def __init__(self, map_hash, wheels, map_reflector):
        self.map_hash = map_hash
        self.wheels = wheels
        self.map_reflector = map_reflector
        self.initial_wheels = deepcopy(wheels)
        self.swapped_map_hash = {v: k for k, v in map_hash.items()}

    def reset_wheels(self):
        self.wheels = deepcopy(self.initial_wheels)

    def encrypt_char(self, char):
        if not char.islower():
            return char

        value = (2 * self.wheels[0] - self.wheels[1] + self.wheels[2]) % 26

        i = self.map_hash[char]

        i = i + 1 if value == 0 else i + value

        i = i % 26

        c1 = self.swapped_map_hash[i]

        c2 = self.map_reflector[c1]

        i = self.map_hash[c2]

        i = i - 1 if value == 0 else i - value

        i = i % 26

        return self.swapped_map_hash[i]

    def advance_wheels(self, pos):
        self.wheels[0] += 1
        if self.wheels[0] > 8:
            self.wheels[0] = 1

        if pos % 2 == 0:
            self.wheels[1] *= 2
        else:
            self.wheels[1] -= 1

        if pos % 10 == 0:
            self.wheels[2] = 10
        elif pos % 3 == 0:
            self.wheels[2] = 5
        else:
            self.wheels[2] = 0

    def encrypt(self, message):
        encrypted_message = []
        encrypted_chars = 0

        for char in message:
            encrypted_char = self.encrypt_char(char)
            encrypted_message.append(encrypted_char)
            encrypted_chars += encrypted_char.islower()
            self.advance_wheels(encrypted_chars)

        self.reset_wheels()
        return ''.join(encrypted_message)

class JSONFileError(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

def load_enigma_from_path(json_path):
    try :
        with open(json_path, 'r') as file:
            data = json.load(file)
            map_hash = data['hash_map']
            wheels = data['wheels']
            map_reflector = data['reflector_map']
            return Enigma(map_hash, wheels, map_reflector)
    except Exception:
        raise JSONFileError("The enigma script has encountered an error")

def main():
    args_dict = {}
    for i in range(1, len(sys.argv), 2):
        key = sys.argv[i].strip('-')
        if key not in [config_flag, input_flag, output_flag]:
            print("Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>")
            sys.exit(1)
        value = sys.argv[i + 1]
        args_dict[key] = value

    config_file = args_dict.get(config_flag)
    input_file = args_dict.get(input_flag)
    output_file = args_dict.get(output_flag)

    if not config_file or not input_file:
        print("Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>")
        sys.exit(1)

    encrypted_messages = []
    try:
        enigma = load_enigma_from_path(config_file)
        with open(input_file, 'r') as input:
            for line in input:
                encrypted_messages.append(enigma.encrypt(line))
    except Exception:
        print("The enigma script has encountered an error")
        sys.exit(1)

    if output_file:
        try:
            with open(output_file, 'w') as file:
                for encrypted_message in encrypted_messages:
                    file.write(encrypted_message + '\n')
        except Exception:
            print("The enigma script has encountered an error")
            sys.exit(1)
    else:
        for encrypted_message in encrypted_messages:
            print(encrypted_message)

if __name__ == "__main__":
    main()
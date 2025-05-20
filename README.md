# Heimdal - Directory Encryption Tool

[English](README.md) | [日本語](README_ja.md)

Heimdal is a tool that converts an entire directory into a single encrypted file.
It has the following features:

- Encrypts a specified directory into a single .hmd file using AES-CBC 256bit.
- Decrypts a .hmd file back into a directory.
- Encryption using a key file or password.
- Key file generation from a password or random generation.

## Usage Examples

```sh
# Install
$ pip install git+https://github.com/mallocfree009/heimdal.git

# Encrypt testdata directory using only a password
$ heimdal encode testdata testdata2.hmd                  
Enter password: 
Confirm password:
Generated IV and Key from password.
Directory 'testdata' compressed to 'testdata.temp.zip'.
Data encrypted and saved to 'testdata2.hmd'.

# Decrypt testdata2.hmd file using only a password
$ heimdal decode testdata2.hmd output2   
Enter password: 
Confirm password:
Generated Key from password.
Zip file 'testdata2.hmd.temp.zip' extracted to 'output2'.

# Generate a key file from a password
$ heimdal genkey test_key_pass.json
Enter password: 
Confirm password:
Generated IV and Key from password.
Generated IV and Key and saved to 'test_key_pass.json' in JSON format.

# Or, generate a key file randomly without using a password
$ heimdal genkey --random test_key.json

# Encrypt testdata directory to testdata.hmd file using a key file
$ heimdal encode -k test_key.json testdata testdata.hmd 

# Decrypt from testdata.hmd file to output directory using a key file
$ heimdal decode -k test_key.json testdata.hmd output
```

---

## Usage

### Installation

You can install this tool using the following command:

```bash
pip install git+https://github.com/mallocfree009/heimdal.git
```

### Basic Usage

After installation, you can run it as the `heimdal` command.

```bash
heimdal <command> [options]
```

Available commands are `encode`, `decode`, and `genkey`.

### `encode` Command

Compresses a file or directory using Zip and encrypts it with AES-CBC 256bit.

```bash
python heimdal.py encode <input_path> <output_file_path> [-k <key_file_path>]
```

- `<input_path>`: Specifies the path to the file or directory you want to encrypt.
- `<output_file_path>`: Specifies the output path for the encrypted `.hmd` file.
- `-k <key_file_path>`, `--key <key_file_path>` (Optional): Specifies the path to a JSON file containing the IV and Key to be used for encryption. If this option is not specified, you will be prompted for a password, and the IV and Key will be generated from the password.

**Examples:**

Encrypting a directory with a password:
```bash
heimdal encode /path/to/your_directory /path/to/output.hmd
```

Encrypting a file with a password:
```bash
heimdal encode /path/to/your_file /path/to/output.hmd
```

Encrypting a directory with a key file:
```bash
heimdal encode /path/to/your_directory /path/to/output.hmd -k /path/to/your_key.json
```

Encrypting a file with a key file:
```bash
heimdal encode /path/to/your_file /path/to/output.hmd -k /path/to/your_key.json
```

### `decode` Command

Decrypts an encrypted `.hmd` file and restores the original file or directory.

```bash
python heimdal.py decode <input_file_path> <output_path> [-k <key_file_path>]
```

- `<input_file_path>`: Specifies the path to the `.hmd` file you want to decrypt.
- `<output_path>`: Specifies the output path for the decrypted file or directory. If the original data was a directory, a directory will be created at the specified path and its contents extracted there. If the original data was a single file, it will be output as a file at the specified path (if the output path ends with a directory, the file will be created with the base name of the input file, excluding the extension).
- `-k <key_file_path>`, `--key <key_file_path>` (Optional): Specifies the path to a JSON file containing the Key to be used for decryption. If this option is not specified, you will be prompted for a password, and the Key will be generated from the Salt in the file and the password. The IV is always read from the `.hmd` file.

**Examples:**

Decrypting a password-encrypted file to a directory:
```bash
heimdal decode /path/to/input.hmd /path/to/output_directory
```

Decrypting a password-encrypted file to a file:
```bash
heimdal decode /path/to/input.hmd /path/to/output_file
```

Decrypting a key file-encrypted file to a directory:
```bash
heimdal decode /path/to/input.hmd /path/to/output_directory -k /path/to/your_key.json
```

Decrypting a key file-encrypted file to a file:
```bash
heimdal decode /path/to/input.hmd /path/to/output_file -k /path/to/your_key.json
```

### `genkey` Command

Generates the IV and Key to be used for encryption and decryption, and outputs them in JSON format.

```bash
python heimdal.py genkey <output_file_path> [--random]
```

- `<output_file_path>`: Specifies the path to the JSON file where the generated IV and Key will be saved.
- `--random` (Optional): If this option is specified, random IV and Key will be generated instead of using a password. If not specified, you will be prompted for a password, and the IV and Key will be derived from the password.

**Examples:**

Generating IV and Key from a password:
```bash
heimdal genkey /path/to/your_key.json
```

Generating random IV and Key:
```bash
heimdal genkey /path/to/your_key.json --random
```

### Key File Format

The JSON file generated by the `genkey` command has the following format. The IV and Key are Base64 encoded.

```json
{
  "iv": "...",
  "key": "..."
}
```

Please store this file securely. Especially for key files generated with the `--random` option, it is essential for decryption.
```

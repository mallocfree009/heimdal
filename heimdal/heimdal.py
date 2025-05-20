import argparse
import os
import zipfile
import shutil
import getpass
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import padding

# 定数
SALT_SIZE = 16
IV_SIZE = 16
KEY_SIZE = 32 # AES-256
ITERATIONS = 100000 # PBKDF2 iterations

def get_password():
    """パスワードを安全に入力させる"""
    while True:
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        if password == password_confirm:
            return password.encode('utf-8')
        else:
            print("Passwords do not match.")

def derive_key(password, salt):
    """パスワードとソルトから鍵を導出する"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password)

def encrypt_data(data, password):
    """データをAES-CBCで暗号化する"""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    iv = os.urandom(IV_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # PKCS7パディングを適用
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return salt, iv, ciphertext

def decrypt_data(encrypted_data, password, salt, iv):
    """データをAES-CBCで復号化する"""
    key = derive_key(password, salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(encrypted_data) + decryptor.finalize()

    # パディングを解除
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext

def load_key_iv_from_json(key_file_path):
    """JSONファイルからBase64エンコードされたIVとKeyを読み込み、デコードする"""
    try:
        with open(key_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        iv_b64 = data.get("iv")
        key_b64 = data.get("key")

        if not iv_b64 or not key_b64:
            raise ValueError("JSONファイルに 'iv' または 'key' フィールドが見つかりません。")

        iv = base64.b64decode(iv_b64)
        key = base64.b64decode(key_b64)

        if len(iv) != IV_SIZE or len(key) != KEY_SIZE:
             raise ValueError("Invalid IV or Key size in JSON file.")

        print(f"Loaded IV and Key from '{key_file_path}'.")
        return key, iv

    except FileNotFoundError:
        print(f"Error: Key file '{key_file_path}' not found.")
        raise
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in key file '{key_file_path}'.")
        raise
    except ValueError as e:
        print(f"Error: Invalid key file content: {e}")
        raise
    except Exception as e:
        print(f"Error loading key file: {e}")
        raise


def encrypt_data(data, key, iv):
    """データをAES-CBCで暗号化する (KeyとIVを直接使用)"""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # PKCS7パディングを適用
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext

def decrypt_data(encrypted_data, key, iv):
    """データをAES-CBCで復号化する (KeyとIVを直接使用)"""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(encrypted_data) + decryptor.finalize()

    # パディングを解除
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext


def genkey_command(args):
    """genkey サブコマンドの処理"""
    output_path = args.output_path
    use_random = args.random

    try:
        if use_random:
            # ランダムなIVとKeyを生成
            key = os.urandom(KEY_SIZE)
            iv = os.urandom(IV_SIZE)
            print("Generated random IV and Key.")
        else:
            # パスワードからSalt, Key, IVを導出
            password = get_password()
            salt = os.urandom(SALT_SIZE) # SaltはKey導出にのみ使用
            key = derive_key(password, salt)
            iv = os.urandom(IV_SIZE)
            print("Generated IV and Key from password.")

        # IVとKeyをBase64エンコード
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        key_b64 = base64.b64encode(key).decode('utf-8')

        # JSONデータ構造を作成
        output_data = {
            "iv": iv_b64,
            "key": key_b64
        }

        # JSONファイルとして出力
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)

        print(f"Generated IV and Key and saved to '{output_path}' in JSON format.")

    except Exception as e:
        print(f"Error during key generation: {e}")


def zip_directory(directory_path, output_zip_path):
    """ディレクトリをZip圧縮する"""
    try:
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Zipファイル内のパスは、元のディレクトリからの相対パスにする
                    arcname = os.path.relpath(file_path, directory_path)
                    zipf.write(file_path, arcname)
        print(f"Directory '{directory_path}' compressed to '{output_zip_path}'.")
    except Exception as e:
        print(f"Error during Zip compression: {e}")
        raise

def extract_zip(zip_path, output_directory):
    """Zipファイルを指定ディレクトリに展開する"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(output_directory)
        print(f"Zip file '{zip_path}' extracted to '{output_directory}'.")
    except Exception as e:
        print(f"Error during Zip extraction: {e}")
        raise

def is_zip_file(data):
    """データがZipファイル形式かどうかを判定する (マジックナンバーを確認)"""
    # Zipファイルのマジックナンバーは PK\x03\x04
    return data.startswith(b'PK\x03\x04')

def encode_command(args):
    """encode サブコマンドの処理"""
    input_path = args.input_path
    output_path = args.output_path
    key_file_path = args.key

    if not os.path.exists(input_path):
        print(f"Error: Input path '{input_path}' does not exist.")
        return

    key = None
    iv = None
    salt = None # ファイル形式互換性のために常に生成

    try:
        if key_file_path:
            # 鍵ファイルからKeyとIVを読み込む
            key, iv = load_key_iv_from_json(key_file_path)
            salt = os.urandom(SALT_SIZE) # ファイル形式互換性のためにランダムなSaltを生成
        else:
            # パスワードからKeyとIVを導出
            password = get_password()
            salt = os.urandom(SALT_SIZE)
            key = derive_key(password, salt)
            iv = os.urandom(IV_SIZE)
            print("Generated IV and Key from password.")

        temp_data_path = None
        data_to_encrypt = None

        if os.path.isdir(input_path):
            # ディレクトリの場合、一時Zipファイルを作成
            temp_data_path = input_path + ".temp.zip"
            zip_directory(input_path, temp_data_path)
            with open(temp_data_path, 'rb') as f:
                data_to_encrypt = f.read()
        elif os.path.isfile(input_path):
            # ファイルの場合、そのまま読み込む
            with open(input_path, 'rb') as f:
                data_to_encrypt = f.read()
        else:
            print(f"Error: Input path '{input_path}' is neither a file nor a directory.")
            return

        if data_to_encrypt is None:
             print("Error: No data to encrypt.")
             return

        # データを暗号化
        ciphertext = encrypt_data(data_to_encrypt, key, iv)

        # ソルト、IV、暗号化データを連結して出力ファイルに書き込む
        with open(output_path, 'wb') as f:
            f.write(salt)
            f.write(iv)
            f.write(ciphertext)

        print(f"Data encrypted and saved to '{output_path}'.")

    except Exception as e:
        print(f"Error during encoding: {e}")
    finally:
        # 一時Zipファイルがあれば削除
        if temp_data_path and os.path.exists(temp_data_path):
            os.remove(temp_data_path)

def decode_command(args):
    """decode サブコマンドの処理"""
    input_path = args.input_path
    output_path = args.output_path
    key_file_path = args.key

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        return

    key = None
    salt = None
    iv = None
    ciphertext = None

    try:
        # ファイルからソルト、IV、暗号化データを読み込む
        with open(input_path, 'rb') as f:
            salt = f.read(SALT_SIZE)
            iv = f.read(IV_SIZE)
            ciphertext = f.read()

        if len(salt) != SALT_SIZE or len(iv) != IV_SIZE:
             print("Error: Invalid input file format.")
             return

        if key_file_path:
            # 鍵ファイルからKeyを読み込む (IVはファイルから読み込んだものを使用)
            loaded_key, _ = load_key_iv_from_json(key_file_path)
            key = loaded_key
            # Saltはファイルから読み込むが、鍵導出には使用しない
            print("Loaded Key from key file.")
        else:
            # パスワードとファイルから読み込んだSaltからKeyを導出
            password = get_password()
            key = derive_key(password, salt)
            print("Generated Key from password.")

        # データを復号化
        plaintext_data = decrypt_data(ciphertext, key, iv)

        # 復号化されたデータがZip形式かどうか判定
        if is_zip_file(plaintext_data):
            # Zip形式の場合、一時ファイルに書き出し、展開
            temp_zip_path = input_path + ".temp.zip"
            try:
                with open(temp_zip_path, 'wb') as f:
                    f.write(plaintext_data)
                # 出力ディレクトリが存在しない場合は作成
                os.makedirs(output_path, exist_ok=True)
                extract_zip(temp_zip_path, output_path)
            finally:
                # 一時Zipファイルがあれば削除
                if os.path.exists(temp_zip_path):
                    os.remove(temp_zip_path)
        else:
            # Zip形式でない場合、そのまま出力ファイルに書き込む
            # 出力パスがディレクトリで終わっている場合は、入力ファイル名を使用
            if os.path.isdir(output_path):
                 # 元のファイル名が不明なため、入力ファイル名から拡張子を除いたものを使用
                 base_name = os.path.basename(input_path)
                 # '.hmd' などの拡張子を削除する簡単な処理
                 if base_name.endswith('.hmd'):
                     base_name = base_name[:-len('.hmd')]
                 output_file_path = os.path.join(output_path, base_name)
            else:
                 output_file_path = output_path

            # 出力ディレクトリが存在しない場合は作成
            output_dir = os.path.dirname(output_file_path)
            if output_dir: # output_file_pathがファイル名のみの場合はディレクトリ作成不要
                os.makedirs(output_dir, exist_ok=True)

            with open(output_file_path, 'wb') as f:
                f.write(plaintext_data)
            print(f"Data decrypted and saved to '{output_file_path}'.")

    except InvalidSignature:
         print("Error: Incorrect password or corrupted file.")
    except InvalidTag: # GCMモードなどで使用されるが、CBCでは発生しない可能性。念のため。
         print("Error: Incorrect password or corrupted file.")
    except Exception as e:
        print(f"Error during decoding: {e}")


def main():
    parser = argparse.ArgumentParser(description="File/Directory Zip Compression and AES Encryption Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # encode サブコマンド
    encode_parser = subparsers.add_parser("encode", help="Compress and encrypt a file or directory")
    encode_parser.add_argument("input_path", help="Path to the input file or directory")
    encode_parser.add_argument("output_path", help="Output file path")
    encode_parser.add_argument("-k", "--key", help="Path to a JSON file containing IV and Key")
    encode_parser.set_defaults(func=encode_command)

    # decode サブコマンド
    decode_parser = subparsers.add_parser("decode", help="Decrypt and extract an encrypted file")
    decode_parser.add_argument("input_path", help="Path to the input file (encrypted file)")
    decode_parser.add_argument("output_path", help="Output path (file or directory)")
    decode_parser.add_argument("-k", "--key", help="Path to a JSON file containing the Key")
    decode_parser.set_defaults(func=decode_command)

    # genkey サブコマンド
    genkey_parser = subparsers.add_parser("genkey", help="Generate IV and Key and output in JSON format")
    genkey_parser.add_argument("output_path", help="Output file path (JSON format)")
    genkey_parser.add_argument("--random", action="store_true", help="Generate random IV and Key instead of using a password")
    genkey_parser.set_defaults(func=genkey_command)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

# if __name__ == "__main__":
#     main()

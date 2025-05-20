# Heimdal - ディレクトリ暗号化ツール

Heimdalはディレクトリ全体を１つの暗号化されたファイルに変換するツールです。
以下の機能があります

- ディレクトリを指定してディレクトリ全体をAES-CBC 256bitで暗号化された1つの.hmdファイルにする
- .hmdファイルを復号してディレクトリに戻す
- キーファイルまたはパスワードによる暗号化
- キーファイルのパスワードからの生成、またはランダム生成

---

## 使い方

### インストール

以下のコマンドでインストールできます。

```bash
pip install git+https://github.com/mallocfree009/heimdal.git
```

### 基本的な使い方

インストール後、`heimdal` コマンドとして実行できます。

```bash
heimdal <command> [options]
```

利用可能なコマンドは `encode`, `decode`, `genkey` です。

### `encode` コマンド

ファイルまたはディレクトリをZip圧縮し、AES-CBC 256bitで暗号化します。

```bash
python heimdal.py encode <入力パス> <出力ファイルパス> [-k <鍵ファイルパス>]
```

- `<入力パス>`: 暗号化したいファイルまたはディレクトリのパスを指定します。
- `<出力ファイルパス>`: 暗号化された `.hmd` ファイルの出力先パスを指定します。
- `-k <鍵ファイルパス>`, `--key <鍵ファイルパス>` (オプション): 暗号化に使用するIVとKeyを含むJSONファイルのパスを指定します。このオプションを指定しない場合、パスワードの入力が求められ、パスワードからIVとKeyが生成されます。

**例:**

ディレクトリをパスワードで暗号化する場合:
```bash
heimdal encode /path/to/your_directory /path/to/output.hmd
```

ファイルをパスワードで暗号化する場合:
```bash
heimdal encode /path/to/your_file /path/to/output.hmd
```

ディレクトリを鍵ファイルで暗号化する場合:
```bash
heimdal encode /path/to/your_directory /path/to/output.hmd -k /path/to/your_key.json
```

ファイルを鍵ファイルで暗号化する場合:
```bash
heimdal encode /path/to/your_file /path/to/output.hmd -k /path/to/your_key.json
```

### `decode` コマンド

暗号化された `.hmd` ファイルを復号化し、元のファイルまたはディレクトリに戻します。

```bash
python heimdal.py decode <入力ファイルパス> <出力先パス> [-k <鍵ファイルパス>]
```

- `<入力ファイルパス>`: 復号化したい `.hmd` ファイルのパスを指定します。
- `<出力先パス>`: 復号化されたファイルまたはディレクトリの出力先パスを指定します。元のデータがディレクトリだった場合は、指定したパスにディレクトリが作成され、その中に内容が展開されます。元のデータが単一ファイルだった場合は、指定したパスにファイルとして出力されます（出力パスがディレクトリで終わっている場合は、入力ファイル名から拡張子を除いた名前でファイルが作成されます）。
- `-k <鍵ファイルパス>`, `--key <鍵ファイルパス>` (オプション): 復号化に使用するKeyを含むJSONファイルのパスを指定します。このオプションを指定しない場合、パスワードの入力が求められ、ファイル内のSaltとパスワードからKeyが生成されます。IVは常に `.hmd` ファイルから読み込まれます。

**例:**

パスワードで暗号化されたファイルをディレクトリに復号化する場合:
```bash
heimdal decode /path/to/input.hmd /path/to/output_directory
```

パスワードで暗号化されたファイルをファイルに復号化する場合:
```bash
heimdal decode /path/to/input.hmd /path/to/output_file
```

鍵ファイルで暗号化されたファイルをディレクトリに復号化する場合:
```bash
heimdal decode /path/to/input.hmd /path/to/output_directory -k /path/to/your_key.json
```

鍵ファイルで暗号化されたファイルをファイルに復号化する場合:
```bash
heimdal decode /path/to/input.hmd /path/to/output_file -k /path/to/your_key.json
```

### `genkey` コマンド

暗号化・復号化に使用するIVとKeyを生成し、JSON形式で出力します。

```bash
python heimdal.py genkey <出力ファイルパス> [--random]
```

- `<出力ファイルパス>`: 生成されたIVとKeyを保存するJSONファイルのパスを指定します。
- `--random` (オプション): このオプションを指定すると、パスワードを使用せずランダムなIVとKeyを生成します。指定しない場合、パスワードの入力が求められ、パスワードからIVとKeyが導出されます。

**例:**

パスワードからIVとKeyを生成する場合:
```bash
heimdal genkey /path/to/your_key.json
```

ランダムなIVとKeyを生成する場合:
```bash
heimdal genkey /path/to/your_key.json --random
```

### 鍵ファイル形式

`genkey` コマンドで生成されるJSONファイルは以下の形式です。IVとKeyはBase64エンコードされています。

```json
{
  "iv": "...",
  "key": "..."
}
```

このファイルは安全に保管してください。特に `--random` オプションで生成した鍵ファイルは、復号化に必須となります。
```

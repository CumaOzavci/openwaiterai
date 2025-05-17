# OpenWaiterai

## 1. Installation
```
# Clone repository
git clone https://github.com/CumaOzavci/openwaiterai.git
cd openwaiterai

# Create python environment
python -m venv .venv
source .venv/activate/bin

# Install dependencies
pip install -r requirements.txt
```

## 2. Setting environment variables
```
export OPENAI_API_KEY="openai_key"
export OPENWAITERAI_DB_HOST="localhost"
export OPENWAITERAI_DB_PORT="5432"
export OPENWAITERAI_DB_NAME="openwaiteraidb_name"
export OPENWAITERAI_DB_USER="openwaiterai_username"
export OPENWAITERAI_DB_PASSWORD="openwaiterai_password"

# Optional
export OPENWAITERAI_QUERY_TIMEOUT=30
export OPENWAITERAI_POLL_INTERVAL=1
```

## 3. Running
```
python tests/test_cli.py
```

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

## 3. Test
```
python tests/test_cli.py
```

## Devlogs:
1. [OpenwaiterAI Devlog #0: Introduction](https://cumaozavci.github.io/ai/openwaiterai/2024/11/18/openwaiterai_0_introduction.html)
2. [OpenwaiterAI Devlog #1: Instructions](https://cumaozavci.github.io/ai/openwaiterai/2024/12/09/openwaiterai_1_instructions.html)
3. [OpenwaiterAI Devlog #2: Retrieval Augmented Generation](https://cumaozavci.github.io/ai/openwaiterai/rag/2025/02/17/openwaiterai_2_rag.html)
4. [OpenwaiterAI Devlog #3: Finishing Tools and System Message](https://cumaozavci.github.io/ai/openwaiterai/rag/2025/05/17/openwaiterai_3_finishing.html)
#!/bin/bash

# 現在の場所を記録
CURRENT_DIR=$(pwd)

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# アプリケーションのディレクトリに移動
cd "$SCRIPT_DIR"

# 仮想環境の存在をチェック
#if [ ! -d "venv" ]; then
#  echo "仮想環境を作成しています..."
#  python3 -m venv venv
#  source venv/bin/activate
#  pip install -r requirements.txt
#else
#  source venv/bin/activate
#fi

# .envファイルの存在をチェック
if [ ! -f ".env" ]; then
  echo ".envファイルが見つかりません。env_example.txtからコピーして作成します。"
  cp env_example.txt .env
  echo ".envファイルを編集して、適切な設定を行ってください。"
  echo "特に、データベース接続情報を正しく設定してください。"
fi

# アプリケーションを起動
echo "アプリケーションを起動しています..."
python main.py

# 元のディレクトリに戻る
cd "$CURRENT_DIR" 
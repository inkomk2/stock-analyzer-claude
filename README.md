# 📈 日経225 スイングトレード分析ツール

信用取引 × IFDOCO注文 × テクニカルスコアリングによる本格的な株式投資支援ツールです。

## 🎯 ツールの目的

- 元手 **300万円** を信用取引（3倍）で運用し、**月次20万円以上**の安定収益を目指す
- **お昼（12-13時）と夜（18時以降）** の限られた時間での効率的なトレードをサポート
- **IFDOCO注文**で自動的に利確・損切りを設定し、ノーリスク放置トレードを実現

---

## 🚀 セットアップ方法

### ローカル実行

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/nikkei225-swing-tool.git
cd nikkei225-swing-tool

# 依存パッケージをインストール
pip install -r requirements.txt

# アプリ起動
streamlit run app.py
```

### Streamlit Cloud で公開（無料）

1. [github.com](https://github.com) に新しいリポジトリを作成
2. このプロジェクトをプッシュ：

```bash
git init
git add .
git commit -m "Initial commit: 日経225スイングトレードツール"
git remote add origin https://github.com/YOUR_USERNAME/nikkei225-swing-tool.git
git push -u origin main
```

3. [share.streamlit.io](https://share.streamlit.io) にアクセス
4. GitHub アカウントでログイン
5. 「New app」→ リポジトリ選択 → `app.py` を指定 → Deploy

**→ `https://YOUR_USERNAME-nikkei225-swing-tool-app-XXXXX.streamlit.app` で公開完了！**

---

## 📊 スコアリングアルゴリズム

| 指標 | 配点 | 評価ロジック |
|------|------|------------|
| **RSI** | 25点 | 30-50（買いゾーン）で最高点、70超で低点 |
| **MACD** | 25点 | ゴールデンクロス後上昇中が最高点 |
| **移動平均** | 20点 | MA5>MA20>MA60のパーフェクトオーダーで最高点 |
| **ボリンジャーバンド** | 15点 | 下限付近（バンドウォーク底）で最高点 |
| **出来高** | 15点 | 平均の2倍以上で最高点 |

---

## 📋 IFDOCO注文の仕組み

```
IF（条件）: 新規買い ¥XXXX 指値
  ↓ 約定したら自動的に↓
OCO①（利確）: 売り ¥XXXX 指値      ← 利益目標達成で自動決済
OCO②（損切）: 売り ¥XXXX 逆指値   ← 損失限定で自動決済
```

**リスクリワード比 1:2.5以上** を基準に設定（ATRベース）

---

## 💡 運用戦略

### 信用取引の使い方
- 元手300万円 × 信用3倍 = 最大900万円の運用力
- 1銘柄に資金の30%（270万円相当）まで
- 同時保有は3〜5銘柄を目安に分散

### 月20万円の達成シナリオ
```
1銘柄あたり期待利益：5〜8%
× 1回の運用額：200〜300万円（信用）
= 利益：10〜24万円/トレード
× 月2〜3回のトレード
= 月次目標：20〜50万円
```

### タイムスケジュール
- **毎朝（起床後5分）**: スマホでランキングを確認
- **昼休み（12:00-13:00）**: 注文状況確認・新規エントリー
- **夜（18:00以降）**: 翌日の戦略検討・IFDOCO注文設定

---

## ⚠️ 免責事項

このツールは情報提供を目的としており、投資アドバイスではありません。
株式投資には元本割れのリスクがあります。投資判断はご自身の責任で行ってください。

---

## 🔧 技術スタック

- **Streamlit** - Web UI フレームワーク
- **yfinance** - 株価データ取得（Yahoo Finance API）
- **pandas / numpy** - データ分析
- **Plotly** - インタラクティブチャート

---

*Built for swing trading Japanese stocks with discipline and data-driven decisions.*

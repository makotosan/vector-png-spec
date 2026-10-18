# 正規化のテストデータ

[English](README.md)

これらは実験的な[正規化プロファイル](../../profiles/svg-normalization-v1.ja.md)を
検査するための、独自作成の合成データです。顧客の SVG や業務内容は含みません。
nameplate.input.svg は style 要素1個、class 属性26個を持ちます。文字と、
無害な文字列 VECTOR-PNG を符号化したバージョン1・誤り訂正Lの QR を含み、
余白は4モジュール、1モジュールは6ピクセルです。モジュール行列は ReportLab の
QR エンコーダーで生成しました。エンコーダーのコードはコピーしておらず、テスト時にも
不要です。qr-matrix.json に期待するモジュール配置を記録しています。

nameplate.expected.svg と nameplate.expected-report.json はレビュー対象の構造上の
期待結果であり、検証済み変換の主張ではありません。レポートは意図的に failure／
render not-checked とし、出力ダイジェストを持ちません。解析だけでは描画判定に合格できません。
公開の cases.json には、カスケード、出現順序、セレクターリスト、継承、グループの不透明度、
メタデータ移行、角丸と水平・折り返しの三角矢印を持つ図を収録し、未対応 CSS、外部参照、
危険な XML、競合に対する無害な拒否例も含みます。拒否データは描画しません。
サイズ・深さ・個数の上限と、出力確定時のファイル保護は、巨大なファイルを保存せず動的にテストします。

tools/normalization_fixture.py はテストデータを動かす例であり、実運用のサニタイザー、
全面監査済みの正規化実装、製品版 CLI ではありません。tinycss2 によるトークン化と、
独立した制限付き出力チェッカーを使います。出力保護テストでは、ファイル確定だけを
検査するための描画スタブだと明記しています。実際の外観は別の Chromium アダプターで
検証します。有限のテスト群は、任意の SVG やアクセシビリティ挙動の認証ではありません。

## 構造の検査

既存の PNG データのテストは依存ライブラリ不要です。追加の正規化テストは、tinycss2 が
ない場合、理由を明示して省略します。すべて実行する手順:

```sh
python -m pip install -r requirements-normalization.txt
python -m unittest discover -s tests -v
python tools/build_fixtures.py --check
python tools/build_normalization_fixtures.py --check
```

build_normalization_fixtures.py は外部依存なしで cases.json だけを再生成します。
期待 SVG・レポート・QR の変更は意図的にレビューしなければなりません。
失敗したテストを通すために自動再生成してはいけません。

## 独立した任意の SVG2 描画検証

フォントを導入した管理下のホストを使用します。テスト用 Python に Pillow、
ローカル Node 環境に Playwright を導入し、Chromium をインストールしてください。
代わりに NORMALIZATION_CHROME に既存の Chrome 実行ファイルを指定できます。

```sh
python -m pip install Pillow
npm install --no-save playwright@1.58.2
npx playwright install chromium
python tools/prepare_normalization_render.py
node tools/render_normalization.cjs .normalization-render/manifest.json
python tools/check_normalization_render.py
```

アダプターは、検査済みソースを独立した SVG 画像文書として描画し、スクリプトと外部通信を
無効にして、宣言した寸法で同一ホストの RGBA プレビューを取得します。
チェッカーは完全一致を要求し、QR の全モジュールと余白の画素、文字領域に描画があることを
検査します。文字と矢印は目視でも確認してください。OCR、印刷物、スマートフォンの
カメラによる読取テストではありません。フォントの選択はホスト依存として記録し、
ホスト間の一致は主張しません。CSS の rx／ry などの形状指定を無視するレンダラーは、
それらの変換前後検査には不適切です。結果は無視対象の .normalization-render/ に保持します。

互換性: PNG wire v1、ソースのキーワード、safe-svg-v1 出力の許可リスト、既存の PNG
21ケースは変更しません。実施済み結果は VALIDATION.md を参照してください。
テストを設定しただけでは実行の証拠にはなりません。

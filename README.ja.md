# vector-png ファイル形式仕様

[English](README.md)

SVG を圧縮 iTXt に埋め込んだ PNG の、**アプリに依存しないドラフト仕様**です。
Codex スキルや Illustrator／Inkscape 拡張の実装とは分けて管理します。

- [正式な仕様本文（英語・wire v1／draft 0.1）](SPEC.md)
- [日本語仕様ガイド](SPEC.ja.md)
- [安全な SVG の対応プロファイル](profiles/safe-svg-v1.md)
- [実装・相互運用のガイド](IMPLEMENTATIONS.md)
- [共通サンプルとテスト](fixtures/README.md)

[既存の Python CLI／Codex スキル](https://github.com/makotosan/vector-png) は
別リポジトリの参照実装です。将来の Illustrator／Inkscape 版は Python や
CairoSVG に依存せず、この仕様を基に実装できます。アプリ向け拡張自体は未実装です。

「保存形式として正しい」「安全な SVG の範囲に対応する」「再描画した画素が一致する」
を区別します。**CairoSVG の完全画素一致は共通形式の必須条件ではありません。**

Python 3.10 以降の標準ライブラリだけで共通サンプルを検証できます。

```sh
python -m unittest discover -s tests -v
python tools/build_fixtures.py --check
```

仕様はドラフトです。英語の SPEC.md を正とし、日本語ガイドは理解を助ける資料です。
独自に作成した仕様・ツール・テストデータは MIT ライセンスで公開します。

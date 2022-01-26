このwikiについて
================

ディレクトリ構造を持ったドキュメント作成に向いたwikiエンジンです。
[jimenezrick/wi-wiki](https://github.com/jimenezrick/wi-wiki)から分岐しています。
次のような特徴があります。

- [markdown](https://ja.wikipedia.org/wiki/Markdown)記法
- シンプル
  - wikiエンジンは500行程度のbashスクリプト
  - DB不要。wikiコンテンツはテキスト形式でgit管理。
- ポータブル
  - cgiが実行可能なサーバなら大体どこでも動く
  - サーバが無くてもエディタで直接編集
  - wikiのコンテンツとエンジンが独立
    - 混じり気の無いドキュメントフォルダと、外側からコンテンツを編集するcgi


ディレクトリ構造
----------------

```
  ├── cgi-bin/
  │   ├── subsh
  │   │   └── md2html    ... markdownパーサ
  │   └── wiki.cgi       ... wiki本体
  ├── contents/          ... wikiコンテンツ格納ディレクトリ(以下は一例)
  │   ├── Home.md
  │   ├── dir1/
  │   │   └── note1.md
  │   ├── dir2/
  │   │   └── note2.md
  ├── data/              ... html作成のための部品置き場
  │   ├── FOOTER
  │   └── HEADER
  ├── doc/               ... GPLのお約束
  │   ├── COPYING
  │   └── README
  └── wrapper/           ... webからアクセスしたときのパーミッション設定に必要なラッパ
      ├── Makefile
      └── wiki.c
```

インストール手順
----------------

1. subsh/以下にmarkdown形式からhtml形式へ変換するパーサを置きます。
   [John Gruberのperlスクリプト](https://daringfireball.net/projects/markdown/)を置いていますが、
   md4c(https://github.com/mity/md4c.git)のmd2htmlの方が高機能なので標準設定でこちらを使うようになっています。
   本レポジトリにはmd4cは含まれませんので別途取得する必要があります。
2. contents/以下に管理したいリポジトリごとにgit initやgit cloneして下さい。コミットするユーザーの名前とemailの設定も必要です。
   $ git config --local user.name "user name"
   $ git config --local user.email user_name@example.com
3. ブラウザからwiki.cgiにアクセスします。

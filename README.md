
#ML cascadeファイルの作成方法


##チョーかんたんまとめ
target-imageに正解画像ファルをを集める
アノテーション作成
'''
$ checkobjects.py
'''
検出器作成
'''
$ makecascade.py
'''
確認
'''
$ detectobjects.py
$ checkobjects.py detectposi.info
'''

##
ちょっと親切な説明
step1　正解画像を集め、アノテーションを作成
正解画像が含まれる画像ファイルを"target-image"ディレクトリに集め、"checkobjects.py"を起動してアノテーションを作成します。　

step2 トレーニング
"makecascade.py"を起動してトレーニングを実行します。(stage19で終わり)
作成された検出器は"classifier/cascade.xml"

step3 テスト検出
"detectobjects.py"を起動して検出テストを行います。
出来上がった"detectposi.info"は"checkobjects.py detectposi.info"と実行することで、現在の正解画像ファイルの検出内容を確認することできます。




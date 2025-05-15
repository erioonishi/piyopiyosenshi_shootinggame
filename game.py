import pygame
import sys
import json
import os  #ファイルの有無確認
from player import Player
from enemy import Enemy

SCORE_FILE = "scores.json"  #スコア保存用のファイル名
MAX_RANKING = 5

class Game:  #ゲーム全体を管理するクラス定義
    def __init__(self, screen, width, height):  #初期化メソッド(ゲーム画面・サイズを受け取る)
        #渡された画面とサイズ保存
        self.screen = screen
        self.width = width
        self.height = height
        #複数のフォント(サイズ別)を用意
        self.font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 28)  #画面の左上にスコア
        self.small_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 22)  #ゲームオーバー画面で上位スコアという見出しトランキング
        self.large_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 72)  #「GAME OVER」の文字
        self.title_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 48)  #タイトル用の小さめのフォントを追加
        #プレイヤーを作り、スプライトグループを作る（描画・管理用）
        self.player = Player(width, height)
        self.player_group = pygame.sprite.Group(self.player)  #Playerクラスはplayer.pyで定義されていてself.playerはプレイヤーキャラのインスタンス
        self.bullet_group = pygame.sprite.Group()  #空のグループとして作られていて弾：Bulletクラスのインスタンスはプレイヤーが撃ったときに作られて追加
        self.enemy_group = pygame.sprite.Group()  #これも空のグループで敵：Enemyクラスのインスタンスは(ちょっと下にある)def spawn_enemy(self):で追加

        #スコア・ゲーム状態・名前入力の初期化
        self.score = 0  #最初は当然0点からスタート
        self.game_over = False  #最初はまだゲームオーバーじゃないのでFalse
        self.running = False  #スタート画面管理(runningは今ゲームがスタートしているかどうかを表すフラグ)
        self.name_input = ""  #プレイヤーが入力する名前で、最初は空文字(何も入力されていない状態)

        #スコア保存フラグ(一度しか保存しないため→Pygameでは衝突判定などが何回も呼ばれるのでもしこのフラグがなければゲームオーバーのたびに何度も同じスコアが保存される)
        self.score_saved = False  #最初はFalseにしておく(未保存の状態)
        
        #事前にスコアファイルを読み込む(前回のランキングを読み込んで、自分のランキングデータとしてセットする)
        self.ranking = self.load_scores()

        # 敵の出現タイミングを管理するためのカウンター
        self.enemy_spawn_counter = 0  # カウンタを0に初期化

    #scores.jsonスコアファイル自体があるかチェックしてランキングを返す(中身があればファイルが存在する)
    def load_scores(self):  #selfはGameクラスのインスタンス(自分自身)
        if os.path.exists(SCORE_FILE):  #そのファイルが存在するか？をチェックするPythonの関数(スコアファイル)
            with open(SCORE_FILE, "r", encoding="utf-8") as f:  #ファイルを読み取りモード("r")で開いて、(日本語encoding="utf-8")with...as...はファイルを開いたあと、自動で閉じてくれる
                return json.load(f)  #ファイルの中身(JSON形式)を読み込んで、Pythonのデータ型(リスト)に変換して返す
        return []  #ファイルが存在しなかった場合は、空のリスト[]を返す
        # ※fはファイルオブジェクトを入れる変数、"r"はファイルを「読み込み専用(read)」で開くモード

    def save_score(self):  #新しいスコアを追加して上位5件にしてファイルに保存(すでに保存済みなら何もしない)
        if self.score_saved:  # self.score_savedがTrue(=すでに保存している)ならもう何もしない(下にコメント)
            return
        self.score_saved = True  #保存したので次回呼ばれても無視できるようself.score_savedをTrue
        self.ranking.append({"name": self.name_input, "score": self.score})  #今までのランキングのリスト(self.ranking)に新しいスコアを追加
        self.ranking = sorted(self.ranking, key=lambda x: x["score"], reverse=True)[:MAX_RANKING] #ランキングをソート＆上位5件に制限(下にコメント)
        with open(SCORE_FILE, "w", encoding="utf-8") as f:  #"w"書き込みモード→今あるファイルを上書き
            json.dump(self.ranking, f, ensure_ascii=False, indent=2)  #json.dump(...)でself.rankingをファイルに書き込む

    def spawn_enemy(self):  #敵を1体作ってenemy_groupに追加
        enemy = Enemy(self.width)  #敵キャラを作る(出現位置は画面幅に応じてランダム決定)
        self.enemy_group.add(enemy)  #その敵をグループに追加して、後でまとめて動かせる・描画できるようにする

    #プレイヤーの入力(キーボードの操作)を受け取って、ゲームの状態ごとに何をするか決める関数
    def handle_input(self, event):  #タイトル画面、ゲーム中、ゲームオーバー時で処理を切り替え
        if not self.running:  #ゲームがまだ始まってないとき(タイトル画面)
            if event.type == pygame.KEYDOWN:  #キーが押されたイベントか確認
                if event.key == pygame.K_BACKSPACE:  #名前入力中にバックスペースが押されたら、最後の文字を削除する
                    self.name_input = self.name_input[:-1]
                elif event.key == pygame.K_RETURN:  #(K_RETURN)Enterキーでゲームスタート
                    self.running = True  #self.runningをTrueにして、タイトル画面→ゲーム開始へ切り替える
                elif event.unicode.isprintable():  #isprintable()はPythonの組み込みの文字列メソッドで表示できる文字か確認
                    if len(self.name_input) < 8:  #8文字までなら名前に追加
                        self.name_input += event.unicode
        elif not self.game_over:  #ゲーム中(self.runningがTrueかつself.game_overがFalse)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  #スペースキーが押されたら
                bullet = self.player.shoot()  #弾を発射！
                self.bullet_group.add(bullet)  #プレイヤーのshoot()メソッドを呼んで弾を作り、bullet_groupに追加
        else:  #ゲームオーバー時(self.runningがTrueかつself.game_overがTrue)
            if event.type == pygame.KEYDOWN:  #キーが押されたら
                if event.key == pygame.K_r:  #Rキーで再スタート
                    self.restart_game()
                elif event.key == pygame.K_q:  #Qキーでゲーム終了してプログラムを終了
                    pygame.quit()
                    sys.exit()

    def update(self, keys):  #ゲーム状態を更新
        if not self.running or self.game_over:  #ゲームがまだ始まってない(self.running==False)またはゲームオーバー中なら、更新ストップですぐ戻る
            return

        self.player_group.update(keys)  #(左・右)キー入力を渡してプレイヤーの動きを更新しプレイヤーのupdateメソッドを呼ぶ
        self.bullet_group.update()  #弾もまとめてupdate()弾は自動で上に飛んでいくからここで位置更新

        #敵の出現をカウンタで制御（180フレームごとに1体の敵が出現）
        self.enemy_spawn_counter += 1
        if self.enemy_spawn_counter >= 180:  #3秒ごとに1体の敵をスポーンさせる
            self.spawn_enemy()
            self.enemy_spawn_counter = 0  #カウンタをリセット

        for enemy in self.enemy_group:
            if enemy.update():  #enemy.update()で敵を下に動かす
                self.game_over = True  #戻り値がTrueなら敵が画面の下に行ってしまったのでゲームオーバー
                self.save_score()  #スコア保存

        hits = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, True)  #弾と敵がぶつかったか確認、True, Trueでぶつかった弾も敵も両方消す
        self.score += len(hits)  #当たった数だけスコアを増やす

        if pygame.sprite.spritecollideany(self.player, self.enemy_group):  #プレイヤーと敵がぶつかったら
            self.game_over = True
            self.save_score()

    def draw(self):  #タイトルかゲーム画面かで描画を切り替え
        if not self.running:  #もしまだゲームが始まってなかったら
            self.draw_start_screen()  #タイトル画面を描く
            return  #returnで終わり→ゲーム画面は描かない
        self.screen.fill((173, 216, 230))  #まずパステル水色(RGB)で塗りつぶす

        self.player_group.draw(self.screen)  #プレイヤーを画面に描画
        self.bullet_group.draw(self.screen)  #弾を画面に描画
        self.enemy_group.draw(self.screen)  #敵を画面に描画

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))  #self.scoreを文字にして白色スコアの文字を作る
        self.screen.blit(score_text, (10, 10))  #作ったスコアのテキストを画面の左上(10, 10の位置)に描画

        if self.game_over:  #ゲームオーバーなら
            self.draw_game_over()  #draw_game_over()を呼んでゲームオーバー画面を重ねて描く

    def draw_start_screen(self):  #タイトル、名前入力欄、スタート案内を表示
        title = self.title_font.render("ぴよぴよ戦士", True, (255, 200, 200))  #Trueはアンチエイリアス(文字を滑らかにする)設定
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 200))  #作ったタイトル文字を画面に描画横は画面の中央(画面の中心 - 文字の横幅の半分)縦は200ピクセルの位置

        input_text = self.font.render(f"名前: {self.name_input}", True, (255, 255, 255))
        self.screen.blit(input_text, (self.width // 2 - input_text.get_width() // 2, 300))

        start_text = self.font.render("Enterキーでスタート", True, (200, 255, 200))
        self.screen.blit(start_text, (self.width // 2 - start_text.get_width() // 2, 350))

    def draw_game_over(self):  #「GAME OVER」やスコアランキングなどを描画
        over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(over_text, (self.width // 2 - over_text.get_width() // 2, self.height // 2 - 100))  #縦は画面の中央-100ピクセルの高さに置く

        restart_text = self.font.render("Rキーで再チャレンジ、Qキーで終了", True, (255, 255, 255))
        self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2))  #画面中央の高さに描く

        top_text = self.small_font.render("上位スコア", True, (255, 255, 0))
        self.screen.blit(top_text, (self.width // 2 - top_text.get_width() // 2, self.height // 2 + 60))  #ゲームオーバーの下+60ピクセルの高さに置く

        for i, entry in enumerate(self.ranking[:5]):
            score_entry = self.small_font.render(f"{i+1}. {entry['name']} : {entry['score']}", True, (255, 255, 255))
            self.screen.blit(score_entry, (self.width // 2 - score_entry.get_width() // 2, self.height // 2 + 90 + i * 30))  #縦位置は90+i*30なので1件目は90ピクセル2件目は120ピクセルとずらして表示する

    def restart_game(self):  #スコアリセット、敵・弾を消去、プレイヤー位置を初期化
        self.score = 0  # スコアを0にリセットする
        self.game_over = False  #ゲームオーバー状態を解除する(またゲームできる状態に戻す)
        self.score_saved = False #これがFalseになることで再び新しいスコアが保存できるようになる→スコア保存フラグをリセット
        self.enemy_group.empty()  #敵を全部消す(enemy_groupの中身を空にする)
        self.bullet_group.empty()  #プレイヤーの弾も全部消す

        # プレイヤーの位置を中心とY座標で明示的に設定
        self.player.rect.centerx = self.width // 2  #self.width//2は画面の横幅の半分だからプレイヤーが横方向で真ん中にくる。
        self.player.rect.bottom = self.height - 30  # ← 高さを調整（画像の高さ分、やや下にする）self.height-30は、画面の高さから30ピクセル上

'''
★game.pyの動き
Gameクラスがすべての中心で、画面状態やオブジェクトを管理
・update() → 状態更新
・draw() → 画面描画
・handle_input() → キー入力を処理
【ざっくりの流れ】
・最初に「準備」
・名前を入力
・弾打ちゲームが始まる
・スコア保存＆ランキング付きでリトライできる
【流れ】
⑴初期化(__init__)
・必要なもの(画面サイズ、フォント、プレイヤー、グループなど)を全部準備
・スコアランキングもファイルから読み込む。
⑵スタート画面(draw_start_screen)
・「ぴよぴよ戦士」のタイトルが出る
・名前入力欄が出る
・「Enterキーでスタート」案内が出る
・キー入力は handle_input が見ていて、Enterキーが押されたら→self.running=Trueでゲーム開始
⑶ゲーム開始(update & draw)
●update:
・プレイヤーや弾、敵を更新
・一定フレームごとに敵を出す(spawn_enemy)
・弾と敵が当たったらスコアUP
・敵が画面下まで来たらゲームオーバー
・プレイヤーが敵に当たってもゲームオーバー
●draw:
・背景塗る
・プレイヤー、弾、敵を描画
・スコアを表
⑷ゲームオーバー画面(draw_game_over)
・「GAME OVER」表示
・「Rキーで再チャレンジ、Qキーで終了」案内
・上位5件のランキング表示
●入力(handle_input)
・Rキー → restart_game()でリセット
・Qキー → 終了
⑸スコア保存(save_score)
・ゲームオーバー時、スコアを一度だけ保存
・上位5件に絞ってJSONファイルに保存
⑹再スタート (resta⑹rt_game)
・スコアや敵・弾を全部リセット
・プレイヤー位置を初期化
・すぐゲーム再開できる
【このループを回す】
スタート画面
→ ゲーム中
→ ゲームオーバー
→ 再チャレンジ or 終了
'''

'''
★self.ranking = sorted(self.ranking, key=lambda x: x["score"], reverse=True)[:MAX_RANKING]
・sorted(...)はランキングを並べ替え
・key=lambda x: x["score"] は「スコアの値」で並べ替える指定
・reverse=True は「スコアが高い順」にする
・[:MAX_RANKING] は 上位5件だけを残す（MAX_RANKING = 5）
'''

'''
★if self.score_saved:
    return
True(=すでに保存している)ならもう何もしない
【流れ】
⑴ゲームオーバーになる
→save_score()が呼ばれてスコアをファイルに保存する
⑵その後、何らかの理由でsave_score()がもう一度呼ばれたとき
→ self.score_savedは でにTrueなので、何もしないでreturn(中断)する
【なぜ必要？】
ゲームの処理によっては、ゲームオーバー判定が複数回走ることがある
<例>
・敵が画面外に出たときも
・敵と自機がぶつかったときも
→ 両方でsave_score()を呼んでいると、1回のゲームで2回スコア保存が試みられることがある
これを放っておくと同じスコアが何度も保存され、ランキングが不自然になる
'''

'''
★コメントなしのcodeだけ必要な時
import pygame
import sys
import json
import os
from player import Player
from enemy import Enemy

SCORE_FILE = "scores.json"
MAX_RANKING = 5

class Game:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 28)
        self.small_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 22)
        self.large_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 72)
        self.title_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 48)  # タイトル用の小さめのフォントを追加
        self.player = Player(width, height)
        self.player_group = pygame.sprite.Group(self.player)
        self.bullet_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        self.score = 0
        self.game_over = False
        self.running = False  # スタート画面管理
        self.name_input = ""

        self.score_saved = False  # スコア保存フラグ
        
        self.ranking = self.load_scores()

        # 敵の出現管理用のカウンタ
        self.enemy_spawn_counter = 0  # カウンタを0に初期化

    def load_scores(self):
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_score(self):
        if self.score_saved:
            return
        self.score_saved = True  # 一度だけ保存する
        self.ranking.append({"name": self.name_input, "score": self.score})
        self.ranking = sorted(self.ranking, key=lambda x: x["score"], reverse=True)[:MAX_RANKING]
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.ranking, f, ensure_ascii=False, indent=2)

    def spawn_enemy(self):
        enemy = Enemy(self.width)
        self.enemy_group.add(enemy)

    def handle_input(self, event):
        if not self.running:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self.running = True
                elif event.unicode.isprintable():
                    if len(self.name_input) < 8:
                        self.name_input += event.unicode
        elif not self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullet = self.player.shoot()
                self.bullet_group.add(bullet)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

    def update(self, keys):
        if not self.running or self.game_over:
            return

        self.player_group.update(keys)
        self.bullet_group.update()

        # 敵の出現をカウンタで制御（180フレームごとに1体の敵が出現）
        self.enemy_spawn_counter += 1
        if self.enemy_spawn_counter >= 180:  # 3秒ごとに1体の敵をスポーンさせる
            self.spawn_enemy()
            self.enemy_spawn_counter = 0  # カウンタをリセット

        for enemy in self.enemy_group:
            if enemy.update():
                self.game_over = True
                self.save_score()

        hits = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, True)
        self.score += len(hits)

        if pygame.sprite.spritecollideany(self.player, self.enemy_group):
            self.game_over = True
            self.save_score()

    def draw(self):
        if not self.running:
            self.draw_start_screen()
            return
        self.screen.fill((173, 216, 230))  # パステル水色（RGB）

        self.player_group.draw(self.screen)
        self.bullet_group.draw(self.screen)
        self.enemy_group.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            self.draw_game_over()

    def draw_start_screen(self):
        title = self.title_font.render("ぴよぴよ戦士", True, (255, 200, 200))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 200))

        input_text = self.font.render(f"名前: {self.name_input}", True, (255, 255, 255))
        self.screen.blit(input_text, (self.width // 2 - input_text.get_width() // 2, 300))

        start_text = self.font.render("Enterキーでスタート", True, (200, 255, 200))
        self.screen.blit(start_text, (self.width // 2 - start_text.get_width() // 2, 350))

    def draw_game_over(self):
        over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(over_text, (self.width // 2 - over_text.get_width() // 2, self.height // 2 - 100))

        restart_text = self.font.render("Rキーで再チャレンジ、Qキーで終了", True, (255, 255, 255))
        self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2))

        top_text = self.small_font.render("上位スコア", True, (255, 255, 0))
        self.screen.blit(top_text, (self.width // 2 - top_text.get_width() // 2, self.height // 2 + 60))

        for i, entry in enumerate(self.ranking[:5]):
            score_entry = self.small_font.render(f"{i+1}. {entry['name']} : {entry['score']}", True, (255, 255, 255))
            self.screen.blit(score_entry, (self.width // 2 - score_entry.get_width() // 2, self.height // 2 + 90 + i * 30))

    def restart_game(self):
        self.score = 0
        self.game_over = False
        self.score_saved = False
        self.enemy_group.empty()
        self.bullet_group.empty()

        # プレイヤーの位置を中心とY座標で明示的に設定
        self.player.rect.centerx = self.width // 2
        self.player.rect.bottom = self.height - 30  # ← 高さを調整（画像の高さ分、やや下にする）

'''
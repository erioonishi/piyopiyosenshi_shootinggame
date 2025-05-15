import pygame

#Bullet(バレット弾丸)

class Bullet(pygame.sprite.Sprite):  #Bulletクラスの定義(pygame.sprite.Sprite)を継承してPygameのスプライト機能を使う
    def __init__(self, x, y):  #コンストラクタ(初期化メソッド)弾を作るときにxとy座標の中心を渡して生成
        super().__init__()  #親クラス(Sprite)の初期化を呼ぶ(これは決まりごと)
        self.image = pygame.Surface((5, 10))  #弾の見た目を作るPygameのSurfaceで幅5ピクセル×高さ10ピクセルの四角形を作る
        self.image.fill((255, 255, 0))  #弾の色を設定→作ったSurfaceを黄色で塗りつぶす
        self.rect = self.image.get_rect(center=(x, y))  #スプライトの当たり判定用のrectを作る→作った画像(Surface)からrectを取り出し、弾の中心を(x, y)座標に配置→このrectが弾の位置や当たり判定を管理
        self.speed = -10  #弾のスピード設定→弾は上方向に発射されるので、Y方向に-10ピクセルずつ動かす設定

    def update(self):  #スプライト更新メソッドで毎フレーム自動的に呼ばれるPygameの仕組み
        self.rect.y += self.speed  #speed = -10なので毎フレーム10ピクセルずつ上に進む動き
        if self.rect.bottom < 0:  #画面の上端(Y=0)より上に弾が完全に出たときを判定
            self.kill()  #スプライトグループからこの弾を自動で消去して、メモリや処理を無駄に使わないようする

'''
★__init__とは(_init_ではだめ)
インスタンスを作るときに最初に呼ばれる初期化メソッド
今回のdef __init__(self, x, y)
selfは「作られるBulletそのもの」を指す(決まり事）
x, yは弾を作る位置(スタート位置)を渡す引数
x, yは弾の中心座標→弾はプレイヤーの位置になければいけない
まとめると、プレイヤーが動くので、毎回その位置から弾が出る必要がある
弾を作るときに「どこから出すか（x, y）」を指定して、そこに小さな黄色い弾を置いておく
'''

'''
★PygameのSurface(サーフェス表面)とは
Pygameで「何かを描きたい」と思ったら、必ずSurfaceが関係している
Surfaceは「画像や画面のキャンバス」を表すオブジェクト
Surfaceとは「画像の入れ物」 のこと
<例>
・画面全体もSurface
・自分で作る画像(弾やキャラなど)もSurface
・ファイルから読み込んだ画像もSurface
【使い方】
⑴画面もSurface
screen = pygame.display.set_mode((600, 600))
→screen は「ウィンドウのSurface」ここに全部描画される
⑵self.image = pygame.image.load("player.png").convert_alpha()
→画像ファイルを読み込んだ結果がSurface
⑶自分で作る
self.image = pygame.Surface((5, 10))
self.image.fill((255, 255, 0))  # 黄色く塗る
空のSurfaceを作って、好きな色で塗る
'''

'''
★self.rect = self.image.get_rect(center=(x, y))
self.image のサイズにぴったりのRectを作ってそのRectの中心位置を(x, y)にして、self.rectに代入する
⑴self.image
これはスプライト(キャラやオブジェクト)の画像を表すSurfaceで、たとえば敵キャラの絵や、自機の画像など
⑵get_rect()
このメソッドは、その画像の「枠(四角形)」を作ります。Pygameでは、画像には位置やサイズの情報は入ってないので、矩形（rect）オブジェクトを作って管理
get_rect()は、画像サイズにぴったり合うRect(長方形)を返す
⑶center=(x, y)
ただget_rect()するだけだと、位置が(0, 0)にあるRectができ、画面の左上から始まってしまう
でもcenter=(x, y)とするとそのRectの中心を(x, y)に合わせることができる
'''

'''
★rectとは
Pygameでは、画像(Surface)を「どこに表示するか」や「当たり判定」を管理するために、Rect(矩形：くけい)オブジェクトを使う
このRectは 位置と大きさの情報をまとめて持っている便利なもの
【Rectの主な中身】
・x, y（左上の座標）
・width, height（幅と高さ）
・top, bottom, left, right, centerx, centery など、位置を簡単に参照できる属性もある
'''

'''
★selfとは
selfはそのクラスの「自分自身」を表すもの
プレイヤーの「名前」
プレイヤーの「HP」
プレイヤーの「位置」
このプレイヤー自身をcodeの中で表すのがself
・self.imageはこのプレイヤー自身が持っている画像
・self.rectはこのプレイヤー自身が持っている位置情報
selfがないと一時的に読み込むだけで、このプレイヤーが持ってるものとは認識されない
self.image = ... とすることで、
そのインスタンス（自分自身）に保存することができる
クラスの中の関数(メソッド)は、自分の持ち物を定義するときは必ずselfを付ける
'''

'''
★コメントなしのcodeだけ必要な時
import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
'''
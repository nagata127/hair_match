from django.shortcuts import redirect, render
from .models import Document
from .forms import ImageForm
from django.views import generic
from django.urls import reverse_lazy

from PIL import Image
import os
import cv2
import sys


class IndexView(generic.ListView):
    model = Document
    context_object_name = "lists"
    template_name = "photo/test.html"

# class ArticleUpdateView(generic.UpdateView):
#         template_name = 'photo/index.html'
#         model = Document
#         fields = ['photo']
#         success_url = reverse_lazy('album:show')

class HomeBaseView(generic.TemplateView):
    # template_name = "photo/show.html"

    # 似ている人検索
    def similar_image(self, img):
        TARGET_FILE = os.path.basename(img) # postされた画像
        IMG_DIR = os.path.abspath(os.path.dirname('album')) + '/media/hair/'
        IMG_SIZE = (200, 200)
        target_img_path = img
        target_img = cv2.imread(target_img_path, cv2.IMREAD_GRAYSCALE)
        target_img = cv2.resize(target_img, IMG_SIZE)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING)

        # ORBとAKAZEは特徴点や特徴量を抽出するアルゴリズム
        # コメントアウトを調節することによりどちらでも行える

        # detector = cv2.ORB_create()
        detector = cv2.AKAZE_create()

        # ターゲットの写真の特徴点を取得する
        (target_kp, target_des) = detector.detectAndCompute(target_img, None)

        # print('TARGET_FILE: %s' % (TARGET_FILE))

        dirs = os.listdir(IMG_DIR)
        ret_min = 100000
        a = []
        # 髪の種類ごとに
        for dir in dirs:
            if dir == '.DS_Store' or dir == TARGET_FILE:
                continue
            # 種類ごとのファイルリスト
            dir_path = IMG_DIR + dir + '/'
            files = os.listdir(dir_path)
            
            
            for file in files:
                comparing_img_path = dir_path + file
                
                try:
                    comparing_img = cv2.imread(comparing_img_path, cv2.IMREAD_GRAYSCALE)
                    comparing_img = cv2.resize(comparing_img, IMG_SIZE)
                    # 比較する写真の特徴点を取得する
                    (comparing_kp, comparing_des) = detector.detectAndCompute(comparing_img, None)
                    # BFMatcherで総当たりマッチングを行う
                    matches = bf.match(target_des, comparing_des)
                    # 特徴量の距離を出し、平均を取る
                    dist = [m.distance for m in matches]
                    ret = sum(dist) / len(dist)
                    
                except cv2.error:
                    # cv2がエラーを吐いた場合の処理
                    ret = 100000

                # 一番似ている顔
                if ret < ret_min:
                    ret_min = ret
                    kind = dir
                    similar = file
                    path = '/media/hair/' + dir + '/' + file

        # 最も似ているものを出力
        # print(similar, kind, ret_min)
        return similar, kind, path, ret_min

    # 変数
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ImageForm()
        context['form'] = form
        return context

    #get処理
    def get(self, request, *args, **kwargs):

        return super().get(request, *args, **kwargs)

    #post処理
    def post(self, request, *args, **kwargs):

        form = ImageForm(request.POST, request.FILES)
        # アップロード処理
        if form.is_valid(): # フォームに入力の際のエラー判定

            # handle_uploaded_file(request.FILES['file'])
            update = Document.objects.last()
            update.photo = request.POST.get('photo')
            
            update.save()

            return redirect('/show')
        
        return render(request, self.template_name, self.get_context_data(form=form))



class Home(HomeBaseView):
    template_name = "photo/index.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     form = ImageForm()
    #     context['form'] = form
    #     return context



class Show_image(HomeBaseView):
    template_name = "photo/show.html"

    # 変数
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        img_path = Document.objects.first().photo.path
        context = {
            'similar':'a',
            **kwargs,
        }
        context['tes'] = super().similar_image(img_path)
        context['update'] = Document.objects.last().photo

        return context

    #get処理
    def get(self, request, *args, **kwargs):
        form = ImageForm()
        # form = ImageForm(request.POST, request.FILES)
        img_path = Document.objects.last().photo.path
        img = super().similar_image(img_path)
        return render(request, self.template_name, self.get_context_data(similar=img[0], kind=img[1], path=img[2], ret=img_path, form=form))

    # post処理
    # def post(self, request, form,  *args, **kwargs):
    #     super().post(form)

    #     return render(request, self.template_name, self.get_context_data(form=form))


def upload(request): # アップロード

    images = Document.objects.all()

    if images.count() >= 2: # モデルを削除
            images[0].delete()

    if request.method == "POST": # アップロード時の処理
        form = ImageForm(request.POST, request.FILES)
        

        if form.is_valid(): # フォームに入力の際のエラー判定
            
            form.save()
            return redirect('/show')
            
    else:
        form = ImageForm()

    context = {
        'form':form,
        'images':images,
        }
        
    return render(request, 'photo/home.html', context)

# 確認用
def test(request):
    img = os.path.abspath(os.path.dirname('album')) + '/media/hair'
    path = os.listdir(img)
    images = Document.objects.first()
    img_path = Document.objects.first().photo.path
    base = os.path.basename(img_path)
    context = {
        'path':path,
        'img':img,
        'images':images,
        'img_path':img_path,
        'base':base,
    }
    return render(request, 'photo/test.html', context)
#!/usr/bin/python3

import cv2
import numpy as np

#im????で表示するwindow名称
ano_window_name = "annotation window"
#imshowで表示しているイメージのすのやつ
show_ano_image = None
#現在の表示ウインドウ大きさ
show_disp_size = (1024, 768)
#今表示している倍率とオフセット左上のところ？どこがいい？
show_scale = 1.0
show_offset = (0,0)
#アノテーションをつけるイメージのファイル名とアノテーションのリスト
ano_imagename = None
ano_items = []
#マウスのオペレーション中に選択されているインデックス
ano_items_idx = -1
# 移動時のスタート地点
start_mouse_pos = None

def _show_shape(img, dsize, offset, scale):
    poff = (max(0,offset[0]), max(0,offset[1]))
    noff = (-min(0,offset[0]), -min(0,offset[1]))
    clip = (int(min(dsize[0]/scale-noff[0], img.shape[1]-poff[0])),int(min(dsize[1]/scale-noff[1], img.shape[0]-poff[1])))
    clipimg = img[poff[1]:poff[1] + clip[1], poff[0]:poff[0] + clip[0]]
    resizeimg = cv2.resize(clipimg, (0,0), fx = scale, fy = scale)
    showimg = np.ones((dsize[1], dsize[0], img.shape[2]), img.dtype) * 255
    noffscale = (int(noff[0]*scale), int(noff[1]*scale))
    showimg[noffscale[1]:noffscale[1] + resizeimg.shape[0], noffscale[0]:noffscale[0] + resizeimg.shape[1]] = resizeimg;
    
    cv2.imshow('dsize{} offset{} scale{}'.format(dsize, offset, scale), showimg)
    
def debug_shape():
    img = cv2.imread("image.jpg")
    
    _show_shape(img, (1024,768), (0,0), 1.0)
    _show_shape(img, (1024,768), (100,100), 1.0)
    _show_shape(img, (1024,768), (-100,-100), 1.0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    _show_shape(img, (1024,768), (0,0), 2.0)
    _show_shape(img, (1024,768), (100,100), 2.0)
    _show_shape(img, (1024,768), (-100,-100), 2.0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    _show_shape(img, (1024,768), (0,0), 0.5)
    _show_shape(img, (1024,768), (100,100), 0.5)
    _show_shape(img, (1024,768), (-100,-100), 0.5)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    
def _check_mouse_pos(item, x, y):
    if x >= item[0] and x <= item[0]+item[2] and y >= item[1] and y <= item[1]+item[3]:
        return True
    return False

def _search_mouse_pos_idx(items, x, y):
    for i in range(len(items)):
        if _check_mouse_pos(items[i], x, y):
            return i
    return -1

def _makeshowimg(img, items, itemidx, dsize = None, offset = (0,0), scale = 1.0):
    
    if dsize is None:
        dsize = (min(img.shape[1], 1024), min(img.shape[0], 768))
        
    for i in range(len(items)):
        item = items[i]
        if i == itemidx:
            col = (0,255,0)
        else:
            col = (0,0,255)
        cv2.rectangle(img, (item[0],item[1]), (item[0]+item[2], item[1]+item[3]), col, 2)
    # ↑↑↑↑↑↑リサイズ前の処理
    poff = (max(0,offset[0]), max(0,offset[1]))
    noff = (-min(0,offset[0]), -min(0,offset[1]))
    clip = (int(min(dsize[0]/scale-noff[0], img.shape[1]-poff[0])),int(min(dsize[1]/scale-noff[1], img.shape[0]-poff[1])))
    clipimg = img[poff[1]:poff[1] + clip[1], poff[0]:poff[0] + clip[0]]
    resizeimg = cv2.resize(clipimg, (0,0), fx = scale, fy = scale)
    showimg = np.ones((dsize[1], dsize[0], img.shape[2]), img.dtype) * 255
    noffscale = (int(noff[0]*scale), int(noff[1]*scale))
    showimg[noffscale[1]:noffscale[1] + resizeimg.shape[0], noffscale[0]:noffscale[0] + resizeimg.shape[1]] = resizeimg

    return showimg

def makeshowimg():
    global show_ano_image, ano_items, ano_items_idx, show_disp_size, show_offset, show_scale
    return _makeshowimg(show_ano_image.copy(), ano_items, ano_items_idx, show_disp_size, show_offset, show_scale)

#位置格納関数
def mouse_event(event, x, y, flags, param):
    #グローバル変数を利用
    global show_ano_image, ano_items, ano_items_idx, show_disp_size, show_offset, show_scale
    global start_mouse_pos, move_roi, move_roi_offset

    imgx = int((x/show_scale) + show_offset[0])
    imgy = int((y/show_scale) + show_offset[1])

    #マウス左ボタン押下時
    if event == cv2.EVENT_LBUTTONDBLCLK:
        _search_idx = _search_mouse_pos_idx(ano_items, imgx, imgy)
        if _search_idx == -1:
            # アイテム新規作成
            ano_items_idx = -1
            ano_items.append([imgx, imgy, 25, 25])
            ano_items_idx = len(ano_items)-1
            cv2.imshow(ano_window_name, makeshowimg())
        
    elif event == cv2.EVENT_LBUTTONDOWN:
        _search_idx = _search_mouse_pos_idx(ano_items, imgx, imgy)
        if _search_idx == -1:       #画面移動
            start_mouse_pos = (imgx, imgy)
        else:       #アイテム選択
            ano_items_idx = _search_idx
            item = ano_items[ano_items_idx]
            if imgx < item[0]+(item[2]/2) or imgy < item[1]+(item[3]/2):  #アイテム移動
                move_roi = 1
                move_roi_offset = (item[0]-imgx, item[1]-imgy)
            else:          #アイテム大きさ変更
                move_roi = 2
        cv2.imshow(ano_window_name, makeshowimg())
        
    #マウス左ボタン解放時
    elif event == cv2.EVENT_LBUTTONUP:
        if start_mouse_pos is not None:
            show_offset = (show_offset[0] + start_mouse_pos[0] - imgx , show_offset[1] + start_mouse_pos[1] - imgy)
            start_mouse_pos = None
        else:
            if ano_items_idx >= 0:
                item = ano_items[ano_items_idx]
                if move_roi == 1:
                    item[0:2] = imgx + move_roi_offset[0], imgy + move_roi_offset[1]
                elif move_roi == 2:
                    item[2:4] = imgx - item[0], imgy - item[1]
                    # Rectの正規化
                    if item[2] < 0:
                        item[0] = item[0] + item[2]
                        item[2] = item[2] * -1
                    if item[3] < 0:
                        item[1] = item[1] + item[3]
                        item[3] = item[3] * -1
                    if item[2] < 4 or item[3] < 4:             #サイズが小さいものは削除
                        del ano_items[ano_items_idx]
        cv2.imshow(ano_window_name, makeshowimg())
        
    elif event == cv2.EVENT_RBUTTONDBLCLK:
        _search_idx = _search_mouse_pos_idx(ano_items, imgx, imgy)
        if ano_items_idx != -1 and _search_idx == ano_items_idx:
            del ano_items[ano_items_idx]
            ano_items_idx = -1
            cv2.imshow(ano_window_name, makeshowimg())
            
    elif event == cv2.EVENT_RBUTTONDOWN:
        pass
    elif event == cv2.EVENT_RBUTTONUP:
        pass

    elif event == cv2.EVENT_MOUSEMOVE:
        if (flags & cv2.EVENT_FLAG_RBUTTON) != 0:
            pass
        elif (flags & cv2.EVENT_FLAG_LBUTTON) != 0:
            if start_mouse_pos is not None:
                show_offset = (show_offset[0] + start_mouse_pos[0] - imgx , show_offset[1] + start_mouse_pos[1] - imgy)
            else:
                if ano_items_idx >= 0:
                    item = ano_items[ano_items_idx]
                    if move_roi == 1:
                        item[0:2] = imgx + move_roi_offset[0], imgy + move_roi_offset[1]
                    else:
                        item[2:4] = imgx - item[0], imgy - item[1]
            cv2.imshow(ano_window_name, makeshowimg())

    # elif event == cv2.EVENT_RBUTTONUP:
    #     if show_scale > 1.9:
    #         show_scale = 0.5
    #     else:
    #         show_scale += 0.5
    #     cv2.imshow(ano_window_name, makeshowimg())
            
    elif event == cv2.EVENT_MOUSEWHEEL:   # macosだとこないっぽい
        pass
    elif event == cv2.EVENT_MOUSEHWHEEL:  # macosだとこないっぽい
        old_scale = show_scale
        if flags < 0:
            if show_scale >= 0.2:
                show_scale = show_scale - 0.1
        else:
            if show_scale <= 4.9:
                show_scale = show_scale + 0.1

        # ds = np.array(show_disp_size)/2
        # ims = ds / show_scale + show_offset
        # show_offset = ((ds - ims/old_scale)*show_scale).astype(np.int)
        # print("ds",ds,"ims",ims,"show_offset", show_offset, "show_scale", show_scale, "old_scale", old_scale)
        cv2.imshow(ano_window_name, makeshowimg())

        # show_offset = (0,0)
        # show_scale = 1.0
        # start_mouse_pos = None
        # cv2.imshow(ano_window_name, makeshowimg())
        
def makeanno(anolist):
    global ano_window_name, ano_imagename, ano_items, ano_items_idx, show_ano_image
    
    ano_items = []
    if type(anolist) is str:
        ano_imagename = anolist
    elif type(anolist) is list:
        ano_imagename = anolist[0]
        if type(anolist[1]) is list:
            ano_items = anolist[1]
        else:
            ano_items = []
    else:
        print("parameter error.")
        return None

    cv2.namedWindow(ano_window_name)
    cv2.setMouseCallback(ano_window_name, mouse_event)
    
    show_ano_image = cv2.imread(ano_imagename)
    while True:
        cv2.imshow(ano_window_name, makeshowimg())
        c = cv2.waitKey(0)
        if c == ord('q'):
            break
        
    cv2.destroyWindow(ano_window_name)
    return [ano_imagename, ano_items]
    
if __name__ == "__main__":
    makeanno("image.jpg")
    

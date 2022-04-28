#!/usr/bin/python3

import cv2
import numpy as np

#im????で表示するwindow名称
ano_window_name = "annotation window"
# helpを表示するかどうか
show_help = True
show_help_text = ["n:next p:previus a:append c:copy d:delete q:save and quit e:save and quit !:force quit", "Allow keys:move position j,k:frame width i,m:frame height home:frame bigger end:frame smoller"]
#imshowで表示しているイメージのすのやつ
show_ano_image = None
#現在の表示ウインドウ大きさ
show_disp_size = (1440,1024)
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
#枠選択モード
move_roi = 0
move_roi_offset = None

def _check_mouse_pos(item, x, y):
    if x >= item[0] and x <= item[0]+item[2] and y >= item[1] and y <= item[1]+item[3]:
        return True
    return False

def _search_mouse_pos_idx(items, idx, x, y):
    if idx != -1:
        if _check_mouse_pos(items[idx], x, y):
            return idx
    for i in range(len(items)):
        if _check_mouse_pos(items[i], x, y):
            return i
    return -1

def scale_updown(changes):
    global show_disp_size, show_offset, show_scale
    dispcenter = np.array(show_disp_size) / 2
    imgc = dispcenter / show_scale + np.array(show_offset)
    show_scale = show_scale + changes
    if show_scale <= 0.1:
        show_scale = 0.1
    elif show_scale >= 5.0:
        show_scale = 5.0
    show_offset = (imgc - (dispcenter / show_scale)).astype(np.int)

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
    global show_ano_image, ano_items, ano_items_idx, show_disp_size, show_offset, show_scale, show_help, show_help_text
    
    _img = _makeshowimg(show_ano_image.copy(), ano_items, ano_items_idx, show_disp_size, show_offset, show_scale)
    if show_help is not None:
        pos = [0, 0]
        for t in show_help_text:
            pos[1] = pos[1] + 25
            cv2.putText(_img, text=t, org=pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0,255,0), thickness=1, lineType=cv2.LINE_4)
        
    return _img

#位置格納関数
def mouse_event(event, x, y, flags, param):
    #グローバル変数を利用
    global show_ano_image, ano_items, ano_items_idx, show_disp_size, show_offset, show_scale
    global start_mouse_pos, move_roi, move_roi_offset

    imgx = int((x/show_scale) + show_offset[0])
    imgy = int((y/show_scale) + show_offset[1])

    #マウス左ボタン押下時
    if event == cv2.EVENT_LBUTTONDBLCLK:
        _search_idx = _search_mouse_pos_idx(ano_items, ano_items_idx, imgx, imgy)
        if _search_idx == -1:
            # アイテム新規作成
            ano_items_idx = -1
            ano_items.append([imgx, imgy, 25, 25])
            ano_items_idx = len(ano_items)-1
            cv2.imshow(ano_window_name, makeshowimg())
        
    elif event == cv2.EVENT_LBUTTONDOWN:
        move_roi = 0
        _search_idx = _search_mouse_pos_idx(ano_items, ano_items_idx, imgx, imgy)
        if _search_idx != -1 and _search_idx == ano_items_idx:
            item = ano_items[ano_items_idx]
            if imgx < item[0]+(item[2]*0.75) or imgy < item[1]+(item[3]*0.75):  #アイテム移動
                move_roi = 1
                move_roi_offset = (item[0]-imgx, item[1]-imgy)
            else:          #アイテム大きさ変更
                move_roi = 2
        else:
            if _search_idx != -1:
                ano_items_idx = -1
            start_mouse_pos = (imgx, imgy)
        cv2.imshow(ano_window_name, makeshowimg())
        
    #マウス左ボタン解放時
    elif event == cv2.EVENT_LBUTTONUP:
        if start_mouse_pos is not None:
            show_offset = (show_offset[0] + start_mouse_pos[0] - imgx , show_offset[1] + start_mouse_pos[1] - imgy)
            start_mouse_pos = None
        if ano_items_idx == -1:
            ano_items_idx = _search_mouse_pos_idx(ano_items, ano_items_idx, imgx, imgy)
        else:
            item = ano_items[ano_items_idx]
            if move_roi == 0:
                pass
            elif move_roi == 1:
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
                ano_items_idx = -1
            move_roi = 0
        cv2.imshow(ano_window_name, makeshowimg())
        
    elif event == cv2.EVENT_RBUTTONDBLCLK:
        _search_idx = _search_mouse_pos_idx(ano_items, ano_items_idx, imgx, imgy)
        if ano_items_idx != -1 and _search_idx == ano_items_idx:
            del ano_items[ano_items_idx]
            ano_items_idx = -1
            cv2.imshow(ano_window_name, makeshowimg())
            
    elif event == cv2.EVENT_RBUTTONDOWN:
        pass
    elif event == cv2.EVENT_RBUTTONUP:
        pass

    elif event == cv2.EVENT_MOUSEMOVE:
        if start_mouse_pos is not None:
            show_offset = (show_offset[0] + start_mouse_pos[0] - imgx , show_offset[1] + start_mouse_pos[1] - imgy)
        elif ano_items_idx >= 0 and move_roi != 0:
            item = ano_items[ano_items_idx]
            if move_roi == 1:
                item[0:2] = imgx + move_roi_offset[0], imgy + move_roi_offset[1]
            elif move_roi == 2:
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
        if flags < 0:
            scale_updown(-0.1)
        elif flags > 0:
            scale_updown(0.1)
        cv2.imshow(ano_window_name, makeshowimg())
        
def makeanno(anolist, anolist_no = None):
    global ano_window_name, ano_imagename
    global show_ano_image, ano_items, ano_items_idx, show_disp_size, show_offset, show_scale, show_help, show_help_text
    global start_mouse_pos, move_roi, move_roi_offset
    
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

    if anolist_no is None:
        ano_window_name = "#### {}".format(ano_imagename)
    else:
        ano_window_name = "#{} {}".format(anolist_no+1, ano_imagename)
    cv2.namedWindow(ano_window_name)
    cv2.setMouseCallback(ano_window_name, mouse_event)
    
    show_ano_image = cv2.imread(ano_imagename)
    #画面初期化
    ano_items_idx = -1
    show_scale = int(min(show_disp_size[0] / show_ano_image.shape[1], show_disp_size[1] / show_ano_image.shape[0])*10)/10
    show_offset = (-int((show_disp_size[0] - show_ano_image.shape[1]*show_scale)/2), -int((show_disp_size[1] - show_ano_image.shape[0]*show_scale)/2))
    start_mouse_pos = None
    move_roi = 0
    move_roi_offset = None
    
    while True:
        cv2.imshow(ano_window_name, makeshowimg())
        c = cv2.waitKey(0)
        if c == ord('d') or c == 255: #削除 255=delキー
            if ano_items_idx != -1:
                del ano_items[ano_items_idx]
                ano_items_idx = -1
        elif c == ord('c'): #コピー 
            if ano_items_idx != -1:
                ano_items.append([ano_items[ano_items_idx][0]+5, ano_items[ano_items_idx][1]+5, ano_items[ano_items_idx][2], ano_items[ano_items_idx][3]])
                ano_items_idx = len(ano_items)-1
        elif c == ord('a'): # 新規
            dispcenter = np.array(show_disp_size) / 2
            imgc = (dispcenter / show_scale + np.array(show_offset)).astype(np.int)
            while True:
                _search_idx = _search_mouse_pos_idx(ano_items, ano_items_idx, imgc[0]+10, imgc[1]+10)
                if _search_idx == -1:
                    break
                imgc = imgc + 5
            ano_items.append([imgc[0], imgc[1], 20, 20])
            ano_items_idx = len(ano_items)-1
        elif c == ord('h'):
            if show_help is None:
                show_help = 1
            else:
                show_help = None
        elif c == 85: #page up
            scale_updown(0.1)
        elif c == 86: #page down
            scale_updown(-0.1)
        elif c == 81:  # ←
            if ano_items_idx != -1 and ano_items[ano_items_idx][0] > 0:
                ano_items[ano_items_idx][0] = ano_items[ano_items_idx][0] - 1
        elif c == 82:  # ↑
            if ano_items_idx != -1 and ano_items[ano_items_idx][1] > 0:
                ano_items[ano_items_idx][1] = ano_items[ano_items_idx][1] - 1
        elif c == 83:  # →
            if ano_items_idx != -1 and ano_items[ano_items_idx][0] + ano_items[ano_items_idx][2] < show_ano_image.shape[1]:
                ano_items[ano_items_idx][0] = ano_items[ano_items_idx][0] + 1
        elif c == 84:  # ↓
            if ano_items_idx != -1 and ano_items[ano_items_idx][1] + ano_items[ano_items_idx][3] < show_ano_image.shape[0]:
                ano_items[ano_items_idx][1] = ano_items[ano_items_idx][1] + 1
        elif c == 80:  # HOME
            item = ano_items[ano_items_idx]
            if item[2] > 4 and item[3] > 4:
                item[2] = item[2] - 1
                item[3] = item[3] - 1
        elif c == 87:
            item = ano_items[ano_items_idx]
            if item[0] + item[2] < show_ano_image.shape[1] and item[1] + item[3] < show_ano_image.shape[0]:
                item[2] = item[2] + 1
                item[3] = item[3] + 1
        elif c == ord('j'):
            item = ano_items[ano_items_idx]
            if item[2] > 4:
                item[2] = item[2] - 1
        elif c == ord('k'):
            item = ano_items[ano_items_idx]
            if item[0] + item[2] < show_ano_image.shape[1]:
                item[2] = item[2] + 1
        elif c == ord('i'):
            item = ano_items[ano_items_idx]
            if item[3] > 4:
                item[3] = item[3] - 1
        elif c == ord('m'):
            item = ano_items[ano_items_idx]
            if item[1] + item[3] < show_ano_image.shape[0]:
                item[3] = item[3] + 1
        else:
            break
    cv2.destroyWindow(ano_window_name)
    return c,[ano_imagename, ano_items]
    
if __name__ == "__main__":
    makeanno("image.jpg")
    

import cv2
from os import path as ospath
import subprocess

def create_detector(img):
    (_,return_obj)=detector.detectAndCompute(img,None)
    return return_obj

path=ospath.dirname(ospath.abspath(__file__))+'\\'

video_path="ここに動画のパス"

#チャンピオン時と結果の画面の判定用画像
champ_img=cv2.imread(path+'champ.png')
summary_img=cv2.imread(path+'summary.png')

#特徴点のマッチングで判定
detector=cv2.AKAZE_create()
bf=cv2.BFMatcher(cv2.NORM_HAMMING)

#動画ファイル読み込み&プロパティ取得
input_video=cv2.VideoCapture(video_path)
fps=input_video.get(cv2.CAP_PROP_FPS)
total_frame_count=input_video.get(cv2.CAP_PROP_FRAME_COUNT)

#現在のフレーム
current_frame=0

#チャンピオン画面判定されたフレーム
champ_f=0
comp_des=create_detector(champ_img)

#残り2分までスキップ
input_video.set(cv2.CAP_PROP_POS_FRAMES,total_frame_count-fps*120)

#チャンピオン画面判定されるまで繰り返す
while input_video.isOpened():
    ret,img=input_video.read()

    if ret:
        clip_img=cv2.cvtColor(img[400:600,400:1520],cv2.COLOR_BGR2GRAY)

        try:
            target_des=create_detector(clip_img)

            matches=bf.match(target_des,comp_des)
            dist=[m.distance for m in matches]
            res=sum(dist)/len(dist)
        except:
            res=100000

        if res<50:
            cv2.imwrite(path+'out\\champi.png',img)
            champ_f=input_video.get(cv2.CAP_PROP_POS_FRAMES)
            break

    else:
        break
    #1秒スキップ
    input_video.set(cv2.CAP_PROP_POS_FRAMES,input_video.get(cv2.CAP_PROP_POS_FRAMES)+fps-1)

if champ_f==0:
    print('見つかりませんでした')

else:
    #結果画面判定
    comp_des=create_detector(summary_img)

    summary=None
    summary_f=0

    #20秒スキップ
    input_video.set(cv2.CAP_PROP_POS_FRAMES,input_video.get(cv2.CAP_PROP_POS_FRAMES)+fps*20)

    while input_video.isOpened():
        ret,img=input_video.read()

        if ret:
            clip_img=cv2.cvtColor(img[112:192,700:1220],cv2.COLOR_BGR2GRAY)

            try:
                target_des=create_detector(clip_img)

                matches=bf.match(target_des,comp_des)
                dist=[m.distance for m in matches]
                res=sum(dist)/len(dist)
            except:
                res=100000

            if res<20:
                summary=img
                summary_f=input_video.get(cv2.CAP_PROP_POS_FRAMES)
            elif summary_f!=0:
                break

        else:
            break

        input_video.set(cv2.CAP_PROP_POS_FRAMES,input_video.get(cv2.CAP_PROP_POS_FRAMES)+fps//2-1)
    
    cv2.imwrite(path+'out\\summary__.png',summary)

input_video.release()

subprocess.call("ffmpeg -i \""+video_path+"\" -c copy -ss "+str(champ_f//fps-20)+" -t 40 out\\out.mp4")
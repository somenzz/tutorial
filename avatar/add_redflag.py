from PIL import Image
import fire
from pathlib import Path

def add_five_starred_red_flag(origin_img: str, target_img : str = None):

    assert origin_img, "请指定原始图片的路径"
    origin_img_path = Path(origin_img)
    assert origin_img_path.exists(), "原始图片的路径必须是真实的"
    
    if target_img is None:
        target_img = origin_img_path.with_name(f"new_{origin_img_path.name}").as_posix()
    
    redflag = Image.open('redflag.png')
    avatar = Image.open(origin_img)

    # 获取国旗的尺寸
    x,y = redflag.size
    # 根据需求，设置左上角坐标和右下角坐标（截取的是正方形）
    area = redflag.crop((262,100, y+62,y-100))

    # 获取头像的尺寸
    w,h = avatar.size
    # 将区域尺寸重置为头像的尺寸
    area = area.resize((w,h))
    # 透明渐变设置
    for i in range(w):
        for j in range(h):
            color = area.getpixel((i, j))
            alpha = 220-(i+1)//3
            if alpha < 0:
                alpha=0
            color = color[:-1] + (alpha, )
            area.putpixel((i, j), color)

    avatar.paste(area,(0,0),area)
    avatar.save(target_img)
    print(f"新头像路径：{target_img}")


if __name__ == '__main__':
    fire.Fire(add_five_starred_red_flag)
    

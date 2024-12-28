# Copyright (c) 2024 misetteichan
# Licensed under the MIT License. See LICENSE file for details.

from solid2 import *
from os import path, makedirs


def __rounded_cube(width: int, height: int, depth: int, radius: int):
    w = width - radius * 2
    h = height - radius * 2
    body = cube(w, height, depth).translate(radius, 0, 0)
    body += cube(width, h, depth).translate(0, radius, 0)
    r = cylinder(h=depth, r=radius).translate(radius, radius, 0)
    corner = r
    corner += r.translate(w, 0, 0)
    corner += r.translate(0, h, 0)
    corner += r.translate(w, h, 0)
    return body + corner


face_width, face_height, face_depth, face_radius = 400, 400, 100, 30
body_depth = 300


def __head():
    radius = 150
    r = cylinder(h=face_height, r=radius)
    h = cube(face_width, face_height, body_depth - radius).translate(0, 0, radius)
    h += cube(face_width, face_height - radius, body_depth).translate(0, radius, 0)
    h += r.rotate(0, 90, 0).translate(0, radius, radius)
    b = intersection()(h, __rounded_cube(face_width, face_height, body_depth, 30))
    return b


def __foot(hole):
    width, height, depth = 140, 200, 50
    h = cube(width, depth, height).translate(10,0,0)
    o = cylinder(h=30, r=50).rotate(90, 0, 0)
    f = h + h.mirror(1, 0, 0)
    if hole:
        f -= cylinder(h=depth, r=40).rotate(90, 0, 0).translate(0,depth,height/2).translate(0, 0, 0)
    o += f.translate(0, -(depth+30), -height/2)
    return o


def __panel(depth):
    def eye(h, r):
        return cylinder(h=h, r=r)

    def eyes(h, r, width):
        e = eye(h, r).translate(-width / 4, 40, 0)
        return e + e.mirror(1, 0, 0)

    def face(width, height, depth):
        mouth = lambda w, h: cube(w, h, depth).translate(-(w / 2), -60, 0)
        # e = eyes(depth, 25, width)
        e = eyes(depth, 30, width)
        f = e + mouth(120, 35)
        return f.translate(width / 2, height / 2, 0)

    def buttons(width, depth):
        w, h = 65, 35
        steps = (width - w) / 2 * 0.8
        button = cube(w, h, depth).translate(width/2 - w/2, h * 1.5, 0)
        return button + button.translate(-steps, 0, 0) + button.translate(steps, 0, 0)

    lcd_w, lcd_h = 320, 240
    f = face(lcd_w, lcd_h, depth).translate((face_width - lcd_w) / 2, (face_height - lcd_h) / 2, 0)
    f += buttons(lcd_w, depth).translate((face_width - lcd_w) / 2, 0, 0)
    return f.translate(0, 0, -depth)


def main(size, holes, is_single_color, stl, out='out'):
    set_global_fn(100)
    head, foot, face, panel, thin_panel = [o.scale(size/face_width) for o in [
       __head(),
       __foot(holes >= 2).translate(face_width/2, 0, (body_depth + face_depth)/2),
       __rounded_cube(face_width, face_height, face_depth, face_radius).translate(0, 0, body_depth),
       __panel(face_depth).translate(0, 0, face_depth + body_depth),
       __panel(face_depth/8).translate(0, 0, face_depth + body_depth),
    ]]
    
    # 穴のサイズはScale関係なく同じ
    hole = cylinder(h=5, r=0.3).rotate(90, 0, 0).translate(size/2, 0, size/2)
    if holes >= 1:
        head -= hole.translate(0, size, 0)
    if holes >= 2:
        head -= hole.translate(0, 5, 0)
        foot -= cylinder(h=10, r=0.3).rotate(90, 0, 0).translate(size/2, 0, size/2)

    if is_single_color:
        pass
    else:
        # ちょっとだけずらすことで確実に同色のフィラメントでサポートが作られることを期待
        foot = foot.translateZ(-0.3)

    if not path.exists(out):
        makedirs(out)

    scale = 0.9
    inner = head.scale(scale).translate(
        size*(1-scale)/2,
        size*(1-scale)/2,
        body_depth*(size/face_width)*(1-scale))
    diameter = 5
    inner += cylinder(h=5, r=diameter/2).translate((size)/2, (size)/2+1, 0)

    depth = body_depth * size / face_width
    poll = cylinder(h=depth, r=diameter/2+0.5).translate((size)/2, (size)/2+1, 0)
    poll -= cylinder(h=depth, r=diameter/2).translate((size)/2, (size)/2+1, 0)

    new_body = (head - inner + poll + foot).color('red')

    new_face = (face - panel).color('black')
    thin_panel = thin_panel.color('white')

    model = new_body + new_face + thin_panel

    def save_as_stl(obj, name):
        from os import remove
        obj.save_as_stl(f'{out}/{name}.stl')
        remove(f'{out}/{name}.stl.scad')

    if stl:
        if is_single_color:
            save_as_stl(model, 'all')
        else:
            save_as_stl(new_face, 'face')
            save_as_stl(thin_panel, 'panel')
            save_as_stl(new_body, 'body')
    else:
        model.rotateX(90).save_as_scad(f'{out}/model.scad')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=12)
    parser.add_argument('--hole', type=int, choices=[0, 1, 2], default=0)
    parser.add_argument('--single', action='store_true')
    parser.add_argument('--stl', action='store_true')
    args = parser.parse_args()

    main(size=args.size, holes=args.hole, is_single_color=args.single, stl=True)

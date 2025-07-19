from pyaccsharedmemory import Vector3f
from pyaccsharedmemory import ContactPoint
from pyaccsharedmemory import Wheels
from pyaccsharedmemory import CarDamage
import quaternion
from enum import Enum

def pack_f44_quaternion(q_lst : list[quaternion.quaternion]) -> str:
    formated_lst = [pack_quaternion(q) for q in q_lst]
    content = ';'.join(formated_lst)
    return f'[{content}]'

def pack_quaternion(q : quaternion.quaternion) -> str :
    return f'{q.x:.6f};{-q.y:.6f};{q.z:.6f};{-q.w:.6f}'

def pack_quaternion_temp(q : quaternion.quaternion) -> str :
    return f'[{-q.x};{q.y};{-q.z};{q.w}]'

def pack_f3(f3 :Vector3f) -> str:
    return f'[{f3.x:.6f};{f3.y:.6f};{f3.z:.6f}]'
def pack_f3_cfg(value :str) ->str:
    return f'[{value.replace(",",";")}]'

def pack_contact_point(con : ContactPoint) -> str:
    front_left = f'{con.front_left.x:.6f};{con.front_left.y:.6f};{con.front_left.z:.6f};{0:.6f}'
    front_right = f'{con.front_right.x:.6f};{con.front_right.y:.6f};{con.front_right.z:.6f};{0:.6f}'
    rear_left = f'{con.rear_left.x:.6f};{con.rear_left.y:.6f};{con.rear_left.z:.6f};{0:.6f}'
    rear_right = f'{con.rear_right.x:.6f};{con.rear_right.y:.6f};{con.rear_right.z:.6f};{0:.6f}'

    return f'[{front_left};{front_right};{rear_left};{rear_right}]' 

def pack_f4_list(list :list):
    return f'[{list[0]};{list[1]};{list[2]};{list[3]}]'

def pack_f4_wheels(wheel : Wheels) -> str:
    return  f'[{wheel.front_left:.6f};{wheel.front_right:.6f};{wheel.rear_left:.6f};{wheel.rear_right:.6f}]'

def pack_f4_car_damage(dmg :CarDamage) -> str:
    return  f'[{dmg.front:.6f};{dmg.rear:.6f};{dmg.left:.6f};{dmg.right:.6f}]'

def pack_array_2f(arr) -> str:
    # Assuming arr is an iterable with two elements
    return f'[{arr.x:.6f};{arr.y:.6f}]'

def pack_str_enum(enum : Enum) -> str:
    return enum.name

def pack_message(name :str ,type :str,data :str) -> str:
    return ",".join([name,type,data])
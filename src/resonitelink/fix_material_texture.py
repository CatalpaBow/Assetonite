import sys
from typing import NoReturn
from dataclasses import dataclass
from collections.abc import Iterable
import asyncio

from pathlib import Path

from pyresonitelink import client
from pyresonitelink.data import messages
from pyresonitelink.data.responses import Response ,AssetData
from pyresonitelink.data.workers import Slot,Component


class SlotNotFoundError(LookupError):
    pass

class ResonitelinkResponseError(Exception):
    def __init__(self, request_type:str,error_info:str):
        message = (
                f"Resonitelink response error"
                f"request_type:{request_type}"
                f"error_info:{error_info}"
                )
        super().__init__(message)

class ResonitelinkWrapper:
    def __init__(self, reso_link:client.Client):
        self.reso_link = reso_link

    async def connect(self,port:int,host:str):
        await self.reso_link.connect(port,host)

    async def find_child_by_name(self, slot: Slot, name: str) -> Slot: 
        child = next(
            (c for c in slot.children if c.name.value == name),
            None,
        )
        if child is None:
            raise SlotNotFoundError(
                f"No child slot '{name}' was found in parent "
                f"(id={slot.id}, name='{slot.name}')"
            )

        msg = messages.GetSlot(slotId=child.id, depth=1)
        response = await self.reso_link.get_slot(msg)

        if not response.success:
            raise ResonitelinkResponseError("get_slot",response.errorInfo)

        return response.data
    
    async def get_root_slot(self) -> Slot:
        msg = messages.GetSlot(slotId="Root", depth=1)
        response = await self.reso_link.get_slot(msg)

        if not response.success:
            raise ResonitelinkResponseError("get_slot",response.errorInfo)
        return response.data
        
    async def get_slot_by_slot(self,slot:Slot,depth:int,includeComponentData:bool) -> Slot:
        msg = messages.GetSlot(slotId=slot.id,depth=depth,includeComponentData=includeComponentData)
        response = await self.reso_link.get_slot(msg)
        
        if not response.success:
            raise ResonitelinkResponseError("get_slot",response.errorInfo)
        return response.data
    
    async def get_component(self,id:str) -> Component:
        msg = messages.GetComponent(componentId=id)
        response = await self.reso_link.get_component(msg)
        if not response.success:
            raise ResonitelinkResponseError("get_component",response.errorInfo)

        return response.data
    
    async def import_texture_2d(self,path:str) -> str:
        msg = messages.ImportTexture2DFile(filePath=path)
        response = await self.reso_link.request(msg)
        if(
            response.success
            and isinstance(response, AssetData)
            and response.assetURL
        ):
            return response.assetURL
        else:
            raise ResonitelinkResponseError("import_texture_2d",response.errorInfo)

async def test():
    car_model_name = "toyota_gt86_new.fbx"
    port = 52961
    reso_link = ResonitelinkWrapper(client.Client())
    await reso_link.connect(port,"localhost")

    slot_root = await reso_link.get_root_slot()
    slot_car_model = await reso_link.find_child_by_name(slot_root,car_model_name)
    slot_assets = await reso_link.find_child_by_name(slot_car_model,"Assets")
    
    slots_material = [
        child 
        for child in slot_assets.children 
        if "Material: " in child.name.value
    ]

    if not slots_material:
        raise LookupError(
            f"No child slot with name containing 'Material: ' found"
            f"(parent_slot='{slot_assets.name.value}')"
        )
    
    slots_material_new:list[Slot] = [
        await reso_link.get_slot_by_slot(slot=slot,depth=0,includeComponentData=True)
        for slot in slots_material
    ]

    #スロット名から'Material: 'を消し、マテリアル名だけにする
    materials = {
        slot.name.value.removeprefix("Material: "): next(
            (
                component
                for component in slot.components
                if component.componentType
                == "[FrooxEngine]FrooxEngine.PBS_Metallic"
            ),
            None,
        )
        for slot in slots_material_new
    }
    
    



def find_component_by_type(components:Iterable[Component],type:str) -> Component | None:
    for component in components:
        if component.componentType == "[FrooxEngine]FrooxEngine.PBS_Metallic":
            return component
    return None

if __name__ == "__main__":
    asyncio.run(test())
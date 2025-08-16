from fbx import*
from typing import Generator

def node_recursion(node: FbxNode) -> Generator[FbxNode, None, None]:
    for i in range(node.GetChildCount()):
        child = node.GetChild(i)
        yield child
        yield from node_recursion(child) 

def get_mats(node :FbxNode) -> list[FbxSurfaceMaterial]:
    mats = []
    for k in range(node.GetMaterialCount()):
        mats.append(node.GetMaterial(k))
    return mats

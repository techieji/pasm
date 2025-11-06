from __future__ import annotations
from typing import *
from dataclasses import dataclass

@dataclass
class Location:
    binimage: BinaryImage
    idx: int

class BinaryImage(bytearray):
    def __init__(self, *args: list[Any], **kwargs: dict[Any, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.refs_from: list[Pointer] = []    # The location that a pointer refers to
        self.refs_to: list[Pointer] = []      # The place where the pointer is used

    def pointer_at(self, size: int, i: int) -> Pointer:
        p = Pointer(size, Location(self, i))
        self.refs_from.append(p)
        return p

    def extend(self, v: Any) -> None:
        if isinstance(v, BinaryImage):
            raise TypeError("BinaryImages can only be combined with combine.")
        if isinstance(v, Pointer):
            v.add_use(self, len(self))
            self.refs_to.append(v)
            super().extend(v.repr)
        else:
            super().extend(v)

    def combine(self, v: BinaryImage) -> None:
        '''Destructively add another binary image to this one.

        This method changes all pointers in the second binary image to point from and to
        this one: pointer resolution will only modify this image, not the other.'''
        for p in v.refs_from:
            if p.dest is not None:
                p.set_dest(self, len(self) + p.dest.idx)
                self.refs_from.append(p)
        for p in v.refs_to:
            for use in p.uses:
                if use.binimage is v:
                    use.binimage = self
                    use.idx += len(self)
        bytearray.extend(self, v)

class Pointer:
    '''Pointer class to ease some management in BinaryImages.

    Constructing a binary file sometimes requires referring to places that haven't been
    generated yet. This class provides a placeholder that can be resolved to
    an actual location later, and which can resolve all previous and subsequent
    uses of itself to valid code.
    '''
    def __init__(self, size: int, dest: Optional[Location] = None):
        self.size = size
        self.uses: list[Location] = []
        self.dest = dest

    @property
    def repr(self) -> bytes:
        if self.dest is None:
            return b'\x00' * self.size
        return self.dest.idx.to_bytes(self.size, 'little')    # TODO make endianness configurable

    def get_byte_at(self) -> Optional[bytes]:
        if self.dest is not None:
            return self.dest.binimage[self.dest.idx].to_bytes()
        return None

    def add_use(self, binimage: BinaryImage, idx: int) -> None:
        self.uses.append(Location(binimage, idx))

    def resolve(self) -> None:
        if self.dest is None:
            raise ValueError("Cannot resolve without destination!")
        if not all(dest.binimage is self.dest.binimage for dest in self.uses):
            raise ValueError("Not all uses are resolved!")
        for use in self.uses:
            use.binimage[use.idx:use.idx+self.size] = self.repr

    def set_dest(self, binimage: BinaryImage, idx: int) -> None:
        self.dest = Location(binimage, idx)

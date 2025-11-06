from binimage import BinaryImage, Pointer, Location
import pytest
# Add test dependencies

def test_pointer_at():
    bi = BinaryImage(b'01234567')
    p = bi.pointer_at(4, 4)
    assert p.repr == b'\x04\x00\x00\x00'
    assert len(bi.refs_from) == 1
    assert bi.refs_from[0] is p
    assert len(bi.refs_to) == 0
    assert p.get_byte_at() == b'4'

def test_unresolved_pointer_at():
    p = Pointer(4)
    assert p.get_byte_at() is None

def test_extend_pointer():
    bi = BinaryImage(b'01234567')
    p = Pointer(4, Location(bi, 4))
    bi.extend(p)
    assert bi == b'01234567\x04\x00\x00\x00'
    assert len(bi.refs_from) == 0      # since the pointer was externally created
    assert len(bi.refs_to) == 1
    assert bi.refs_to[0] is p

def test_extend_binimage():
    bi1 = BinaryImage(b'0123')
    bi2 = BinaryImage(b'4567')
    with pytest.raises(TypeError):
        bi1.extend(bi2)

def test_extend_default():
    bi1 = BinaryImage(b'0123')
    bi1.extend(b'4567')
    assert bi1 == b'01234567'

def test_resolve_pointer_basic():
    bi = BinaryImage(b'01234567')
    p = Pointer(4)
    bi.extend(p)
    assert bi == b'01234567' + p.repr == b'01234567\x00\x00\x00\x00'
    with pytest.raises(ValueError):
        p.resolve()
    p.set_dest(bi, 4)
    p.resolve()
    assert bi == b'01234567\x04\x00\x00\x00'
   
def test_combine_simple():
    'Tests pointers pointing to their own image'
    bi1 = BinaryImage(b'0123')
    bi2 = BinaryImage(b'4567')
    p1 = bi1.pointer_at(4, 1)
    p2 = bi2.pointer_at(4, 2)
    assert p1.get_byte_at() == b'1'
    assert p2.get_byte_at() == b'6'
    bi1.combine(bi2)
    assert len(bi1.refs_from) == 2
    assert len(bi1.refs_to) == 0
    assert p1.get_byte_at() == b'1'
    assert p2.get_byte_at() == b'6'

def test_combine_cross_use():
    'Tests cross-image pointer reference and use'
    bi1 = BinaryImage(b'0123')
    p1 = bi1.pointer_at(4, 2)
    p2 = Pointer(4)
    bi1.extend(p2)
    bi2 = BinaryImage(b'4567')
    p2.set_dest(bi2, 2)
    bi2.extend(p1)
    assert p1.get_byte_at() == b'2'
    assert p2.get_byte_at() == b'6'
    bi1.combine(bi2)
    assert p1.uses[0].binimage is bi1
    assert p2.uses[0].binimage is bi1
    assert p1.get_byte_at() == b'2'
    assert p2.get_byte_at() == b'6'

def test_resolve_combine_cross_image():
    bi1 = BinaryImage(b'0123')
    p1 = bi1.pointer_at(2, 2)
    bi2 = BinaryImage(b'4567')
    p2 = bi2.pointer_at(2, 2)
    bi1.extend(p2)
    bi2.extend(p1)
    with pytest.raises(ValueError):
        p1.resolve()
    with pytest.raises(ValueError):
        p2.resolve()
    bi1.combine(bi2)
    p1.resolve()
    p2.resolve()
    assert bi1 == b'0123\x08\x004567\x02\x00'
 
# TODO Future features:
#  - MemoryImage as subclass of BinaryImage supporting mmaping
#  - BinaryImage accepting assembler instructions
#    - Assembly supporting interpretation and compilation

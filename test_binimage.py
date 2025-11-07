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
    assert len(bi.refs_from) == 1
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
    # NOTE: bi2.refs_from isn't tested because bi2 should not be used!
    assert p1.get_byte_at() == b'1'
    assert p2.get_byte_at() == b'6'
    assert p2.dest.binimage is bi1

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

@pytest.mark.parametrize('shift, expected', [
    (0, b'012\x00345\x04678\x08'),
    (1, b'012\x04345\x08678\x00'),
    (2, b'012\x08345\x00678\x04'),
])
def test_resolve_combine_three_image_crossshift(shift, expected):
    bi1 = BinaryImage(b'012')
    bi2 = BinaryImage(b'345')
    bi3 = BinaryImage(b'678')
    p1 = bi1.pointer_at(1, 0)
    p2 = bi2.pointer_at(1, 0)
    p3 = bi3.pointer_at(1, 0)
    ps = [p1,p2,p3]
    bi1.extend(ps[shift])
    bi2.extend(ps[(shift+1)%3])
    bi3.extend(ps[(shift+2)%3])
    bi1.combine(bi2)
    bi1.combine(bi3)
    p1.resolve()
    p2.resolve()
    p3.resolve()
    assert bi1 == expected

#@pytest.mark.xfail()
def test_resolve_combine_realistic():
    pheader2 = Pointer(2)
    header1 = BinaryImage(b'top-header')
    header1.extend(pheader2)

    pcode = Pointer(2)
    header2 = BinaryImage(b'sub-header')
    header2.extend(pcode)
    pheader2.set_dest(header2, 0)

    code = BinaryImage(b'code')
    pcode.set_dest(code, 0)

    header1.combine(header2)
    header1.combine(code)
    print(pheader2.uses, pheader2.dest)
    pheader2.resolve()
    pcode.resolve()
    assert header1 == b'top-header\x0c\x00sub-header\x18\x00code'
 
# TODO Future features:
#  - MemoryImage as subclass of BinaryImage supporting mmaping
#  - BinaryImage accepting assembler instructions
#    - Assembly supporting interpretation and compilation

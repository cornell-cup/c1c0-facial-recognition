import struct


def compute_checksum(data):
    i = 0
    l = len(data)
    sum_ = 0
    while i < l - 1:
        sum_ += (ord(data[i]) << 8) | ord(data[i + 1])
        if sum_ > 0xffff:
            sum_ -= 0xffff

        i += 2

    if i < l:
        sum_ += ord(data[i]) << 8
        if sum_ > 0xffff:
            sum_ -= 0xffff

    return sum_


# Decodes data or returns None
def decode(input_):
    # FIXME: Check if bytes actually have encode method.
    start = input_.find(bytes("G00").encode("ascii"))
    if start < 0:
        return None

    index = start + 3

    params = {}
    end = False
    try:
        while not end and index < len(input_):
            key = input_[index]
            index += 1
            if key == "S":
                (length,) = struct.unpack_from("B", input_, offset=index)
                index += 1
                (source,) = struct.unpack_from("{}s".format(length), input_,
                                               offset=index)
                params["source"] = source
                index += length
            elif key == "D":
                (length,) = struct.unpack_from("B", input_, offset=index)
                index += 1
                (destination,) = struct.unpack_from("{}s".format(length),
                                                    input_, offset=index)
                params["destination"] = destination
                index += length
            elif key == "T":
                (length,) = struct.unpack_from("B", input_, offset=index)
                index += 1
                (id,) = struct.unpack_from("{}s".format(length), input_,
                                           offset=index)
                params["id"] = id
                index += length
            elif key == "P":
                (length,) = struct.unpack_from("I", input_, offset=index)
                index += 4
                (params["data"],) = struct.unpack_from("{}s".format(length),
                                                       input_, offset=index)
                index += length
            # elif key == "K":
            #     (length,) = struct.unpack_from("B", input, offset=index)
            #     index += 1
            #     (checksum,) = struct.unpack_from(">H", input, offset=index)
            #     params["checksum"] = bytes("{:04x}".format(checksum),
            #     "ascii")
            #     index += length
            elif key == "G":
                k1, k2 = struct.unpack_from("c c", input_, offset=index)
                if k1 == '0' and k2 == '1':
                    end = True
                index += 3
        params['read'] = index
        return params
    except:
        return None


# Encodes data into a binary string
def encode(source, destination, id_, data):
    length = sum([
        3,  # G00 start
        2,  # S{length1} source
        len(source),  # source
        2,  # D{length1} destination
        len(destination),  # destination
        2,  # T{length1} transaction id
        len(id_),  # transaction id
        5,  # P{length4}
        len(data),  # data
        4,  # K{length}{data} checksum
        3  # G01 end
    ])
    body = struct.pack("< 3s c B {}s c B {}s c B {}s c I {}s".format(
        len(source),
        len(destination),
        len(id_),
        len(data)
    ),
        bytes("G00").encode("ascii"),
        b'S', len(source), source,
        b'D', len(destination), destination,
        b'T', len(id_), id_,
        b'P', len(data), data
    )
    checksum = struct.pack("> H", compute_checksum(body))
    encoded = struct.pack("< {}s c B {}s 3s".format(
        len(body),
        len(checksum)
    ),
        body,
        bytes('K').encode("ascii"), 2, checksum,
        bytes("G01").encode("ascii")
    )
    return encoded

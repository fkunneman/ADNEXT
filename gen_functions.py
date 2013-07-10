#! /usr/bin/env python

def make_chunks(lines,size):
    chunks=[]
    i=0
    remains = len(lines)
    while remains > size:
        chunks.append(lines[i:(i+size)])
        i += size
        remains = len(lines[i:])
    chunks.append(lines[i:])
    return chunks

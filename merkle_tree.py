#!/usr/bin/env python3
#
# Most of this code was gratuitously ripped-off from the PyPI module evm-sc-utils (v0.3.0)
# My thanks to the author, mpayfuss, for creating this module and for what I was able to
# learn by reviewing his code.
#
# This code will create a sorted Merkle Tree using the same Keccak hashing algorithm as
# generally used within the Ethereum blockchain. It can create a tree with any number of
# leaf nodes, but it obviously takes longer (and creates a longer/deeper tree) based on the
# number of leaf nodes in use. I've taken the liberty of creating a "demo" tree with only two
# nodes, a test address value of '0x1337133713371337133713371337133713371337' and a kind of "null"
# value of '0x0000000000000000000000000000000000000000'. This will create the following values:
#
# Root: 0x431aa5796d9dcb4f660d5693a60130628c39fcbe6b83648a572929b1625f5332
# Proof: 0x5380c7b7ae81a58eb98d9c78de4a1fd7fd9535fc953ed2be602daaa41767312a
#
# Obviously, using a Merkle Tree for two values doesn't make much sense, but this will work to
# create the root and proof for any number of leaf nodes. Simply replace the '0' value in the
# line:
#
# print('Proof:', mt.get_proof(Web3.solidityKeccak(['bytes'], [allowlist[0]])))
#
# with whatever value points to the value you're interested in within your 'allowlist,' an the
# code will output the correct proof value.
#
# As an example, using the allow list:
#
# allowlist = ['0x1111111111111111111111111111111111111111',
#              '0x2222222222222222222222222222222222222222',
#              '0x3333333333333333333333333333333333333333', <----- Proof for this item
#              '0x4444444444444444444444444444444444444444',
#              '0x5555555555555555555555555555555555555555',
#              '0x6666666666666666666666666666666666666666',
#              '0x7777777777777777777777777777777777777777',
#              '0x8888888888888888888888888888888888888888']
#
# Gives us the following output:
#
# Root: 0x92b50ba94b4eddae31256603c1e445747eb4da7bbcce500a1c711ebeef99757e
# Proof: ['0x2ab0a4443bbea3fbe4d0e1503d11ff1367842fb0c8b28a5c8550f27599a40751', 
#         '0xe53833745f812dbbffd118a573b4b380aae6b82afd4839d67dd7a2f809a5554c', 
#         '0xab642276d45d87c4c538fea27c78e9fae2b6f5d3505d3f108d480897899b5993']
# 
# Copyright 2022 Prof. Qwerty Petabyte 
# This code is released under the MIT License 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions: The above
# copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.

from typing import List, Dict
from hexbytes import HexBytes
from eth_typing import HexStr
from web3 import Web3

class MerkleTreeKeccak:
    '''Class for computing a sorted Merkle Tree using Keccak hashing algorithm'''

    def __init__(self, leaves: List[HexBytes]):
        MerkleTreeKeccak.__check_input(leaves)
        self.tree = MerkleTreeKeccak.__compute_tree(leaves)

    @staticmethod 
    def __check_input(leaves: List[HexBytes]):
        if not isinstance(leaves, list):
            raise ValueError('MerkleTreeKeccak: Leaves are not a list')

        if len(leaves) == 0:
            raise ValueError('MerkleTreeKeccak: Leaves are an empty list')

        for leaf in leaves:
            if not isinstance(leaf, HexBytes):
                raise TypeError(f'MerkleTreeKeccak: {leaf!r} not of HexBytes type')
            if len(leaf) != 32:
                raise ValueError(f'MerkleTreeKeccak: {leaf!r} is not a valid 32 byte hash')

    @staticmethod
    def __compute_tree(leaves: List[HexBytes]):
        tree: Dict = {}
        leaves.sort()
        tree[0] = leaves
        node_level = 0
        while len(tree[node_level]) != 1:
            nodes = tree[node_level]
            next_nodes: List[HexBytes] = []
            num_of_nodes = len(nodes)
            is_odd = num_of_nodes % 2 != 0
            if is_odd:
                for i in range(0, num_of_nodes - 1, 2):
                    next_nodes.append(Web3.solidityKeccak(['bytes32', 'bytes32'], [nodes[i], nodes[i + 1]]))
                next_nodes.append(nodes[-1])
            else:
                for i in range(0, num_of_nodes, 2):
                    next_nodes.append(Web3.solidityKeccak(['bytes32', 'bytes32'], [nodes[i], nodes[i + 1]]))
            # sort in place
            next_nodes.sort()
            tree[node_level + 1] = next_nodes
            node_level = len(tree.keys()) - 1
        return tree

    @property
    def root_hash(self) -> HexStr:
        '''Returns the merkle root hash'''
        return self.tree[len(self.tree.keys()) - 1][0].hex()

    def get_proof(self, leaf: HexBytes) -> List[HexStr]:
        '''Function to get the merkle proof for an input leaf'''
        if not isinstance(leaf, HexBytes):
            raise TypeError(f'MerkleTreeKeccak: {leaf!r} not of HexBytes type')
        if len(leaf) != 32:
            raise ValueError(f'MerkleTreeKeccak: {leaf!r} is not a valid 32 byte hash')

        if self.tree[0].index(leaf) < 0:
            print(self.tree[0].index(leaf))
            return []

        proof: List[HexStr] = []
        num_of_nodes: int = len(self.tree.keys()) - 1
        lookup_val: HexBytes = leaf
        for i in range(num_of_nodes):
            loc: int = 0
            for (node, j) in zip(self.tree[i], range(len(self.tree[i]))):
                if node.hex() == lookup_val.hex():
                    loc = j
                    break
            if loc % 2 == 0 and loc != len(self.tree[i]) - 1:
                proof.append(self.tree[i][loc + 1].hex())
                lookup_val = Web3.solidityKeccak(['bytes32', 'bytes32'],[self.tree[i][loc], self.tree[i][loc + 1]])
            elif loc % 2 == 0 and loc == len(self.tree[i]) - 1:
                pass
            else:
                proof.append(self.tree[i][loc - 1].hex())
                lookup_val = Web3.solidityKeccak(['bytes32', 'bytes32'],[self.tree[i][loc - 1], self.tree[i][loc]])
        return proof

allowlist = ['0x1337133713371337133713371337133713371337','0x0000000000000000000000000000000000000000']

leaves = []
for address in allowlist:
    leaves.append(Web3.solidityKeccak(['bytes'], [address]))
mt = MerkleTreeKeccak(leaves)
# this gives us the root value, which is 1/2 of the values necessary 
# to show that an address is part of the allow list
print('Root:', mt.root_hash)
# now, we need to get the proof value associated with the allow list: in this case, so we use allowlist[0] to pull it out.
# normally there would be a whole bunch of addresses in the allow list, 
# but we're just making a list with only our address and a "null" address...
print('Proof:', mt.get_proof(Web3.solidityKeccak(['bytes'], [allowlist[0]])))

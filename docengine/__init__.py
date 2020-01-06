"""
Commutative Replicated Datatype (CRDT) document engine to provide support of
simultaneous editing of the same document by multiple users. Using algorithm
defined on this paper:
https://hal.archives-ouvertes.fr/hal-00921633/document
"""
from .doc import Doc

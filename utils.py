from argparse import Namespace

def namespace(ns: Namepace(), d: dict):

    ''' Creates a Namespace object ns in place for an arbitrarily deep input dictionary, d. '''

    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict):
                leaf_ns = Namespace()
                ns.__dict__[k] = leaf_ns
                namespace(leaf_ns, v)
            else:
                ns.__dict__[k] = v

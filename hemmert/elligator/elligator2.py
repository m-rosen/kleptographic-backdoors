#! /usr/bin/env python3

# This file is dual-licensed.  Choose whichever licence you want from
# the two licences listed below.
#
# The first licence is a regular 2-clause BSD licence.  The second licence
# is the CC-0 from Creative Commons. It is intended to release Monocypher
# to the public domain.  The BSD licence serves as a fallback option.
#
# SPDX-License-Identifier: BSD-2-Clause OR CC0-1.0
#
# ------------------------------------------------------------------------
#
# Copyright (c) 2020-2022, Loup Vaillant
# Copyright (c) 2020-2021, Andrew Moon
# All rights reserved.
#
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ------------------------------------------------------------------------
#
# Written in 2020-2022 by Loup Vaillant and Andrew Moon
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related neighboring rights to this software to the public domain
# worldwide.  This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software.  If not, see
# <https://creativecommons.org/publicdomain/zero/1.0/>


# -------------------------------------------------------------------------
# NOTE : 2023: Miriam Rosén
# This file is a patchwork of functions from the elligator2 reference impelentation
# The goal was to enable use of curves where the B coefficient is not 1.


from elligator.core import *

# Configure to your specific curve
GF.p = None
A = None
B = None
Z = None


# From curve25519.py
# ---------------------------------------------
def is_negative(self):
    """True iff self is in [p.+1 / 2.. p-1]

    An alternative definition is to just test whether self is odd.
    """
    dbl = (self.val * 2) % GF.p
    return dbl % 2 == 1

GF.is_negative = is_negative

# End curve25519.py
# ---------------------------------------------


# From curve448.py
# --------------------------------------------

# #########################
# # Square root functions #
# #########################
def sqrt(n):
    """Principal square root of n

    If n is not a square, the behaviour is undefined.

    To know how it works, refer to https//elligator.org/sqrt
    """
    square = n**((GF.p+1) // 4)
    square = cmove(square, -square, square.is_negative())
    return square

# End curve448.py
# --------------------------------------------


# From elligator.py
# ---------------------------------------------
############################
# Reference Implementation #
############################
def dir_map_ref(r):
    """Computes a point (u, v) from the representative r in GF(p)

    Always succeds
    """
    w = -A / (GF(1) + Z * r**2)
    e = legendre(w**3 + A*w**2 + B*w)
    u = e*w - (GF(1)-e)*(A//2)
    v = -e * sqrt(u**3 + A*u**2 + B*u)
    return (u, v)

def rev_map_ref(u, v_is_negative):
    """Computes the representative of the point (u, v), if possible

    Returns None if the point cannot be mapped.
    """
    if u == -A or not is_square(-Z * u * (u+A)):
        return None
    sq1 = sqrt(-u     / (Z * (u+A)))
    sq2 = sqrt(-(u+A) / (Z * u    ))
    rep = sq1
    rep = cmove(rep, sq2, v_is_negative)
    rep = cmove(rep, -rep, rep.is_negative()) # abs(rep)
    return rep


################################
# Compare both implementations #
################################
def dir_map(r):
    p_ref  = dir_map_ref(r)
    # p_fast = dir_map_fast(r)
    p_neg  = dir_map_ref(-r)
    u, v   = p_ref
    r_back = rev_map_ref(u, v.is_negative())
    # if p_ref  != p_fast : raise ValueError('ref/fast map mismatch')
    if p_ref  != p_neg  : raise ValueError('+r/-r map mismatch')
    if r_back != r.abs(): raise ValueError('roundtrip map mismatch')
    return p_ref

def rev_map(u, v_is_negative):
    r_ref  = rev_map_ref (u, v_is_negative)
    # r_fast = rev_map_fast(u, v_is_negative)
    # if r_ref != r_fast: raise ValueError('r mismatch (ref vs fast rev_map')
    if r_ref:
        u_back, v_back = dir_map_ref(r_ref)
        if u_back != u or v_back.is_negative() != v_is_negative:
            raise ValueError('roundtrip mismatch (rev_map)')
    return r_ref



# End elligator.py
# ----------------------------------------------

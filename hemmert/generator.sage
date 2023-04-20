'''
    Written by Miriam Rosén in 2023
'''

q = 2**257 - 93
d = 1088

# Twisted Montgomery: B_mont*v^2 = u^3 + A_mont*u^2 + u 
A_mont = 4/(1-d)-2
B_mont = 4/(1-d)

# Elligator representation: v^2 = u^3 + A_elli*u^2 + B_elli*u
A_elli = A_mont*B_mont
B_elli = B_mont*B_mont

C = EllipticCurve(GF(q), [0, A_elli, 0, B_elli, 0])

_, Q = C.lift_x(8, True) # We choose the point with "positive" y
assert Q.order() == C.order()
print(Q)

R = Q * (C.order() // 4)
assert R.order() == 4
print(R)


# Translate to Edward's space
u = int(Q[0])
v = int(Q[1])

u_1 = u / B_mont
v_1 = v / B_mont**2
x = u_1 / v_1
y = (u_1 - 1)/ (u_1 + 1)

x = x % q
y = y % q

print(f"({x}, {y})")


# Output =======================

'''
(
    8 :
    202147041914464820605132653760910020457625730962775268383643592932733397899169 :
    1
)
(
    181517681748285921804751571715551237333920932723322466534715476678458116749192 :
    36828651963700236524266771330447045643988363267168526840616566388290330419728 :
    1
)
(
    228372640616428539900130013049815066326154907798774733358185911637216892286314,
    165508619038704143113488945898290217115626586457192633182952257675369618343994
)
'''
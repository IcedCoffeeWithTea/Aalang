n1 = 0
n2 = 1


for("i in 14")
    old = n2    
    n2 = n1 + n2
    n1 = old
    i = i - 1
endloop

print(n1)
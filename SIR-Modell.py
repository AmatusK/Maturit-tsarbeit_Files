import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

suscval = [990]
infval = [10]
remval = [0]
naught = 0.0005
rectime = 0.035
x = 0

while x < 80:
    suscval.append(suscval[x] - suscval[x] * naught * infval[x]) 
    infval.append(infval[x] + naught * suscval[x] * infval[x] - rectime * infval[x])
    remval.append(remval[x] + rectime * infval[x])
    x += 1
    
#print(suscval)
#print(infval)
#print(remval)

plt.figure(figsize=(20, 20))
plt.plot(suscval, label="Anfällige Menschen")
plt.plot(infval, label="Infizierte Menschen")
plt.plot(remval, label ="Immun/Verstorbene Menschen")

plt.xlim([0, 80])
plt.title("SIR Modell")
plt.xlabel("Anzahl vergangener Tage")
plt.ylabel("Verhältniss")
plt.legend(loc="upper right")
plt.show()

import matplotlib.pyplot as plt
import numpy as np
s = input('Digite um código de 6 digitos hexadecimal: ').strip().upper()
if len(s) != 6 or not all(c in '0123456789ABCDEF' for c in s):
    print("⚠️ Código hexadecimal inválido. Use apenas 6 caracteres de 0 a 9 ou A a F.")
    exit()
def f(s):
    hex_inverso = {'0': 0,'1': 1,'2': 2,'3': 3,'4': 4,'5': 5,'6': 6,'7': 7,'8': 8,'9': 9,'A': 10,'B': 11,'C': 12,'D': 13,'E': 14,'F': 15}
    R = s[0:2]
    G = s[2:4]
    B = s[4:]
    listaR = list(R)
    listaG = list(G)
    listaB = list(B)
    novalistaR = [hex_inverso[x] for x in listaR]
    novalistaG = [hex_inverso[y] for y in listaG]
    novalistaB = [hex_inverso[z] for z in listaB]
    novalistaR[0] = novalistaR[0] * 16
    novalistaG[0] = novalistaG[0] * 16
    novalistaB[0] = novalistaB[0] * 16
    somaR = sum(novalistaR)
    somaG = sum(novalistaG)
    somaB = sum(novalistaB)
    return np.array([somaR, somaG, somaB]) / 255
cor_rgb = f(s)
anticor = 1 - cor_rgb
steps = 150
cores = np.concatenate([
    np.linspace(cor_rgb, anticor, steps),
    np.linspace(anticor, cor_rgb, steps)
])

# Plot
fig, ax = plt.subplots(figsize=(6, 2))
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
fig.canvas.manager.set_window_title("Transição de cor")

# Desenha um retângulo colorido preenchendo toda a área
rect = plt.Rectangle((0, 0), 1, 1, color=cor_rgb)
ax.add_patch(rect)

# Animação
try:
    while True:
        for c in cores:
            rect.set_color(c)
            ax.set_title(f"Transição #{s} → anticor", color='white' if sum(c) < 1.5 else 'black')
            plt.pause(0.01)
except KeyboardInterrupt:
    plt.close()
    print("Encerrado pelo usuário.")
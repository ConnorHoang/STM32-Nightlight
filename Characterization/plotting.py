import matplotlib.pyplot as plt
import numpy as np

dist = (np.array([7, 6, 5, 4, 3, 2, 1, 0.15]))/2 # Base measurements taken in units of two inches (as two inch tiles were used as refernce) so division  
I_rel = 1.0 / (dist**2)
R = np.array([3.7, 2.9, 2.2, 1.6, 1.1, 0.7, 0.4, 0.0])
err = 0.3

# Power-law fit
m, b = np.polyfit(np.log10(I_rel[:-1]), np.log10(R[:-1]), 1)
x_fit = np.logspace(np.log10(I_rel.min()), np.log10(I_rel.max()), 200)
y_fit = (10**b) * (x_fit**m)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# Linear plot
ax1.errorbar(I_rel, R, yerr=err, fmt='ro', capsize=3, label='Data')
ax1.plot(x_fit, y_fit, 'b-', label=f'Fit: R = {10**b:.2f} * I^{m:.2f}')
ax1.set(xlabel='Relative Light (1/d²)', ylabel='Resistance (kOhms)', title='Linear')
ax1.legend()

# Log-Log plot
ax2.errorbar(I_rel[:-1], R[:-1], yerr=err, fmt='ro', capsize=3, label='Data')
ax2.plot(x_fit, y_fit, 'b-', label=f'Slope = {m:.2f}')
ax2.set(xscale='log', yscale='log', xlabel='Relative Light (1/d²)', ylabel='Resistance (kOhms)', title='Log-Log')
ax2.legend()

plt.tight_layout()
plt.savefig('ldr_characterization.png')
plt.show()
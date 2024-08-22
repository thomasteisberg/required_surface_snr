import os
import pandas as pd
import matplotlib.pyplot as plt

# Hide the root window of Tkinter
root = Tk()
root.withdraw()

# Specify the folder where the SNR data file is located
myFolder = filedialog.askdirectory()

# Load the CSV file
csv_file_path = os.path.join(myFolder, 'snr_data.csv')

if not os.path.isfile(csv_file_path):
    print(f'Error: The following file does not exist:\n{csv_file_path}')
    exit()

df = pd.read_csv(csv_file_path)

x, y, snr = df['x'], df['y'], df['snr']

# Plot the data
plt.scatter(x, y, c=snr, s=20, cmap='viridis', edgecolor='none', alpha=0.75)
plt.colorbar(label='snr')
plt.show()

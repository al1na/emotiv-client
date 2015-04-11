from matplotlib import pyplot as plt

lg = []
x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
y = [11, 25, 13, 34, 51, 44, 19, 39, 6]
colors = ['b', 'g', 'r', 'b', 'g', 'r', 'b', 'g', 'r']
markers = ['s', 's', 's', 'o', 'o', 'o', 'v', 'v', 'v']
labels = ['csv/bzip', 'csv/7zip', 'csv/gzip', 'json/bzip', 'json/7zip', 'json/gzip', 'sqlite/bzip', 'sqlite/7zip', 'sqlite/gzip']

plt.xlabel('Time in seconds')
plt.ylabel('Memory in bytes')

for i in range(0, 9):
    lg.append(plt.scatter(x[i], y[i], marker=markers[i], color=colors[i], s=100))

for label, xi, yi in zip(labels, x, y):
    plt.annotate(label, xy = (xi, yi), xytext = (-10, 10), textcoords = 'offset points')

plt.legend((lg[0], lg[1], lg[2], lg[3], lg[4], lg[5], lg[6], lg[7], lg[8]),
           ('csv/bzip', 'csv/7zip', 'csv/gzip', 'json/bzip', 'json/7zip', 'json/gzip', 'sqlite/bzip', 'sqlite/7zip', 'sqlite/gzip'),
           scatterpoints=1,
           loc='upper right',
           ncol=3,
           fontsize=10,
           bbox_to_anchor=(0., 1.02, 1., .102),
           mode="expand",
           borderaxespad=0.)

plt.show()
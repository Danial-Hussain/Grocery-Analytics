import matplotlib.pyplot as plt
import seaborn as sns

sns.set(font = 'Franklin Gothic Book',
rc = {
'axes.axisbelow': False,
'axes.edgecolor': 'lightgrey',
'axes.facecolor': 'None',
'axes.grid': False,
'axes.labelcolor': 'dimgrey',
'axes.spines.right': False,
'axes.spines.top': False,
'figure.facecolor': 'white',
'lines.solid_capstyle': 'round',
'patch.edgecolor': 'w',
'patch.force_edgecolor': True,
'text.color': 'dimgrey',
'xtick.bottom': 'False',
'xtick.color': 'dimgrey',
'xtick.direction': 'out',
'xtick.top': False,
'ytick.color': 'dimgrey',
'ytick.direction': 'out',
'ytick.left': False,
'ytick.right': False
})

sns.set_context('notebook', rc= {"font.size": 16,
"axes.titlesize": 18,
"axes.labelsize": 18})

sns.set_palette(["#20bf6b", "#0fb9b1", "#26de81", "#fa983a", "#6a89cc",
	"#f8c291", "#b8e994", "#fad390"])
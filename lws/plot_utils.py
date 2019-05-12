import matplotlib.pyplot as plt
# from matplotlib.backends.backend_pdf import PdfPages
import os


plot_style_list = ['go-', 'g*-', 'gv-', 'gs-', 'gD-', 'gX-', 'gh-']

plot_color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
def simple_2d_plot(x_arr, y_arr, x_label, y_label, plot_label, grid_on=True):
    fig = plt.figure()
    plt.plot(x_arr, y_arr, label=plot_label)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if grid_on:
        plt.grid()
    return fig

def savePlotAsPdf(path, name, fig):
    # pp = PdfPages(os.path.join(path, name))
    # pp.savefig(fig)
    # print("Figure {} Saved!".format(name))
    # pp.close()
    # plt.closse()
    # plt.plot(range(10), range(10), "o")
    # plt.show()
    fig.savefig(os.path.join(path,name), bbox_inches='tight')
    print("Figure {} Saved!".format(name))
    plt.close()    

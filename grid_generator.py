import tikz
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from itertools import product, combinations
import copy

import networkx as nx

from pylatex import Document, TikZ
from pylatex import Package, Command
from pylatex.utils import italic, bold, NoEscape
from pylatex.basic import NewLine

def generate_locations(seed=None):
    n_colors = 8
    n_copies = 8

    # locations = [0.33 * (np.array([i,j]) - 3.5) for i in range(n_colors) for j in range(n_copies)]

    indices = [(i,j) for i in range(n_colors) for j in range(n_copies)]

    if seed is None:
        seed = np.random.randint(2**31)
    print('Initial seed = %i' % seed)
    np.random.seed(seed)

    flag = 1
    while flag == 1:
        shuffled_indices = [(i,j) for i in range(n_colors) for j in range(n_copies)]
        np.random.shuffle(shuffled_indices)

        n_colors_real = 6
        n_copies_real = 10
        labels = [1,2,3,4,5,6,0,0]
        g = nx.Graph()
        for i in range(n_colors_real):
            for j in range(n_copies_real):
                g.add_node(shuffled_indices[n_copies_real*i + j], label=labels[i])

        for i in range(n_copies_real*n_colors_real, n_colors*n_copies):
            g.add_node(shuffled_indices[i], label=0)

        print(len(g.nodes()))

        for i in range(n_colors - 1):
            for j in range(n_copies - 1):
                g.add_edge((i,j), (i+1,j), capacity=1)
                g.add_edge((i,j), (i,j+1), capacity=1)

        for j in range(n_copies-1):
            g.add_edge((n_colors-1, j), (n_colors-1,j+1), capacity=1)
            g.add_edge((j, n_colors-1), (j+1, n_colors-1), capacity=1)

        node_labels = nx.get_node_attributes(g, 'label')

        for x,y,z in combinations([1,2,3,4,5,6], 3):
            h = copy.deepcopy(g)
            for i,j in product(np.arange(n_colors), np.arange(n_copies)):
                if node_labels[(i,j)] in (x,y,z):
                    h.remove_node((i,j))
            # Collect nodes on top and bottom rows
            top_nodes = [x for x in h.nodes() if x[1] == n_colors-1]
            bottom_nodes = [x for x in h.nodes() if x[1] == 0]
            left_nodes = [x for x in h.nodes() if x[0] == 0]
            right_nodes = [x for x in h.nodes() if x[0] == n_colors-1]
            flag = 1
            for bottom, top in product(bottom_nodes, top_nodes):
                cut_value = nx.minimum_cut_value(h, bottom, top)
                if cut_value > 0:
                    print((x,y,z), bottom, top)
                    flag = 0
                    break
            if flag:
                for left, right in product(left_nodes, right_nodes):
                    cut_value = nx.minimum_cut_value(h, left, right)
                    if cut_value > 0:
                        print((x,y,z), left, right)
                        flag = 0
                        break
            if flag:
                print('Miss at %s' % ((x,y,z),))
                break

        if flag:
            seed = np.random.randint(2**31)
            print('New seed = %i' % seed)
            np.random.seed(seed)


    locations = [0.33 * (np.array([i,j]) - (n_colors//2 - 0.5)) for i,j in shuffled_indices]

    return locations, seed


def generate_electorate_grid(locations):
    # color_list = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']
    color_list = ['black'] * 6

    n_real = 10

    pic = tikz.Picture()
    pic.usetikzlibrary('shapes.geometric')

    x_locs = np.arange(-1.155, 1.16, 0.33/8)
    y_locs = np.arange(-1.155, 1.16, 0.33)
    dot_locations = product(x_locs, y_locs)
    for i,j in dot_locations:
        point = '(%fin, %fin)' % (i,j)
        pic.node(r'\phantom{}', at=point, inner_sep='0.25pt', fill='black', circle=True)

    dot_locations = product(y_locs, x_locs)
    for i,j in dot_locations:
        point = '(%fin, %fin)' % (i,j)
        pic.node(r'\phantom{}', at=point, inner_sep='0.25pt', fill='black', circle=True)


    for location in locations[:n_real]:
        point = '(%fin, %fin)' % (location[0], location[1])
        pic.node(r'\phantom{.}', at=point, minimum_width='0.165in', minimum_height='0.165in', draw=True, fill='white')#, fill=color_list[0])
        pic.node(r'\phantom{1}', at=point, draw=color_list[0], circle=True, inner_sep='0.75pt', line_width='0.45mm', scale=0.5, transform_shape=True)

    for location in locations[n_real:2*n_real]:
        point = '(%fin, %fin)' % (location[0], location[1])
        pic.node(r'\phantom{.}', at=point, minimum_width='0.165in', minimum_height='0.165in', draw=True, fill='white')#, fill=color_list[1])
        pic.node(r'\rule{6mm}{1mm}', at=point, text=color_list[1], rotate=45, inner_sep='0pt', scale=0.5, transform_shape=True)
        pic.node(r'\rule{6mm}{1mm}', at=point, text=color_list[1], rotate=-45, inner_sep='0pt', scale=0.5, transform_shape=True)

    for location in locations[2*n_real:3*n_real]:
        point = '(%fin, %fin)' % (location[0], location[1])
        point2 = '(%fin, %fin)' % (location[0], location[1]-0.0175)
        pic.node(r'\phantom{.}', at=point, minimum_width='0.165in', minimum_height='0.165in', draw=True, fill='white')#, fill=color_list[2])
        pic.node(r'\phantom{.}', at=point2, regular_polygon=True, regular_polygon_sides=3, draw=color_list[2], line_width='0.45mm', inner_sep='1.0pt', scale=0.5, transform_shape=True)

    for location in locations[3*n_real:4*n_real]:
        point = '(%fin, %fin)' % (location[0], location[1])
        pic.node(r'\phantom{.}', at=point, minimum_width='0.165in', minimum_height='0.165in', draw=True, fill='white')#, fill=color_list[3])
        pic.node(r'\phantom{.}', at=point, draw=color_list[3], diamond=True, inner_sep='2.125pt', line_width='0.45mm', fill=color_list[3], scale=0.5, transform_shape=True)

    for location in locations[4*n_real:5*n_real]:
        point = '(%fin, %fin)' % (location[0], location[1])
        point2 = '(%fin, %fin)' % (location[0], location[1]-0.0025)
        pic.node(r'\phantom{.}', at=point, minimum_width='0.165in', minimum_height='0.165in', draw=True, fill='white')#, fill=color_list[4])
        pic.node(r'\phantom{.}', at=point2, star=True, star_points=5, star_point_ratio=2, fill=color_list[4], inner_sep='1.6pt', scale=0.5, transform_shape=True)

    for location in locations[5*n_real:6*n_real]:
        point = '(%fin, %fin)' % (location[0], location[1])
        pic.node(r'\phantom{.}', at=point, minimum_width='0.165in', minimum_height='0.165in', draw=True, fill='white')#, fill=color_list[5])
        pic.node(r'\phantom{.}', at=point, regular_polygon=True, regular_polygon_sides=6, fill=color_list[5], inner_sep='3.2pt', scale=0.5, transform_shape=True)

    for location in locations[6*n_real:64]:
        point = '(%fin, %fin)' % (location[0], location[1])
        pic.node(r'\phantom{.}', at=point, minimum_width='0.165in', minimum_height='0.165in', draw=True, fill='white')#, fill=color_list[5])

    # pic.node(r'\phantom{}', at='(0in,0in)', draw='black', line_width='0.25mm', minimum_width='1.99in', minimum_height='1.99in')
    pic.node(r'\phantom{}', at='(0in,0in)', draw='white', line_width='0.3329145728643216mm', minimum_width='2.65in', minimum_height='2.65in')

    tikzpicture = pic.code()
    return tikzpicture

def save_tikzpicture(tikzpicture, filename):
    f = open(filename, 'w')
    f.write(tikzpicture)
    f.close()

# def generate_latex_doc(tikzpicture, seed):
#     geometry_options = {'margin': '10mm'}
#     doc = Document(documentclass = 'scrartcl',
#                 document_options = ["paper=a4","parskip=half"],
#                 fontenc=None,
#                 inputenc=None,
#                 lmodern=False,
#                 textcomp=False,
#                 page_numbers=False,
#                 geometry_options=geometry_options)

#     doc.packages.append(Package('tikz'))
#     doc.packages.append(Package('fontspec'))
#     doc.packages.append(Package('enumitem'))
#     doc.packages.append(Package('multicol'))
#     doc.packages.append(Package('booktabs'))
#     doc.packages.append(Package('epsdice'))
#     doc.packages.append(Package('astrollogy'))

#     doc.preamble.append(Command('usetikzlibrary', 'shapes.geometric'))
#     doc.preamble.append(Command('setkomafont', NoEscape(r'section}{\setmainfont{Century Gothic}\LARGE\bfseries\center')))
#     doc.preamble.append(Command('RedeclareSectionCommand', 'section', ([r'runin=false', NoEscape(r'afterskip=0.0\baselineskip'), NoEscape(r'beforeskip=1.0\baselineskip')])))
#     doc.change_length("\columnsep", "10mm")

#     doc.append(Command(NoEscape(r'begin{center}')))
#     doc.append(NoEscape(tikzpicture))
#     doc.append(Command(NoEscape(r'end{center}')))

#     doc.append(Command(r'vspace{-8.5mm}'))

#     doc.append(NoEscape(r'\begin{center}\includegraphics[width=155mm]{Images/ASTROLLOGY_Logo.eps}\end{center}'))

#     doc.append(Command(r'vspace{-1.5mm}'))
#     doc.append(Command(NoEscape(r'setmainfont[Scale=0.95]{Century Gothic}')))
#     doc.append(Command(NoEscape(r'raggedright')))

#     doc.append(Command(r'begin{multicols}{2}'))
#     f = open('astrollogy_rules_text.tex')
#     rules_text = f.read()
#     f.close()
#     doc.append(NoEscape(rules_text))
#     doc.append(Command(r'vfill'))
#     doc.append(NoEscape(r"\textbf{Random Seed:} %i\\\textbf{Game Design:} Michael~Purcell\\\textbf{Graphic Design:} Kyle~``KYNG''~Jarratt\\\textbf{Contact:} ttkttkt@gmail.com\vfill\null" % seed))
#     doc.append(Command(r'end{multicols}'))

#     doc.append(Command(r'vspace{-5mm}'))

#     doc.append(NoEscape(r'{\Huge \dieone{} = \tikz{\pic {onestar}} \hfill \dietwo{} = \tikz{\pic {twostar}} \hfill \diethree{} = \tikz{\pic {threestar}} \hfill \diefour{} = \tikz{\pic {fourstar}} \hfill \diefive{} = \tikz{\pic {fivestar}} \hfill \diesix{} = \tikz{\pic {sixstar}}}'))

#     return doc

# def save_latex_doc(latex_doc, seed):
#     latex_doc.generate_pdf('astrollogy_starfield_%i' % seed, compiler='xelatex')

if __name__ == '__main__':
    seed = None
    # seed = 1795770665
    locations, seed = generate_locations(seed=seed)
    print(seed)
    tikzpicture = generate_electorate_grid(locations=locations)
    save_tikzpicture(tikzpicture=tikzpicture, filename='site_grid.tex')
    # latex_doc = generate_latex_doc(tikzpicture, seed)
    # save_latex_doc(latex_doc, seed)
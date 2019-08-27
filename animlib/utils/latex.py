def getTexReplaceText():
        return "TEXT_TO_REPLACE"

def getTexTemplate(isCTex=False):
    if isCTex:
        return """\\documentclass[preview]{standalone}

\\usepackage[english]{babel}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{dsfont}
\\usepackage{setspace}
\\usepackage{tipa}
\\usepackage{relsize}
\\usepackage{textcomp}
\\usepackage{mathrsfs}
\\usepackage{calligra}
\\usepackage{wasysym}
\\usepackage{ragged2e}
\\usepackage{physics}
\\usepackage{xcolor}
\\usepackage{microtype}
%\\DisableLigatures{encoding = *, family = * }
\\usepackage[UTF8]{ctex}
\\linespread{1}

\\begin{document}
\\begin{align*}
""" + getTexReplaceText() + """
\\end{align*}
\\end{document}
"""
    else:
        return """\\documentclass[preview]{standalone}

\\usepackage[english]{babel}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{dsfont}
\\usepackage{setspace}
\\usepackage{tipa}
\\usepackage{relsize}
\\usepackage{textcomp}
\\usepackage{mathrsfs}
\\usepackage{calligra}
\\usepackage{wasysym}
\\usepackage{ragged2e}
\\usepackage{physics}
\\usepackage{xcolor}
\\usepackage{microtype}
\\DisableLigatures{encoding = *, family = * }
%\\usepackage[UTF8]{ctex}
\\linespread{1}

\\begin{document}
\\begin{align*}
""" + getTexReplaceText() + """
\\end{align*}
\\end{document}
"""
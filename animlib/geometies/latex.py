from animlib.geometies.svg import SVG
from animlib.utils.latex import *

import hashlib, os
from time import sleep

class Latex(SVG):

    def __init__(self, *args, **kwargs):
        self.__tmpdir = "_tmp"
        self._useCTex = False
        if not os.path.exists(self.__tmpdir):
            os.mkdir(self.__tmpdir)
        
        assert len(args) == 0 or len(args) == 2 or len(args) == 3, "must pass [x, y] or [x, y, expr]"

        if len(args) > 0:
            kwargs["x"] = args[0]
        if len(args) > 1:
            kwargs["y"] = args[1]
        if len(args) > 2 and not any([k in kwargs.keys() for k in ["expression", "Expression", "expr", "Expr"]]):
                kwargs["expr"] = args[2]

        self._expression = None
        for key in kwargs:
            arg = kwargs[key]
            if key in ["expression", "Expression", "expr", "Expr"]:
                self._expression = arg
            if key in ["ctex"]:
                self._useCTex = arg

        assert isinstance(self._expression, str), "Must pass expression=(str) to Latex"
        self._texToSvgFile()
        
        # make sure the SVG us used properly in super class
        kwargs["svg"] = self._svgFile
        super().__init__(**kwargs)

    def _texToSvgFile(self):
        self._texFile = os.path.join(
            self.__tmpdir,
            self._texHash()
        ) + ".tex"
        print("LaTeX conversion : {}".format(os.path.split(self._texFile)[-1]), end=" ")
        self._divFile = self._texFile.replace(".tex", ".dvi" if not self._useCTex else ".xdv")
        self._svgFile = self._divFile.replace(".dvi" if not self._useCTex else ".xdv", ".svg")

        if not os.path.exists(self._texFile):
            texBody = getTexTemplate(self._useCTex).replace(getTexReplaceText(), self._expression)
            with open(self._texFile, "w", encoding="utf-8") as texOutFile:
                texOutFile.write(texBody)
                texOutFile.close()
            self._texToDvi()
            self._dviToSvg()
        print("-> DONE")

    def _texHash(self):
        idStr = str(self._expression + getTexTemplate(self._useCTex))
        hasher = hashlib.sha256()
        hasher.update(idStr.encode())
        # Truncating at 16 bytes for cleanliness
        return hasher.hexdigest()[:16]

    def _texToDvi(self):
        if not os.path.exists(self._divFile):
            commands = [
                "latex",
                "-interaction=batchmode",
                "-halt-on-error",
                "-output-directory=\"{}\"".format(self.__tmpdir),
                "\"{}\"".format(self._texFile),
                ">",
                os.devnull
            ] if not self._useCTex else [
                "xelatex",
                "-no-pdf",
                "-interaction=batchmode",
                "-halt-on-error",
                "-output-directory=\"{}\"".format(self.__tmpdir),
                "\"{}\"".format(self._texFile),
                ">",
                os.devnull
            ]
            exit_code = os.system(" ".join(commands))
            if exit_code != 0:
                log_file = self._texFile.replace(".tex", ".log")
                self._divFile = None
                raise Exception(
                    ("Latex error converting to dvi. " if not self._useCTex
                    else "Xelatex error converting to xdv. ") +
                    "See log output above or the log file: {}".format(log_file))

    def _dviToSvg(self):
        if not os.path.exists(self._svgFile):
            commands = [
                "dvisvgm",
                "\"{}\"".format(self._divFile),
                "-n",
                "-v",
                "0",
                "-o",
                "\"{}\"".format(self._svgFile),
                ">",
                os.devnull
            ]
            exit_code = os.system(" ".join(commands))
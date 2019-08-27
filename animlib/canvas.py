from animlib.geometies.base import Base
from animlib.animations.animation import Animation

try:
    import cairo
except:
    import cairocffi as cairo
import time, hashlib, subprocess, shutil
import numpy as np
from time import sleep
from tqdm import tqdm


class Canvas():
    """ The `Canvas` enables drawing of multiple geometries (i.e. `Base`) """

    def __init__(self, name, width=2560, height=1440, fps=60, movieFileExtension=".mp4"):
        if not isinstance(name, str):
            name = str(format(time.time()*1000))
            hasher = hashlib.sha256()
            hasher.update(name.encode())
            name = hasher.hexdigest()[:16]
        self._name = name
        self._width = width if (isinstance(width, int) and width > 320) else 320
        self._height = height if (isinstance(height, int) and height > 240) else 240
        self._fps = fps if (isinstance(fps, (int, float)) and fps > 16) else 16
        self._movieFileExtension = movieFileExtension if movieFileExtension in [".mp4", ".mov"] else ".mp4"
        self._geometrySet = []
        self._backgroundColor = np.array((0.0, 0.0, 0.0, 1.0))

        self._progressBarStyle = "{desc:<8}{percentage:3.0f}%|{bar}|{n_fmt:3s}/{total_fmt:3s}[{elapsed}<{remaining},{rate_fmt}{postfix}]"

        self._initCairo()
        self._openMoviePipe()
    
    def __del__(self):
        self._closeMoviePipe()

    def addGeometry(self, geometry, behind=None, toFront=None):
        """ Adds one or more geometries to the geometries which will be drawn """
        if isinstance(geometry, (list, tuple)):
            if isinstance(behind, (list, tuple)):
                return [self.addGeometry(g, b) for g, b in zip(geometry, behind)]
            else:
                return [self.addGeometry(g) for g in geometry]
        elif not isinstance(geometry, Base):
            return False
        
        if geometry in self._geometrySet:
            if isinstance(toFront, bool):
                if toFront:
                    self._geometrySet = [g for g in self._geometrySet if g is not geometry] + [geometry]
                    return True
                else:
                    self._geometrySet = [geometry] + [g for g in self._geometrySet if g is not geometry]
                    return True
            else:
                return False

        elif behind is not None and behind in self._geometrySet:
            idx = self._geometrySet.index(behind)
            self._geometrySet.insert(idx, geometry)
            return True    
        else:
            self._geometrySet += [geometry]
            return True

    def removeGeometry(self, geometry):
        if isinstance(geometry, (list, tuple)):
            return [self.removeGeometry(g) for g in geometry]
        elif not isinstance(geometry, Base) or geometry not in self._geometrySet:
            return False
        else:
            self._geometrySet.remove(geometry)
            return True

    def saveToPNG(self, name=None):
        """ Saves the presently drawn geometies into a png """
        name = name if name is not None else self._name

        self._context.set_source_rgba(
            self._backgroundColor[0],
            self._backgroundColor[1],
            self._backgroundColor[0],
            self._backgroundColor[3])
        self._context.paint()
        [g.draw(self._context) for g in self._geometrySet]
        self._surface.write_to_png(name + ".png")

    def animate(self, *animations):
        if any([not isinstance(a, Animation) for a in animations]):
            raise Exception("can only animate type Animation")
        
        tmpGeometries, finalGeometries = [], []
        animationDuration = 0
        for animation in animations:
            d = animation.begin()
            animationDuration = d if d > animationDuration else animationDuration
            tmpGeometries.append(animation.getAnimatedObjects())
            finalGeometries.append(animation.getTargetObjects())
        self.addGeometry(finalGeometries)
        self.addGeometry(tmpGeometries, behind=finalGeometries)

        # initialize the progress bar
        progressBar = tqdm(
            total=animationDuration,
            desc="animate",
            bar_format=self._progressBarStyle,
            mininterval=0)

        while any([a.next() for a in animations]):
            progressBar.update(1)
            self._writeFrame()
        
        self.removeGeometry(tmpGeometries)
        progressBar.close()

    def wait(self, duration):
        duration = int(self._fps * duration)

        for _ in tqdm(range(duration),
            desc="wait",
            bar_format=self._progressBarStyle,
            mininterval=0):
            self._writeFrame()

    def _initCairo(self):
        self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self._width, self._height)
        self._context = cairo.Context(self._surface)
        self._context.set_antialias(cairo.ANTIALIAS_DEFAULT)

        # center context axis
        self._context.translate(self._width/2, self._height/2)


    def _openMoviePipe(self):
        """ Opens a movie pipe into which frame data can be written """
        self._outputFilePath = self._name + self._movieFileExtension
        self._tempFilePath = "_temp_" + self._outputFilePath

        command = [
            "ffmpeg",
            '-y',  # overwrite output file if it exists
            '-f', 'rawvideo',
            '-s', '%dx%d' % (self._width, self._height),  # size of one frame
            '-pix_fmt', 'bgra',
            '-r', str(self._fps),  # frames per second
            '-i', '-',  # The imput comes from a pipe
            '-c:v', 'h264_nvenc',
            '-an',  # Tells FFMPEG not to expect any audio
            '-loglevel', 'error',
        ]
        if self._movieFileExtension == ".mov":
            # This is if the background of the exported video
            # should be transparent.
            command += [
                '-vcodec', 'qtrle',
            ]
        else:
            command += [
                '-vcodec', 'libx264',
                '-pix_fmt', 'yuv420p',
            ]
        command += [self._tempFilePath]
        self.writing_process = subprocess.Popen(command, stdin=subprocess.PIPE)
        # self.writing_process.stdin.write(b" ")
        

    def _closeMoviePipe(self):
        """ Closes the movie pipe once frames have been written """
        # closes the movie pipe
        self.writing_process.stdin.close()
        self.writing_process.wait()
        # cleans up the generated files
        shutil.move(
            self._tempFilePath,
            self._outputFilePath
        )
        
    def _writeFrame(self):
        """ Writes the content of the cairo surface to the movie """
        # draw background
        # self._context.rectangle(-self._width/2, -self._height/2, self._width, self._height)
        self._context.set_source_rgba(
            self._backgroundColor[0],
            self._backgroundColor[1],
            self._backgroundColor[2],
            self._backgroundColor[3])
        # self._context.fill()
        self._context.paint()
        [g.draw(self._context) for g in self._geometrySet]
        frame = self._surface.get_data()
        self.writing_process.stdin.write(frame.tobytes())